package predictor

import (
	"context"
	"fmt"
	"math"
	"sync"
	"time"

	"github.com/iteksmart/itechsmart-agent/internal/logger"
)

// Predictor handles failure prediction and forecasting
type Predictor struct {
	mu              sync.RWMutex
	historicalData  map[string][]DataPoint
	predictions     map[string]*Prediction
	config          *Config
	logger          *logger.Logger
	anomalyDetector *AnomalyDetector
}

// Config holds predictor configuration
type Config struct {
	HistoryWindow      time.Duration // How far back to look
	PredictionWindow   time.Duration // How far ahead to predict
	MinDataPoints      int           // Minimum data points for prediction
	ConfidenceLevel    float64       // Confidence level (0-1)
	AnomalyThreshold   float64       // Threshold for anomaly detection
	UpdateInterval     time.Duration // How often to update predictions
	EnableMLPrediction bool          // Enable ML-based prediction
}

// DataPoint represents a single metric data point
type DataPoint struct {
	Timestamp time.Time
	Value     float64
	Metadata  map[string]string
}

// Prediction represents a predicted future state
type Prediction struct {
	MetricName      string
	CurrentValue    float64
	PredictedValue  float64
	PredictedTime   time.Time
	Confidence      float64
	Trend           string // "increasing", "decreasing", "stable"
	RiskLevel       string // "low", "medium", "high", "critical"
	Recommendation  string
	FailureProbability float64
	TimeToFailure   *time.Duration
}

// AnomalyDetector detects anomalies in metrics
type AnomalyDetector struct {
	sensitivity float64
	windowSize  int
}

// New creates a new Predictor instance
func New(cfg *Config, log *logger.Logger) *Predictor {
	if cfg == nil {
		cfg = &Config{
			HistoryWindow:      24 * time.Hour,
			PredictionWindow:   4 * time.Hour,
			MinDataPoints:      10,
			ConfidenceLevel:    0.85,
			AnomalyThreshold:   2.0,
			UpdateInterval:     5 * time.Minute,
			EnableMLPrediction: true,
		}
	}

	return &Predictor{
		historicalData: make(map[string][]DataPoint),
		predictions:    make(map[string]*Prediction),
		config:         cfg,
		logger:         log,
		anomalyDetector: &AnomalyDetector{
			sensitivity: cfg.AnomalyThreshold,
			windowSize:  20,
		},
	}
}

// AddDataPoint adds a new data point for prediction
func (p *Predictor) AddDataPoint(metricName string, value float64, metadata map[string]string) {
	p.mu.Lock()
	defer p.mu.Unlock()

	dataPoint := DataPoint{
		Timestamp: time.Now(),
		Value:     value,
		Metadata:  metadata,
	}

	if _, exists := p.historicalData[metricName]; !exists {
		p.historicalData[metricName] = make([]DataPoint, 0)
	}

	p.historicalData[metricName] = append(p.historicalData[metricName], dataPoint)

	// Keep only data within history window
	cutoff := time.Now().Add(-p.config.HistoryWindow)
	filtered := make([]DataPoint, 0)
	for _, dp := range p.historicalData[metricName] {
		if dp.Timestamp.After(cutoff) {
			filtered = append(filtered, dp)
		}
	}
	p.historicalData[metricName] = filtered
}

// PredictFailure predicts potential failures
func (p *Predictor) PredictFailure(ctx context.Context, metricName string) (*Prediction, error) {
	p.mu.RLock()
	data, exists := p.historicalData[metricName]
	p.mu.RUnlock()

	if !exists || len(data) < p.config.MinDataPoints {
		return nil, fmt.Errorf("insufficient data for prediction: need at least %d points, have %d", 
			p.config.MinDataPoints, len(data))
	}

	// Calculate trend and prediction
	trend := p.calculateTrend(data)
	predictedValue := p.predictValue(data, p.config.PredictionWindow)
	confidence := p.calculateConfidence(data)
	
	// Detect anomalies
	isAnomaly := p.anomalyDetector.Detect(data)
	
	// Calculate failure probability
	failureProbability := p.calculateFailureProbability(data, predictedValue, metricName)
	
	// Estimate time to failure
	var timeToFailure *time.Duration
	if failureProbability > 0.5 {
		ttf := p.estimateTimeToFailure(data, metricName)
		timeToFailure = &ttf
	}

	// Determine risk level
	riskLevel := p.determineRiskLevel(failureProbability, predictedValue, metricName)
	
	// Generate recommendation
	recommendation := p.generateRecommendation(metricName, predictedValue, failureProbability, trend)

	prediction := &Prediction{
		MetricName:         metricName,
		CurrentValue:       data[len(data)-1].Value,
		PredictedValue:     predictedValue,
		PredictedTime:      time.Now().Add(p.config.PredictionWindow),
		Confidence:         confidence,
		Trend:              trend,
		RiskLevel:          riskLevel,
		Recommendation:     recommendation,
		FailureProbability: failureProbability,
		TimeToFailure:      timeToFailure,
	}

	// Store prediction
	p.mu.Lock()
	p.predictions[metricName] = prediction
	p.mu.Unlock()

	// Log if anomaly detected
	if isAnomaly {
		p.logger.Warn("Anomaly detected in metric", 
			"metric", metricName,
			"current_value", data[len(data)-1].Value,
			"predicted_value", predictedValue)
	}

	return prediction, nil
}

