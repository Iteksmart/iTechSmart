import express from 'express';
import { body, param, query } from 'express-validator';
import { authenticateAny, AuthRequest, requireRole } from '../middleware/auth';
import { asyncHandler, AppError } from '../middleware/errorHandler';
import { validationRateLimiter } from '../middleware/rateLimiter';
import { prisma } from '../index';
import { LicenseGenerator } from '../utils/licenseGenerator';
import { logger } from '../utils/logger';
import { LicenseTier, LicenseStatus } from '@prisma/client';

const router = express.Router();

/**
 * POST /api/licenses/validate
 * Validate a license key
 */
router.post(
  '/validate',
  validationRateLimiter,
  [
    body('licenseKey').notEmpty().withMessage('License key is required'),
    body('productId').optional().isString(),
    body('machineId').optional().isString()
  ],
  asyncHandler(async (req: AuthRequest, res) => {
    const { licenseKey, productId, machineId } = req.body;

    // Find license
    const license = await prisma.license.findUnique({
      where: { licenseKey },
      include: { organization: true }
    });

    if (!license) {
      // Log failed validation
      await prisma.licenseValidation.create({
        data: {
          licenseId: 'unknown',
          isValid: false,
          reason: 'License key not found',
          ipAddress: req.ip,
          userAgent: req.get('user-agent'),
          machineId,
          productId
        }
      });

      return res.json({
        valid: false,
        reason: 'Invalid license key'
      });
    }

    // Check status
    if (license.status !== LicenseStatus.ACTIVE) {
      await prisma.licenseValidation.create({
        data: {
          licenseId: license.id,
          isValid: false,
          reason: `License is ${license.status.toLowerCase()}`,
          ipAddress: req.ip,
          userAgent: req.get('user-agent'),
          machineId,
          productId
        }
      });

      return res.json({
        valid: false,
        reason: `License is ${license.status.toLowerCase()}`
      });
    }

    // Check expiration
    if (license.expiresAt && license.expiresAt < new Date()) {
      await prisma.license.update({
        where: { id: license.id },
        data: { status: LicenseStatus.EXPIRED }
      });

      await prisma.licenseValidation.create({
        data: {
          licenseId: license.id,
          isValid: false,
          reason: 'License expired',
          ipAddress: req.ip,
          userAgent: req.get('user-agent'),
          machineId,
          productId
        }
      });

      return res.json({
        valid: false,
        reason: 'License expired'
      });
    }

    // Check trial expiration
    if (license.isTrial && license.trialEndsAt && license.trialEndsAt < new Date()) {
      await prisma.license.update({
        where: { id: license.id },
        data: { status: LicenseStatus.EXPIRED }
      });

      await prisma.licenseValidation.create({
        data: {
          licenseId: license.id,
          isValid: false,
          reason: 'Trial period expired',
          ipAddress: req.ip,
          userAgent: req.get('user-agent'),
          machineId,
          productId
        }
      });

      return res.json({
        valid: false,
        reason: 'Trial period expired'
      });
    }

    // Check product access
    if (productId) {
      const allowedProducts = license.allowedProducts as string[];
      const hasAccess = 
        license.tier === LicenseTier.UNLIMITED ||
        license.tier === LicenseTier.ENTERPRISE ||
        allowedProducts.includes(productId);

      if (!hasAccess) {
        await prisma.licenseValidation.create({
          data: {
            licenseId: license.id,
            isValid: false,
            reason: 'Product not included in license',
            ipAddress: req.ip,
            userAgent: req.get('user-agent'),
            machineId,
            productId
          }
        });

        return res.json({
          valid: false,
          reason: 'Product not included in license'
        });
      }
    }

    // Check machine ID (if provided)
    if (machineId) {
      const machineIds = license.machineIds as string[];
      const machineIdHash = LicenseGenerator.generateMachineIdHash(machineId);

      if (machineIds.length > 0 && !machineIds.includes(machineIdHash)) {
        // Check if we can add this machine
        if (machineIds.length >= license.maxMachines) {
          await prisma.licenseValidation.create({
            data: {
              licenseId: license.id,
              isValid: false,
              reason: 'Maximum machines exceeded',
              ipAddress: req.ip,
              userAgent: req.get('user-agent'),
              machineId,
              productId
            }
          });

          return res.json({
            valid: false,
            reason: 'Maximum number of machines exceeded'
          });
        }

        // Add machine ID
        await prisma.license.update({
          where: { id: license.id },
          data: {
            machineIds: [...machineIds, machineIdHash]
          }
        });
      }
    }

    // Log successful validation
    await prisma.licenseValidation.create({
      data: {
        licenseId: license.id,
        isValid: true,
        ipAddress: req.ip,
        userAgent: req.get('user-agent'),
        machineId,
        productId
      }
    });

    // Update last validated
    await prisma.license.update({
      where: { id: license.id },
      data: { lastValidated: new Date() }
    });

    // Record usage
    if (productId) {
      await prisma.usageRecord.create({
        data: {
          organizationId: license.organizationId,
          licenseId: license.id,
          productId,
          eventType: 'license_validation',
          quantity: 1
        }
      });
    }

    res.json({
      valid: true,
      license: {
        tier: license.tier,
        organization: license.organization.name,
        maxUsers: license.maxUsers,
        maxProducts: license.maxProducts,
        allowedProducts: license.allowedProducts,
        features: license.features,
        expiresAt: license.expiresAt,
        isTrial: license.isTrial,
        trialEndsAt: license.trialEndsAt
      }
    });
  })
);

