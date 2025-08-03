# Wire Report Complete System Documentation
## Version 2.0 - August 2025

This comprehensive guide documents the entire Wire Report ecosystem, including all agents, scripts, APIs, and services that power automated sports content generation across multiple social media accounts.

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Directory Structure](#directory-structure)
4. [Tier-Based Agent System](#tier-based-agent-system)
5. [Core Services](#core-services)
6. [API Servers](#api-servers)
7. [Scripts and Utilities](#scripts-and-utilities)
8. [Configuration](#configuration)
9. [Database Management](#database-management)
10. [Queue System](#queue-system)
11. [Posting Pipeline](#posting-pipeline)
12. [Monitoring and Resilience](#monitoring-and-resilience)
13. [Historical Data Integration](#historical-data-integration)
14. [Development Guide](#development-guide)

---

## System Overview

Wire Report is an autonomous sports content generation and posting system that leverages 200+ specialized AI agents organized in a 4-tier hierarchy. The system:

- **Generates** contextual sports content using OpenAI GPT
- **Posts** to multiple Twitter accounts (@wirereporthq, @wirereportwnba)
- **Manages** rate limits, budgets, and content quality
- **Integrates** real-time data from multiple sports APIs
- **Maintains** historical context from Kaggle datasets
- **Operates** 24/7 with automatic failure recovery

### Key Features
- Multi-sport coverage (NBA, WNBA, NFL, NHL, MLB, MLS, CFB, CBB)
- OAuth 2.0 authentication for Twitter posting
- Queue-based content distribution
- Media attribution with copyright compliance
- Engagement feedback loop
- Distributed multi-server architecture

---

## Architecture

### High-Level System Flow

```
┌─────────────────────────────────────────────────────────┐
│                    SWARM MASTER                         │
│                 (200+ AI Agents)                        │
│    Tier 1: Master Coordinator (1)                      │
│    Tier 2: Domain Orchestrators (8)                    │
│    Tier 3: Specialized Workers (50+)                   │
│    Tier 4: Micro-Task Executors (150+)                 │
└────────────────────┬───────────────────────────────────┘
                     │ Content Generation
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  BRAIN SERVER                           │
│            Central Intelligence Hub                     │
│    - Brain API (Port 8000): Swarm coordination        │
│    - Queue API (Port 8080): Content distribution      │
│    - Context Management: Historical tracking          │
└────────────────────┬───────────────────────────────────┘
                     │ Queues
     ┌───────────────┴───────────────┬─────────────────┐
     ▼                               ▼                 ▼
┌─────────────┐            ┌──────────────┐   ┌──────────────┐
│  HQ Queue   │            │ WNBA Queue   │   │Future Queues │
│  Processor  │            │    API       │   │(NFL,MLB,etc) │
└──────┬──────┘            └──────┬───────┘   └──────────────┘
       │                          │ Remote polling
       ▼                          ▼
┌─────────────┐            ┌──────────────┐
│@wirereporthq│            │@wirereportwnba│
│Local Posting│            │Remote Server  │
└─────────────┘            └──────────────┘
```

### Communication Flow
1. **Content Generation**: Swarm agents create content based on triggers
2. **Queue Distribution**: Brain server routes content to appropriate queues
3. **Rate Limit Checking**: Verify posting capacity before generation
4. **Posting Execution**: Local or remote processors post to Twitter
5. **Feedback Loop**: Posted tweets report back for context enhancement

---

## Directory Structure

### Root Directory Organization

```
/root/
├── wirereport/                 # Main application directory
│   ├── agents/                 # 4-tier agent hierarchy
│   ├── scripts/               # Core scripts and utilities
│   ├── data/                  # Cache files and local data
│   ├── config/                # Configuration files
│   ├── logs/                  # Application logs
│   └── utils/                 # Shared utilities
│
├── wirereport_api/            # API server directory
│   ├── data/                  # Queue and sync data
│   │   ├── queues/           # Tweet queues by account
│   │   ├── sync/             # Posted tweets tracking
│   │   └── logs/             # API logs
│   └── *.py                   # API server scripts
│
└── wirereporthq/              # HQ account directory
    ├── data/                  # OAuth tokens and history
    ├── scripts/              # Account-specific scripts
    └── logs/                 # Posting logs
```

---

## Tier-Based Agent System

### Tier 1: Master Coordinator (1 Agent)

#### Swarm Master (`/root/wirereport/agents/swarm_master_runner.py`)
- **Purpose**: Central orchestration of entire agent network
- **Responsibilities**:
  - Daily task planning and delegation
  - Resource allocation across accounts
  - Rate limit management (17 tweets/day/account)
  - Performance monitoring
  - Error recovery coordination
- **Key Functions**:
  ```python
  async def run_daily_cycle()     # Main 24-hour operation loop
  async def delegate_to_tier2()   # Task distribution
  async def monitor_health()      # System health checks
  ```

### Tier 2: Domain Orchestrators (8 Agents)

Location: `/root/wirereport/agents/tier2_orchestrators/`

1. **Content Orchestrator** (`content_orchestrator.py`)
   - Manages all content generation workflows
   - Coordinates tier 3 content specialists
   - Ensures content diversity and quality

2. **League Orchestrator** (`league_orchestrator.py`)
   - Handles multi-sport coordination
   - Manages league-specific timings
   - Distributes workload across sports

3. **Infrastructure Orchestrator** (`infrastructure_orchestrator.py`)
   - Monitors system health
   - Manages API resilience
   - Coordinates database optimization

4. **Media Orchestrator** (`media_orchestrator.py`)
   - Handles video/image processing
   - Manages copyright compliance
   - Coordinates attribution

5. **Engagement Orchestrator** (`engagement_orchestrator.py`)
   - Analyzes posting performance
   - Optimizes timing strategies
   - Manages reply/quote tweet balance

6. **Data Orchestrator** (`data_orchestrator.py`)
   - Coordinates API data fetching
   - Manages cache freshness
   - Handles Kaggle dataset updates

7. **Pipeline Orchestrator** (`pipeline_orchestrator.py`)
   - Manages content flow pipelines
   - Coordinates breaking news detection
   - Handles priority routing

8. **Compliance Orchestrator** (`compliance_orchestrator.py`)
   - Ensures rate limit compliance
   - Manages content filtering
   - Handles platform rule adherence

### Tier 3: Specialized Workers (50+ Agents)

Location: `/root/wirereport/agents/tier3_specialists/`

#### Content Specialists (`/content/`)
- **tweet_formatter_agent.py**: Applies formatting standards
- **breaking_news_agent.py**: Rapid response to developing stories
- **game_recap_agent.py**: Post-game analysis generation
- **player_highlight_agent.py**: Individual performance focus
- **statistical_insight_agent.py**: Advanced metrics analysis
- **historical_comparison_agent.py**: Past vs present context
- **trending_topic_agent.py**: Viral moment detection
- **meme_generator_agent.py**: Humor and engagement content

#### Infrastructure Specialists (`/infrastructure/`)
- **api_resilience_agent.py**: Service health monitoring
- **database_optimizer_agent.py**: Query performance tuning
- **cache_manager_agent.py**: Data freshness management
- **rate_limit_monitor_agent.py**: API usage tracking
- **backup_manager_agent.py**: Data preservation
- **log_analyzer_agent.py**: Error pattern detection

#### League Specialists (`/leagues/`)
- **nba_specialist_agent.py**: NBA-specific knowledge
- **wnba_specialist_agent.py**: WNBA expertise
- **nfl_specialist_agent.py**: NFL coverage
- **mlb_specialist_agent.py**: MLB insights
- **nhl_specialist_agent.py**: NHL analysis
- **mls_specialist_agent.py**: MLS content

#### Media Specialists (`/media/`)
- **video_processor_agent.py**: Clip extraction
- **image_analyzer_agent.py**: Visual content understanding
- **transcription_agent.py**: Audio to text conversion
- **attribution_validator_agent.py**: Copyright compliance
- **thumbnail_generator_agent.py**: Visual optimization

### Tier 4: Micro-Task Executors (150+ Agents)

Location: `/root/wirereport/agents/tier4_executors/`

These agents handle atomic tasks:
- API call execution
- Text formatting
- Hashtag generation
- Emoji selection
- URL shortening
- Timestamp formatting
- Score formatting
- Player name validation
- Team abbreviation standardization
- Statistical calculations

---

## Core Services

### 1. Swarm Service (`wirereport-swarm.service`)

**File**: `/etc/systemd/system/wirereport-swarm.service`
**Script**: `/root/wirereport/agents/swarm_master_runner.py`
**Port**: 9999 (monitoring interface)

**Functionality**:
- Runs the main swarm orchestration
- Manages daily tweet budgets
- Coordinates all agent activities
- Generates content for all accounts

**Key Operations**:
```python
# Main entry point
async def main():
    swarm = SwarmMaster()
    await swarm.initialize()
    await swarm.run_daily_cycle()
```

### 2. Brain API Service (`wirereport-brain.service`)

**File**: `/etc/systemd/system/wirereport-brain.service`
**Script**: `/root/wirereport/agents/brain_api_server.py`
**Port**: 8000

**Endpoints**:
- `POST /api/think` - Content generation request
- `GET /api/status` - Swarm status
- `POST /api/feedback` - Performance feedback
- `GET /health` - Service health check

**Key Features**:
- Centralized AI coordination
- Context management
- Performance tracking
- Request routing

### 3. Queue API Service (`wirereport-wnba-api.service`)

**File**: `/etc/systemd/system/wirereport-wnba-api.service`
**Script**: `/root/wirereport_api/wnba_api_server.py`
**Port**: 8080

**Endpoints**:
- `GET /api/queues/wnba` - Fetch pending tweets
- `POST /api/queues/wnba/ack` - Acknowledge processing
- `POST /api/tweets/posted` - Report posted tweets
- `GET /api/context/posted_tweets` - Historical context
- `POST /api/sync/posted_tweets` - Two-way sync

### 4. HQ Queue Processor (`wirereport-hq-queue.service`)

**File**: `/etc/systemd/system/wirereport-hq-queue.service`
**Script**: `/root/wirereporthq/scripts/hq_queue_processor.py`

**Functionality**:
- Polls HQ queue every 30 seconds
- Posts tweets via OAuth 2.0
- Reports success to brain server
- Manages rate limiting

### 5. API Resilience Monitor (`wirereport-api-resilience.service`)

**File**: `/etc/systemd/system/wirereport-api-resilience.service`
**Script**: `/root/wirereport/agents/tier3_specialists/infrastructure/api_resilience_agent.py`

**Monitoring**:
- Brain API health
- Queue API responsiveness
- Swarm master status
- Automatic service recovery

---

## API Servers

### Brain API Server (`/root/wirereport/agents/brain_api_server.py`)

**Purpose**: Central intelligence hub for swarm coordination

**Key Classes**:
```python
class BrainAPIServer:
    async def think(request: ThinkRequest) -> ThinkResponse
    async def get_swarm_status() -> SwarmStatus
    async def receive_feedback(feedback: Feedback) -> None
```

**Integration Points**:
- Receives requests from swarm agents
- Coordinates with OpenAI API
- Manages context database
- Tracks performance metrics

### Queue API Server (`/root/wirereport_api/wnba_api_server.py`)

**Purpose**: Unified queue management for all accounts

**Queue Management**:
```python
class QueueManager:
    def add_to_queue(tweet: Tweet, queue_name: str)
    def get_from_queue(queue_name: str, limit: int)
    def acknowledge_tweets(tweet_ids: List[str])
    def mark_as_posted(tweet_id: str, twitter_id: str)
```

**Security**:
- IP-based access control
- Rate limit enforcement
- Request validation

### Rate Limit Manager (`/root/wirereport_api/rate_limit_manager.py`)

**Purpose**: Prevent API limit violations

**Remote Server Integration**:
```python
remote_servers = {
    "@wirereportwnba": {
        "ip": "155.138.211.147",
        "port": 8081,
        "health_endpoint": "/api/rate-limit/status"
    }
}
```

---

## Scripts and Utilities

### Data Fetchers (`/root/wirereport/scripts/data_fetchers/`)

1. **nba_data_fetcher.py**
   - Fetches live NBA game data
   - Updates player statistics
   - Monitors injuries and trades

2. **wnba_data_fetcher.py**
   - WNBA-specific data collection
   - Season statistics tracking
   - Team standings updates

3. **dual_league_fetcher.py**
   - Concurrent NBA/WNBA fetching
   - Cross-league comparisons
   - Unified data format

4. **scheduled_tweet_fetcher_v2.py**
   - X (Twitter) timeline monitoring
   - Trending topic detection
   - Engagement analysis

5. **kaggle_data_fetcher.py**
   - Historical data downloads
   - Dataset updates
   - Cross-league integration

### Tweet Generators (`/root/wirereport/scripts/`)

1. **nba_tweet_generator.py**
   - NBA content creation
   - Context enhancement
   - Formatting application

2. **wnba_tweet_generator.py**
   - WNBA-focused content
   - Player highlights
   - Game analysis

### Bot Modules (`/root/wirereport/scripts/bots/`)

1. **reply_bot.py**
   - Engages with trending conversations
   - Adds expert commentary
   - Maintains conversation threads

2. **retweet_manager.py**
   - Curates quality content
   - Adds value with quotes
   - Manages attribution

3. **meme_bot.py**
   - Generates humorous content
   - Creates visual memes
   - Tracks viral formats

4. **telegram_approval_bot.py**
   - Human review interface
   - Content approval workflow
   - Quality control

### Utilities (`/root/wirereport/utils/`)

1. **tweet_budget.py**
   - Daily limit enforcement
   - Budget allocation
   - Usage tracking

2. **relevancy_scorer.py**
   - Content quality assessment
   - Engagement prediction
   - Topic relevance scoring

3. **entity_recognition.py**
   - Player name extraction
   - Team identification
   - Statistical parsing

4. **video_processor.py**
   - Clip extraction
   - Highlight detection
   - Format conversion

5. **content_filter.py**
   - Inappropriate content detection
   - Duplicate prevention
   - Platform compliance

---

## Configuration

### Main Configuration (`/root/wirereport/config/config.py`)

```python
# API Keys
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
TWITTER_CLIENT_ID = os.getenv('TWITTER_CLIENT_ID')
TWITTER_CLIENT_SECRET = os.getenv('TWITTER_CLIENT_SECRET')

# Limits
DAILY_TWEET_LIMIT = 17  # Free X API plan
MAX_QUEUE_SIZE = 100
RATE_LIMIT_WINDOW = 3 * 60 * 60  # 3 hours

# Timeouts
API_TIMEOUT = 10
DB_TIMEOUT = 5
POST_RETRY_DELAY = 30
```

### League Configurations (`/root/wirereport/config/league_configs/`)

Each league has specific settings:
- Game schedules
- Key players to track
- Trending hashtags
- Season dates
- Statistical priorities

### Kaggle Datasets (`/root/wirereport/config/kaggle_datasets.py`)

```python
KAGGLE_DATASETS = {
    'NBA': 'historical-nba-data-and-player-box-scores',
    'WNBA': 'wnba-stats',
    'NFL': 'nfl-scores-and-betting-data',
    # ... more leagues
}
```

---

## Database Management

### Schema (`/root/wirereport/scripts/tools/schema.sql`)

**Core Tables**:
- `teams`: League teams and metadata
- `players`: Player information and stats
- `games`: Game schedules and results
- `player_stats`: Performance metrics
- `posted_tweets`: Historical posts
- `engagement_metrics`: Performance tracking

### Database Tools (`/root/wirereport/scripts/tools/`)

1. **initialize_database.py**
   - Creates schema
   - Sets up indexes
   - Configures WAL mode

2. **populate_player_stats.py**
   - Imports Kaggle data
   - Updates current stats
   - Maintains history

3. **backup_and_prune.py**
   - Daily backups
   - Old data removal
   - Storage optimization

4. **daily_reset.py**
   - Clears temporary data
   - Resets counters
   - Updates caches

---

## Queue System

### Queue Files

**HQ Queue**: `/root/wirereport_api/data/queues/hq_queue.json`
```json
{
  "id": "unique_identifier",
  "content": "Tweet text with emojis 🏀",
  "league": "NBA",
  "account": "@wirereporthq",
  "created_at": "2025-08-02T10:00:00",
  "priority": 10,
  "metadata": {
    "source": "swarm",
    "content_type": "game_update"
  }
}
```

**WNBA Queue**: `/root/wirereport_api/data/queues/wnba_queue.json`
- Same format as HQ
- Polled by remote server
- Auto-cleared after posting

### Queue Processing Flow

1. **Generation Phase**
   - Swarm creates content
   - Checks rate limits
   - Adds to appropriate queue

2. **Distribution Phase**
   - Queue API serves tweets
   - Processors poll queues
   - Priority-based selection

3. **Posting Phase**
   - OAuth authentication
   - Twitter API call
   - Success/failure handling

4. **Feedback Phase**
   - Remove from queue
   - Add to posted history
   - Update context database

---

## Posting Pipeline

### HQ Account Pipeline

1. **Content Generation**
   ```python
   swarm → brain_api → content_agent → format_agent → queue
   ```

2. **Queue Processing**
   ```python
   hq_queue_processor → posting_agent → twitter_api
   ```

3. **Feedback Loop**
   ```python
   twitter_response → queue_api → posted_tweets → context_db
   ```

### WNBA Account Pipeline

1. **Remote Polling**
   ```python
   remote_server → GET /api/queues/wnba → local_queue
   ```

2. **Processing**
   ```python
   rate_check → post_to_twitter → acknowledge
   ```

3. **Sync Back**
   ```python
   POST /api/tweets/posted → brain_server → context_update
   ```

---

## Monitoring and Resilience

### Health Checks

**Endpoint Monitoring**:
- `/health` on all services
- 10-second timeout detection
- Automatic restart triggers

**Service Recovery**:
```python
class APIResilienceAgent:
    async def monitor_service(service_id: str):
        if not healthy:
            await self.restart_service(service_id)
            await self.notify_recovery(service_id)
```

### Logging System

**Log Locations**:
- Swarm: `/root/wirereport/logs/swarm.log`
- Brain: `/root/wirereport/logs/brain_api.log`
- Queue: `/root/wirereport_api/data/logs/wnba_api.log`
- HQ: `/root/wirereporthq/logs/hq_queue_processor.log`

**Log Rotation**:
- Daily rotation
- 7-day retention
- Compression enabled

### Error Handling

**Retry Logic**:
- API calls: 3 retries with exponential backoff
- Posting: 5 retries over 15 minutes
- Queue operations: Immediate retry

**Failure Recovery**:
- Automatic service restart
- Queue persistence
- State recovery from disk

---

## Historical Data Integration

### Kaggle Integration

**Setup Process**:
1. Configure API credentials
2. Run dataset downloads
3. Import to database
4. Schedule updates

**Available Datasets**:
- NBA: 1946-present statistics
- WNBA: 1997-present data
- NFL: Complete game history
- MLB: Baseball almanac data

### Query Examples

```python
# Get historical performance
optimizer = DatabaseOptimizerAgent()
stats = await optimizer.get_historical_stats(
    league='NBA',
    player_name='LeBron James',
    stat_type='points',
    days_back=365
)

# Compare eras
comparison = await optimizer.compare_players(
    player1='Michael Jordan',
    player2='LeBron James',
    metrics=['ppg', 'rpg', 'apg']
)
```

---

## Development Guide

### Adding New Agents

1. **Choose Appropriate Tier**
   - Tier 2: Domain-wide coordination
   - Tier 3: Specific expertise
   - Tier 4: Simple tasks

2. **Follow Agent Template**
   ```python
   class NewSpecialistAgent(BaseAgent):
       def __init__(self):
           super().__init__(
               name="New Specialist",
               tier=3,
               capabilities=["task1", "task2"]
           )
       
       async def process(self, task: Task) -> Result:
           # Implementation
           pass
   ```

3. **Register with Orchestrator**
   - Add to appropriate tier2 orchestrator
   - Define trigger conditions
   - Set resource limits

### Testing Procedures

**Unit Tests**:
```bash
python -m pytest tests/agents/
python -m pytest tests/scripts/
```

**Integration Tests**:
```bash
python scripts/test_both_accounts.py
python scripts/test_queue_system.py
```

**Load Tests**:
```bash
python tests/load/simulate_game_day.py
```

### Deployment Checklist

1. **Pre-deployment**
   - [ ] Run all tests
   - [ ] Check rate limits
   - [ ] Verify API keys
   - [ ] Review logs

2. **Deployment**
   - [ ] Stop services gracefully
   - [ ] Deploy code changes
   - [ ] Run migrations
   - [ ] Restart services

3. **Post-deployment**
   - [ ] Monitor health endpoints
   - [ ] Check queue processing
   - [ ] Verify posting
   - [ ] Review error logs

---

## Troubleshooting Guide

### Common Issues

1. **Service Won't Start**
   ```bash
   # Check logs
   journalctl -u wirereport-swarm -n 100
   
   # Verify dependencies
   systemctl status wirereport-brain
   ```

2. **Tweets Not Posting**
   ```bash
   # Check queues
   cat /root/wirereport_api/data/queues/hq_queue.json | jq .
   
   # Verify rate limits
   curl http://localhost:8080/api/rate-limit/status
   ```

3. **API Errors**
   ```bash
   # Test endpoints
   curl http://localhost:8000/health
   curl http://localhost:8080/health
   ```

### Recovery Procedures

**Full System Restart**:
```bash
systemctl restart wirereport-swarm
systemctl restart wirereport-brain
systemctl restart wirereport-wnba-api
systemctl restart wirereport-hq-queue
systemctl restart wirereport-api-resilience
```

**Queue Recovery**:
```bash
# Backup current queues
cp /root/wirereport_api/data/queues/*.json /tmp/

# Clear stuck queues
echo "[]" > /root/wirereport_api/data/queues/hq_queue.json
```

**Database Recovery**:
```bash
# Run integrity check
sqlite3 /root/wirereport/data/wirereport.db "PRAGMA integrity_check"

# Restore from backup
cp /root/wirereport/backups/latest.db /root/wirereport/data/wirereport.db
```

---

## Performance Optimization

### Database Tuning

**Indexes Created**:
- player_name + team_id
- game_date + league
- created_at DESC
- twitter_id UNIQUE

**WAL Mode Benefits**:
- Concurrent reads/writes
- Better crash recovery
- Improved performance

### Caching Strategy

**In-Memory Caches**:
- Recent tweets (1 hour)
- Player stats (15 minutes)
- API responses (5 minutes)

**Disk Caches**:
- Kaggle datasets (24 hours)
- Media files (7 days)
- Historical queries (1 hour)

### Resource Limits

**Systemd Constraints**:
- Memory: 500MB per service
- CPU: 20% per service
- Restart: on-failure
- Restart delay: 10s

---

## Future Enhancements

### Planned Features

1. **Multi-Account Expansion**
   - NFL account setup
   - MLB integration
   - NHL coverage
   - MLS content

2. **Advanced Analytics**
   - Predictive modeling
   - Sentiment analysis
   - Engagement optimization
   - A/B testing

3. **Media Enhancement**
   - Auto-video generation
   - Infographic creation
   - Live stream clips
   - AR statistics

4. **Interactive Features**
   - Poll creation
   - Contest management
   - Fan engagement
   - Live Q&A

### Scalability Roadmap

1. **Horizontal Scaling**
   - Multi-server swarm
   - Distributed queues
   - Load balancing
   - Regional deployment

2. **Performance Improvements**
   - GPU acceleration
   - Async everything
   - Connection pooling
   - Query optimization

---

## Conclusion

Wire Report represents a cutting-edge implementation of autonomous AI agents for social media content generation. The system's modular design, comprehensive monitoring, and fault-tolerant architecture ensure reliable 24/7 operation while maintaining high content quality and platform compliance.

For questions or issues, consult:
- System logs in `/root/wirereport/logs/`
- CLAUDE.md files in each directory
- This documentation
- GitHub issues at the project repository

---

*Documentation Version: 2.0*
*Last Updated: August 2, 2025*
*System Version: WireReport 2.0 Enhanced*