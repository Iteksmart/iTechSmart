# Read the file
with open("itechsmart-ninja/vscode-extension/src/terminal/panel.ts", "r") as f:
    content = f.read()

# Find the Data Visualization section and add Document Processing section after it
old_section = """   Data Visualization:
     chart                     Create a new chart
     create-chart              (alias for chart)
     dashboard                 Create a dashboard
     create-dashboard          (alias for dashboard)
     list-charts               List all charts
     export-chart              Export chart to file
     analyze                   Analyze data file
     analyze-data              (alias for analyze)
   
   GitHub Commands:"""

new_section = """   Data Visualization:
     chart                     Create a new chart
     create-chart              (alias for chart)
     dashboard                 Create a dashboard
     create-dashboard          (alias for dashboard)
     list-charts               List all charts
     export-chart              Export chart to file
     analyze                   Analyze data file
     analyze-data              (alias for analyze)
   
   Document Processing:
     doc-upload                Upload document for processing
     upload-document           (alias for doc-upload)
     doc-list                  List all documents
     list-documents            (alias for doc-list)
     doc-extract               Extract text from document
     extract-text              (alias for doc-extract)
     doc-tables                Extract tables from document
     extract-tables            (alias for doc-tables)
     doc-ocr                   Perform OCR on document
     ocr-document              (alias for doc-ocr)
     doc-search                Search within document
     search-document           (alias for doc-search)
   
   GitHub Commands:"""

content = content.replace(old_section, new_section)

# Update examples section
old_examples = """   Examples:
     generate Create a REST API endpoint for user login
     research Latest AI trends in 2024
     analyze sales_data.csv
     img-generate A sunset over mountains
     chart                     Create a bar chart
     dashboard                 Create analytics dashboard
     gh-repos"""

new_examples = """   Examples:
     generate Create a REST API endpoint for user login
     research Latest AI trends in 2024
     analyze sales_data.csv
     img-generate A sunset over mountains
     chart                     Create a bar chart
     doc-upload                Upload a PDF document
     doc-extract               Extract text from PDF
     gh-repos"""

content = content.replace(old_examples, new_examples)

# Write back
with open("itechsmart-ninja/vscode-extension/src/terminal/panel.ts", "w") as f:
    f.write(content)

print("✓ Help text updated with document commands")
