# Wire Report API Endpoints Complete Guide

This document provides comprehensive documentation for all API endpoints across the Wire Report system.

---

## Overview

The Wire Report system uses multiple API servers for different functions:

- **Brain API** (Port 8000): Central intelligence and swarm coordination
- **Queue API** (Port 8080): Tweet queue management and distribution
- **Rate Limit API** (Port 8081): Remote server rate limit checking
- **Health Monitoring**: Built into all services

---

## Brain API Server (Port 8000)

**Base URL**: `http://localhost:8000`

### POST /api/think

Central content generation endpoint for swarm coordination.

**Purpose**: Processes content generation requests from swarm agents

**Request**:
```json
{
  "task_type": "generate_tweet",
  "league": "NBA",
  "context": {
    "game_id": "12345",
    "priority": 8,
    "content_type": "game_update"
  },
  "account": "@wirereporthq",
  "parameters": {
    "max_length": 240,
    "include_emojis": true,
    "hashtags": ["#NBA", "#WireReport"]
  }
}
```

**Response**:
```json
{
  "success": true,
  "content": {
    "text": "🏀 FINAL: Lakers 118, Celtics 114\n\nLeBron: 35pts, 12ast | Tatum: 41pts, 8reb\n\nLakers complete the comeback in Boston! #NBA #WireReport",
    "metadata": {
      "character_count": 134,
      "emoji_count": 1,
      "hashtag_count": 2,
      "generated_at": "2025-08-02T10:15:30Z"
    }
  },
  "task_id": "brain_task_123456"
}
```

**Error Response**:
```json
{
  "success": false,
  "error": "Rate limit exceeded",
  "error_code": "RATE_LIMIT",
  "retry_after": 3600
}
```

### GET /api/status

Returns current swarm operational status.

**Response**:
```json
{
  "swarm_status": "active",
  "active_agents": 187,
  "tasks_in_progress": 12,
  "daily_budgets": {
    "@wirereporthq": {
      "used": 8,
      "remaining": 9,
      "last_reset": "2025-08-02T00:00:00Z"
    },
    "@wirereportwnba": {
      "used": 12,
      "remaining": 5,
      "last_reset": "2025-08-02T00:00:00Z"
    }
  },
  "error_counts": {
    "last_hour": 2,
    "last_24h": 15
  },
  "uptime": "18h 32m 15s"
}
```

### POST /api/feedback

Receives performance feedback from posting operations.

**Request**:
```json
{
  "tweet_id": "queue_id_123",
  "twitter_id": "1690123456789",
  "success": true,
  "engagement": {
    "likes": 45,
    "retweets": 12,
    "replies": 8,
    "impressions": 2340
  },
  "posted_at": "2025-08-02T10:20:00Z",
  "account": "@wirereporthq"
}
```

**Response**:
```json
{
  "feedback_recorded": true,
  "optimization_applied": true,
  "new_strategy_score": 0.73
}
```

### GET /health

Service health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-02T10:25:00Z",
  "service": "brain_api",
  "uptime": 67890.5,
  "checks": {
    "database": "connected",
    "swarm_master": "active",
    "memory_usage": "45%",
    "cpu_usage": "12%",
    "openai_api": "responsive"
  },
  "version": "2.0.1"
}
```

---

## Queue API Server (Port 8080)

**Base URL**: `http://localhost:8080`

### GET /api/queues/wnba

Remote servers poll this endpoint to retrieve pending tweets.

**Query Parameters**:
- `league` (optional): Filter by league (default: WNBA)
- `limit` (optional): Max tweets to return (default: 5, max: 10)
- `since` (optional): ISO timestamp for filtering recent tweets
- `priority_min` (optional): Minimum priority level (1-10)

**Example Request**:
```
GET /api/queues/wnba?league=WNBA&limit=3&since=2025-08-02T10:00:00Z&priority_min=7
```

**Response**:
```json
{
  "tweets": [
    {
      "id": "trending_win_20250802_012030",
      "content": "🏆 Victory! The Sun pick up their FIFTH WIN of the season against the defending champs 😯\n\nJust two months ago New York beat Connecticut by 48 POINTS 😳\n\n#WNBA #WomensBasketball",
      "league": "WNBA",
      "account": "@wirereportwnba",
      "created_at": "2025-08-02T01:20:30.958922",
      "content_type": "trending_news",
      "priority": 8,
      "metadata": {
        "source": "trending_monitor",
        "topic": "win",
        "urgency": "medium",
        "engagement_score": 817
      }
    },
    {
      "id": "trending_goal_20250802_012500",
      "content": "🔥 Update: Ally Schlegel. The Header. The Equalizer.\n\n🎥 via @JustWSports\n\n#WNBA #WomensBasketball",
      "media_embed_url": "https://x.com/JustWSports/status/1951476427423097045/video/1",
      "league": "WNBA",
      "account": "@wirereportwnba",
      "created_at": "2025-08-02T01:25:00.000000",
      "content_type": "trending_news",
      "priority": 10,
      "metadata": {
        "source": "trending_monitor",
        "topic": "goal",
        "urgency": "high",
        "engagement_score": 1000,
        "has_media": true,
        "media_source": "JustWSports"
      }
    }
  ],
  "total_available": 6,
  "queue_size": 6,
  "server_time": "2025-08-02T10:30:00Z"
}
```

