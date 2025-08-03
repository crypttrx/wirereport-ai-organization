# 🔴 Real-Time Integration Guide

## Overview

The Real-Time Integrator is a comprehensive system that continuously monitors live sports events, breaking news, and provides real-time intelligence updates across all sources. It seamlessly integrates with all existing Wire Report intelligence systems to enhance content generation with live data.

## Key Features

### 🚀 Real-Time Data Streams
- **Twitter Breaking News**: Monitors breaking news tweets and insider reports
- **ESPN Live Scores**: Tracks live game events and score updates
- **NBA API Integration**: Official game data and statistics
- **Social Media Trending**: Trending topics and viral content
- **Trade Rumors**: Insider reports and trade deadline monitoring
- **Injury Reports**: Real-time injury detection and impact analysis

### 🧠 Intelligent Processing
- **Event Correlation**: Automatically links related events across sources
- **Duplicate Detection**: Prevents redundant event processing
- **Priority Scoring**: Intelligent event prioritization system
- **Verification System**: Multi-source event verification
- **Impact Analysis**: Fantasy and betting impact calculations
- **Entity Extraction**: Players, teams, and league identification

### 🔗 System Integration
- **Breaking News Synthesis**: Enhanced with real-time events
- **Player Intelligence**: Live performance and news updates
- **Team Intelligence**: Real-time roster and organizational changes
- **Historical Data Mining**: Continuous data ingestion
- **Context Enhancement**: Real-time context for tweet generation

## Quick Start

### Basic Usage

```python
from intelligence.agents.realtime_integrator import (
    get_realtime_integrator,
    start_realtime_monitoring,
    get_breaking_news_events,
    get_player_events,
    get_team_events
)

# Start real-time monitoring
integrator = await start_realtime_monitoring()

# Get breaking news events
breaking_news = await get_breaking_news_events(limit=10)

# Get player-specific events
lebron_events = await get_player_events("LeBron James")

# Get team-specific events  
lakers_events = await get_team_events("Lakers")
```

### Integration with Tweet Generation

```python
# Enhanced tweet generation with real-time context
async def generate_enhanced_tweets():
    # Get recent breaking news
    breaking_news = await get_breaking_news_events(limit=5)
    
    for event in breaking_news:
        if event.priority.value >= EventPriority.HIGH.value:
            # Generate breaking news tweet
            tweet_data = {
                'title': event.title,
                'description': event.description,
                'entities': event.entities,
                'priority': event.priority.name,
                'verification': event.verification_status
            }
            
            # Use existing tweet generation with enhanced context
            generated_tweet = await generate_wire_report_tweet(tweet_data)
            
            # Post if approved
            if should_auto_post(event.priority):
                await post_tweet(generated_tweet)
```

## Event Types

The system processes the following event types:

| Event Type | Description | Priority Range |
|------------|-------------|----------------|
| `BREAKING_NEWS` | Major breaking news stories | HIGH - ULTRA_CRITICAL |
| `TRADE` | Player trades and acquisitions | MEDIUM - ULTRA_CRITICAL |
| `SIGNING` | Free agent signings and contracts | MEDIUM - CRITICAL |
| `INJURY` | Player injuries and medical updates | MEDIUM - CRITICAL |
| `LINEUP_CHANGE` | Starting lineup and roster changes | LOW - MEDIUM |
| `SCORE_UPDATE` | Live game scores and updates | LOW - MEDIUM |
| `RECORD_ACHIEVEMENT` | Records and milestones | MEDIUM - HIGH |
| `SOCIAL_TRENDING` | Trending social media topics | LOW - MEDIUM |
| `PRESS_CONFERENCE` | Press conferences and interviews | LOW - MEDIUM |
| `LEAGUE_ANNOUNCEMENT` | Official league announcements | MEDIUM - HIGH |

## Alert System

### Alert Configuration

```python
# Configure custom alerts
alert_config = AlertConfiguration(
    event_type=EventType.TRADE,
    min_priority=EventPriority.HIGH,
    keywords=["traded", "acquired", "deal"],
    entities_filter=["Lakers", "Warriors"],  # Optional team filter
    cooldown_minutes=30,
    notification_channels=["telegram", "slack", "webhook"]
)
```

