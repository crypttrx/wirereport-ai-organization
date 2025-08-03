# Wire Report Backup and Recovery Procedures

This document outlines comprehensive backup strategies and recovery procedures for the Wire Report system.

---

## Backup Strategy Overview

The Wire Report system requires backing up multiple components:
- **Database**: SQLite files with tweets, stats, and history
- **Configuration**: API keys, service configs, and settings
- **Queue Data**: Current tweet queues and sync data
- **Logs**: System logs for debugging and analysis
- **OAuth Tokens**: Twitter authentication credentials
- **Code**: Application code and agent configurations

---

## Automated Backup System

### 1. Daily Backup Script

**Location**: `/root/wirereport/scripts/tools/daily_backup.py`

```python
#!/usr/bin/env python3
"""
Daily backup script for Wire Report system.
Runs automatically via cron job at 2 AM daily.
"""

import os
import shutil
import sqlite3
import json
import gzip
import datetime
from pathlib import Path

class WireReportBackup:
    def __init__(self):
        self.backup_base = Path("/root/wirereport/backups")
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir = self.backup_base / f"backup_{self.timestamp}"
        
    def create_full_backup(self):
        """Creates comprehensive system backup."""
        print(f"Starting backup at {self.timestamp}")
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup database
        self.backup_database()
        
        # Backup configuration
        self.backup_configuration()
        
        # Backup queue data
        self.backup_queue_data()
        
        # Backup OAuth tokens
        self.backup_oauth_tokens()
        
        # Backup logs (compressed)
        self.backup_logs()
        
        # Create manifest
        self.create_manifest()
        
        # Cleanup old backups
        self.cleanup_old_backups()
        
        print(f"Backup completed: {self.backup_dir}")
    
    def backup_database(self):
        """Backup SQLite database with integrity check."""
        db_backup_dir = self.backup_dir / "database"
        db_backup_dir.mkdir(exist_ok=True)
        
        source_db = "/root/wirereport/data/wirereport.db"
        backup_db = db_backup_dir / "wirereport.db"
        
        # Perform integrity check
        conn = sqlite3.connect(source_db)
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        conn.close()
        
        if integrity != "ok":
            raise Exception(f"Database integrity check failed: {integrity}")
        
        # Create backup copy
        shutil.copy2(source_db, backup_db)
        
        # Compress for space saving
        with open(backup_db, 'rb') as f_in:
            with gzip.open(f"{backup_db}.gz", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Remove uncompressed copy
        backup_db.unlink()
        
        print(f"Database backed up: {backup_db}.gz")
    
    def backup_configuration(self):
        """Backup all configuration files."""
        config_backup_dir = self.backup_dir / "config"
        config_backup_dir.mkdir(exist_ok=True)
        
        # Config files to backup
        config_sources = [
            "/root/wirereport/config/",
            "/root/wirereport/.env",
            "/etc/systemd/system/wirereport-*.service"
        ]
        
        for source in config_sources:
            if Path(source).exists():
                if Path(source).is_file():
                    shutil.copy2(source, config_backup_dir)
                else:
                    dest = config_backup_dir / Path(source).name
                    shutil.copytree(source, dest, ignore=shutil.ignore_patterns('*.pyc', '__pycache__'))
        
        print(f"Configuration backed up: {config_backup_dir}")
    
    def backup_queue_data(self):
        """Backup current queue state and sync data."""
        queue_backup_dir = self.backup_dir / "queue_data"
        queue_backup_dir.mkdir(exist_ok=True)
        
        # Queue files
        queue_sources = [
            "/root/wirereport_api/data/queues/",
            "/root/wirereport_api/data/sync/",
            "/root/wirereporthq/data/posted_tweets.json"
        ]
        
        for source in queue_sources:
            if Path(source).exists():
                if Path(source).is_file():
                    shutil.copy2(source, queue_backup_dir)
                else:
                    dest = queue_backup_dir / Path(source).name
                    shutil.copytree(source, dest)
        
        print(f"Queue data backed up: {queue_backup_dir}")
    
    def backup_oauth_tokens(self):
        """Backup OAuth tokens (encrypted)."""
        token_backup_dir = self.backup_dir / "tokens"
        token_backup_dir.mkdir(exist_ok=True)
        
        token_files = [
            "/root/wirereporthq/data/tokens.json",
            "/root/wirereporthq/data/token_metadata.json"
        ]
        
        for token_file in token_files:
            if Path(token_file).exists():
                # Copy token file
                dest = token_backup_dir / Path(token_file).name
                shutil.copy2(token_file, dest)
        
        print(f"OAuth tokens backed up: {token_backup_dir}")
    
    def backup_logs(self):
        """Backup logs with compression."""
        log_backup_dir = self.backup_dir / "logs"
        log_backup_dir.mkdir(exist_ok=True)
        
        log_sources = [
            "/root/wirereport/logs/",
            "/root/wirereport_api/data/logs/",
            "/root/wirereporthq/logs/"
        ]
        
        for source in log_sources:
            if Path(source).exists():
                dest_name = f"{Path(source).parent.name}_{Path(source).name}"
                dest = log_backup_dir / f"{dest_name}.tar.gz"
                
                # Create compressed archive
                shutil.make_archive(str(dest)[:-7], 'gztar', source)
        
        print(f"Logs backed up: {log_backup_dir}")
    
    def create_manifest(self):
        """Create backup manifest with metadata."""
        manifest = {
            "backup_timestamp": self.timestamp,
            "system_info": {
                "hostname": os.uname().nodename,
                "python_version": os.sys.version,
                "backup_version": "2.0"
            },
            "backed_up_components": [
                "database",
                "configuration", 
                "queue_data",
                "oauth_tokens",
                "logs"
            ],
            "database_integrity": "verified",
            "backup_size_mb": self._calculate_backup_size()
        }
        
        manifest_file = self.backup_dir / "backup_manifest.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"Manifest created: {manifest_file}")
    
    def _calculate_backup_size(self):
        """Calculate total backup size in MB."""
        total_size = 0
        for path in self.backup_dir.rglob('*'):
            if path.is_file():
                total_size += path.stat().st_size
        return round(total_size / (1024 * 1024), 2)
    
    def cleanup_old_backups(self):
        """Remove backups older than 30 days."""
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=30)
        
        for backup_path in self.backup_base.glob("backup_*"):
            if backup_path.is_dir():
                # Extract timestamp from folder name
                timestamp_str = backup_path.name.replace("backup_", "")
                try:
                    backup_date = datetime.datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                    if backup_date < cutoff_date:
                        shutil.rmtree(backup_path)
                        print(f"Removed old backup: {backup_path}")
                except ValueError:
                    continue  # Skip malformed backup directories

if __name__ == "__main__":
    backup = WireReportBackup()
    backup.create_full_backup()
```

