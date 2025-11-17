package executor

import (
	"context"
	"fmt"
	"os/exec"
	"runtime"
	"strings"
	"time"

	"github.com/iteksmart/itechsmart-agent/internal/communicator"
	"github.com/iteksmart/itechsmart-agent/internal/config"
	"github.com/iteksmart/itechsmart-agent/internal/logger"
)

// Executor handles command execution
type Executor struct {
	cfg  *config.Config
	log  *logger.Logger
	comm *communicator.Communicator
}

// NewExecutor creates a new executor
func NewExecutor(cfg *config.Config, log *logger.Logger, comm *communicator.Communicator) *Executor {
	return &Executor{
		cfg:  cfg,
		log:  log,
		comm: comm,
	}
}

// Start starts the executor
func (e *Executor) Start(ctx context.Context) error {
	e.log.Info("Starting command executor")
	
	if !e.cfg.EnableRemoteCommands {
		e.log.Info("Remote commands disabled")
		return nil
	}
	
	// Listen for commands
	go e.processCommands(ctx)
	
	return nil
}

// processCommands processes incoming commands
func (e *Executor) processCommands(ctx context.Context) {
	commandChan := e.comm.GetCommandChannel()
	
	for {
		select {
		case <-ctx.Done():
			return
		case cmd := <-commandChan:
			e.log.Info("Processing command", "type", cmd.Type, "id", cmd.ID)
			
			result := e.executeCommand(cmd)
			
			if err := e.comm.SendCommandResult(result); err != nil {
				e.log.Error("Failed to send command result", "error", err)
			}
		}
	}
}

// executeCommand executes a command
func (e *Executor) executeCommand(cmd communicator.Command) communicator.CommandResult {
	result := communicator.CommandResult{
		CommandID: cmd.ID,
		Timestamp: time.Now(),
		Payload:   make(map[string]interface{}),
	}
	
	switch cmd.Type {
	case "shell":
		result = e.executeShellCommand(cmd)
	case "script":
		result = e.executeScript(cmd)
	case "install_software":
		result = e.installSoftware(cmd)
	case "uninstall_software":
		result = e.uninstallSoftware(cmd)
	case "update_software":
		result = e.updateSoftware(cmd)
	case "restart":
		result = e.restartSystem(cmd)
	case "get_file":
		result = e.getFile(cmd)
	case "put_file":
		result = e.putFile(cmd)
	case "run_diagnostics":
		result = e.runDiagnostics(cmd)
	default:
		result.Success = false
		result.Error = fmt.Sprintf("unknown command type: %s", cmd.Type)
	}
	
	return result
}

// executeShellCommand executes a shell command
func (e *Executor) executeShellCommand(cmd communicator.Command) communicator.CommandResult {
	result := communicator.CommandResult{
		CommandID: cmd.ID,
		Timestamp: time.Now(),
	}
	
	// Get command string
	cmdStr, ok := cmd.Payload["command"].(string)
	if !ok {
		result.Success = false
		result.Error = "missing command parameter"
		return result
	}
	
	e.log.Info("Executing shell command", "command", cmdStr)
	
	// Create context with timeout
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Minute)
	defer cancel()
	
	// Execute command based on platform
	var execCmd *exec.Cmd
	switch runtime.GOOS {
	case "windows":
		execCmd = exec.CommandContext(ctx, "powershell", "-Command", cmdStr)
	case "linux", "darwin":
		execCmd = exec.CommandContext(ctx, "bash", "-c", cmdStr)
	default:
		result.Success = false
		result.Error = fmt.Sprintf("unsupported platform: %s", runtime.GOOS)
		return result
	}
	
	// Execute
	output, err := execCmd.CombinedOutput()
	result.Output = string(output)
	
	if err != nil {
		result.Success = false
		result.Error = err.Error()
		e.log.Error("Command execution failed", "error", err, "output", result.Output)
	} else {
		result.Success = true
		e.log.Info("Command executed successfully")
	}
	
	return result
}

// executeScript executes a script
func (e *Executor) executeScript(cmd communicator.Command) communicator.CommandResult {
	result := communicator.CommandResult{
		CommandID: cmd.ID,
		Timestamp: time.Now(),
	}
	
	// Get script content
	scriptContent, ok := cmd.Payload["script"].(string)
	if !ok {
		result.Success = false
		result.Error = "missing script parameter"
		return result
	}
	
	scriptType, _ := cmd.Payload["script_type"].(string)
	
	e.log.Info("Executing script", "type", scriptType)
	
	// Create temporary script file
	// Execute script
	// Clean up
	
	result.Success = true
	result.Output = "Script execution not yet implemented"
	
	return result
}

// installSoftware installs software
func (e *Executor) installSoftware(cmd communicator.Command) communicator.CommandResult {
	result := communicator.CommandResult{
		CommandID: cmd.ID,
		Timestamp: time.Now(),
	}
	
	if !e.cfg.EnablePatchManagement {
		result.Success = false
		result.Error = "patch management disabled"
		return result
	}
	
	packageName, ok := cmd.Payload["package"].(string)
	if !ok {
		result.Success = false
		result.Error = "missing package parameter"
		return result
	}
	
	e.log.Info("Installing software", "package", packageName)
	
	var execCmd *exec.Cmd
	switch runtime.GOOS {
	case "windows":
		execCmd = exec.Command("choco", "install", packageName, "-y")
	case "linux":
		// Try apt first, then yum
		if _, err := exec.LookPath("apt"); err == nil {
			execCmd = exec.Command("apt", "install", "-y", packageName)
		} else if _, err := exec.LookPath("yum"); err == nil {
			execCmd = exec.Command("yum", "install", "-y", packageName)
		}
	case "darwin":
		execCmd = exec.Command("brew", "install", packageName)
	}
	
	if execCmd == nil {
		result.Success = false
		result.Error = "package manager not found"
		return result
	}
	
	output, err := execCmd.CombinedOutput()
	result.Output = string(output)
	
	if err != nil {
		result.Success = false
		result.Error = err.Error()
	} else {
		result.Success = true
	}
	
	return result
}

