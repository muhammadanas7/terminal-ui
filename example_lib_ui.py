#!/usr/bin/env python3
"""
Example usage of the Terminal UI Library
Demonstrates how to integrate terminal UI elements into your applications.
"""

import time
import random
import threading
from terminal_ui import (
    TerminalUI, SpinnerStyle, ProgressStyle, Theme, NotificationLevel,
    MatrixRain, FireEffect
)

def data_processing_simulation():
    """Simulate a data processing application with terminal UI"""
    ui = TerminalUI(theme=Theme.CYBERPUNK, speed_factor=1.2)
    
    ui.header("Data Processing System", "v1.2.3")
    
    # Initial setup
    ui.info("Initializing data processing system...")
    
    with ui.spinner("Loading configuration", SpinnerStyle.DOTS):
        time.sleep(1)
    
    ui.success("Configuration loaded")
    
    # Database connection simulation
    with ui.spinner("Connecting to database", SpinnerStyle.SNAKE, suffix=" (timeout: 30s)"):
        time.sleep(2)
    
    ui.success("Database connection established")
    
    # File processing with progress
    files_to_process = 250
    ui.info(f"Processing {files_to_process} files...")
    
    with ui.progress(f"Processing files", files_to_process, ProgressStyle.BLOCKS) as pbar:
        for i in range(files_to_process):
            # Simulate variable processing time
            if i % 50 == 0:
                time.sleep(0.05)  # Some files take longer
            elif i % 10 == 0:
                time.sleep(0.02)
            else:
                time.sleep(0.01)
            
            pbar.update(1)
            
            # Simulate occasional errors
            if random.random() < 0.02:  # 2% chance of warning
                ui.warning(f"File {i+1}: Minor formatting issue corrected")
    
    # Analysis phase
    ui.separator()
    ui.info("Starting data analysis...")
    
    analysis_steps = [
        ("Data validation", SpinnerStyle.CIRCLES, 1.5),
        ("Statistical analysis", SpinnerStyle.DOTS2, 2.0),
        ("Pattern recognition", SpinnerStyle.DNA, 1.8),
        ("Report generation", SpinnerStyle.BLOCKS, 1.2)
    ]
    
    for step_name, spinner_style, duration in analysis_steps:
        with ui.spinner(f"{step_name}...", spinner_style):
            time.sleep(duration)
        ui.success(f"{step_name} completed")
    
    # Results display
    ui.separator()
    ui.header("Analysis Results", "Summary Report")
    
    # Results table
    headers = ["Metric", "Value", "Status", "Threshold"]
    results = [
        ["Records processed", "250,000", "✓ Normal", "< 1M"],
        ["Error rate", "0.02%", "✓ Good", "< 5%"],
        ["Processing time", "47.3s", "✓ Fast", "< 60s"],
        ["Memory usage", "2.1 GB", "⚠ High", "< 4GB"],
        ["CPU utilization", "78%", "✓ Normal", "< 90%"]
    ]
    
    ui.table(headers, results, "Performance Metrics")
    
    # Final status
    ui.separator()
    ui.success("Data processing completed successfully!")
    ui.info("Reports saved to /var/reports/")
    ui.info("Next scheduled run: Tomorrow 02:00")

