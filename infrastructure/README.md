# iTechSmart Suite - Infrastructure as Code

Complete infrastructure automation for deploying the iTechSmart Suite using Terraform and Ansible.

## Overview

This directory contains Infrastructure as Code (IaC) configurations for deploying the iTechSmart Suite across multiple cloud providers and on-premises environments.

### What's Included

- **Terraform** - Infrastructure provisioning for AWS, Azure, and GCP
- **Ansible** - Configuration management and application deployment
- **Scripts** - Helper scripts for common tasks
- **Documentation** - Comprehensive guides and best practices

## Quick Start

### Option 1: AWS Deployment with Terraform

```bash
cd terraform/aws
terraform init
terraform plan
terraform apply
```

### Option 2: Server Deployment with Ansible

```bash
cd ansible
ansible-playbook -i inventory/hosts.ini playbook.yml
```

## Directory Structure

```
infrastructure/
├── terraform/
│   ├── aws/              # AWS infrastructure
│   ├── azure/            # Azure infrastructure (coming soon)
│   └── gcp/              # GCP infrastructure (coming soon)
├── ansible/
│   ├── playbook.yml      # Main playbook
│   ├── inventory/        # Server inventories
│   ├── tasks/            # Task definitions
│   ├── vars/             # Variables
│   └── templates/        # Configuration templates
└── README.md             # This file
```

## Deployment Options

### 1. Cloud Deployment (Terraform)

**Best for:**
- Production environments
- Scalable infrastructure
- Managed services
- High availability

**Providers:**
- ✅ AWS (Complete)
- 🚧 Azure (Coming soon)
- 🚧 GCP (Coming soon)

**Features:**
- Auto-scaling ECS clusters
- Managed databases (RDS)
- Load balancing (ALB)
- Container registry (ECR)
- Monitoring (CloudWatch)
- Backup automation

### 2. Server Deployment (Ansible)

**Best for:**
- On-premises deployment
- Existing infrastructure
- Custom configurations
- Development/staging

**Features:**
- Automated server setup
- Docker deployment
- Database configuration
- Monitoring setup
- Backup configuration
- Health checks

## Prerequisites

### For Terraform
- Terraform >= 1.0
- AWS/Azure/GCP account
- Cloud provider CLI configured
- S3 bucket for state (AWS)

### For Ansible
- Ansible >= 2.14
- Python >= 3.8
- SSH access to servers
- Sudo privileges

## Architecture

### Cloud Architecture (AWS)

```
┌─────────────────────────────────────────────────────────┐
│                    AWS Cloud                             │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────────────────┐   │
│  │              Application Load Balancer            │   │
│  └────────────────────┬─────────────────────────────┘   │
│                       │                                   │
│         ┌─────────────┴─────────────┐                   │
│         │                           │                   │
│    ┌────▼────┐                 ┌───▼────┐              │
│    │   ECS   │                 │  ECS   │              │
│    │Cluster 1│                 │Cluster 2│              │
│    └────┬────┘                 └───┬────┘              │
│         │                          │                    │
│    ┌────▼──────────────────────────▼────┐              │
│    │         RDS PostgreSQL              │              │
│    │         (Multi-AZ)                  │              │
│    └─────────────────────────────────────┘              │
│                                                           │
│    ┌─────────────────────────────────────┐              │
│    │      ElastiCache Redis              │              │
│    └─────────────────────────────────────┘              │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

### On-Premises Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  Load Balancer (Nginx)                   │
└────────────────────┬─────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼────┐             ┌───▼────┐
    │ Server 1│             │Server 2│
    │ Docker  │             │ Docker │
    └────┬────┘             └───┬────┘
         │                      │
    ┌────▼──────────────────────▼────┐
    │      PostgreSQL Database        │
    └─────────────────────────────────┘
    
    ┌─────────────────────────────────┐
    │         Redis Cache             │
    └─────────────────────────────────┘
```

## Deployment Workflows

### Production Deployment

1. **Infrastructure Provisioning (Terraform)**
   ```bash
   cd terraform/aws
   terraform init
   terraform workspace new production
   terraform apply -var="environment=production"
   ```

2. **Application Deployment (Ansible)**
   ```bash
   cd ansible
   ansible-playbook -i inventory/hosts.ini playbook.yml \
     --extra-vars "environment=production"
   ```

