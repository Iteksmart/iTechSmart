# iTechSmart Suite - Ansible Automation

Automated deployment and configuration management for the iTechSmart Suite using Ansible.

## Overview

This Ansible playbook automates the complete deployment of all 33 iTechSmart products, including:
- System preparation and hardening
- Docker installation and configuration
- Database and Redis deployment
- All 33 product deployments
- Monitoring and backup setup
- Health checks and verification

## Prerequisites

### Control Node (Your Machine)
- Ansible >= 2.14 installed
- Python >= 3.8
- SSH access to target servers
- AWS/Azure/GCP credentials (if using cloud)

### Target Servers
- Ubuntu 20.04+ or CentOS 8+ (recommended)
- Minimum 16GB RAM, 8 CPU cores
- 200GB+ disk space
- Root or sudo access
- Open ports: 22 (SSH), 80 (HTTP), 443 (HTTPS), 8001-8033 (backends), 3001-3033 (frontends)

## Installation

### 1. Install Ansible

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ansible
```

**macOS:**
```bash
brew install ansible
```

**Python pip:**
```bash
pip install ansible
```

### 2. Clone Repository

```bash
git clone https://github.com/itechsmart/suite.git
cd suite/infrastructure/ansible
```

### 3. Install Required Collections

```bash
ansible-galaxy collection install community.docker
ansible-galaxy collection install community.postgresql
```

## Configuration

### 1. Configure Inventory

Edit `inventory/hosts.ini` with your server details:

```ini
[itechsmart_servers]
prod-server-1 ansible_host=YOUR_SERVER_IP ansible_user=ubuntu
```

### 2. Configure Variables

Edit environment-specific variables in `vars/`:
- `vars/production.yml` - Production settings
- `vars/staging.yml` - Staging settings
- `vars/development.yml` - Development settings

### 3. Set Secrets

Create an Ansible Vault for sensitive data:

```bash
ansible-vault create vars/vault.yml
```

Add your secrets:
```yaml
vault_database_password: "your-secure-password"
vault_redis_password: "your-secure-password"
vault_secret_key: "your-secret-key"
```

## Deployment

### Quick Start

Deploy to production:
```bash
ansible-playbook -i inventory/hosts.ini playbook.yml \
  --extra-vars "environment=production" \
  --ask-vault-pass
```

### Step-by-Step Deployment

#### 1. Test Connection
```bash
ansible -i inventory/hosts.ini all -m ping
```

#### 2. Check Playbook Syntax
```bash
ansible-playbook -i inventory/hosts.ini playbook.yml --syntax-check
```

#### 3. Dry Run
```bash
ansible-playbook -i inventory/hosts.ini playbook.yml --check
```

#### 4. Deploy
```bash
ansible-playbook -i inventory/hosts.ini playbook.yml \
  --extra-vars "environment=production" \
  --ask-vault-pass
```

### Environment-Specific Deployments

**Development:**
```bash
ansible-playbook -i inventory/hosts.ini playbook.yml \
  --extra-vars "environment=development" \
  --limit itechsmart_dev
```

**Staging:**
```bash
ansible-playbook -i inventory/hosts.ini playbook.yml \
  --extra-vars "environment=staging" \
  --limit itechsmart_staging
```

**Production:**
```bash
ansible-playbook -i inventory/hosts.ini playbook.yml \
  --extra-vars "environment=production" \
  --limit itechsmart_servers
```

## Playbook Structure

```
ansible/
├── playbook.yml              # Main playbook
├── inventory/
│   └── hosts.ini            # Server inventory
├── vars/
│   ├── production.yml       # Production variables
│   ├── staging.yml          # Staging variables
│   └── development.yml      # Development variables
├── tasks/
│   ├── system-prep.yml      # System preparation
│   ├── docker-install.yml   # Docker installation
│   ├── firewall-config.yml  # Firewall configuration
│   ├── database-deploy.yml  # Database deployment
│   ├── redis-deploy.yml     # Redis deployment
│   ├── products-deploy.yml  # Products deployment
│   ├── monitoring-setup.yml # Monitoring setup
│   ├── backup-setup.yml     # Backup configuration
│   ├── health-checks.yml    # Health verification
│   └── verify-deployment.yml # Deployment verification
├── templates/
│   ├── docker-compose.yml.j2 # Docker Compose template
│   └── .env.j2               # Environment template
└── README.md                 # This file
```

## Common Tasks

### Deploy Single Product

```bash
ansible-playbook -i inventory/hosts.ini playbook.yml \
  --tags "product-deploy" \
  --extra-vars "product_name=enterprise"