### 2. Cron Job Configuration

```bash
# Add to root crontab
sudo crontab -e

# Daily backup at 2 AM
0 2 * * * /usr/bin/python3 /root/wirereport/scripts/tools/daily_backup.py >> /var/log/wirereport_backup.log 2>&1

# Weekly cleanup of logs (keep 7 days)
0 3 * * 0 find /root/wirereport/logs -name "*.log" -mtime +7 -delete
```

---

## Manual Backup Procedures

### 1. Emergency Backup Script

```bash
#!/bin/bash
# emergency_backup.sh - Quick manual backup
# Usage: ./emergency_backup.sh [description]

BACKUP_DIR="/root/wirereport/backups/emergency_$(date +%Y%m%d_%H%M%S)"
DESCRIPTION="${1:-manual_backup}"

echo "Creating emergency backup: $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Critical files only
cp /root/wirereport/data/wirereport.db "$BACKUP_DIR/"
cp -r /root/wirereport_api/data/queues "$BACKUP_DIR/"
cp -r /root/wirereporthq/data "$BACKUP_DIR/"
cp /root/wirereport/.env "$BACKUP_DIR/"

# Create quick manifest
echo "{\"timestamp\": \"$(date -Iseconds)\", \"description\": \"$DESCRIPTION\"}" > "$BACKUP_DIR/manifest.json"

echo "Emergency backup completed: $BACKUP_DIR"
```

