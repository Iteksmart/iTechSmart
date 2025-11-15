# ProofLink.AI Extension Icons

This folder should contain the extension icons in the following sizes:

- `icon16.png` - 16x16 pixels (toolbar icon)
- `icon32.png` - 32x32 pixels (toolbar icon @2x)
- `icon48.png` - 48x48 pixels (extension management)
- `icon128.png` - 128x128 pixels (Chrome Web Store)

## Creating Icons

You can create these icons using any image editor. The icons should:

1. Use the ProofLink.AI brand colors (purple gradient: #667eea to #764ba2)
2. Be simple and recognizable at small sizes
3. Have a transparent background
4. Follow the design guidelines for Chrome/Firefox extensions

## Placeholder Icons

For development, you can use placeholder icons. Here's how to create them quickly:

### Using ImageMagick (Command Line)

```bash
# Install ImageMagick
# Ubuntu/Debian: sudo apt-get install imagemagick
# macOS: brew install imagemagick

# Create placeholder icons
convert -size 16x16 xc:purple icon16.png
convert -size 32x32 xc:purple icon32.png
convert -size 48x48 xc:purple icon48.png
convert -size 128x128 xc:purple icon128.png
```

### Using Online Tools

1. Go to https://www.favicon-generator.org/
2. Upload your logo or design
3. Download the generated icons
4. Rename them to match the required sizes

### Design Recommendations

- Use a lock (🔒) or shield symbol to represent security
- Incorporate the "P" from ProofLink
- Use the brand gradient colors
- Keep it simple and bold
- Test at 16x16 to ensure it's recognizable

## Production Icons

For production deployment, replace these placeholder icons with professionally designed icons that match your brand identity.