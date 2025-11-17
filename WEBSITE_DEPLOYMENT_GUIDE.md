# iTechSmart Suite - Website Deployment Guide

## Overview
This guide provides instructions for deploying the iTechSmart Suite website to various hosting platforms.

## Website Structure
```
website/
├── index.html              # Main landing page
├── css/
│   └── style.css          # Stylesheet
├── js/                    # JavaScript files (if needed)
├── docs/                  # Documentation pages
│   ├── ITECHSMART_SUITE_COMPLETE_DOCUMENTATION.html
│   ├── EXECUTIVE_PRESENTATION.html
│   ├── iTechSmart_Complete_Architecture.html
│   ├── ITECHSMART_PORTFOLIO_SHOWCASE.html
│   ├── DEPLOYMENT_GUIDE.html
│   └── API_DOCUMENTATION.html
└── assets/                # Images and other assets
```

## Deployment Options

### Option 1: GitHub Pages (Recommended)

#### Automatic Deployment
The repository includes a GitHub Actions workflow that automatically deploys to GitHub Pages on every push to the main branch.

**Steps:**
1. Enable GitHub Pages in repository settings:
   - Go to Settings → Pages
   - Source: GitHub Actions
   - The workflow will automatically deploy on the next push

2. Access your site at:
   ```
   https://[username].github.io/iTechSmart/
   ```

#### Manual Deployment
If you prefer manual deployment:

1. Build the site:
   ```bash
   cd iTechSmart
   mkdir -p _site
   cp -r website/* _site/
   ```

2. Push to gh-pages branch:
   ```bash
   git checkout --orphan gh-pages
   git rm -rf .
   cp -r _site/* .
   git add .
   git commit -m "Deploy website"
   git push origin gh-pages
   ```

### Option 2: Netlify

1. **Via Netlify CLI:**
   ```bash
   npm install -g netlify-cli
   cd iTechSmart/website
   netlify deploy --prod
   ```

2. **Via Netlify Dashboard:**
   - Connect your GitHub repository
   - Build settings:
     - Base directory: `website`
     - Publish directory: `website`
   - Deploy!

3. **Using Deploy Button:**
   Add this to your README:
   ```markdown
   [![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/yourusername/iTechSmart)
   ```

### Option 3: Vercel

1. **Via Vercel CLI:**
   ```bash
   npm install -g vercel
   cd iTechSmart/website
   vercel --prod
   ```

2. **Via Vercel Dashboard:**
   - Import your GitHub repository
   - Framework Preset: Other
   - Root Directory: `website`
   - Deploy!

### Option 4: AWS S3 + CloudFront

1. **Create S3 Bucket:**
   ```bash
   aws s3 mb s3://itechsmart-website
   aws s3 website s3://itechsmart-website --index-document index.html
   ```

2. **Upload Files:**
   ```bash
   cd iTechSmart/website
   aws s3 sync . s3://itechsmart-website --acl public-read
   ```

3. **Configure CloudFront:**
   - Create CloudFront distribution
   - Origin: Your S3 bucket
   - Enable HTTPS
   - Set custom domain (optional)

### Option 5: Docker + Nginx

1. **Create Dockerfile:**
   ```dockerfile
   FROM nginx:alpine
   COPY website/ /usr/share/nginx/html/
   EXPOSE 80
   CMD ["nginx", "-g", "daemon off;"]
   ```

2. **Build and Run:**
   ```bash
   docker build -t itechsmart-website .
   docker run -d -p 80:80 itechsmart-website
   ```

## Custom Domain Setup

### GitHub Pages
1. Add CNAME file to website directory:
   ```bash
   echo "www.yourdomain.com" > website/CNAME
   ```

2. Configure DNS:
   - Add CNAME record: `www` → `[username].github.io`
   - Add A records for apex domain:
     ```
     185.199.108.153
     185.199.109.153
     185.199.110.153
     185.199.111.153
     ```

