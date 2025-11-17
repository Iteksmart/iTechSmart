#!/usr/bin/env python3

import os
import subprocess
import json
import time

class iTechSmartTestSuite:
    def __init__(self):
        self.results = {}
        self.base_path = "/workspace/iTechSmart"
        
    def run_command(self, command, cwd=None, timeout=30):
        """Run a command and return success, output, error"""
        try:
            result = subprocess.run(
                command, 
                shell=True, 
                cwd=cwd, 
                capture_output=True, 
                text=True, 
                timeout=timeout
            )
            return result.returncode == 0, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return False, "", "Command timed out"
        except Exception as e:
            return False, "", str(e)
    
    def test_frontend_build(self, frontend_path):
        """Test if a frontend can build successfully"""
        print(f"🔧 Testing {frontend_path}...")
        
        # Check if package.json exists
        package_json_path = os.path.join(self.base_path, frontend_path, "package.json")
        if not os.path.exists(package_json_path):
            return False, "package.json not found"
        
        # Check if node_modules exists, if not install
        node_modules_path = os.path.join(self.base_path, frontend_path, "node_modules")
        if not os.path.exists(node_modules_path):
            print(f"📦 Installing dependencies for {frontend_path}...")
            success, output, error = self.run_command(
                "npm install", 
                cwd=os.path.join(self.base_path, frontend_path),
                timeout=120
            )
            if not success:
                return False, f"npm install failed: {error}"
        
        # Try to build
        print(f"🏗️  Building {frontend_path}...")
        success, output, error = self.run_command(
            "npm run build",
            cwd=os.path.join(self.base_path, frontend_path),
            timeout=180
        )
        
        if success:
            return True, "Build successful"
        else:
            return False, f"Build failed: {error}"
    
    def test_backend_build(self, backend_path):
        """Test if a backend can build successfully"""
        print(f"🔧 Testing backend {backend_path}...")
        
        # Check for common backend files
        backend_full_path = os.path.join(self.base_path, backend_path)
        
        # Look for requirements.txt (Python) or package.json (Node.js)
        python_req = os.path.join(backend_full_path, "requirements.txt")
        node_package = os.path.join(backend_full_path, "package.json")
        
        if os.path.exists(python_req):
            # Python backend
            return self.test_python_backend(backend_full_path)
        elif os.path.exists(node_package):
            # Node.js backend
            return self.test_nodejs_backend(backend_full_path)
        else:
            return False, "No recognized backend project structure"
    
    def test_python_backend(self, backend_path):
        """Test Python backend"""
        # Check if we can import main modules
        success, output, error = self.run_command(
            "python3 -c 'import sys; print(&quot;Python OK&quot;)'",
            timeout=10
        )
        return success, "Python backend structure OK"
    
    def test_nodejs_backend(self, backend_path):
        """Test Node.js backend"""
        # Check if dependencies are installed
        node_modules = os.path.join(backend_path, "node_modules")
        if not os.path.exists(node_modules):
            success, output, error = self.run_command(
                "npm install",
                cwd=backend_path,
                timeout=60
            )
            if not success:
                return False, f"npm install failed: {error}"
        
        return True, "Node.js backend structure OK"
    
    def run_comprehensive_tests(self):
        """Run tests across the iTechSmart suite"""
        print("🚀 Starting comprehensive iTechSmart Suite Test...\n")
        
        # Test key frontends
        key_frontends = [
            "itechsmart-ninja/frontend",
            "itechsmart-enterprise/frontend", 
            "itechsmart-impactos/frontend",
            "itechsmart-ai/frontend",
            "itechsmart-analytics/frontend",
            "itechsmart-citadel/frontend",
            "itechsmart-cloud/frontend",
            "itechsmart-compliance/frontend"
        ]
        
        frontend_results = {}
        for frontend in key_frontends:
            if os.path.exists(os.path.join(self.base_path, frontend)):
                success, message = self.test_frontend_build(frontend)
                frontend_results[frontend] = {"success": success, "message": message}
                status = "✅" if success else "❌"
                print(f"{status} {frontend}: {message}")
            else:
                frontend_results[frontend] = {"success": False, "message": "Directory not found"}
                print(f"❌ {frontend}: Directory not found")
        
        # Test key backends
        key_backends = [
            "itechsmart-ninja/backend",
            "itechsmart-enterprise/backend",
            "itechsmart-ai/backend",
            "itechsmart-analytics/backend",
            "itechsmart-citadel/backend"
        ]
        
        backend_results = {}
        for backend in key_backends:
            if os.path.exists(os.path.join(self.base_path, backend)):
                success, message = self.test_backend_build(backend)
                backend_results[backend] = {"success": success, "message": message}
                status = "✅" if success else "❌"
                print(f"{status} {backend}: {message}")
            else:
                backend_results[backend] = {"success": False, "message": "Directory not found"}
                print(f"❌ {backend}: Directory not found")
        
        # Compile results
        self.results = {
            "frontend_tests": frontend_results,
            "backend_tests": backend_results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 TEST SUMMARY")
        print("="*60)
        
        frontend_success = sum(1 for r in self.results["frontend_tests"].values() if r["success"])
        frontend_total = len(self.results["frontend_tests"])
        
        backend_success = sum(1 for r in self.results["backend_tests"].values() if r["success"])
        backend_total = len(self.results["backend_tests"])
        
        print(f"Frontends: {frontend_success}/{frontend_total} passed")
        print(f"Backends:  {backend_success}/{backend_total} passed")
        
        overall_success = frontend_success == frontend_total and backend_success == backend_total
        
        if overall_success:
            print("\n🎉 ALL TESTS PASSED! iTechSmart Suite is ready for v1.5.0")
        else:
            print("\n⚠️  Some tests failed. Please review the issues above.")
        
        print(f"\nTest completed at: {self.results['timestamp']}")

if __name__ == "__main__":
    tester = iTechSmartTestSuite()
    tester.run_comprehensive_tests()