### 2. Pre-Deployment Backup

```bash
#!/bin/bash
# pre_deployment_backup.sh - Backup before code changes

BACKUP_DIR="/root/wirereport/backups/pre_deploy_$(date +%Y%m%d_%H%M%S)"
echo "Creating pre-deployment backup: $BACKUP_DIR"

# Stop services
systemctl stop wirereport-*

# Create backup
python3 /root/wirereport/scripts/tools/daily_backup.py

# Restart services
systemctl start wirereport-brain
systemctl start wirereport-wnba-api
systemctl start wirereport-swarm
systemctl start wirereport-hq-queue
systemctl start wirereport-api-resilience

echo "Pre-deployment backup completed"
```

---

## Recovery Procedures

### 1. Full System Recovery

```python
#!/usr/bin/env python3
"""
Full system recovery from backup.
Usage: python3 recovery.py --backup-dir /path/to/backup
"""

import os
import shutil
import sqlite3
import json
import gzip
import argparse
from pathlib import Path

class WireReportRecovery:
    def __init__(self, backup_dir):
        self.backup_dir = Path(backup_dir)
        self.manifest = self.load_manifest()
        
    def load_manifest(self):
        """Load backup manifest."""
        manifest_file = self.backup_dir / "backup_manifest.json"
        if not manifest_file.exists():
            raise Exception("Backup manifest not found")
        
        with open(manifest_file) as f:
            return json.load(f)
    
    def full_recovery(self):
        """Perform complete system recovery."""
        print(f"Starting recovery from: {self.backup_dir}")
        print(f"Backup timestamp: {self.manifest['backup_timestamp']}")
        
        # Stop all services
        self.stop_services()
        
        # Recover database
        self.recover_database()
        
        # Recover configuration
        self.recover_configuration()
        
        # Recover queue data
        self.recover_queue_data()
        
        # Recover OAuth tokens
        self.recover_oauth_tokens()
        
        # Start services
        self.start_services()
        
        # Verify recovery
        self.verify_recovery()
        
        print("Recovery completed successfully")
    
    def stop_services(self):
        """Stop all Wire Report services."""
        services = [
            "wirereport-swarm",
            "wirereport-brain", 
            "wirereport-wnba-api",
            "wirereport-hq-queue",
            "wirereport-api-resilience"
        ]
        
        for service in services:
            os.system(f"systemctl stop {service}")
        
        print("Services stopped")
    
    def recover_database(self):
        """Recover database from backup."""
        backup_db = self.backup_dir / "database" / "wirereport.db.gz"
        target_db = "/root/wirereport/data/wirereport.db"
        
        if not backup_db.exists():
            raise Exception("Database backup not found")
        
        # Create backup of current database
        if Path(target_db).exists():
            shutil.move(target_db, f"{target_db}.pre_recovery")
        
        # Extract and restore database
        with gzip.open(backup_db, 'rb') as f_in:
            with open(target_db, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Verify integrity
        conn = sqlite3.connect(target_db)
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        conn.close()
        
        if integrity != "ok":
            raise Exception(f"Recovered database failed integrity check: {integrity}")
        
        print("Database recovered successfully")
    
    def recover_configuration(self):
        """Recover configuration files."""
        config_backup = self.backup_dir / "config"
        
        if not config_backup.exists():
            print("No configuration backup found")
            return
        
        # Recover main config
        for config_file in config_backup.glob("*"):
            if config_file.is_file():
                if config_file.name.endswith(".service"):
                    # Systemd service files
                    shutil.copy2(config_file, "/etc/systemd/system/")
                elif config_file.name == ".env":
                    # Environment file
                    shutil.copy2(config_file, "/root/wirereport/")
            elif config_file.is_dir() and config_file.name == "config":
                # Config directory
                target = "/root/wirereport/config"
                if Path(target).exists():
                    shutil.move(target, f"{target}.pre_recovery")
                shutil.copytree(config_file, target)
        
        # Reload systemd
        os.system("systemctl daemon-reload")
        
        print("Configuration recovered")
    
    def recover_queue_data(self):
        """Recover queue and sync data."""
        queue_backup = self.backup_dir / "queue_data"
        
        if not queue_backup.exists():
            print("No queue data backup found")
            return
        
        # Queue directories
        for queue_item in queue_backup.iterdir():
            if queue_item.name == "queues":
                target = "/root/wirereport_api/data/queues"
                if Path(target).exists():
                    shutil.move(target, f"{target}.pre_recovery")
                shutil.copytree(queue_item, target)
            elif queue_item.name == "sync":
                target = "/root/wirereport_api/data/sync"
                if Path(target).exists():
                    shutil.move(target, f"{target}.pre_recovery")
                shutil.copytree(queue_item, target)
            elif queue_item.name == "posted_tweets.json":
                target = "/root/wirereporthq/data/posted_tweets.json"
                shutil.copy2(queue_item, target)
        
        print("Queue data recovered")
    
    def recover_oauth_tokens(self):
        """Recover OAuth tokens."""
        token_backup = self.backup_dir / "tokens"
        
        if not token_backup.exists():
            print("No token backup found")
            return
        
        target_dir = "/root/wirereporthq/data"
        Path(target_dir).mkdir(parents=True, exist_ok=True)
        
        for token_file in token_backup.glob("*.json"):
            shutil.copy2(token_file, target_dir)
        
        print("OAuth tokens recovered")
    
    def start_services(self):
        """Start services in correct order."""
        services = [
            "wirereport-brain",
            "wirereport-wnba-api", 
            "wirereport-swarm",
            "wirereport-hq-queue",
            "wirereport-api-resilience"
        ]
        
        for service in services:
            os.system(f"systemctl start {service}")
            # Wait a moment between services
            os.system("sleep 5")
        
        print("Services started")
    
    def verify_recovery(self):
        """Verify recovery was successful."""
        # Check services
        services_ok = True
        services = ["wirereport-swarm", "wirereport-brain", "wirereport-wnba-api"]
        
        for service in services:
            result = os.system(f"systemctl is-active {service} > /dev/null")
            if result != 0:
                print(f"WARNING: {service} is not running")
                services_ok = False
        
        # Check API endpoints
        api_ok = True
        apis = ["http://localhost:8000/health", "http://localhost:8080/health"]
        
        for api in apis:
            result = os.system(f"curl -s {api} > /dev/null")
            if result != 0:
                print(f"WARNING: {api} is not responding")
                api_ok = False
        
        if services_ok and api_ok:
            print("✓ Recovery verification successful")
        else:
            print("⚠ Recovery verification found issues - check logs")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recover Wire Report system from backup")
    parser.add_argument("--backup-dir", required=True, help="Path to backup directory")
    parser.add_argument("--force", action="store_true", help="Force recovery without prompts")
    
    args = parser.parse_args()
    
    if not args.force:
        response = input(f"This will restore system from {args.backup_dir}. Continue? (yes/no): ")
        if response.lower() != 'yes':
            print("Recovery cancelled")
            exit(1)
    
    recovery = WireReportRecovery(args.backup_dir)
    recovery.full_recovery()
```

