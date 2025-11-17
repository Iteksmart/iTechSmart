#!/usr/bin/env python3
"""
Compile iTechSmart Go-To-Market Manual into PDF
This script converts all GTM markdown files into a comprehensive PDF manual
"""

import os
import subprocess
from datetime import datetime


def create_cover_page():
    """Create a professional cover page"""
    cover = """---
title: "iTechSmart Go-To-Market Master Manual"
subtitle: "Complete Implementation Guide with Tracking System"
author: "iTechSmart Strategy Team"
date: "{date}"
geometry: margin=1in
fontsize: 12pt
documentclass: report
toc: true
toc-depth: 3
numbersections: true
colorlinks: true
linkcolor: blue
urlcolor: blue
header-includes:
  - \\usepackage{{fancyhdr}}
  - \\pagestyle{{fancy}}
  - \\fancyhead[L]{{iTechSmart GTM Manual}}
  - \\fancyhead[R]{{\\thepage}}
  - \\fancyfoot[C]{{Confidential - Internal Use Only}}
  - \\usepackage{{graphicx}}
  - \\usepackage{{xcolor}}
  - \\definecolor{{itechblue}}{{RGB}}{{10, 36, 99}}
  - \\definecolor{{itechgreen}}{{RGB}}{{82, 214, 129}}
---

\\newpage

# Executive Summary

This comprehensive Go-To-Market (GTM) manual provides step-by-step implementation strategies for all iTechSmart products. It is designed as a working document with completion tracking, notes sections, and actionable tasks.

## Document Purpose

This manual serves as:

1. **Strategic Roadmap** - Complete GTM strategy for each product
2. **Implementation Guide** - Step-by-step execution plans
3. **Tracking System** - Progress monitoring and completion tracking
4. **Reference Manual** - Comprehensive product information and FAQs
5. **Training Resource** - Onboarding guide for new team members

## How to Use This Manual

### Daily Usage
- Review your assigned tasks each morning
- Execute tasks systematically
- Document progress and learnings in notes sections
- Check off completed items
- Update tracking dashboards

### Weekly Reviews
- Review completed tasks
- Assess progress against targets
- Identify and address blockers
- Adjust timelines if needed
- Update stakeholders

### Monthly Reviews
- Comprehensive progress review
- Strategy adjustments
- Budget review
- Team alignment
- Planning for next month

## Portfolio Overview

### Products Covered

1. **iTechSmart Core** - AI-powered IT troubleshooting ($0-60/mo)
2. **iTechSmart Ninja** - Autonomous development assistant ($20-100/mo)
3. **iTechSmart Supreme** - Self-healing infrastructure ($1.5K-6K/mo)
4. **iTechSmart Enterprise** - Enterprise integration platform (Custom)
5. **iTechSmart HL7** - Healthcare integration monitoring (Custom)
6. **iTechSmart Citadel** - Sovereign digital infrastructure (Q4 2025)

### Portfolio Value

- **Development Value:** $1,280,238.80
- **Current Market Value:** $319.4M (with projections)
- **5-Year Projected Valuation:** $7.1B

### Success Metrics (90 Days)

| Metric | Target |
|--------|--------|
| **Total ARR** | $1.7M |
| **Total Customers** | 2,500 |
| **Pipeline Value** | $20M |
| **Website Traffic** | 150K visits |
| **Team Size** | 50 employees |

## Document Structure

This manual is organized into the following sections:

1. **Product GTM Strategies** - Individual strategies for each product
2. **Overall Business Strategy** - Unified company-wide approach
3. **Comprehensive FAQ** - Answers to all common questions
4. **Appendices** - Additional resources and templates

## Getting Started

To begin implementation:

1. ✅ Read the Executive Summary (this section)
2. ✅ Review the Overall Business Strategy
3. ✅ Deep dive into your product's GTM strategy
4. ✅ Set up tracking systems
5. ✅ Begin Week 1 tasks
6. ✅ Schedule weekly team meetings
7. ✅ Establish reporting cadence

## Key Success Factors

### 1. Execution Excellence
- Follow the plan systematically
- Don't skip steps
- Document everything
- Measure progress daily

### 2. Customer Focus
- Always prioritize customer needs
- Listen to feedback
- Iterate quickly
- Deliver value early

### 3. Team Alignment
- Clear communication
- Regular check-ins
- Shared goals
- Collaborative culture

### 4. Data-Driven Decisions
- Track all metrics
- Analyze results
- Adjust based on data
- Test and learn

### 5. Continuous Improvement
- Regular retrospectives
- Learn from failures
- Celebrate wins
- Iterate constantly

## Important Notes

### Confidentiality
This document contains confidential business information. Do not share outside the organization without explicit approval.

### Version Control
- **Version:** 1.0
- **Last Updated:** {date}
- **Next Review:** 30 days from publication
- **Owner:** VP of Strategy

### Feedback
We welcome feedback to improve this manual. Please submit suggestions to: strategy@itechsmart.dev

---

\\newpage
""".format(
        date=datetime.now().strftime("%B %d, %Y")
    )

    return cover


