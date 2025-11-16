import Docker from 'dockerode';
import { exec } from 'child_process';
import { promisify } from 'util';
import { PRODUCTS, Product } from './products';
import si from 'systeminformation';

const execAsync = promisify(exec);

export class DockerManager {
  private docker: Docker;

  constructor() {
    this.docker = new Docker();
  }

  /**
   * Check if Docker is installed and running
   */
  async checkDockerInstalled(): Promise<boolean> {
    try {
      await this.docker.ping();
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Install Docker Desktop (platform-specific)
   */
  async installDocker(): Promise<boolean> {
    const platform = process.platform;

    try {
      if (platform === 'win32') {
        // Windows: Download and run Docker Desktop installer
        const url = 'https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe';
        await execAsync(`powershell -Command "Start-Process '${url}'"`);
      } else if (platform === 'darwin') {
        // macOS: Download and install Docker Desktop
        const url = 'https://desktop.docker.com/mac/main/amd64/Docker.dmg';
        await execAsync(`open '${url}'`);
      } else {
        // Linux: Install via package manager
        await execAsync('curl -fsSL https://get.docker.com | sh');
      }
      return true;
    } catch (error) {
      console.error('Failed to install Docker:', error);
      return false;
    }
  }

  /**
   * Pull Docker image
   */
  private async pullImage(imageName: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.docker.pull(imageName, (err: any, stream: any) => {
        if (err) return reject(err);

        this.docker.modem.followProgress(stream, (err: any) => {
          if (err) return reject(err);
          resolve();
        }, (event: any) => {
          // Progress callback
          console.log('Pull progress:', event);
        });
      });
    });
  }

  /**
   * Start a product
   */
  async startProduct(productId: string): Promise<boolean> {
    try {
      const product = PRODUCTS.find(p => p.id === productId);
      if (!product) {
        throw new Error(`Product ${productId} not found`);
      }

      // Check if containers already exist
      const backendExists = await this.containerExists(`${productId}-backend`);
      const frontendExists = await this.containerExists(`${productId}-frontend`);

      // Pull images if containers don't exist
      if (!backendExists) {
        console.log(`Pulling backend image for ${productId}...`);
        await this.pullImage(`ghcr.io/iteksmart/${productId}-backend:main`);
      }

      if (!frontendExists) {
        console.log(`Pulling frontend image for ${productId}...`);
        await this.pullImage(`ghcr.io/iteksmart/${productId}-frontend:main`);
      }

      // Start backend
      if (backendExists) {
        const backend = this.docker.getContainer(`${productId}-backend`);
        const info = await backend.inspect();
        if (!info.State.Running) {
          await backend.start();
        }
      } else {
        await this.createAndStartContainer(
          `${productId}-backend`,
          `ghcr.io/iteksmart/${productId}-backend:main`,
          product.backendPort,
          8000
        );
      }

      // Start frontend
      if (frontendExists) {
        const frontend = this.docker.getContainer(`${productId}-frontend`);
        const info = await frontend.inspect();
        if (!info.State.Running) {
          await frontend.start();
        }
      } else {
        await this.createAndStartContainer(
          `${productId}-frontend`,
          `ghcr.io/iteksmart/${productId}-frontend:main`,
          product.frontendPort,
          80
        );
      }

      return true;
    } catch (error) {
      console.error(`Failed to start ${productId}:`, error);
      return false;
    }
  }

  /**
   * Stop a product
   */
  async stopProduct(productId: string): Promise<boolean> {
    try {
      const backend = this.docker.getContainer(`${productId}-backend`);
      const frontend = this.docker.getContainer(`${productId}-frontend`);

      await backend.stop();
      await frontend.stop();

      return true;
    } catch (error) {
      console.error(`Failed to stop ${productId}:`, error);
      return false;
    }
  }

  /**
   * Get product status
   */
  async getProductStatus(productId: string): Promise<'running' | 'stopped' | 'error'> {
    try {
      const backend = this.docker.getContainer(`${productId}-backend`);
      const info = await backend.inspect();
      return info.State.Running ? 'running' : 'stopped';
    } catch (error) {
      return 'stopped';
    }
  }

  /**
   * Check if container exists
   */
  private async containerExists(name: string): Promise<boolean> {
    try {
      const container = this.docker.getContainer(name);
      await container.inspect();
      return true;
    } catch (error) {
      return false;
    }
  }

  /**
   * Create and start container
   */
  private async createAndStartContainer(
    name: string,
    image: string,
    hostPort: number,
    containerPort: number
  ): Promise<void> {
    const container = await this.docker.createContainer({
      Image: image,
      name,
      ExposedPorts: {
        [`${containerPort}/tcp`]: {}
      },
      HostConfig: {
        PortBindings: {
          [`${containerPort}/tcp`]: [{ HostPort: hostPort.toString() }]
        },
        RestartPolicy: {
          Name: 'unless-stopped'
        }
      }
    });

    await container.start();
  }

  /**
   * Get system information
   */
  async getSystemInfo() {
    try {
      const cpu = await si.cpu();
      const mem = await si.mem();
      const disk = await si.fsSize();
      const dockerInfo = await this.docker.info();

      return {
        cpu: {
          manufacturer: cpu.manufacturer,
          brand: cpu.brand,
          cores: cpu.cores,
          speed: cpu.speed
        },
        memory: {
          total: mem.total,
          free: mem.free,
          used: mem.used
        },
        disk: disk.map(d => ({
          fs: d.fs,
          size: d.size,
          used: d.used,
          available: d.available
        })),
        docker: {
          containers: dockerInfo.Containers,
          containersRunning: dockerInfo.ContainersRunning,
          containersPaused: dockerInfo.ContainersPaused,
          containersStopped: dockerInfo.ContainersStopped,
          images: dockerInfo.Images
        }
      };
    } catch (error) {
      console.error('Failed to get system info:', error);
      return null;
    }
  }

  /**
   * Clean up unused Docker resources
   */
  async cleanup(): Promise<void> {
    try {
      await this.docker.pruneContainers();
      await this.docker.pruneImages();
      await this.docker.pruneVolumes();
      await this.docker.pruneNetworks();
    } catch (error) {
      console.error('Failed to cleanup Docker resources:', error);
    }
  }
}