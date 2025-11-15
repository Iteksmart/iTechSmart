#!/bin/bash
# Release Preparation Script for iTechSmart Suite

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Check if version is provided
if [ -z "$1" ]; then
    print_error "Version number required"
    echo "Usage: ./prepare_release.sh <version>"
    echo "Example: ./prepare_release.sh 1.0.0"
    exit 1
fi

VERSION=$1
TAG="v${VERSION}"

print_header "iTechSmart Suite Release Preparation"
echo ""
print_info "Version: ${VERSION}"
print_info "Tag: ${TAG}"
echo ""

# Step 1: Check if on main branch
print_info "Checking current branch..."
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    print_warning "Not on main branch (current: ${CURRENT_BRANCH})"
    read -p "Switch to main branch? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git checkout main
        print_success "Switched to main branch"
    else
        print_error "Release must be created from main branch"
        exit 1
    fi
fi

# Step 2: Pull latest changes
print_info "Pulling latest changes..."
git pull origin main
print_success "Repository updated"

# Step 3: Check if tag already exists
print_info "Checking if tag exists..."
if git rev-parse "$TAG" >/dev/null 2>&1; then
    print_error "Tag ${TAG} already exists"
    read -p "Delete existing tag and continue? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git tag -d "$TAG"
        git push origin ":refs/tags/${TAG}" 2>/dev/null || true
        print_success "Existing tag deleted"
    else
        exit 1
    fi
fi

# Step 4: Check for uncommitted changes
print_info "Checking for uncommitted changes..."
if ! git diff-index --quiet HEAD --; then
    print_warning "You have uncommitted changes"
    git status --short
    read -p "Commit changes before release? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "Commit message: " COMMIT_MSG
        git add -A
        git commit -m "$COMMIT_MSG"
        git push origin main
        print_success "Changes committed and pushed"
    else
        print_error "Please commit or stash changes before creating release"
        exit 1
    fi
fi

# Step 5: Verify build status
print_info "Checking latest build status..."
BUILD_STATUS=$(gh run list --limit 1 --json status,conclusion --jq '.[0].status')
BUILD_CONCLUSION=$(gh run list --limit 1 --json status,conclusion --jq '.[0].conclusion')

if [ "$BUILD_STATUS" = "completed" ]; then
    if [ "$BUILD_CONCLUSION" = "success" ]; then
        print_success "Latest build: SUCCESS"
    else
        print_error "Latest build: FAILED"
        print_warning "Creating release with failed build"
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    print_warning "Build is still running (status: ${BUILD_STATUS})"
    read -p "Wait for build to complete? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Monitoring build..."
        python scripts/monitor_build.py --once
        exit 0
    fi
fi

# Step 6: Generate release notes
print_info "Generating release notes..."
if [ -f "build-tools/generate_release_notes.py" ]; then
    python build-tools/generate_release_notes.py "$VERSION" > release-notes-${VERSION}.md
    print_success "Release notes generated: release-notes-${VERSION}.md"
else
    print_warning "Release notes generator not found"
fi

# Step 7: Create and push tag
print_info "Creating release tag..."
read -p "Release message (press Enter for default): " RELEASE_MSG
if [ -z "$RELEASE_MSG" ]; then
    RELEASE_MSG="Release version ${VERSION}"
fi

git tag -a "$TAG" -m "$RELEASE_MSG"
print_success "Tag created: ${TAG}"

# Step 8: Push tag
print_info "Pushing tag to GitHub..."
git push origin "$TAG"
print_success "Tag pushed to GitHub"

# Step 9: Summary
echo ""
print_header "Release Preparation Complete!"
echo ""
print_success "Version: ${VERSION}"
print_success "Tag: ${TAG}"
print_success "Status: Tag pushed to GitHub"
echo ""
print_info "GitHub Actions will now:"
echo "  1. Build all 35 products for Windows, macOS, Linux"
echo "  2. Create demo versions"
echo "  3. Create suite installers"
echo "  4. Run integration tests"
echo "  5. Create GitHub Release with all artifacts"
echo ""
print_info "Monitor the build:"
echo "  - Web: https://github.com/Iteksmart/iTechSmart/actions"
echo "  - CLI: python scripts/monitor_build.py"
echo ""
print_info "View the release (after build completes):"
echo "  - https://github.com/Iteksmart/iTechSmart/releases/tag/${TAG}"
echo ""
print_success "🎉 Release ${VERSION} is being built!"