### Notification Channels

1. **Telegram**: Instant mobile notifications
2. **Slack**: Team workspace alerts  
3. **Webhook**: Custom API integration

## Dashboard and Monitoring

### Real-Time Dashboard Data

```python
# Get comprehensive dashboard data
dashboard = get_realtime_dashboard_data()

print(f"Active Streams: {dashboard['system_status']['active_streams']}")
print(f"Events Today: {dashboard['event_statistics']['total_events']}")
print(f"Breaking News: {len(dashboard['recent_events'])}")
```

### System Health Monitoring

```python
# Check system health
integrator = get_realtime_integrator()
health = integrator.get_system_health()

print(f"System Running: {health['system_running']}")
print(f"Database Status: {health['database_accessible']}")
print(f"Active Streams: {health['active_streams']}")
```

## Intelligence System Integration

### Player Intelligence Updates

The real-time integrator automatically updates player intelligence profiles:

```python
# Player events automatically update:
# - Recent performance changes
# - Injury status updates
# - Trade rumors and news
# - Social media buzz
# - Market value changes

# Access enhanced player context
player_context = await player_intelligence.get_enhanced_context("LeBron James")
```

### Team Intelligence Updates

Team profiles are continuously updated with:

```python
# Team events automatically update:
# - Roster changes
# - Trade acquisitions
# - Injury reports
# - Performance trends
# - Organizational news

# Access enhanced team context
team_context = await team_intelligence.get_enhanced_context("Lakers")
```

### Breaking News Synthesis

Enhanced breaking news synthesis with real-time correlation:

```python
# Breaking news events are automatically:
# - Correlated across sources
# - Verified through multiple channels
# - Enhanced with historical context
# - Synthesized into comprehensive reports

# Access synthesized breaking news
synthesized_reports = await breaking_news_synthesizer.get_recent_reports()
```

## Advanced Features

### Event Correlation

Events are automatically correlated based on:
- Entity overlap (players, teams, leagues)
- Temporal proximity (time-based relationships)
- Content similarity (duplicate detection)
- Source diversity (multi-source verification)

### WebSocket Real-Time Updates

```python
# Subscribe to real-time updates
import websockets

async def handle_realtime_updates():
    uri = "ws://localhost:8766"
    async with websockets.connect(uri) as websocket:
        async for message in websocket:
            data = json.loads(message)
            if data['type'] == 'event_update':
                await process_new_event(data['event'])
```

### Context Cache Updates

The system maintains a real-time context cache:

```python
# Context is automatically updated for:
# - Player recent events
# - Team news and changes  
# - Trending topics
# - Market movements
# - Social sentiment

# Access context cache
context_file = integrator.data_dir / "real_time_context.json"
with open(context_file, 'r') as f:
    real_time_context = json.load(f)
```

## Configuration

### Environment Variables

```bash
# API Keys
RAPIDAPI_KEY=your_rapidapi_key
OPENAI_API_KEY=your_openai_key

# Alert Channels
TELEGRAM_BOT_TOKEN=your_telegram_token
TELEGRAM_CHAT_ID=your_chat_id
SLACK_WEBHOOK_URL=your_slack_webhook
WEBHOOK_URL=your_custom_webhook

# Database
REALTIME_DB_PATH=data/realtime_intelligence/realtime_events.db
```

### Stream Configuration

```python
# Customize polling intervals
stream_config = {
    'twitter_breaking_news': 60,    # 1 minute
    'espn_live_scores': 30,         # 30 seconds  
    'nba_api_games': 45,            # 45 seconds
    'social_trending': 300          # 5 minutes
}
```

## Performance Optimization

### Rate Limiting

- Automatic rate limit management for all API sources
- Intelligent backoff strategies
- Priority-based request queuing

### Caching

- Event deduplication cache (1 hour window)
- Context cache for enhanced tweet generation
- Performance metrics caching

### Database Management

- Automatic cleanup of expired events
- Efficient indexing for quick queries
- Backup and recovery capabilities

## Testing

### Run Comprehensive Tests

