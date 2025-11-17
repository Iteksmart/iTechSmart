#!/usr/bin/env python3
"""
Comprehensive validation script for all iTechSmart projects.
Checks for essential files, structure, and completeness.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple


class ProjectValidator:
    def __init__(self):
        self.results = {}
        self.workspace = Path("/workspace")

    def validate_project(
        self, project_name: str, project_path: Path, project_type: str = "web"
    ) -> Dict:
        """Validate a single project."""
        result = {
            "name": project_name,
            "type": project_type,
            "exists": project_path.exists(),
            "checks": {},
            "score": 0,
            "max_score": 0,
            "status": "❌",
        }

        if not project_path.exists():
            return result

        # Common checks for all projects
        checks = {
            "README.md": (project_path / "README.md").exists(),
            "docker-compose.yml": (project_path / "docker-compose.yml").exists(),
            ".gitignore": (project_path / ".gitignore").exists(),
        }

        if project_type == "web":
            # Web application checks
            backend_path = project_path / "backend"
            frontend_path = project_path / "frontend"

            checks.update(
                {
                    "backend_exists": backend_path.exists(),
                    "frontend_exists": frontend_path.exists(),
                    "requirements.txt": (
                        (backend_path / "requirements.txt").exists()
                        if backend_path.exists()
                        else False
                    ),
                    "package.json": (
                        (frontend_path / "package.json").exists()
                        if frontend_path.exists()
                        else False
                    ),
                    "main.py": (
                        (backend_path / "app" / "main.py").exists()
                        if backend_path.exists()
                        else False
                    ),
                }
            )

            # Count API files
            if backend_path.exists():
                api_files = list(backend_path.rglob("**/api/**/*.py")) + list(
                    backend_path.rglob("**/routers/**/*.py")
                )
                checks["api_files_count"] = len(api_files)
                checks["has_api_files"] = len(api_files) > 0

            # Count frontend pages
            if frontend_path.exists():
                page_files = (
                    list(frontend_path.rglob("**/pages/**/*.tsx"))
                    + list(frontend_path.rglob("**/pages/**/*.jsx"))
                    + list(frontend_path.rglob("**/app/**/*.tsx"))
                )
                checks["frontend_pages_count"] = len(page_files)
                checks["has_frontend_pages"] = len(page_files) > 0

        elif project_type == "cli":
            # CLI tool checks
            checks.update(
                {
                    "main.py": (project_path / "main.py").exists(),
                    "requirements.txt": (project_path / "requirements.txt").exists(),
                    "setup.py": (project_path / "setup.py").exists(),
                }
            )

            # Count Python files
            py_files = list(project_path.rglob("*.py"))
            checks["python_files_count"] = len(py_files)
            checks["has_python_files"] = len(py_files) > 5

        # Calculate score
        result["checks"] = checks
        result["max_score"] = len([v for v in checks.values() if isinstance(v, bool)])
        result["score"] = sum([1 for v in checks.values() if v is True])

        # Determine status
        completion_rate = (
            (result["score"] / result["max_score"] * 100)
            if result["max_score"] > 0
            else 0
        )
        if completion_rate >= 90:
            result["status"] = "✅"
        elif completion_rate >= 70:
            result["status"] = "⚠️"
        else:
            result["status"] = "❌"

        result["completion_rate"] = round(completion_rate, 1)

        return result

    def validate_all(self) -> Dict:
        """Validate all projects."""
        projects = [
            ("ProofLink.AI", "prooflink", "web"),
            ("PassPort", "passport", "web"),
            ("ImpactOS", "itechsmart-impactos", "web"),
            ("iTechSmart Ninja", "itechsmart-ninja", "web"),
            ("iTechSmart Enterprise", "itechsmart-enterprise", "web"),
            ("iTechSmart HL7", "itechsmart-hl7", "web"),
            ("iTechSmart Supreme", "itechsmart_supreme", "cli"),
            ("FitSnap.AI", "fitsnap-ai", "web"),
        ]

        results = []
        for display_name, folder_name, project_type in projects:
            project_path = self.workspace / folder_name
            result = self.validate_project(display_name, project_path, project_type)
            results.append(result)

        return {
            "projects": results,
            "total_projects": len(results),
            "complete_projects": sum(1 for r in results if r["status"] == "✅"),
            "warning_projects": sum(1 for r in results if r["status"] == "⚠️"),
            "incomplete_projects": sum(1 for r in results if r["status"] == "❌"),
        }

    def print_report(self, results: Dict):
        """Print a formatted report."""
        print("=" * 80)
        print("iTechSmart Portfolio - Comprehensive Validation Report")
        print("=" * 80)
        print()

        print(f"Total Projects: {results['total_projects']}")
        print(f"✅ Complete: {results['complete_projects']}")
        print(f"⚠️  Warning: {results['warning_projects']}")
        print(f"❌ Incomplete: {results['incomplete_projects']}")
        print()
        print("=" * 80)
        print()

        for project in results["projects"]:
            print(f"{project['status']} {project['name']} ({project['type'].upper()})")
            print(
                f"   Completion: {project['completion_rate']}% ({project['score']}/{project['max_score']})"
            )

            if project["type"] == "web":
                if "api_files_count" in project["checks"]:
                    print(f"   API Files: {project['checks']['api_files_count']}")
                if "frontend_pages_count" in project["checks"]:
                    print(
                        f"   Frontend Pages: {project['checks']['frontend_pages_count']}"
                    )
            elif project["type"] == "cli":
                if "python_files_count" in project["checks"]:
                    print(f"   Python Files: {project['checks']['python_files_count']}")

            # Show failed checks
            failed_checks = [
                k for k, v in project["checks"].items() if isinstance(v, bool) and not v
            ]
            if failed_checks:
                print(f"   Missing: {', '.join(failed_checks)}")

            print()

        print("=" * 80)

        # Overall status
        if results["incomplete_projects"] == 0 and results["warning_projects"] == 0:
            print("🎉 ALL PROJECTS ARE COMPLETE AND READY FOR DEPLOYMENT!")
        elif results["incomplete_projects"] == 0:
            print("⚠️  All projects exist but some have minor issues.")
        else:
            print("❌ Some projects need attention.")

        print("=" * 80)


def main():
    validator = ProjectValidator()
    results = validator.validate_all()
    validator.print_report(results)

    # Save results to JSON
    output_file = Path("/workspace/validation_results.json")
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")


if __name__ == "__main__":
    main()
