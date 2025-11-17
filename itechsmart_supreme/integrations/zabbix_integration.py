"""
Zabbix Integration - Enterprise-Level Monitoring Solution
Monitor infrastructure and collect metrics from Zabbix
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable
import aiohttp
import json
from datetime import datetime

from ..core.models import Alert, AlertSource, SeverityLevel


class ZabbixIntegration:
    """Integration with Zabbix for enterprise monitoring"""

    def __init__(
        self, url: str, username: str, password: str, alert_callback: Callable
    ):
        self.url = url.rstrip("/")
        self.username = username
        self.password = password
        self.alert_callback = alert_callback
        self.auth_token = None
        self.logger = logging.getLogger(__name__)
        self.running = False

    async def authenticate(self) -> bool:
        """Authenticate with Zabbix API"""

        payload = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {"user": self.username, "password": self.password},
            "id": 1,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.url}/api_jsonrpc.php", json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.auth_token = data.get("result")
                        self.logger.info("Authenticated with Zabbix")
                        return True
                    else:
                        self.logger.error(
                            f"Zabbix authentication failed: {response.status}"
                        )
                        return False

        except Exception as e:
            self.logger.error(f"Zabbix authentication error: {e}")
            return False

    async def api_call(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make Zabbix API call"""

        if not self.auth_token:
            await self.authenticate()

        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "auth": self.auth_token,
            "id": 1,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.url}/api_jsonrpc.php", json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("result", {})
                    else:
                        self.logger.error(f"Zabbix API call failed: {response.status}")
                        return {}

        except Exception as e:
            self.logger.error(f"Zabbix API error: {e}")
            return {}

    async def start(self):
        """Start monitoring Zabbix triggers"""
        self.running = True
        self.logger.info("Starting Zabbix monitoring...")

        await self.authenticate()

        tasks = [self.monitor_triggers(), self.monitor_problems()]

        await asyncio.gather(*tasks)

    async def stop(self):
        """Stop monitoring"""
        self.running = False
        self.logger.info("Stopping Zabbix monitoring...")

    async def monitor_triggers(self):
        """Monitor Zabbix triggers"""

        while self.running:
            try:
                triggers = await self.get_triggers(only_true=True, min_severity=2)

                for trigger in triggers:
                    await self.process_trigger(trigger)

                await asyncio.sleep(30)

            except Exception as e:
                self.logger.error(f"Trigger monitoring error: {e}")
                await asyncio.sleep(60)

    async def monitor_problems(self):
        """Monitor Zabbix problems"""

        while self.running:
            try:
                problems = await self.get_problems(recent=True)

                for problem in problems:
                    await self.process_problem(problem)

                await asyncio.sleep(30)

            except Exception as e:
                self.logger.error(f"Problem monitoring error: {e}")
                await asyncio.sleep(60)

    async def get_triggers(
        self, only_true: bool = False, min_severity: int = 0
    ) -> List[Dict[str, Any]]:
        """Get Zabbix triggers"""

        params = {
            "output": "extend",
            "selectHosts": ["host", "name"],
            "selectItems": ["key_", "lastvalue"],
            "monitored": True,
            "active": True,
        }

        if only_true:
            params["filter"] = {"value": 1}

        if min_severity > 0:
            params["min_severity"] = min_severity

        return await self.api_call("trigger.get", params)

    async def get_problems(self, recent: bool = False) -> List[Dict[str, Any]]:
        """Get Zabbix problems"""

        params = {
            "output": "extend",
            "selectHosts": ["host", "name"],
            "selectTags": "extend",
            "recent": recent,
            "sortfield": ["eventid"],
            "sortorder": "DESC",
        }

        return await self.api_call("problem.get", params)

    async def get_hosts(self) -> List[Dict[str, Any]]:
        """Get Zabbix hosts"""

        params = {
            "output": ["hostid", "host", "name", "status"],
            "selectInterfaces": ["ip", "port"],
        }

        return await self.api_call("host.get", params)

    async def get_items(self, hostid: str) -> List[Dict[str, Any]]:
        """Get items for a host"""

        params = {"output": "extend", "hostids": hostid, "monitored": True}

        return await self.api_call("item.get", params)

    async def get_history(
        self, itemid: str, history_type: int = 0, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get item history"""

        params = {
            "output": "extend",
            "history": history_type,
            "itemids": itemid,
            "sortfield": "clock",
            "sortorder": "DESC",
            "limit": limit,
        }

        return await self.api_call("history.get", params)

    async def process_trigger(self, trigger: Dict[str, Any]):
        """Process Zabbix trigger and create alert"""

        severity_map = {
            0: SeverityLevel.LOW,
            1: SeverityLevel.LOW,
            2: SeverityLevel.MEDIUM,
            3: SeverityLevel.MEDIUM,
            4: SeverityLevel.HIGH,
            5: SeverityLevel.CRITICAL,
        }

        severity = severity_map.get(
            int(trigger.get("priority", 0)), SeverityLevel.MEDIUM
        )

        hosts = trigger.get("hosts", [])
        host = hosts[0].get("host", "unknown") if hosts else "unknown"

        alert = Alert(
            source=AlertSource.CUSTOM,
            severity=severity,
            message=trigger.get("description", "Zabbix trigger"),
            host=host,
            metrics={
                "trigger_id": trigger.get("triggerid"),
                "priority": trigger.get("priority"),
                "value": trigger.get("value"),
                "metric_type": "zabbix_trigger",
            },
            raw_data=trigger,
            tags=["zabbix", "trigger"],
        )

        await self.alert_callback(alert)

    async def process_problem(self, problem: Dict[str, Any]):
        """Process Zabbix problem and create alert"""

        severity_map = {
            0: SeverityLevel.LOW,
            1: SeverityLevel.LOW,
            2: SeverityLevel.MEDIUM,
            3: SeverityLevel.MEDIUM,
            4: SeverityLevel.HIGH,
            5: SeverityLevel.CRITICAL,
        }

        severity = severity_map.get(
            int(problem.get("severity", 0)), SeverityLevel.MEDIUM
        )

        hosts = problem.get("hosts", [])
        host = hosts[0].get("host", "unknown") if hosts else "unknown"

        alert = Alert(
            source=AlertSource.CUSTOM,
            severity=severity,
            message=problem.get("name", "Zabbix problem"),
            host=host,
            metrics={
                "eventid": problem.get("eventid"),
                "severity": problem.get("severity"),
                "acknowledged": problem.get("acknowledged"),
                "metric_type": "zabbix_problem",
            },
            raw_data=problem,
            tags=["zabbix", "problem"],
        )

        await self.alert_callback(alert)

    async def acknowledge_problem(self, eventid: str, message: str) -> bool:
        """Acknowledge a Zabbix problem"""

        params = {"eventids": eventid, "action": 6, "message": message}

        result = await self.api_call("event.acknowledge", params)
        return bool(result)
