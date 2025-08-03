# Wire Report Agent Function Reference Guide

This document provides detailed function descriptions for every agent and script in the Wire Report system.

---

## Tier 1: Master Coordinator

### SwarmMaster (`/root/wirereport/agents/swarm_master_runner.py`)

**Primary Functions:**

```python
async def initialize(self):
    """
    Initialize the swarm master with all tier 2 orchestrators.
    - Loads configuration for all accounts
    - Initializes daily budgets (17 tweets/account)
    - Establishes orchestrator connections
    - Sets up monitoring endpoints
    """

async def run_daily_cycle(self):
    """
    Main 24-hour operational loop.
    - Plans daily content strategy
    - Delegates tasks to tier 2 orchestrators
    - Monitors system health every 5 minutes
    - Manages rate limits across accounts
    - Handles error recovery
    """

async def delegate_to_tier2(self, task_type: str, parameters: dict):
    """
    Routes tasks to appropriate tier 2 orchestrators.
    - Content tasks → Content Orchestrator
    - League tasks → League Orchestrator
    - Infrastructure tasks → Infrastructure Orchestrator
    Returns: Task result or error
    """

async def monitor_health(self):
    """
    Continuous health monitoring of all systems.
    - Checks API endpoints
    - Monitors queue sizes
    - Tracks posting success rates
    - Alerts on failures
    """
```

---

## Tier 2: Domain Orchestrators

### Content Orchestrator (`/root/wirereport/agents/tier2_orchestrators/content_orchestrator.py`)

```python
async def generate_content(self, content_type: str, league: str, context: dict):
    """
    Orchestrates content generation workflow.
    - Selects appropriate tier 3 specialist
    - Provides context from database
    - Ensures formatting compliance
    - Returns generated content
    """

async def manage_content_mix(self):
    """
    Balances content types for optimal engagement.
    - 25% breaking news
    - 25% player highlights
    - 20% statistical insights
    - 20% game recaps
    - 10% memes/humor
    """

async def enforce_quality_standards(self, content: str):
    """
    Validates content before queuing.
    - Character count (230-260)
    - Emoji usage (1-3 max)
    - Hashtag placement
    - Third-person perspective
    """
```

### League Orchestrator (`/root/wirereport/agents/tier2_orchestrators/league_orchestrator.py`)

```python
async def coordinate_leagues(self):
    """
    Manages multi-sport content generation.
    - Tracks game schedules
    - Prioritizes by activity level
    - Balances coverage across leagues
    """

async def get_league_context(self, league: str):
    """
    Retrieves league-specific information.
    - Current standings
    - Recent games
    - Trending players
    - Key storylines
    """

async def schedule_league_content(self, league: str, time_slots: list):
    """
    Plans content timing for each league.
    - Game-time focus
    - Off-season management
    - Breaking news priority
    """
```

### Infrastructure Orchestrator (`/root/wirereport/agents/tier2_orchestrators/infrastructure_orchestrator.py`)

```python
async def monitor_infrastructure(self):
    """
    Oversees system health and performance.
    - Service availability
    - API response times
    - Database performance
    - Queue processing rates
    """

async def coordinate_maintenance(self):
    """
    Manages system maintenance tasks.
    - Database optimization
    - Log rotation
    - Cache clearing
    - Backup verification
    """

async def handle_failures(self, service_id: str, error: Exception):
    """
    Orchestrates failure recovery.
    - Initiates service restart
    - Notifies relevant agents
    - Logs incident details
    - Monitors recovery
    """
```

---

## Tier 3: Specialized Workers

### Content Specialists

#### Tweet Formatter Agent (`/root/wirereport/agents/tier3_specialists/content/tweet_formatter_agent.py`)

```python
def format_game_update(self, game_data: dict) -> str:
    """
    Formats game updates with standard structure.
    Input: Raw game data
    Output: Formatted tweet with scores, players, narrative
    Example: "🏀 FINAL: Lakers 118, Celtics 114\n\nLeBron: 35pts, 12ast | Tatum: 41pts, 8reb\n\nLakers complete the comeback!"
    """

def apply_media_attribution(self, content: str, media_source: str) -> str:
    """
    Adds proper attribution for media content.
    - Appends "via @{source}" 
    - Validates source exists
    - Ensures copyright compliance
    """

def optimize_character_count(self, content: str) -> str:
    """
    Optimizes tweet length while preserving meaning.
    - Target: 230-240 characters
    - Preserves key information
    - Maintains readability
    """
```

