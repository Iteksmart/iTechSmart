package main

import (
	"context"
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/iteksmart/itechsmart-agent/internal/agent"
	"github.com/iteksmart/itechsmart-agent/internal/config"
	"github.com/iteksmart/itechsmart-agent/internal/logger"
	"github.com/spf13/cobra"
)

var (
	version   = "1.0.0"
	buildDate = "2025-11-17"
	cfgFile   string
)

func main() {
	rootCmd := &cobra.Command{
		Use:   "itechsmart-agent",
		Short: "iTechSmart Agent - System monitoring and management",
		Long: `iTechSmart Agent is a lightweight, cross-platform system monitoring 
and management agent that communicates with the iTechSmart Cloud Platform.

Features:
  - Real-time system monitoring (CPU, Memory, Disk, Network)
  - Security and compliance checks
  - Software inventory and management
  - Remote command execution
  - Automated patch management
  - Proactive alerts and notifications
  - Comprehensive audit logging

Copyright © 2025 iTechSmart Inc. All rights reserved.`,
		Version: fmt.Sprintf("%s (built on %s)", version, buildDate),
		RunE:    runAgent,
	}

	rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default is /etc/itechsmart/agent.yaml)")
	rootCmd.AddCommand(versionCmd())
	rootCmd.AddCommand(installCmd())
	rootCmd.AddCommand(uninstallCmd())
	rootCmd.AddCommand(statusCmd())

	if err := rootCmd.Execute(); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}

func runAgent(cmd *cobra.Command, args []string) error {
	// Load configuration
	cfg, err := config.Load(cfgFile)
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	// Initialize logger
	log, err := logger.New(cfg.LogLevel, cfg.LogFile)
	if err != nil {
		return fmt.Errorf("failed to initialize logger: %w", err)
	}
	defer log.Sync()

	log.Info("Starting iTechSmart Agent",
		"version", version,
		"build_date", buildDate,
		"platform", cfg.Platform,
	)

	// Create agent instance
	agentInstance, err := agent.New(cfg, log)
	if err != nil {
		return fmt.Errorf("failed to create agent: %w", err)
	}

	// Create context with cancellation
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	// Start agent
	if err := agentInstance.Start(ctx); err != nil {
		return fmt.Errorf("failed to start agent: %w", err)
	}

	log.Info("iTechSmart Agent started successfully")

	// Wait for shutdown signal
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt, syscall.SIGTERM, syscall.SIGQUIT)
	
	sig := <-sigChan
	log.Info("Received shutdown signal", "signal", sig.String())

	// Graceful shutdown
	log.Info("Shutting down iTechSmart Agent...")
	if err := agentInstance.Stop(); err != nil {
		log.Error("Error during shutdown", "error", err)
		return err
	}

	log.Info("iTechSmart Agent stopped successfully")
	return nil
}

func versionCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "version",
		Short: "Print version information",
		Run: func(cmd *cobra.Command, args []string) {
			fmt.Printf("iTechSmart Agent v%s\n", version)
			fmt.Printf("Build Date: %s\n", buildDate)
			fmt.Printf("Copyright © 2025 iTechSmart Inc. All rights reserved.\n")
		},
	}
}

func installCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "install",
		Short: "Install iTechSmart Agent as a system service",
		RunE: func(cmd *cobra.Command, args []string) error {
			fmt.Println("Installing iTechSmart Agent as system service...")
			// Service installation logic will be implemented per platform
			return fmt.Errorf("not implemented yet - use platform-specific installer")
		},
	}
}

func uninstallCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "uninstall",
		Short: "Uninstall iTechSmart Agent system service",
		RunE: func(cmd *cobra.Command, args []string) error {
			fmt.Println("Uninstalling iTechSmart Agent...")
			// Service uninstallation logic will be implemented per platform
			return fmt.Errorf("not implemented yet - use platform-specific uninstaller")
		},
	}
}

func statusCmd() *cobra.Command {
	return &cobra.Command{
		Use:   "status",
		Short: "Check iTechSmart Agent status",
		RunE: func(cmd *cobra.Command, args []string) error {
			fmt.Println("Checking iTechSmart Agent status...")
			// Status check logic will be implemented
			return fmt.Errorf("not implemented yet")
		},
	}
}