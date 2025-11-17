package capacity

import (
	"context"
	"fmt"
	"math"
	"sync"
	"time"

	"github.com/iteksmart/itechsmart-agent/internal/logger"
)

// Planner handles capacity planning and forecasting
type Planner struct {
	mu              sync.RWMutex
	historicalData  map[string][]Measurement
	forecasts       map[string]*Forecast
	config          *Config
	logger          *logger.Logger
	trendAnalyzer   *TrendAnalyzer
}

// Config holds capacity planner configuration
type Config struct {
	ForecastWindow     time.Duration // How far ahead to forecast
	HistoryWindow      time.Duration // How much history to analyze
	MinDataPoints      int           // Minimum data points for forecasting
	GrowthThreshold    float64       // Threshold for growth alerts
	UpdateInterval     time.Duration // How often to update forecasts
	EnableAlerts       bool          // Enable capacity alerts
}

// Measurement represents a capacity measurement
type Measurement struct {
	Timestamp time.Time
	Value     float64
	Capacity  float64 // Total capacity
	Usage     float64 // Usage percentage
	Metadata  map[string]string
}

// Forecast represents a capacity forecast
type Forecast struct {
	ResourceName       string
	CurrentUsage       float64
	CurrentCapacity    float64
	ForecastedUsage    float64
	ForecastedCapacity float64
	ForecastTime       time.Time
	GrowthRate         float64 // Percentage per day
	TimeToExhaustion   *time.Duration
	RecommendedAction  string
	Confidence         float64
	Trend              string // "linear", "exponential", "seasonal"
	Alerts             []CapacityAlert
}

// CapacityAlert represents a capacity alert
type CapacityAlert struct {
	Severity    string // "info", "warning", "critical"
	Message     string
	Threshold   float64
	CurrentValue float64
	Timestamp   time.Time
}

// TrendAnalyzer analyzes trends in capacity data
type TrendAnalyzer struct {
	logger *logger.Logger
}

// CapacityReport represents a comprehensive capacity report
type CapacityReport struct {
	GeneratedAt    time.Time
	ReportPeriod   time.Duration
	Resources      []ResourceSummary
	Recommendations []string
	TotalScore     float64 // 0-100, health score
}

// ResourceSummary summarizes capacity for a resource
type ResourceSummary struct {
	Name              string
	CurrentUsage      float64
	CurrentCapacity   float64
	UtilizationRate   float64
	GrowthRate        float64
	TimeToExhaustion  *time.Duration
	Status            string // "healthy", "warning", "critical"
	Recommendation    string
}

// New creates a new capacity Planner instance
func New(cfg *Config, log *logger.Logger) *Planner {
	if cfg == nil {
		cfg = &Config{
			ForecastWindow:  30 * 24 * time.Hour, // 30 days
			HistoryWindow:   90 * 24 * time.Hour, // 90 days
			MinDataPoints:   20,
			GrowthThreshold: 10.0, // 10% growth threshold
			UpdateInterval:  1 * time.Hour,
			EnableAlerts:    true,
		}
	}

	return &Planner{
		historicalData: make(map[string][]Measurement),
		forecasts:      make(map[string]*Forecast),
		config:         cfg,
		logger:         log,
		trendAnalyzer: &TrendAnalyzer{
			logger: log,
		},
	}
}

// AddMeasurement adds a new capacity measurement
func (p *Planner) AddMeasurement(resourceName string, value, capacity float64, metadata map[string]string) {
	p.mu.Lock()
	defer p.mu.Unlock()

	usage := (value / capacity) * 100.0
	if usage > 100.0 {
		usage = 100.0
	}

	measurement := Measurement{
		Timestamp: time.Now(),
		Value:     value,
		Capacity:  capacity,
		Usage:     usage,
		Metadata:  metadata,
	}

	if _, exists := p.historicalData[resourceName]; !exists {
		p.historicalData[resourceName] = make([]Measurement, 0)
	}

	p.historicalData[resourceName] = append(p.historicalData[resourceName], measurement)

	// Keep only data within history window
	cutoff := time.Now().Add(-p.config.HistoryWindow)
	filtered := make([]Measurement, 0)
	for _, m := range p.historicalData[resourceName] {
		if m.Timestamp.After(cutoff) {
			filtered = append(filtered, m)
		}
	}
	p.historicalData[resourceName] = filtered
}

