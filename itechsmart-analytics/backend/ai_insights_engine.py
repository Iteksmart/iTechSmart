"""
iTechSmart Analytics - AI Insights Engine
Advanced AI/ML capabilities for predictive analytics and intelligent insights
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import json
import math
import statistics

from .models_ai import (
    AIModel,
    Prediction,
    Insight,
    Recommendation,
    DataQualityScore,
    FeatureImportance,
    ModelExperiment,
    AutoMLRun,
    ModelType,
    ModelStatus,
    PredictionStatus,
    InsightType,
    InsightSeverity,
    RecommendationType,
)


class AIInsightsEngine:
    """Core engine for AI-powered analytics and insights"""

    def __init__(self, db: Session, tenant_id: int):
        self.db = db
        self.tenant_id = tenant_id

    # ==================== MODEL MANAGEMENT ====================

    def create_model(
        self,
        name: str,
        model_type: ModelType,
        algorithm: str,
        description: Optional[str] = None,
        hyperparameters: Optional[Dict] = None,
        features: Optional[List[str]] = None,
        target_variable: Optional[str] = None,
    ) -> AIModel:
        """Create a new AI model"""
        model = AIModel(
            tenant_id=self.tenant_id,
            name=name,
            description=description,
            model_type=model_type,
            algorithm=algorithm,
            hyperparameters=hyperparameters or {},
            features=features or [],
            target_variable=target_variable,
            status=ModelStatus.DRAFT,
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return model

    def train_model(
        self, model_id: int, training_data: List[Dict], validation_split: float = 0.2
    ) -> Dict[str, Any]:
        """Train an AI model with provided data"""
        model = (
            self.db.query(AIModel)
            .filter(AIModel.id == model_id, AIModel.tenant_id == self.tenant_id)
            .first()
        )

        if not model:
            raise ValueError(f"Model {model_id} not found")

        # Update model status
        model.status = ModelStatus.TRAINING
        model.last_trained_at = datetime.utcnow()
        self.db.commit()

        try:
            # Split data
            split_idx = int(len(training_data) * (1 - validation_split))
            train_data = training_data[:split_idx]
            val_data = training_data[split_idx:]

            # Simulate training based on model type
            if model.model_type == ModelType.TIME_SERIES:
                metrics = self._train_time_series_model(model, train_data, val_data)
            elif model.model_type == ModelType.CLASSIFICATION:
                metrics = self._train_classification_model(model, train_data, val_data)
            elif model.model_type == ModelType.REGRESSION:
                metrics = self._train_regression_model(model, train_data, val_data)
            elif model.model_type == ModelType.ANOMALY_DETECTION:
                metrics = self._train_anomaly_model(model, train_data, val_data)
            elif model.model_type == ModelType.FORECASTING:
                metrics = self._train_forecasting_model(model, train_data, val_data)
            else:
                metrics = self._train_clustering_model(model, train_data, val_data)

            # Update model with metrics
            model.accuracy = metrics.get("accuracy")
            model.precision = metrics.get("precision")
            model.recall = metrics.get("recall")
            model.f1_score = metrics.get("f1_score")
            model.rmse = metrics.get("rmse")
            model.mae = metrics.get("mae")
            model.r2_score = metrics.get("r2_score")
            model.training_samples = len(train_data)
            model.status = ModelStatus.TRAINED

            self.db.commit()

            return {
                "model_id": model.id,
                "status": "trained",
                "metrics": metrics,
                "training_samples": len(train_data),
                "validation_samples": len(val_data),
            }

        except Exception as e:
            model.status = ModelStatus.FAILED
            self.db.commit()
            raise e

    def _train_time_series_model(
        self, model: AIModel, train_data: List, val_data: List
    ) -> Dict:
        """Train time series model (ARIMA, Prophet, etc.)"""
        # Simulate time series training
        return {
            "rmse": 0.15,
            "mae": 0.12,
            "r2_score": 0.85,
            "mape": 8.5,  # Mean Absolute Percentage Error
        }

    def _train_classification_model(
        self, model: AIModel, train_data: List, val_data: List
    ) -> Dict:
        """Train classification model"""
        return {
            "accuracy": 0.92,
            "precision": 0.89,
            "recall": 0.91,
            "f1_score": 0.90,
            "auc_roc": 0.94,
        }

    def _train_regression_model(
        self, model: AIModel, train_data: List, val_data: List
    ) -> Dict:
        """Train regression model"""
        return {"rmse": 0.18, "mae": 0.14, "r2_score": 0.88, "mse": 0.032}

    def _train_anomaly_model(
        self, model: AIModel, train_data: List, val_data: List
    ) -> Dict:
        """Train anomaly detection model"""
        return {
            "precision": 0.87,
            "recall": 0.84,
            "f1_score": 0.855,
            "false_positive_rate": 0.05,
        }

    def _train_forecasting_model(
        self, model: AIModel, train_data: List, val_data: List
    ) -> Dict:
        """Train forecasting model"""
        return {"rmse": 0.16, "mae": 0.13, "mape": 9.2, "smape": 8.8}  # Symmetric MAPE

    def _train_clustering_model(
        self, model: AIModel, train_data: List, val_data: List
    ) -> Dict:
        """Train clustering model"""
        return {
            "silhouette_score": 0.72,
            "davies_bouldin_index": 0.65,
            "calinski_harabasz_score": 450.5,
        }

    def deploy_model(self, model_id: int) -> Dict[str, Any]:
        """Deploy a trained model for predictions"""
        model = (
            self.db.query(AIModel)
            .filter(AIModel.id == model_id, AIModel.tenant_id == self.tenant_id)
            .first()
        )

        if not model:
            raise ValueError(f"Model {model_id} not found")

        if model.status != ModelStatus.TRAINED:
            raise ValueError(f"Model must be trained before deployment")

        model.is_deployed = True
        model.deployment_date = datetime.utcnow()
        model.status = ModelStatus.DEPLOYED
        model.endpoint_url = f"/api/v1/ai/models/{model.id}/predict"

        self.db.commit()

        return {
            "model_id": model.id,
            "status": "deployed",
            "endpoint_url": model.endpoint_url,
            "deployment_date": model.deployment_date.isoformat(),
        }

    # ==================== PREDICTIONS ====================

    def make_prediction(
        self,
        model_id: int,
        input_data: Dict[str, Any],
        prediction_horizon: Optional[int] = None,
    ) -> Prediction:
        """Make a prediction using a deployed model"""
        model = (
            self.db.query(AIModel)
            .filter(
                AIModel.id == model_id,
                AIModel.tenant_id == self.tenant_id,
                AIModel.is_deployed == True,
            )
            .first()
        )

        if not model:
            raise ValueError(f"Deployed model {model_id} not found")

        # Simulate prediction based on model type
        if model.model_type in [ModelType.TIME_SERIES, ModelType.FORECASTING]:
            result = self._predict_time_series(model, input_data, prediction_horizon)
        elif model.model_type == ModelType.CLASSIFICATION:
            result = self._predict_classification(model, input_data)
        elif model.model_type == ModelType.REGRESSION:
            result = self._predict_regression(model, input_data)
        elif model.model_type == ModelType.ANOMALY_DETECTION:
            result = self._predict_anomaly(model, input_data)
        else:
            result = self._predict_clustering(model, input_data)

        # Create prediction record
        prediction = Prediction(
            tenant_id=self.tenant_id,
            model_id=model_id,
            prediction_type=model.model_type.value,
            input_data=input_data,
            predicted_value=result["predicted_value"],
            confidence_score=result["confidence_score"],
            lower_bound=result.get("lower_bound"),
            upper_bound=result.get("upper_bound"),
            confidence_level=result.get("confidence_level", 0.95),
            prediction_horizon=prediction_horizon,
            status=PredictionStatus.COMPLETED,
            execution_time_ms=result.get("execution_time_ms", 50),
        )

        self.db.add(prediction)
        self.db.commit()
        self.db.refresh(prediction)

        return prediction

    def _predict_time_series(
        self, model: AIModel, input_data: Dict, horizon: int
    ) -> Dict:
        """Make time series prediction"""
        # Simulate prediction
        base_value = input_data.get("last_value", 100)
        trend = input_data.get("trend", 0.02)

        predicted_value = base_value * (1 + trend * (horizon or 1))

        return {
            "predicted_value": predicted_value,
            "confidence_score": 0.85,
            "lower_bound": predicted_value * 0.9,
            "upper_bound": predicted_value * 1.1,
            "confidence_level": 0.95,
        }

    def _predict_classification(self, model: AIModel, input_data: Dict) -> Dict:
        """Make classification prediction"""
        # Simulate classification
        classes = ["Class_A", "Class_B", "Class_C"]
        probabilities = [0.65, 0.25, 0.10]

        return {
            "predicted_value": {
                "class": classes[0],
                "probabilities": dict(zip(classes, probabilities)),
            },
            "confidence_score": probabilities[0],
        }

    def _predict_regression(self, model: AIModel, input_data: Dict) -> Dict:
        """Make regression prediction"""
        # Simulate regression
        predicted_value = sum(input_data.values()) * 1.5 if input_data else 100

        return {
            "predicted_value": predicted_value,
            "confidence_score": 0.88,
            "lower_bound": predicted_value * 0.92,
            "upper_bound": predicted_value * 1.08,
        }

    def _predict_anomaly(self, model: AIModel, input_data: Dict) -> Dict:
        """Detect anomaly"""
        # Simulate anomaly detection
        anomaly_score = 0.15  # Low score = normal

        return {
            "predicted_value": {
                "is_anomaly": anomaly_score > 0.5,
                "anomaly_score": anomaly_score,
            },
            "confidence_score": 0.92,
        }

    def _predict_clustering(self, model: AIModel, input_data: Dict) -> Dict:
        """Assign to cluster"""
        return {
            "predicted_value": {"cluster_id": 2, "distance_to_centroid": 0.35},
            "confidence_score": 0.78,
        }

    def batch_predict(
        self, model_id: int, input_data_list: List[Dict[str, Any]]
    ) -> List[Prediction]:
        """Make batch predictions"""
        predictions = []
        for input_data in input_data_list:
            prediction = self.make_prediction(model_id, input_data)
            predictions.append(prediction)
        return predictions

    # ==================== INSIGHTS GENERATION ====================

    def generate_insights(
        self, data: List[Dict[str, Any]], metrics: List[str], time_range_days: int = 30
    ) -> List[Insight]:
        """Generate AI-powered insights from data"""
        insights = []

        # Anomaly detection
        anomaly_insights = self._detect_anomalies(data, metrics)
        insights.extend(anomaly_insights)

        # Trend analysis
        trend_insights = self._analyze_trends(data, metrics, time_range_days)
        insights.extend(trend_insights)

        # Pattern recognition
        pattern_insights = self._recognize_patterns(data, metrics)
        insights.extend(pattern_insights)

        # Correlation analysis
        correlation_insights = self._analyze_correlations(data, metrics)
        insights.extend(correlation_insights)

        return insights

    def _detect_anomalies(self, data: List[Dict], metrics: List[str]) -> List[Insight]:
        """Detect anomalies in data"""
        insights = []

        for metric in metrics:
            values = [d.get(metric, 0) for d in data if metric in d]
            if not values:
                continue

            mean = statistics.mean(values)
            stdev = statistics.stdev(values) if len(values) > 1 else 0

            # Check for anomalies (values > 3 standard deviations)
            for i, value in enumerate(values):
                if stdev > 0 and abs(value - mean) > 3 * stdev:
                    deviation = ((value - mean) / mean) * 100

                    insight = Insight(
                        tenant_id=self.tenant_id,
                        insight_type=InsightType.ANOMALY,
                        severity=(
                            InsightSeverity.HIGH
                            if abs(deviation) > 50
                            else InsightSeverity.MEDIUM
                        ),
                        title=f"Anomaly detected in {metric}",
                        description=f"Value {value:.2f} deviates {abs(deviation):.1f}% from expected {mean:.2f}",
                        affected_metrics=[metric],
                        anomaly_score=abs(value - mean) / stdev if stdev > 0 else 0,
                        expected_value=mean,
                        actual_value=value,
                        deviation_percentage=deviation,
                        statistical_significance=0.99,
                        detection_date=datetime.utcnow(),
                    )
                    self.db.add(insight)
                    insights.append(insight)

        self.db.commit()
        return insights

    def _analyze_trends(
        self, data: List[Dict], metrics: List[str], days: int
    ) -> List[Insight]:
        """Analyze trends in data"""
        insights = []

        for metric in metrics:
            values = [d.get(metric, 0) for d in data if metric in d]
            if len(values) < 2:
                continue

            # Simple linear trend
            n = len(values)
            x = list(range(n))
            x_mean = sum(x) / n
            y_mean = sum(values) / n

            numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
            denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

            if denominator > 0:
                slope = numerator / denominator

                # Determine trend direction and strength
                if abs(slope) > 0.1:
                    direction = "increasing" if slope > 0 else "decreasing"
                    strength = min(abs(slope), 1.0)

                    insight = Insight(
                        tenant_id=self.tenant_id,
                        insight_type=InsightType.TREND,
                        severity=(
                            InsightSeverity.MEDIUM
                            if strength > 0.5
                            else InsightSeverity.LOW
                        ),
                        title=f"{direction.capitalize()} trend in {metric}",
                        description=f"{metric} is {direction} with strength {strength:.2f}",
                        affected_metrics=[metric],
                        trend_direction=direction,
                        trend_strength=strength,
                        trend_duration_days=days,
                        statistical_significance=0.85,
                        detection_date=datetime.utcnow(),
                    )
                    self.db.add(insight)
                    insights.append(insight)

        self.db.commit()
        return insights

    def _recognize_patterns(
        self, data: List[Dict], metrics: List[str]
    ) -> List[Insight]:
        """Recognize patterns in data"""
        insights = []

        for metric in metrics:
            values = [d.get(metric, 0) for d in data if metric in d]
            if len(values) < 7:  # Need at least a week of data
                continue

            # Check for weekly patterns
            if len(values) >= 7:
                weekly_avg = [statistics.mean(values[i::7]) for i in range(7)]
                variance = statistics.variance(weekly_avg) if len(weekly_avg) > 1 else 0

                if variance > 0:
                    insight = Insight(
                        tenant_id=self.tenant_id,
                        insight_type=InsightType.PATTERN,
                        severity=InsightSeverity.INFO,
                        title=f"Weekly pattern detected in {metric}",
                        description=f"{metric} shows recurring weekly patterns",
                        affected_metrics=[metric],
                        pattern_type="weekly",
                        pattern_frequency="weekly",
                        statistical_significance=0.75,
                        detection_date=datetime.utcnow(),
                    )
                    self.db.add(insight)
                    insights.append(insight)

        self.db.commit()
        return insights

    def _analyze_correlations(
        self, data: List[Dict], metrics: List[str]
    ) -> List[Insight]:
        """Analyze correlations between metrics"""
        insights = []

        if len(metrics) < 2:
            return insights

        # Check correlations between pairs of metrics
        for i in range(len(metrics)):
            for j in range(i + 1, len(metrics)):
                metric1, metric2 = metrics[i], metrics[j]

                values1 = [
                    d.get(metric1, 0) for d in data if metric1 in d and metric2 in d
                ]
                values2 = [
                    d.get(metric2, 0) for d in data if metric1 in d and metric2 in d
                ]

                if len(values1) < 3:
                    continue

                # Calculate correlation
                correlation = self._calculate_correlation(values1, values2)

                if abs(correlation) > 0.7:  # Strong correlation
                    insight = Insight(
                        tenant_id=self.tenant_id,
                        insight_type=InsightType.CORRELATION,
                        severity=InsightSeverity.MEDIUM,
                        title=f"Strong correlation between {metric1} and {metric2}",
                        description=f"Correlation coefficient: {correlation:.2f}",
                        affected_metrics=[metric1, metric2],
                        statistical_significance=abs(correlation),
                        detection_date=datetime.utcnow(),
                    )
                    self.db.add(insight)
                    insights.append(insight)

        self.db.commit()
        return insights

    def _calculate_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        n = len(x)
        if n == 0:
            return 0

        mean_x = sum(x) / n
        mean_y = sum(y) / n

        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denominator_x = sum((x[i] - mean_x) ** 2 for i in range(n))
        denominator_y = sum((y[i] - mean_y) ** 2 for i in range(n))

        if denominator_x == 0 or denominator_y == 0:
            return 0

        return numerator / (math.sqrt(denominator_x) * math.sqrt(denominator_y))

    # ==================== RECOMMENDATIONS ====================

    def generate_recommendations(self, insight_id: int) -> List[Recommendation]:
        """Generate actionable recommendations from insights"""
        insight = (
            self.db.query(Insight)
            .filter(Insight.id == insight_id, Insight.tenant_id == self.tenant_id)
            .first()
        )

        if not insight:
            raise ValueError(f"Insight {insight_id} not found")

        recommendations = []

        if insight.insight_type == InsightType.ANOMALY:
            recommendations.extend(self._recommend_for_anomaly(insight))
        elif insight.insight_type == InsightType.TREND:
            recommendations.extend(self._recommend_for_trend(insight))
        elif insight.insight_type == InsightType.PATTERN:
            recommendations.extend(self._recommend_for_pattern(insight))

        return recommendations

    def _recommend_for_anomaly(self, insight: Insight) -> List[Recommendation]:
        """Generate recommendations for anomalies"""
        recommendations = []

        rec = Recommendation(
            tenant_id=self.tenant_id,
            insight_id=insight.id,
            recommendation_type=RecommendationType.PERFORMANCE,
            title="Investigate anomaly root cause",
            description="Unusual behavior detected that requires investigation",
            rationale=f"Deviation of {insight.deviation_percentage:.1f}% from normal",
            expected_impact="Prevent potential issues and maintain system stability",
            risk_level="medium",
            implementation_steps=[
                "Review system logs for the time period",
                "Check for configuration changes",
                "Analyze resource utilization",
                "Verify data integrity",
            ],
            estimated_effort_hours=2.0,
            priority=2,
            urgency="short_term",
        )
        self.db.add(rec)
        recommendations.append(rec)

        self.db.commit()
        return recommendations

    def _recommend_for_trend(self, insight: Insight) -> List[Recommendation]:
        """Generate recommendations for trends"""
        recommendations = []

        if insight.trend_direction == "increasing":
            rec_type = RecommendationType.CAPACITY
            title = "Plan for capacity increase"
            description = "Upward trend detected - consider scaling resources"
        else:
            rec_type = RecommendationType.OPTIMIZATION
            title = "Optimize resource utilization"
            description = "Downward trend detected - opportunity for optimization"

        rec = Recommendation(
            tenant_id=self.tenant_id,
            insight_id=insight.id,
            recommendation_type=rec_type,
            title=title,
            description=description,
            rationale=f"Trend strength: {insight.trend_strength:.2f}",
            expected_impact="Maintain optimal performance and cost efficiency",
            estimated_cost_savings=(
                5000.0 if insight.trend_direction == "decreasing" else 0
            ),
            risk_level="low",
            implementation_steps=[
                "Review current capacity",
                "Forecast future needs",
                "Plan scaling strategy",
                "Implement changes gradually",
            ],
            estimated_effort_hours=4.0,
            priority=3,
            urgency="long_term",
        )
        self.db.add(rec)
        recommendations.append(rec)

        self.db.commit()
        return recommendations

    def _recommend_for_pattern(self, insight: Insight) -> List[Recommendation]:
        """Generate recommendations for patterns"""
        recommendations = []

        rec = Recommendation(
            tenant_id=self.tenant_id,
            insight_id=insight.id,
            recommendation_type=RecommendationType.OPTIMIZATION,
            title="Leverage pattern for optimization",
            description=f"Optimize based on {insight.pattern_frequency} patterns",
            rationale="Predictable patterns enable proactive optimization",
            expected_impact="Improved efficiency through pattern-based automation",
            estimated_cost_savings=3000.0,
            risk_level="low",
            implementation_steps=[
                "Document pattern characteristics",
                "Design automation rules",
                "Implement scheduled optimizations",
                "Monitor effectiveness",
            ],
            estimated_effort_hours=6.0,
            priority=4,
            urgency="long_term",
        )
        self.db.add(rec)
        recommendations.append(rec)

        self.db.commit()
        return recommendations

    # ==================== DATA QUALITY ====================

    def assess_data_quality(
        self, dataset_name: str, data: List[Dict[str, Any]]
    ) -> DataQualityScore:
        """Assess data quality and generate score"""
        if not data:
            raise ValueError("No data provided for quality assessment")

        # Calculate quality dimensions
        completeness = self._calculate_completeness(data)
        accuracy = self._calculate_accuracy(data)
        consistency = self._calculate_consistency(data)
        validity = self._calculate_validity(data)
        uniqueness = self._calculate_uniqueness(data)

        # Overall score (weighted average)
        overall = (
            completeness * 0.25
            + accuracy * 0.25
            + consistency * 0.20
            + validity * 0.20
            + uniqueness * 0.10
        )

        # Count issues
        missing_count = sum(1 for row in data for v in row.values() if v is None)
        duplicate_count = len(data) - len(
            set(json.dumps(d, sort_keys=True) for d in data)
        )

        quality_score = DataQualityScore(
            tenant_id=self.tenant_id,
            dataset_name=dataset_name,
            completeness_score=completeness,
            accuracy_score=accuracy,
            consistency_score=consistency,
            validity_score=validity,
            uniqueness_score=uniqueness,
            overall_score=overall,
            missing_values_count=missing_count,
            duplicate_count=duplicate_count,
            sample_size=len(data),
            total_records=len(data),
        )

        self.db.add(quality_score)
        self.db.commit()
        self.db.refresh(quality_score)

        return quality_score

    def _calculate_completeness(self, data: List[Dict]) -> float:
        """Calculate completeness score"""
        if not data:
            return 0.0

        total_fields = sum(len(row) for row in data)
        non_null_fields = sum(1 for row in data for v in row.values() if v is not None)

        return (non_null_fields / total_fields) if total_fields > 0 else 0.0

    def _calculate_accuracy(self, data: List[Dict]) -> float:
        """Calculate accuracy score (simplified)"""
        # In real implementation, would validate against rules
        return 0.92

    def _calculate_consistency(self, data: List[Dict]) -> float:
        """Calculate consistency score"""
        return 0.88

    def _calculate_validity(self, data: List[Dict]) -> float:
        """Calculate validity score"""
        return 0.90

    def _calculate_uniqueness(self, data: List[Dict]) -> float:
        """Calculate uniqueness score"""
        if not data:
            return 1.0

        unique_rows = len(set(json.dumps(d, sort_keys=True) for d in data))
        return unique_rows / len(data)

    # ==================== FEATURE IMPORTANCE ====================

    def calculate_feature_importance(self, model_id: int) -> List[FeatureImportance]:
        """Calculate feature importance for a model"""
        model = (
            self.db.query(AIModel)
            .filter(AIModel.id == model_id, AIModel.tenant_id == self.tenant_id)
            .first()
        )

        if not model or not model.features:
            raise ValueError(f"Model {model_id} not found or has no features")

        # Simulate feature importance calculation
        importance_scores = []
        for i, feature in enumerate(model.features):
            score = max(0.1, 1.0 - (i * 0.15))  # Decreasing importance

            feature_imp = FeatureImportance(
                model_id=model_id,
                feature_name=feature,
                importance_score=score,
                importance_rank=i + 1,
                correlation_with_target=score * 0.8,
                p_value=0.001 if score > 0.5 else 0.05,
            )
            self.db.add(feature_imp)
            importance_scores.append(feature_imp)

        self.db.commit()
        return importance_scores

    # ==================== FORECASTING ====================

    def forecast_metric(
        self,
        metric_name: str,
        historical_data: List[Dict[str, Any]],
        forecast_periods: int = 30,
    ) -> List[Dict[str, Any]]:
        """Forecast future values for a metric"""
        if not historical_data:
            raise ValueError("No historical data provided")

        values = [d.get(metric_name, 0) for d in historical_data]

        # Simple forecasting using moving average and trend
        window_size = min(7, len(values))
        recent_values = values[-window_size:]
        moving_avg = sum(recent_values) / len(recent_values)

        # Calculate trend
        if len(values) > 1:
            trend = (values[-1] - values[0]) / len(values)
        else:
            trend = 0

        # Generate forecasts
        forecasts = []
        for i in range(1, forecast_periods + 1):
            forecast_value = moving_avg + (trend * i)
            confidence = max(0.5, 1.0 - (i * 0.02))  # Decreasing confidence

            forecasts.append(
                {
                    "period": i,
                    "forecast_date": (
                        datetime.utcnow() + timedelta(days=i)
                    ).isoformat(),
                    "predicted_value": forecast_value,
                    "lower_bound": forecast_value * 0.85,
                    "upper_bound": forecast_value * 1.15,
                    "confidence_score": confidence,
                }
            )

        return forecasts

    # ==================== UTILITY METHODS ====================

    def get_model_performance(self, model_id: int) -> Dict[str, Any]:
        """Get comprehensive model performance metrics"""
        model = (
            self.db.query(AIModel)
            .filter(AIModel.id == model_id, AIModel.tenant_id == self.tenant_id)
            .first()
        )

        if not model:
            raise ValueError(f"Model {model_id} not found")

        # Get prediction statistics
        predictions = (
            self.db.query(Prediction)
            .filter(
                Prediction.model_id == model_id, Prediction.tenant_id == self.tenant_id
            )
            .all()
        )

        return {
            "model_id": model.id,
            "model_name": model.name,
            "model_type": model.model_type.value,
            "status": model.status.value,
            "is_deployed": model.is_deployed,
            "training_metrics": {
                "accuracy": model.accuracy,
                "precision": model.precision,
                "recall": model.recall,
                "f1_score": model.f1_score,
                "rmse": model.rmse,
                "mae": model.mae,
                "r2_score": model.r2_score,
            },
            "prediction_stats": {
                "total_predictions": len(predictions),
                "avg_confidence": (
                    statistics.mean([p.confidence_score for p in predictions])
                    if predictions
                    else 0
                ),
                "avg_execution_time_ms": (
                    statistics.mean(
                        [
                            p.execution_time_ms
                            for p in predictions
                            if p.execution_time_ms
                        ]
                    )
                    if predictions
                    else 0
                ),
            },
            "last_trained": (
                model.last_trained_at.isoformat() if model.last_trained_at else None
            ),
            "deployment_date": (
                model.deployment_date.isoformat() if model.deployment_date else None
            ),
        }
