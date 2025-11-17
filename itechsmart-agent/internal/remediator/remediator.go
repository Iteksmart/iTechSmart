package remediator

import (
	"context"
	"fmt"
	"os/exec"
	"sync"
	"time"

	"github.com/iteksmart/itechsmart-agent/internal/logger"
)

// Remediator handles automated remediation actions
type Remediator struct {
	mu              sync.RWMutex
	rules           map[string]*RemediationRule
	history         []RemediationAction
	config          *Config
	logger          *logger.Logger
	actionExecutor  *ActionExecutor
}

// Config holds remediator configuration
type Config struct {
	EnableAutoRemediation bool
	MaxRetries            int
	RetryDelay            time.Duration
	ActionTimeout         time.Duration
	DryRun                bool
	RequireApproval       bool
}

// RemediationRule defines a remediation rule
type RemediationRule struct {
	ID          string
	Name        string
	Description string
	Condition   Condition
	Actions     []Action
	Priority    int
	Enabled     bool
	AutoExecute bool
}

// Condition defines when a rule should trigger
type Condition struct {
	MetricName  string
	Operator    string // "gt", "lt", "eq", "gte", "lte"
	Threshold   float64
	Duration    time.Duration // How long condition must persist
}

// Action defines a remediation action
type Action struct {
	Type        string // "command", "script", "api", "restart_service", "cleanup"
	Command     string
	Args        []string
	Script      string
	Timeout     time.Duration
	Description string
}

// RemediationAction represents an executed action
type RemediationAction struct {
	ID          string
	RuleID      string
	RuleName    string
	Timestamp   time.Time
	Status      string // "pending", "running", "success", "failed", "cancelled"
	Actions     []ActionResult
	TotalTime   time.Duration
	Error       string
}

// ActionResult represents the result of a single action
type ActionResult struct {
	Action      Action
	Status      string
	Output      string
	Error       string
	StartTime   time.Time
	EndTime     time.Time
	Duration    time.Duration
}

// ActionExecutor executes remediation actions
type ActionExecutor struct {
	logger  *logger.Logger
	timeout time.Duration
	dryRun  bool
}

// New creates a new Remediator instance
func New(cfg *Config, log *logger.Logger) *Remediator {
	if cfg == nil {
		cfg = &Config{
			EnableAutoRemediation: true,
			MaxRetries:            3,
			RetryDelay:            30 * time.Second,
			ActionTimeout:         5 * time.Minute,
			DryRun:                false,
			RequireApproval:       false,
		}
	}

	return &Remediator{
		rules:   make(map[string]*RemediationRule),
		history: make([]RemediationAction, 0),
		config:  cfg,
		logger:  log,
		actionExecutor: &ActionExecutor{
			logger:  log,
			timeout: cfg.ActionTimeout,
			dryRun:  cfg.DryRun,
		},
	}
}

// AddRule adds a remediation rule
func (r *Remediator) AddRule(rule *RemediationRule) error {
	if rule.ID == "" {
		return fmt.Errorf("rule ID cannot be empty")
	}

	r.mu.Lock()
	defer r.mu.Unlock()

	r.rules[rule.ID] = rule
	r.logger.Info("Added remediation rule", "rule_id", rule.ID, "name", rule.Name)
	return nil
}

// RemoveRule removes a remediation rule
func (r *Remediator) RemoveRule(ruleID string) error {
	r.mu.Lock()
	defer r.mu.Unlock()

	if _, exists := r.rules[ruleID]; !exists {
		return fmt.Errorf("rule not found: %s", ruleID)
	}

	delete(r.rules, ruleID)
	r.logger.Info("Removed remediation rule", "rule_id", ruleID)
	return nil
}

// EvaluateCondition evaluates if a condition is met
func (r *Remediator) EvaluateCondition(metricName string, value float64) []*RemediationRule {
	r.mu.RLock()
	defer r.mu.RUnlock()

	triggeredRules := make([]*RemediationRule, 0)

	for _, rule := range r.rules {
		if !rule.Enabled {
			continue
		}

		if rule.Condition.MetricName != metricName {
			continue
		}

		if r.checkCondition(rule.Condition, value) {
			triggeredRules = append(triggeredRules, rule)
		}
	}

	return triggeredRules
}

// checkCondition checks if a condition is met
func (r *Remediator) checkCondition(condition Condition, value float64) bool {
	switch condition.Operator {
	case "gt":
		return value > condition.Threshold
	case "gte":
		return value >= condition.Threshold
	case "lt":
		return value < condition.Threshold
	case "lte":
		return value <= condition.Threshold
	case "eq":
		return value == condition.Threshold
	default:
		return false
	}
}

