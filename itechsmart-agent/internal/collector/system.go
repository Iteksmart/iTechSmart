package collector

import (
	"runtime"
	"time"

	"github.com/shirou/gopsutil/v3/cpu"
	"github.com/shirou/gopsutil/v3/disk"
	"github.com/shirou/gopsutil/v3/host"
	"github.com/shirou/gopsutil/v3/mem"
	"github.com/shirou/gopsutil/v3/net"
)

// SystemMetrics represents system-level metrics
type SystemMetrics struct {
	Timestamp    time.Time         `json:"timestamp"`
	Hostname     string            `json:"hostname"`
	OS           string            `json:"os"`
	Platform     string            `json:"platform"`
	Architecture string            `json:"architecture"`
	CPUInfo      CPUMetrics        `json:"cpu"`
	MemoryInfo   MemoryMetrics     `json:"memory"`
	DiskInfo     []DiskMetrics     `json:"disks"`
	NetworkInfo  []NetworkMetrics  `json:"network"`
	Uptime       uint64            `json:"uptime"`
	BootTime     uint64            `json:"boot_time"`
	Processes    int               `json:"processes"`
}

// CPUMetrics represents CPU metrics
type CPUMetrics struct {
	UsagePercent float64   `json:"usage_percent"`
	Cores        int       `json:"cores"`
	ModelName    string    `json:"model_name"`
	PerCoreUsage []float64 `json:"per_core_usage"`
}

// MemoryMetrics represents memory metrics
type MemoryMetrics struct {
	Total       uint64  `json:"total"`
	Available   uint64  `json:"available"`
	Used        uint64  `json:"used"`
	UsedPercent float64 `json:"used_percent"`
	Free        uint64  `json:"free"`
	SwapTotal   uint64  `json:"swap_total"`
	SwapUsed    uint64  `json:"swap_used"`
	SwapFree    uint64  `json:"swap_free"`
}

// DiskMetrics represents disk metrics
type DiskMetrics struct {
	Device      string  `json:"device"`
	MountPoint  string  `json:"mount_point"`
	FSType      string  `json:"fs_type"`
	Total       uint64  `json:"total"`
	Free        uint64  `json:"free"`
	Used        uint64  `json:"used"`
	UsedPercent float64 `json:"used_percent"`
}

// NetworkMetrics represents network interface metrics
type NetworkMetrics struct {
	Interface   string `json:"interface"`
	BytesSent   uint64 `json:"bytes_sent"`
	BytesRecv   uint64 `json:"bytes_recv"`
	PacketsSent uint64 `json:"packets_sent"`
	PacketsRecv uint64 `json:"packets_recv"`
	ErrorsIn    uint64 `json:"errors_in"`
	ErrorsOut   uint64 `json:"errors_out"`
	DropsIn     uint64 `json:"drops_in"`
	DropsOut    uint64 `json:"drops_out"`
}

// SystemCollector collects system metrics
type SystemCollector struct{}

// NewSystemCollector creates a new system collector
func NewSystemCollector() *SystemCollector {
	return &SystemCollector{}
}

// Collect collects all system metrics
func (c *SystemCollector) Collect() (*SystemMetrics, error) {
	metrics := &SystemMetrics{
		Timestamp:    time.Now(),
		OS:           runtime.GOOS,
		Architecture: runtime.GOARCH,
	}

	// Host information
	if hostInfo, err := host.Info(); err == nil {
		metrics.Hostname = hostInfo.Hostname
		metrics.Platform = hostInfo.Platform
		metrics.Uptime = hostInfo.Uptime
		metrics.BootTime = hostInfo.BootTime
		metrics.Processes = int(hostInfo.Procs)
	}

	// CPU metrics
	if cpuInfo, err := c.collectCPUMetrics(); err == nil {
		metrics.CPUInfo = *cpuInfo
	}

	// Memory metrics
	if memInfo, err := c.collectMemoryMetrics(); err == nil {
		metrics.MemoryInfo = *memInfo
	}

	// Disk metrics
	if diskInfo, err := c.collectDiskMetrics(); err == nil {
		metrics.DiskInfo = diskInfo
	}

	// Network metrics
	if netInfo, err := c.collectNetworkMetrics(); err == nil {
		metrics.NetworkInfo = netInfo
	}

	return metrics, nil
}

// collectCPUMetrics collects CPU metrics
func (c *SystemCollector) collectCPUMetrics() (*CPUMetrics, error) {
	metrics := &CPUMetrics{
		Cores: runtime.NumCPU(),
	}

	// Overall CPU usage
	if percent, err := cpu.Percent(time.Second, false); err == nil && len(percent) > 0 {
		metrics.UsagePercent = percent[0]
	}

	// Per-core CPU usage
	if perCore, err := cpu.Percent(time.Second, true); err == nil {
		metrics.PerCoreUsage = perCore
	}

	// CPU info
	if cpuInfo, err := cpu.Info(); err == nil && len(cpuInfo) > 0 {
		metrics.ModelName = cpuInfo[0].ModelName
	}

	return metrics, nil
}

// collectMemoryMetrics collects memory metrics
func (c *SystemCollector) collectMemoryMetrics() (*MemoryMetrics, error) {
	metrics := &MemoryMetrics{}

	// Virtual memory
	if vmem, err := mem.VirtualMemory(); err == nil {
		metrics.Total = vmem.Total
		metrics.Available = vmem.Available
		metrics.Used = vmem.Used
		metrics.UsedPercent = vmem.UsedPercent
		metrics.Free = vmem.Free
	}

	// Swap memory
	if swap, err := mem.SwapMemory(); err == nil {
		metrics.SwapTotal = swap.Total
		metrics.SwapUsed = swap.Used
		metrics.SwapFree = swap.Free
	}

	return metrics, nil
}

// collectDiskMetrics collects disk metrics
func (c *SystemCollector) collectDiskMetrics() ([]DiskMetrics, error) {
	var metrics []DiskMetrics

	// Get all partitions
	partitions, err := disk.Partitions(false)
	if err != nil {
		return nil, err
	}

	for _, partition := range partitions {
		usage, err := disk.Usage(partition.Mountpoint)
		if err != nil {
			continue
		}

		metrics = append(metrics, DiskMetrics{
			Device:      partition.Device,
			MountPoint:  partition.Mountpoint,
			FSType:      partition.Fstype,
			Total:       usage.Total,
			Free:        usage.Free,
			Used:        usage.Used,
			UsedPercent: usage.UsedPercent,
		})
	}

	return metrics, nil
}

// collectNetworkMetrics collects network metrics
func (c *SystemCollector) collectNetworkMetrics() ([]NetworkMetrics, error) {
	var metrics []NetworkMetrics

	// Get network IO counters
	ioCounters, err := net.IOCounters(true)
	if err != nil {
		return nil, err
	}

	for _, counter := range ioCounters {
		metrics = append(metrics, NetworkMetrics{
			Interface:   counter.Name,
			BytesSent:   counter.BytesSent,
			BytesRecv:   counter.BytesRecv,
			PacketsSent: counter.PacketsSent,
			PacketsRecv: counter.PacketsRecv,
			ErrorsIn:    counter.Errin,
			ErrorsOut:   counter.Errout,
			DropsIn:     counter.Dropin,
			DropsOut:    counter.Dropout,
		})
	}

	return metrics, nil
}