// calculateTrend determines the trend direction
func (p *Predictor) calculateTrend(data []DataPoint) string {
	if len(data) < 2 {
		return "stable"
	}

	// Calculate linear regression slope
	n := float64(len(data))
	var sumX, sumY, sumXY, sumX2 float64

	for i, dp := range data {
		x := float64(i)
		y := dp.Value
		sumX += x
		sumY += y
		sumXY += x * y
		sumX2 += x * x
	}

	slope := (n*sumXY - sumX*sumY) / (n*sumX2 - sumX*sumX)

	// Determine trend based on slope
	if math.Abs(slope) < 0.01 {
		return "stable"
	} else if slope > 0 {
		return "increasing"
	}
	return "decreasing"
}

// predictValue predicts future value using linear regression
func (p *Predictor) predictValue(data []DataPoint, window time.Duration) float64 {
	if len(data) < 2 {
		return data[len(data)-1].Value
	}

	// Simple linear regression
	n := float64(len(data))
	var sumX, sumY, sumXY, sumX2 float64

	for i, dp := range data {
		x := float64(i)
		y := dp.Value
		sumX += x
		sumY += y
		sumXY += x * y
		sumX2 += x * x
	}

	slope := (n*sumXY - sumX*sumY) / (n*sumX2 - sumX*sumX)
	intercept := (sumY - slope*sumX) / n

	// Predict for future point
	futureX := n + (window.Seconds() / 60) // Assuming 1-minute intervals
	predictedValue := slope*futureX + intercept

	// Ensure non-negative for percentage metrics
	if predictedValue < 0 {
		predictedValue = 0
	}
	if predictedValue > 100 && (data[0].Metadata["type"] == "percentage") {
		predictedValue = 100
	}

	return predictedValue
}

// calculateConfidence calculates prediction confidence
func (p *Predictor) calculateConfidence(data []DataPoint) float64 {
	if len(data) < p.config.MinDataPoints {
		return 0.0
	}

	// Calculate variance
	var sum, sumSq float64
	for _, dp := range data {
		sum += dp.Value
		sumSq += dp.Value * dp.Value
	}
	mean := sum / float64(len(data))
	variance := (sumSq / float64(len(data))) - (mean * mean)
	
	// Lower variance = higher confidence
	confidence := 1.0 / (1.0 + variance/100.0)
	
	// Adjust for data quantity
	dataFactor := float64(len(data)) / float64(p.config.MinDataPoints*2)
	if dataFactor > 1.0 {
		dataFactor = 1.0
	}
	
	return confidence * dataFactor
}

// calculateFailureProbability calculates probability of failure
func (p *Predictor) calculateFailureProbability(data []DataPoint, predictedValue float64, metricName string) float64 {
	// Define thresholds based on metric type
	var criticalThreshold float64
	switch metricName {
	case "cpu_usage", "memory_usage":
		criticalThreshold = 95.0
	case "disk_usage":
		criticalThreshold = 90.0
	case "network_errors":
		criticalThreshold = 100.0
	default:
		criticalThreshold = 90.0
	}

	// Calculate probability based on predicted value
	if predictedValue >= criticalThreshold {
		return 0.95
	} else if predictedValue >= criticalThreshold*0.9 {
		return 0.75
	} else if predictedValue >= criticalThreshold*0.8 {
		return 0.50
	} else if predictedValue >= criticalThreshold*0.7 {
		return 0.25
	}
	return 0.10
}

// estimateTimeToFailure estimates time until failure
func (p *Predictor) estimateTimeToFailure(data []DataPoint, metricName string) time.Duration {
	if len(data) < 2 {
		return 24 * time.Hour
	}

	// Calculate rate of change
	recent := data[len(data)-10:]
	if len(recent) < 2 {
		recent = data
	}

	var totalChange float64
	for i := 1; i < len(recent); i++ {
		totalChange += recent[i].Value - recent[i-1].Value
	}
	avgChange := totalChange / float64(len(recent)-1)

	if avgChange <= 0 {
		return 24 * time.Hour // Not increasing, no immediate failure
	}

	// Calculate time to reach critical threshold
	currentValue := data[len(data)-1].Value
	var criticalThreshold float64
	switch metricName {
	case "cpu_usage", "memory_usage":
		criticalThreshold = 95.0
	case "disk_usage":
		criticalThreshold = 90.0
	default:
		criticalThreshold = 90.0
	}

	remaining := criticalThreshold - currentValue
	if remaining <= 0 {
		return 1 * time.Hour
	}

	minutesToFailure := remaining / avgChange
	return time.Duration(minutesToFailure) * time.Minute
}

