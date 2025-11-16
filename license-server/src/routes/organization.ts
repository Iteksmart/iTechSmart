import express from 'express';
import { body } from 'express-validator';
import { authenticateToken, AuthRequest, requireRole } from '../middleware/auth';
import { asyncHandler, AppError } from '../middleware/errorHandler';
import { prisma } from '../index';
import { LicenseGenerator } from '../utils/licenseGenerator';

const router = express.Router();

/**
 * GET /api/organizations/me
 * Get current organization details
 */
router.get(
  '/me',
  authenticateToken,
  asyncHandler(async (req: AuthRequest, res) => {
    const organizationId = req.organization?.id;

    const organization = await prisma.organization.findUnique({
      where: { id: organizationId },
      include: {
        licenses: {
          where: { status: 'ACTIVE' },
          orderBy: { createdAt: 'desc' }
        },
        users: {
          select: {
            id: true,
            email: true,
            name: true,
            role: true,
            isActive: true,
            lastLogin: true
          }
        },
        _count: {
          select: {
            licenses: true,
            users: true,
            apiKeys: true
          }
        }
      }
    });

    if (!organization) {
      throw new AppError('Organization not found', 404);
    }

    res.json({
      organization: {
        id: organization.id,
        name: organization.name,
        domain: organization.domain,
        email: organization.email,
        phone: organization.phone,
        address: organization.address,
        country: organization.country,
        createdAt: organization.createdAt,
        licenses: organization.licenses,
        users: organization.users,
        stats: {
          totalLicenses: organization._count.licenses,
          totalUsers: organization._count.users,
          totalApiKeys: organization._count.apiKeys
        }
      }
    });
  })
);

/**
 * PATCH /api/organizations/me
 * Update organization details
 */
router.patch(
  '/me',
  authenticateToken,
  requireRole(['admin']),
  [
    body('name').optional().notEmpty(),
    body('email').optional().isEmail(),
    body('phone').optional().isString(),
    body('address').optional().isString(),
    body('country').optional().isString()
  ],
  asyncHandler(async (req: AuthRequest, res) => {
    const organizationId = req.organization?.id;
    const { name, email, phone, address, country } = req.body;

    const organization = await prisma.organization.update({
      where: { id: organizationId },
      data: {
        ...(name && { name }),
        ...(email && { email }),
        ...(phone && { phone }),
        ...(address && { address }),
        ...(country && { country })
      }
    });

    res.json({
      success: true,
      organization: {
        id: organization.id,
        name: organization.name,
        domain: organization.domain,
        email: organization.email,
        phone: organization.phone,
        address: organization.address,
        country: organization.country
      }
    });
  })
);

/**
 * GET /api/organizations/me/api-keys
 * Get organization API keys
 */
router.get(
  '/me/api-keys',
  authenticateToken,
  asyncHandler(async (req: AuthRequest, res) => {
    const organizationId = req.organization?.id;

    const apiKeys = await prisma.apiKey.findMany({
      where: { organizationId },
      orderBy: { createdAt: 'desc' }
    });

    res.json({
      apiKeys: apiKeys.map(key => ({
        id: key.id,
        name: key.name,
        key: key.key,
        scopes: key.scopes,
        isActive: key.isActive,
        expiresAt: key.expiresAt,
        lastUsed: key.lastUsed,
        usageCount: key.usageCount,
        createdAt: key.createdAt
      }))
    });
  })
);

/**
 * POST /api/organizations/me/api-keys
 * Create new API key
 */
router.post(
  '/me/api-keys',
  authenticateToken,
  requireRole(['admin']),
  [
    body('name').notEmpty().withMessage('API key name is required'),
    body('scopes').optional().isArray(),
    body('expiresAt').optional().isISO8601()
  ],
  asyncHandler(async (req: AuthRequest, res) => {
    const organizationId = req.organization?.id;
    const userId = req.user?.id;
    const { name, scopes, expiresAt } = req.body;

    // Generate API key
    const key = LicenseGenerator.generateApiKey();

    const apiKey = await prisma.apiKey.create({
      data: {
        key,
        name,
        organizationId: organizationId!,
        userId,
        scopes: scopes || ['read'],
        expiresAt: expiresAt ? new Date(expiresAt) : null
      }
    });

    res.status(201).json({
      success: true,
      apiKey: {
        id: apiKey.id,
        name: apiKey.name,
        key: apiKey.key,
        scopes: apiKey.scopes,
        expiresAt: apiKey.expiresAt,
        createdAt: apiKey.createdAt
      }
    });
  })
);

/**
 * DELETE /api/organizations/me/api-keys/:id
 * Delete API key
 */
router.delete(
  '/me/api-keys/:id',
  authenticateToken,
  requireRole(['admin']),
  asyncHandler(async (req: AuthRequest, res) => {
    const { id } = req.params;
    const organizationId = req.organization?.id;

    // Verify API key belongs to organization
    const apiKey = await prisma.apiKey.findFirst({
      where: { id, organizationId }
    });

    if (!apiKey) {
      throw new AppError('API key not found', 404);
    }

    await prisma.apiKey.delete({
      where: { id }
    });

    res.json({
      success: true,
      message: 'API key deleted successfully'
    });
  })
);

/**
 * GET /api/organizations/me/usage
 * Get organization usage statistics
 */
router.get(
  '/me/usage',
  authenticateToken,
  asyncHandler(async (req: AuthRequest, res) => {
    const organizationId = req.organization?.id;
    const { startDate, endDate, productId } = req.query;

    const where: any = { organizationId };

    if (startDate || endDate) {
      where.recordedAt = {};
      if (startDate) where.recordedAt.gte = new Date(startDate as string);
      if (endDate) where.recordedAt.lte = new Date(endDate as string);
    }

    if (productId) {
      where.productId = productId;
    }

    const usage = await prisma.usageRecord.groupBy({
      by: ['productId', 'eventType'],
      where,
      _sum: {
        quantity: true
      },
      _count: true
    });

    const totalRecords = await prisma.usageRecord.count({ where });

    res.json({
      usage: usage.map(record => ({
        productId: record.productId,
        eventType: record.eventType,
        totalQuantity: record._sum.quantity,
        recordCount: record._count
      })),
      totalRecords
    });
  })
);

export default router;