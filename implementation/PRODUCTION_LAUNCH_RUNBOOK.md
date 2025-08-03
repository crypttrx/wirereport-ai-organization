# Wire Report Production Launch Runbook

## Overview
This runbook orchestrates the launch of the fully automated Wire Report system with 200+ agents operating across multiple accounts and platforms.

## Pre-Launch Status Check

### 1. System Services Verification
```bash
# Check all systemd services
systemctl status wirereport-swarm
systemctl status wirereport-brain  
systemctl status wirereport-wnba-api

# View recent logs
journalctl -u wirereport-swarm -n 100
journalctl -u wirereport-brain -n 100
journalctl -u wirereport-wnba-api -n 100
```

### 2. Configuration Validation
```bash
# Verify environment files
ls -la /root/wirereport/.env
ls -la /root/wirereport_api/.env

# Check secure config
python3 -c "from config.secure_config import get_twitter_credentials; print('✓ Config loaded')"

# Validate OAuth tokens
python3 scripts/check_api_config.py
```

### 3. Database & Queue Health
```bash
# Check Redis connectivity
redis-cli ping

# Verify queue status
python3 agents/check_wnba_queue.py

# Database integrity
python3 scripts/tools/check_database_integrity.py
```

## Launch Phases

### Phase 0: Pre-Production Validation (T-24 hours)

#### 0.1 Security Audit
```bash
# Run security audit
bash scripts/security_audit.sh

# Check for exposed credentials
grep -r "sk-" /root/wirereport/ --exclude-dir=.git
grep -r "Bearer" /root/wirereport/ --exclude-dir=.git

# Verify log masking
tail -n 1000 /root/wirereport/logs/*.log | grep -E "(api_key|secret|token)"
```

#### 0.2 Performance Baseline
```bash
# Test swarm response time
time python3 agents/test_swarm_media_enhancement.py

# Measure API latency
python3 scripts/tools/measure_api_performance.py

# Check memory usage
free -h
htop
```

#### 0.3 Content Quality Test
```bash
# Generate test tweets without posting
python3 scripts/test_both_accounts.py --dry-run

# Review generated content
cat /root/wirereport/data/test_tweets_*.json
```

### Phase 1: Monitoring Mode (T-12 hours)

#### 1.1 Enable Read-Only Mode
```python
# /root/wirereport/launch_phase1.py
import json
from pathlib import Path

# Set monitoring-only mode
config = {
    "mode": "monitoring",
    "posting_enabled": False,
    "queue_enabled": True,
    "filtering_enabled": True,
    "daily_limits": {
        "@wirereporthq": 0,
        "@wirereportwnba": 0
    }
}

Path("/root/wirereport/data/launch_config.json").write_text(json.dumps(config, indent=2))
print("✓ Phase 1: Monitoring mode enabled")
```

#### 1.2 Start Monitoring
```bash
# Launch monitoring dashboard
python3 agents/swarm_health_monitor.py --dashboard

# Watch queue activity
watch -n 5 'python3 agents/monitor_wnba_posts.py'

# Track API usage
python3 scripts/tools/monitor_api_usage.py --continuous
```

### Phase 2: Limited Testing (T-6 hours)

#### 2.1 Enable Limited Posting
```python
# /root/wirereport/launch_phase2.py
import json
from pathlib import Path

config = json.loads(Path("/root/wirereport/data/launch_config.json").read_text())
config.update({
    "mode": "limited_testing",
    "posting_enabled": True,
    "daily_limits": {
        "@wirereporthq": 2,
        "@wirereportwnba": 2
    },
    "test_hours": [10, 14, 18, 22]  # Spread throughout day
})

Path("/root/wirereport/data/launch_config.json").write_text(json.dumps(config, indent=2))
print("✓ Phase 2: Limited testing enabled (2 tweets/account)")
```

#### 2.2 Test Posts
```bash
# Send test tweet to each account
python3 scripts/send_test_tweet.py
python3 scripts/send_wnba_test.py

# Verify posts appeared
python3 agents/verify_posted_tweets.py

# Check engagement metrics
python3 scripts/engagement_metrics.py --last-hour
```

### Phase 3: Gradual Ramp-Up (T-3 hours)

