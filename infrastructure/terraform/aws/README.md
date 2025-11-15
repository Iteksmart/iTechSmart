# iTechSmart Suite - AWS Terraform Infrastructure

This directory contains Terraform configurations for deploying the iTechSmart Suite to AWS.

## Architecture Overview

The infrastructure includes:
- **VPC** with public and private subnets across 3 availability zones
- **Application Load Balancer** for traffic distribution
- **ECS Fargate** cluster for containerized applications
- **RDS PostgreSQL** for database
- **ElastiCache Redis** for caching
- **ECR** repositories for Docker images
- **S3** buckets for application data
- **CloudWatch** for logging and monitoring
- **IAM** roles and policies for security

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **Terraform** >= 1.0 installed
3. **AWS CLI** configured with credentials
4. **S3 Bucket** for Terraform state (create manually first)

## Quick Start

### 1. Configure AWS Credentials

```bash
aws configure
```

### 2. Create S3 Bucket for Terraform State

```bash
aws s3 mb s3://itechsmart-terraform-state --region us-east-1
aws s3api put-bucket-versioning \
  --bucket itechsmart-terraform-state \
  --versioning-configuration Status=Enabled
```

### 3. Initialize Terraform

```bash
cd infrastructure/terraform/aws
terraform init
```

### 4. Configure Variables

```bash
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
vim terraform.tfvars
```

### 5. Plan Deployment

```bash
terraform plan
```

### 6. Deploy Infrastructure

```bash
terraform apply
```

## Configuration

### Required Variables

- `db_password` - Database master password (sensitive)

### Optional Variables

- `aws_region` - AWS region (default: us-east-1)
- `environment` - Environment name (default: production)
- `vpc_cidr` - VPC CIDR block (default: 10.0.0.0/16)
- `db_instance_class` - RDS instance type (default: db.t3.large)
- `redis_node_type` - Redis node type (default: cache.t3.medium)

See `variables.tf` for all available options.

## Environments

### Development
```bash
terraform workspace new development
terraform workspace select development
terraform apply -var="environment=development"
```

### Staging
```bash
terraform workspace new staging
terraform workspace select staging
terraform apply -var="environment=staging"
```

### Production
```bash
terraform workspace new production
terraform workspace select production
terraform apply -var="environment=production"
```

## Outputs

After deployment, Terraform provides:
- `vpc_id` - VPC identifier
- `alb_dns_name` - Load balancer DNS name
- `ecs_cluster_name` - ECS cluster name
- `rds_endpoint` - Database endpoint
- `redis_endpoint` - Redis endpoint
- `ecr_repositories` - Docker registry URLs
- `s3_bucket_name` - Application data bucket

## Cost Estimation

### Development Environment (~$200/month)
- ECS Fargate: ~$50
- RDS db.t3.medium: ~$60
- ElastiCache cache.t3.micro: ~$15
- ALB: ~$20
- Data transfer: ~$20
- Other services: ~$35

### Production Environment (~$800/month)
- ECS Fargate: ~$300
- RDS db.t3.large (Multi-AZ): ~$250
- ElastiCache cache.t3.medium: ~$80
- ALB: ~$40
- Data transfer: ~$80
- Other services: ~$50

## Security

### Best Practices Implemented
- ✅ VPC with private subnets for databases
- ✅ Security groups with least privilege
- ✅ Encrypted RDS storage
- ✅ Encrypted S3 buckets
- ✅ IAM roles with minimal permissions
- ✅ CloudWatch logging enabled
- ✅ Multi-AZ deployment for production
- ✅ Automated backups

### Additional Recommendations
1. Enable AWS GuardDuty for threat detection
2. Use AWS Secrets Manager for sensitive data
3. Enable AWS Config for compliance monitoring
4. Set up AWS CloudTrail for audit logging
5. Implement AWS WAF for web application firewall

## Maintenance

### Updating Infrastructure

```bash
# Pull latest changes
git pull

# Review changes
terraform plan

# Apply updates
terraform apply
```

### Backing Up State

```bash
# State is automatically backed up to S3
# To manually backup:
terraform state pull > terraform.tfstate.backup
```

### Destroying Infrastructure

```bash
# WARNING: This will destroy all resources
terraform destroy
```

## Troubleshooting

### Common Issues

**Issue: Terraform state locked**
```bash
# Force unlock (use with caution)
terraform force-unlock <LOCK_ID>
```

**Issue: Resource already exists**
```bash
# Import existing resource
terraform import aws_vpc.main vpc-xxxxx
```

**Issue: Insufficient permissions**
- Ensure IAM user has required permissions
- Check AWS CLI credentials: `aws sts get-caller-identity`

### Getting Help

- Check Terraform logs: `TF_LOG=DEBUG terraform apply`
- Review AWS CloudWatch logs
- Contact iTechSmart support

## Monitoring

### CloudWatch Dashboards

Access CloudWatch dashboards for:
- ECS cluster metrics
- RDS performance
- Redis cache hits/misses
- ALB request metrics
- Application logs

### Alarms

Set up CloudWatch alarms for:
- High CPU usage
- Low memory
- Database connections
- Error rates
- Response times

## Compliance

### HIPAA Compliance

This infrastructure is designed with HIPAA compliance in mind:
- ✅ Encrypted data at rest
- ✅ Encrypted data in transit
- ✅ Audit logging enabled
- ✅ Access controls implemented
- ✅ Backup and recovery procedures

### Additional Steps Required
1. Sign AWS Business Associate Agreement (BAA)
2. Enable AWS CloudTrail
3. Configure AWS Config rules
4. Implement data retention policies
5. Conduct security assessments

## Support

For issues or questions:
- Email: support@itechsmart.ai
- Documentation: https://docs.itechsmart.ai
- GitHub: https://github.com/itechsmart/suite

---

**Version**: 1.0.0  
**Last Updated**: August 8, 2025  
**Copyright**: © 2025 iTechSmart Inc.. All rights reserved.