// ForecastCapacity forecasts future capacity needs
func (p *Planner) ForecastCapacity(ctx context.Context, resourceName string) (*Forecast, error) {
	p.mu.RLock()
	data, exists := p.historicalData[resourceName]
	p.mu.RUnlock()

	if !exists || len(data) < p.config.MinDataPoints {
		return nil, fmt.Errorf("insufficient data for forecasting: need at least %d points, have %d",
			p.config.MinDataPoints, len(data))
	}

	// Analyze trend
	trend := p.trendAnalyzer.AnalyzeTrend(data)
	
	// Calculate growth rate
	growthRate := p.calculateGrowthRate(data)
	
	// Forecast future usage
	forecastedUsage := p.forecastUsage(data, p.config.ForecastWindow, trend)
	
	// Calculate confidence
	confidence := p.calculateConfidence(data, trend)
	
	// Estimate time to exhaustion
	var timeToExhaustion *time.Duration
	if growthRate > 0 {
		tte := p.estimateTimeToExhaustion(data, growthRate)
		timeToExhaustion = &tte
	}
	
	// Generate alerts
	alerts := p.generateAlerts(resourceName, data[len(data)-1].Usage, forecastedUsage, timeToExhaustion)
	
	// Generate recommendation
	recommendation := p.generateRecommendation(resourceName, data[len(data)-1].Usage, forecastedUsage, growthRate, timeToExhaustion)

	forecast := &Forecast{
		ResourceName:       resourceName,
		CurrentUsage:       data[len(data)-1].Value,
		CurrentCapacity:    data[len(data)-1].Capacity,
		ForecastedUsage:    forecastedUsage,
		ForecastedCapacity: data[len(data)-1].Capacity, // Assume capacity stays same
		ForecastTime:       time.Now().Add(p.config.ForecastWindow),
		GrowthRate:         growthRate,
		TimeToExhaustion:   timeToExhaustion,
		RecommendedAction:  recommendation,
		Confidence:         confidence,
		Trend:              trend,
		Alerts:             alerts,
	}

	// Store forecast
	p.mu.Lock()
	p.forecasts[resourceName] = forecast
	p.mu.Unlock()

	return forecast, nil
}

// AnalyzeTrend analyzes the trend in measurements
func (ta *TrendAnalyzer) AnalyzeTrend(data []Measurement) string {
	if len(data) < 10 {
		return "linear"
	}

	// Calculate linear regression
	n := float64(len(data))
	var sumX, sumY, sumXY, sumX2 float64

	for i, m := range data {
		x := float64(i)
		y := m.Usage
		sumX += x
		sumY += y
		sumXY += x * y
		sumX2 += x * x
	}

	slope := (n*sumXY - sumX*sumY) / (n*sumX2 - sumX*sumX)

	// Check for exponential growth
	if slope > 0.5 {
		// Calculate exponential fit
		var sumLogY, sumXLogY float64
		for i, m := range data {
			if m.Usage > 0 {
				x := float64(i)
				logY := math.Log(m.Usage)
				sumLogY += logY
				sumXLogY += x * logY
			}
		}
		
		expSlope := (n*sumXLogY - sumX*sumLogY) / (n*sumX2 - sumX*sumX)
		
		if expSlope > slope*1.5 {
			return "exponential"
		}
	}

	// Check for seasonal patterns (simplified)
	if len(data) >= 30 {
		// Look for weekly patterns
		weeklyVariance := ta.calculateWeeklyVariance(data)
		overallVariance := ta.calculateVariance(data)
		
		if weeklyVariance < overallVariance*0.7 {
			return "seasonal"
		}
	}

	return "linear"
}

// calculateWeeklyVariance calculates variance in weekly patterns
func (ta *TrendAnalyzer) calculateWeeklyVariance(data []Measurement) float64 {
	if len(data) < 14 {
		return 0
	}

	// Group by day of week
	weeklyData := make(map[time.Weekday][]float64)
	for _, m := range data {
		weekday := m.Timestamp.Weekday()
		weeklyData[weekday] = append(weeklyData[weekday], m.Usage)
	}

	// Calculate variance for each day
	var totalVariance float64
	count := 0
	for _, values := range weeklyData {
		if len(values) > 1 {
			variance := ta.calculateVarianceFromValues(values)
			totalVariance += variance
			count++
		}
	}

	if count == 0 {
		return 0
	}

	return totalVariance / float64(count)
}

// calculateVariance calculates overall variance
func (ta *TrendAnalyzer) calculateVariance(data []Measurement) float64 {
	if len(data) < 2 {
		return 0
	}

	values := make([]float64, len(data))
	for i, m := range data {
		values[i] = m.Usage
	}

	return ta.calculateVarianceFromValues(values)
}

// calculateVarianceFromValues calculates variance from values
func (ta *TrendAnalyzer) calculateVarianceFromValues(values []float64) float64 {
	if len(values) < 2 {
		return 0
	}

	var sum, sumSq float64
	for _, v := range values {
		sum += v
		sumSq += v * v
	}

	mean := sum / float64(len(values))
	variance := (sumSq / float64(len(values))) - (mean * mean)

	return variance
}