3. **Verification**
   ```bash
   # Check all services
   ansible-playbook -i inventory/hosts.ini playbook.yml \
     --tags "health-check"
   ```

### Development Deployment

1. **Quick Setup**
   ```bash
   cd ansible
   ansible-playbook -i inventory/hosts.ini playbook.yml \
     --extra-vars "environment=development" \
     --limit itechsmart_dev
   ```

## Configuration

### Environment Variables

Create environment-specific configurations:

**Terraform:**
- `terraform.tfvars` - Variable values
- Backend configuration in `main.tf`

**Ansible:**
- `vars/production.yml` - Production settings
- `vars/staging.yml` - Staging settings
- `vars/development.yml` - Development settings
- `vars/vault.yml` - Encrypted secrets

### Secrets Management

**Terraform:**
```bash
# Use environment variables
export TF_VAR_db_password="secure-password"
```

**Ansible:**
```bash
# Use Ansible Vault
ansible-vault create vars/vault.yml
ansible-vault edit vars/vault.yml
```

## Cost Estimation

### AWS Deployment

**Development:** ~$200/month
- ECS Fargate: ~$50
- RDS db.t3.medium: ~$60
- ElastiCache: ~$15
- Other: ~$75

**Production:** ~$800/month
- ECS Fargate: ~$300
- RDS db.t3.large (Multi-AZ): ~$250
- ElastiCache: ~$80
- Other: ~$170

### On-Premises

**Hardware Costs:**
- Servers: $5,000 - $20,000 (one-time)
- Storage: $2,000 - $10,000 (one-time)
- Network: $1,000 - $5,000 (one-time)

**Operational Costs:**
- Power: ~$200/month
- Cooling: ~$100/month
- Maintenance: ~$500/month

## Monitoring

### Cloud (AWS)
- CloudWatch Dashboards
- CloudWatch Alarms
- X-Ray Tracing
- CloudTrail Audit Logs

### On-Premises
- Prometheus Metrics
- Grafana Dashboards
- ELK Stack Logging
- Custom Alerts

## Backup & Recovery

### Automated Backups
- Database: Daily snapshots
- Application Data: Daily backups
- Configuration: Version controlled
- Retention: 30 days (production)

### Disaster Recovery
- RTO: < 4 hours
- RPO: < 1 hour
- Multi-region failover (cloud)
- Backup server (on-premises)

## Security

### Best Practices Implemented
- ✅ Encrypted data at rest
- ✅ Encrypted data in transit
- ✅ Network isolation (VPC/subnets)
- ✅ Security groups/firewalls
- ✅ IAM roles with least privilege
- ✅ Secrets management
- ✅ Audit logging
- ✅ Regular security updates

### Compliance
- HIPAA ready
- SOC 2 compliant
- GDPR compliant
- PCI DSS ready

## Troubleshooting

### Common Issues

**Terraform:**
```bash
# State locked
terraform force-unlock <LOCK_ID>

# Refresh state
terraform refresh

# Import existing resource
terraform import aws_vpc.main vpc-xxxxx
```

**Ansible:**
```bash
# Connection test
ansible -i inventory/hosts.ini all -m ping

# Verbose output
ansible-playbook playbook.yml -vvv

# Check syntax
ansible-playbook playbook.yml --syntax-check
```

## Maintenance

### Updates

**Infrastructure:**
```bash
# Terraform
terraform plan
terraform apply

# Ansible
ansible-playbook playbook.yml --tags "update"
```

**Security Patches:**
```bash
# Automated with Ansible
ansible-playbook playbook.yml --tags "security-update"
```

## Support

### Documentation
- [Terraform AWS Guide](terraform/aws/README.md)
- [Ansible Deployment Guide](ansible/README.md)
- [Master Technical Manual](../MASTER_TECHNICAL_MANUAL.md)

### Contact
- Email: support@itechsmart.ai
- Documentation: https://docs.itechsmart.ai
- GitHub: https://github.com/itechsmart/suite

## Contributing

1. Fork the repository
2. Create a feature branch
3. Test changes thoroughly
4. Submit a pull request
5. Update documentation

## License

Copyright © 2025 iTechSmart Inc.. All rights reserved.

---

**Version**: 1.0.0  
**Last Updated**: August 8, 2025  
**Launch Date**: August 8, 2025