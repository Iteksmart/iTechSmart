package collector

import (
	"os/exec"
	"runtime"
	"strings"
	"time"
)

// SoftwareInventory represents installed software inventory
type SoftwareInventory struct {
	Timestamp         time.Time           `json:"timestamp"`
	InstalledSoftware []InstalledSoftware `json:"installed_software"`
	TotalCount        int                 `json:"total_count"`
	LicensedSoftware  []LicensedSoftware  `json:"licensed_software"`
	UpdatesAvailable  []SoftwareUpdate    `json:"updates_available"`
}

// InstalledSoftware represents an installed software package
type InstalledSoftware struct {
	Name            string    `json:"name"`
	Version         string    `json:"version"`
	Publisher       string    `json:"publisher"`
	InstallDate     time.Time `json:"install_date"`
	InstallLocation string    `json:"install_location"`
	Size            int64     `json:"size"`
	Architecture    string    `json:"architecture"`
}

// LicensedSoftware represents licensed software
type LicensedSoftware struct {
	Name          string    `json:"name"`
	Version       string    `json:"version"`
	LicenseKey    string    `json:"license_key"`
	LicenseType   string    `json:"license_type"`
	ExpiryDate    time.Time `json:"expiry_date"`
	IsValid       bool      `json:"is_valid"`
	AssignedUsers int       `json:"assigned_users"`
}

// SoftwareUpdate represents an available software update
type SoftwareUpdate struct {
	Name            string    `json:"name"`
	CurrentVersion  string    `json:"current_version"`
	AvailableVersion string   `json:"available_version"`
	UpdateType      string    `json:"update_type"` // security, feature, bugfix
	Severity        string    `json:"severity"`    // critical, high, medium, low
	ReleaseDate     time.Time `json:"release_date"`
	Description     string    `json:"description"`
}

// SoftwareCollector collects software inventory
type SoftwareCollector struct{}

// NewSoftwareCollector creates a new software collector
func NewSoftwareCollector() *SoftwareCollector {
	return &SoftwareCollector{}
}

// Collect collects software inventory
func (c *SoftwareCollector) Collect() (*SoftwareInventory, error) {
	inventory := &SoftwareInventory{
		Timestamp: time.Now(),
	}

	// Collect installed software
	if software, err := c.collectInstalledSoftware(); err == nil {
		inventory.InstalledSoftware = software
		inventory.TotalCount = len(software)
	}

	// Collect licensed software
	if licensed, err := c.collectLicensedSoftware(); err == nil {
		inventory.LicensedSoftware = licensed
	}

	// Collect available updates
	if updates, err := c.collectAvailableUpdates(); err == nil {
		inventory.UpdatesAvailable = updates
	}

	return inventory, nil
}

// collectInstalledSoftware collects installed software
func (c *SoftwareCollector) collectInstalledSoftware() ([]InstalledSoftware, error) {
	var software []InstalledSoftware

	switch runtime.GOOS {
	case "windows":
		software = c.collectWindowsSoftware()
	case "linux":
		software = c.collectLinuxSoftware()
	case "darwin":
		software = c.collectMacOSSoftware()
	}

	return software, nil
}

// collectWindowsSoftware collects Windows installed software
func (c *SoftwareCollector) collectWindowsSoftware() []InstalledSoftware {
	var software []InstalledSoftware

	// Query Windows Registry for installed software
	cmd := exec.Command("powershell", "-Command", `
		Get-ItemProperty HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\* |
		Select-Object DisplayName, DisplayVersion, Publisher, InstallDate |
		ConvertTo-Json
	`)

	output, err := cmd.Output()
	if err != nil {
		return software
	}

	// Parse JSON output
	// In production, properly parse the JSON
	lines := strings.Split(string(output), "\n")
	for _, line := range lines {
		if strings.Contains(line, "DisplayName") {
			// Simplified parsing
			software = append(software, InstalledSoftware{
				Name: strings.TrimSpace(line),
			})
		}
	}

	return software
}

// collectLinuxSoftware collects Linux installed software
func (c *SoftwareCollector) collectLinuxSoftware() []InstalledSoftware {
	var software []InstalledSoftware

	// Try dpkg (Debian/Ubuntu)
	if _, err := exec.LookPath("dpkg"); err == nil {
		cmd := exec.Command("dpkg", "-l")
		output, err := cmd.Output()
		if err == nil {
			lines := strings.Split(string(output), "\n")
			for _, line := range lines {
				if strings.HasPrefix(line, "ii") {
					fields := strings.Fields(line)
					if len(fields) >= 3 {
						software = append(software, InstalledSoftware{
							Name:    fields[1],
							Version: fields[2],
						})
					}
				}
			}
		}
	}

	// Try rpm (RedHat/CentOS)
	if _, err := exec.LookPath("rpm"); err == nil {
		cmd := exec.Command("rpm", "-qa", "--queryformat", "%{NAME} %{VERSION}\n")
		output, err := cmd.Output()
		if err == nil {
			lines := strings.Split(string(output), "\n")
			for _, line := range lines {
				fields := strings.Fields(line)
				if len(fields) >= 2 {
					software = append(software, InstalledSoftware{
						Name:    fields[0],
						Version: fields[1],
					})
				}
			}
		}
	}

	return software
}