```bash
# Full system test
python test_realtime_integrator.py

# Integration demo
python demo_realtime_integration.py
```

### Unit Testing

```python
# Test specific functionality
async def test_breaking_news():
    events = await get_breaking_news_events(limit=5)
    assert len(events) <= 5
    
    for event in events:
        assert event.priority.value >= EventPriority.HIGH.value
        assert event.event_type == EventType.BREAKING_NEWS
```

## Production Deployment

### System Requirements

- Python 3.8+
- SQLite 3.x
- 8GB+ RAM (for high-volume processing)
- Reliable internet connection
- API rate limit headroom

### Monitoring

- Set up health check endpoints
- Configure alert thresholds
- Monitor API rate limits
- Track processing latency

### Scaling

- Horizontal scaling with multiple workers
- Load balancing for WebSocket connections
- Database sharding for high volume
- CDN for static dashboard assets

## Troubleshooting

### Common Issues

1. **API Rate Limits**: Check rate limit status and adjust polling intervals
2. **Database Locks**: Ensure proper connection management
3. **Memory Usage**: Monitor event queue size and processed events
4. **Network Issues**: Implement retry logic and fallback sources

### Debug Mode

```python
# Enable debug logging
logging.getLogger('intelligence.agents.realtime_integrator').setLevel(logging.DEBUG)

# Check system health
health = integrator.get_system_health()
print(json.dumps(health, indent=2))
```

## API Reference

### Core Functions

```python
# Primary integration functions
get_realtime_integrator(project_root: Path) -> RealtimeIntegrator
start_realtime_monitoring() -> RealtimeIntegrator
get_breaking_news_events(limit: int = 20) -> List[RealTimeEvent]
get_player_events(player_name: str) -> List[RealTimeEvent]  
get_team_events(team_name: str) -> List[RealTimeEvent]
get_realtime_dashboard_data() -> Dict[str, Any]

# Event filtering
get_live_events(
    event_types: List[EventType] = None,
    min_priority: EventPriority = EventPriority.LOW,
    limit: int = 100
) -> List[RealTimeEvent]

# Entity-specific queries
get_entity_events(entity_name: str, entity_type: str = None) -> List[RealTimeEvent]
```

### Data Structures

```python
@dataclass
class RealTimeEvent:
    event_id: str
    event_type: EventType
    priority: EventPriority
    title: str
    description: str
    entities: Dict[str, List[str]]
    metadata: Dict[str, Any]
    source_id: str
    source_type: str
    confidence_score: float
    verification_status: str
    created_at: datetime
    expires_at: Optional[datetime]
    related_events: List[str]
    impact_score: float
    geographic_scope: str
```

## Best Practices

### Event Processing

1. **Prioritize High-Impact Events**: Focus processing on breaking news and trades
2. **Verify Before Publishing**: Use multi-source verification for important news
3. **Maintain Context**: Link related events for comprehensive coverage
4. **Monitor Performance**: Track processing latency and queue sizes

### Content Generation

1. **Real-Time Enhancement**: Use live events to enhance tweet relevance
2. **Context Integration**: Incorporate real-time context in all content
3. **Priority-Based Posting**: Auto-post high-priority breaking news
4. **Audience Targeting**: Use entity filters for account-specific content

### System Maintenance

1. **Regular Health Checks**: Monitor system health and stream status
2. **Database Cleanup**: Automatically clean expired events and logs
3. **Performance Monitoring**: Track memory usage and processing times
4. **Alert Management**: Configure appropriate alert thresholds

## Support

For questions, issues, or feature requests:

1. Check the troubleshooting section
2. Review system health status
3. Enable debug logging for detailed information
4. Test individual components with provided test scripts

## Version History

- **v1.0**: Initial real-time integration system
- Features: Multi-source monitoring, event correlation, intelligence integration
- Capabilities: Breaking news synthesis, player/team tracking, alert system
- Performance: Sub-second event processing, real-time WebSocket updates

---

The Real-Time Integrator transforms Wire Report from a periodic content generator into a truly real-time sports intelligence platform, capable of detecting, processing, and responding to breaking news and live events as they happen.