// calculateGrowthRate calculates the growth rate
func (p *Planner) calculateGrowthRate(data []Measurement) float64 {
	if len(data) < 2 {
		return 0
	}

	// Use recent data for growth rate
	recentWindow := 30 // Last 30 measurements
	if len(data) < recentWindow {
		recentWindow = len(data)
	}

	recent := data[len(data)-recentWindow:]
	
	// Calculate linear regression slope
	n := float64(len(recent))
	var sumX, sumY, sumXY, sumX2 float64

	for i, m := range recent {
		x := float64(i)
		y := m.Usage
		sumX += x
		sumY += y
		sumXY += x * y
		sumX2 += x * x
	}

	slope := (n*sumXY - sumX*sumY) / (n*sumX2 - sumX*sumX)

	// Convert to percentage per day
	// Assuming measurements are hourly
	growthRatePerDay := slope * 24.0

	return growthRatePerDay
}

// forecastUsage forecasts future usage
func (p *Planner) forecastUsage(data []Measurement, window time.Duration, trend string) float64 {
	if len(data) < 2 {
		return data[len(data)-1].Usage
	}

	currentUsage := data[len(data)-1].Usage
	growthRate := p.calculateGrowthRate(data)
	
	days := window.Hours() / 24.0

	switch trend {
	case "exponential":
		// Exponential growth: y = a * e^(bx)
		return currentUsage * math.Exp(growthRate*days/100.0)
	
	case "seasonal":
		// Use average growth with seasonal adjustment
		baseGrowth := currentUsage + (growthRate * days)
		// Simplified seasonal adjustment
		return baseGrowth * 1.1 // 10% seasonal buffer
	
	default: // linear
		return currentUsage + (growthRate * days)
	}
}

// calculateConfidence calculates forecast confidence
func (p *Planner) calculateConfidence(data []Measurement, trend string) float64 {
	if len(data) < p.config.MinDataPoints {
		return 0.0
	}

	// Base confidence on data quantity
	dataFactor := float64(len(data)) / float64(p.config.MinDataPoints*3)
	if dataFactor > 1.0 {
		dataFactor = 1.0
	}

	// Adjust for variance
	variance := p.trendAnalyzer.calculateVariance(data)
	varianceFactor := 1.0 / (1.0 + variance/100.0)

	// Adjust for trend type
	trendFactor := 1.0
	switch trend {
	case "linear":
		trendFactor = 0.9
	case "exponential":
		trendFactor = 0.7
	case "seasonal":
		trendFactor = 0.8
	}

	confidence := dataFactor * varianceFactor * trendFactor

	return confidence
}

// estimateTimeToExhaustion estimates time until capacity exhaustion
func (p *Planner) estimateTimeToExhaustion(data []Measurement, growthRate float64) time.Duration {
	if growthRate <= 0 {
		return 365 * 24 * time.Hour // 1 year if not growing
	}

	currentUsage := data[len(data)-1].Usage
	remaining := 100.0 - currentUsage

	if remaining <= 0 {
		return 0
	}

	daysToExhaustion := remaining / growthRate
	return time.Duration(daysToExhaustion*24) * time.Hour
}

// generateAlerts generates capacity alerts
func (p *Planner) generateAlerts(resourceName string, currentUsage, forecastedUsage float64, tte *time.Duration) []CapacityAlert {
	alerts := make([]CapacityAlert, 0)

	// Current usage alerts
	if currentUsage >= 90 {
		alerts = append(alerts, CapacityAlert{
			Severity:     "critical",
			Message:      fmt.Sprintf("%s is at critical capacity (%.1f%%)", resourceName, currentUsage),
			Threshold:    90.0,
			CurrentValue: currentUsage,
			Timestamp:    time.Now(),
		})
	} else if currentUsage >= 80 {
		alerts = append(alerts, CapacityAlert{
			Severity:     "warning",
			Message:      fmt.Sprintf("%s is approaching capacity limit (%.1f%%)", resourceName, currentUsage),
			Threshold:    80.0,
			CurrentValue: currentUsage,
			Timestamp:    time.Now(),
		})
	}

	// Forecasted usage alerts
	if forecastedUsage >= 90 {
		alerts = append(alerts, CapacityAlert{
			Severity:     "warning",
			Message:      fmt.Sprintf("%s forecasted to reach critical capacity (%.1f%%) in %s", resourceName, forecastedUsage, p.config.ForecastWindow),
			Threshold:    90.0,
			CurrentValue: forecastedUsage,
			Timestamp:    time.Now(),
		})
	}

	// Time to exhaustion alerts
	if tte != nil && *tte < 30*24*time.Hour {
		severity := "warning"
		if *tte < 7*24*time.Hour {
			severity = "critical"
		}
		
		alerts = append(alerts, CapacityAlert{
			Severity:     severity,
			Message:      fmt.Sprintf("%s will exhaust capacity in approximately %s", resourceName, tte.String()),
			Threshold:    100.0,
			CurrentValue: currentUsage,
			Timestamp:    time.Now(),
		})
	}

	return alerts
}

