#!/usr/bin/env python3
"""
Export iTechSmart Architecture Diagrams to Images
This script converts HTML diagrams to PNG/PDF for presentations
"""

import os
import subprocess
from pathlib import Path


def export_diagrams():
    """Export architecture diagrams to various formats"""

    print("🎨 Exporting iTechSmart Architecture Diagrams...")
    print()

    # Files to export
    html_files = [
        "iTechSmart_Architecture_Map.html",
        "iTechSmart_Architecture_Simple.html",
    ]

    # Check if files exist
    for html_file in html_files:
        if not os.path.exists(html_file):
            print(f"❌ Error: {html_file} not found")
            return False

    print("✅ Found all HTML files")
    print()

    # Instructions for manual export
    print("📋 EXPORT INSTRUCTIONS:")
    print()
    print("=" * 70)
    print("METHOD 1: Browser Screenshot (Recommended)")
    print("=" * 70)
    print()
    print("For iTechSmart_Architecture_Simple.html (Presentation Version):")
    print("1. Open iTechSmart_Architecture_Simple.html in Chrome/Firefox")
    print("2. Press F11 for fullscreen mode")
    print("3. Press Ctrl+P (Windows) or Cmd+P (Mac)")
    print("4. Select 'Save as PDF'")
    print("5. Choose 'Landscape' orientation")
    print("6. Set margins to 'None'")
    print("7. Enable 'Background graphics'")
    print("8. Save as 'iTechSmart_Architecture_Simple.pdf'")
    print()
    print("For High-Resolution PNG:")
    print("1. Open in Chrome")
    print("2. Press F12 to open DevTools")
    print("3. Press Ctrl+Shift+P (Windows) or Cmd+Shift+P (Mac)")
    print("4. Type 'screenshot' and select 'Capture full size screenshot'")
    print("5. Save as 'iTechSmart_Architecture_Simple.png'")
    print()

    print("=" * 70)
    print("METHOD 2: Online Converter")
    print("=" * 70)
    print()
    print("1. Go to https://www.web2pdfconvert.com/")
    print("2. Upload iTechSmart_Architecture_Simple.html")
    print("3. Click 'Convert to PDF'")
    print("4. Download the PDF")
    print()
    print("For PNG:")
    print("1. Go to https://cloudconvert.com/html-to-png")
    print("2. Upload the HTML file")
    print("3. Set width to 1920px for HD quality")
    print("4. Convert and download")
    print()

    print("=" * 70)
    print("METHOD 3: Command Line (If wkhtmltopdf installed)")
    print("=" * 70)
    print()

    # Try to use wkhtmltopdf if available
    try:
        subprocess.run(["wkhtmltopdf", "--version"], check=True, capture_output=True)

        print("✅ wkhtmltopdf found! Converting to PDF...")
        print()

        for html_file in html_files:
            output_pdf = html_file.replace(".html", ".pdf")

            cmd = [
                "wkhtmltopdf",
                "--enable-local-file-access",
                "--page-size",
                "A3",
                "--orientation",
                "Landscape",
                "--margin-top",
                "0",
                "--margin-bottom",
                "0",
                "--margin-left",
                "0",
                "--margin-right",
                "0",
                html_file,
                output_pdf,
            ]

            try:
                subprocess.run(cmd, check=True, capture_output=True)
                print(f"✅ Created: {output_pdf}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️  Error converting {html_file}: {e}")

        print()
        print("🎉 PDF export complete!")

    except FileNotFoundError:
        print("ℹ️  wkhtmltopdf not installed")
        print("   Install: sudo apt-get install wkhtmltopdf")
        print("   Or use Method 1 or 2 above")

    print()
    print("=" * 70)
    print("RECOMMENDED EXPORTS:")
    print("=" * 70)
    print()
    print("For Presentations:")
    print("  📄 iTechSmart_Architecture_Simple.pdf (Landscape, A3)")
    print()
    print("For Website:")
    print("  🖼️  iTechSmart_Architecture_Map.html (Use directly)")
    print()
    print("For Social Media:")
    print("  📱 iTechSmart_Architecture_Simple.png (1920x1080)")
    print()
    print("For Print:")
    print("  🖨️  iTechSmart_Architecture_Simple.pdf (A3, 300 DPI)")
    print()

    # Create a summary document
    create_export_summary()

    return True


def create_export_summary():
    """Create a summary document with export information"""

    summary = """# 📊 Architecture Diagram Export Summary

## Files Available

### HTML Files (Interactive)
1. **iTechSmart_Architecture_Map.html**
   - Interactive version with hover effects
   - Best for: Website, detailed presentations
   - Size: ~15 KB
   - Opens in any browser

2. **iTechSmart_Architecture_Simple.html**
   - Clean presentation version
   - Best for: Investor pitches, print
   - Size: ~10 KB
   - Print-friendly

## Recommended Exports

### For Investor Pitches
- **Format:** PDF
- **File:** iTechSmart_Architecture_Simple.pdf
- **Size:** A3 Landscape
- **Quality:** 300 DPI
- **Use:** Print and present

### For Website
- **Format:** HTML (use directly)
- **File:** iTechSmart_Architecture_Map.html
- **Embed:** iFrame or direct link
- **Responsive:** Yes

### For Social Media
- **Format:** PNG
- **File:** iTechSmart_Architecture_Simple.png
- **Size:** 1920x1080 (HD)
- **Platforms:** LinkedIn, Twitter, Facebook

### For Email
- **Format:** PNG
- **File:** iTechSmart_Architecture_Simple.png
- **Size:** 1200x800 (optimized)
- **Compress:** Use TinyPNG

### For Print Materials
- **Format:** PDF
- **File:** iTechSmart_Architecture_Simple.pdf
- **Size:** A3 or Tabloid
- **Quality:** 300 DPI minimum

## Quick Export Guide

### Browser Method (Easiest)
1. Open HTML file in Chrome
2. Press Ctrl+P (Print)
3. Save as PDF
4. Done!

### Screenshot Method (For PNG)
1. Open HTML file in Chrome
2. Press F12 (DevTools)
3. Ctrl+Shift+P → "Capture full size screenshot"
4. Save PNG

### Online Converter (No Software)
1. Go to web2pdfconvert.com
2. Upload HTML file
3. Download PDF
4. Done!

## File Sizes

| Format | Size | Best For |
|--------|------|----------|
| HTML | 10-15 KB | Website, email |
| PDF | 200-500 KB | Presentations, print |
| PNG (HD) | 500-800 KB | Social media |
| PNG (4K) | 1-2 MB | High-quality print |

## Usage Rights

✅ Use in presentations
✅ Use on website
✅ Use in marketing materials
✅ Share with clients/investors
✅ Print for events

❌ Do not modify without approval
❌ Do not remove branding
❌ Do not share source files publicly

## Support

Questions? Contact:
- Design: design@itechsmart.dev
- Technical: support@itechsmart.dev

---

*Last updated: December 2024*
"""

    with open("ARCHITECTURE_EXPORT_GUIDE.md", "w") as f:
        f.write(summary)

    print("📝 Created: ARCHITECTURE_EXPORT_GUIDE.md")
    print()


if __name__ == "__main__":
    export_diagrams()
    print("✅ Export guide complete!")
    print()
    print("📁 Files ready:")
    print("   • iTechSmart_Architecture_Map.html")
    print("   • iTechSmart_Architecture_Simple.html")
    print("   • ARCHITECTURE_DIAGRAMS_README.md")
    print("   • ARCHITECTURE_EXPORT_GUIDE.md")
    print()
    print("🚀 Next: Open the HTML files in your browser!")
