# Read the file
with open("itechsmart-ninja/vscode-extension/src/terminal/panel.ts", "r") as f:
    content = f.read()

# Find the Image Generation section and add Visualization section after it
old_section = """   Image Generation:
     img-generate              Generate image from text
     generate-image            (alias for img-generate)
     img-transform             Transform an existing image
     transform-image           (alias for img-transform)
     img-upscale               Upscale image resolution
     upscale-image             (alias for img-upscale)
     img-remove-bg             Remove image background
     remove-background         (alias for img-remove-bg)
     img-providers             List available image providers
     list-image-providers      (alias for img-providers)
   
   GitHub Commands:"""

new_section = """   Image Generation:
     img-generate              Generate image from text
     generate-image            (alias for img-generate)
     img-transform             Transform an existing image
     transform-image           (alias for img-transform)
     img-upscale               Upscale image resolution
     upscale-image             (alias for img-upscale)
     img-remove-bg             Remove image background
     remove-background         (alias for img-remove-bg)
     img-providers             List available image providers
     list-image-providers      (alias for img-providers)
   
   Data Visualization:
     chart                     Create a new chart
     create-chart              (alias for chart)
     dashboard                 Create a dashboard
     create-dashboard          (alias for dashboard)
     list-charts               List all charts
     export-chart              Export chart to file
     analyze                   Analyze data file
     analyze-data              (alias for analyze)
   
   GitHub Commands:"""

content = content.replace(old_section, new_section)

# Update examples section
old_examples = """   Examples:
     generate Create a REST API endpoint for user login
     research Latest AI trends in 2024
     analyze sales_data.csv
     img-generate A sunset over mountains
     gh-repos"""

new_examples = """   Examples:
     generate Create a REST API endpoint for user login
     research Latest AI trends in 2024
     analyze sales_data.csv
     img-generate A sunset over mountains
     chart                     Create a bar chart
     dashboard                 Create analytics dashboard
     gh-repos"""

content = content.replace(old_examples, new_examples)

# Write back
with open("itechsmart-ninja/vscode-extension/src/terminal/panel.ts", "w") as f:
    f.write(content)

print("✓ Help text updated with visualization commands")