#### Breaking News Agent (`/root/wirereport/agents/tier3_specialists/content/breaking_news_agent.py`)

```python
async def detect_breaking_news(self, data_stream: dict) -> bool:
    """
    Identifies breaking news from data feeds.
    Triggers on:
    - Major trades
    - Injury reports
    - Record-breaking performances
    - Unexpected results
    """

async def generate_breaking_tweet(self, news_item: dict) -> dict:
    """
    Creates urgent news tweets.
    - Priority: 10 (highest)
    - Format: "🚨 BREAKING: {news}"
    - Includes source verification
    """

async def validate_news_accuracy(self, news_item: dict) -> bool:
    """
    Verifies breaking news before posting.
    - Checks multiple sources
    - Confirms details
    - Prevents false reports
    """
```

### Infrastructure Specialists

#### API Resilience Agent (`/root/wirereport/agents/tier3_specialists/infrastructure/api_resilience_agent.py`)

```python
async def monitor_api_health(self):
    """
    Continuous API health monitoring.
    - Checks every 60 seconds
    - 10-second timeout threshold
    - Tracks response times
    - Identifies hanging services
    """

async def detect_failure_patterns(self, service_logs: list) -> dict:
    """
    Analyzes logs for failure patterns.
    Returns:
    - Failure frequency
    - Common error types
    - Correlation with load
    - Recommended actions
    """

async def execute_recovery(self, service_id: str):
    """
    Performs service recovery actions.
    Steps:
    1. Attempt graceful restart
    2. Force restart if needed
    3. Verify service health
    4. Update monitoring status
    """

async def prevent_cascade_failures(self):
    """
    Prevents failure propagation.
    - Circuit breaker implementation
    - Request rate limiting
    - Fallback mechanisms
    - Queue overflow protection
    """
```

#### Database Optimizer Agent (`/root/wirereport/agents/tier3_specialists/infrastructure/database_optimizer_agent.py`)

```python
async def optimize_queries(self):
    """
    Improves database query performance.
    - Analyzes slow queries
    - Suggests index additions
    - Implements query caching
    - Monitors improvement
    """

async def manage_kaggle_datasets(self):
    """
    Handles Kaggle data integration.
    - Downloads new datasets
    - Updates existing data
    - Manages storage space
    - Indexes for performance
    """

async def implement_data_lifecycle(self):
    """
    Manages data retention policies.
    - Archives old tweets (>30 days)
    - Prunes cache files
    - Compresses logs
    - Maintains performance
    """

def get_historical_stats(self, league: str, player: str, days: int) -> dict:
    """
    Retrieves historical statistics.
    - Queries Kaggle data
    - Calculates trends
    - Compares to averages
    - Returns formatted stats
    """
```

---

## API Server Functions

### Brain API Server (`/root/wirereport/agents/brain_api_server.py`)

```python
async def think(self, request: ThinkRequest) -> ThinkResponse:
    """
    Main AI processing endpoint.
    Input: Task description, context, parameters
    Process:
    1. Route to appropriate agent
    2. Generate content
    3. Apply formatting
    4. Return response
    """

async def get_swarm_status(self) -> dict:
    """
    Returns current swarm operational status.
    Includes:
    - Active agents count
    - Tasks in progress
    - Daily budget remaining
    - Error counts
    """

async def receive_feedback(self, feedback: Feedback):
    """
    Processes performance feedback.
    - Updates success metrics
    - Adjusts content strategies
    - Trains optimization models
    """

async def health_check(self) -> dict:
    """
    Comprehensive health status.
    Returns:
    - Service uptime
    - Memory usage
    - Request latency
    - Database connectivity
    """
```

### Queue API Server (`/root/wirereport_api/wnba_api_server.py`)

```python
async def get_queue_tweets(self, league: str, limit: int = 5) -> list:
    """
    Retrieves tweets from queue.
    - Filters by league
    - Sorts by priority
    - Limits response size
    - Marks as processing
    """

async def acknowledge_tweets(self, tweet_ids: list, server_ip: str):
    """
    Confirms tweet processing.
    - Removes from queue
    - Logs acknowledgment
    - Updates metrics
    """

async def report_posted_tweet(self, tweet_data: dict):
    """
    Records successful posting.
    - Removes from queue
    - Adds to posted history
    - Updates context database
    - Triggers feedback loop
    """

async def get_posted_context(self, league: str, hours: int = 24) -> list:
    """
    Provides historical context.
    - Recent posted tweets
    - Engagement metrics
    - Popular topics
    - Aids content generation
    """
```

