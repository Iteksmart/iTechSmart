package agent

import (
	"context"
	"fmt"
	"time"

	"github.com/iteksmart/itechsmart-agent/internal/capacity"
	"github.com/iteksmart/itechsmart-agent/internal/collector"
	"github.com/iteksmart/itechsmart-agent/internal/communicator"
	"github.com/iteksmart/itechsmart-agent/internal/config"
	"github.com/iteksmart/itechsmart-agent/internal/executor"
	"github.com/iteksmart/itechsmart-agent/internal/logger"
	"github.com/iteksmart/itechsmart-agent/internal/predictor"
	"github.com/iteksmart/itechsmart-agent/internal/remediator"
)

// Agent represents the main agent
type Agent struct {
	cfg               *config.Config
	log               *logger.Logger
	comm              *communicator.Communicator
	exec              *executor.Executor
	systemCollector   *collector.SystemCollector
	securityCollector *collector.SecurityCollector
	softwareCollector *collector.SoftwareCollector
	predictor         *predictor.Predictor
	remediator        *remediator.Remediator
	capacityPlanner   *capacity.Planner
	ctx               context.Context
	cancel            context.CancelFunc
}

// New creates a new agent instance
func New(cfg *config.Config, log *logger.Logger) (*Agent, error) {
	ctx, cancel := context.WithCancel(context.Background())
	
	// Create communicator
	comm := communicator.NewCommunicator(cfg, log)
	
	// Create executor
	exec := executor.NewExecutor(cfg, log, comm)
	
	// Create collectors
	systemCollector := collector.NewSystemCollector()
	securityCollector := collector.NewSecurityCollector()
	softwareCollector := collector.NewSoftwareCollector()
	
	// Create predictor with configuration
	predictorCfg := &predictor.Config{
		HistoryWindow:      24 * time.Hour,
		PredictionWindow:   4 * time.Hour,
		MinDataPoints:      10,
		ConfidenceLevel:    0.85,
		AnomalyThreshold:   2.0,
		UpdateInterval:     5 * time.Minute,
		EnableMLPrediction: true,
	}
	pred := predictor.New(predictorCfg, log)
	
	// Create remediator with configuration
	remediatorCfg := &remediator.Config{
		EnableAutoRemediation: true,
		MaxRetries:            3,
		RetryDelay:            30 * time.Second,
		ActionTimeout:         5 * time.Minute,
		DryRun:                false,
		RequireApproval:       false,
	}
	rem := remediator.New(remediatorCfg, log)
	
	// Initialize default remediation rules
	rem.InitializeDefaultRules()
	
	// Create capacity planner with configuration
	capacityCfg := &capacity.Config{
		ForecastWindow:  30 * 24 * time.Hour,
		HistoryWindow:   90 * 24 * time.Hour,
		MinDataPoints:   20,
		GrowthThreshold: 10.0,
		UpdateInterval:  1 * time.Hour,
		EnableAlerts:    true,
	}
	cap := capacity.New(capacityCfg, log)
	
	agent := &Agent{
		cfg:               cfg,
		log:               log,
		comm:              comm,
		exec:              exec,
		systemCollector:   systemCollector,
		securityCollector: securityCollector,
		softwareCollector: softwareCollector,
		predictor:         pred,
		remediator:        rem,
		capacityPlanner:   cap,
		ctx:               ctx,
		cancel:            cancel,
	}
	
	return agent, nil
}

// Start starts the agent
func (a *Agent) Start(ctx context.Context) error {
	a.log.Info("Starting iTechSmart Agent v1.2.0",
		"agent_id", a.cfg.AgentID,
		"organization", a.cfg.Organization,
		"platform", a.cfg.Platform,
		"features", "failure_prediction,automated_remediation,capacity_planning",
	)
	
	// Start communicator
	if err := a.comm.Start(); err != nil {
		return fmt.Errorf("failed to start communicator: %w", err)
	}
	
	// Start executor
	if err := a.exec.Start(ctx); err != nil {
		return fmt.Errorf("failed to start executor: %w", err)
	}
	
	// Start predictor
	go func() {
		if err := a.predictor.Start(ctx); err != nil {
			a.log.Error("Predictor stopped", "error", err)
		}
	}()
	
	// Start capacity planner
	go func() {
		if err := a.capacityPlanner.Start(ctx); err != nil {
			a.log.Error("Capacity planner stopped", "error", err)
		}
	}()
	
	// Start collection loops
	if a.cfg.EnableSystemMonitoring {
		go a.systemMetricsLoop()
	}
	
	if a.cfg.EnableSecurityChecks {
		go a.securityMetricsLoop()
	}
	
	if a.cfg.EnableSoftwareInventory {
		go a.softwareInventoryLoop()
	}
	
	// Start product integrations
	if a.cfg.NinjaEnabled {
		go a.ninjaIntegrationLoop()
	}
	
	if a.cfg.EnterpriseEnabled {
		go a.enterpriseIntegrationLoop()
	}
	
	a.log.Info("iTechSmart Agent started successfully with advanced features")
	
	return nil
}