def network_monitoring_app():
    """Simulate a network monitoring application"""
    ui = TerminalUI(theme=Theme.MATRIX, speed_factor=1.5)
    
    ui.header("Network Monitoring System", "Real-time Network Analysis")
    
    # System startup
    services = [
        "Network interface scanner",
        "Packet capture engine", 
        "Traffic analyzer",
        "Security monitor",
        "Alert manager"
    ]
    
    ui.info("Starting network monitoring services...")
    for service in services:
        with ui.spinner(f"Starting {service}", SpinnerStyle.DOTS):
            time.sleep(random.uniform(0.5, 1.5))
        ui.success(f"{service} started")
    
    ui.separator()
    
    # Network scanning simulation
    ui.info("Scanning network interfaces...")
    interfaces = ["eth0", "wlan0", "lo", "docker0"]
    
    for interface in interfaces:
        with ui.progress(f"Scanning {interface}", 100, ProgressStyle.ARROWS) as pbar:
            for i in range(100):
                time.sleep(0.01)
                pbar.update(1)
        
        # Random status for each interface
        status = random.choice(["Active", "Inactive", "Monitoring"])
        if status == "Active":
            ui.success(f"{interface}: {status} - {random.randint(50, 500)} Mbps")
        elif status == "Monitoring":
            ui.info(f"{interface}: {status}")
        else:
            ui.warning(f"{interface}: {status}")
    
    # Security scan
    ui.separator()
    ui.info("Running security analysis...")
    
    with ui.monitor_performance("Port scan analysis"):
        with ui.spinner("Scanning for open ports", SpinnerStyle.MATRIX):
            time.sleep(3)
    
    # Simulate some security findings
    security_events = [
        ("SSH brute force attempt blocked", NotificationLevel.WARNING),
        ("Suspicious traffic pattern detected", NotificationLevel.ERROR),
        ("Firewall rules updated", NotificationLevel.SUCCESS),
        ("DDoS protection activated", NotificationLevel.CRITICAL)
    ]
    
    ui.info("Security events detected:")
    for event, level in security_events:
        ui.notify(event, level, prefix="SEC")
        time.sleep(0.5)
    
    # Network stats table
    ui.separator()
    headers = ["Interface", "RX (GB)", "TX (GB)", "Packets", "Errors"]
    network_stats = [
        ["eth0", "15.2", "8.7", "2,547,891", "0"],
        ["wlan0", "0.3", "0.1", "45,223", "2"],
        ["lo", "0.0", "0.0", "1,205", "0"],
        ["docker0", "1.8", "1.2", "892,441", "0"]
    ]
    
    ui.table(headers, network_stats, "Network Statistics")
    
    ui.success("Network monitoring active - Press Ctrl+C to stop")

def software_installation_wizard():
    """Simulate a software installation process"""
    ui = TerminalUI(theme=Theme.OCEAN, speed_factor=1.0)
    
    ui.header("Software Installation Wizard", "MyApp v2.1.0")
    
    # Pre-installation checks
    ui.info("Performing pre-installation checks...")
    
    checks = [
        ("System compatibility", True),
        ("Available disk space", True),
        ("Required dependencies", True),
        ("Administrator privileges", False),
        ("Network connectivity", True)
    ]
    
    for check_name, passed in checks:
        with ui.spinner(f"Checking {check_name}", SpinnerStyle.DOTS):
            time.sleep(random.uniform(0.5, 1.5))
        
        if passed:
            ui.success(f"{check_name}: OK")
        else:
            ui.error(f"{check_name}: FAILED")
            ui.warning("Installation cannot continue without administrator privileges")
            return
    
    ui.separator()
    
    # Download phase
    ui.info("Downloading installation packages...")
    
    packages = [
        ("Core application", 125, ProgressStyle.BLOCKS),
        ("Runtime libraries", 45, ProgressStyle.EQUALS),
        ("Documentation", 15, ProgressStyle.DOTS),
        ("Sample data", 80, ProgressStyle.GRADIENT)
    ]
    
    total_size = sum(size for _, size, _ in packages)
    ui.info(f"Total download size: {total_size} MB")
    
    for package_name, size_mb, style in packages:
        with ui.progress(f"Downloading {package_name}", size_mb, style) as pbar:
            # Simulate variable download speed
            chunk_size = random.randint(1, 5)
            while pbar.current < size_mb:
                time.sleep(0.05)
                remaining = size_mb - pbar.current
                to_download = min(chunk_size, remaining)
                pbar.update(to_download)
    
    ui.success("All packages downloaded successfully")
    
    # Installation phase
    ui.separator()
    ui.info("Installing software...")
    
    installation_steps = [
        ("Extracting files", 100, ProgressStyle.BLOCKS),
        ("Installing core components", 75, ProgressStyle.ARROWS),
        ("Configuring system integration", 25, ProgressStyle.PIPES),
        ("Setting up shortcuts", 10, ProgressStyle.SQUARES),
        ("Finalizing installation", 15, ProgressStyle.CIRCLES)
    ]
    
    for step_name, steps, style in installation_steps:
        with ui.progress(step_name, steps, style) as pbar:
            for i in range(steps):
                time.sleep(0.03)
                pbar.update(1)
                
                # Simulate occasional file conflicts
                if random.random() < 0.01:
                    ui.warning(f"File conflict resolved: {random.choice(['config.xml', 'readme.txt', 'license.pdf'])}")
    
    # Post-installation
    ui.separator()
    ui.success("Installation completed successfully!")
    
    # Installation summary
    summary = [
        "Installation completed in 2m 34s",
        "Installed to: /opt/myapp/",
        "Shortcuts created on desktop",
        "Documentation available at: /opt/myapp/docs/"
    ]
    
    ui.box(summary, "Installation Summary", "rounded")
    
    ui.info("Application ready to use!")