// determineRiskLevel determines risk level
func (p *Predictor) determineRiskLevel(probability, predictedValue float64, metricName string) string {
	if probability >= 0.75 || predictedValue >= 90 {
		return "critical"
	} else if probability >= 0.50 || predictedValue >= 80 {
		return "high"
	} else if probability >= 0.25 || predictedValue >= 70 {
		return "medium"
	}
	return "low"
}

// generateRecommendation generates actionable recommendation
func (p *Predictor) generateRecommendation(metricName string, predictedValue, probability float64, trend string) string {
	if probability < 0.25 {
		return "System is operating normally. Continue monitoring."
	}

	switch metricName {
	case "cpu_usage":
		if probability >= 0.75 {
			return "CRITICAL: CPU usage predicted to reach critical levels. Consider scaling up resources or optimizing workloads immediately."
		}
		return "WARNING: CPU usage trending upward. Review running processes and consider resource optimization."
	
	case "memory_usage":
		if probability >= 0.75 {
			return "CRITICAL: Memory exhaustion predicted. Increase RAM or identify memory leaks immediately."
		}
		return "WARNING: Memory usage increasing. Review application memory consumption and consider optimization."
	
	case "disk_usage":
		if probability >= 0.75 {
			return "CRITICAL: Disk space will be exhausted soon. Clean up unnecessary files or expand storage immediately."
		}
		return "WARNING: Disk usage growing. Schedule cleanup or storage expansion."
	
	default:
		if probability >= 0.75 {
			return fmt.Sprintf("CRITICAL: %s predicted to reach critical levels. Immediate action required.", metricName)
		}
		return fmt.Sprintf("WARNING: %s trending toward critical levels. Monitor closely and plan remediation.", metricName)
	}
}

// Detect detects anomalies in data
func (ad *AnomalyDetector) Detect(data []DataPoint) bool {
	if len(data) < ad.windowSize {
		return false
	}

	// Use recent window
	window := data[len(data)-ad.windowSize:]
	
	// Calculate mean and standard deviation
	var sum, sumSq float64
	for _, dp := range window {
		sum += dp.Value
		sumSq += dp.Value * dp.Value
	}
	mean := sum / float64(len(window))
	variance := (sumSq / float64(len(window))) - (mean * mean)
	stdDev := math.Sqrt(variance)

	// Check if latest value is anomalous
	latest := data[len(data)-1].Value
	zScore := math.Abs((latest - mean) / stdDev)

	return zScore > ad.sensitivity
}

// GetPrediction retrieves a stored prediction
func (p *Predictor) GetPrediction(metricName string) (*Prediction, bool) {
	p.mu.RLock()
	defer p.mu.RUnlock()
	
	pred, exists := p.predictions[metricName]
	return pred, exists
}

// GetAllPredictions retrieves all stored predictions
func (p *Predictor) GetAllPredictions() map[string]*Prediction {
	p.mu.RLock()
	defer p.mu.RUnlock()
	
	// Create a copy to avoid race conditions
	predictions := make(map[string]*Prediction)
	for k, v := range p.predictions {
		predictions[k] = v
	}
	return predictions
}

// Start starts the predictor background tasks
func (p *Predictor) Start(ctx context.Context) error {
	p.logger.Info("Starting predictor service")
	
	ticker := time.NewTicker(p.config.UpdateInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			p.logger.Info("Stopping predictor service")
			return ctx.Err()
		case <-ticker.C:
			p.updatePredictions(ctx)
		}
	}
}

// updatePredictions updates all predictions
func (p *Predictor) updatePredictions(ctx context.Context) {
	p.mu.RLock()
	metrics := make([]string, 0, len(p.historicalData))
	for metric := range p.historicalData {
		metrics = append(metrics, metric)
	}
	p.mu.RUnlock()

	for _, metric := range metrics {
		if _, err := p.PredictFailure(ctx, metric); err != nil {
			p.logger.Error("Failed to update prediction", "metric", metric, "error", err)
		}
	}
}

// GetHistoricalData retrieves historical data for a metric
func (p *Predictor) GetHistoricalData(metricName string) []DataPoint {
	p.mu.RLock()
	defer p.mu.RUnlock()
	
	data, exists := p.historicalData[metricName]
	if !exists {
		return nil
	}
	
	// Return a copy
	result := make([]DataPoint, len(data))
	copy(result, data)
	return result
}

// ClearHistory clears historical data for a metric
func (p *Predictor) ClearHistory(metricName string) {
	p.mu.Lock()
	defer p.mu.Unlock()
	
	delete(p.historicalData, metricName)
	delete(p.predictions, metricName)
}