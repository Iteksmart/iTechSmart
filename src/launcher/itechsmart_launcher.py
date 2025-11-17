"""
iTechSmart Suite - Main Launcher
Central launcher for all 36 products with license management
"""

import os
import sys
import json
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from license_system.license_manager import LicenseManager
from auto_update.update_manager import UpdateManager
from telemetry.telemetry_manager import TelemetryManager
from crash_reporting.crash_reporter import CrashReporter


class iTechSmartLauncher:
    """Main launcher application for iTechSmart Suite"""

    PRODUCTS = [
        {
            "id": 1,
            "name": "iTechSmart Enterprise",
            "exe": "itechsmart-enterprise.exe",
            "category": "Foundation",
        },
        {
            "id": 2,
            "name": "iTechSmart Ninja",
            "exe": "itechsmart-ninja.exe",
            "category": "Foundation",
        },
        {
            "id": 3,
            "name": "iTechSmart Analytics",
            "exe": "itechsmart-analytics.exe",
            "category": "Foundation",
        },
        {
            "id": 4,
            "name": "iTechSmart Supreme",
            "exe": "itechsmart-supreme.exe",
            "category": "Foundation",
        },
        {
            "id": 5,
            "name": "iTechSmart HL7",
            "exe": "itechsmart-hl7.exe",
            "category": "Foundation",
        },
        {
            "id": 6,
            "name": "ProofLink",
            "exe": "prooflink.exe",
            "category": "Foundation",
        },
        {"id": 7, "name": "PassPort", "exe": "passport.exe", "category": "Foundation"},
        {"id": 8, "name": "ImpactOS", "exe": "impactos.exe", "category": "Foundation"},
        {
            "id": 9,
            "name": "LegalAI Pro",
            "exe": "legalai-pro.exe",
            "category": "Foundation",
        },
        {
            "id": 10,
            "name": "iTechSmart DataFlow",
            "exe": "itechsmart-dataflow.exe",
            "category": "Strategic",
        },
        {
            "id": 11,
            "name": "iTechSmart Pulse",
            "exe": "itechsmart-pulse.exe",
            "category": "Strategic",
        },
        {
            "id": 12,
            "name": "iTechSmart Connect",
            "exe": "itechsmart-connect.exe",
            "category": "Strategic",
        },
        {
            "id": 13,
            "name": "iTechSmart Vault",
            "exe": "itechsmart-vault.exe",
            "category": "Strategic",
        },
        {
            "id": 14,
            "name": "iTechSmart Notify",
            "exe": "itechsmart-notify.exe",
            "category": "Strategic",
        },
        {
            "id": 15,
            "name": "iTechSmart Ledger",
            "exe": "itechsmart-ledger.exe",
            "category": "Strategic",
        },
        {
            "id": 16,
            "name": "iTechSmart Copilot",
            "exe": "itechsmart-copilot.exe",
            "category": "Strategic",
        },
        {
            "id": 17,
            "name": "iTechSmart Shield",
            "exe": "itechsmart-shield.exe",
            "category": "Strategic",
        },
        {
            "id": 18,
            "name": "iTechSmart Workflow",
            "exe": "itechsmart-workflow.exe",
            "category": "Strategic",
        },
        {
            "id": 19,
            "name": "iTechSmart Marketplace",
            "exe": "itechsmart-marketplace.exe",
            "category": "Strategic",
        },
        {
            "id": 20,
            "name": "iTechSmart Cloud",
            "exe": "itechsmart-cloud.exe",
            "category": "Business",
        },
        {
            "id": 21,
            "name": "iTechSmart DevOps",
            "exe": "itechsmart-devops.exe",
            "category": "Business",
        },
        {
            "id": 22,
            "name": "iTechSmart Mobile",
            "exe": "itechsmart-mobile.exe",
            "category": "Business",
        },
        {
            "id": 23,
            "name": "iTechSmart AI",
            "exe": "itechsmart-ai.exe",
            "category": "Business",
        },
        {
            "id": 24,
            "name": "iTechSmart Compliance",
            "exe": "itechsmart-compliance.exe",
            "category": "Business",
        },
        {
            "id": 25,
            "name": "iTechSmart Data Platform",
            "exe": "itechsmart-data-platform.exe",
            "category": "Business",
        },
        {
            "id": 26,
            "name": "iTechSmart Customer Success",
            "exe": "itechsmart-customer-success.exe",
            "category": "Business",
        },
        {
            "id": 27,
            "name": "iTechSmart Port Manager",
            "exe": "itechsmart-port-manager.exe",
            "category": "Infrastructure",
        },
        {
            "id": 28,
            "name": "iTechSmart MDM Agent",
            "exe": "itechsmart-mdm-agent.exe",
            "category": "Infrastructure",
        },
        {
            "id": 29,
            "name": "iTechSmart QA/QC",
            "exe": "itechsmart-qaqc.exe",
            "category": "Infrastructure",
        },
        {
            "id": 30,
            "name": "iTechSmart Think-Tank",
            "exe": "itechsmart-think-tank.exe",
            "category": "Internal",
        },
        {
            "id": 31,
            "name": "iTechSmart Sentinel",
            "exe": "itechsmart-sentinel.exe",
            "category": "Latest",
        },
        {
            "id": 32,
            "name": "iTechSmart Forge",
            "exe": "itechsmart-forge.exe",
            "category": "Latest",
        },
        {
            "id": 33,
            "name": "iTechSmart Sandbox",
            "exe": "itechsmart-sandbox.exe",
            "category": "Latest",
        },
        {
            "id": 34,
            "name": "iTechSmart Supreme Plus",
            "exe": "itechsmart-supreme-plus.exe",
            "category": "Latest",
        },
        {
            "id": 35,
            "name": "iTechSmart Citadel",
            "exe": "itechsmart-citadel.exe",
            "category": "Latest",
        },
        {
            "id": 36,
            "name": "iTechSmart Observatory",
            "exe": "itechsmart-observatory.exe",
            "category": "Latest",
        },
    ]

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("iTechSmart Suite Launcher")
        self.root.geometry("1200x800")

        # Initialize managers
        self.license_manager = LicenseManager()
        self.update_manager = UpdateManager()
        self.telemetry = TelemetryManager(enabled=True)
        self.crash_reporter = CrashReporter("iTechSmart Suite", "1.0.0")

        # Track session
        self.telemetry.start_session()

        # Setup UI
        self.setup_ui()

        # Check license
        self.check_license()

        # Check for updates
        self.check_updates()

    def setup_ui(self):
        """Setup the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Logo and header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, columnspan=2, pady=10)

        # Load and display logo
        try:
            logo_path = "assets/logo-256.png"
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((64, 64), Image.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = ttk.Label(header_frame, image=logo_photo)
                logo_label.image = logo_photo  # Keep reference
                logo_label.grid(row=0, column=0, padx=10)
        except:
            pass

        title_label = ttk.Label(
            header_frame, text="iTechSmart Suite", font=("Arial", 24, "bold")
        )
        title_label.grid(row=0, column=1, padx=10)

        subtitle_label = ttk.Label(
            header_frame,
            text="Complete Enterprise Platform - 36 Integrated Products",
            font=("Arial", 12),
        )
        subtitle_label.grid(row=1, column=1, padx=10)

        # License info
        license_frame = ttk.LabelFrame(
            main_frame, text="License Information", padding="10"
        )
        license_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)

        self.license_label = ttk.Label(license_frame, text="Checking license...")
        self.license_label.grid(row=0, column=0, sticky=tk.W)

        # Category tabs
        notebook = ttk.Notebook(main_frame)
        notebook.grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10
        )

        # Create tabs for each category
        categories = [
            "All",
            "Foundation",
            "Strategic",
            "Business",
            "Infrastructure",
            "Latest",
        ]

        for category in categories:
            tab_frame = ttk.Frame(notebook)
            notebook.add(tab_frame, text=category)

            # Create scrollable product list
            self.create_product_list(tab_frame, category)

        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.status_label = ttk.Label(status_frame, text="Ready")
        self.status_label.grid(row=0, column=0, sticky=tk.W)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(
            button_frame, text="Check for Updates", command=self.check_updates
        ).grid(row=0, column=0, padx=5)
        ttk.Button(
            button_frame, text="Manage License", command=self.manage_license
        ).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Settings", command=self.show_settings).grid(
            row=0, column=2, padx=5
        )
        ttk.Button(button_frame, text="Help", command=self.show_help).grid(
            row=0, column=3, padx=5
        )
        ttk.Button(button_frame, text="Exit", command=self.exit_app).grid(
            row=0, column=4, padx=5
        )

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)

    def create_product_list(self, parent, category):
        """Create product list for a category"""
        # Filter products by category
        if category == "All":
            products = self.PRODUCTS
        else:
            products = [p for p in self.PRODUCTS if p["category"] == category]

        # Create scrollable frame
        canvas = tk.Canvas(parent)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Add products
        for i, product in enumerate(products):
            product_frame = ttk.Frame(scrollable_frame, relief="raised", borderwidth=1)
            product_frame.grid(row=i, column=0, sticky=(tk.W, tk.E), padx=5, pady=5)

            # Product info
            info_frame = ttk.Frame(product_frame)
            info_frame.grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)

            name_label = ttk.Label(
                info_frame,
                text=f"{product['id']}. {product['name']}",
                font=("Arial", 11, "bold"),
            )
            name_label.grid(row=0, column=0, sticky=tk.W)

            category_label = ttk.Label(
                info_frame, text=f"Category: {product['category']}", font=("Arial", 9)
            )
            category_label.grid(row=1, column=0, sticky=tk.W)

            # Launch button
            launch_btn = ttk.Button(
                product_frame,
                text="Launch",
                command=lambda p=product: self.launch_product(p),
            )
            launch_btn.grid(row=0, column=1, padx=10, pady=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def check_license(self):
        """Check and display license status"""
        info = self.license_manager.get_license_info()

        if info["status"] == "valid":
            license_type = info["license_type"].upper()
            days_remaining = info.get("days_remaining")

            if days_remaining:
                license_text = (
                    f"✅ {license_type} License - {days_remaining} days remaining"
                )
            else:
                license_text = f"✅ {license_type} License - Perpetual"

            self.license_label.config(text=license_text, foreground="green")
        else:
            self.license_label.config(
                text="❌ No valid license - Click 'Manage License' to activate",
                foreground="red",
            )

            # Offer trial
            if messagebox.askyesno(
                "No License Found", "Would you like to start a 30-day trial?"
            ):
                self.start_trial()

    def start_trial(self):
        """Start trial license"""
        success, key, message = self.license_manager.create_trial_license()

        if success:
            messagebox.showinfo("Trial Started", message)
            self.check_license()
        else:
            messagebox.showerror("Trial Error", message)

    def launch_product(self, product):
        """Launch a product"""
        # Check license
        if not self.license_manager.check_product_access(product["name"]):
            messagebox.showerror(
                "Access Denied",
                f"Your license does not include access to {product['name']}",
            )
            return

        # Track launch
        self.telemetry.track_feature_usage(f"launch_{product['name']}")

        # Update status
        self.status_label.config(text=f"Launching {product['name']}...")

        # Launch executable
        exe_path = os.path.join("products", product["exe"])

        if os.path.exists(exe_path):
            try:
                subprocess.Popen([exe_path])
                self.status_label.config(text=f"✅ {product['name']} launched")
            except Exception as e:
                self.crash_reporter.report_crash(
                    type(e), e, sys.exc_info()[2], context={"product": product["name"]}
                )
                messagebox.showerror(
                    "Launch Error", f"Failed to launch {product['name']}: {str(e)}"
                )
        else:
            messagebox.showerror(
                "Product Not Found", f"Executable not found: {exe_path}"
            )

    def check_updates(self):
        """Check for updates"""
        self.status_label.config(text="Checking for updates...")

        has_update, update_info = self.update_manager.check_for_updates()

        if has_update:
            if messagebox.askyesno(
                "Update Available",
                f"Version {update_info.get('version')} is available.\n\nWould you like to update now?",
            ):
                self.install_update(update_info)
        else:
            self.status_label.config(text="✅ You have the latest version")
            messagebox.showinfo("No Updates", "You are running the latest version")

    def install_update(self, update_info):
        """Install update"""
        self.status_label.config(text="Downloading update...")

        success, result = self.update_manager.download_update(update_info)

        if success:
            self.status_label.config(text="Installing update...")
            success, message = self.update_manager.install_update(result, update_info)

            if success:
                messagebox.showinfo(
                    "Update Complete",
                    "Update installed successfully. Please restart the application.",
                )
                self.exit_app()
            else:
                messagebox.showerror("Update Failed", message)
        else:
            messagebox.showerror("Download Failed", result)

    def manage_license(self):
        """Open license management dialog"""
        dialog = tk.Toplevel(self.root)
        dialog.title("License Management")
        dialog.geometry("500x400")

        # License info
        info = self.license_manager.get_license_info()

        info_text = tk.Text(dialog, height=10, width=60)
        info_text.pack(padx=10, pady=10)
        info_text.insert("1.0", json.dumps(info, indent=2))
        info_text.config(state="disabled")

        # License key entry
        ttk.Label(dialog, text="Enter License Key:").pack(pady=5)

        key_entry = ttk.Entry(dialog, width=50)
        key_entry.pack(pady=5)

        def activate():
            key = key_entry.get().strip()
            if key:
                success, message = self.license_manager.activate_license(key)
                messagebox.showinfo("Activation", message)
                if success:
                    dialog.destroy()
                    self.check_license()

        ttk.Button(dialog, text="Activate", command=activate).pack(pady=10)

    def show_settings(self):
        """Show settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog coming soon!")

    def show_help(self):
        """Show help dialog"""
        messagebox.showinfo(
            "Help",
            "iTechSmart Suite v1.0.0\n\n"
            "For support, visit: https://itechsmart.dev/support\n"
            "Email: support@itechsmart.dev",
        )

    def exit_app(self):
        """Exit application"""
        self.telemetry.end_session()
        self.root.quit()

    def run(self):
        """Run the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = iTechSmartLauncher()
    app.run()
