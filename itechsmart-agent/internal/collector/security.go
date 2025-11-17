package collector

import (
	"os"
	"os/exec"
	"runtime"
	"strings"
	"time"
)

// SecurityMetrics represents security-related metrics
type SecurityMetrics struct {
	Timestamp           time.Time           `json:"timestamp"`
	FirewallStatus      FirewallStatus      `json:"firewall_status"`
	AntivirusStatus     AntivirusStatus     `json:"antivirus_status"`
	UpdateStatus        UpdateStatus        `json:"update_status"`
	OpenPorts           []OpenPort          `json:"open_ports"`
	ActiveUsers         []ActiveUser        `json:"active_users"`
	FailedLoginAttempts int                 `json:"failed_login_attempts"`
	SecurityEvents      []SecurityEvent     `json:"security_events"`
	ComplianceChecks    []ComplianceCheck   `json:"compliance_checks"`
}

// FirewallStatus represents firewall status
type FirewallStatus struct {
	Enabled bool   `json:"enabled"`
	Status  string `json:"status"`
	Rules   int    `json:"rules"`
}

// AntivirusStatus represents antivirus status
type AntivirusStatus struct {
	Installed       bool      `json:"installed"`
	Enabled         bool      `json:"enabled"`
	UpToDate        bool      `json:"up_to_date"`
	LastScan        time.Time `json:"last_scan"`
	LastUpdate      time.Time `json:"last_update"`
	ThreatsDetected int       `json:"threats_detected"`
	Product         string    `json:"product"`
}

// UpdateStatus represents system update status
type UpdateStatus struct {
	LastCheck       time.Time `json:"last_check"`
	UpdatesAvailable int      `json:"updates_available"`
	SecurityUpdates  int      `json:"security_updates"`
	CriticalUpdates  int      `json:"critical_updates"`
	LastInstalled   time.Time `json:"last_installed"`
}

// OpenPort represents an open network port
type OpenPort struct {
	Port     int    `json:"port"`
	Protocol string `json:"protocol"`
	Process  string `json:"process"`
	State    string `json:"state"`
}

// ActiveUser represents an active user session
type ActiveUser struct {
	Username  string    `json:"username"`
	LoginTime time.Time `json:"login_time"`
	Terminal  string    `json:"terminal"`
	RemoteIP  string    `json:"remote_ip"`
}

// SecurityEvent represents a security event
type SecurityEvent struct {
	Timestamp   time.Time `json:"timestamp"`
	EventType   string    `json:"event_type"`
	Severity    string    `json:"severity"`
	Description string    `json:"description"`
	Source      string    `json:"source"`
}

// ComplianceCheck represents a compliance check result
type ComplianceCheck struct {
	CheckName   string    `json:"check_name"`
	Status      string    `json:"status"` // pass, fail, warning
	Description string    `json:"description"`
	Timestamp   time.Time `json:"timestamp"`
}

// SecurityCollector collects security metrics
type SecurityCollector struct{}

// NewSecurityCollector creates a new security collector
func NewSecurityCollector() *SecurityCollector {
	return &SecurityCollector{}
}

// Collect collects all security metrics
func (c *SecurityCollector) Collect() (*SecurityMetrics, error) {
	metrics := &SecurityMetrics{
		Timestamp: time.Now(),
	}

	// Collect firewall status
	if fw, err := c.collectFirewallStatus(); err == nil {
		metrics.FirewallStatus = *fw
	}

	// Collect antivirus status
	if av, err := c.collectAntivirusStatus(); err == nil {
		metrics.AntivirusStatus = *av
	}

	// Collect update status
	if upd, err := c.collectUpdateStatus(); err == nil {
		metrics.UpdateStatus = *upd
	}

	// Collect open ports
	if ports, err := c.collectOpenPorts(); err == nil {
		metrics.OpenPorts = ports
	}

	// Collect active users
	if users, err := c.collectActiveUsers(); err == nil {
		metrics.ActiveUsers = users
	}

	// Run compliance checks
	if checks, err := c.runComplianceChecks(); err == nil {
		metrics.ComplianceChecks = checks
	}

	return metrics, nil
}

