import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { prisma } from '../index';
import { logger } from '../utils/logger';

export interface AuthRequest extends Request {
  user?: {
    id: string;
    email: string;
    organizationId: string;
    role: string;
  };
  organization?: {
    id: string;
    name: string;
    domain: string;
  };
}

/**
 * Verify JWT token
 */
export const authenticateToken = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  try {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

    if (!token) {
      return res.status(401).json({ error: 'Access token required' });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET!) as any;

    // Fetch user from database
    const user = await prisma.user.findUnique({
      where: { id: decoded.userId },
      include: { organization: true }
    });

    if (!user || !user.isActive) {
      return res.status(401).json({ error: 'Invalid or inactive user' });
    }

    req.user = {
      id: user.id,
      email: user.email,
      organizationId: user.organizationId,
      role: user.role
    };

    req.organization = {
      id: user.organization.id,
      name: user.organization.name,
      domain: user.organization.domain
    };

    next();
  } catch (error) {
    logger.error('Authentication error:', error);
    return res.status(403).json({ error: 'Invalid or expired token' });
  }
};

/**
 * Verify API key
 */
export const authenticateApiKey = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  try {
    const apiKey = req.headers['x-api-key'] as string;

    if (!apiKey) {
      return res.status(401).json({ error: 'API key required' });
    }

    // Fetch API key from database
    const keyRecord = await prisma.apiKey.findUnique({
      where: { key: apiKey },
      include: { organization: true }
    });

    if (!keyRecord || !keyRecord.isActive) {
      return res.status(401).json({ error: 'Invalid or inactive API key' });
    }

    // Check expiration
    if (keyRecord.expiresAt && keyRecord.expiresAt < new Date()) {
      return res.status(401).json({ error: 'API key expired' });
    }

    // Update usage stats
    await prisma.apiKey.update({
      where: { id: keyRecord.id },
      data: {
        lastUsed: new Date(),
        usageCount: { increment: 1 }
      }
    });

    req.organization = {
      id: keyRecord.organization.id,
      name: keyRecord.organization.name,
      domain: keyRecord.organization.domain
    };

    next();
  } catch (error) {
    logger.error('API key authentication error:', error);
    return res.status(403).json({ error: 'Invalid API key' });
  }
};

/**
 * Check if user has required role
 */
export const requireRole = (roles: string[]) => {
  return (req: AuthRequest, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }

    next();
  };
};

/**
 * Authenticate with either JWT or API key
 */
export const authenticateAny = async (
  req: AuthRequest,
  res: Response,
  next: NextFunction
) => {
  const authHeader = req.headers['authorization'];
  const apiKey = req.headers['x-api-key'];

  if (authHeader) {
    return authenticateToken(req, res, next);
  } else if (apiKey) {
    return authenticateApiKey(req, res, next);
  } else {
    return res.status(401).json({ error: 'Authentication required' });
  }
};