// collectMacOSSoftware collects macOS installed software
func (c *SoftwareCollector) collectMacOSSoftware() []InstalledSoftware {
	var software []InstalledSoftware

	// List applications in /Applications
	cmd := exec.Command("ls", "-1", "/Applications")
	output, err := cmd.Output()
	if err == nil {
		lines := strings.Split(string(output), "\n")
		for _, line := range lines {
			if strings.HasSuffix(line, ".app") {
				name := strings.TrimSuffix(line, ".app")
				software = append(software, InstalledSoftware{
					Name: name,
				})
			}
		}
	}

	// Also check Homebrew
	if _, err := exec.LookPath("brew"); err == nil {
		cmd := exec.Command("brew", "list", "--versions")
		output, err := cmd.Output()
		if err == nil {
			lines := strings.Split(string(output), "\n")
			for _, line := range lines {
				fields := strings.Fields(line)
				if len(fields) >= 2 {
					software = append(software, InstalledSoftware{
						Name:    fields[0],
						Version: fields[1],
					})
				}
			}
		}
	}

	return software
}

// collectLicensedSoftware collects licensed software information
func (c *SoftwareCollector) collectLicensedSoftware() ([]LicensedSoftware, error) {
	var licensed []LicensedSoftware

	// This would integrate with iTechSmart License Server
	// For now, return empty list
	// In production, query the license server API

	return licensed, nil
}

// collectAvailableUpdates collects available software updates
func (c *SoftwareCollector) collectAvailableUpdates() ([]SoftwareUpdate, error) {
	var updates []SoftwareUpdate

	switch runtime.GOOS {
	case "windows":
		updates = c.collectWindowsUpdates()
	case "linux":
		updates = c.collectLinuxUpdates()
	case "darwin":
		updates = c.collectMacOSUpdates()
	}

	return updates, nil
}

// collectWindowsUpdates collects Windows updates
func (c *SoftwareCollector) collectWindowsUpdates() []SoftwareUpdate {
	var updates []SoftwareUpdate

	cmd := exec.Command("powershell", "-Command", `
		Get-WindowsUpdate | 
		Select-Object Title, KB, Severity |
		ConvertTo-Json
	`)

	output, err := cmd.Output()
	if err == nil {
		// Parse JSON output
		// Simplified for now
		lines := strings.Split(string(output), "\n")
		for _, line := range lines {
			if strings.Contains(line, "Title") {
				updates = append(updates, SoftwareUpdate{
					Name:       strings.TrimSpace(line),
					UpdateType: "security",
					Severity:   "high",
				})
			}
		}
	}

	return updates
}

// collectLinuxUpdates collects Linux updates
func (c *SoftwareCollector) collectLinuxUpdates() []SoftwareUpdate {
	var updates []SoftwareUpdate

	// Try apt
	if _, err := exec.LookPath("apt"); err == nil {
		cmd := exec.Command("apt", "list", "--upgradable")
		output, err := cmd.Output()
		if err == nil {
			lines := strings.Split(string(output), "\n")
			for _, line := range lines {
				if strings.Contains(line, "/") {
					fields := strings.Fields(line)
					if len(fields) >= 2 {
						updates = append(updates, SoftwareUpdate{
							Name:             fields[0],
							AvailableVersion: fields[1],
							UpdateType:       "feature",
							Severity:         "medium",
						})
					}
				}
			}
		}
	}

	return updates
}

// collectMacOSUpdates collects macOS updates
func (c *SoftwareCollector) collectMacOSUpdates() []SoftwareUpdate {
	var updates []SoftwareUpdate

	cmd := exec.Command("softwareupdate", "-l")
	output, err := cmd.Output()
	if err == nil {
		lines := strings.Split(string(output), "\n")
		for _, line := range lines {
			if strings.Contains(line, "*") {
				updates = append(updates, SoftwareUpdate{
					Name:       strings.TrimSpace(line),
					UpdateType: "feature",
					Severity:   "medium",
				})
			}
		}
	}

	return updates
}