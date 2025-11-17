#!/bin/bash

# Array of product names and their values
declare -A products=(
    ["iTechSmart Compliance"]="1.8M"
    ["iTechSmart Connect"]="1.5M"
    ["iTechSmart Customer Success"]="1.7M"
    ["iTechSmart Data Platform"]="2.8M"
    ["iTechSmart DataFlow"]="2.0M"
    ["iTechSmart Forge"]="1.9M"
    ["iTechSmart HL7"]="2.2M"
    ["iTechSmart Impactos"]="1.6M"
    ["iTechSmart Ledger"]="2.4M"
    ["iTechSmart Marketplace"]="2.1M"
    ["iTechSmart MDM Agent"]="1.5M"
    ["iTechSmart Mobile"]="2.0M"
    ["iTechSmart Notify"]="1.3M"
    ["iTechSmart Observatory"]="1.9M"
    ["iTechSmart Port Manager"]="1.2M"
    ["iTechSmart Pulse"]="1.6M"
    ["iTechSmart QAQC"]="1.7M"
    ["iTechSmart Sandbox"]="1.4M"
    ["iTechSmart ThinkTank"]="1.5M"
    ["iTechSmart Vault"]="2.0M"
    ["iTechSmart Workflow"]="2.2M"
    ["LegalAI Pro"]="2.5M"
    ["Passport"]="1.8M"
    ["ProofLink"]="1.6M"
    ["iTechSmart Supreme"]="2.0M"
)

for product in "${!products[@]}"; do
    value="${products[$product]}"
    sed -i "s|<h4>$product</h4>\n                        <p>|<h4>$product</h4>\n                        <p>|" ITECHSMART_SUITE_COMPLETE_DOCUMENTATION.html
done