---

## Core Scripts

### Data Fetchers

#### NBA Data Fetcher (`/root/wirereport/scripts/data_fetchers/nba_data_fetcher.py`)

```python
def fetch_live_games(self) -> list:
    """
    Retrieves current NBA games.
    - Uses RapidAPI endpoint
    - Includes scores, time, quarter
    - Updates every 30 seconds during games
    """

def fetch_player_stats(self, player_id: str) -> dict:
    """
    Gets detailed player statistics.
    - Season averages
    - Last 5 games
    - Career highs
    - Advanced metrics
    """

def update_standings(self):
    """
    Updates team standings.
    - Conference rankings
    - Win/loss records
    - Playoff positioning
    - Tiebreaker info
    """
```

#### Scheduled Tweet Fetcher (`/root/wirereport/scripts/scheduled_tweet_fetcher_v2.py`)

```python
async def fetch_timeline_tweets(self, account: str) -> list:
    """
    Retrieves tweets from X timeline.
    - Uses Twitter API v2
    - Includes engagement metrics
    - Filters by relevance
    - Caches for analysis
    """

async def analyze_trending_topics(self, tweets: list) -> dict:
    """
    Identifies trending conversations.
    - Hashtag frequency
    - Mentioned players
    - Viral moments
    - Engagement patterns
    """

async def detect_reply_opportunities(self, tweets: list) -> list:
    """
    Finds tweets worth replying to.
    - High engagement posts
    - Relevant questions
    - Expert opinions
    - Breaking news
    """
```

### Tweet Generators

#### NBA Tweet Generator (`/root/wirereport/scripts/nba_tweet_generator.py`)

```python
def generate_game_recap(self, game_data: dict) -> str:
    """
    Creates post-game summary tweets.
    - Final scores
    - Key performers
    - Turning points
    - Statistical highlights
    """

def generate_player_highlight(self, player_stats: dict) -> str:
    """
    Focuses on individual performances.
    - Notable achievements
    - Statistical milestones
    - Historical comparisons
    - Impact on game
    """

def generate_statistical_insight(self, stats_data: dict) -> str:
    """
    Creates analytics-focused content.
    - Advanced metrics
    - Trend analysis
    - League comparisons
    - Predictive insights
    """
```

### Bot Modules

#### Reply Bot (`/root/wirereport/scripts/bots/reply_bot.py`)

```python
def generate_contextual_reply(self, original_tweet: dict) -> str:
    """
    Creates relevant reply content.
    - Analyzes original context
    - Adds expert perspective
    - Maintains conversation flow
    - Includes supporting data
    """

def select_reply_targets(self, tweets: list) -> list:
    """
    Chooses tweets to reply to.
    Criteria:
    - Relevance score > 0.7
    - Engagement > 100
    - No previous reply
    - Conversation potential
    """

def manage_thread_depth(self, conversation: dict) -> bool:
    """
    Controls reply thread participation.
    - Max depth: 3 replies
    - Ensures value addition
    - Avoids spam appearance
    """
```

#### Retweet Manager (`/root/wirereport/scripts/bots/retweet_manager.py`)

```python
def evaluate_retweet_quality(self, tweet: dict) -> float:
    """
    Scores tweet quality for retweeting.
    Factors:
    - Source credibility
    - Content relevance
    - Media presence
    - Engagement level
    Returns: Score 0.0-1.0
    """

def add_quote_commentary(self, original: dict) -> str:
    """
    Adds value to retweets.
    - Provides context
    - Offers analysis
    - Adds statistics
    - Engages audience
    """

def track_attribution(self, tweet: dict):
    """
    Ensures proper crediting.
    - Logs original author
    - Tracks media sources
    - Prevents violations
    - Maintains relationships
    """
```

---

## Utility Functions

### Tweet Budget Manager (`/root/wirereport/utils/tweet_budget.py`)

