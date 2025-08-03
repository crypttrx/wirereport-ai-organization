# Wire Report Development Setup Guide

This guide provides step-by-step instructions for setting up a complete Wire Report development environment.

---

## Prerequisites

### System Requirements

- **OS**: Ubuntu 20.04+ or similar Linux distribution
- **Python**: 3.8+ (3.9 recommended)
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 10GB available space
- **Network**: Stable internet connection for API access

### Required Accounts & Keys

1. **Twitter Developer Account**
   - Apply at: https://developer.twitter.com/
   - Create app for OAuth 2.0 credentials
   - Note: Free tier allows 17 tweets/day per account

2. **OpenAI API Key**
   - Sign up at: https://platform.openai.com/
   - Generate API key in dashboard
   - Monitor usage to avoid overage

3. **RapidAPI Account**
   - Register at: https://rapidapi.com/
   - Subscribe to NBA/sports APIs
   - Copy API key from dashboard

4. **Kaggle API Credentials**
   - Create account at: https://www.kaggle.com/
   - Go to Account → Create New API Token
   - Download kaggle.json file

---

## Installation Steps

### 1. Clone Repository

```bash
# Create project directory
mkdir -p /root/wirereport_project
cd /root/wirereport_project

# If using git (recommended)
git clone <repository-url> wirereport
cd wirereport

# Or extract from archive
tar -xzf wirereport-v2.tar.gz
cd wirereport
```

### 2. Install Python Dependencies

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Python and pip
sudo apt install python3 python3-pip python3-venv -y

# Create virtual environment (recommended)
python3 -m venv wirereport_env
source wirereport_env/bin/activate

# Install requirements
pip install -r requirements.txt

# Additional dependencies for development
pip install pytest pytest-asyncio black flake8 mypy
```

### 3. Install System Dependencies

```bash
# Install SQLite
sudo apt install sqlite3 libsqlite3-dev -y

# Install Redis (for caching)
sudo apt install redis-server -y
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Install curl and jq (for testing)
sudo apt install curl jq -y

# Install FFmpeg (for video processing)
sudo apt install ffmpeg -y
```

### 4. Configure API Keys

```bash
# Create environment file
cp config/example.env .env

# Edit with your actual keys
nano .env
```

**Required Environment Variables**:
```bash
# Twitter OAuth 2.0
TWITTER_CLIENT_ID=your_client_id_here
TWITTER_CLIENT_SECRET=your_client_secret_here

# OpenAI
OPENAI_API_KEY=your_openai_key_here

# RapidAPI
RAPIDAPI_KEY=your_rapidapi_key_here

# Telegram (optional, for approval workflow)
TELEGRAM_BOT_TOKEN=your_telegram_token_here
TELEGRAM_CHAT_ID=your_chat_id_here

# System Configuration
PYTHONPATH=/root/wirereport
DEBUG=True
LOG_LEVEL=INFO
```

### 5. Setup Kaggle Integration

```bash
# Create kaggle directory
mkdir -p ~/.kaggle

# Copy credentials (download from kaggle.com)
cp kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# Test kaggle access
kaggle competitions list
```

### 6. Initialize Database

```bash
# Create database directory
mkdir -p data

# Initialize schema
python scripts/tools/initialize_database.py

# Verify database creation
sqlite3 data/wirereport.db ".tables"
```

### 7. Setup Directory Structure

```bash
# Create required directories
mkdir -p {data,logs,backups}
mkdir -p data/{cache,tokens,queues,sync}
mkdir -p logs/{swarm,brain,queue,posted}