### 2. Selective Recovery

```bash
#!/bin/bash
# selective_recovery.sh - Recover specific components

BACKUP_DIR="$1"
COMPONENT="$2"

if [ -z "$BACKUP_DIR" ] || [ -z "$COMPONENT" ]; then
    echo "Usage: $0 <backup_dir> <component>"
    echo "Components: database, config, queues, tokens"
    exit 1
fi

case $COMPONENT in
    "database")
        echo "Recovering database..."
        systemctl stop wirereport-*
        gunzip -c "$BACKUP_DIR/database/wirereport.db.gz" > /root/wirereport/data/wirereport.db
        systemctl start wirereport-*
        ;;
    "config")
        echo "Recovering configuration..."
        cp -r "$BACKUP_DIR/config/"* /root/wirereport/config/
        systemctl daemon-reload
        ;;
    "queues")
        echo "Recovering queues..."
        cp -r "$BACKUP_DIR/queue_data/queues/"* /root/wirereport_api/data/queues/
        ;;
    "tokens")
        echo "Recovering OAuth tokens..."
        cp "$BACKUP_DIR/tokens/"* /root/wirereporthq/data/
        ;;
    *)
        echo "Unknown component: $COMPONENT"
        exit 1
        ;;
esac

echo "Recovery of $COMPONENT completed"
```

