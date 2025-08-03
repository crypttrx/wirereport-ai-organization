# 🚨 URGENT: Wire Report WNBA Remote Server Connection Fix (CORRECTED)

## Critical Issue
@wirereportwnba hasn't posted any tweets despite having content ready in the queue. The remote server needs to connect to the CORRECT brain server IP.

## CORRECT SERVER IPs
- **Brain Server (THIS SERVER)**: 216.128.150.51
- **Queue API Port**: 8080
- **WNBA Remote Server**: 155.138.211.147
- **WireReportNBA Server**: 45.76.61.139 (different server - not used here)

## Immediate Actions Required

### 1. Update Your Configuration
The WNBA remote server must connect to the CORRECT brain server:
```python
# CORRECT configuration
BRAIN_SERVER_URL = "http://216.128.150.51:8080"
```

### 2. Test Brain Server Connection
Run this command on the WNBA remote server (155.138.211.147):
```bash
# Test the CORRECT brain server
curl http://216.128.150.51:8080/api/queues/wnba
```

You should see 5 tweets ready to post. If you were connecting to 45.77.66.197 or 45.76.61.139, that was WRONG.

### 3. Update All API Calls

**Fetch tweets from queue:**
```bash
GET http://216.128.150.51:8080/api/queues/wnba
```

**Acknowledge after posting:**
```bash
POST http://216.128.150.51:8080/api/queues/wnba/ack
Body: {
  "tweet_ids": ["id1", "id2"],
  "server_ip": "155.138.211.147"
}
```

**Report successful posts:**
```bash
POST http://216.128.150.51:8080/api/tweets/posted
Body: {
  "queue_id": "original_queue_id",
  "twitter_id": "twitter_post_id",
  "content": "tweet content",
  "posted_at": "ISO timestamp",
  "account": "@wirereportwnba",
  "league": "WNBA"
}
```

### 4. Update Your Posting Script
Make sure ALL references point to 216.128.150.51:
```python
import requests

# CORRECT brain server
BRAIN_API = "http://216.128.150.51:8080"

# Fetch queue
response = requests.get(f"{BRAIN_API}/api/queues/wnba")
queue_data = response.json()

# Process tweets...

# Acknowledge
ack_response = requests.post(
    f"{BRAIN_API}/api/queues/wnba/ack",
    json={"tweet_ids": posted_ids, "server_ip": "155.138.211.147"}
)

# Report posted
report_response = requests.post(
    f"{BRAIN_API}/api/tweets/posted",
    json=posted_tweet_data
)
```

### 5. Debug Commands

Run these on the WNBA remote server:

```bash
# 1. Test CORRECT brain server
curl -v http://216.128.150.51:8080/api/queues/wnba

# 2. Check old incorrect connections
grep -r "45.77.66.197\|45.76.61.139" /path/to/your/scripts/

# 3. Update any incorrect IPs found
sed -i 's/45.77.66.197/216.128.150.51/g' /path/to/your/script.py
sed -i 's/45.76.61.139/216.128.150.51/g' /path/to/your/script.py

# 4. Restart your service
systemctl restart wirereport-wnba-poster

# 5. Check logs
journalctl -u wirereport-wnba-poster -f
```

### 6. Rate Limit API Configuration

For the brain server to check WNBA rate limits, update this file on the brain server:
`/root/wirereport_api/rate_limit_manager.py`

Should have:
```python
"@wirereportwnba": {
    "ip": "155.138.211.147",
    "port": 8081,  # Or whatever port your rate limit API uses
    "health_endpoint": "/api/rate-limit/status"
}
```

## Current Queue Status

5 tweets are waiting in the queue:
1. Test tweet
2. Game update
3. Victory announcement (Sun vs defending champs)
4. Ally Schlegel goal with media (needs URL at END)
5. Wire Report 2.0 announcement

## Expected Behavior After Fix

1. WNBA server polls http://216.128.150.51:8080/api/queues/wnba
2. Receives 5 tweets
3. Posts to @wirereportwnba
4. Acknowledges back to brain server
5. Reports successful posts

## Critical Note About Media

For the tweet with media_embed_url, the URL MUST be placed at the END of the tweet content for proper embedding on X!

---

**CORRECTED IPs:**
- **Brain Server**: 216.128.150.51:8080 ✅
- **NOT**: 45.77.66.197 or 45.76.61.139 ❌
- **WNBA Remote**: 155.138.211.147

**Priority**: CRITICAL - Fix IP configuration immediately!