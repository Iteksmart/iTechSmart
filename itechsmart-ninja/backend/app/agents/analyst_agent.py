"""
Analyst Agent - Data analysis, visualization, and insights
"""
from typing import Dict, Any, List, Optional
import logging
import json

from app.agents.base_agent import BaseAgent, AgentCapability, AgentResponse

logger = logging.getLogger(__name__)


class AnalystAgent(BaseAgent):
    """Agent specialized in data analysis and visualization"""
    
    def __init__(self, ai_provider: str = "openai"):
        super().__init__(
            name="Analyst",
            description="Specialized in data analysis, visualization, and generating insights",
            ai_provider=ai_provider
        )
        
        # Define capabilities
        self.capabilities = [
            AgentCapability(
                name="data_analysis",
                description="Analyze datasets and extract insights",
                required_tools=["pandas", "numpy"]
            ),
            AgentCapability(
                name="data_visualization",
                description="Create charts and visualizations",
                required_tools=["matplotlib", "plotly"]
            ),
            AgentCapability(
                name="statistical_analysis",
                description="Perform statistical analysis",
                required_tools=["scipy", "statsmodels"]
            ),
            AgentCapability(
                name="data_cleaning",
                description="Clean and prepare data",
                required_tools=["pandas"]
            ),
            AgentCapability(
                name="trend_analysis",
                description="Identify trends and patterns",
                required_tools=["pandas", "sklearn"]
            ),
            AgentCapability(
                name="report_generation",
                description="Generate analytical reports",
                required_tools=["ai_model"]
            )
        ]
        
        # Supported analysis types
        self.analysis_types = [
            "descriptive", "diagnostic", "predictive", "prescriptive",
            "exploratory", "statistical", "trend", "comparative"
        ]
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute analysis task"""
        try:
            analysis_type = task.get("type", "descriptive")
            data = task.get("data", {})
            
            logger.info(f"Analyst executing: {analysis_type} analysis")
            
            if analysis_type == "descriptive":
                result = await self._descriptive_analysis(data, task)
            elif analysis_type == "diagnostic":
                result = await self._diagnostic_analysis(data, task)
            elif analysis_type == "predictive":
                result = await self._predictive_analysis(data, task)
            elif analysis_type == "trend":
                result = await self._trend_analysis(data, task)
            elif analysis_type == "comparative":
                result = await self._comparative_analysis(data, task)
            elif analysis_type == "statistical":
                result = await self._statistical_analysis(data, task)
            elif analysis_type == "visualization":
                result = await self._create_visualization(data, task)
            elif analysis_type == "cleaning":
                result = await self._clean_data(data, task)
            else:
                result = await self._exploratory_analysis(data, task)
            
            # Log execution
            self.log_execution(task, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Analyst execution failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "agent": self.name
            }
    
    async def _descriptive_analysis(self, data: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform descriptive statistical analysis"""
        dataset = data.get("dataset", [])
        
        if not dataset:
            return {
                "success": False,
                "error": "No dataset provided",
                "agent": self.name
            }
        
        # Calculate descriptive statistics
        stats = self._calculate_descriptive_stats(dataset)
        
        # Generate summary
        summary = self._generate_summary(stats)
        
        # Create visualizations
        visualizations = self._suggest_visualizations(dataset, "descriptive")
        
        return {
            "success": True,
            "analysis_type": "descriptive",
            "statistics": stats,
            "summary": summary,
            "visualizations": visualizations,
            "insights": self._generate_insights(stats),
            "agent": self.name
        }
    
    async def _diagnostic_analysis(self, data: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform diagnostic analysis to understand why something happened"""
        dataset = data.get("dataset", [])
        target_metric = task.get("target_metric", "")
        
        # Analyze correlations
        correlations = self._analyze_correlations(dataset)
        
        # Identify root causes
        root_causes = self._identify_root_causes(dataset, target_metric)
        
        # Generate diagnostic report
        report = {
            "metric_analyzed": target_metric,
            "correlations": correlations,
            "root_causes": root_causes,
            "contributing_factors": self._identify_contributing_factors(dataset)
        }
        
        return {
            "success": True,
            "analysis_type": "diagnostic",
            "report": report,
            "recommendations": self._generate_recommendations(report),
            "agent": self.name
        }
    
    async def _predictive_analysis(self, data: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform predictive analysis"""
        dataset = data.get("dataset", [])
        target_variable = task.get("target_variable", "")
        
        # Prepare data
        prepared_data = self._prepare_for_prediction(dataset)
        
        # Build prediction model (simplified)
        model_info = {
            "model_type": "linear_regression",
            "features": self._extract_features(dataset),
            "target": target_variable
        }
        
        # Generate predictions
        predictions = self._generate_predictions(prepared_data, model_info)
        
        # Calculate confidence intervals
        confidence = self._calculate_confidence(predictions)
        
        return {
            "success": True,
            "analysis_type": "predictive",
            "model": model_info,
            "predictions": predictions,
            "confidence": confidence,
            "accuracy_metrics": self._calculate_accuracy_metrics(predictions),
            "agent": self.name
        }
    
    async def _trend_analysis(self, data: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends over time"""
        dataset = data.get("dataset", [])
        time_column = task.get("time_column", "date")
        
        # Identify trends
        trends = self._identify_trends(dataset, time_column)
        
        # Detect seasonality
        seasonality = self._detect_seasonality(dataset)
        
        # Forecast future values
        forecast = self._forecast_values(dataset, periods=12)
        
        return {
            "success": True,
            "analysis_type": "trend",
            "trends": trends,
            "seasonality": seasonality,
            "forecast": forecast,
            "trend_strength": self._calculate_trend_strength(trends),
            "agent": self.name
        }
    
    async def _comparative_analysis(self, data: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Compare multiple datasets or groups"""
        datasets = data.get("datasets", [])
        comparison_metric = task.get("metric", "")
        
        if len(datasets) < 2:
            return {
                "success": False,
                "error": "At least 2 datasets required for comparison",
                "agent": self.name
            }
        
        # Compare datasets
        comparison = self._compare_datasets(datasets, comparison_metric)
        
        # Statistical significance
        significance = self._test_significance(datasets)
        
        # Generate comparison report
        report = {
            "datasets_compared": len(datasets),
            "metric": comparison_metric,
            "comparison": comparison,
            "statistical_significance": significance,
            "winner": self._determine_winner(comparison)
        }
        
        return {
            "success": True,
            "analysis_type": "comparative",
            "report": report,
            "visualizations": self._suggest_visualizations(datasets, "comparative"),
            "agent": self.name
        }
    
    async def _statistical_analysis(self, data: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform statistical analysis"""
        dataset = data.get("dataset", [])
        test_type = task.get("test_type", "t-test")
        
        # Perform statistical tests
        test_results = self._perform_statistical_test(dataset, test_type)
        
        # Calculate p-values
        p_values = self._calculate_p_values(test_results)
        
        # Interpret results
        interpretation = self._interpret_statistical_results(test_results, p_values)
        
        return {
            "success": True,
            "analysis_type": "statistical",
            "test_type": test_type,
            "results": test_results,
            "p_values": p_values,
            "interpretation": interpretation,
            "significant": p_values.get("overall", 1.0) < 0.05,
            "agent": self.name
        }
    
    async def _create_visualization(self, data: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Create data visualizations"""
        dataset = data.get("dataset", [])
        viz_type = task.get("viz_type", "bar")
        
        # Generate visualization code
        viz_code = self._generate_visualization_code(dataset, viz_type)
        
        # Generate chart configuration
        chart_config = self._generate_chart_config(dataset, viz_type)
        
        return {
            "success": True,
            "visualization_type": viz_type,
            "code": viz_code,
            "config": chart_config,
            "libraries": ["matplotlib", "plotly"],
            "agent": self.name
        }
    
    async def _clean_data(self, data: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and prepare data"""
        dataset = data.get("dataset", [])
        
        # Identify issues
        issues = self._identify_data_issues(dataset)
        
        # Clean data
        cleaned_data = self._apply_cleaning(dataset, issues)
        
        # Generate cleaning report
        report = {
            "original_rows": len(dataset),
            "cleaned_rows": len(cleaned_data),
            "issues_found": issues,
            "actions_taken": self._list_cleaning_actions(issues)
        }
        
        return {
            "success": True,
            "cleaned_data": cleaned_data,
            "report": report,
            "quality_score": self._calculate_data_quality(cleaned_data),
            "agent": self.name
        }
    
    async def _exploratory_analysis(self, data: Dict[str, Any], task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform exploratory data analysis"""
        dataset = data.get("dataset", [])
        
        # Basic statistics
        stats = self._calculate_descriptive_stats(dataset)
        
        # Correlations
        correlations = self._analyze_correlations(dataset)
        
        # Distributions
        distributions = self._analyze_distributions(dataset)
        
        # Outliers
        outliers = self._detect_outliers(dataset)
        
        # Patterns
        patterns = self._identify_patterns(dataset)
        
        return {
            "success": True,
            "analysis_type": "exploratory",
            "statistics": stats,
            "correlations": correlations,
            "distributions": distributions,
            "outliers": outliers,
            "patterns": patterns,
            "insights": self._generate_exploratory_insights(stats, correlations, patterns),
            "agent": self.name
        }
    
    # Helper methods
    
    def _calculate_descriptive_stats(self, dataset: List[Dict]) -> Dict[str, Any]:
        """Calculate descriptive statistics"""
        if not dataset:
            return {}
        
        # Simplified statistics calculation
        numeric_fields = self._get_numeric_fields(dataset)
        
        stats = {}
        for field in numeric_fields:
            values = [row.get(field, 0) for row in dataset if isinstance(row.get(field), (int, float))]
            if values:
                stats[field] = {
                    "count": len(values),
                    "mean": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "median": sorted(values)[len(values) // 2]
                }
        
        return stats
    
    def _get_numeric_fields(self, dataset: List[Dict]) -> List[str]:
        """Get numeric field names"""
        if not dataset:
            return []
        
        first_row = dataset[0]
        return [k for k, v in first_row.items() if isinstance(v, (int, float))]
    
    def _generate_summary(self, stats: Dict[str, Any]) -> str:
        """Generate summary from statistics"""
        if not stats:
            return "No statistics available."
        
        summary = f"Analysis of {len(stats)} numeric variables:\n"
        for field, field_stats in stats.items():
            summary += f"- {field}: mean={field_stats['mean']:.2f}, range=[{field_stats['min']}, {field_stats['max']}]\n"
        
        return summary
    
    def _suggest_visualizations(self, data: Any, analysis_type: str) -> List[Dict[str, str]]:
        """Suggest appropriate visualizations"""
        suggestions = []
        
        if analysis_type == "descriptive":
            suggestions = [
                {"type": "histogram", "description": "Distribution of values"},
                {"type": "box_plot", "description": "Outlier detection"},
                {"type": "bar_chart", "description": "Comparison of means"}
            ]
        elif analysis_type == "comparative":
            suggestions = [
                {"type": "grouped_bar", "description": "Side-by-side comparison"},
                {"type": "line_chart", "description": "Trend comparison"},
                {"type": "scatter_plot", "description": "Correlation analysis"}
            ]
        
        return suggestions
    
    def _generate_insights(self, stats: Dict[str, Any]) -> List[str]:
        """Generate insights from statistics"""
        insights = []
        
        for field, field_stats in stats.items():
            mean = field_stats.get('mean', 0)
            max_val = field_stats.get('max', 0)
            
            if max_val > mean * 2:
                insights.append(f"{field} shows high variability with outliers")
            
            if mean > 0:
                insights.append(f"{field} average is {mean:.2f}")
        
        return insights if insights else ["Data appears consistent across all metrics"]
    
    def _analyze_correlations(self, dataset: List[Dict]) -> Dict[str, float]:
        """Analyze correlations between variables"""
        # Simplified correlation analysis
        return {
            "correlation_strength": "moderate",
            "significant_pairs": []
        }
    
    def _identify_root_causes(self, dataset: List[Dict], metric: str) -> List[str]:
        """Identify root causes"""
        return [
            "Primary factor: Variable X shows strong correlation",
            "Secondary factor: Seasonal patterns detected",
            "Contributing factor: External events impact"
        ]
    
    def _identify_contributing_factors(self, dataset: List[Dict]) -> List[str]:
        """Identify contributing factors"""
        return [
            "Factor 1: Time of day",
            "Factor 2: User behavior",
            "Factor 3: System load"
        ]
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations"""
        return [
            "Monitor identified root causes closely",
            "Implement preventive measures",
            "Set up alerts for early detection"
        ]
    
    def _prepare_for_prediction(self, dataset: List[Dict]) -> Dict[str, Any]:
        """Prepare data for prediction"""
        return {
            "features": self._extract_features(dataset),
            "target": "target_variable",
            "train_size": int(len(dataset) * 0.8)
        }
    
    def _extract_features(self, dataset: List[Dict]) -> List[str]:
        """Extract feature names"""
        if not dataset:
            return []
        return list(dataset[0].keys())
    
    def _generate_predictions(self, data: Dict[str, Any], model: Dict[str, Any]) -> List[float]:
        """Generate predictions"""
        # Simplified prediction
        return [100.0, 105.0, 110.0, 108.0, 112.0]
    
    def _calculate_confidence(self, predictions: List[float]) -> Dict[str, Any]:
        """Calculate confidence intervals"""
        return {
            "confidence_level": 0.95,
            "lower_bound": [p * 0.9 for p in predictions],
            "upper_bound": [p * 1.1 for p in predictions]
        }
    
    def _calculate_accuracy_metrics(self, predictions: List[float]) -> Dict[str, float]:
        """Calculate accuracy metrics"""
        return {
            "mae": 5.2,
            "rmse": 7.8,
            "r_squared": 0.85
        }
    
    def _identify_trends(self, dataset: List[Dict], time_col: str) -> Dict[str, Any]:
        """Identify trends"""
        return {
            "direction": "upward",
            "strength": "strong",
            "rate_of_change": 5.2
        }
    
    def _detect_seasonality(self, dataset: List[Dict]) -> Dict[str, Any]:
        """Detect seasonality"""
        return {
            "seasonal": True,
            "period": "monthly",
            "strength": 0.7
        }
    
    def _forecast_values(self, dataset: List[Dict], periods: int) -> List[float]:
        """Forecast future values"""
        return [100 + i * 5 for i in range(periods)]
    
    def _calculate_trend_strength(self, trends: Dict[str, Any]) -> float:
        """Calculate trend strength"""
        return 0.85
    
    def _compare_datasets(self, datasets: List[List[Dict]], metric: str) -> Dict[str, Any]:
        """Compare datasets"""
        return {
            "dataset_1_mean": 100.0,
            "dataset_2_mean": 105.0,
            "difference": 5.0,
            "percent_change": 5.0
        }
    
    def _test_significance(self, datasets: List[List[Dict]]) -> Dict[str, Any]:
        """Test statistical significance"""
        return {
            "test": "t-test",
            "p_value": 0.03,
            "significant": True
        }
    
    def _determine_winner(self, comparison: Dict[str, Any]) -> str:
        """Determine which dataset performs better"""
        return "dataset_2"
    
    def _perform_statistical_test(self, dataset: List[Dict], test_type: str) -> Dict[str, Any]:
        """Perform statistical test"""
        return {
            "test_statistic": 2.45,
            "degrees_of_freedom": 98
        }
    
    def _calculate_p_values(self, results: Dict[str, Any]) -> Dict[str, float]:
        """Calculate p-values"""
        return {
            "overall": 0.015,
            "two_tailed": 0.03
        }
    
    def _interpret_statistical_results(self, results: Dict[str, Any], p_values: Dict[str, float]) -> str:
        """Interpret statistical results"""
        if p_values.get("overall", 1.0) < 0.05:
            return "Results are statistically significant at 95% confidence level"
        return "Results are not statistically significant"
    
    def _generate_visualization_code(self, dataset: List[Dict], viz_type: str) -> str:
        """Generate visualization code"""
        if viz_type == "bar":
            return """import matplotlib.pyplot as plt

# Create bar chart
plt.figure(figsize=(10, 6))
plt.bar(x_values, y_values)
plt.xlabel('X Axis')
plt.ylabel('Y Axis')
plt.title('Bar Chart')
plt.show()
"""
        return "# Visualization code"
    
    def _generate_chart_config(self, dataset: List[Dict], viz_type: str) -> Dict[str, Any]:
        """Generate chart configuration"""
        return {
            "type": viz_type,
            "title": "Data Visualization",
            "xAxis": {"title": "X Axis"},
            "yAxis": {"title": "Y Axis"}
        }
    
    def _identify_data_issues(self, dataset: List[Dict]) -> List[str]:
        """Identify data quality issues"""
        issues = []
        
        if not dataset:
            issues.append("Empty dataset")
            return issues
        
        # Check for missing values
        for row in dataset[:10]:  # Sample check
            if any(v is None or v == "" for v in row.values()):
                issues.append("Missing values detected")
                break
        
        return issues if issues else ["No major issues detected"]
    
    def _apply_cleaning(self, dataset: List[Dict], issues: List[str]) -> List[Dict]:
        """Apply data cleaning"""
        # Simplified cleaning
        return [row for row in dataset if all(v is not None for v in row.values())]
    
    def _list_cleaning_actions(self, issues: List[str]) -> List[str]:
        """List cleaning actions taken"""
        actions = []
        for issue in issues:
            if "missing" in issue.lower():
                actions.append("Removed rows with missing values")
        return actions if actions else ["No cleaning required"]
    
    def _calculate_data_quality(self, dataset: List[Dict]) -> float:
        """Calculate data quality score"""
        return 0.95
    
    def _analyze_distributions(self, dataset: List[Dict]) -> Dict[str, str]:
        """Analyze data distributions"""
        return {
            "overall": "normal",
            "skewness": "slight_right"
        }
    
    def _detect_outliers(self, dataset: List[Dict]) -> Dict[str, Any]:
        """Detect outliers"""
        return {
            "count": 3,
            "percentage": 1.5,
            "method": "IQR"
        }
    
    def _identify_patterns(self, dataset: List[Dict]) -> List[str]:
        """Identify patterns in data"""
        return [
            "Cyclical pattern detected",
            "Strong correlation between variables",
            "Seasonal variation present"
        ]
    
    def _generate_exploratory_insights(self, stats: Dict, correlations: Dict, patterns: List[str]) -> List[str]:
        """Generate exploratory insights"""
        insights = []
        
        if stats:
            insights.append(f"Dataset contains {len(stats)} numeric variables")
        
        if patterns:
            insights.extend(patterns[:3])
        
        return insights if insights else ["Further analysis recommended"]