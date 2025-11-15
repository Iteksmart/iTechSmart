"""
Executable Testing Framework
Tests built executables across all platforms
"""

import os
import sys
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

class ExecutableTester:
    """Test built executables"""
    
    def __init__(self, platform: str, version: str):
        self.platform = platform
        self.version = version
        self.workspace = Path.cwd()
        self.dist_dir = self.workspace / "dist" / platform
        self.test_results = []
        
    def discover_executables(self) -> List[Path]:
        """Discover all executables to test"""
        executables = []
        
        if self.platform == "windows":
            executables = list(self.dist_dir.rglob("*.exe"))
        elif self.platform == "macos":
            executables = list(self.dist_dir.rglob("*.app"))
        elif self.platform == "linux":
            # Find executable files
            for item in self.dist_dir.rglob("*"):
                if item.is_file() and os.access(item, os.X_OK):
                    executables.append(item)
        
        return executables
    
    def test_executable_exists(self, exe_path: Path) -> Tuple[bool, str]:
        """Test if executable exists"""
        if exe_path.exists():
            return True, f"Executable exists: {exe_path}"
        else:
            return False, f"Executable not found: {exe_path}"
    
    def test_executable_permissions(self, exe_path: Path) -> Tuple[bool, str]:
        """Test if executable has correct permissions"""
        if self.platform == "windows":
            return True, "Windows executables don't require permission check"
        
        if os.access(exe_path, os.X_OK):
            return True, f"Executable has correct permissions: {exe_path}"
        else:
            return False, f"Executable lacks execute permission: {exe_path}"
    
    def test_executable_launch(self, exe_path: Path) -> Tuple[bool, str]:
        """Test if executable can launch"""
        try:
            # Try to launch with --version or --help flag
            if self.platform == "windows":
                cmd = [str(exe_path), "--version"]
            elif self.platform == "macos":
                # For .app bundles, find the actual executable
                exe_name = exe_path.stem
                actual_exe = exe_path / "Contents" / "MacOS" / exe_name
                if actual_exe.exists():
                    cmd = [str(actual_exe), "--version"]
                else:
                    return False, f"Cannot find executable in .app bundle: {exe_path}"
            else:
                cmd = [str(exe_path), "--version"]
            
            # Run with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return True, f"Executable launched successfully: {exe_path}"
            
        except subprocess.TimeoutExpired:
            return False, f"Executable launch timeout: {exe_path}"
        except Exception as e:
            return False, f"Executable launch failed: {exe_path} - {str(e)}"
    
    def test_dependencies(self, exe_path: Path) -> Tuple[bool, str]:
        """Test if all dependencies are included"""
        try:
            if self.platform == "windows":
                # Use dumpbin or similar to check dependencies
                return True, "Dependency check skipped on Windows"
            elif self.platform == "macos":
                # Use otool to check dependencies
                result = subprocess.run(
                    ["otool", "-L", str(exe_path)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                # Check for system libraries only
                if "@rpath" in result.stdout or "@executable_path" in result.stdout:
                    return True, "Dependencies properly bundled"
                else:
                    return False, "Missing bundled dependencies"
            else:
                # Use ldd to check dependencies
                result = subprocess.run(
                    ["ldd", str(exe_path)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if "not found" in result.stdout:
                    return False, f"Missing dependencies: {result.stdout}"
                else:
                    return True, "All dependencies found"
                    
        except Exception as e:
            return False, f"Dependency check failed: {str(e)}"
    
    def test_file_size(self, exe_path: Path) -> Tuple[bool, str]:
        """Test if executable size is reasonable"""
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        
        # Reasonable size limits
        if size_mb < 1:
            return False, f"Executable too small ({size_mb:.2f} MB): {exe_path}"
        elif size_mb > 500:
            return False, f"Executable too large ({size_mb:.2f} MB): {exe_path}"
        else:
            return True, f"Executable size OK ({size_mb:.2f} MB): {exe_path}"
    
    def test_version_info(self, exe_path: Path) -> Tuple[bool, str]:
        """Test if version information is present"""
        version_file = exe_path.parent / "version.json"
        
        if version_file.exists():
            try:
                with open(version_file) as f:
                    version_data = json.load(f)
                
                if version_data.get("version") == self.version:
                    return True, f"Version info correct: {self.version}"
                else:
                    return False, f"Version mismatch: expected {self.version}, got {version_data.get('version')}"
            except Exception as e:
                return False, f"Version file invalid: {str(e)}"
        else:
            return False, f"Version file not found: {version_file}"
    
    def run_test_suite(self, exe_path: Path) -> Dict:
        """Run complete test suite on executable"""
        print(f"\nTesting: {exe_path.name}")
        print("=" * 60)
        
        results = {
            "executable": str(exe_path),
            "platform": self.platform,
            "tests": []
        }
        
        # Run all tests
        tests = [
            ("Existence", self.test_executable_exists),
            ("Permissions", self.test_executable_permissions),
            ("Launch", self.test_executable_launch),
            ("Dependencies", self.test_dependencies),
            ("File Size", self.test_file_size),
            ("Version Info", self.test_version_info)
        ]
        
        for test_name, test_func in tests:
            try:
                passed, message = test_func(exe_path)
                
                results["tests"].append({
                    "name": test_name,
                    "passed": passed,
                    "message": message
                })
                
                status = "✓" if passed else "✗"
                print(f"{status} {test_name}: {message}")
                
            except Exception as e:
                results["tests"].append({
                    "name": test_name,
                    "passed": False,
                    "message": f"Test error: {str(e)}"
                })
                print(f"✗ {test_name}: Test error: {str(e)}")
        
        # Calculate pass rate
        passed_tests = sum(1 for test in results["tests"] if test["passed"])
        total_tests = len(results["tests"])
        results["pass_rate"] = (passed_tests / total_tests) * 100
        
        print(f"\nPass Rate: {results['pass_rate']:.1f}% ({passed_tests}/{total_tests})")
        
        return results
    
    def generate_report(self):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        total_executables = len(self.test_results)
        total_tests = sum(len(r["tests"]) for r in self.test_results)
        passed_tests = sum(
            sum(1 for test in r["tests"] if test["passed"])
            for r in self.test_results
        )
        
        overall_pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Platform: {self.platform}")
        print(f"Version: {self.version}")
        print(f"Executables Tested: {total_executables}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed Tests: {passed_tests}")
        print(f"Failed Tests: {total_tests - passed_tests}")
        print(f"Overall Pass Rate: {overall_pass_rate:.1f}%")
        
        # Save report
        report_file = Path("test-results") / f"{self.platform}-test-report.json"
        report_file.parent.mkdir(exist_ok=True)
        
        with open(report_file, 'w') as f:
            json.dump({
                "platform": self.platform,
                "version": self.version,
                "summary": {
                    "executables_tested": total_executables,
                    "total_tests": total_tests,
                    "passed_tests": passed_tests,
                    "failed_tests": total_tests - passed_tests,
                    "pass_rate": overall_pass_rate
                },
                "results": self.test_results
            }, f, indent=2)
        
        print(f"\nReport saved to: {report_file}")
        
        return overall_pass_rate >= 80  # 80% pass rate required
    
    def run(self):
        """Run all tests"""
        print("=" * 60)
        print(f"EXECUTABLE TESTING - {self.platform.upper()}")
        print(f"Version: {self.version}")
        print("=" * 60)
        
        executables = self.discover_executables()
        
        if not executables:
            print(f"No executables found in {self.dist_dir}")
            return False
        
        print(f"\nFound {len(executables)} executable(s) to test")
        
        for exe_path in executables:
            result = self.run_test_suite(exe_path)
            self.test_results.append(result)
        
        return self.generate_report()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python test_executables.py <platform> <version>")
        sys.exit(1)
    
    platform = sys.argv[1]
    version = sys.argv[2]
    
    tester = ExecutableTester(platform, version)
    success = tester.run()
    
    sys.exit(0 if success else 1)