// generateRecommendation generates capacity recommendation
func (p *Planner) generateRecommendation(resourceName string, currentUsage, forecastedUsage, growthRate float64, tte *time.Duration) string {
	if currentUsage < 70 && forecastedUsage < 80 {
		return fmt.Sprintf("%s capacity is healthy. Continue monitoring.", resourceName)
	}

	if currentUsage >= 90 {
		return fmt.Sprintf("URGENT: %s is at critical capacity. Immediate expansion required.", resourceName)
	}

	if forecastedUsage >= 90 {
		return fmt.Sprintf("Plan capacity expansion for %s within %s to avoid exhaustion.", resourceName, p.config.ForecastWindow)
	}

	if tte != nil && *tte < 30*24*time.Hour {
		return fmt.Sprintf("Schedule capacity expansion for %s within the next 30 days (estimated exhaustion in %s).", resourceName, tte.String())
	}

	if growthRate > p.config.GrowthThreshold {
		return fmt.Sprintf("%s is growing rapidly (%.1f%% per day). Monitor closely and plan for expansion.", resourceName, growthRate)
	}

	return fmt.Sprintf("%s capacity is adequate. Review in %s.", resourceName, p.config.ForecastWindow)
}

// GenerateReport generates a comprehensive capacity report
func (p *Planner) GenerateReport(ctx context.Context) (*CapacityReport, error) {
	p.mu.RLock()
	resources := make([]string, 0, len(p.historicalData))
	for resource := range p.historicalData {
		resources = append(resources, resource)
	}
	p.mu.RUnlock()

	report := &CapacityReport{
		GeneratedAt:     time.Now(),
		ReportPeriod:    p.config.ForecastWindow,
		Resources:       make([]ResourceSummary, 0),
		Recommendations: make([]string, 0),
	}

	var totalScore float64
	validResources := 0

	for _, resource := range resources {
		forecast, err := p.ForecastCapacity(ctx, resource)
		if err != nil {
			p.logger.Error("Failed to forecast capacity", "resource", resource, "error", err)
			continue
		}

		status := "healthy"
		if forecast.CurrentUsage >= 90 {
			status = "critical"
		} else if forecast.CurrentUsage >= 80 {
			status = "warning"
		}

		summary := ResourceSummary{
			Name:             resource,
			CurrentUsage:     forecast.CurrentUsage,
			CurrentCapacity:  forecast.CurrentCapacity,
			UtilizationRate:  (forecast.CurrentUsage / forecast.CurrentCapacity) * 100,
			GrowthRate:       forecast.GrowthRate,
			TimeToExhaustion: forecast.TimeToExhaustion,
			Status:           status,
			Recommendation:   forecast.RecommendedAction,
		}

		report.Resources = append(report.Resources, summary)

		// Calculate health score (100 = healthy, 0 = critical)
		healthScore := 100.0 - summary.UtilizationRate
		if healthScore < 0 {
			healthScore = 0
		}
		totalScore += healthScore
		validResources++

		// Add to recommendations if needed
		if status != "healthy" {
			report.Recommendations = append(report.Recommendations, summary.Recommendation)
		}
	}

	if validResources > 0 {
		report.TotalScore = totalScore / float64(validResources)
	}

	return report, nil
}

// GetForecast retrieves a stored forecast
func (p *Planner) GetForecast(resourceName string) (*Forecast, bool) {
	p.mu.RLock()
	defer p.mu.RUnlock()

	forecast, exists := p.forecasts[resourceName]
	return forecast, exists
}

// GetAllForecasts retrieves all stored forecasts
func (p *Planner) GetAllForecasts() map[string]*Forecast {
	p.mu.RLock()
	defer p.mu.RUnlock()

	forecasts := make(map[string]*Forecast)
	for k, v := range p.forecasts {
		forecasts[k] = v
	}
	return forecasts
}

// Start starts the capacity planner background tasks
func (p *Planner) Start(ctx context.Context) error {
	p.logger.Info("Starting capacity planner service")

	ticker := time.NewTicker(p.config.UpdateInterval)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			p.logger.Info("Stopping capacity planner service")
			return ctx.Err()
		case <-ticker.C:
			p.updateForecasts(ctx)
		}
	}
}

// updateForecasts updates all capacity forecasts
func (p *Planner) updateForecasts(ctx context.Context) {
	p.mu.RLock()
	resources := make([]string, 0, len(p.historicalData))
	for resource := range p.historicalData {
		resources = append(resources, resource)
	}
	p.mu.RUnlock()

	for _, resource := range resources {
		if _, err := p.ForecastCapacity(ctx, resource); err != nil {
			p.logger.Error("Failed to update forecast", "resource", resource, "error", err)
		}
	}
}