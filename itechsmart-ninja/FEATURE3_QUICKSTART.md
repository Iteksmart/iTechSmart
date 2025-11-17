# Feature 3: Embedded Code Editors - Quick Start Guide

## 🚀 Getting Started

This guide will help you quickly start using the embedded code editors in iTechSmart Ninja.

---

## 📋 Prerequisites

1. iTechSmart Ninja backend running
2. VS Code extension installed
3. Authenticated user session

---

## 🎯 Quick Access Methods

### Method 1: Command Palette (Ctrl+Shift+P)

```
iTechSmart: Open Monaco Editor
iTechSmart: Open Image Editor
iTechSmart: Open Website Builder
iTechSmart: Open Markdown Editor
iTechSmart: Open JSON Editor
iTechSmart: Open YAML Editor
```

### Method 2: Terminal Commands

Open iTechSmart terminal and use:
```bash
> monaco          # Open Monaco editor
> edit file.py    # Open file in Monaco
> image-edit      # Open image editor
> website         # Open website builder
> markdown        # Open markdown editor
> json-edit       # Open JSON editor
> yaml-edit       # Open YAML editor
> editors         # List active editors
```

### Method 3: Context Menu

Right-click on a file in VS Code Explorer:
- **Edit in Monaco** - For code files
- **Edit Image** - For image files (.png, .jpg, .svg)

---

## 📝 Monaco Editor

### Opening a New Editor

1. Press `Ctrl+Shift+P`
2. Type "Monaco"
3. Select "iTechSmart: Open Monaco Editor"
4. Choose language (Python, JavaScript, etc.)
5. Choose theme (Dark or Light)

### Opening an Existing File

**Terminal:**
```bash
> edit src/main.py
```

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "Open File in Monaco"
3. Select file

### Saving Files

Click the **Save** button in the editor toolbar or use `Ctrl+S`.

### Supported Languages

- Python (.py)
- JavaScript (.js, .mjs)
- TypeScript (.ts)
- HTML (.html, .htm)
- CSS (.css)
- JSON (.json)
- YAML (.yaml, .yml)
- Markdown (.md)
- Java (.java)
- Go (.go)
- Rust (.rs)
- C++ (.cpp, .cc)
- C (.c, .h)
- Ruby (.rb)
- PHP (.php)
- Swift (.swift)
- Kotlin (.kt)
- SQL (.sql)
- Shell (.sh, .bash)
- Dockerfile

---

## 🎨 Image Editor

### Creating a New Image

**Terminal:**
```bash
> image-edit
```

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "Image Editor"
3. Select "iTechSmart: Open Image Editor"
4. Enter canvas width (default: 800)
5. Enter canvas height (default: 600)

### Editing an Existing Image

**Terminal:**
```bash
> image-edit path/to/image.png
```

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "Edit Image"
3. Select file

### Drawing Tools

- **Rectangle** - Click to add rectangle
- **Circle** - Click to add circle
- **Text** - Click to add text
- **Move** - Drag objects to move
- **Resize** - Drag corners to resize

### Exporting

Click **Export PNG** or **Export JPG** button to save your image.

---

## 🌐 Website Builder

### Creating a New Website

**Terminal:**
```bash
> website
```

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "Website Builder"
3. Select "iTechSmart: Open Website Builder"
4. Enter project name
5. Choose template:
   - **Blank** - Start from scratch
   - **Landing Page** - Single page website
   - **Portfolio** - Showcase your work
   - **Blog** - Content-focused site
   - **Business** - Corporate website

### Building Your Site

1. **Drag components** from the left panel
2. **Drop on canvas** to add elements
3. **Click to edit** text and properties
4. **Preview** in different screen sizes

### Exporting

Click **Export HTML** to download your website files.

---

## 📄 Markdown Editor

### Opening Markdown Editor

**Terminal:**
```bash
> markdown
```

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "Markdown"
3. Select "iTechSmart: Open Markdown Editor"

### Features

- **Left Pane:** Write markdown
- **Right Pane:** Live HTML preview
- **Word Count:** Displayed in toolbar
- **Auto-save:** Saves as you type

### Saving

Click **Save** button to save as .md file.

---

## 📋 JSON Editor

### Opening JSON Editor