def system_backup_utility():
    """Simulate a system backup utility"""
    ui = TerminalUI(theme=Theme.SUNSET, speed_factor=2.0)
    
    ui.header("System Backup Utility", "Automated Backup Manager")
    
    # Backup configuration
    ui.info("Loading backup configuration...")
    
    backup_config = {
        "Source directories": ["/home/user/", "/etc/", "/var/log/", "/opt/"],
        "Destination": "/backup/daily/2024-01-15/",
        "Compression": "gzip",
        "Encryption": "AES-256",
        "Incremental": "Enabled"
    }
    
    config_data = [[key, str(value)] for key, value in backup_config.items()]
    ui.table(["Setting", "Value"], config_data, "Backup Configuration")
    
    ui.separator()
    
    # Analyzing source directories
    ui.info("Analyzing source directories...")
    
    directories = backup_config["Source directories"]
    total_files = 0
    total_size = 0
    
    for directory in directories:
        with ui.spinner(f"Scanning {directory}", SpinnerStyle.DOTS2):
            time.sleep(random.uniform(1.0, 2.0))
        
        files = random.randint(100, 5000)
        size_gb = random.uniform(0.5, 15.0)
        total_files += files
        total_size += size_gb
        
        ui.success(f"{directory}: {files:,} files ({size_gb:.1f} GB)")
    
    ui.info(f"Total: {total_files:,} files, {total_size:.1f} GB")
    
    # Backup process
    ui.separator()
    ui.info("Starting backup process...")
    
    # Phase 1: File copying
    with ui.progress("Copying files", total_files, ProgressStyle.GRADIENT) as pbar:
        files_processed = 0
        while files_processed < total_files:
            # Simulate variable processing speed
            batch_size = random.randint(10, 100)
            remaining = total_files - files_processed
            to_process = min(batch_size, remaining)
            
            time.sleep(0.1)  # Simulate I/O time
            pbar.update(to_process)
            files_processed += to_process
            
            # Simulate occasional issues
            if random.random() < 0.005:  # 0.5% chance
                ui.warning(f"Permission denied: {random.choice(['temp.log', 'cache.db', 'lock.file'])}")
    
    # Phase 2: Compression
    ui.info("Compressing backup archive...")
    with ui.spinner("Applying gzip compression", SpinnerStyle.BLOCKS):
        time.sleep(3)
    
    compressed_size = total_size * random.uniform(0.3, 0.7)  # Realistic compression
    ui.success(f"Compression completed: {total_size:.1f} GB → {compressed_size:.1f} GB ({((total_size-compressed_size)/total_size)*100:.1f}% saved)")
    
    # Phase 3: Encryption
    ui.info("Encrypting backup...")
    with ui.progress("Applying AES-256 encryption", int(compressed_size * 10), ProgressStyle.BLOCKS) as pbar:
        for i in range(int(compressed_size * 10)):
            time.sleep(0.05)
            pbar.update(1)
    
    # Phase 4: Verification
    ui.info("Verifying backup integrity...")
    with ui.spinner("Computing checksums", SpinnerStyle.DNA):
        time.sleep(2)
    
    ui.success("Backup verification passed")
    
    # Backup summary
    ui.separator()
    backup_summary = [
        f"Backup completed successfully",
        f"Files backed up: {total_files:,}",
        f"Original size: {total_size:.1f} GB",
        f"Compressed size: {compressed_size:.1f} GB",
        f"Backup location: {backup_config['Destination']}backup.tar.gz.enc",
        f"Duration: {random.randint(8, 25)} minutes"
    ]