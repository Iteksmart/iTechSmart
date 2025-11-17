"""
Linux Package Creator
Creates DEB, RPM, and AppImage packages for iTechSmart products
"""

import os
import sys
import subprocess
import shutil
import json
from pathlib import Path


class LinuxPackageCreator:
    """Create Linux packages (DEB, RPM, AppImage)"""

    def __init__(self, product_name: str, version: str):
        self.product_name = product_name
        self.version = version
        self.workspace = Path.cwd()
        self.dist_dir = self.workspace / "dist" / "linux" / product_name
        self.installer_dir = self.workspace / "installers" / "linux" / product_name

    def prepare_environment(self):
        """Prepare package build environment"""
        print(f"Preparing package environment for {self.product_name}...")
        self.installer_dir.mkdir(parents=True, exist_ok=True)

    def get_product_metadata(self) -> dict:
        """Get product metadata"""
        metadata_file = self.workspace / self.product_name / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file) as f:
                return json.load(f)

        return {
            "name": self.product_name.replace("-", " ").title(),
            "description": f"{self.product_name} - iTechSmart Suite",
            "version": self.version,
            "company": "iTechSmart",
            "maintainer": "iTechSmart <support@itechsmart.com>",
            "homepage": "https://itechsmart.com",
        }

    def create_deb_package(self):
        """Create Debian package"""
        print("Creating DEB package...")

        metadata = self.get_product_metadata()
        deb_dir = self.installer_dir / "deb"

        # Create directory structure
        dirs = [
            deb_dir / "DEBIAN",
            deb_dir / "usr" / "bin",
            deb_dir / "usr" / "share" / "applications",
            deb_dir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps",
            deb_dir / "usr" / "share" / self.product_name,
        ]

        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

        # Copy binary
        binary_src = self.dist_dir / self.product_name
        binary_dst = deb_dir / "usr" / "share" / self.product_name / self.product_name
        if binary_src.exists():
            shutil.copy2(binary_src, binary_dst)
            os.chmod(binary_dst, 0o755)

        # Create symlink in /usr/bin
        bin_link = deb_dir / "usr" / "bin" / self.product_name
        os.symlink(f"/usr/share/{self.product_name}/{self.product_name}", bin_link)

        # Copy desktop file
        desktop_src = self.dist_dir / f"{self.product_name}.desktop"
        desktop_dst = (
            deb_dir / "usr" / "share" / "applications" / f"{self.product_name}.desktop"
        )
        if desktop_src.exists():
            shutil.copy2(desktop_src, desktop_dst)

        # Copy icon
        icon_src = (
            self.workspace
            / "installers"
            / "assets"
            / "icons"
            / f"{self.product_name}.png"
        )
        icon_dst = (
            deb_dir
            / "usr"
            / "share"
            / "icons"
            / "hicolor"
            / "256x256"
            / "apps"
            / f"{self.product_name}.png"
        )
        if icon_src.exists():
            shutil.copy2(icon_src, icon_dst)

        # Create control file
        control_content = f"""Package: {self.product_name}
Version: {self.version}
Section: utils
Priority: optional
Architecture: amd64
Maintainer: {metadata['maintainer']}
Description: {metadata['description']}
 {metadata['name']} is part of the iTechSmart Suite.
 .
 For more information, visit {metadata['homepage']}
Homepage: {metadata['homepage']}
"""

        control_file = deb_dir / "DEBIAN" / "control"
        control_file.write_text(control_content)

        # Create postinst script
        postinst_content = """#!/bin/bash
set -e

# Update desktop database
if [ -x /usr/bin/update-desktop-database ]; then
    update-desktop-database -q
fi

# Update icon cache
if [ -x /usr/bin/gtk-update-icon-cache ]; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor
fi

exit 0
"""

        postinst_file = deb_dir / "DEBIAN" / "postinst"
        postinst_file.write_text(postinst_content)
        os.chmod(postinst_file, 0o755)

        # Build DEB package
        deb_file = self.installer_dir / f"{self.product_name}_{self.version}_amd64.deb"

        try:
            subprocess.run(
                [
                    "dpkg-deb",
                    "--build",
                    "--root-owner-group",
                    str(deb_dir),
                    str(deb_file),
                ],
                check=True,
                capture_output=True,
            )

            print(f"✓ DEB package created: {deb_file}")

            # Cleanup
            shutil.rmtree(deb_dir)

        except subprocess.CalledProcessError as e:
            print(f"⚠ DEB creation failed: {e}")
            print(f"  stderr: {e.stderr.decode() if e.stderr else 'N/A'}")

    def create_rpm_package(self):
        """Create RPM package"""
        print("Creating RPM package...")

        metadata = self.get_product_metadata()
        rpm_dir = self.installer_dir / "rpm"

        # Create directory structure
        dirs = [
            rpm_dir / "BUILD",
            rpm_dir / "RPMS",
            rpm_dir / "SOURCES",
            rpm_dir / "SPECS",
            rpm_dir / "SRPMS",
        ]

        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

        # Create spec file
        spec_content = f"""
Name:           {self.product_name}
Version:        {self.version}
Release:        1%{{?dist}}
Summary:        {metadata['description']}

License:        Proprietary
URL:            {metadata['homepage']}
Source0:        %{{name}}-%{{version}}.tar.gz

BuildArch:      x86_64
Requires:       glibc

%description
{metadata['name']} is part of the iTechSmart Suite.

For more information, visit {metadata['homepage']}

%prep
%setup -q

%build
# Nothing to build

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT/usr/bin
mkdir -p $RPM_BUILD_ROOT/usr/share/applications
mkdir -p $RPM_BUILD_ROOT/usr/share/icons/hicolor/256x256/apps
mkdir -p $RPM_BUILD_ROOT/usr/share/{self.product_name}

install -m 755 {self.product_name} $RPM_BUILD_ROOT/usr/share/{self.product_name}/{self.product_name}
ln -s /usr/share/{self.product_name}/{self.product_name} $RPM_BUILD_ROOT/usr/bin/{self.product_name}
install -m 644 {self.product_name}.desktop $RPM_BUILD_ROOT/usr/share/applications/
install -m 644 {self.product_name}.png $RPM_BUILD_ROOT/usr/share/icons/hicolor/256x256/apps/

%files
/usr/bin/{self.product_name}
/usr/share/{self.product_name}/{self.product_name}
/usr/share/applications/{self.product_name}.desktop
/usr/share/icons/hicolor/256x256/apps/{self.product_name}.png

%post
update-desktop-database &amp;> /dev/null || :
gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor &amp;> /dev/null || :

%postun
update-desktop-database &amp;> /dev/null || :
gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor &amp;> /dev/null || :

%changelog
* {subprocess.check_output(['date', '+%a %b %d %Y'], text=True).strip()} iTechSmart <support@itechsmart.com> - {self.version}-1
- Initial release
"""

        spec_file = rpm_dir / "SPECS" / f"{self.product_name}.spec"
        spec_file.write_text(spec_content)

        print("⚠ RPM creation requires rpmbuild. Spec file created.")

    def create_appimage(self):
        """Create AppImage"""
        print("Creating AppImage...")

        metadata = self.get_product_metadata()
        appdir = self.installer_dir / f"{self.product_name}.AppDir"

        # Create AppDir structure
        dirs = [
            appdir / "usr" / "bin",
            appdir / "usr" / "share" / "applications",
            appdir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps",
        ]

        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)

        # Copy binary
        binary_src = self.dist_dir / self.product_name
        binary_dst = appdir / "usr" / "bin" / self.product_name
        if binary_src.exists():
            shutil.copy2(binary_src, binary_dst)
            os.chmod(binary_dst, 0o755)

        # Copy desktop file
        desktop_src = self.dist_dir / f"{self.product_name}.desktop"
        desktop_dst = (
            appdir / "usr" / "share" / "applications" / f"{self.product_name}.desktop"
        )
        if desktop_src.exists():
            shutil.copy2(desktop_src, desktop_dst)
            shutil.copy2(desktop_src, appdir / f"{self.product_name}.desktop")

        # Copy icon
        icon_src = (
            self.workspace
            / "installers"
            / "assets"
            / "icons"
            / f"{self.product_name}.png"
        )
        icon_dst = (
            appdir
            / "usr"
            / "share"
            / "icons"
            / "hicolor"
            / "256x256"
            / "apps"
            / f"{self.product_name}.png"
        )
        if icon_src.exists():
            shutil.copy2(icon_src, icon_dst)
            shutil.copy2(icon_src, appdir / f"{self.product_name}.png")

        # Create AppRun script
        apprun_content = f"""#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${{SELF%/*}}
export PATH="${{HERE}}/usr/bin:${{PATH}}"
export LD_LIBRARY_PATH="${{HERE}}/usr/lib:${{LD_LIBRARY_PATH}}"
exec "${{HERE}}/usr/bin/{self.product_name}" "$@"
"""

        apprun_file = appdir / "AppRun"
        apprun_file.write_text(apprun_content)
        os.chmod(apprun_file, 0o755)

        print(f"✓ AppImage directory created: {appdir}")
        print("⚠ AppImage creation requires appimagetool")

    def run(self):
        """Run the complete package creation process"""
        print("=" * 60)
        print(f"Creating Linux Packages: {self.product_name}")
        print(f"Version: {self.version}")
        print("=" * 60)

        try:
            self.prepare_environment()
            self.create_deb_package()
            self.create_rpm_package()
            self.create_appimage()

            print("\n" + "=" * 60)
            print("✓ PACKAGE CREATION SUCCESSFUL")
            print("=" * 60)
            print(f"Output directory: {self.installer_dir}")

            return True

        except Exception as e:
            print("\n" + "=" * 60)
            print("✗ PACKAGE CREATION FAILED")
            print("=" * 60)
            print(f"Error: {e}")
            import traceback

            traceback.print_exc()
            return False


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_linux_packages.py <product_name> <version>")
        sys.exit(1)

    product_name = sys.argv[1]
    version = sys.argv[2]

    creator = LinuxPackageCreator(product_name, version)
    success = creator.run()

    sys.exit(0 if success else 1)