// ExecuteRemediation executes remediation for triggered rules
func (r *Remediator) ExecuteRemediation(ctx context.Context, rules []*RemediationRule) error {
	if len(rules) == 0 {
		return nil
	}

	if !r.config.EnableAutoRemediation {
		r.logger.Info("Auto-remediation disabled, skipping execution")
		return nil
	}

	// Sort rules by priority (higher priority first)
	sortedRules := make([]*RemediationRule, len(rules))
	copy(sortedRules, rules)
	for i := 0; i < len(sortedRules); i++ {
		for j := i + 1; j < len(sortedRules); j++ {
			if sortedRules[j].Priority > sortedRules[i].Priority {
				sortedRules[i], sortedRules[j] = sortedRules[j], sortedRules[i]
			}
		}
	}

	for _, rule := range sortedRules {
		if !rule.AutoExecute && r.config.RequireApproval {
			r.logger.Info("Rule requires approval, skipping", "rule_id", rule.ID)
			continue
		}

		if err := r.executeRule(ctx, rule); err != nil {
			r.logger.Error("Failed to execute rule", "rule_id", rule.ID, "error", err)
			continue
		}
	}

	return nil
}

// executeRule executes a single remediation rule
func (r *Remediator) executeRule(ctx context.Context, rule *RemediationRule) error {
	actionID := fmt.Sprintf("%s-%d", rule.ID, time.Now().Unix())
	
	remediationAction := RemediationAction{
		ID:        actionID,
		RuleID:    rule.ID,
		RuleName:  rule.Name,
		Timestamp: time.Now(),
		Status:    "running",
		Actions:   make([]ActionResult, 0),
	}

	r.logger.Info("Executing remediation rule", "rule_id", rule.ID, "name", rule.Name)

	startTime := time.Now()

	for _, action := range rule.Actions {
		result := r.actionExecutor.Execute(ctx, action)
		remediationAction.Actions = append(remediationAction.Actions, result)

		if result.Status == "failed" {
			remediationAction.Status = "failed"
			remediationAction.Error = result.Error
			break
		}
	}

	if remediationAction.Status != "failed" {
		remediationAction.Status = "success"
	}

	remediationAction.TotalTime = time.Since(startTime)

	// Store in history
	r.mu.Lock()
	r.history = append(r.history, remediationAction)
	// Keep only last 1000 actions
	if len(r.history) > 1000 {
		r.history = r.history[len(r.history)-1000:]
	}
	r.mu.Unlock()

	r.logger.Info("Remediation completed", 
		"rule_id", rule.ID,
		"status", remediationAction.Status,
		"duration", remediationAction.TotalTime)

	return nil
}

// Execute executes a single action
func (ae *ActionExecutor) Execute(ctx context.Context, action Action) ActionResult {
	result := ActionResult{
		Action:    action,
		Status:    "running",
		StartTime: time.Now(),
	}

	if ae.dryRun {
		ae.logger.Info("DRY RUN: Would execute action", "type", action.Type, "command", action.Command)
		result.Status = "success"
		result.Output = "DRY RUN - Action not executed"
		result.EndTime = time.Now()
		result.Duration = time.Since(result.StartTime)
		return result
	}

	// Create context with timeout
	actionCtx, cancel := context.WithTimeout(ctx, ae.timeout)
	defer cancel()

	switch action.Type {
	case "command":
		result = ae.executeCommand(actionCtx, action)
	case "script":
		result = ae.executeScript(actionCtx, action)
	case "restart_service":
		result = ae.restartService(actionCtx, action)
	case "cleanup":
		result = ae.cleanup(actionCtx, action)
	default:
		result.Status = "failed"
		result.Error = fmt.Sprintf("unknown action type: %s", action.Type)
	}

	result.EndTime = time.Now()
	result.Duration = time.Since(result.StartTime)

	return result
}

// executeCommand executes a shell command
func (ae *ActionExecutor) executeCommand(ctx context.Context, action Action) ActionResult {
	result := ActionResult{
		Action:    action,
		Status:    "running",
		StartTime: time.Now(),
	}

	cmd := exec.CommandContext(ctx, action.Command, action.Args...)
	output, err := cmd.CombinedOutput()

	result.Output = string(output)

	if err != nil {
		result.Status = "failed"
		result.Error = err.Error()
		ae.logger.Error("Command execution failed", 
			"command", action.Command,
			"error", err,
			"output", string(output))
	} else {
		result.Status = "success"
		ae.logger.Info("Command executed successfully", 
			"command", action.Command,
			"output", string(output))
	}

	return result
}

// executeScript executes a script
func (ae *ActionExecutor) executeScript(ctx context.Context, action Action) ActionResult {
	result := ActionResult{
		Action:    action,
		Status:    "running",
		StartTime: time.Now(),
	}

	// Create temporary script file
	
	// Write script content (simplified - in production, use proper file handling)
	cmd := exec.CommandContext(ctx, "sh", "-c", action.Script)
	output, err := cmd.CombinedOutput()

	result.Output = string(output)

	if err != nil {
		result.Status = "failed"
		result.Error = err.Error()
		ae.logger.Error("Script execution failed", "error", err)
	} else {
		result.Status = "success"
		ae.logger.Info("Script executed successfully")
	}

	return result
}