```

### Update All Products

```bash
ansible-playbook -i inventory/hosts.ini playbook.yml \
  --tags "update" \
  --extra-vars "itechsmart_version=1.1.0"
```

### Restart Services

```bash
ansible-playbook -i inventory/hosts.ini playbook.yml \
  --tags "restart"
```

### Run Health Checks

```bash
ansible-playbook -i inventory/hosts.ini playbook.yml \
  --tags "health-check"
```

### Backup Database

```bash
ansible-playbook -i inventory/hosts.ini playbook.yml \
  --tags "backup"
```

## Tags

Available tags for selective execution:
- `system-prep` - System preparation only
- `docker` - Docker installation only
- `database` - Database deployment only
- `redis` - Redis deployment only
- `products` - Products deployment only
- `monitoring` - Monitoring setup only
- `backup` - Backup configuration only
- `health-check` - Health checks only
- `update` - Update products
- `restart` - Restart services

## Variables

### Required Variables
- `environment` - Environment name (production/staging/development)
- `vault_database_password` - Database password (in vault)
- `vault_redis_password` - Redis password (in vault)

### Optional Variables
- `itechsmart_version` - Version to deploy (default: 1.0.0)
- `itechsmart_base_dir` - Installation directory (default: /opt/itechsmart)
- `docker_registry` - Docker registry URL
- `enable_monitoring` - Enable monitoring (default: true)
- `enable_backup` - Enable backups (default: true)

## Troubleshooting

### Connection Issues

**Problem:** Cannot connect to servers
```bash
# Test SSH connection
ssh -i ~/.ssh/key.pem user@server

# Verify inventory
ansible-inventory -i inventory/hosts.ini --list
```

### Permission Issues

**Problem:** Permission denied
```bash
# Use sudo
ansible-playbook -i inventory/hosts.ini playbook.yml --become --ask-become-pass
```

### Docker Issues

**Problem:** Docker not starting
```bash
# Check Docker status on target
ansible -i inventory/hosts.ini all -m shell -a "systemctl status docker"

# Restart Docker
ansible -i inventory/hosts.ini all -m shell -a "systemctl restart docker" --become
```

### Deployment Failures

**Problem:** Deployment fails
```bash
# Run with verbose output
ansible-playbook -i inventory/hosts.ini playbook.yml -vvv

# Check logs on target
ansible -i inventory/hosts.ini all -m shell -a "docker logs itechsmart-enterprise"
```

## Best Practices

### Security
1. Always use Ansible Vault for sensitive data
2. Use SSH keys instead of passwords
3. Limit SSH access by IP
4. Enable firewall on all servers
5. Regularly update systems and packages

### Performance
1. Use pipelining for faster execution
2. Enable fact caching
3. Use async tasks for long-running operations
4. Limit parallelism based on resources

### Maintenance
1. Keep playbooks in version control
2. Test changes in development first
3. Document custom modifications
4. Maintain separate inventories per environment
5. Regular backup of Ansible vault

## Advanced Usage

### Custom Roles

Create custom roles for specific needs:
```bash
ansible-galaxy init roles/custom-role
```

### Dynamic Inventory

Use dynamic inventory for cloud providers:
```bash
# AWS
ansible-playbook -i aws_ec2.yml playbook.yml

# Azure
ansible-playbook -i azure_rm.yml playbook.yml
```

### Ansible Tower/AWX

For enterprise deployments, consider using Ansible Tower or AWX for:
- Web-based UI
- Role-based access control
- Job scheduling
- Audit logging
- REST API

## Monitoring

After deployment, access monitoring dashboards:
- Prometheus: http://your-server:9090
- Grafana: http://your-server:3000
- Enterprise Hub: https://your-server:3001

## Support

For issues or questions:
- Email: support@itechsmart.ai
- Documentation: https://docs.itechsmart.ai
- GitHub: https://github.com/itechsmart/suite

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**Version**: 1.0.0  
**Last Updated**: August 8, 2025  
**Copyright**: © 2025 iTechSmart Inc.. All rights reserved.