# Set permissions
chmod 755 data logs backups
chmod 644 data/* logs/*
```

---

## Configuration Setup

### 1. Twitter OAuth 2.0 Setup

**For @wirereporthq account**:
```bash
# Create token directory
mkdir -p /root/wirereporthq/data

# Run OAuth setup script
python scripts/oauth_setup.py --account wirereporthq

# Follow prompts to authorize
# Tokens will be saved to /root/wirereporthq/data/tokens.json
```

**For @wirereportwnba account** (on remote server):
```bash
# Similar setup on remote server
python scripts/oauth_setup.py --account wirereportwnba
```

### 2. League Configuration

```bash
# Copy example configs
cp -r config/league_configs_example config/league_configs

# Customize for your needs
nano config/league_configs/nba_config.json
nano config/league_configs/wnba_config.json
```

### 3. Swarm Agent Configuration

```bash
# Configure agent settings
nano agents/swarm_master_runner.py

# Update account settings
accounts = [
    {
        "handle": "@wirereporthq",
        "leagues": ["NBA", "WNBA", "NFL", "NHL", "MLB"],
        "daily_limit": 17,
        "strategy": "mixed"
    },
    {
        "handle": "@wirereportwnba",
        "leagues": ["WNBA"],
        "daily_limit": 17,
        "strategy": "focused",
        "remote": True
    }
]
```

---

## Service Setup

### 1. Create Systemd Services

```bash
# Copy service files
sudo cp systemd/*.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable wirereport-swarm
sudo systemctl enable wirereport-brain
sudo systemctl enable wirereport-wnba-api
sudo systemctl enable wirereport-hq-queue
sudo systemctl enable wirereport-api-resilience
```

### 2. Start Core Services

```bash
# Start in order
sudo systemctl start wirereport-brain
sudo systemctl start wirereport-wnba-api
sudo systemctl start wirereport-swarm
sudo systemctl start wirereport-hq-queue
sudo systemctl start wirereport-api-resilience

# Check status
sudo systemctl status wirereport-swarm
```

### 3. Configure Service Dependencies

Edit service files to ensure proper startup order:

```bash
sudo nano /etc/systemd/system/wirereport-swarm.service
```

Add dependencies:
```ini
[Unit]
After=wirereport-brain.service wirereport-wnba-api.service
Requires=wirereport-brain.service wirereport-wnba-api.service
```

---

## API Server Configuration

### 1. Brain API Server

**Configuration** (`/root/wirereport/agents/brain_api_server.py`):
```python
# Server settings
HOST = "0.0.0.0"
PORT = 8000
DEBUG = True

# Rate limiting
RATE_LIMIT = 100  # requests per minute
```

### 2. Queue API Server

**Configuration** (`/root/wirereport_api/wnba_api_server.py`):
```python
# Server settings
HOST = "0.0.0.0"
PORT = 8080

# Allowed IPs (add your development IP)
ALLOWED_IPS = [
    "127.0.0.1",
    "::1",
    "155.138.211.147",  # WNBA server
    "YOUR_DEV_IP_HERE"
]
```

### 3. Rate Limit Manager

**Configuration** (`/root/wirereport_api/rate_limit_manager.py`):
```python
# Remote servers (update for your setup)
remote_servers = {
    "@wirereportwnba": {
        "ip": "YOUR_WNBA_SERVER_IP",
        "port": 8081,
        "health_endpoint": "/api/rate-limit/status"
    }
}
```

---

## Development Workflow

### 1. Daily Development Routine

```bash
# Activate virtual environment
source wirereport_env/bin/activate

# Update code
git pull origin main

# Install new dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Check services
systemctl status wirereport-*
```

### 2. Testing Commands

```bash
# Test both Twitter accounts
python scripts/test_both_accounts.py

# Test individual components
python scripts/test_nba_fetcher.py
python scripts/test_wnba_generator.py
python scripts/test_queue_system.py

# Test API endpoints
curl http://localhost:8000/health | jq .
curl http://localhost:8080/health | jq .
```

### 3. Debugging Tools

```bash
# Monitor logs in real-time
journalctl -u wirereport-swarm -f
journalctl -u wirereport-brain -f
journalctl -u wirereport-wnba-api -f

# Check queue status
cat /root/wirereport_api/data/queues/hq_queue.json | jq .
cat /root/wirereport_api/data/queues/wnba_queue.json | jq .

# Database inspection
sqlite3 data/wirereport.db "SELECT * FROM posted_tweets LIMIT 10;"
```

---

## Development Best Practices

### 1. Code Organization

```
/root/wirereport/
├── agents/                  # AI agent hierarchy
│   ├── tier1_master/       # Master coordinator
│   ├── tier2_orchestrators/# Domain orchestrators
│   ├── tier3_specialists/  # Specialized workers
│   └── tier4_executors/    # Micro-task agents
├── scripts/                # Core functionality
│   ├── data_fetchers/     # API data collection
│   ├── bots/              # Automated behaviors
│   └── tools/             # Utility scripts
├── config/                # Configuration files
├── utils/                 # Shared utilities
├── tests/                 # Test suite
└── docs/                  # Documentation
```

### 2. Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-agent

# Make changes
git add .
git commit -m "Add new specialist agent for MLB coverage"

# Push and create PR
git push origin feature/new-agent
```

### 3. Testing Strategy

**Unit Tests**:
```bash
# Test individual functions
python -m pytest tests/test_tweet_formatter.py -v

# Test with coverage
python -m pytest --cov=agents tests/
```

**Integration Tests**:
```bash
# Test full workflow
python tests/integration/test_posting_pipeline.py

# Test API endpoints
python tests/integration/test_api_servers.py
```

**Load Tests**:
```bash
# Simulate high traffic
python tests/load/test_game_day_load.py

# Test rate limiting
python tests/load/test_rate_limits.py
```

### 4. Code Quality

```bash
# Format code
black agents/ scripts/ utils/

# Check style
flake8 agents/ scripts/ utils/

# Type checking
mypy agents/ scripts/ utils/
```

---

## Remote Server Setup

### 1. WNBA Server Configuration

**On remote server** (155.138.211.147):

```bash
# Clone minimal posting setup
git clone <repository-url> wirereport_wnba
cd wirereport_wnba

# Install dependencies
pip install tweepy aiohttp schedule

# Configure for remote operation
nano config/remote_config.py
```

**Remote Configuration**:
```python
# Brain server connection
BRAIN_SERVER_IP = "YOUR_BRAIN_SERVER_IP"
BRAIN_SERVER_PORT = 8080

# Local rate limit API
LOCAL_PORT = 8081

# Polling settings
POLL_INTERVAL = 30  # seconds
BATCH_SIZE = 5      # tweets per poll
```

### 2. Remote Service Setup

```bash
# Create systemd service for remote
sudo nano /etc/systemd/system/wirereport-wnba-remote.service

[Unit]
Description=WireReport WNBA Remote Poster
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/wirereport_wnba
ExecStart=/usr/bin/python3 scripts/remote_wnba_poster.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable wirereport-wnba-remote
sudo systemctl start wirereport-wnba-remote
```

---

## Monitoring Setup

### 1. Log Monitoring

```bash
# Install log aggregation (optional)
sudo apt install rsyslog logrotate

# Configure logrotate
sudo nano /etc/logrotate.d/wirereport

/root/wirereport/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    create 644 root root
}
```

### 2. Health Monitoring

```bash
# Create monitoring script
nano scripts/health_monitor.sh

#!/bin/bash
# Check all services and APIs
systemctl is-active wirereport-* | grep -q inactive && echo "Service down!"
curl -s http://localhost:8000/health | jq -r .status
curl -s http://localhost:8080/health | jq -r .status

# Add to crontab
crontab -e
*/5 * * * * /root/wirereport/scripts/health_monitor.sh >> /var/log/health_monitor.log
```

### 3. Performance Monitoring

```bash
# Monitor resource usage
top -p $(pgrep -f wirereport)

