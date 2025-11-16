# Icon Assets Requirements

## Required Icons

To complete the desktop launcher, you need to create the following icon files:

### 1. Main Application Icon

**File**: `assets/icons/icon.png`
- **Size**: 512x512 pixels
- **Format**: PNG with transparency
- **Usage**: Main application icon, used as base for other formats

### 2. macOS Icon

**File**: `assets/icons/icon.icns`
- **Format**: Apple Icon Image (.icns)
- **Sizes included**: 16x16, 32x32, 64x64, 128x128, 256x256, 512x512, 1024x1024
- **Tool**: Use `png2icns` or `iconutil` to convert from PNG

**How to create**:
```bash
# Using png2icns (install with: npm install -g png2icns)
png2icns assets/icons/icon.icns assets/icons/icon.png

# Or using macOS iconutil
mkdir icon.iconset
sips -z 16 16     icon.png --out icon.iconset/icon_16x16.png
sips -z 32 32     icon.png --out icon.iconset/icon_16x16@2x.png
sips -z 32 32     icon.png --out icon.iconset/icon_32x32.png
sips -z 64 64     icon.png --out icon.iconset/icon_32x32@2x.png
sips -z 128 128   icon.png --out icon.iconset/icon_128x128.png
sips -z 256 256   icon.png --out icon.iconset/icon_128x128@2x.png
sips -z 256 256   icon.png --out icon.iconset/icon_256x256.png
sips -z 512 512   icon.png --out icon.iconset/icon_256x256@2x.png
sips -z 512 512   icon.png --out icon.iconset/icon_512x512.png
sips -z 1024 1024 icon.png --out icon.iconset/icon_512x512@2x.png
iconutil -c icns icon.iconset
```

### 3. Windows Icon

**File**: `assets/icons/icon.ico`
- **Format**: Windows Icon (.ico)
- **Sizes included**: 16x16, 32x32, 48x48, 64x64, 128x128, 256x256
- **Tool**: Use ImageMagick or online converter

**How to create**:
```bash
# Using ImageMagick
convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico

# Or use online tool: https://convertio.co/png-ico/
```

### 4. System Tray Icon

**File**: `assets/icons/tray-icon.png`
- **Size**: 16x16 pixels (or 32x32 for retina)
- **Format**: PNG with transparency
- **Style**: Simple, monochrome design works best
- **Usage**: System tray/menu bar icon

**Note**: Should be a simplified version of the main icon that's recognizable at small sizes.

### 5. DMG Background (macOS)

**File**: `assets/dmg-background.png`
- **Size**: 800x400 pixels
- **Format**: PNG
- **Usage**: Background image for macOS DMG installer
- **Design**: Should include iTechSmart branding and installation instructions

## Quick Solution: Use Placeholder Icons

If you don't have custom icons ready, you can use placeholder icons temporarily:

### Option 1: Generate Simple Icons with ImageMagick

```bash
cd assets/icons

# Create a simple colored square as placeholder
convert -size 512x512 xc:#3B82F6 -gravity center \
  -pointsize 200 -fill white -annotate +0+0 "iTS" \
  icon.png

# Create smaller version for tray
convert icon.png -resize 16x16 tray-icon.png

# Create Windows icon
convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico

# Create macOS icon (requires macOS)
# png2icns icon.icns icon.png
```

### Option 2: Use Existing Logo

If you have the iTechSmart logo (`logo itechsmart.JPG`), convert it:

```bash
# Convert and resize logo
convert "logo itechsmart.JPG" -resize 512x512 -background transparent \
  -gravity center -extent 512x512 assets/icons/icon.png

# Create other formats
convert assets/icons/icon.png -resize 16x16 assets/icons/tray-icon.png
convert assets/icons/icon.png -define icon:auto-resize=256,128,64,48,32,16 \
  assets/icons/icon.ico
```

### Option 3: Download Free Icons

Use free icon resources:
- **Flaticon**: https://www.flaticon.com/
- **Icons8**: https://icons8.com/
- **Iconscout**: https://iconscout.com/

Search for "tech", "smart", "IT", or "suite" icons.

## Icon Design Guidelines

### Style
- Modern, clean design
- Recognizable at small sizes
- Works well on light and dark backgrounds
- Consistent with iTechSmart branding

### Colors
- Primary: Blue (#3B82F6)
- Secondary: Purple (#8B5CF6)
- Accent: Gradient from blue to purple

### Elements
- Could include: Circuit patterns, tech symbols, "iTS" monogram
- Keep it simple and professional
- Avoid too much detail (won't be visible at small sizes)

## Testing Icons

After creating icons, test them:

```bash
# View icon in different sizes
convert icon.png -resize 16x16 test-16.png
convert icon.png -resize 32x32 test-32.png
convert icon.png -resize 64x64 test-64.png
convert icon.png -resize 128x128 test-128.png

# Check if they're recognizable at each size
```

## Current Status

- [ ] icon.png (512x512) - Main icon
- [ ] icon.icns - macOS icon
- [ ] icon.ico - Windows icon
- [ ] tray-icon.png (16x16) - System tray icon
- [ ] dmg-background.png (800x400) - DMG background

**Once these are created, the desktop launcher will be 100% complete!**

## Need Help?

If you need assistance creating icons:
1. Provide the iTechSmart logo
2. Specify preferred colors/style
3. I can help generate placeholder icons or provide design specifications for a designer