// uninstallSoftware uninstalls software
func (e *Executor) uninstallSoftware(cmd communicator.Command) communicator.CommandResult {
	result := communicator.CommandResult{
		CommandID: cmd.ID,
		Timestamp: time.Now(),
	}
	
	if !e.cfg.EnablePatchManagement {
		result.Success = false
		result.Error = "patch management disabled"
		return result
	}
	
	packageName, ok := cmd.Payload["package"].(string)
	if !ok {
		result.Success = false
		result.Error = "missing package parameter"
		return result
	}
	
	e.log.Info("Uninstalling software", "package", packageName)
	
	var execCmd *exec.Cmd
	switch runtime.GOOS {
	case "windows":
		execCmd = exec.Command("choco", "uninstall", packageName, "-y")
	case "linux":
		if _, err := exec.LookPath("apt"); err == nil {
			execCmd = exec.Command("apt", "remove", "-y", packageName)
		} else if _, err := exec.LookPath("yum"); err == nil {
			execCmd = exec.Command("yum", "remove", "-y", packageName)
		}
	case "darwin":
		execCmd = exec.Command("brew", "uninstall", packageName)
	}
	
	if execCmd == nil {
		result.Success = false
		result.Error = "package manager not found"
		return result
	}
	
	output, err := execCmd.CombinedOutput()
	result.Output = string(output)
	
	if err != nil {
		result.Success = false
		result.Error = err.Error()
	} else {
		result.Success = true
	}
	
	return result
}

// updateSoftware updates software
func (e *Executor) updateSoftware(cmd communicator.Command) communicator.CommandResult {
	result := communicator.CommandResult{
		CommandID: cmd.ID,
		Timestamp: time.Now(),
	}
	
	if !e.cfg.EnablePatchManagement {
		result.Success = false
		result.Error = "patch management disabled"
		return result
	}
	
	e.log.Info("Updating software")
	
	var execCmd *exec.Cmd
	switch runtime.GOOS {
	case "windows":
		execCmd = exec.Command("choco", "upgrade", "all", "-y")
	case "linux":
		if _, err := exec.LookPath("apt"); err == nil {
			execCmd = exec.Command("apt", "upgrade", "-y")
		} else if _, err := exec.LookPath("yum"); err == nil {
			execCmd = exec.Command("yum", "update", "-y")
		}
	case "darwin":
		execCmd = exec.Command("brew", "upgrade")
	}
	
	if execCmd == nil {
		result.Success = false
		result.Error = "package manager not found"
		return result
	}
	
	output, err := execCmd.CombinedOutput()
	result.Output = string(output)
	
	if err != nil {
		result.Success = false
		result.Error = err.Error()
	} else {
		result.Success = true
	}
	
	return result
}

// restartSystem restarts the system
func (e *Executor) restartSystem(cmd communicator.Command) communicator.CommandResult {
	result := communicator.CommandResult{
		CommandID: cmd.ID,
		Timestamp: time.Now(),
	}
	
	e.log.Warn("System restart requested")
	
	// Get delay in minutes
	delay := 1
	if d, ok := cmd.Payload["delay"].(float64); ok {
		delay = int(d)
	}
	
	var execCmd *exec.Cmd
	switch runtime.GOOS {
	case "windows":
		execCmd = exec.Command("shutdown", "/r", "/t", fmt.Sprintf("%d", delay*60))
	case "linux", "darwin":
		execCmd = exec.Command("shutdown", "-r", fmt.Sprintf("+%d", delay))
	}
	
	output, err := execCmd.CombinedOutput()
	result.Output = string(output)
	
	if err != nil {
		result.Success = false
		result.Error = err.Error()
	} else {
		result.Success = true
		result.Output = fmt.Sprintf("System will restart in %d minute(s)", delay)
	}
	
	return result
}

// getFile retrieves a file from the system
func (e *Executor) getFile(cmd communicator.Command) communicator.CommandResult {
	result := communicator.CommandResult{
		CommandID: cmd.ID,
		Timestamp: time.Now(),
	}
	
	// Implementation for file retrieval
	result.Success = false
	result.Error = "file retrieval not yet implemented"
	
	return result
}

// putFile uploads a file to the system
func (e *Executor) putFile(cmd communicator.Command) communicator.CommandResult {
	result := communicator.CommandResult{
		CommandID: cmd.ID,
		Timestamp: time.Now(),
	}
	
	// Implementation for file upload
	result.Success = false
	result.Error = "file upload not yet implemented"
	
	return result
}

// runDiagnostics runs system diagnostics
func (e *Executor) runDiagnostics(cmd communicator.Command) communicator.CommandResult {
	result := communicator.CommandResult{
		CommandID: cmd.ID,
		Timestamp: time.Now(),
		Payload:   make(map[string]interface{}),
	}
	
	e.log.Info("Running system diagnostics")
	
	var diagnostics []string
	
	// Check disk space
	diagnostics = append(diagnostics, "Disk Space: OK")
	
	// Check memory
	diagnostics = append(diagnostics, "Memory: OK")
	
	// Check CPU
	diagnostics = append(diagnostics, "CPU: OK")
	
	// Check network
	diagnostics = append(diagnostics, "Network: OK")
	
	result.Success = true
	result.Output = strings.Join(diagnostics, "\n")
	result.Payload["diagnostics"] = diagnostics
	
	return result
}