import crypto from 'crypto';
import { v4 as uuidv4 } from 'uuid';

export class LicenseGenerator {
  /**
   * Generate a license key in format: XXXX-XXXX-XXXX-XXXX-XXXX
   */
  static generateLicenseKey(): string {
    const segments = 5;
    const segmentLength = 4;
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789'; // Exclude similar chars
    
    const key = Array.from({ length: segments }, () => {
      return Array.from({ length: segmentLength }, () => {
        return chars[Math.floor(Math.random() * chars.length)];
      }).join('');
    }).join('-');
    
    return key;
  }

  /**
   * Generate a secure API key
   */
  static generateApiKey(): string {
    return `itsk_${crypto.randomBytes(32).toString('hex')}`;
  }

  /**
   * Generate a webhook secret
   */
  static generateWebhookSecret(): string {
    return `whsec_${crypto.randomBytes(32).toString('hex')}`;
  }

  /**
   * Hash a license key for storage
   */
  static hashLicenseKey(key: string): string {
    return crypto
      .createHash('sha256')
      .update(key)
      .digest('hex');
  }

  /**
   * Encrypt sensitive data
   */
  static encrypt(text: string): string {
    const algorithm = 'aes-256-cbc';
    const key = Buffer.from(process.env.ENCRYPTION_KEY || '', 'base64');
    const iv = crypto.randomBytes(16);
    
    const cipher = crypto.createCipheriv(algorithm, key, iv);
    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');
    
    return `${iv.toString('hex')}:${encrypted}`;
  }

  /**
   * Decrypt sensitive data
   */
  static decrypt(text: string): string {
    const algorithm = 'aes-256-cbc';
    const key = Buffer.from(process.env.ENCRYPTION_KEY || '', 'base64');
    
    const [ivHex, encryptedHex] = text.split(':');
    const iv = Buffer.from(ivHex, 'hex');
    
    const decipher = crypto.createDecipheriv(algorithm, key, iv);
    let decrypted = decipher.update(encryptedHex, 'hex', 'utf8');
    decrypted += decipher.final('utf8');
    
    return decrypted;
  }

  /**
   * Generate machine ID hash
   */
  static generateMachineIdHash(machineId: string): string {
    return crypto
      .createHash('sha256')
      .update(machineId)
      .digest('hex');
  }

  /**
   * Validate license key format
   */
  static isValidLicenseKeyFormat(key: string): boolean {
    const pattern = /^[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}-[A-Z0-9]{4}$/;
    return pattern.test(key);
  }
}