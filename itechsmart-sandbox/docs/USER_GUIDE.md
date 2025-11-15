# iTechSmart Sandbox - User Guide

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Dashboard](#dashboard)
4. [Managing Sandboxes](#managing-sandboxes)
5. [Code Editor](#code-editor)
6. [Resource Monitoring](#resource-monitoring)
7. [File Management](#file-management)
8. [Testing](#testing)
9. [Best Practices](#best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

iTechSmart Sandbox is a secure, isolated code execution environment designed for testing, development, and running code across multiple programming languages. It provides:

- **Secure Isolation**: Each sandbox runs in its own Docker container
- **GPU Support**: Optional GPU acceleration for ML/AI workloads
- **Resource Monitoring**: Real-time tracking of CPU, memory, GPU, disk, and network usage
- **Persistent Storage**: Volume support for data persistence
- **Snapshot Management**: Save and restore sandbox states
- **Multi-Language Support**: Python, JavaScript, TypeScript, Java, C++, Go, Rust, and more

---

## Getting Started

### Accessing the Platform

1. Navigate to `http://localhost:3033` in your web browser
2. You'll see the Dashboard with an overview of your sandboxes

### Creating Your First Sandbox

1. Click the **"Create Sandbox"** button on the Dashboard
2. Fill in the sandbox configuration:
   - **Name**: A descriptive name for your sandbox
   - **Base Image**: Select a Docker image (Python, Node.js, Ubuntu, etc.)
   - **GPU Type**: Optional - select if you need GPU acceleration
   - **Time to Live**: How long the sandbox should run before auto-termination
3. Click **"Create Sandbox"**
4. Wait for the sandbox to be created (status will change from "creating" to "running")

---

## Dashboard

The Dashboard provides an at-a-glance view of your sandbox environment:

### Statistics Cards

- **Total Sandboxes**: Total number of sandboxes you've created
- **Running**: Number of currently active sandboxes
- **Stopped**: Number of paused sandboxes
- **Creating**: Number of sandboxes being initialized

### Recent Sandboxes

View your most recently created sandboxes with:
- Sandbox name and base image
- Current status (running, stopped, creating, etc.)
- GPU type (if applicable)
- Creation time
- Time remaining before auto-termination
- Quick action buttons (Start, Stop, Terminate)

---

## Managing Sandboxes

### Sandbox List

Access the full list of sandboxes from the sidebar navigation:

1. Click **"Sandboxes"** in the sidebar
2. Use the search bar to find specific sandboxes
3. Filter by status using the dropdown menu

### Sandbox Actions

#### Starting a Sandbox

1. Find the stopped sandbox
2. Click the **"Start"** button
3. Wait for status to change to "running"

#### Stopping a Sandbox

1. Find the running sandbox
2. Click the **"Stop"** button
3. The sandbox will pause but retain its state

#### Terminating a Sandbox

1. Click the **"Terminate"** button
2. Confirm the action in the dialog
3. The sandbox and all its data will be permanently deleted

### Sandbox Details

Click on any sandbox card to view detailed information:

- **Status and Configuration**: Current state, image, GPU type
- **Time Information**: Created time, time remaining
- **Resource Metrics**: Real-time charts showing resource usage
- **Quick Actions**: Open code editor, view monitoring, manage files

---

## Code Editor

The integrated code editor allows you to write and execute code directly in your sandbox.

### Opening the Editor

1. From the Dashboard or Sandbox Details, click **"Open Code Editor"**
2. Or navigate to **"Code Editor"** in the sidebar

### Writing Code

1. Select your programming language from the dropdown
2. Write your code in the Monaco editor (same editor as VS Code)
3. The editor provides:
   - Syntax highlighting
   - Auto-completion
   - Line numbers
   - Code folding

### Running Code

1. Click the **"Run Code"** button
2. View output in the right panel
3. Errors will be displayed in red
4. Standard output appears in the output panel

### Supported Languages

- Python (3.10, 3.11)
- JavaScript (Node.js 18, 20)
- TypeScript
- Java
- C++
- Go
- Rust

### File Operations

- **Upload**: Click "Upload" to load code from your computer
- **Save**: Click "Save" to download your code
- Files are automatically named based on the selected language

---

## Resource Monitoring

Monitor your sandbox's resource usage in real-time.

### Available Metrics

#### CPU Usage
- Real-time CPU utilization percentage
- Historical data shown in line chart
- Helps identify CPU-intensive operations

#### Memory Usage
- Current memory consumption in MB and percentage
- Memory trends over time
- Useful for detecting memory leaks

#### GPU Utilization (if available)
- GPU usage percentage
- GPU memory consumption
- Only available for sandboxes with GPU support

#### Disk I/O
- Disk read operations (MB)
- Disk write operations (MB)
- Helps identify I/O bottlenecks

#### Network Traffic
- Network received (MB)
- Network transmitted (MB)
- Monitor data transfer rates

### Accessing Monitoring

1. Navigate to sandbox details
2. Scroll down to the "Resource Metrics" section
3. View real-time charts for all metrics
4. Or click **"View Monitoring"** for full-screen view

---

## File Management

Manage files within your sandbox environment.

### Uploading Files

1. Navigate to **"Files"** in the sidebar
2. Select your sandbox
3. Click **"Upload"** button
4. Choose files from your computer
5. Files are uploaded to the sandbox filesystem

### Downloading Files

1. Browse the file tree
2. Select the file you want to download
3. Click the **"Download"** button
4. File will be saved to your computer

### File Operations

- **Create**: Create new files or directories
- **Delete**: Remove files or directories
- **Rename**: Change file or directory names
- **Navigate**: Browse through the directory structure

### Snapshots

Save the current state of your sandbox:

1. Click **"Create Snapshot"**
2. Enter a name and description
3. The snapshot is saved
4. Restore later by clicking **"Restore"** on the snapshot

---

## Testing

Run automated tests for iTechSmart products within sandboxes.

### Running Tests

1. Navigate to **"Tests"** in the sidebar
2. Select your sandbox
3. Choose the product to test
4. Select test type
5. Click **"Run Test"**

### Test Types

- **Unit Tests**: Test individual components
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Measure performance metrics

### Viewing Results

- Test status (pending, running, passed, failed)
- Detailed results and logs
- Error messages for failed tests
- Test history and trends

---

## Best Practices

### Resource Management

1. **Set Appropriate TTL**: Choose a time-to-live that matches your needs
2. **Stop Unused Sandboxes**: Stop sandboxes when not in use to save resources
3. **Monitor Resource Usage**: Keep an eye on CPU, memory, and disk usage
4. **Clean Up**: Terminate sandboxes you no longer need

### Security

1. **Don't Store Sensitive Data**: Sandboxes are temporary environments
2. **Use Snapshots**: Save important work before termination
3. **Review Code**: Always review code before execution
4. **Limit Permissions**: Use appropriate base images with minimal permissions

### Performance

1. **Choose Right Image**: Select the most appropriate base image
2. **Use GPU When Needed**: Enable GPU for ML/AI workloads
3. **Optimize Code**: Write efficient code to minimize resource usage
4. **Monitor Metrics**: Use monitoring to identify bottlenecks

### Development Workflow

1. **Create Template**: Save common configurations as templates
2. **Use Snapshots**: Create snapshots at key milestones
3. **Test Incrementally**: Test code changes in small increments
4. **Document Work**: Keep notes on sandbox configurations

---

## Troubleshooting

### Sandbox Won't Start

**Problem**: Sandbox stuck in "creating" status

**Solutions**:
1. Wait a few minutes - creation can take time
2. Check if the base image is valid
3. Verify sufficient system resources
4. Try terminating and recreating

### Code Execution Fails

**Problem**: Code doesn't run or produces errors

**Solutions**:
1. Check syntax errors in your code
2. Verify the correct language is selected
3. Ensure required dependencies are installed
4. Check sandbox logs for detailed errors

### High Resource Usage

**Problem**: Sandbox consuming too many resources

**Solutions**:
1. Review your code for inefficiencies
2. Check for infinite loops or memory leaks
3. Consider using a more powerful base image
4. Enable GPU if running ML/AI workloads

### Connection Issues

**Problem**: Can't connect to sandbox or API

**Solutions**:
1. Check your internet connection
2. Verify the backend is running
3. Check firewall settings
4. Try refreshing the page

### File Upload Fails

**Problem**: Can't upload files to sandbox

**Solutions**:
1. Check file size (must be under limit)
2. Verify sandbox is running
3. Ensure sufficient disk space
4. Try uploading smaller files

### Snapshot Restore Fails

**Problem**: Can't restore from snapshot

**Solutions**:
1. Verify snapshot exists and is valid
2. Check if sandbox is stopped
3. Ensure sufficient resources
4. Try creating a new sandbox from snapshot

---

## Getting Help

If you encounter issues not covered in this guide:

1. Check the [API Documentation](./API.md)
2. Review the [Architecture Guide](./ARCHITECTURE.md)
3. Contact iTechSmart Inc. support
4. Visit our documentation portal

---

## Appendix

### Keyboard Shortcuts (Code Editor)

- `Ctrl/Cmd + S`: Save code
- `Ctrl/Cmd + Enter`: Run code
- `Ctrl/Cmd + /`: Toggle comment
- `Ctrl/Cmd + F`: Find
- `Ctrl/Cmd + H`: Replace

### Common Base Images

- `python:3.11`: Python 3.11 with pip
- `python:3.10`: Python 3.10 with pip
- `node:20`: Node.js 20 with npm
- `node:18`: Node.js 18 with npm
- `ubuntu:22.04`: Ubuntu 22.04 LTS
- `ubuntu:20.04`: Ubuntu 20.04 LTS

### GPU Types

- **T4**: NVIDIA Tesla T4 (16GB, good for inference)
- **A10G**: NVIDIA A10G (24GB, balanced performance)
- **V100**: NVIDIA V100 (16GB/32GB, high performance)
- **A100**: NVIDIA A100 (40GB/80GB, top performance)

---

**Last Updated**: August 8, 2025  
**Version**: 1.0.0  
**Copyright**: © 2025 iTechSmart Inc.. All rights reserved.