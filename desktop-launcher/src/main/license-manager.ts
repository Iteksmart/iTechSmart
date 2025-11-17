import Store from 'electron-store';
import axios from 'axios';
import { machineIdSync } from 'node-machine-id';
import crypto from 'crypto';

interface License {
  key: string;
  tier: 'trial' | 'starter' | 'professional' | 'enterprise' | 'unlimited';
  email: string;
  organization: string;
  expiresAt: string;
  products: string[];
  maxUsers: number;
  features: Record<string, any>;
  isTrial: boolean;
  trialEndsAt?: string;
}

export class LicenseManager {
  private store: Store;
  private licenseServerUrl: string;

  constructor() {
    this.store = new Store();
    this.licenseServerUrl = process.env.LICENSE_SERVER_URL || 'https://license.itechsmart.dev/api';
  }

  /**
   * Activate license with server
   */
  async activateLicense(licenseKey: string): Promise<{ success: boolean; message: string }> {
    try {
      const machineId = this.getMachineId();

      const response = await axios.post(`${this.licenseServerUrl}/licenses/validate`, {
        licenseKey,
        machineId
      });

      if (response.data.valid) {
        // Store license locally
        this.store.set('license', {
          key: licenseKey,
          ...response.data.license,
          activatedAt: new Date().toISOString(),
          machineId
        });

        return {
          success: true,
          message: 'License activated successfully'
        };
      } else {
        return {
          success: false,
          message: response.data.reason || 'Invalid license key'
        };
      }
    } catch (error) {
      console.error('License activation failed:', error);
      return {
        success: false,
        message: 'Failed to activate license. Please check your internet connection.'
      };
    }
  }

  /**
   * Validate license with server
   */
  async validateLicense(): Promise<boolean> {
    const license = this.getLicense();

    if (!license) {
      // Start trial if no license
      return this.startTrial();
    }

    // Check expiration locally first
    if (license.expiresAt && new Date(license.expiresAt) < new Date()) {
      return false;
    }

    // Check trial expiration
    if (license.isTrial && license.trialEndsAt && new Date(license.trialEndsAt) < new Date()) {
      return false;
    }

    // Validate with server (every 24 hours)
    const lastValidation = this.store.get('lastValidation') as string;
    const now = new Date();
    const dayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

    if (!lastValidation || new Date(lastValidation) < dayAgo) {
      try {
        const machineId = this.getMachineId();
        const response = await axios.post(`${this.licenseServerUrl}/licenses/validate`, {
          licenseKey: license.key,
          machineId
        });

        this.store.set('lastValidation', now.toISOString());

        if (!response.data.valid) {
          return false;
        }

        // Update license data
        this.store.set('license', {
          ...license,
          ...response.data.license
        });
      } catch (error) {
        console.error('License validation failed:', error);
        // Allow offline usage for up to 7 days
        const sevenDaysAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        if (lastValidation && new Date(lastValidation) > sevenDaysAgo) {
          return true;
        }
        return false;
      }
    }

    return true;
  }

  /**
   * Start trial license
   */
  async startTrial(): Promise<boolean> {
    const trialLicense: License = {
      key: 'TRIAL-' + this.generateTrialKey(),
      tier: 'trial',
      email: '',
      organization: '',
      expiresAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
      products: ['itechsmart-ninja', 'itechsmart-enterprise', 'itechsmart-analytics'],
      maxUsers: 5,
      features: { demo_watermark: true },
      isTrial: true,
      trialEndsAt: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString()
    };

    this.store.set('license', trialLicense);
    this.store.set('lastValidation', new Date().toISOString());
    return true;
  }

  /**
   * Get current license
   */
  getLicense(): License | null {
    return this.store.get('license') as License | null;
  }

  /**
   * Check if user can access a product
   */
  canAccessProduct(productId: string): boolean {
    const license = this.getLicense();
    if (!license) return false;

    if (license.tier === 'unlimited' || license.tier === 'enterprise') {
      return true;
    }

    return license.products.includes(productId);
  }

  /**
   * Get machine ID
   */
  private getMachineId(): string {
    try {
      return machineIdSync();
    } catch (error) {
      // Fallback to generated ID
      let id = this.store.get('machineId') as string;
      if (!id) {
        id = crypto.randomBytes(16).toString('hex');
        this.store.set('machineId', id);
      }
      return id;
    }
  }

  /**
   * Generate trial key
   */
  private generateTrialKey(): string {
    return crypto.randomBytes(8).toString('hex').toUpperCase();
  }

  /**
   * Get days remaining
   */
  getDaysRemaining(): number {
    const license = this.getLicense();
    if (!license) return 0;

    const expiresAt = license.isTrial && license.trialEndsAt 
      ? new Date(license.trialEndsAt)
      : license.expiresAt 
        ? new Date(license.expiresAt)
        : null;

    if (!expiresAt) return 999;

    const now = new Date();
    const diff = expiresAt.getTime() - now.getTime();
    return Math.ceil(diff / (1000 * 60 * 60 * 24));
  }

  /**
   * Clear license (for testing)
   */
  clearLicense(): void {
    this.store.delete('license');
    this.store.delete('lastValidation');
  }
}