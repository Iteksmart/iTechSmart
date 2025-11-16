import express from 'express';
import { body } from 'express-validator';
import { authenticateAny, AuthRequest } from '../middleware/auth';
import { asyncHandler } from '../middleware/errorHandler';
import { prisma } from '../index';

const router = express.Router();

/**
 * POST /api/usage/record
 * Record usage event
 */
router.post(
  '/record',
  authenticateAny,
  [
    body('licenseKey').notEmpty().withMessage('License key is required'),
    body('productId').notEmpty().withMessage('Product ID is required'),
    body('eventType').notEmpty().withMessage('Event type is required'),
    body('quantity').optional().isInt({ min: 1 }),
    body('metadata').optional().isObject()
  ],
  asyncHandler(async (req: AuthRequest, res) => {
    const { licenseKey, productId, eventType, quantity, metadata } = req.body;

    // Find license
    const license = await prisma.license.findUnique({
      where: { licenseKey }
    });

    if (!license) {
      return res.status(404).json({ error: 'License not found' });
    }

    // Record usage
    await prisma.usageRecord.create({
      data: {
        organizationId: license.organizationId,
        licenseId: license.id,
        productId,
        eventType,
        quantity: quantity || 1,
        metadata: metadata || {}
      }
    });

    res.json({
      success: true,
      message: 'Usage recorded successfully'
    });
  })
);

/**
 * GET /api/usage/summary
 * Get usage summary for organization
 */
router.get(
  '/summary',
  authenticateAny,
  asyncHandler(async (req: AuthRequest, res) => {
    const organizationId = req.organization?.id;
    const { period } = req.query; // 'day', 'week', 'month'

    let startDate = new Date();
    
    switch (period) {
      case 'day':
        startDate.setDate(startDate.getDate() - 1);
        break;
      case 'week':
        startDate.setDate(startDate.getDate() - 7);
        break;
      case 'month':
        startDate.setMonth(startDate.getMonth() - 1);
        break;
      default:
        startDate.setDate(startDate.getDate() - 30);
    }

    const usage = await prisma.usageRecord.groupBy({
      by: ['productId', 'eventType'],
      where: {
        organizationId,
        recordedAt: { gte: startDate }
      },
      _sum: {
        quantity: true
      },
      _count: true
    });

    res.json({
      period: period || 'month',
      startDate,
      endDate: new Date(),
      usage: usage.map(record => ({
        productId: record.productId,
        eventType: record.eventType,
        totalQuantity: record._sum.quantity,
        recordCount: record._count
      }))
    });
  })
);

export default router;