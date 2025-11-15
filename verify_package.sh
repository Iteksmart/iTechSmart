#!/bin/bash

echo "=========================================="
echo "iTechSmart Suite Package Verification"
echo "=========================================="
echo ""

# Check for required files
echo "Checking core files..."

files=(
    "src/license-system/license_manager.py"
    "src/auto-update/update_manager.py"
    "src/telemetry/telemetry_manager.py"
    "src/crash-reporting/crash_reporter.py"
    "src/launcher/itechsmart_launcher.py"
    "build-tools/master_build.py"
    "build-tools/build_all_products.py"
    "build-tools/create_installers.py"
    "build-tools/build_for_client.py"
    "clients/template/config.json"
    "logo itechsmart.JPG"
)

missing=0
for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file (MISSING)"
        missing=$((missing + 1))
    fi
done

echo ""
echo "Checking documentation..."

docs=(
    "INSTALLER_BUILD_GUIDE.md"
    "CLIENT_CUSTOMIZATION_GUIDE.md"
    "COMPLETE_BUILD_PACKAGE_SUMMARY.md"
    "FINAL_COMPLETE_PACKAGE.md"
    "QUICK_REFERENCE.md"
)

for doc in "${docs[@]}"; do
    if [ -f "$doc" ]; then
        echo "✓ $doc"
    else
        echo "✗ $doc (MISSING)"
        missing=$((missing + 1))
    fi
done

echo ""
echo "Checking for .com references (should be 0)..."
com_count=$(grep -r "itechsmart\.com" --include="*.py" --include="*.md" src/ build-tools/ 2>/dev/null | wc -l)
echo "Found: $com_count references"

if [ $com_count -eq 0 ]; then
    echo "✓ All URLs correctly use .dev domain"
else
    echo "✗ Some .com references still exist"
    missing=$((missing + 1))
fi

echo ""
echo "=========================================="
if [ $missing -eq 0 ]; then
    echo "✅ VERIFICATION PASSED"
    echo "All components are in place!"
else
    echo "❌ VERIFICATION FAILED"
    echo "Missing $missing components"
fi
echo "=========================================="