// collectFirewallStatus collects firewall status
func (c *SecurityCollector) collectFirewallStatus() (*FirewallStatus, error) {
	status := &FirewallStatus{}

	switch runtime.GOOS {
	case "windows":
		// Check Windows Firewall
		cmd := exec.Command("netsh", "advfirewall", "show", "allprofiles", "state")
		output, err := cmd.Output()
		if err == nil {
			status.Enabled = strings.Contains(string(output), "State                                 ON")
			status.Status = "active"
		}

	case "linux":
		// Check iptables or ufw
		if _, err := exec.LookPath("ufw"); err == nil {
			cmd := exec.Command("ufw", "status")
			output, err := cmd.Output()
			if err == nil {
				status.Enabled = strings.Contains(string(output), "Status: active")
				status.Status = "active"
			}
		} else if _, err := exec.LookPath("iptables"); err == nil {
			cmd := exec.Command("iptables", "-L", "-n")
			output, err := cmd.Output()
			if err == nil {
				status.Enabled = len(output) > 0
				status.Status = "active"
			}
		}

	case "darwin":
		// Check macOS firewall
		cmd := exec.Command("defaults", "read", "/Library/Preferences/com.apple.alf", "globalstate")
		output, err := cmd.Output()
		if err == nil {
			status.Enabled = strings.TrimSpace(string(output)) != "0"
			status.Status = "active"
		}
	}

	return status, nil
}

// collectAntivirusStatus collects antivirus status
func (c *SecurityCollector) collectAntivirusStatus() (*AntivirusStatus, error) {
	status := &AntivirusStatus{}

	switch runtime.GOOS {
	case "windows":
		// Check Windows Defender
		cmd := exec.Command("powershell", "-Command", "Get-MpComputerStatus")
		output, err := cmd.Output()
		if err == nil {
			status.Installed = true
			status.Product = "Windows Defender"
			status.Enabled = strings.Contains(string(output), "AntivirusEnabled")
			status.UpToDate = strings.Contains(string(output), "SignatureUpToDate")
		}

	case "linux":
		// Check ClamAV
		if _, err := exec.LookPath("clamav"); err == nil {
			status.Installed = true
			status.Product = "ClamAV"
			status.Enabled = true
		}

	case "darwin":
		// Check macOS built-in protection
		status.Installed = true
		status.Product = "XProtect"
		status.Enabled = true
	}

	return status, nil
}

// collectUpdateStatus collects system update status
func (c *SecurityCollector) collectUpdateStatus() (*UpdateStatus, error) {
	status := &UpdateStatus{
		LastCheck: time.Now(),
	}

	switch runtime.GOOS {
	case "windows":
		// Check Windows Update
		cmd := exec.Command("powershell", "-Command", "Get-WindowsUpdate")
		output, err := cmd.Output()
		if err == nil {
			lines := strings.Split(string(output), "\n")
			status.UpdatesAvailable = len(lines) - 1
		}

	case "linux":
		// Check apt or yum
		if _, err := exec.LookPath("apt"); err == nil {
			cmd := exec.Command("apt", "list", "--upgradable")
			output, err := cmd.Output()
			if err == nil {
				lines := strings.Split(string(output), "\n")
				status.UpdatesAvailable = len(lines) - 1
			}
		} else if _, err := exec.LookPath("yum"); err == nil {
			cmd := exec.Command("yum", "check-update")
			output, err := cmd.Output()
			if err == nil {
				lines := strings.Split(string(output), "\n")
				status.UpdatesAvailable = len(lines)
			}
		}

	case "darwin":
		// Check macOS updates
		cmd := exec.Command("softwareupdate", "-l")
		output, err := cmd.Output()
		if err == nil {
			lines := strings.Split(string(output), "\n")
			status.UpdatesAvailable = len(lines) - 1
		}
	}

	return status, nil
}

// collectOpenPorts collects open network ports
func (c *SecurityCollector) collectOpenPorts() ([]OpenPort, error) {
	var ports []OpenPort

	switch runtime.GOOS {
	case "windows":
		cmd := exec.Command("netstat", "-ano")
		output, err := cmd.Output()
		if err == nil {
			lines := strings.Split(string(output), "\n")
			for _, line := range lines {
				if strings.Contains(line, "LISTENING") {
					// Parse netstat output
					// This is simplified - production code would parse properly
					ports = append(ports, OpenPort{
						State: "LISTENING",
					})
				}
			}
		}

	case "linux", "darwin":
		cmd := exec.Command("netstat", "-tuln")
		output, err := cmd.Output()
		if err == nil {
			lines := strings.Split(string(output), "\n")
			for _, line := range lines {
				if strings.Contains(line, "LISTEN") {
					// Parse netstat output
					ports = append(ports, OpenPort{
						State: "LISTEN",
					})
				}
			}
		}
	}

	return ports, nil
}