/**
 * POST /api/licenses/create
 * Create a new license (admin only)
 */
router.post(
  '/create',
  authenticateAny,
  requireRole(['admin']),
  [
    body('organizationId').notEmpty().withMessage('Organization ID is required'),
    body('tier').isIn(['TRIAL', 'STARTER', 'PROFESSIONAL', 'ENTERPRISE', 'UNLIMITED']),
    body('maxUsers').optional().isInt({ min: 1 }),
    body('maxProducts').optional().isInt({ min: 1 }),
    body('allowedProducts').optional().isArray(),
    body('expiresAt').optional().isISO8601(),
    body('isTrial').optional().isBoolean()
  ],
  asyncHandler(async (req: AuthRequest, res) => {
    const {
      organizationId,
      tier,
      maxUsers,
      maxProducts,
      allowedProducts,
      expiresAt,
      isTrial
    } = req.body;

    // Verify organization exists
    const organization = await prisma.organization.findUnique({
      where: { id: organizationId }
    });

    if (!organization) {
      throw new AppError('Organization not found', 404);
    }

    // Generate license key
    const licenseKey = LicenseGenerator.generateLicenseKey();

    // Get default limits based on tier
    const tierDefaults = getTierDefaults(tier);

    // Create license
    const license = await prisma.license.create({
      data: {
        licenseKey,
        organizationId,
        tier,
        status: LicenseStatus.ACTIVE,
        maxUsers: maxUsers || tierDefaults.maxUsers,
        maxProducts: maxProducts || tierDefaults.maxProducts,
        maxApiCalls: tierDefaults.maxApiCalls,
        maxStorage: tierDefaults.maxStorage,
        allowedProducts: allowedProducts || [],
        features: tierDefaults.features,
        expiresAt: expiresAt ? new Date(expiresAt) : null,
        isTrial: isTrial || false,
        trialEndsAt: isTrial 
          ? new Date(Date.now() + 30 * 24 * 60 * 60 * 1000) 
          : null
      },
      include: { organization: true }
    });

    logger.info('License created', {
      licenseId: license.id,
      organizationId,
      tier,
      createdBy: req.user?.email
    });

    res.status(201).json({
      success: true,
      license: {
        id: license.id,
        licenseKey: license.licenseKey,
        tier: license.tier,
        status: license.status,
        organization: {
          id: organization.id,
          name: organization.name
        },
        maxUsers: license.maxUsers,
        maxProducts: license.maxProducts,
        expiresAt: license.expiresAt,
        isTrial: license.isTrial,
        trialEndsAt: license.trialEndsAt,
        createdAt: license.createdAt
      }
    });
  })
);

/**
 * GET /api/licenses/:id
 * Get license details
 */
