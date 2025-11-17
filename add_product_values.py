#!/usr/bin/env python3

# Product values mapping
product_values = {
    "iTechSmart Compliance": "1.8M",
    "iTechSmart Connect": "1.5M",
    "iTechSmart Customer Success": "1.7M",
    "iTechSmart Data Platform": "2.8M",
    "iTechSmart DataFlow": "2.0M",
    "iTechSmart Forge": "1.9M",
    "iTechSmart HL7": "2.2M",
    "iTechSmart Impactos": "1.6M",
    "iTechSmart Ledger": "2.4M",
    "iTechSmart Marketplace": "2.1M",
    "iTechSmart MDM Agent": "1.5M",
    "iTechSmart Mobile": "2.0M",
    "iTechSmart Notify": "1.3M",
    "iTechSmart Observatory": "1.9M",
    "iTechSmart Port Manager": "1.2M",
    "iTechSmart Pulse": "1.6M",
    "iTechSmart QAQC": "1.7M",
    "iTechSmart Sandbox": "1.4M",
    "iTechSmart ThinkTank": "1.5M",
    "iTechSmart Vault": "2.0M",
    "iTechSmart Workflow": "2.2M",
    "LegalAI Pro": "2.5M",
    "Passport": "1.8M",
    "ProofLink": "1.6M",
    "iTechSmart Supreme": "2.0M"
}

# Read the HTML file
with open('ITECHSMART_SUITE_COMPLETE_DOCUMENTATION.html', 'r') as f:
    content = f.read()

# Add value badges to each product
for product, value in product_values.items():
    # Find the product card and add value badge after the description
    search_pattern = f'<h4>{product}</h4>'
    if search_pattern in content:
        # Find the position after the <p> tag
        pos = content.find(search_pattern)
        if pos != -1:
            # Find the closing </p> tag after this product
            p_close = content.find('</p>', pos)
            if p_close != -1:
                # Insert the value badge
                value_badge = f'\n                        <div style="margin-top: 15px;">\n                            <span class="badge badge-price">${value} Value</span>\n                        </div>'
                content = content[:p_close + 4] + value_badge + content[p_close + 4:]

# Write back to file
with open('ITECHSMART_SUITE_COMPLETE_DOCUMENTATION.html', 'w') as f:
    f.write(content)

print("Product values added successfully!")