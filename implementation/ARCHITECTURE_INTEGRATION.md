# WireReport Architecture Integration Specifications
# Security-Enhanced League-Agnostic System

## Overview

This document provides comprehensive integration specifications for the WireReport security-enhanced, league-agnostic architecture. The system has been designed to support multi-league operations with robust security, scalable queue-based communication, and flexible deployment configurations.

## Architecture Components

### 1. Enhanced Central Dispatcher (`pipelines/central_dispatcher.py`)

**Integration Points:**
- **Security Framework**: Validates all tweet content using `security.input_validation`
- **Secure Configuration**: Uses `security.secure_config` for league config validation
- **Rate Limiting**: Integrates `security.rate_limiting` for operation throttling
- **Queue Communication**: Routes to secure queues instead of direct HTTP dispatch

**Key Enhancements:**
```python
# Security-validated tweet processing
def determine_tweet_league(tweet: Dict[str, Any]) -> str:
    if SECURITY_ENABLED and SECURE_VALIDATOR:
        validation_result = SECURE_VALIDATOR.validate_tweet_content(tweet, ...)
        if not validation_result.is_valid:
            return "HQ"  # Safe fallback
        tweet = validation_result.sanitized_data
```

**Configuration Loading:**
```python
def load_league_configs():
    # Enhanced validation with security integration
    is_valid, validation_details = validate_league_config(league_name, module)
    if validation_details.get("security_validated"):
        validation_summary["security_validated"] += 1
```

### 2. Secure Queue Dispatcher (`pipelines/secure_queue_dispatcher.py`)

**Purpose**: Complete security-first implementation of the central dispatcher using queue-based communication.

**Key Features:**
- Full security framework integration
- Secure queue-based tweet processing  
- Multi-server brain-to-poster communication
- Comprehensive audit logging

**Usage:**
```bash
# Single cycle execution
python pipelines/secure_queue_dispatcher.py --single

# Continuous operation
python pipelines/secure_queue_dispatcher.py
```

**Integration with Security:**
```python
def validate_and_sanitize_tweet(self, tweet: Dict[str, Any], league_id: str):
    validation_result = self.validator.validate_tweet_content(
        tweet, league_id=league_id, validation_level=ValidationLevel.MODERATE
    )
    # Returns sanitized content with validation metadata
```

### 3. League Configuration Manager (`config/league_config_manager.py`)

**Standardization**: Provides unified schema and management for all league configurations.

**Schema Structure:**
```python
@dataclass
class LeagueConfigSchema:
    # Core identification
    enabled: bool
    league_id: str
    league_name: str
    
    # Security integration
    poster_endpoint: str  # Validated for HTTPS
    supported_tweet_types: List[str]  # Validated against allowed types
    
    # Content and engagement settings
    min_engagement_score: int
    blocked_keywords: List[str]
    boost_keywords: List[str]
```

**Security Integration:**
```python
def validate_config_structure(self, config_data: Dict[str, Any], league_id: str):
    # Security validation if available
    if self.secure_config:
        security_result = self.secure_config.validate_league_config(mock_module)
        result.security_validated = security_result["valid"]
```

**CLI Usage:**
```bash
# Validate all configurations
python config/league_config_manager.py --validate

# Create new league config
python config/league_config_manager.py --create NFL --name "National Football League" --endpoint "https://api.nfl.com/post"

# Show system status
python config/league_config_manager.py --status
```

### 4. Multi-Server Architecture (`architecture/multi_server_manager.py`)

**Purpose**: Manages communication between brain servers (content generation) and poster servers (social media posting).

**Server Roles:**
- **BRAIN**: Content generation and processing
- **POSTER**: Social media posting  
- **HYBRID**: Both brain and posting capabilities
- **MONITOR**: Monitoring and health checks

**Load Balancing Strategies:**
- `round_robin`: Distributes requests evenly
- `least_load`: Routes to server with lowest load
- `league_affinity`: Prefers servers dedicated to specific leagues

**Deployment Configuration** (`config/deployment.json`):
```json
{
  "brain_servers": [
    {
      "server_id": "brain-primary",
      "host": "localhost", 
      "port": 8001,
      "leagues": ["HQ", "NBA", "WNBA"],
      "capabilities": ["content_generation", "security_validation"]
    }
  ],
  "poster_servers": [
    {
      "server_id": "poster-nba",
      "host": "45.76.61.139",
      "port": 8000,
      "leagues": ["NBA"],
      "capabilities": ["twitter_posting", "queue_consumption"]
    }
  ]
}
```

**Integration with Secure Queues:**
```python
def send_via_secure_queue(self, league: str, tweet_data: Dict[str, Any]):
    success, message_id = self.queue_manager.send_message(
        client_id="brain_server",
        message_type=MessageType.TWEET,
        league_id=league,
        content=tweet_data,
        priority=priority
    )
```

## Security Framework Integration

### 1. Secure Configuration (`security/secure_config.py`)

**Integration Points:**
- League configuration validation
- Credential management for API keys
- Environment-specific settings
- Security headers for HTTP requests

**Usage in Components:**
```python
# In central dispatcher
SECURE_CONFIG_MANAGER = init_security_config(project_root)
league_security_config = SECURE_CONFIG_MANAGER.get_league_security_config(league)
```

### 2. Input Validation (`security/input_validation.py`)

**Integration Points:**
- Tweet content sanitization
- SQL injection prevention
- Risk score calculation
- Multi-level validation (BASIC, MODERATE, STRICT)

**Usage in Processing:**
```python
validation_result = validator.validate_tweet_content(
    tweet, league_id="NBA", validation_level=ValidationLevel.MODERATE
)
if validation_result.is_valid:
    sanitized_tweet = validation_result.sanitized_data
```