// Stop stops the agent
func (a *Agent) Stop() error {
	a.log.Info("Stopping iTechSmart Agent")
	
	a.cancel()
	
	if err := a.comm.Stop(); err != nil {
		a.log.Error("Error stopping communicator", "error", err)
	}
	
	a.log.Info("iTechSmart Agent stopped")
	
	return nil
}

// systemMetricsLoop collects and sends system metrics
func (a *Agent) systemMetricsLoop() {
	ticker := time.NewTicker(time.Duration(a.cfg.SystemMetricsInterval) * time.Second)
	defer ticker.Stop()
	
	// Collect immediately on start
	a.collectAndSendSystemMetrics()
	
	for {
		select {
		case <-a.ctx.Done():
			return
		case <-ticker.C:
			a.collectAndSendSystemMetrics()
		}
	}
}

// collectAndSendSystemMetrics collects and sends system metrics
func (a *Agent) collectAndSendSystemMetrics() {
	a.log.Debug("Collecting system metrics")
	
	metrics, err := a.systemCollector.Collect()
	if err != nil {
		a.log.Error("Failed to collect system metrics", "error", err)
		return
	}
	
	if err := a.comm.SendMetrics("system", metrics); err != nil {
		a.log.Error("Failed to send system metrics", "error", err)
		return
	}
	
	a.log.Debug("System metrics sent successfully")
	
	// Add data to predictor
	a.predictor.AddDataPoint("cpu_usage", metrics.CPUInfo.UsagePercent, map[string]string{"type": "percentage"})
	a.predictor.AddDataPoint("memory_usage", metrics.MemoryInfo.UsedPercent, map[string]string{"type": "percentage"})
	
	// Add data to capacity planner
	a.capacityPlanner.AddMeasurement("cpu", metrics.CPUInfo.UsagePercent, 100.0, map[string]string{"cores": fmt.Sprintf("%d", metrics.CPUInfo.Cores)})
	a.capacityPlanner.AddMeasurement("memory", float64(metrics.MemoryInfo.Used), float64(metrics.MemoryInfo.Total), map[string]string{"unit": "bytes"})
	
	for _, disk := range metrics.DiskInfo {
		a.predictor.AddDataPoint(fmt.Sprintf("disk_usage_%s", disk.MountPoint), disk.UsedPercent, map[string]string{"type": "percentage", "mount": disk.MountPoint})
		a.capacityPlanner.AddMeasurement(fmt.Sprintf("disk_%s", disk.MountPoint), float64(disk.Used), float64(disk.Total), map[string]string{"mount": disk.MountPoint, "unit": "bytes"})
	}
	
	// Check for alerts and predictions
	a.checkSystemAlerts(metrics)
	a.checkPredictions(metrics)
	a.checkCapacityAlerts(metrics)
}

// checkSystemAlerts checks for system alerts
func (a *Agent) checkSystemAlerts(metrics *collector.SystemMetrics) {
	// CPU alert
	if metrics.CPUInfo.UsagePercent > 90 {
		a.comm.SendAlert("warning", "High CPU Usage",
			fmt.Sprintf("CPU usage is at %.2f%%", metrics.CPUInfo.UsagePercent),
			map[string]interface{}{
				"cpu_usage": metrics.CPUInfo.UsagePercent,
			},
		)
		
		// Evaluate remediation
		rules := a.remediator.EvaluateCondition("cpu_usage", metrics.CPUInfo.UsagePercent)
		if len(rules) > 0 {
			a.log.Info("Triggering remediation for high CPU", "rules", len(rules))
			go a.remediator.ExecuteRemediation(a.ctx, rules)
		}
	}
	
	// Memory alert
	if metrics.MemoryInfo.UsedPercent > 90 {
		a.comm.SendAlert("warning", "High Memory Usage",
			fmt.Sprintf("Memory usage is at %.2f%%", metrics.MemoryInfo.UsedPercent),
			map[string]interface{}{
				"memory_usage": metrics.MemoryInfo.UsedPercent,
			},
		)
		
		// Evaluate remediation
		rules := a.remediator.EvaluateCondition("memory_usage", metrics.MemoryInfo.UsedPercent)
		if len(rules) > 0 {
			a.log.Info("Triggering remediation for high memory", "rules", len(rules))
			go a.remediator.ExecuteRemediation(a.ctx, rules)
		}
	}
	
	// Disk alert
	for _, disk := range metrics.DiskInfo {
		if disk.UsedPercent > 90 {
			a.comm.SendAlert("warning", "Low Disk Space",
				fmt.Sprintf("Disk %s is %.2f%% full", disk.MountPoint, disk.UsedPercent),
				map[string]interface{}{
					"mount_point": disk.MountPoint,
					"used_percent": disk.UsedPercent,
				},
			)
			
			// Evaluate remediation
			rules := a.remediator.EvaluateCondition("disk_usage", disk.UsedPercent)
			if len(rules) > 0 {
				a.log.Info("Triggering remediation for low disk space", "mount", disk.MountPoint, "rules", len(rules))
				go a.remediator.ExecuteRemediation(a.ctx, rules)
			}
		}
	}
}