# Database performance
sqlite3 data/wirereport.db "EXPLAIN QUERY PLAN SELECT * FROM posted_tweets WHERE created_at > datetime('now', '-1 day');"

# API response times
curl -w "@curl-format.txt" http://localhost:8000/health -o /dev/null -s
```

---

## Troubleshooting Common Issues

### 1. Service Won't Start

```bash
# Check logs
journalctl -u wirereport-swarm -n 50

# Common issues:
# - Missing environment variables
# - Database permissions
# - Port conflicts
# - Missing dependencies

# Check port usage
sudo netstat -tlnp | grep :800
```

### 2. API Connection Issues

```bash
# Test connectivity
curl -v http://localhost:8000/health
curl -v http://localhost:8080/health

# Check firewall
sudo ufw status

# Verify services are listening
sudo ss -tlnp | grep python
```

### 3. Database Issues

```bash
# Check database integrity
sqlite3 data/wirereport.db "PRAGMA integrity_check;"

# Fix permissions
chmod 644 data/wirereport.db
chown $USER:$USER data/wirereport.db

# Backup and restore
cp data/wirereport.db data/wirereport.db.backup
```

### 4. Twitter API Errors

```bash
# Check rate limits
python scripts/tools/check_rate_limit.py

# Verify tokens
python scripts/tools/verify_oauth_tokens.py