def compile_pdf():
    """Compile all markdown files into a single PDF"""

    print("🚀 Starting iTechSmart GTM Manual Compilation...")

    # Create cover page
    print("📄 Creating cover page...")
    cover_content = create_cover_page()

    # List of markdown files in order
    md_files = [
        "ITECHSMART_GTM_MASTER_PLAN.md",
        "GTM_PRODUCT_1_ITECHSMART_CORE.md",
        "GTM_PRODUCT_2_ITECHSMART_NINJA.md",
        "GTM_PRODUCT_3_ITECHSMART_SUPREME.md",
        "GTM_PRODUCT_4_ENTERPRISE_HL7_CITADEL.md",
        "GTM_OVERALL_BUSINESS_STRATEGY.md",
        "GTM_COMPREHENSIVE_FAQ.md",
    ]

    # Read and combine all markdown files
    print("📚 Reading markdown files...")
    combined_content = cover_content

    for md_file in md_files:
        if os.path.exists(md_file):
            print(f"   ✓ Reading {md_file}")
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
                # Add page break before each major section
                combined_content += "\n\\newpage\n\n" + content
        else:
            print(f"   ⚠ Warning: {md_file} not found, skipping...")

    # Write combined markdown
    combined_md = "ITECHSMART_GTM_COMPLETE_MANUAL.md"
    print(f"📝 Writing combined markdown to {combined_md}...")
    with open(combined_md, "w", encoding="utf-8") as f:
        f.write(combined_content)

    # Convert to PDF using pandoc
    output_pdf = "iTechSmart_GTM_Master_Manual.pdf"
    print(f"🔄 Converting to PDF: {output_pdf}...")

    try:
        # Check if pandoc is installed
        subprocess.run(["pandoc", "--version"], check=True, capture_output=True)

        # Convert to PDF with pandoc
        cmd = [
            "pandoc",
            combined_md,
            "-o",
            output_pdf,
            "--pdf-engine=xelatex",
            "--toc",
            "--toc-depth=3",
            "--number-sections",
            "--highlight-style=tango",
            "-V",
            "geometry:margin=1in",
            "-V",
            "fontsize=11pt",
            "-V",
            "documentclass=report",
            "-V",
            "colorlinks=true",
            "-V",
            "linkcolor=blue",
            "-V",
            "urlcolor=blue",
        ]

        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ PDF created successfully: {output_pdf}")
        print(f"📊 File size: {os.path.getsize(output_pdf) / 1024 / 1024:.2f} MB")

    except FileNotFoundError:
        print("❌ Error: pandoc not found. Please install pandoc:")
        print("   Ubuntu/Debian: sudo apt-get install pandoc texlive-xetex")
        print("   macOS: brew install pandoc basictex")
        print("   Windows: Download from https://pandoc.org/installing.html")
        print("\n📄 Combined markdown file created: {combined_md}")
        print("   You can convert it to PDF manually or use an online converter.")
        return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during PDF conversion: {e}")
        print(f"   stderr: {e.stderr}")
        print(f"\n📄 Combined markdown file created: {combined_md}")
        return False

    # Create a Word document as alternative
    try:
        output_docx = "iTechSmart_GTM_Master_Manual.docx"
        print(f"📝 Creating Word document: {output_docx}...")

        cmd_docx = [
            "pandoc",
            combined_md,
            "-o",
            output_docx,
            "--toc",
            "--toc-depth=3",
            "--number-sections",
            "--highlight-style=tango",
        ]

        subprocess.run(cmd_docx, check=True, capture_output=True)
        print(f"✅ Word document created successfully: {output_docx}")
        print(f"📊 File size: {os.path.getsize(output_docx) / 1024 / 1024:.2f} MB")

    except Exception as e:
        print(f"⚠ Could not create Word document: {e}")

    print("\n🎉 Compilation complete!")
    print(f"\n📦 Generated files:")
    print(f"   • {combined_md} (Combined Markdown)")
    if os.path.exists(output_pdf):
        print(f"   • {output_pdf} (PDF Manual)")
    if os.path.exists(output_docx):
        print(f"   • {output_docx} (Word Document)")

    return True


if __name__ == "__main__":
    compile_pdf()