// checkPredictions checks predictions and sends alerts
func (a *Agent) checkPredictions(metrics *collector.SystemMetrics) {
	// Check CPU prediction
	if pred, err := a.predictor.PredictFailure(a.ctx, "cpu_usage"); err == nil {
		if pred.FailureProbability > 0.5 {
			a.comm.SendAlert("info", "CPU Failure Prediction",
				fmt.Sprintf("CPU usage predicted to reach %.2f%% (current: %.2f%%). %s", 
					pred.PredictedValue, pred.CurrentValue, pred.Recommendation),
				map[string]interface{}{
					"current_value":       pred.CurrentValue,
					"predicted_value":     pred.PredictedValue,
					"failure_probability": pred.FailureProbability,
					"confidence":          pred.Confidence,
					"risk_level":          pred.RiskLevel,
				},
			)
		}
	}
	
	// Check memory prediction
	if pred, err := a.predictor.PredictFailure(a.ctx, "memory_usage"); err == nil {
		if pred.FailureProbability > 0.5 {
			a.comm.SendAlert("info", "Memory Failure Prediction",
				fmt.Sprintf("Memory usage predicted to reach %.2f%% (current: %.2f%%). %s", 
					pred.PredictedValue, pred.CurrentValue, pred.Recommendation),
				map[string]interface{}{
					"current_value":       pred.CurrentValue,
					"predicted_value":     pred.PredictedValue,
					"failure_probability": pred.FailureProbability,
					"confidence":          pred.Confidence,
					"risk_level":          pred.RiskLevel,
				},
			)
		}
	}
}

// checkCapacityAlerts checks capacity forecasts and sends alerts
func (a *Agent) checkCapacityAlerts(metrics *collector.SystemMetrics) {
	// Check CPU capacity
	if forecast, err := a.capacityPlanner.ForecastCapacity(a.ctx, "cpu"); err == nil {
		if len(forecast.Alerts) > 0 {
			for _, alert := range forecast.Alerts {
				a.comm.SendAlert(alert.Severity, "CPU Capacity Alert", alert.Message,
					map[string]interface{}{
						"current_usage":      forecast.CurrentUsage,
						"forecasted_usage":   forecast.ForecastedUsage,
						"growth_rate":        forecast.GrowthRate,
						"time_to_exhaustion": forecast.TimeToExhaustion,
					},
				)
			}
		}
	}
	
	// Check memory capacity
	if forecast, err := a.capacityPlanner.ForecastCapacity(a.ctx, "memory"); err == nil {
		if len(forecast.Alerts) > 0 {
			for _, alert := range forecast.Alerts {
				a.comm.SendAlert(alert.Severity, "Memory Capacity Alert", alert.Message,
					map[string]interface{}{
						"current_usage":      forecast.CurrentUsage,
						"forecasted_usage":   forecast.ForecastedUsage,
						"growth_rate":        forecast.GrowthRate,
						"time_to_exhaustion": forecast.TimeToExhaustion,
					},
				)
			}
		}
	}
}

// securityMetricsLoop collects and sends security metrics
func (a *Agent) securityMetricsLoop() {
	ticker := time.NewTicker(time.Duration(a.cfg.SecurityCheckInterval) * time.Second)
	defer ticker.Stop()
	
	// Collect immediately on start
	a.collectAndSendSecurityMetrics()
	
	for {
		select {
		case <-a.ctx.Done():
			return
		case <-ticker.C:
			a.collectAndSendSecurityMetrics()
		}
	}
}

