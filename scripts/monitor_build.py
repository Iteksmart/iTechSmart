#!/usr/bin/env python3
"""
GitHub Actions Build Monitor
Monitors build status and provides real-time updates
"""

import subprocess
import json
import time
import sys
from datetime import datetime
from typing import Dict, List, Optional


class BuildMonitor:
    """Monitor GitHub Actions builds"""

    def __init__(self, run_id: Optional[str] = None):
        self.run_id = run_id
        self.last_status = None

    def get_latest_run(self) -> Optional[str]:
        """Get the latest workflow run ID"""
        try:
            result = subprocess.run(
                ["gh", "run", "list", "--limit", "1", "--json", "databaseId"],
                capture_output=True,
                text=True,
                check=True,
            )

            data = json.loads(result.stdout)
            if data and len(data) > 0:
                return str(data[0]["databaseId"])
            return None

        except Exception as e:
            print(f"Error getting latest run: {e}")
            return None

    def get_run_status(self, run_id: str) -> Dict:
        """Get detailed status of a workflow run"""
        try:
            result = subprocess.run(
                [
                    "gh",
                    "run",
                    "view",
                    run_id,
                    "--json",
                    "status,conclusion,name,createdAt,updatedAt,jobs",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            return json.loads(result.stdout)

        except Exception as e:
            print(f"Error getting run status: {e}")
            return {}

    def count_job_status(self, jobs: List[Dict]) -> Dict[str, int]:
        """Count jobs by status"""
        counts = {
            "completed": 0,
            "in_progress": 0,
            "queued": 0,
            "failed": 0,
            "success": 0,
            "total": len(jobs),
        }

        for job in jobs:
            status = job.get("status", "")
            conclusion = job.get("conclusion", "")

            if status == "completed":
                counts["completed"] += 1
                if conclusion == "success":
                    counts["success"] += 1
                elif conclusion == "failure":
                    counts["failed"] += 1
            elif status == "in_progress":
                counts["in_progress"] += 1
            elif status == "queued":
                counts["queued"] += 1

        return counts

    def print_status(self, status_data: Dict):
        """Print formatted status"""
        print("\n" + "=" * 70)
        print(f"Build Monitor - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        print(f"\n📋 Workflow: {status_data.get('name', 'Unknown')}")
        print(f"🔄 Status: {status_data.get('status', 'Unknown').upper()}")

        if status_data.get("conclusion"):
            conclusion = status_data["conclusion"]
            emoji = "✅" if conclusion == "success" else "❌"
            print(f"{emoji} Conclusion: {conclusion.upper()}")

        print(f"⏰ Started: {status_data.get('createdAt', 'Unknown')}")
        print(f"🔄 Updated: {status_data.get('updatedAt', 'Unknown')}")

        # Job statistics
        jobs = status_data.get("jobs", [])
        if jobs:
            counts = self.count_job_status(jobs)

            print(f"\n📊 Job Statistics:")
            print(f"   Total Jobs: {counts['total']}")
            print(f"   ✅ Completed: {counts['completed']}")
            print(f"   🎉 Success: {counts['success']}")
            print(f"   ❌ Failed: {counts['failed']}")
            print(f"   🔄 In Progress: {counts['in_progress']}")
            print(f"   ⏳ Queued: {counts['queued']}")

            # Progress bar
            if counts["total"] > 0:
                progress = (counts["completed"] / counts["total"]) * 100
                bar_length = 50
                filled = int(bar_length * progress / 100)
                bar = "█" * filled + "░" * (bar_length - filled)
                print(f"\n   Progress: [{bar}] {progress:.1f}%")

        print("\n" + "=" * 70)

    def print_failed_jobs(self, jobs: List[Dict]):
        """Print details of failed jobs"""
        failed_jobs = [j for j in jobs if j.get("conclusion") == "failure"]

        if failed_jobs:
            print("\n❌ Failed Jobs:")
            for job in failed_jobs:
                print(f"   - {job.get('name', 'Unknown')}")

    def monitor(self, interval: int = 30, max_iterations: int = 0):
        """
        Monitor build status continuously

        Args:
            interval: Seconds between checks
            max_iterations: Maximum number of checks (0 = infinite)
        """
        if not self.run_id:
            self.run_id = self.get_latest_run()
            if not self.run_id:
                print("❌ No workflow runs found")
                return

        print(f"🔍 Monitoring workflow run: {self.run_id}")
        print(f"⏱️  Checking every {interval} seconds")
        print(f"Press Ctrl+C to stop\n")

        iteration = 0
        try:
            while True:
                status_data = self.get_run_status(self.run_id)

                if status_data:
                    self.print_status(status_data)

                    # Check if build is complete
                    if status_data.get("status") == "completed":
                        conclusion = status_data.get("conclusion", "")

                        if conclusion == "success":
                            print("\n🎉 BUILD SUCCESSFUL! 🎉")
                        elif conclusion == "failure":
                            print("\n❌ BUILD FAILED")
                            self.print_failed_jobs(status_data.get("jobs", []))
                        else:
                            print(f"\n⚠️  Build completed with status: {conclusion}")

                        print(
                            f"\n🔗 View details: https://github.com/Iteksmart/iTechSmart/actions/runs/{self.run_id}"
                        )
                        break

                iteration += 1
                if max_iterations > 0 and iteration >= max_iterations:
                    print(f"\n⏱️  Reached maximum iterations ({max_iterations})")
                    break

                # Wait before next check
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n⏹️  Monitoring stopped by user")
            print(
                f"🔗 View details: https://github.com/Iteksmart/iTechSmart/actions/runs/{self.run_id}"
            )

    def check_once(self):
        """Check status once and exit"""
        if not self.run_id:
            self.run_id = self.get_latest_run()
            if not self.run_id:
                print("❌ No workflow runs found")
                return

        status_data = self.get_run_status(self.run_id)
        if status_data:
            self.print_status(status_data)

            if status_data.get("status") == "completed":
                conclusion = status_data.get("conclusion", "")
                if conclusion == "success":
                    print("\n🎉 BUILD SUCCESSFUL! 🎉")
                elif conclusion == "failure":
                    print("\n❌ BUILD FAILED")
                    self.print_failed_jobs(status_data.get("jobs", []))

            print(
                f"\n🔗 View details: https://github.com/Iteksmart/iTechSmart/actions/runs/{self.run_id}"
            )


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Monitor GitHub Actions builds")
    parser.add_argument("--run-id", help="Specific run ID to monitor")
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Check interval in seconds (default: 30)",
    )
    parser.add_argument(
        "--max-checks",
        type=int,
        default=0,
        help="Maximum number of checks (0 = infinite)",
    )
    parser.add_argument("--once", action="store_true", help="Check once and exit")

    args = parser.parse_args()

    monitor = BuildMonitor(run_id=args.run_id)

    if args.once:
        monitor.check_once()
    else:
        monitor.monitor(interval=args.interval, max_iterations=args.max_checks)


if __name__ == "__main__":
    main()