### Netlify/Vercel
1. Add custom domain in dashboard
2. Update DNS records as instructed
3. SSL certificate is automatically provisioned

## Environment-Specific Configuration

### Update Repository Links
Before deploying, update GitHub repository links in HTML files:

```bash
# Replace placeholder with actual repository URL
find website -name "*.html" -type f -exec sed -i 's|yourusername/iTechSmart|actualusername/iTechSmart|g' {} +
```

### Update Contact Information
Update any contact information or company details in:
- `website/index.html`
- Footer sections in all HTML files

## Testing Locally

### Using Python HTTP Server
```bash
cd iTechSmart/website
python -m http.server 8000
# Visit http://localhost:8000
```

### Using Node.js HTTP Server
```bash
cd iTechSmart/website
npx http-server -p 8000
# Visit http://localhost:8000
```

### Using Docker
```bash
cd iTechSmart
docker run -d -p 8000:80 -v $(pwd)/website:/usr/share/nginx/html nginx:alpine
# Visit http://localhost:8000
```

## Continuous Deployment

### GitHub Actions (Included)
The repository includes `.github/workflows/deploy-pages.yml` which:
- Triggers on push to main branch
- Builds the website
- Deploys to GitHub Pages automatically

### Netlify (Auto-deploy)
Once connected, Netlify automatically deploys on:
- Push to main branch
- Pull request previews
- Manual triggers

### Vercel (Auto-deploy)
Vercel provides:
- Automatic deployments on push
- Preview deployments for PRs
- Instant rollbacks

## Monitoring and Analytics

### Add Google Analytics
Add to `<head>` section of index.html:
```html
<!-- Google Analytics -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### Add Plausible Analytics (Privacy-friendly)
```html
<script defer data-domain="yourdomain.com" src="https://plausible.io/js/script.js"></script>
```

## Performance Optimization

### Image Optimization
```bash
# Install imagemin
npm install -g imagemin-cli

# Optimize images
imagemin website/assets/*.{jpg,png} --out-dir=website/assets/optimized
```

### Minify CSS/JS
```bash
# Install minifiers
npm install -g csso-cli uglify-js

# Minify CSS
csso website/css/style.css -o website/css/style.min.css

# Minify JS (if applicable)
uglifyjs website/js/main.js -o website/js/main.min.js
```

## Security Best Practices

1. **Enable HTTPS** - Always use HTTPS in production
2. **Add Security Headers** - Configure CSP, X-Frame-Options, etc.
3. **Regular Updates** - Keep dependencies and content updated
4. **Access Control** - Restrict admin access appropriately

## Troubleshooting

### GitHub Pages Not Updating
- Check Actions tab for deployment status
- Verify Pages is enabled in Settings
- Clear browser cache
- Wait 5-10 minutes for propagation

### Custom Domain Not Working
- Verify DNS records are correct
- Check CNAME file exists
- Wait for DNS propagation (up to 48 hours)
- Verify SSL certificate is issued

### 404 Errors
- Check file paths are correct
- Ensure index.html exists in root
- Verify case sensitivity in file names

## Maintenance

### Regular Updates
- Update documentation regularly
- Keep version numbers current
- Test all links periodically
- Monitor site performance

### Backup Strategy
- Keep source files in Git
- Export analytics data monthly
- Document configuration changes

## Support

For deployment issues:
- GitHub Issues: [Report deployment issues](https://github.com/yourusername/iTechSmart/issues)
- Documentation: See complete documentation in `docs/`
- Community: Join discussions on GitHub

## Next Steps

After deployment:
1. ✅ Verify all pages load correctly
2. ✅ Test all navigation links
3. ✅ Check mobile responsiveness
4. ✅ Set up analytics
5. ✅ Configure custom domain (optional)
6. ✅ Add to search engines
7. ✅ Share with team and stakeholders

---

**Deployment Status:** Ready for production deployment
**Last Updated:** November 17, 2024
**Version:** 1.4.0