#### 3.1 Increase Limits
```python
# /root/wirereport/launch_phase3.py
import json
from pathlib import Path

config = json.loads(Path("/root/wirereport/data/launch_config.json").read_text())
config.update({
    "mode": "ramp_up",
    "daily_limits": {
        "@wirereporthq": 8,
        "@wirereportwnba": 8
    },
    "quality_threshold": 0.8,  # Higher quality bar
    "duplicate_check_hours": 48  # Strict duplicate prevention
})

Path("/root/wirereport/data/launch_config.json").write_text(json.dumps(config, indent=2))
print("✓ Phase 3: Ramping up to 8 tweets/account")
```

#### 3.2 Monitor Performance
```bash
# Real-time monitoring
tail -f /root/wirereport/logs/swarm_master.log

# Queue health
watch -n 10 'redis-cli zcard wirereport_api:queue:wnba_queue'

# Error tracking
grep -i error /root/wirereport/logs/*.log | tail -20
```

### Phase 4: Full Production (T-0)

#### 4.1 Enable Full Automation
```python
# /root/wirereport/launch_phase4.py
import json
from pathlib import Path
from datetime import datetime

config = {
    "mode": "production",
    "posting_enabled": True,
    "queue_enabled": True,
    "filtering_enabled": True,
    "daily_limits": {
        "@wirereporthq": 17,
        "@wirereportwnba": 17
    },
    "quality_threshold": 0.75,
    "duplicate_check_hours": 24,
    "breaking_news_enabled": True,
    "launch_time": datetime.now().isoformat()
}

Path("/root/wirereport/data/launch_config.json").write_text(json.dumps(config, indent=2))
print("🚀 Phase 4: FULL PRODUCTION ENABLED")
print(f"✓ Both accounts active with 17 tweets/day limit")
print(f"✓ Breaking news monitoring active")
print(f"✓ 200+ agents operational")
```

#### 4.2 Final Verification
```bash
# Confirm all services running
systemctl status wirereport-* --no-pager

# Check swarm health
curl http://localhost:9999/health

# Verify brain API
curl http://localhost:8000/health

# Test WNBA queue
curl http://localhost:8080/health
```

## Emergency Procedures

### Emergency Stop
```bash
# Stop all posting immediately
systemctl stop wirereport-swarm
systemctl stop wirereport-brain
systemctl stop wirereport-wnba-api

# Clear queues
redis-cli FLUSHDB
```

### Rollback
```bash
# Restore previous configuration
cp /root/wirereport/data/launch_config.json.backup /root/wirereport/data/launch_config.json

# Restart with safe config
systemctl restart wirereport-swarm
```

### Manual Override
```python
# /root/wirereport/emergency_override.py
import redis
import json

r = redis.Redis()
r.set("wirereport:emergency_stop", "true", ex=3600)  # 1 hour stop
print("⚠️  Emergency stop activated for 1 hour")
```

## Success Criteria

### Phase 1 Success
- [ ] All services running without errors
- [ ] Monitoring shows game data flowing
- [ ] No unauthorized posts sent
- [ ] API rate limits respected

### Phase 2 Success
- [ ] Test tweets posted successfully
- [ ] No duplicate content
- [ ] Quality scores > 0.8
- [ ] Positive engagement metrics

### Phase 3 Success
- [ ] Sustained posting without issues
- [ ] Queue processing smooth
- [ ] Memory usage stable
- [ ] Error rate < 1%

### Phase 4 Success
- [ ] 24/7 autonomous operation
- [ ] Breaking news captured
- [ ] Daily limits respected
- [ ] Zero manual intervention needed

## Post-Launch Monitoring

### Daily Health Checks
```bash
# Morning check (9 AM)
python3 scripts/tools/daily_health_check.py

# Evening summary (6 PM)
python3 scripts/tools/daily_summary_report.py

# Weekly metrics
python3 scripts/tools/weekly_analytics.py
```

### Key Metrics Dashboard
- Posts per account
- Engagement rates
- API usage percentages
- Error rates
- Queue depths
- Response times

## Contact Information

### Escalation Path
1. Check logs: `journalctl -u wirereport-*`
2. Review monitoring: `http://localhost:9999/health`
3. Emergency stop if needed
4. Document issues in `/root/wirereport/logs/incidents/`

## Launch Authorization

Launch Commander: _________________
Date/Time: _______________________
Phase Completed: _________________
Notes: ___________________________