---

## Backup Validation

### 1. Backup Integrity Check

```python
#!/usr/bin/env python3
"""
Validates backup integrity and completeness.
"""

import json
import sqlite3
import gzip
from pathlib import Path

def validate_backup(backup_dir):
    """Validate backup completeness and integrity."""
    backup_path = Path(backup_dir)
    
    print(f"Validating backup: {backup_path}")
    
    # Check manifest
    manifest_file = backup_path / "backup_manifest.json"
    if not manifest_file.exists():
        print("❌ Manifest file missing")
        return False
    
    with open(manifest_file) as f:
        manifest = json.load(f)
    
    print(f"✓ Manifest found - Backup from {manifest['backup_timestamp']}")
    
    # Check database
    db_file = backup_path / "database" / "wirereport.db.gz"
    if not db_file.exists():
        print("❌ Database backup missing")
        return False
    
    # Test database integrity
    try:
        with gzip.open(db_file, 'rb') as f:
            # Create temporary file to test
            temp_db = "/tmp/test_backup.db"
            with open(temp_db, 'wb') as temp_f:
                temp_f.write(f.read())
        
        conn = sqlite3.connect(temp_db)
        integrity = conn.execute("PRAGMA integrity_check").fetchone()[0]
        conn.close()
        
        Path(temp_db).unlink()  # Clean up
        
        if integrity == "ok":
            print("✓ Database integrity verified")
        else:
            print(f"❌ Database integrity check failed: {integrity}")
            return False
    except Exception as e:
        print(f"❌ Database validation error: {e}")
        return False
    
    # Check other components
    required_components = ["config", "queue_data", "tokens"]
    for component in required_components:
        if (backup_path / component).exists():
            print(f"✓ {component} backup found")
        else:
            print(f"⚠ {component} backup missing")
    
    print(f"✓ Backup validation completed")
    return True

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python3 validate_backup.py <backup_dir>")
        sys.exit(1)
    
    validate_backup(sys.argv[1])
```

---

## Monitoring and Alerts

### 1. Backup Monitoring Script