// restartService restarts a system service
func (ae *ActionExecutor) restartService(ctx context.Context, action Action) ActionResult {
	result := ActionResult{
		Action:    action,
		Status:    "running",
		StartTime: time.Now(),
	}

	serviceName := action.Command
	
	// Try systemctl first (Linux)
	cmd := exec.CommandContext(ctx, "systemctl", "restart", serviceName)
	output, err := cmd.CombinedOutput()

	result.Output = string(output)

	if err != nil {
		result.Status = "failed"
		result.Error = err.Error()
		ae.logger.Error("Service restart failed", "service", serviceName, "error", err)
	} else {
		result.Status = "success"
		ae.logger.Info("Service restarted successfully", "service", serviceName)
	}

	return result
}

// cleanup performs cleanup actions
func (ae *ActionExecutor) cleanup(ctx context.Context, action Action) ActionResult {
	result := ActionResult{
		Action:    action,
		Status:    "running",
		StartTime: time.Now(),
	}

	// Execute cleanup command
	cmd := exec.CommandContext(ctx, "sh", "-c", action.Command)
	output, err := cmd.CombinedOutput()

	result.Output = string(output)

	if err != nil {
		result.Status = "failed"
		result.Error = err.Error()
		ae.logger.Error("Cleanup failed", "error", err)
	} else {
		result.Status = "success"
		ae.logger.Info("Cleanup completed successfully")
	}

	return result
}

// GetHistory retrieves remediation history
func (r *Remediator) GetHistory(limit int) []RemediationAction {
	r.mu.RLock()
	defer r.mu.RUnlock()

	if limit <= 0 || limit > len(r.history) {
		limit = len(r.history)
	}

	// Return most recent actions
	start := len(r.history) - limit
	result := make([]RemediationAction, limit)
	copy(result, r.history[start:])

	return result
}

// GetRules retrieves all remediation rules
func (r *Remediator) GetRules() map[string]*RemediationRule {
	r.mu.RLock()
	defer r.mu.RUnlock()

	rules := make(map[string]*RemediationRule)
	for k, v := range r.rules {
		rules[k] = v
	}
	return rules
}

// InitializeDefaultRules initializes default remediation rules
func (r *Remediator) InitializeDefaultRules() {
	// High CPU usage remediation
	r.AddRule(&RemediationRule{
		ID:          "high-cpu-remediation",
		Name:        "High CPU Usage Remediation",
		Description: "Automatically remediate high CPU usage",
		Condition: Condition{
			MetricName: "cpu_usage",
			Operator:   "gte",
			Threshold:  90.0,
			Duration:   5 * time.Minute,
		},
		Actions: []Action{
			{
				Type:        "command",
				Command:     "ps",
				Args:        []string{"aux", "--sort=-pcpu"},
				Description: "List processes by CPU usage",
				Timeout:     30 * time.Second,
			},
			{
				Type:        "script",
				Script:      "kill -9 $(ps aux --sort=-pcpu | awk 'NR==2{print $2}')",
				Description: "Kill highest CPU process",
				Timeout:     30 * time.Second,
			},
		},
		Priority:    10,
		Enabled:     true,
		AutoExecute: false, // Requires approval
	})

	// High memory usage remediation
	r.AddRule(&RemediationRule{
		ID:          "high-memory-remediation",
		Name:        "High Memory Usage Remediation",
		Description: "Automatically remediate high memory usage",
		Condition: Condition{
			MetricName: "memory_usage",
			Operator:   "gte",
			Threshold:  90.0,
			Duration:   5 * time.Minute,
		},
		Actions: []Action{
			{
				Type:        "command",
				Command:     "sync",
				Args:        []string{},
				Description: "Sync filesystem",
				Timeout:     30 * time.Second,
			},
			{
				Type:        "command",
				Command:     "echo",
				Args:        []string{"3", ">", "/proc/sys/vm/drop_caches"},
				Description: "Clear page cache",
				Timeout:     30 * time.Second,
			},
		},
		Priority:    9,
		Enabled:     true,
		AutoExecute: true,
	})

	// Disk cleanup remediation
	r.AddRule(&RemediationRule{
		ID:          "disk-cleanup-remediation",
		Name:        "Disk Cleanup Remediation",
		Description: "Automatically clean up disk space",
		Condition: Condition{
			MetricName: "disk_usage",
			Operator:   "gte",
			Threshold:  85.0,
			Duration:   10 * time.Minute,
		},
		Actions: []Action{
			{
				Type:        "cleanup",
				Command:     "find /tmp -type f -atime +7 -delete",
				Description: "Clean old temp files",
				Timeout:     5 * time.Minute,
			},
			{
				Type:        "cleanup",
				Command:     "journalctl --vacuum-time=7d",
				Description: "Clean old journal logs",
				Timeout:     2 * time.Minute,
			},
		},
		Priority:    8,
		Enabled:     true,
		AutoExecute: true,
	})

	r.logger.Info("Initialized default remediation rules", "count", 3)
}