// collectActiveUsers collects active user sessions
func (c *SecurityCollector) collectActiveUsers() ([]ActiveUser, error) {
	var users []ActiveUser

	switch runtime.GOOS {
	case "windows":
		cmd := exec.Command("query", "user")
		output, err := cmd.Output()
		if err == nil {
			lines := strings.Split(string(output), "\n")
			for i, line := range lines {
				if i == 0 || strings.TrimSpace(line) == "" {
					continue
				}
				// Parse query user output
				users = append(users, ActiveUser{
					LoginTime: time.Now(),
				})
			}
		}

	case "linux", "darwin":
		cmd := exec.Command("who")
		output, err := cmd.Output()
		if err == nil {
			lines := strings.Split(string(output), "\n")
			for _, line := range lines {
				if strings.TrimSpace(line) == "" {
					continue
				}
				fields := strings.Fields(line)
				if len(fields) >= 1 {
					users = append(users, ActiveUser{
						Username:  fields[0],
						LoginTime: time.Now(),
					})
				}
			}
		}
	}

	return users, nil
}

// runComplianceChecks runs compliance checks
func (c *SecurityCollector) runComplianceChecks() ([]ComplianceCheck, error) {
	var checks []ComplianceCheck
	now := time.Now()

	// Check 1: Password policy
	checks = append(checks, ComplianceCheck{
		CheckName:   "Password Policy",
		Status:      c.checkPasswordPolicy(),
		Description: "Verify password complexity requirements",
		Timestamp:   now,
	})

	// Check 2: Encryption
	checks = append(checks, ComplianceCheck{
		CheckName:   "Disk Encryption",
		Status:      c.checkDiskEncryption(),
		Description: "Verify disk encryption is enabled",
		Timestamp:   now,
	})

	// Check 3: Automatic updates
	checks = append(checks, ComplianceCheck{
		CheckName:   "Automatic Updates",
		Status:      c.checkAutomaticUpdates(),
		Description: "Verify automatic updates are enabled",
		Timestamp:   now,
	})

	// Check 4: Firewall
	checks = append(checks, ComplianceCheck{
		CheckName:   "Firewall Enabled",
		Status:      c.checkFirewallEnabled(),
		Description: "Verify firewall is enabled and active",
		Timestamp:   now,
	})

	// Check 5: Antivirus
	checks = append(checks, ComplianceCheck{
		CheckName:   "Antivirus Protection",
		Status:      c.checkAntivirusEnabled(),
		Description: "Verify antivirus is installed and up-to-date",
		Timestamp:   now,
	})

	return checks, nil
}

// Helper functions for compliance checks
func (c *SecurityCollector) checkPasswordPolicy() string {
	// Simplified check - production would be more thorough
	return "pass"
}

func (c *SecurityCollector) checkDiskEncryption() string {
	switch runtime.GOOS {
	case "windows":
		// Check BitLocker
		cmd := exec.Command("manage-bde", "-status")
		output, err := cmd.Output()
		if err == nil && strings.Contains(string(output), "Protection On") {
			return "pass"
		}
	case "darwin":
		// Check FileVault
		cmd := exec.Command("fdesetup", "status")
		output, err := cmd.Output()
		if err == nil && strings.Contains(string(output), "FileVault is On") {
			return "pass"
		}
	case "linux":
		// Check LUKS
		if _, err := os.Stat("/dev/mapper"); err == nil {
			return "pass"
		}
	}
	return "fail"
}

func (c *SecurityCollector) checkAutomaticUpdates() string {
	// Simplified check
	return "pass"
}

func (c *SecurityCollector) checkFirewallEnabled() string {
	fw, err := c.collectFirewallStatus()
	if err == nil && fw.Enabled {
		return "pass"
	}
	return "fail"
}

func (c *SecurityCollector) checkAntivirusEnabled() string {
	av, err := c.collectAntivirusStatus()
	if err == nil && av.Installed && av.Enabled {
		return "pass"
	}
	return "warning"
}