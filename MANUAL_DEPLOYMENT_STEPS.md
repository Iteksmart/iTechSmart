# Manual Deployment Steps - Quick Reference

## 🚨 Action Required: Complete Website Deployment

Due to network timeout issues, the following manual steps are required to complete the website deployment.

---

## Step 1: Push to GitHub

Open your terminal and run:

```bash
cd iTechSmart
git push origin main
```

**What this does:**
- Pushes all website files to GitHub
- Triggers the GitHub Pages deployment workflow
- Makes the website available online

**Expected output:**
```
Enumerating objects: X, done.
Counting objects: 100% (X/X), done.
Writing objects: 100% (X/X), done.
To https://github.com/[username]/iTechSmart.git
   abc1234..def5678  main -> main
```

---

## Step 2: Enable GitHub Pages

1. Go to your repository on GitHub
2. Click **Settings** (top menu)
3. Click **Pages** (left sidebar)
4. Under "Source", select **GitHub Actions**
5. Click **Save**

**Screenshot locations:**
- Settings: Top right of repository page
- Pages: Left sidebar under "Code and automation"
- Source: Dropdown menu in Pages settings

---

## Step 3: Monitor Deployment

1. Go to the **Actions** tab in your repository
2. Look for the "Deploy to GitHub Pages" workflow
3. Click on the running workflow to see progress
4. Wait for the green checkmark (usually 2-3 minutes)

**Workflow status:**
- 🟡 Yellow dot = In progress
- ✅ Green checkmark = Success
- ❌ Red X = Failed (check logs)

---

## Step 4: Access Your Website

Once deployment is complete, your website will be available at:

```
https://[your-username].github.io/iTechSmart/
```

**Example:**
If your GitHub username is `johndoe`, the URL will be:
```
https://johndoe.github.io/iTechSmart/
```

---

## Step 5: Update README (Optional)

Update the website URL in `README.md`:

```bash
# Find this line in README.md:
**📱 Visit our website:** [iTechSmart Suite Website](https://8050-4e3e6dbe-4567-44ca-a9cd-36cc5d8cf07b.proxy.daytona.works)

# Replace with:
**📱 Visit our website:** [iTechSmart Suite Website](https://[your-username].github.io/iTechSmart/)
```

Then commit and push:
```bash
git add README.md
git commit -m "Update website URL"
git push origin main
```

---

## Troubleshooting

### Push Fails
**Error:** `Authentication failed`
**Solution:** 
```bash
# Use personal access token
git remote set-url origin https://[token]@github.com/[username]/iTechSmart.git
git push origin main
```

### Workflow Doesn't Run
**Check:**
1. Go to Settings → Actions → General
2. Ensure "Allow all actions and reusable workflows" is selected
3. Ensure "Read and write permissions" is enabled

### 404 Error on Website
**Solutions:**
1. Wait 5-10 minutes for propagation
2. Check that GitHub Pages is enabled
3. Verify the workflow completed successfully
4. Clear browser cache

### Custom Domain Issues
**If using custom domain:**
1. Add `CNAME` file to `website/` directory
2. Configure DNS records:
   - CNAME: `www` → `[username].github.io`
   - A records for apex domain
3. Enable HTTPS in Pages settings

---

## Verification Checklist

After deployment, verify:

- [ ] Website loads at GitHub Pages URL
- [ ] All navigation links work
- [ ] Documentation pages are accessible
- [ ] Images and styles load correctly
- [ ] Mobile responsive design works
- [ ] No console errors in browser

---

## Alternative: Deploy to Netlify (If GitHub Pages Issues)

If GitHub Pages doesn't work, use Netlify:

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd iTechSmart/website
netlify deploy --prod
```

Follow the prompts to:
1. Authorize Netlify
2. Create new site or link existing
3. Confirm deployment

Your site will be live at: `https://[random-name].netlify.app`

---

## Need Help?

- **GitHub Pages Documentation:** https://docs.github.com/en/pages
- **Deployment Guide:** See `WEBSITE_DEPLOYMENT_GUIDE.md`
- **Status Document:** See `WEBSITE_DEPLOYMENT_STATUS.md`
- **Complete Summary:** See `WEBSITE_DEPLOYMENT_COMPLETE.md`

---

## Quick Commands Reference

```bash
# Push to GitHub
git push origin main

# Check git status
git status

# View commit history
git log --oneline -5

# Force push (if needed)
git push origin main --force

# Check remote URL
git remote -v
```

---

**Current Status:** Website files committed, awaiting push to GitHub
**Next Action:** Run `git push origin main`
**Estimated Time:** 5-10 minutes total