### POST /api/queues/wnba/ack

Remote servers acknowledge successful processing of tweets.

**Request**:
```json
{
  "tweet_ids": [
    "trending_win_20250802_012030",
    "trending_goal_20250802_012500"
  ],
  "server_ip": "155.138.211.147",
  "processed_at": "2025-08-02T10:32:00Z"
}
```

**Response**:
```json
{
  "acknowledged": true,
  "removed_count": 2,
  "remaining_queue_size": 4,
  "message": "Tweets successfully acknowledged and removed from queue"
}
```

### POST /api/tweets/posted

Reports successfully posted tweets for removal from queue and context tracking.

**Request**:
```json
{
  "queue_id": "trending_win_20250802_012030",
  "twitter_id": "1690987654321",
  "content": "🏆 Victory! The Sun pick up their FIFTH WIN...",
  "posted_at": "2025-08-02T10:33:15Z",
  "account": "@wirereportwnba",
  "league": "WNBA",
  "engagement": {
    "initial_impressions": 150
  }
}
```

**Response**:
```json
{
  "success": true,
  "removed_from_queue": true,
  "added_to_history": true,
  "context_updated": true,
  "posted_tweet_id": "posted_tweet_456789"
}
```

### GET /api/context/posted_tweets

Provides historical context for content generation agents.

**Query Parameters**:
- `league` (optional): Filter by league (default: all)
- `hours` (optional): Hours to look back (default: 24, max: 168)
- `limit` (optional): Max tweets to return (default: 100, max: 500)
- `account` (optional): Filter by account

**Example Request**:
```
GET /api/context/posted_tweets?league=WNBA&hours=48&limit=50
```

**Response**:
```json
{
  "posted_tweets": [
    {
      "twitter_id": "1690987654321",
      "content": "🏆 Victory! The Sun pick up their FIFTH WIN...",
      "account": "@wirereportwnba",
      "league": "WNBA",
      "posted_at": "2025-08-02T10:33:15Z",
      "engagement": {
        "likes": 23,
        "retweets": 5,
        "replies": 3,
        "impressions": 1240
      },
      "content_type": "trending_news",
      "topics": ["win", "Sun", "victory"]
    }
  ],
  "total_tweets": 23,
  "date_range": {
    "from": "2025-07-31T10:33:15Z",
    "to": "2025-08-02T10:33:15Z"
  },
  "league_breakdown": {
    "WNBA": 23,
    "NBA": 0
  }
}
```

### POST /api/sync/posted_tweets

Legacy endpoint for two-way sync with remote servers.

**Request**:
```json
{
  "tweets": [
    {
      "twitter_id": "1690987654321",
      "content": "Posted tweet content...",
      "account": "@wirereportwnba",
      "posted_at": "2025-08-02T10:33:15Z"
    }
  ],
  "server_info": {
    "ip": "155.138.211.147",
    "sync_time": "2025-08-02T10:35:00Z"
  }
}
```

**Response**:
```json
{
  "synced_count": 1,
  "duplicates_found": 0,
  "updated_context": true
}
```

### GET /api/sync/posted_tweets/all

Returns all recently posted tweets for duplicate checking.

**Query Parameters**:
- `hours` (optional): Hours to look back (default: 24)

**Response**:
```json
{
  "all_posted": [
    {
      "twitter_id": "1690987654321",
      "content_hash": "abc123def456",
      "posted_at": "2025-08-02T10:33:15Z",
      "account": "@wirereportwnba"
    }
  ],
  "total_count": 45,
  "last_updated": "2025-08-02T10:35:00Z"
}
```

### GET /health

Queue API health check.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-02T10:30:00Z",
  "service": "queue_api",
  "uptime": 45230.2,
  "checks": {
    "database": "connected",
    "queue_files": "accessible",
    "memory_usage": "28%",
    "disk_usage": "65%",
    "brain_api": "connected"
  },
  "queue_stats": {
    "hq_queue_size": 4,
    "wnba_queue_size": 0,
    "processed_today": 89
  }
}
```

---

## Rate Limit API (Remote Server - Port 8081)

**Base URL**: `http://155.138.211.147:8081`

### GET /api/rate-limit/status

Brain server checks remote account rate limit status before generating content.

**Response**:
```json
{
  "account": "@wirereportwnba",
  "rate_limit_status": {
    "tweets_remaining": 9,
    "reset_time": "2025-08-03T00:00:00Z",
    "limit": 17,
    "used": 8
  },
  "posting_enabled": true,
  "last_post": "2025-08-02T09:45:00Z",
  "server_time": "2025-08-02T10:30:00Z"
}
```

