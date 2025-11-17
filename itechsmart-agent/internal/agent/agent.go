package agent

import (
	"context"
	"fmt"
	"time"

	"github.com/iteksmart/itechsmart-agent/internal/collector"
	"github.com/iteksmart/itechsmart-agent/internal/communicator"
	"github.com/iteksmart/itechsmart-agent/internal/config"
	"github.com/iteksmart/itechsmart-agent/internal/executor"
	"github.com/iteksmart/itechsmart-agent/internal/logger"
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
	
	agent := &Agent{
		cfg:               cfg,
		log:               log,
		comm:              comm,
		exec:              exec,
		systemCollector:   systemCollector,
		securityCollector: securityCollector,
		softwareCollector: softwareCollector,
		ctx:               ctx,
		cancel:            cancel,
	}
	
	return agent, nil
}

// Start starts the agent
func (a *Agent) Start(ctx context.Context) error {
	a.log.Info("Starting iTechSmart Agent",
		"agent_id", a.cfg.AgentID,
		"organization", a.cfg.Organization,
		"platform", a.cfg.Platform,
	)
	
	// Start communicator
	if err := a.comm.Start(); err != nil {
		return fmt.Errorf("failed to start communicator: %w", err)
	}
	
	// Start executor
	if err := a.exec.Start(ctx); err != nil {
		return fmt.Errorf("failed to start executor: %w", err)
	}
	
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
	
	a.log.Info("iTechSmart Agent started successfully")
	
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
	
	// Check for alerts
	a.checkSystemAlerts(metrics)
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
	}
	
	// Memory alert
	if metrics.MemoryInfo.UsedPercent > 90 {
		a.comm.SendAlert("warning", "High Memory Usage",
			fmt.Sprintf("Memory usage is at %.2f%%", metrics.MemoryInfo.UsedPercent),
			map[string]interface{}{
				"memory_usage": metrics.MemoryInfo.UsedPercent,
			},
		)
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