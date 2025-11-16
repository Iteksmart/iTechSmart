import express from 'express';
import { body } from 'express-validator';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import { asyncHandler, AppError } from '../middleware/errorHandler';
import { strictRateLimiter } from '../middleware/rateLimiter';
import { prisma } from '../index';
import { logger } from '../utils/logger';

const router = express.Router();

/**
 * POST /api/auth/register
 * Register a new organization and admin user
 */
router.post(
  '/register',
  strictRateLimiter,
  [
    body('organizationName').notEmpty().withMessage('Organization name is required'),
    body('domain').notEmpty().withMessage('Domain is required'),
    body('email').isEmail().withMessage('Valid email is required'),
    body('password').isLength({ min: 8 }).withMessage('Password must be at least 8 characters'),
    body('name').notEmpty().withMessage('Name is required')
  ],
  asyncHandler(async (req, res) => {
    const { organizationName, domain, email, password, name, phone, address, country } = req.body;

    // Check if organization already exists
    const existingOrg = await prisma.organization.findUnique({
      where: { domain }
    });

    if (existingOrg) {
      throw new AppError('Organization with this domain already exists', 400);
    }

    // Check if user already exists
    const existingUser = await prisma.user.findUnique({
      where: { email }
    });

    if (existingUser) {
      throw new AppError('User with this email already exists', 400);
    }

    // Hash password
    const passwordHash = await bcrypt.hash(password, 12);

    // Create organization and admin user in a transaction
    const result = await prisma.$transaction(async (tx) => {
      // Create organization
      const organization = await tx.organization.create({
        data: {
          name: organizationName,
          domain,
          email,
          phone,
          address,
          country
        }
      });

      // Create admin user
      const user = await tx.user.create({
        data: {
          email,
          passwordHash,
          name,
          role: 'admin',
          organizationId: organization.id,
          isActive: true
        }
      });

      // Create trial license
      const trialEndsAt = new Date();
      trialEndsAt.setDate(trialEndsAt.getDate() + 30);

      const license = await tx.license.create({
        data: {
          licenseKey: generateTrialLicenseKey(),
          organizationId: organization.id,
          tier: 'TRIAL',
          status: 'ACTIVE',
          maxUsers: 5,
          maxProducts: 3,
          maxApiCalls: 1000,
          maxStorage: BigInt(10 * 1024 * 1024 * 1024),
          allowedProducts: ['itechsmart-ninja', 'itechsmart-enterprise', 'itechsmart-analytics'],
          features: { demo_watermark: true },
          isTrial: true,
          trialEndsAt
        }
      });

      return { organization, user, license };
    });

    logger.info('New organization registered', {
      organizationId: result.organization.id,
      domain,
      email
    });

    // Generate JWT token
    const token = jwt.sign(
      { userId: result.user.id, organizationId: result.organization.id },
      process.env.JWT_SECRET!,
      { expiresIn: '7d' }
    );

    res.status(201).json({
      success: true,
      message: 'Organization registered successfully',
      token,
      user: {
        id: result.user.id,
        email: result.user.email,
        name: result.user.name,
        role: result.user.role
      },
      organization: {
        id: result.organization.id,
        name: result.organization.name,
        domain: result.organization.domain
      },
      license: {
        licenseKey: result.license.licenseKey,
        tier: result.license.tier,
        trialEndsAt: result.license.trialEndsAt
      }
    });
  })
);

/**
 * POST /api/auth/login
 * Login user
 */
router.post(
  '/login',
  strictRateLimiter,
  [
    body('email').isEmail().withMessage('Valid email is required'),
    body('password').notEmpty().withMessage('Password is required')
  ],
  asyncHandler(async (req, res) => {
    const { email, password } = req.body;

    // Find user
    const user = await prisma.user.findUnique({
      where: { email },
      include: { organization: true }
    });

    if (!user) {
      throw new AppError('Invalid email or password', 401);
    }

    // Check if user is active
    if (!user.isActive) {
      throw new AppError('Account is inactive', 401);
    }

    // Verify password
    const isValidPassword = await bcrypt.compare(password, user.passwordHash);

    if (!isValidPassword) {
      throw new AppError('Invalid email or password', 401);
    }

    // Update last login
    await prisma.user.update({
      where: { id: user.id },
      data: { lastLogin: new Date() }
    });

    // Generate JWT token
    const token = jwt.sign(
      { userId: user.id, organizationId: user.organizationId },
      process.env.JWT_SECRET!,
      { expiresIn: '7d' }
    );

    logger.info('User logged in', {
      userId: user.id,
      email: user.email,
      organizationId: user.organizationId
    });

    res.json({
      success: true,
      token,
      user: {
        id: user.id,
        email: user.email,
        name: user.name,
        role: user.role
      },
      organization: {
        id: user.organization.id,
        name: user.organization.name,
        domain: user.organization.domain
      }
    });
  })
);

/**
 * POST /api/auth/refresh
 * Refresh JWT token
 */
router.post(
  '/refresh',
  asyncHandler(async (req, res) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (!token) {
      throw new AppError('Token required', 401);
    }

    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET!) as any;

      // Generate new token
      const newToken = jwt.sign(
        { userId: decoded.userId, organizationId: decoded.organizationId },
        process.env.JWT_SECRET!,
        { expiresIn: '7d' }
      );

      res.json({
        success: true,
        token: newToken
      });
    } catch (error) {
      throw new AppError('Invalid or expired token', 401);
    }
  })
);

/**
 * Helper function to generate trial license key
 */
function generateTrialLicenseKey(): string {
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  const segments = 5;
  const segmentLength = 4;

  return Array.from({ length: segments }, () => {
    return Array.from({ length: segmentLength }, () => {
      return chars[Math.floor(Math.random() * chars.length)];
    }).join('');
  }).join('-');
}

export default router;