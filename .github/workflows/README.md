# GitHub Actions Workflows

This directory contains automated build workflows for the iTechSmart Suite Desktop Launcher.

## Available Workflows

### 1. Build macOS Installer (`build-macos.yml`)
**Purpose**: Builds macOS installers (DMG, PKG, ZIP) on GitHub's macOS runners.

**Triggers**:
- Push to `main` branch (when desktop-launcher files change)
- Pull requests to `main` branch
- Manual trigger via workflow_dispatch

**Outputs**:
- macOS DMG installer
- macOS PKG installer
- macOS ZIP archive

**Artifacts**: Available for download from the Actions tab for 90 days.

### 2. Build All Platforms (`build-all-platforms.yml`)
**Purpose**: Builds installers for Windows, Linux, and macOS in parallel.

**Triggers**:
- Push to `main` branch
- Push of version tags (v*)
- Pull requests to `main` branch
- Manual trigger via workflow_dispatch

**Outputs**:
- Windows EXE installer
- Linux AppImage
- macOS DMG installer
- macOS PKG installer

**Release Creation**: Automatically creates GitHub releases when version tags are pushed.

## How to Use

### Manual Trigger
1. Go to the repository on GitHub
2. Click on "Actions" tab
3. Select the workflow you want to run
4. Click "Run workflow" button
5. Select the branch and click "Run workflow"

### Automatic Builds
Workflows run automatically when:
- Code is pushed to the main branch
- Pull requests are created
- Version tags are pushed (for releases)

### Downloading Built Installers

#### From Workflow Runs:
1. Go to "Actions" tab
2. Click on a completed workflow run
3. Scroll down to "Artifacts" section
4. Download the desired installer

#### From Releases (for tagged versions):
1. Go to "Releases" section
2. Find the desired version
3. Download installers from "Assets"

## Creating a Release

To create a new release with installers:

```bash
# Tag the current commit
git tag -a v1.3.0 -m "Release version 1.0.0"

# Push the tag to GitHub
git push origin v1.3.0
```

The `build-all-platforms` workflow will automatically:
1. Build installers for all platforms
2. Create a GitHub release
3. Upload all installers to the release

## Workflow Status Badges

Add these badges to your README.md to show build status:

```markdown
![Build macOS](https://github.com/Iteksmart/iTechSmart/actions/workflows/build-macos.yml/badge.svg)
![Build All Platforms](https://github.com/Iteksmart/iTechSmart/actions/workflows/build-all-platforms.yml/badge.svg)
```

## Requirements

### Secrets
No additional secrets are required. The workflows use the default `GITHUB_TOKEN` which is automatically provided by GitHub Actions.

### Permissions
The workflows require the following permissions (automatically granted):
- `contents: write` - For creating releases
- `actions: read` - For downloading artifacts

## Troubleshooting

### Build Failures
1. Check the workflow logs in the Actions tab
2. Verify that package.json has correct build scripts
3. Ensure all dependencies are properly listed
4. Check for platform-specific issues in the logs

### Missing Artifacts
- Artifacts are retained for 90 days by default
- Check if the build completed successfully
- Verify the artifact upload step didn't fail

### Release Creation Issues
- Ensure you're pushing a tag (not just a commit)
- Tag must start with 'v' (e.g., v1.3.0)
- Check that GITHUB_TOKEN has sufficient permissions

## Customization

### Changing Retention Period
Edit the workflow file and add:
```yaml
- name: Upload artifact
  uses: actions/upload-artifact@v4
  with:
    retention-days: 30  # Change from default 90 days
```

### Adding Code Signing
For production releases, add code signing steps:
- Windows: Add Authenticode signing
- macOS: Add Apple Developer ID signing and notarization
- Linux: Add GPG signing

### Modifying Triggers
Edit the `on:` section in the workflow files to change when builds run.

## Support

For issues with the workflows:
1. Check the Actions tab for detailed logs
2. Review the workflow YAML files
3. Consult GitHub Actions documentation
4. Open an issue in the repository