# Common errors:
# - Expired tokens (re-run OAuth setup)
# - Rate limit exceeded (wait for reset)
# - Invalid credentials (check config)
```

---

## Performance Optimization

### 1. Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_posted_tweets_created_at ON posted_tweets(created_at);
CREATE INDEX idx_player_stats_player_name ON player_stats(player_name);
CREATE INDEX idx_games_game_date ON games(game_date);

-- Enable WAL mode for better concurrency
PRAGMA journal_mode=WAL;
```

### 2. Caching Strategy

```python
# Redis caching configuration
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'decode_responses': True
}

# Cache durations
CACHE_DURATIONS = {
    'player_stats': 900,      # 15 minutes
    'game_scores': 300,       # 5 minutes
    'trending_topics': 600,   # 10 minutes
    'posted_tweets': 3600     # 1 hour
}
```

### 3. Resource Limits

**Systemd service limits**:
```ini
[Service]
MemoryLimit=500M
CPUQuota=20%
TasksMax=100
LimitNOFILE=1024
```

---

## Deployment Checklist

### Pre-Deployment

- [ ] All tests pass
- [ ] Environment variables configured
- [ ] Database initialized
- [ ] API keys valid
- [ ] Services configured
- [ ] Logs directory writable
- [ ] Backup strategy in place

### Deployment

- [ ] Stop existing services
- [ ] Deploy new code
- [ ] Run database migrations
- [ ] Update configuration
- [ ] Start services in order
- [ ] Verify health checks

### Post-Deployment

- [ ] Monitor logs for errors
- [ ] Test posting functionality
- [ ] Verify queue processing
- [ ] Check API endpoints
- [ ] Monitor resource usage
- [ ] Confirm backup execution

---

## Additional Resources

### Documentation

- [Wire Report Full Documentation](WIRE_REPORT_FULL_DOCUMENTATION.md)
- [Agent Function Reference](AGENT_FUNCTION_REFERENCE.md)
- [API Endpoints Guide](API_ENDPOINTS_GUIDE.md)
- [Swarm Architecture](agents/SWARM_ARCHITECTURE.md)

### External APIs

- [Twitter API v2 Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [RapidAPI NBA Documentation](https://rapidapi.com/api-sports/api/api-nba/)
- [Kaggle API Documentation](https://www.kaggle.com/docs/api)

### Support

- Check logs first: `/root/wirereport/logs/`
- Review configuration: `/root/wirereport/config/`
- Test individual components before full system
- Monitor resource usage during development

---

This setup guide provides a complete development environment for the Wire Report system. Follow the steps carefully and refer to the troubleshooting section for common issues.

*Last Updated: August 2, 2025*