**Rate Limited Response**:
```json
{
  "account": "@wirereportwnba",
  "rate_limit_status": {
    "tweets_remaining": 0,
    "reset_time": "2025-08-03T00:00:00Z",
    "limit": 17,
    "used": 17
  },
  "posting_enabled": false,
  "reason": "Daily limit reached",
  "next_available": "2025-08-03T00:00:00Z"
}
```

---

## Health Monitoring Endpoints

All services implement consistent health check endpoints for monitoring.

### Standard Health Check Response Format

```json
{
  "status": "healthy" | "degraded" | "unhealthy",
  "timestamp": "2025-08-02T10:30:00Z",
  "service": "service_name",
  "uptime": 45230.2,
  "checks": {
    "dependency1": "status",
    "dependency2": "status"
  },
  "metrics": {
    "memory_usage": "28%",
    "cpu_usage": "15%",
    "disk_usage": "65%"
  },
  "version": "2.0.1"
}
```

### Service-Specific Health Endpoints

1. **Brain API**: `http://localhost:8000/health`
2. **Queue API**: `http://localhost:8080/health`
3. **Rate Limit API**: `http://155.138.211.147:8081/health`

---

## Error Handling

### Standard Error Response Format

```json
{
  "error": true,
  "error_code": "ERROR_TYPE",
  "message": "Human readable error message",
  "details": {
    "field": "specific error details",
    "suggestion": "recommended action"
  },
  "timestamp": "2025-08-02T10:30:00Z",
  "request_id": "req_12345"
}
```

### Common Error Codes

- `RATE_LIMIT`: Rate limit exceeded
- `INVALID_REQUEST`: Malformed request
- `UNAUTHORIZED`: Authentication failed
- `NOT_FOUND`: Resource not found
- `SERVER_ERROR`: Internal server error
- `TIMEOUT`: Request timeout
- `SERVICE_UNAVAILABLE`: Service temporarily down

---

## Authentication & Security

### IP Whitelisting

The Queue API (port 8080) uses IP-based access control:

**Allowed IPs**:
- `155.138.211.147` (WNBA server)
- `127.0.0.1`, `::1` (localhost)

**Blocked Response**:
```json
{
  "error": true,
  "error_code": "UNAUTHORIZED",
  "message": "IP address not authorized",
  "client_ip": "192.168.1.100"
}
```

### Request Validation

All endpoints validate:
- Content-Type headers
- Required fields
- Data types
- Value ranges
- JSON structure

---

## Rate Limiting

### API Rate Limits

- **Brain API**: 100 requests/minute per IP
- **Queue API**: 60 requests/minute per IP
- **Health Endpoints**: 30 requests/minute per IP

### Rate Limit Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1690987200
X-RateLimit-RetryAfter: 60
```

---

## Testing Endpoints

### cURL Examples

**Test Brain API**:
```bash
curl -X POST http://localhost:8000/api/think \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "generate_tweet",
    "league": "NBA",
    "context": {"game_id": "12345"},
    "account": "@wirereporthq"
  }'
```

**Check Queue**:
```bash
curl "http://localhost:8080/api/queues/wnba?limit=3" | jq .
```

**Health Check**:
```bash
curl http://localhost:8000/health | jq .
```

**Rate Limit Status**:
```bash
curl http://155.138.211.147:8081/api/rate-limit/status | jq .
```

---

## Integration Examples

### Python Client Example

```python
import aiohttp
import asyncio

class WireReportAPI:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        
    async def get_queue_tweets(self, league="WNBA", limit=5):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/queues/{league.lower()}"
            params = {"league": league, "limit": limit}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"API Error: {response.status}")
    
    async def acknowledge_tweets(self, tweet_ids, server_ip):
        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/queues/wnba/ack"
            data = {
                "tweet_ids": tweet_ids,
                "server_ip": server_ip
            }
            
            async with session.post(url, json=data) as response:
                return await response.json()

# Usage
async def main():
    api = WireReportAPI()
    tweets = await api.get_queue_tweets(limit=3)
    print(f"Retrieved {len(tweets['tweets'])} tweets")

asyncio.run(main())
```

---

## Monitoring & Observability

### Metrics Collection

All endpoints collect metrics:
- Request count
- Response time
- Error rate
- Status code distribution

### Logging Format

```json
{
  "timestamp": "2025-08-02T10:30:00Z",
  "level": "INFO",
  "service": "queue_api",
  "endpoint": "/api/queues/wnba",
  "method": "GET",
  "status_code": 200,
  "response_time_ms": 45,
  "client_ip": "155.138.211.147",
  "user_agent": "WireReport-WNBA/1.0"
}
```

---

This comprehensive API guide provides all necessary information for integrating with and maintaining the Wire Report system's API infrastructure.

*Last Updated: August 2, 2025*