// collectAndSendSecurityMetrics collects and sends security metrics
func (a *Agent) collectAndSendSecurityMetrics() {
	a.log.Debug("Collecting security metrics")
	
	metrics, err := a.securityCollector.Collect()
	if err != nil {
		a.log.Error("Failed to collect security metrics", "error", err)
		return
	}
	
	if err := a.comm.SendMetrics("security", metrics); err != nil {
		a.log.Error("Failed to send security metrics", "error", err)
		return
	}
	
	a.log.Debug("Security metrics sent successfully")
	
	// Check for security alerts
	a.checkSecurityAlerts(metrics)
}

// checkSecurityAlerts checks for security alerts
func (a *Agent) checkSecurityAlerts(metrics *collector.SecurityMetrics) {
	// Firewall alert
	if !metrics.FirewallStatus.Enabled {
		a.comm.SendAlert("critical", "Firewall Disabled",
			"System firewall is not enabled",
			map[string]interface{}{
				"firewall_status": metrics.FirewallStatus,
			},
		)
	}
	
	// Antivirus alert
	if !metrics.AntivirusStatus.Enabled {
		a.comm.SendAlert("critical", "Antivirus Disabled",
			"Antivirus protection is not enabled",
			map[string]interface{}{
				"antivirus_status": metrics.AntivirusStatus,
			},
		)
	}
	
	// Compliance alerts
	for _, check := range metrics.ComplianceChecks {
		if check.Status == "fail" {
			a.comm.SendAlert("high", "Compliance Check Failed",
				fmt.Sprintf("Compliance check '%s' failed: %s", check.CheckName, check.Description),
				map[string]interface{}{
					"check_name": check.CheckName,
					"status":     check.Status,
				},
			)
		}
	}
}

// softwareInventoryLoop collects and sends software inventory
func (a *Agent) softwareInventoryLoop() {
	ticker := time.NewTicker(time.Duration(a.cfg.SoftwareInventoryInterval) * time.Second)
	defer ticker.Stop()
	
	// Collect immediately on start
	a.collectAndSendSoftwareInventory()
	
	for {
		select {
		case <-a.ctx.Done():
			return
		case <-ticker.C:
			a.collectAndSendSoftwareInventory()
		}
	}
}

// collectAndSendSoftwareInventory collects and sends software inventory
func (a *Agent) collectAndSendSoftwareInventory() {
	a.log.Debug("Collecting software inventory")
	
	inventory, err := a.softwareCollector.Collect()
	if err != nil {
		a.log.Error("Failed to collect software inventory", "error", err)
		return
	}
	
	if err := a.comm.SendMetrics("software", inventory); err != nil {
		a.log.Error("Failed to send software inventory", "error", err)
		return
	}
	
	a.log.Debug("Software inventory sent successfully")
	
	// Check for update alerts
	if len(inventory.UpdatesAvailable) > 0 {
		criticalUpdates := 0
		securityUpdates := 0
		
		for _, update := range inventory.UpdatesAvailable {
			if update.Severity == "critical" {
				criticalUpdates++
			}
			if update.UpdateType == "security" {
				securityUpdates++
			}
		}
		
		if criticalUpdates > 0 || securityUpdates > 0 {
			a.comm.SendAlert("high", "Updates Available",
				fmt.Sprintf("%d critical updates and %d security updates available", criticalUpdates, securityUpdates),
				map[string]interface{}{
					"total_updates":    len(inventory.UpdatesAvailable),
					"critical_updates": criticalUpdates,
					"security_updates": securityUpdates,
				},
			)
		}
	}
}

// ninjaIntegrationLoop handles iTechSmart Ninja integration
func (a *Agent) ninjaIntegrationLoop() {
	ticker := time.NewTicker(5 * time.Minute)
	defer ticker.Stop()
	
	a.log.Info("iTechSmart Ninja integration enabled", "url", a.cfg.NinjaURL)
	
	for {
		select {
		case <-a.ctx.Done():
			return
		case <-ticker.C:
			// Send agent status to Ninja
			a.log.Debug("Syncing with iTechSmart Ninja")
			// Implementation would call Ninja API
		}
	}
}

// enterpriseIntegrationLoop handles iTechSmart Enterprise integration
func (a *Agent) enterpriseIntegrationLoop() {
	ticker := time.NewTicker(5 * time.Minute)
	defer ticker.Stop()
	
	a.log.Info("iTechSmart Enterprise integration enabled", "url", a.cfg.EnterpriseURL)
	
	for {
		select {
		case <-a.ctx.Done():
			return
		case <-ticker.C:
			// Send agent status to Enterprise
			a.log.Debug("Syncing with iTechSmart Enterprise")
			// Implementation would call Enterprise API
		}
	}
}