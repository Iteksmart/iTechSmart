"""
iTechSmart Analytics - Core Analytics Engine
Advanced analytics, predictive modeling, and machine learning capabilities
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import warnings
warnings.filterwarnings('ignore')


class AnalyticsEngine:
    """Core analytics engine with ML capabilities"""
    
    def __init__(self, db: Session):
        self.db = db
        self.models = {}
        self.scalers = {}
    
    async def forecast(
        self,
        metric: str,
        data: pd.DataFrame,
        horizon: int = 30,
        model_type: str = "auto"
    ) -> Dict[str, Any]:
        """
        Generate forecast for a metric
        
        Args:
            metric: Metric name to forecast
            data: Historical data
            horizon: Forecast horizon in days
            model_type: Model type (auto, linear, rf, prophet)
        
        Returns:
            Forecast results with confidence intervals
        """
        
        if len(data) < 30:
            return {
                "error": "Insufficient data for forecasting (minimum 30 data points required)"
            }
        
        # Prepare data
        data = data.sort_values('timestamp')
        data['day'] = (data['timestamp'] - data['timestamp'].min()).dt.days
        
        X = data[['day']].values
        y = data[metric].values
        
        # Choose model
        if model_type == "auto":
            model_type = self._select_best_model(X, y)
        
        # Train model
        if model_type == "rf":
            model = RandomForestRegressor(n_estimators=100, random_state=42)
        else:
            from sklearn.linear_model import LinearRegression
            model = LinearRegression()
        
        model.fit(X, y)
        
        # Generate forecast
        last_day = data['day'].max()
        future_days = np.array([[last_day + i] for i in range(1, horizon + 1)])
        forecast_values = model.predict(future_days)
        
        # Calculate confidence intervals (simplified)
        residuals = y - model.predict(X)
        std_error = np.std(residuals)
        confidence_interval = 1.96 * std_error  # 95% CI
        
        forecast_dates = [
            data['timestamp'].max() + timedelta(days=i)
            for i in range(1, horizon + 1)
        ]
        
        return {
            "metric": metric,
            "model_type": model_type,
            "forecast": [
                {
                    "date": date.isoformat(),
                    "value": float(value),
                    "lower_bound": float(value - confidence_interval),
                    "upper_bound": float(value + confidence_interval)
                }
                for date, value in zip(forecast_dates, forecast_values)
            ],
            "accuracy_score": float(model.score(X, y)),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def detect_anomalies(
        self,
        metric: str,
        data: pd.DataFrame,
        sensitivity: str = "medium"
    ) -> Dict[str, Any]:
        """
        Detect anomalies in metric data
        
        Args:
            metric: Metric name
            data: Historical data
            sensitivity: Detection sensitivity (low, medium, high)
        
        Returns:
            Detected anomalies with scores
        """
        
        if len(data) < 10:
            return {
                "error": "Insufficient data for anomaly detection"
            }
        
        # Set contamination based on sensitivity
        contamination_map = {
            "low": 0.01,
            "medium": 0.05,
            "high": 0.10
        }
        contamination = contamination_map.get(sensitivity, 0.05)
        
        # Prepare features
        data = data.sort_values('timestamp')
        features = self._extract_features(data, metric)
        
        # Train isolation forest
        model = IsolationForest(
            contamination=contamination,
            random_state=42
        )
        predictions = model.fit_predict(features)
        scores = model.score_samples(features)
        
        # Identify anomalies
        anomalies = []
        for idx, (pred, score) in enumerate(zip(predictions, scores)):
            if pred == -1:  # Anomaly
                anomalies.append({
                    "timestamp": data.iloc[idx]['timestamp'].isoformat(),
                    "value": float(data.iloc[idx][metric]),
                    "anomaly_score": float(-score),  # Convert to positive
                    "severity": self._calculate_severity(score, scores)
                })
        
        return {
            "metric": metric,
            "sensitivity": sensitivity,
            "total_points": len(data),
            "anomalies_detected": len(anomalies),
            "anomalies": sorted(anomalies, key=lambda x: x['anomaly_score'], reverse=True),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def analyze_trends(
        self,
        metric: str,
        data: pd.DataFrame,
        period: str = "daily"
    ) -> Dict[str, Any]:
        """
        Analyze trends in metric data
        
        Args:
            metric: Metric name
            data: Historical data
            period: Aggregation period (hourly, daily, weekly, monthly)
        
        Returns:
            Trend analysis results
        """
        
        data = data.sort_values('timestamp')
        
        # Aggregate by period
        if period == "hourly":
            data['period'] = data['timestamp'].dt.floor('H')
        elif period == "daily":
            data['period'] = data['timestamp'].dt.date
        elif period == "weekly":
            data['period'] = data['timestamp'].dt.to_period('W')
        elif period == "monthly":
            data['period'] = data['timestamp'].dt.to_period('M')
        
        aggregated = data.groupby('period')[metric].agg(['mean', 'min', 'max', 'std']).reset_index()
        
        # Calculate trend
        values = aggregated['mean'].values
        trend_direction = "stable"
        trend_strength = 0.0
        
        if len(values) > 1:
            # Simple linear regression for trend
            x = np.arange(len(values))
            coefficients = np.polyfit(x, values, 1)
            slope = coefficients[0]
            
            # Determine direction and strength
            avg_value = np.mean(values)
            if avg_value != 0:
                trend_strength = abs(slope / avg_value) * 100
                
                if slope > 0.01 * avg_value:
                    trend_direction = "increasing"
                elif slope < -0.01 * avg_value:
                    trend_direction = "decreasing"
        
        # Calculate statistics
        overall_stats = {
            "mean": float(np.mean(values)),
            "median": float(np.median(values)),
            "std": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
            "range": float(np.max(values) - np.min(values))
        }
        
        # Identify peaks and valleys
        peaks = self._find_peaks(values)
        valleys = self._find_valleys(values)
        
        return {
            "metric": metric,
            "period": period,
            "trend_direction": trend_direction,
            "trend_strength": float(trend_strength),
            "statistics": overall_stats,
            "peaks": [
                {
                    "period": str(aggregated.iloc[i]['period']),
                    "value": float(values[i])
                }
                for i in peaks
            ],
            "valleys": [
                {
                    "period": str(aggregated.iloc[i]['period']),
                    "value": float(values[i])
                }
                for i in valleys
            ],
            "data_points": len(values),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def correlation_analysis(
        self,
        metrics: List[str],
        data: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Analyze correlations between multiple metrics
        
        Args:
            metrics: List of metric names
            data: Historical data containing all metrics
        
        Returns:
            Correlation matrix and insights
        """
        
        # Calculate correlation matrix
        correlation_matrix = data[metrics].corr()
        
        # Find strong correlations
        strong_correlations = []
        for i, metric1 in enumerate(metrics):
            for j, metric2 in enumerate(metrics):
                if i < j:  # Avoid duplicates
                    corr_value = correlation_matrix.iloc[i, j]
                    if abs(corr_value) > 0.7:  # Strong correlation threshold
                        strong_correlations.append({
                            "metric1": metric1,
                            "metric2": metric2,
                            "correlation": float(corr_value),
                            "strength": "strong positive" if corr_value > 0 else "strong negative"
                        })
        
        return {
            "metrics": metrics,
            "correlation_matrix": correlation_matrix.to_dict(),
            "strong_correlations": sorted(
                strong_correlations,
                key=lambda x: abs(x['correlation']),
                reverse=True
            ),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def segment_analysis(
        self,
        data: pd.DataFrame,
        segment_by: str,
        metrics: List[str]
    ) -> Dict[str, Any]:
        """
        Analyze metrics by segments
        
        Args:
            data: Historical data
            segment_by: Column to segment by
            metrics: Metrics to analyze
        
        Returns:
            Segment analysis results
        """
        
        segments = {}
        
        for segment_value in data[segment_by].unique():
            segment_data = data[data[segment_by] == segment_value]
            
            segment_stats = {}
            for metric in metrics:
                segment_stats[metric] = {
                    "mean": float(segment_data[metric].mean()),
                    "median": float(segment_data[metric].median()),
                    "std": float(segment_data[metric].std()),
                    "min": float(segment_data[metric].min()),
                    "max": float(segment_data[metric].max()),
                    "count": int(len(segment_data))
                }
            
            segments[str(segment_value)] = segment_stats
        
        return {
            "segment_by": segment_by,
            "metrics": metrics,
            "segments": segments,
            "total_segments": len(segments),
            "generated_at": datetime.utcnow().isoformat()
        }
    
    async def cohort_analysis(
        self,
        data: pd.DataFrame,
        cohort_column: str,
        metric: str,
        time_column: str = "timestamp"
    ) -> Dict[str, Any]:
        """
        Perform cohort analysis
        
        Args:
            data: Historical data
            cohort_column: Column defining cohorts
            metric: Metric to analyze
            time_column: Time column name
        
        Returns:
            Cohort analysis results
        """
        
        # Group by cohort and time period
        data['period'] = data[time_column].dt.to_period('M')
        cohort_data = data.groupby([cohort_column, 'period'])[metric].mean().reset_index()
        
        # Pivot to create cohort matrix
        cohort_matrix = cohort_data.pivot(
            index=cohort_column,
            columns='period',
            values=metric
        )
        
        return {
            "cohort_column": cohort_column,
            "metric": metric,
            "cohort_matrix": cohort_matrix.to_dict(),
            "cohorts": list(cohort_matrix.index),
            "periods": [str(p) for p in cohort_matrix.columns],
            "generated_at": datetime.utcnow().isoformat()
        }
    
    # Helper methods
    
    def _select_best_model(self, X: np.ndarray, y: np.ndarray) -> str:
        """Select best forecasting model based on data characteristics"""
        
        # Simple heuristic: use RF for non-linear patterns, linear otherwise
        if len(y) < 100:
            return "linear"
        
        # Check for non-linearity
        from sklearn.linear_model import LinearRegression
        lr = LinearRegression()
        lr.fit(X, y)
        linear_score = lr.score(X, y)
        
        if linear_score > 0.8:
            return "linear"
        else:
            return "rf"
    
    def _extract_features(self, data: pd.DataFrame, metric: str) -> np.ndarray:
        """Extract features for anomaly detection"""
        
        features = []
        
        # Value itself
        features.append(data[metric].values)
        
        # Rolling statistics
        if len(data) > 5:
            features.append(data[metric].rolling(window=5, min_periods=1).mean().values)
            features.append(data[metric].rolling(window=5, min_periods=1).std().fillna(0).values)
        
        return np.column_stack(features)
    
    def _calculate_severity(self, score: float, all_scores: np.ndarray) -> str:
        """Calculate anomaly severity"""
        
        percentile = np.percentile(all_scores, [25, 50, 75])
        
        if score < percentile[0]:
            return "critical"
        elif score < percentile[1]:
            return "high"
        elif score < percentile[2]:
            return "medium"
        else:
            return "low"
    
    def _find_peaks(self, values: np.ndarray) -> List[int]:
        """Find peaks in data"""
        
        peaks = []
        for i in range(1, len(values) - 1):
            if values[i] > values[i-1] and values[i] > values[i+1]:
                peaks.append(i)
        return peaks
    
    def _find_valleys(self, values: np.ndarray) -> List[int]:
        """Find valleys in data"""
        
        valleys = []
        for i in range(1, len(values) - 1):
            if values[i] < values[i-1] and values[i] < values[i+1]:
                valleys.append(i)
        return valleys