# Icon Assets - Setup Instructions

## Current Status

✅ **icon.svg** - SVG template created (can be converted to PNG/ICO/ICNS)

## Quick Setup Options

### Option 1: Use Online Converters (Fastest - 5 minutes)

1. **Convert SVG to PNG**:
   - Go to: https://cloudconvert.com/svg-to-png
   - Upload `icon.svg`
   - Set size to 512x512
   - Download as `icon.png`

2. **Create Windows Icon (.ico)**:
   - Go to: https://convertio.co/png-ico/
   - Upload `icon.png`
   - Download as `icon.ico`

3. **Create macOS Icon (.icns)**:
   - Go to: https://cloudconvert.com/png-to-icns
   - Upload `icon.png`
   - Download as `icon.icns`

4. **Create Tray Icon**:
   - Go to: https://www.iloveimg.com/resize-image
   - Upload `icon.png`
   - Resize to 16x16
   - Download as `tray-icon.png`

### Option 2: Use ImageMagick (If Available)

```bash
cd desktop-launcher/assets/icons

# Convert SVG to PNG
convert icon.svg -resize 512x512 icon.png

# Create tray icon
convert icon.png -resize 16x16 tray-icon.png

# Create Windows icon
convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico

# Create macOS icon (requires macOS or png2icns)
png2icns icon.icns icon.png
```

### Option 3: Use Existing Logo

If you prefer to use the iTechSmart logo:

```bash
# Copy logo to icons directory
cp "../../logo itechsmart.JPG" ./logo.jpg

# Use online tools to:
# 1. Remove background: https://remove.bg
# 2. Resize to 512x512: https://www.iloveimg.com/resize-image
# 3. Convert to PNG: https://cloudconvert.com/jpg-to-png
# 4. Follow Option 1 steps above
```

### Option 4: Use Placeholder (Temporary)

For testing purposes, you can use simple colored squares:

1. Create a 512x512 blue square with "iTS" text
2. Use any image editor (Paint, GIMP, Photoshop, Figma)
3. Export as PNG
4. Follow Option 1 for conversions

## Required Files Checklist

Place these files in `desktop-launcher/assets/icons/`:

- [ ] `icon.png` (512x512) - Main application icon
- [ ] `icon.ico` (Windows icon with multiple sizes)
- [ ] `icon.icns` (macOS icon with multiple sizes)
- [ ] `tray-icon.png` (16x16) - System tray icon

Optional:
- [ ] `dmg-background.png` (800x400) - macOS DMG installer background

## Testing Icons

After creating icons, test the build:

```bash
cd desktop-launcher

# Install dependencies
npm install

# Test development mode
npm run dev
npm start

# Build for current platform
npm run build
npm run package
```

## Icon Design Tips

The provided SVG template includes:
- Blue to purple gradient background
- "iTS" monogram in white
- Circuit pattern decoration
- Professional, modern look

Feel free to customize:
- Change colors in the SVG
- Modify the text/monogram
- Add your own design elements
- Use your company logo instead

## Need Custom Icons?

If you need professionally designed icons:
1. Hire a designer on Fiverr/Upwork ($20-50)
2. Use AI tools like Midjourney/DALL-E
3. Use icon design tools like Figma/Sketch
4. Contact: design@itechsmart.com

## Current Status

**Desktop Launcher Completion**: 95% → 100% (once icons are added)

The launcher is fully functional and ready to build. Icons are the only missing piece!