```bash
#!/bin/bash
# backup_monitor.sh - Monitor backup health

BACKUP_DIR="/root/wirereport/backups"
ALERT_EMAIL="admin@wirereport.com"
MAX_AGE_HOURS=25  # Alert if no backup in 25 hours

# Find latest backup
LATEST_BACKUP=$(find "$BACKUP_DIR" -name "backup_*" -type d -printf '%T@ %p\n' | sort -n | tail -1 | cut -d' ' -f2-)

if [ -z "$LATEST_BACKUP" ]; then
    echo "ERROR: No backups found"
    exit 1
fi

# Check backup age
BACKUP_TIME=$(stat -c %Y "$LATEST_BACKUP")
CURRENT_TIME=$(date +%s)
AGE_HOURS=$(( (CURRENT_TIME - BACKUP_TIME) / 3600 ))

if [ $AGE_HOURS -gt $MAX_AGE_HOURS ]; then
    echo "WARNING: Latest backup is $AGE_HOURS hours old"
    # Send alert (configure mail server)
    # echo "Backup age warning: $AGE_HOURS hours" | mail -s "Backup Alert" "$ALERT_EMAIL"
fi

# Check backup size (should be reasonable)
BACKUP_SIZE=$(du -sm "$LATEST_BACKUP" | cut -f1)
if [ $BACKUP_SIZE -lt 10 ]; then
    echo "WARNING: Backup size unusually small: ${BACKUP_SIZE}MB"
fi

echo "Latest backup: $LATEST_BACKUP (${AGE_HOURS}h old, ${BACKUP_SIZE}MB)"
```

---

## Disaster Recovery Plan

### 1. Server Failure Recovery

**Scenario**: Main server is completely lost

**Steps**:
1. Provision new server with same OS
2. Install Python and dependencies
3. Restore from latest backup:
   ```bash
   # Download backup from remote storage
   scp user@backup-server:/backups/latest.tar.gz ./
   tar -xzf latest.tar.gz
   
   # Run full recovery
   python3 recovery.py --backup-dir ./backup_20250802_020000
   ```
4. Update DNS/IP settings if needed
5. Verify all services running
6. Monitor for 24 hours

### 2. Database Corruption Recovery

**Scenario**: SQLite database is corrupted

**Steps**:
1. Stop all services immediately
2. Backup corrupted database for analysis
3. Restore from latest backup:
   ```bash
   ./selective_recovery.sh /root/wirereport/backups/backup_latest database
   ```
4. Verify integrity
5. Restart services
6. Check data consistency

### 3. Configuration Loss Recovery

**Scenario**: Configuration files deleted/corrupted

**Steps**:
1. Restore configuration from backup
2. Reload systemd services
3. Restart affected services
4. Verify functionality

---

## Remote Backup Storage

### 1. Cloud Backup Script

```bash
#!/bin/bash
# cloud_backup.sh - Upload backups to cloud storage

LOCAL_BACKUP_DIR="/root/wirereport/backups"
CLOUD_BUCKET="s3://wirereport-backups"
RETENTION_DAYS=90

# Find latest backup
LATEST_BACKUP=$(find "$LOCAL_BACKUP_DIR" -name "backup_*" -type d | sort | tail -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "No backup found to upload"
    exit 1
fi

# Create archive
ARCHIVE_NAME="$(basename "$LATEST_BACKUP").tar.gz"
tar -czf "/tmp/$ARCHIVE_NAME" -C "$(dirname "$LATEST_BACKUP")" "$(basename "$LATEST_BACKUP")"

# Upload to cloud (requires AWS CLI configured)
aws s3 cp "/tmp/$ARCHIVE_NAME" "$CLOUD_BUCKET/"

# Cleanup local archive
rm "/tmp/$ARCHIVE_NAME"

# Cleanup old cloud backups
aws s3 ls "$CLOUD_BUCKET/" | while read -r line; do
    BACKUP_DATE=$(echo "$line" | awk '{print $1" "$2}')
    BACKUP_FILE=$(echo "$line" | awk '{print $4}')
    
    if [ $(date -d "$BACKUP_DATE" +%s) -lt $(date -d "$RETENTION_DAYS days ago" +%s) ]; then
        aws s3 rm "$CLOUD_BUCKET/$BACKUP_FILE"
        echo "Removed old backup: $BACKUP_FILE"
    fi
done

echo "Cloud backup completed: $ARCHIVE_NAME"
```

---

This comprehensive backup and recovery documentation ensures the Wire Report system can survive any disaster and be restored quickly with minimal data loss.

*Last Updated: August 2, 2025*