### 3. Secure Queue Communication (`security/secure_queue.py`)

**Features:**
- Authenticated message queuing
- Message integrity verification (HMAC)
- Optional message encryption
- Rate limiting and abuse prevention
- League-specific queue isolation

**Client Authentication:**
```python
# Clients defined in secure queue system
clients = {
    "central_dispatcher": {
        "permissions": ["send", "receive", "admin"],
        "rate_limit": 1000
    },
    "nba_poster": {
        "permissions": ["receive"], 
        "rate_limit": 100
    }
}
```

### 4. Rate Limiting (`security/rate_limiting.py`)

**Integration Points:**
- League-specific rate limits
- Endpoint protection
- Burst detection
- Emergency bypass capabilities

## Deployment Architecture

### Brain Server Configuration

**Primary Brain Server (localhost:8001)**:
- Content generation for all leagues
- Security validation and sanitization
- Queue message production
- Health monitoring

**Setup:**
```bash
# Initialize security components
python -c "from security.secure_config import init_security_config; init_security_config()"

# Start secure queue dispatcher
python pipelines/secure_queue_dispatcher.py
```

### Poster Server Configuration

**HQ Poster (localhost:8000)**:
- Cross-league content aggregation
- @WireReportHQ posting
- Queue message consumption

**NBA Poster (45.76.61.139:8000)**:
- NBA-specific content posting
- @WireReportNBA posting
- High-volume processing

**Setup:**
```bash
# Configure league-specific poster
export LEAGUE_ID=NBA
export POSTER_ENDPOINT=http://45.76.61.139:8000/post

# Start poster service with queue consumption
python scripts/poster_server.py --league NBA --consume-queue
```

### Queue Flow Architecture

```
[Brain Server] 
    ↓ (Secure Queue)
[Multi-Server Manager]
    ↓ (Load Balancing)
[Poster Servers]
    ↓ (Twitter API)
[Social Media Platforms]
```

**Message Flow:**
1. Brain server processes tweets through security validation
2. Messages queued with authentication and integrity verification
3. Multi-server manager routes to appropriate poster servers
4. Poster servers consume queue and post to social media

## Integration Specifications for Queue Management Subagent

### Queue Structure Requirements

**Message Format:**
```python
{
    "id": "unique_message_id",
    "type": "tweet|reply|retweet|breaking_news", 
    "league_id": "NBA|WNBA|HQ|NFL",
    "content": {
        "original_tweet": {...},
        "processed_content": {...},
        "security_metadata": {...}
    },
    "priority": "LOW|NORMAL|HIGH",
    "timestamp": "ISO_timestamp",
    "sender_id": "brain_server_id"
}
```

**Queue Operations Required:**
- `enqueue_tweet()`: Add tweet to league-specific queue
- `get_next_tweet()`: Retrieve highest priority tweet
- `mark_tweet_dispatched()`: Mark successful dispatch
- `mark_tweet_failed()`: Handle failed dispatch with retry logic
- `cleanup_expired_messages()`: Remove old messages

**Security Requirements:**
- All queue operations must use authenticated clients
- Message integrity verification via HMAC signatures
- Optional encryption for sensitive content
- Rate limiting per client and operation type
- Comprehensive audit logging

### Performance Requirements

**Throughput:**
- Support 1000+ messages per hour per league
- Sub-second message queuing latency
- Handle burst traffic during breaking news

**Reliability:**
- Message persistence across system restarts
- Automatic retry for failed dispatches
- Dead letter queue for permanently failed messages
- Health monitoring and alerting

### Monitoring and Observability

**Metrics to Track:**
- Queue depth per league
- Message processing rates
- Dispatch success/failure rates
- Security validation metrics
- Server health and availability

**Logging Requirements:**
- All queue operations with timestamps
- Security events and violations
- Performance metrics and alerts
- Error conditions and recovery actions

## Configuration Management Best Practices

### League Configuration Standards

1. **Required Fields**: All leagues must define core identification, endpoints, and supported features
2. **Security Validation**: Configurations must pass security framework validation
3. **Versioning**: Track configuration changes with version numbers and timestamps
4. **Backup**: Automatic backup of configuration changes
5. **Environment Separation**: Different configs for dev/staging/production

### Security Configuration

1. **Credential Storage**: All API keys encrypted and stored securely
2. **Environment Variables**: Sensitive values loaded from environment
3. **Access Control**: Role-based access to configuration management
4. **Audit Trail**: Complete log of configuration changes
5. **Validation**: Automated testing of configuration changes

## Operational Procedures

### Deployment Process

1. **Brain Server Deployment**:
   ```bash
   # Deploy secure queue dispatcher
   python pipelines/secure_queue_dispatcher.py --single  # Test
   python pipelines/secure_queue_dispatcher.py          # Production
   ```

2. **Poster Server Deployment**:
   ```bash
   # Deploy league-specific poster
   python scripts/poster_server.py --league NBA --consume-queue
   ```

3. **Health Monitoring**:
   ```bash
   # Start multi-server health monitoring
   python architecture/multi_server_manager.py --monitor
   ```

### Troubleshooting Guide

**Queue Issues:**
- Check secure queue client authentication
- Verify message integrity and signatures
- Monitor rate limiting and quotas
- Review audit logs for security violations

**Configuration Issues:**
- Validate league configurations: `python config/league_config_manager.py --validate`
- Check security validation results
- Verify endpoint connectivity and HTTPS usage
- Review deployment configuration for server discovery

**Security Issues:**
- Check credential encryption and storage
- Verify input validation and sanitization
- Monitor rate limiting and abuse detection
- Review audit logs for unauthorized access

This integrated architecture provides a robust, secure, and scalable foundation for WireReport's multi-league social media automation system.