"""
Integration Testing Utilities
Tools for testing EMR integrations and HL7 message handling
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class IntegrationTester:
    """
    Test EMR integrations and validate functionality
    """

    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
        self.test_results = []

    async def test_all_connections(self) -> Dict[str, Any]:
        """
        Test all configured EMR connections
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_connections": 0,
            "successful": 0,
            "failed": 0,
            "connection_results": [],
        }

        connections = self.connection_manager.list_connections()
        results["total_connections"] = len(connections)

        for connection in connections:
            connection_id = connection["id"]
            test_result = await self.test_connection(connection_id)
            results["connection_results"].append(test_result)

            if test_result["success"]:
                results["successful"] += 1
            else:
                results["failed"] += 1

        return results

    async def test_connection(self, connection_id: str) -> Dict[str, Any]:
        """
        Test a specific EMR connection
        """
        result = {
            "connection_id": connection_id,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "tests": {},
            "errors": [],
        }

        try:
            # Test authentication
            auth_result = await self.connection_manager.test_connection(connection_id)
            result["tests"]["authentication"] = auth_result

            if not auth_result:
                result["errors"].append("Authentication failed")
                return result

            # Test patient search
            search_result = await self._test_patient_search(connection_id)
            result["tests"]["patient_search"] = search_result["success"]
            if not search_result["success"]:
                result["errors"].append(
                    f"Patient search failed: {search_result.get('error')}"
                )

            # Test patient retrieval
            if search_result["success"] and search_result.get("patient_id"):
                patient_result = await self._test_patient_retrieval(
                    connection_id, search_result["patient_id"]
                )
                result["tests"]["patient_retrieval"] = patient_result["success"]
                if not patient_result["success"]:
                    result["errors"].append(
                        f"Patient retrieval failed: {patient_result.get('error')}"
                    )

            # Overall success
            result["success"] = all(result["tests"].values())

        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"Connection test failed for {connection_id}: {e}")

        return result

    async def _test_patient_search(self, connection_id: str) -> Dict[str, Any]:
        """
        Test patient search functionality
        """
        try:
            # Search for test patient
            patients = await self.connection_manager.search_patients(
                connection_id, {"name": "Test"}
            )

            return {
                "success": True,
                "patient_count": len(patients),
                "patient_id": patients[0]["id"] if patients else None,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _test_patient_retrieval(
        self, connection_id: str, patient_id: str
    ) -> Dict[str, Any]:
        """
        Test patient data retrieval
        """
        try:
            patient = await self.connection_manager.get_patient(
                connection_id, patient_id
            )

            return {
                "success": patient is not None,
                "has_demographics": bool(patient.get("name")) if patient else False,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    async def test_data_aggregation(
        self, patient_identifiers: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Test patient data aggregation from multiple sources
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "sources_tested": len(patient_identifiers),
            "data_retrieved": {},
            "errors": [],
        }

        try:
            aggregated_data = await self.connection_manager.aggregate_patient_data(
                patient_identifiers
            )

            result["data_retrieved"] = {
                "demographics": aggregated_data["demographics"] is not None,
                "observations_count": len(aggregated_data["observations"]),
                "medications_count": len(aggregated_data["medications"]),
                "allergies_count": len(aggregated_data["allergies"]),
                "conditions_count": len(aggregated_data["conditions"]),
                "encounters_count": len(aggregated_data["encounters"]),
                "sources": aggregated_data["sources"],
            }

            result["success"] = aggregated_data["demographics"] is not None

        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"Data aggregation test failed: {e}")

        return result

    def generate_test_report(self) -> str:
        """
        Generate a comprehensive test report
        """
        report = []
        report.append("=" * 80)
        report.append("iTechSmart HL7 Integration Test Report")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")

        if not self.test_results:
            report.append("No test results available.")
            return "\n".join(report)

        for result in self.test_results:
            report.append(f"\nConnection: {result['connection_id']}")
            report.append(f"Status: {'PASSED' if result['success'] else 'FAILED'}")
            report.append(f"Timestamp: {result['timestamp']}")

            if result["tests"]:
                report.append("\nTests:")
                for test_name, test_result in result["tests"].items():
                    status = "✓" if test_result else "✗"
                    report.append(f"  {status} {test_name}")

            if result["errors"]:
                report.append("\nErrors:")
                for error in result["errors"]:
                    report.append(f"  - {error}")

            report.append("-" * 80)

        return "\n".join(report)


class HL7MessageValidator:
    """
    Validate HL7 v2.x messages
    """

    @staticmethod
    def validate_message(message: str) -> Dict[str, Any]:
        """
        Validate HL7 message structure and content
        """
        result = {
            "valid": False,
            "errors": [],
            "warnings": [],
            "message_type": None,
            "segments": [],
        }

        try:
            # Split into segments
            segments = message.split("\r")
            result["segments"] = [seg.split("|")[0] for seg in segments if seg]

            if not segments:
                result["errors"].append("Empty message")
                return result

            # Validate MSH segment
            msh = segments[0]
            if not msh.startswith("MSH"):
                result["errors"].append("Message must start with MSH segment")
                return result

            msh_fields = msh.split("|")
            if len(msh_fields) < 12:
                result["errors"].append("MSH segment has insufficient fields")
                return result

            # Extract message type
            if len(msh_fields) > 8:
                result["message_type"] = msh_fields[8]

            # Validate required segments based on message type
            message_type = result["message_type"]
            if message_type:
                if message_type.startswith("ADT"):
                    if "PID" not in result["segments"]:
                        result["errors"].append("ADT message missing PID segment")
                elif message_type.startswith("ORU"):
                    if "OBR" not in result["segments"]:
                        result["errors"].append("ORU message missing OBR segment")
                elif message_type.startswith("ORM"):
                    if "ORC" not in result["segments"]:
                        result["errors"].append("ORM message missing ORC segment")

            # Check for common issues
            for i, segment in enumerate(segments):
                if not segment.strip():
                    result["warnings"].append(f"Empty segment at position {i}")

                fields = segment.split("|")
                if len(fields) < 2:
                    result["warnings"].append(
                        f"Segment {segment[:3]} has too few fields"
                    )

            # If no errors, mark as valid
            result["valid"] = len(result["errors"]) == 0

        except Exception as e:
            result["errors"].append(f"Validation error: {str(e)}")

        return result

    @staticmethod
    def validate_patient_demographics(pid_segment: str) -> Dict[str, Any]:
        """
        Validate PID segment for patient demographics
        """
        result = {"valid": False, "errors": [], "warnings": [], "fields": {}}

        try:
            fields = pid_segment.split("|")

            if not pid_segment.startswith("PID"):
                result["errors"].append("Not a PID segment")
                return result

            # Check required fields
            if len(fields) < 6:
                result["errors"].append("PID segment missing required fields")
                return result

            # Extract and validate fields
            result["fields"]["patient_id"] = fields[3] if len(fields) > 3 else None
            result["fields"]["patient_name"] = fields[5] if len(fields) > 5 else None
            result["fields"]["dob"] = fields[7] if len(fields) > 7 else None
            result["fields"]["gender"] = fields[8] if len(fields) > 8 else None

            # Validate patient ID
            if not result["fields"]["patient_id"]:
                result["errors"].append("Missing patient ID")

            # Validate patient name
            if not result["fields"]["patient_name"]:
                result["warnings"].append("Missing patient name")

            # Validate DOB format (YYYYMMDD)
            dob = result["fields"]["dob"]
            if dob and len(dob) != 8:
                result["warnings"].append(
                    "DOB format may be incorrect (expected YYYYMMDD)"
                )

            # Validate gender
            gender = result["fields"]["gender"]
            if gender and gender not in ["M", "F", "O", "U"]:
                result["warnings"].append(f"Unusual gender value: {gender}")

            result["valid"] = len(result["errors"]) == 0

        except Exception as e:
            result["errors"].append(f"Validation error: {str(e)}")

        return result


class MockEMRServer:
    """
    Mock EMR server for testing
    """

    def __init__(self, port: int = 2575):
        self.port = port
        self.server = None
        self.received_messages = []

    async def start(self):
        """
        Start mock HL7 server
        """

        async def handle_client(reader, writer):
            try:
                data = await reader.read(4096)
                message = data.decode("utf-8").strip("\x0b\x1c\x0d")

                self.received_messages.append(
                    {"timestamp": datetime.now().isoformat(), "message": message}
                )

                logger.info(f"Mock server received message: {message[:100]}...")

                # Send ACK
                ack = self._build_ack(message)
                ack_data = f"\x0b{ack}\x1c\x0d".encode("utf-8")

                writer.write(ack_data)
                await writer.drain()

            except Exception as e:
                logger.error(f"Mock server error: {e}")
            finally:
                writer.close()
                await writer.wait_closed()

        self.server = await asyncio.start_server(handle_client, "0.0.0.0", self.port)
        logger.info(f"Mock EMR server started on port {self.port}")

    def _build_ack(self, message: str) -> str:
        """
        Build ACK message
        """
        lines = message.split("\r")
        msh = lines[0]
        fields = msh.split("|")

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        message_control_id = fields[9] if len(fields) > 9 else timestamp

        ack_msh = f"MSH|^~\\&|MockEMR|MockFacility|{fields[2]}|{fields[3]}|{timestamp}||ACK|{message_control_id}|P|2.5"
        msa = f"MSA|AA|{message_control_id}"

        return f"{ack_msh}\r{msa}"

    async def stop(self):
        """
        Stop mock server
        """
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("Mock EMR server stopped")

    def get_received_messages(self) -> List[Dict]:
        """
        Get all received messages
        """
        return self.received_messages

    def clear_messages(self):
        """
        Clear received messages
        """
        self.received_messages = []


class PerformanceTester:
    """
    Test performance of EMR integrations
    """

    def __init__(self, connection_manager):
        self.connection_manager = connection_manager

    async def test_throughput(
        self, connection_id: str, num_requests: int = 100
    ) -> Dict[str, Any]:
        """
        Test throughput of EMR connection
        """
        result = {
            "connection_id": connection_id,
            "num_requests": num_requests,
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_seconds": 0,
            "requests_per_second": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "errors": [],
        }

        start_time = datetime.now()

        try:
            # Create test tasks
            tasks = []
            for i in range(num_requests):
                task = self._make_test_request(connection_id)
                tasks.append(task)

            # Execute all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Count successes and failures
            for res in results:
                if isinstance(res, Exception):
                    result["failed_requests"] += 1
                    result["errors"].append(str(res))
                elif res:
                    result["successful_requests"] += 1
                else:
                    result["failed_requests"] += 1

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            result["end_time"] = end_time.isoformat()
            result["duration_seconds"] = duration
            result["requests_per_second"] = (
                num_requests / duration if duration > 0 else 0
            )

        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"Throughput test failed: {e}")

        return result

    async def _make_test_request(self, connection_id: str) -> bool:
        """
        Make a test request to EMR
        """
        try:
            # Test with patient search
            patients = await self.connection_manager.search_patients(
                connection_id, {"name": "Test"}
            )
            return True
        except Exception:
            return False

    async def test_latency(
        self, connection_id: str, num_samples: int = 10
    ) -> Dict[str, Any]:
        """
        Test latency of EMR connection
        """
        result = {
            "connection_id": connection_id,
            "num_samples": num_samples,
            "latencies_ms": [],
            "min_latency_ms": 0,
            "max_latency_ms": 0,
            "avg_latency_ms": 0,
            "median_latency_ms": 0,
        }

        try:
            for i in range(num_samples):
                start_time = datetime.now()

                await self._make_test_request(connection_id)

                end_time = datetime.now()
                latency_ms = (end_time - start_time).total_seconds() * 1000
                result["latencies_ms"].append(latency_ms)

            # Calculate statistics
            if result["latencies_ms"]:
                result["min_latency_ms"] = min(result["latencies_ms"])
                result["max_latency_ms"] = max(result["latencies_ms"])
                result["avg_latency_ms"] = sum(result["latencies_ms"]) / len(
                    result["latencies_ms"]
                )

                sorted_latencies = sorted(result["latencies_ms"])
                mid = len(sorted_latencies) // 2
                result["median_latency_ms"] = sorted_latencies[mid]

        except Exception as e:
            logger.error(f"Latency test failed: {e}")

        return result
