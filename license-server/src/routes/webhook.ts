import express from 'express';
import { body } from 'express-validator';
import { authenticateToken, AuthRequest, requireRole } from '../middleware/auth';
import { asyncHandler, AppError } from '../middleware/errorHandler';
import { prisma } from '../index';
import { LicenseGenerator } from '../utils/licenseGenerator';

const router = express.Router();

/**
 * GET /api/webhooks
 * List webhooks for organization
 */
router.get(
  '/',
  authenticateToken,
  asyncHandler(async (req: AuthRequest, res) => {
    const organizationId = req.organization?.id;

    const webhooks = await prisma.webhook.findMany({
      where: { organizationId },
      orderBy: { createdAt: 'desc' }
    });

    res.json({
      webhooks: webhooks.map(webhook => ({
        id: webhook.id,
        url: webhook.url,
        events: webhook.events,
        isActive: webhook.isActive,
        lastTriggered: webhook.lastTriggered,
        successCount: webhook.successCount,
        failureCount: webhook.failureCount,
        createdAt: webhook.createdAt
      }))
    });
  })
);

/**
 * POST /api/webhooks
 * Create new webhook
 */
router.post(
  '/',
  authenticateToken,
  requireRole(['admin']),
  [
    body('url').isURL().withMessage('Valid URL is required'),
    body('events').isArray().withMessage('Events array is required')
  ],
  asyncHandler(async (req: AuthRequest, res) => {
    const organizationId = req.organization?.id;
    const { url, events } = req.body;

    // Generate webhook secret
    const secret = LicenseGenerator.generateWebhookSecret();

    const webhook = await prisma.webhook.create({
      data: {
        organizationId: organizationId!,
        url,
        events,
        secret
      }
    });

    res.status(201).json({
      success: true,
      webhook: {
        id: webhook.id,
        url: webhook.url,
        events: webhook.events,
        secret: webhook.secret,
        isActive: webhook.isActive,
        createdAt: webhook.createdAt
      }
    });
  })
);

/**
 * DELETE /api/webhooks/:id
 * Delete webhook
 */
router.delete(
  '/:id',
  authenticateToken,
  requireRole(['admin']),
  asyncHandler(async (req: AuthRequest, res) => {
    const { id } = req.params;
    const organizationId = req.organization?.id;

    // Verify webhook belongs to organization
    const webhook = await prisma.webhook.findFirst({
      where: { id, organizationId }
    });

    if (!webhook) {
      throw new AppError('Webhook not found', 404);
    }

    await prisma.webhook.delete({
      where: { id }
    });

    res.json({
      success: true,
      message: 'Webhook deleted successfully'
    });
  })
);

export default router;