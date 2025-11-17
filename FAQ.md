# iTechSmart Suite - Frequently Asked Questions (FAQ)

## Table of Contents
1. [General Questions](#general-questions)
2. [Licensing & Pricing](#licensing--pricing)
3. [Installation & Setup](#installation--setup)
4. [Product Usage](#product-usage)
5. [Technical Questions](#technical-questions)
6. [Troubleshooting](#troubleshooting)
7. [Security & Privacy](#security--privacy)
8. [Support & Updates](#support--updates)

---

## General Questions

### What is iTechSmart Suite?

iTechSmart Suite is a comprehensive IT management platform that provides 35 enterprise-grade applications in one unified solution. It covers everything from security and compliance to analytics and automation.

### Who is iTechSmart Suite for?

iTechSmart Suite is designed for:
- **IT Teams:** System administrators, DevOps engineers, security professionals
- **Businesses:** Small to large enterprises needing IT management tools
- **Developers:** Software teams building and deploying applications
- **Analysts:** Data professionals requiring analytics and insights

### What products are included?

The suite includes 35 products across 7 categories:
1. **Core Platform** (4 products) - Foundation services
2. **Security & Compliance** (5 products) - Protection and governance
3. **Operations & Monitoring** (6 products) - System management
4. **Development & Automation** (5 products) - Build and deploy tools
5. **Data & Analytics** (5 products) - Insights and intelligence
6. **Collaboration** (5 products) - Team communication
7. **Enterprise & Integration** (5 products) - Business systems

### How is iTechSmart Suite different from competitors?

**Key Differentiators:**
- ✅ **All-in-One:** 35 products vs. buying individual tools
- ✅ **Single License:** One license for everything
- ✅ **Integrated:** Products work together seamlessly
- ✅ **Cost-Effective:** Significant savings vs. individual tools
- ✅ **Easy to Use:** Unified interface and management

### Can I try before buying?

Yes! We offer a **14-day free trial** with full access to all products. No credit card required.

**Start your trial:** https://itechsmart.dev/trial

---

## Licensing & Pricing

### What license tiers are available?

| Tier | Users | Products | Price/Month | Best For |
|------|-------|----------|-------------|----------|
| **Trial** | 5 | 3 | Free | Testing |
| **Starter** | 10 | 5 | $99 | Small teams |
| **Professional** | 25 | 10 | $299 | Growing businesses |
| **Enterprise** | 100 | 20 | $999 | Large organizations |
| **Unlimited** | ∞ | 35 | Custom | Enterprises |

### How does licensing work?

**License Model:**
- One license per organization
- License bound to specific machines (configurable)
- Annual or monthly billing
- Automatic renewal (can be disabled)

**What's Included:**
- All products in your tier
- Unlimited usage within limits
- Free updates and support
- Access to documentation

### Can I upgrade my license?

Yes! You can upgrade at any time:
1. Log into your account portal
2. Click "Upgrade License"
3. Choose new tier
4. Pay the difference
5. Instant activation

**Pro-rated billing:** You only pay for the remaining time in your billing period.

### What happens when my license expires?

**30 Days Before Expiration:**
- Email reminders sent
- In-app notifications
- Grace period begins

**On Expiration:**
- Products stop working
- Data remains intact
- 30-day grace period to renew

**After Grace Period:**
- Account suspended
- Data retained for 90 days
- Contact support to reactivate

### Can I transfer my license to another machine?

Yes, with limitations:
- **Professional:** 1 machine, can transfer once per month
- **Enterprise:** 5 machines, unlimited transfers
- **Unlimited:** Unlimited machines and transfers

**To Transfer:**
1. Deactivate on current machine (Settings > License > Deactivate)
2. Install on new machine
3. Activate with same license key

### Do you offer educational or non-profit discounts?

Yes! We offer:
- **Educational:** 50% discount for schools and universities
- **Non-Profit:** 40% discount for registered non-profits
- **Open Source:** Free licenses for open source projects

**Apply:** https://itechsmart.dev/discounts

---

## Installation & Setup

### What are the system requirements?

**Minimum:**
- **OS:** Windows 10, macOS 10.13, or Ubuntu 18.04
- **RAM:** 4GB
- **Disk:** 10GB free space
- **Internet:** Required for setup
- **Docker:** Required

**Recommended:**
- **OS:** Windows 11, macOS 14, or Ubuntu 22.04
- **RAM:** 8GB or more
- **Disk:** 50GB free space
- **Internet:** Broadband
- **Docker:** Latest version

### Do I need Docker?

Yes, Docker is required to run the products. Don't worry - we'll guide you through installing it if you don't have it.

**Why Docker?**
- Consistent environment across platforms
- Easy updates and management
- Isolated product containers
- Better resource management

### How long does installation take?

**Installation Time:**
- Download: 2-5 minutes (depends on internet speed)
- Installation: 1-3 minutes
- First launch: 30 seconds
- License activation: 10 seconds
- **Total:** ~5-10 minutes

### Can I install on multiple computers?

It depends on your license tier:
- **Trial/Starter/Professional:** 1 machine
- **Enterprise:** Up to 5 machines
- **Unlimited:** Unlimited machines

### Do I need administrator/root access?

**Windows/macOS:** Yes, for initial installation  
**Linux:** Yes, for Docker and system packages  
**After Installation:** No, runs as regular user

---

## Product Usage

### How do I start using a product?

**Quick Start:**
1. Open iTechSmart Suite
2. Find the product you want
3. Click "Start"
4. Wait 10-30 seconds
5. Click "Open" to access the product

### How many products can I run at once?

**Technical Limit:** Depends on your system resources  
**Practical Limit:** 5-10 products simultaneously

**Resource Usage:**
- Each product: 200-500MB RAM
- Total recommended: 8GB RAM for 5+ products

### Can I use products offline?

**Offline Capabilities:**
- ✅ Products work offline after initial setup
- ✅ License validated from cache
- ✅ Most features available
- ❌ Updates require internet
- ❌ License refresh requires internet

**Offline Duration:** Up to 30 days before re-validation needed

### How do I access a product's UI?

**Method 1: From Dashboard**
1. Ensure product is running (green status)
2. Click "Open" button
3. Browser opens automatically

**Method 2: Direct URL**
- Each product has a unique port
- Access at `http://localhost:PORT`
- Port numbers shown in product details

### Can I customize products?

Yes! Each product has its own configuration:
- Access via product's UI
- Settings menu within each product
- Configuration files (advanced users)
- API for programmatic configuration

### Do products share data?

Yes, products can share data when configured:
- **Automatic:** Core platform products
- **Optional:** Enable in product settings
- **Secure:** Encrypted data transfer
- **Controlled:** You decide what to share

---

## Technical Questions

### What technology is iTechSmart Suite built on?

**Desktop Launcher:**
- Electron (cross-platform desktop apps)
- React (user interface)
- TypeScript (type-safe code)

**License Server:**
- Node.js (backend runtime)
- Express (web framework)
- PostgreSQL (database)
- Prisma (ORM)

**Products:**
- Docker containers
- Various technologies per product
- Microservices architecture

### What ports does it use?

**License Server:** 3001 (configurable)  
**Products:** 3000-9000 range (varies by product)  
**Docker:** 2375/2376 (Docker API)

**Firewall Rules:**
- Allow outbound HTTPS (443) for license validation
- Allow localhost connections for products
- No inbound ports needed (unless exposing products)

### How much disk space do products use?

**Per Product:** 500MB - 2GB  
**Total (all 35):** ~40GB  
**Recommended Free Space:** 50GB

**Storage Breakdown:**
- Docker images: 30GB
- Product data: 5GB
- Application: 500MB
- Logs: 1GB

### Can I run this in a virtual machine?

Yes, with considerations:
- **Nested Virtualization:** Required for Docker
- **Resources:** Allocate sufficient RAM and CPU
- **Performance:** May be slower than native
- **Compatibility:** Test with your hypervisor

**Tested Hypervisors:**
- VMware Workstation/Fusion ✅
- VirtualBox ✅
- Hyper-V ✅
- Parallels ✅

### Does it work with Docker alternatives?

Yes, compatible with:
- **Podman:** Full compatibility
- **Rancher Desktop:** Full compatibility
- **Docker Desktop alternatives:** Most work

**Note:** Some features may require Docker-specific APIs.

### Can I deploy to Kubernetes?

Not directly, but:
- Products are containerized
- Can be deployed to K8s manually
- Enterprise support available for K8s deployments
- Helm charts coming soon

---

## Troubleshooting

### Application won't start

**Common Causes:**
1. Docker not running
2. Insufficient permissions
3. Port conflicts
4. Corrupted installation

**Solutions:**
```bash
# Check Docker
docker --version
docker ps

# Restart Docker
# Windows/Mac: Restart Docker Desktop
# Linux: sudo systemctl restart docker

# Reinstall application
# Download fresh installer and reinstall
```

### License activation fails

**Error: "Invalid License Key"**
- Check for typos
- Verify key hasn't expired
- Ensure correct format: ITSM-XXXX-XXXX-XXXX-XXXX

**Error: "Cannot Connect to Server"**
- Check internet connection
- Disable VPN temporarily
- Check firewall settings
- Try again in a few minutes

**Error: "License Already in Use"**
- License is active on another machine
- Deactivate on other machine first
- Or contact support to transfer

### Product won't start

**Symptoms:**
- Stuck in "Starting" state
- Error message appears
- Immediately stops

**Solutions:**
1. Check Docker is running
2. Verify sufficient disk space
3. Check port availability
4. Review logs (Settings > Advanced > View Logs)
5. Restart the product
6. Restart Docker
7. Restart application

### High CPU/Memory usage

**Normal Usage:**
- Idle: 5% CPU, 200MB RAM
- Active: 20% CPU, 500MB RAM
- Multiple products: Higher usage expected

**If Excessive:**
1. Stop unused products
2. Check for runaway containers
3. Restart Docker
4. Update to latest version
5. Check for malware

### Cannot access product UI

**Checklist:**
- [ ] Product status is "Running" (green)
- [ ] Wait 30 seconds after starting
- [ ] Try refreshing browser
- [ ] Check firewall isn't blocking localhost
- [ ] Try different browser
- [ ] Check product logs

---

## Security & Privacy

### Is my data secure?

Yes! Security measures include:
- ✅ **Encryption:** Data encrypted at rest and in transit
- ✅ **Isolation:** Products run in isolated containers
- ✅ **Authentication:** Secure license validation
- ✅ **Updates:** Regular security patches
- ✅ **Auditing:** Comprehensive audit logs

### What data do you collect?

**We Collect:**
- License validation data
- Usage statistics (anonymous)
- Error reports (opt-in)
- Update checks

**We Don't Collect:**
- Your product data
- Personal files
- Browsing history
- Sensitive information

**Privacy Policy:** https://itechsmart.dev/privacy

### Can I use this in a regulated environment?

Yes! iTechSmart Suite supports:
- **GDPR:** EU data protection compliance
- **HIPAA:** Healthcare data security (with BAA)
- **SOC 2:** Security and availability controls
- **ISO 27001:** Information security management

**Compliance Documentation:** Available on request

### Is the code open source?

**Desktop Launcher:** Proprietary  
**License Server:** Proprietary  
**Products:** Mix of proprietary and open source components

**Open Source Components:**
- We use many open source libraries
- Full attribution in About section
- Licenses included with distribution

### How do you handle security vulnerabilities?

**Security Process:**
1. **Report:** security@itechsmart.dev
2. **Acknowledge:** Within 24 hours
3. **Assess:** Severity and impact
4. **Fix:** Develop and test patch
5. **Release:** Emergency update if critical
6. **Disclose:** After fix is deployed

**Bug Bounty:** https://itechsmart.dev/security/bounty

---

## Support & Updates

### How do I get support?

**Support Channels:**
- **Email:** support@itechsmart.dev (24-48 hour response)
- **Live Chat:** https://itechsmart.dev (business hours)
- **Phone:** 1-800-ITECH-SMART (24/7 for critical)
- **Community:** https://community.itechsmart.dev

**Support Levels:**
- **Trial/Starter:** Email support
- **Professional:** Email + chat support
- **Enterprise:** Priority support + phone
- **Unlimited:** Dedicated support team

### How often are updates released?

**Update Schedule:**
- **Major Updates:** Quarterly (new features)
- **Minor Updates:** Monthly (improvements)
- **Security Patches:** As needed (immediate)
- **Product Updates:** Varies by product

**Auto-Update:**
- Enabled by default
- Downloads in background
- Installs on restart
- Can be disabled in settings

### What's included in updates?

**Typical Update Includes:**
- New features and improvements
- Bug fixes
- Security patches
- Performance optimizations
- New product versions
- Documentation updates

**Update Notes:** Detailed changelog with each update

### Can I roll back an update?

**Automatic Rollback:**
- If update fails, auto-rollback to previous version
- Your data and settings preserved

**Manual Rollback:**
- Download previous version from website
- Uninstall current version
- Install previous version
- Reactivate license

**Note:** Not recommended unless critical issue

### How do I report a bug?

**Bug Report:**
1. Go to Settings > Advanced > Report Bug
2. Or email: bugs@itechsmart.dev
3. Include:
   - What you were doing
   - What happened
   - What you expected
   - Screenshots if applicable
   - Log files (auto-attached)

**Bug Tracking:** https://github.com/Iteksmart/iTechSmart/issues

### Where can I request features?

**Feature Requests:**
- **Community Forum:** https://community.itechsmart.dev/features
- **Email:** features@itechsmart.dev
- **GitHub:** https://github.com/Iteksmart/iTechSmart/discussions

**Voting:** Upvote existing requests to prioritize

---

## Still Have Questions?

### Contact Us

**General Inquiries:**
- Email: info@itechsmart.dev
- Phone: 1-800-ITECH-INFO
- Website: https://itechsmart.dev/contact

**Sales:**
- Email: sales@itechsmart.dev
- Phone: 1-800-ITECH-SALES
- Schedule Demo: https://itechsmart.dev/demo

**Technical Support:**
- Email: support@itechsmart.dev
- Phone: 1-800-ITECH-SMART
- Portal: https://support.itechsmart.dev

**Social Media:**
- Twitter: @iTechSmart
- LinkedIn: /company/itechsmart
- YouTube: /iTechSmart
- GitHub: /Iteksmart

### Resources

**Documentation:**
- User Guide: https://docs.itechsmart.dev/user
- Admin Guide: https://docs.itechsmart.dev/admin
- API Reference: https://docs.itechsmart.dev/api
- Video Tutorials: https://youtube.com/itechsmart

**Community:**
- Forums: https://community.itechsmart.dev
- Blog: https://blog.itechsmart.dev
- Newsletter: https://itechsmart.dev/newsletter
- Events: https://itechsmart.dev/events

---

**Document Version:** 1.0  
**Last Updated:** November 16, 2025  
**For:** iTechSmart Suite v1.0.0

**Have a question not answered here?** Contact us at support@itechsmart.dev