**Terminal:**
```bash
> json-edit
```

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "JSON"
3. Select "iTechSmart: Open JSON Editor"

### Features

- **Real-time Validation:** Errors shown immediately
- **Auto-formatting:** Click "Format" button
- **Syntax Highlighting:** Color-coded JSON
- **Status Indicator:** ✓ Valid or ✗ Invalid

### Validation

The editor automatically validates JSON as you type. Invalid JSON will show:
- Red status indicator
- Error message with line number

---

## 📋 YAML Editor

### Opening YAML Editor

**Terminal:**
```bash
> yaml-edit
```

**Command Palette:**
1. Press `Ctrl+Shift+P`
2. Type "YAML"
3. Select "iTechSmart: Open YAML Editor"

### Features

- **Left Pane:** YAML content
- **Right Pane:** JSON equivalent
- **Real-time Validation:** Errors shown immediately
- **Auto-formatting:** Proper indentation
- **YAML ↔ JSON Conversion:** See both formats

### Validation

The editor automatically validates YAML and shows the JSON equivalent in real-time.

---

## 🔧 Managing Editors

### List Active Editors

**Terminal:**
```bash
> editors
```

**Output:**
```
📝 Active Editors:
════════════════════════════════════════════════════════════════════════════════

📝 MONACO
   ID: abc-123-def
   File: src/main.py
   Created: 12/20/2025, 10:30:00 AM
   Modified: Yes

🎨 IMAGE
   ID: def-456-ghi
   File: logo.png
   Created: 12/20/2025, 10:35:00 AM
   Modified: No

════════════════════════════════════════════════════════════════════════════════
Total: 2 editor(s)
```

### Close an Editor

Click the **Close** button in the editor toolbar.

---

## 💡 Tips & Tricks

### Monaco Editor
- Use `Ctrl+F` to find text
- Use `Ctrl+H` to find and replace
- Use `Ctrl+/` to toggle comments
- Use `Alt+Up/Down` to move lines

### Image Editor
- Hold `Shift` while resizing to maintain aspect ratio
- Double-click text to edit
- Use `Delete` key to remove selected object
- Click outside objects to deselect

### Website Builder
- Use the device icons to preview different screen sizes
- Click the code icon to view/edit HTML/CSS
- Use the layers panel to manage element order
- Save frequently to avoid losing work

### Markdown Editor
- Use `#` for headings (# H1, ## H2, ### H3)
- Use `**text**` for bold
- Use `*text*` for italic
- Use `` `code` `` for inline code
- Use triple backticks for code blocks

### JSON/YAML Editors
- Use the Format button to clean up messy JSON/YAML
- Check the status indicator before saving
- Use the validation errors to fix issues
- Copy the formatted output for use elsewhere

---

## 🐛 Troubleshooting

### Editor Won't Open
1. Check backend is running
2. Check you're logged in
3. Check console for errors
4. Try reloading VS Code

### Can't Save File
1. Check file permissions
2. Check disk space
3. Check file path is valid
4. Try saving to a different location

### Validation Errors
1. Check syntax carefully
2. Use the Format button
3. Compare with working examples
4. Check for missing commas/brackets

### Performance Issues
1. Close unused editors
2. Reduce canvas size (image editor)
3. Simplify website (website builder)
4. Clear browser cache

---

## 📚 Additional Resources

- **Full Documentation:** See `FEATURE3_COMPLETE.md`
- **API Reference:** See `backend/app/api/editors.py`
- **Examples:** See `examples/` directory
- **Support:** Open an issue on GitHub

---

## 🎉 Quick Examples

### Example 1: Edit Python File
```bash
> edit src/main.py
# Edit code in Monaco editor
# Click Save when done
```

### Example 2: Create Logo
```bash
> image-edit
# Add shapes and text
# Export as PNG
```

### Example 3: Build Landing Page
```bash
> website
# Enter project name: "my-landing-page"
# Choose template: "Landing Page"
# Drag and drop components
# Export HTML
```

### Example 4: Write Documentation
```bash
> markdown
# Write markdown content
# See live preview
# Save as README.md
```

### Example 5: Edit Configuration
```bash
> json-edit
# Paste JSON config
# Click Format
# Fix any errors
# Save
```

---

**Happy Editing! 🚀**