```python
def allocate_daily_budget(self, accounts: list) -> dict:
    """
    Distributes daily tweet allowance.
    - 17 tweets per account
    - Priority-based allocation
    - Time-based distribution
    - Reserve for breaking news
    """

def track_usage(self, account: str, tweet_type: str):
    """
    Monitors budget consumption.
    - Updates remaining count
    - Logs usage patterns
    - Enforces limits
    - Alerts on depletion
    """

def calculate_optimal_timing(self, account: str) -> list:
    """
    Determines best posting times.
    - Historical engagement data
    - League schedules
    - Time zone considerations
    - Audience activity
    """
```

### Content Filter (`/root/wirereport/utils/content_filter.py`)

```python
def check_inappropriate_content(self, text: str) -> bool:
    """
    Screens for problematic content.
    - Profanity detection
    - Sensitive topics
    - Platform violations
    - Controversial statements
    """

def detect_duplicates(self, content: str, history: list) -> bool:
    """
    Prevents duplicate posting.
    - Fuzzy matching
    - Semantic similarity
    - Time-based checks
    - Cross-account verification
    """

def verify_factual_accuracy(self, claims: list) -> dict:
    """
    Validates statistical claims.
    - Database verification
    - Source checking
    - Historical accuracy
    - Confidence scoring
    """
```

### Entity Recognition (`/root/wirereport/utils/entity_recognition.py`)

```python
def extract_players(self, text: str) -> list:
    """
    Identifies player mentions.
    - Full names
    - Nicknames
    - Common misspellings
    - Contextual identification
    """

def extract_teams(self, text: str) -> list:
    """
    Identifies team references.
    - Full names
    - Abbreviations
    - City names
    - Nickname variations
    """

def extract_statistics(self, text: str) -> dict:
    """
    Parses statistical information.
    - Points, rebounds, assists
    - Percentages
    - Advanced metrics
    - Time-based stats
    """
```

---

## Queue Processing Functions

### HQ Queue Processor (`/root/wirereporthq/scripts/hq_queue_processor.py`)

```python
async def process_queue(self):
    """
    Main queue processing loop.
    - Polls every 30 seconds
    - Processes up to 5 tweets
    - Handles rate limits
    - Reports successes
    """

async def post_tweet(self, tweet_data: dict) -> dict:
    """
    Posts individual tweet.
    - OAuth 2.0 authentication
    - Media attachment
    - Error handling
    - Response parsing
    """

async def handle_rate_limit(self, reset_time: int):
    """
    Manages rate limit responses.
    - Calculates wait time
    - Pauses processing
    - Logs limit hit
    - Resumes at reset
    """

async def report_success(self, tweet_id: str, twitter_id: str):
    """
    Reports successful posting.
    - Updates queue API
    - Logs posting time
    - Tracks metrics
    - Triggers feedback
    """
```

---

## Monitoring Functions

### API Resilience Monitor (`/root/wirereport/monitoring/api_resilience_monitor.py`)

```python
async def continuous_monitoring(self):
    """
    24/7 service monitoring loop.
    - Checks every 60 seconds
    - Tests all endpoints
    - Measures response times
    - Triggers recovery
    """

async def test_endpoint_health(self, url: str, timeout: int = 10) -> dict:
    """
    Tests individual endpoint.
    Returns:
    - Response time
    - Status code
    - Error details
    - Hanging detection
    """

async def analyze_performance_trends(self, metrics: list) -> dict:
    """
    Identifies performance degradation.
    - Response time trends
    - Error rate changes
    - Memory usage patterns
    - CPU utilization
    """

async def generate_health_report(self) -> dict:
    """
    Creates system health summary.
    - Service statuses
    - Performance metrics
    - Recent incidents
    - Recommendations
    """
```

---

## Testing Functions

### Test Both Accounts (`/root/wirereport/scripts/test_both_accounts.py`)

```python
def test_hq_posting():
    """
    Tests @wirereporthq posting.
    - Creates test tweet
    - Adds to queue
    - Verifies processing
    - Confirms posting
    """

def test_wnba_posting():
    """
    Tests @wirereportwnba flow.
    - Adds to WNBA queue
    - Simulates remote poll
    - Verifies acknowledgment
    - Checks sync-back
    """

def test_rate_limiting():
    """
    Verifies rate limit compliance.
    - Checks current limits
    - Tests enforcement
    - Validates budgets
    - Confirms blocking
    """
```

---

This reference guide provides comprehensive documentation of all major functions in the Wire Report system. Each function includes its purpose, parameters, process flow, and return values to aid in understanding and development.

*Last Updated: August 2, 2025*