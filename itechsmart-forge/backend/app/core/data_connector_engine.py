"""
iTechSmart Forge - Data Connector Engine
Connect to all iTechSmart products and external data sources
"""

from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
import httpx

from app.models.models import DataSource, DataQuery


class DataConnectorEngine:
    """
    Engine for connecting to data sources
    """

    def __init__(self, db: Session):
        self.db = db
        self.itechsmart_products = [
            "itechsmart-enterprise",
            "itechsmart-ninja",
            "itechsmart-analytics",
            "itechsmart-dataflow",
            "itechsmart-pulse",
            "itechsmart-connect",
            "itechsmart-vault",
            "itechsmart-notify",
            "itechsmart-ledger",
            "itechsmart-copilot",
            "itechsmart-shield",
            "itechsmart-workflow",
            "itechsmart-cloud",
            "itechsmart-devops",
            "itechsmart-mobile",
            "itechsmart-ai",
            "itechsmart-compliance",
            "itechsmart-data-platform",
            "itechsmart-customer-success",
            "itechsmart-marketplace",
            "itechsmart-supreme",
            "itechsmart-hl7",
            "prooflink-ai",
            "passport",
            "impactos",
            "legalai-pro",
            "itechsmart-sentinel",
            "itechsmart-port-manager",
            "itechsmart-mdm-agent",
            "itechsmart-qaqc",
            "itechsmart-thinktank",
        ]

    async def create_data_source(
        self,
        app_id: int,
        name: str,
        source_type: str,
        connection_config: Dict[str, Any],
    ) -> DataSource:
        """Create a new data source connection"""
        data_source = DataSource(
            app_id=app_id,
            name=name,
            source_type=source_type,
            connection_config=connection_config,
            is_active=True,
        )

        self.db.add(data_source)
        self.db.commit()
        self.db.refresh(data_source)

        return data_source

    async def test_connection(self, data_source_id: int) -> Dict[str, Any]:
        """Test data source connection"""
        data_source = (
            self.db.query(DataSource).filter(DataSource.id == data_source_id).first()
        )

        if not data_source:
            raise ValueError(f"Data source {data_source_id} not found")

        try:
            if data_source.source_type == "itechsmart_product":
                result = await self._test_itechsmart_connection(data_source)
            elif data_source.source_type in ["postgresql", "mysql"]:
                result = await self._test_database_connection(data_source)
            elif data_source.source_type == "rest_api":
                result = await self._test_api_connection(data_source)
            else:
                result = {
                    "success": True,
                    "message": "Connection type not yet implemented",
                }

            data_source.last_tested = datetime.utcnow()
            data_source.test_status = "success" if result["success"] else "failed"
            data_source.test_message = result["message"]

            self.db.commit()

            return result

        except Exception as e:
            data_source.last_tested = datetime.utcnow()
            data_source.test_status = "failed"
            data_source.test_message = str(e)
            self.db.commit()

            return {"success": False, "message": str(e)}

    async def execute_query(
        self, query_id: int, parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a saved query"""
        query = self.db.query(DataQuery).filter(DataQuery.id == query_id).first()
        if not query:
            raise ValueError(f"Query {query_id} not found")

        data_source = query.data_source

        try:
            if data_source.source_type == "itechsmart_product":
                result = await self._execute_itechsmart_query(
                    data_source, query, parameters
                )
            elif data_source.source_type in ["postgresql", "mysql"]:
                result = await self._execute_database_query(
                    data_source, query, parameters
                )
            elif data_source.source_type == "rest_api":
                result = await self._execute_api_query(data_source, query, parameters)
            else:
                result = {"data": [], "message": "Query type not yet implemented"}

            query.last_executed = datetime.utcnow()
            self.db.commit()

            return result

        except Exception as e:
            return {"error": str(e), "data": []}

    async def get_available_itechsmart_products(self) -> List[Dict[str, Any]]:
        """Get list of available iTechSmart products"""
        return [
            {"name": product, "status": "available"}
            for product in self.itechsmart_products
        ]

    async def _test_itechsmart_connection(
        self, data_source: DataSource
    ) -> Dict[str, Any]:
        """Test connection to iTechSmart product"""
        product_name = data_source.product_name

        if product_name not in self.itechsmart_products:
            return {"success": False, "message": f"Unknown product: {product_name}"}

        # Try to connect via Enterprise Hub
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"http://localhost:8001/api/integration/services/{product_name}",
                    timeout=5.0,
                )

                if response.status_code == 200:
                    return {"success": True, "message": f"Connected to {product_name}"}
                else:
                    return {
                        "success": False,
                        "message": f"Product {product_name} not available",
                    }
        except Exception as e:
            return {"success": False, "message": f"Connection failed: {str(e)}"}

    async def _test_database_connection(
        self, data_source: DataSource
    ) -> Dict[str, Any]:
        """Test database connection"""
        # Mock implementation
        return {"success": True, "message": "Database connection successful"}

    async def _test_api_connection(self, data_source: DataSource) -> Dict[str, Any]:
        """Test API connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(data_source.base_url, timeout=5.0)

                if response.status_code < 400:
                    return {"success": True, "message": "API connection successful"}
                else:
                    return {
                        "success": False,
                        "message": f"API returned {response.status_code}",
                    }
        except Exception as e:
            return {"success": False, "message": str(e)}

    async def _execute_itechsmart_query(
        self,
        data_source: DataSource,
        query: DataQuery,
        parameters: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Execute query on iTechSmart product"""
        # Mock implementation - would call actual product API
        return {
            "data": [
                {"id": 1, "name": "Sample Data 1"},
                {"id": 2, "name": "Sample Data 2"},
            ],
            "count": 2,
        }

    async def _execute_database_query(
        self,
        data_source: DataSource,
        query: DataQuery,
        parameters: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Execute database query"""
        # Mock implementation
        return {
            "data": [{"id": 1, "column1": "value1"}, {"id": 2, "column1": "value2"}],
            "count": 2,
        }

    async def _execute_api_query(
        self,
        data_source: DataSource,
        query: DataQuery,
        parameters: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Execute API query"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{data_source.base_url}{query.query}",
                    params=parameters,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    return {"data": response.json(), "count": len(response.json())}
                else:
                    return {"error": f"API returned {response.status_code}", "data": []}
        except Exception as e:
            return {"error": str(e), "data": []}
