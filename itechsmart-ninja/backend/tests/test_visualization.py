"""
Tests for Data Visualization Feature
"""
import pytest
from app.integrations.data_visualization import DataVisualizationClient


@pytest.fixture
def viz_client():
    """Create visualization client fixture"""
    return DataVisualizationClient()


@pytest.mark.asyncio
async def test_create_bar_chart(viz_client):
    """Test creating a bar chart"""
    data = {
        "labels": ["A", "B", "C"],
        "datasets": [{
            "label": "Test Data",
            "data": [10, 20, 30]
        }]
    }
    
    result = await viz_client.create_chart(
        chart_type="bar",
        data=data,
        options={"title": "Test Chart"}
    )
    
    assert result is not None
    assert result["chart_type"] == "bar"
    assert "chart_id" in result
    assert result["options"]["title"] == "Test Chart"


@pytest.mark.asyncio
async def test_create_line_chart(viz_client):
    """Test creating a line chart"""
    data = {
        "labels": ["Jan", "Feb", "Mar"],
        "datasets": [{
            "label": "Sales",
            "data": [100, 150, 200]
        }]
    }
    
    result = await viz_client.create_chart(
        chart_type="line",
        data=data,
        options={"title": "Sales Chart"}
    )
    
    assert result["chart_type"] == "line"
    assert result["data"]["type"] == "line"


@pytest.mark.asyncio
async def test_create_pie_chart(viz_client):
    """Test creating a pie chart"""
    data = {
        "labels": ["Red", "Blue", "Green"],
        "values": [30, 50, 20]
    }
    
    result = await viz_client.create_chart(
        chart_type="pie",
        data=data,
        options={"title": "Color Distribution"}
    )
    
    assert result["chart_type"] == "pie"
    assert result["data"]["type"] == "pie"


@pytest.mark.asyncio
async def test_invalid_chart_type(viz_client):
    """Test creating chart with invalid type"""
    with pytest.raises(ValueError):
        await viz_client.create_chart(
            chart_type="invalid_type",
            data={},
            options={}
        )


@pytest.mark.asyncio
async def test_analyze_data(viz_client):
    """Test data analysis"""
    data = [10, 20, 30, 40, 50]
    
    result = await viz_client.analyze_data(data, "basic")
    
    assert result["count"] == 5
    assert result["mean"] == 30.0
    assert result["median"] == 30.0
    assert result["min"] == 10
    assert result["max"] == 50


@pytest.mark.asyncio
async def test_analyze_data_advanced(viz_client):
    """Test advanced data analysis"""
    data = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    
    result = await viz_client.analyze_data(data, "advanced")
    
    assert result["count"] == 10
    assert "percentiles" in result
    assert "25" in result["percentiles"]
    assert "50" in result["percentiles"]
    assert "75" in result["percentiles"]


@pytest.mark.asyncio
async def test_export_chart(viz_client):
    """Test chart export"""
    result = await viz_client.export_chart("chart_123", "png")
    
    assert result["format"] == "png"
    assert result["mime_type"] == "image/png"


@pytest.mark.asyncio
async def test_get_chart_types(viz_client):
    """Test getting chart types"""
    result = await viz_client.get_chart_types()
    
    assert len(result) >= 12
    assert any(ct["type"] == "bar" for ct in result)
    assert any(ct["type"] == "line" for ct in result)
    assert any(ct["type"] == "pie" for ct in result)


@pytest.mark.asyncio
async def test_create_dashboard(viz_client):
    """Test dashboard creation"""
    charts = [
        {
            "type": "bar",
            "data": {"labels": ["A"], "datasets": [{"data": [10]}]},
            "options": {"title": "Chart 1"}
        },
        {
            "type": "line",
            "data": {"labels": ["B"], "datasets": [{"data": [20]}]},
            "options": {"title": "Chart 2"}
        }
    ]
    
    result = await viz_client.create_dashboard(
        charts=charts,
        layout={"columns": 2}
    )
    
    assert "dashboard_id" in result
    assert len(result["charts"]) == 2
    assert result["layout"]["columns"] == 2


@pytest.mark.asyncio
async def test_update_chart_data(viz_client):
    """Test updating chart data"""
    new_data = {
        "labels": ["X", "Y", "Z"],
        "datasets": [{"data": [5, 10, 15]}]
    }
    
    result = await viz_client.update_chart_data("chart_123", new_data)
    
    assert result["chart_id"] == "chart_123"
    assert result["data"] == new_data
    assert "updated_at" in result


@pytest.mark.asyncio
async def test_empty_data_analysis(viz_client):
    """Test analysis with empty data"""
    with pytest.raises(ValueError):
        await viz_client.analyze_data([], "basic")


@pytest.mark.asyncio
async def test_chart_with_custom_options(viz_client):
    """Test chart with custom options"""
    data = {"labels": ["A"], "datasets": [{"data": [10]}]}
    options = {
        "title": "Custom Chart",
        "width": 1000,
        "height": 800,
        "theme": "dark",
        "colors": ["#ff0000", "#00ff00"]
    }
    
    result = await viz_client.create_chart("bar", data, options)
    
    assert result["options"]["width"] == 1000
    assert result["options"]["height"] == 800
    assert result["options"]["theme"] == "dark"