router.get(
  '/:id',
  authenticateAny,
  asyncHandler(async (req: AuthRequest, res) => {
    const { id } = req.params;

    const license = await prisma.license.findUnique({
      where: { id },
      include: {
        organization: true,
        validations: {
          take: 10,
          orderBy: { validatedAt: 'desc' }
        }
      }
    });

    if (!license) {
      throw new AppError('License not found', 404);
    }

    // Check permissions
    if (
      req.user?.role !== 'admin' &&
      license.organizationId !== req.organization?.id
    ) {
      throw new AppError('Unauthorized', 403);
    }

    res.json({
      license: {
        id: license.id,
        licenseKey: license.licenseKey,
        tier: license.tier,
        status: license.status,
        organization: {
          id: license.organization.id,
          name: license.organization.name,
          domain: license.organization.domain
        },
        maxUsers: license.maxUsers,
        maxProducts: license.maxProducts,
        maxApiCalls: license.maxApiCalls,
        maxStorage: license.maxStorage,
        allowedProducts: license.allowedProducts,
        features: license.features,
        startDate: license.startDate,
        expiresAt: license.expiresAt,
        isTrial: license.isTrial,
        trialEndsAt: license.trialEndsAt,
        machineIds: license.machineIds,
        maxMachines: license.maxMachines,
        lastValidated: license.lastValidated,
        createdAt: license.createdAt,
        recentValidations: license.validations
      }
    });
  })
);

/**
 * GET /api/licenses
 * List licenses for organization
 */
router.get(
  '/',
  authenticateAny,
  asyncHandler(async (req: AuthRequest, res) => {
    const organizationId = req.organization?.id;

    if (!organizationId) {
      throw new AppError('Organization not found', 404);
    }

    const licenses = await prisma.license.findMany({
      where: { organizationId },
      include: { organization: true },
      orderBy: { createdAt: 'desc' }
    });

    res.json({
      licenses: licenses.map(license => ({
        id: license.id,
        licenseKey: license.licenseKey,
        tier: license.tier,
        status: license.status,
        maxUsers: license.maxUsers,
        maxProducts: license.maxProducts,
        expiresAt: license.expiresAt,
        isTrial: license.isTrial,
        lastValidated: license.lastValidated,
        createdAt: license.createdAt
      }))
    });
  })
);

/**
 * PATCH /api/licenses/:id/status
 * Update license status
 */
router.patch(
  '/:id/status',
  authenticateAny,
  requireRole(['admin']),
  [
    body('status').isIn(['ACTIVE', 'SUSPENDED', 'EXPIRED', 'CANCELLED'])
  ],
  asyncHandler(async (req: AuthRequest, res) => {
    const { id } = req.params;
    const { status } = req.body;

    const license = await prisma.license.update({
      where: { id },
      data: { status }
    });

    logger.info('License status updated', {
      licenseId: id,
      newStatus: status,
      updatedBy: req.user?.email
    });

    res.json({
      success: true,
      license: {
        id: license.id,
        status: license.status
      }
    });
  })
);

/**
 * Helper function to get tier defaults
 */
function getTierDefaults(tier: LicenseTier) {
  const defaults = {
    TRIAL: {
      maxUsers: 5,
      maxProducts: 3,
      maxApiCalls: 1000,
      maxStorage: BigInt(10 * 1024 * 1024 * 1024), // 10 GB
      features: { demo_watermark: true }
    },
    STARTER: {
      maxUsers: 25,
      maxProducts: 5,
      maxApiCalls: 10000,
      maxStorage: BigInt(100 * 1024 * 1024 * 1024), // 100 GB
      features: { email_support: true }
    },
    PROFESSIONAL: {
      maxUsers: 100,
      maxProducts: 15,
      maxApiCalls: 50000,
      maxStorage: BigInt(500 * 1024 * 1024 * 1024), // 500 GB
      features: { priority_support: true, custom_branding: true }
    },
    ENTERPRISE: {
      maxUsers: 1000,
      maxProducts: 35,
      maxApiCalls: 1000000,
      maxStorage: BigInt(2 * 1024 * 1024 * 1024 * 1024), // 2 TB
      features: { 
        dedicated_support: true, 
        custom_branding: true,
        sla: true,
        audit_logs: true
      }
    },
    UNLIMITED: {
      maxUsers: 999999,
      maxProducts: 35,
      maxApiCalls: 999999999,
      maxStorage: BigInt(10 * 1024 * 1024 * 1024 * 1024), // 10 TB
      features: {
        white_label: true,
        custom_integrations: true,
        dedicated_support: true,
        sla: true,
        audit_logs: true,
        custom_development: true
      }
    }
  };

  return defaults[tier];
}

export default router;