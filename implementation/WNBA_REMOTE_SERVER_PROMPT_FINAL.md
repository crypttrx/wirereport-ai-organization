# 🚨 URGENT: Wire Report WNBA Remote Server Connection Fix

## Critical Issue
@wirereportwnba hasn't posted any tweets despite having content ready in the queue. The remote server appears to be having connection/processing issues.

## Immediate Actions Required

### 1. Test Brain Server Connection
Run this command on the WNBA remote server (155.138.211.147):
```bash
curl http://45.77.66.197:8080/api/queues/wnba
```

You should see 5 tweets ready to post. If this times out or returns empty, there's a connection issue.

### 2. Fix Queue Processing
I've cleaned up a malformed tweet that was blocking the queue. The queue now has 5 valid tweets ready:
- 1 test tweet
- 1 game update 
- 2 trending news (one with media that needs URL at end)
- 1 Wire Report 2.0 announcement

### 3. Update Your Posting Script
Make sure your script:
1. **Validates content is a string** before processing
2. **Handles media URLs properly** (must be at END of tweet for embedding)
3. **Acknowledges posted tweets** back to brain server

### 4. Required API Endpoints

**Fetch tweets from queue:**
```bash
GET http://45.77.66.197:8080/api/queues/wnba
```

**Acknowledge after posting:**
```bash
POST http://45.77.66.197:8080/api/queues/wnba/ack
Body: {
  "tweet_ids": ["id1", "id2"],
  "server_ip": "155.138.211.147"
}
```

**Report successful posts:**
```bash
POST http://45.77.66.197:8080/api/tweets/posted
Body: {
  "queue_id": "original_queue_id",
  "twitter_id": "twitter_post_id",
  "content": "tweet content",
  "posted_at": "ISO timestamp",
  "account": "@wirereportwnba",
  "league": "WNBA"
}
```

### 5. Debug Checklist

Run these commands on the WNBA server:

```bash
# 1. Test queue API is reachable
curl -v http://45.77.66.197:8080/api/queues/wnba

# 2. Check your service is running
systemctl status wirereport-wnba-poster

# 3. Check recent logs
journalctl -u wirereport-wnba-poster -n 50

# 4. Test posting script manually
python3 /path/to/your/posting_script.py --test

# 5. Check network connectivity
ping 45.77.66.197
```

### 6. Rate Limit API Issue

The rate limit API at http://155.138.211.147:8081 is not responding. This needs to be fixed or the brain server updated to use correct port. Current config expects port 8081.

## Expected Behavior

Once fixed, the WNBA server should:
1. Poll http://45.77.66.197:8080/api/queues/wnba every 30 seconds
2. Receive 5 tweets in the queue
3. Post each tweet to @wirereportwnba
4. Acknowledge posted tweets back to brain
5. Report successful posts for tracking

## Quick Fix if Needed

If the remote server can't be fixed immediately, I can:
1. Move WNBA posting to the brain server (like HQ)
2. Update the configuration to post directly
3. This would be temporary until remote server is fixed

## Current Queue Sample
Here's what's waiting to be posted:
```json
{
  "id": "trending_goal_20250802_012500",
  "content": "🔥 Update: Ally Schlegel. The Header. The Equalizer.\n\n🎥 via @JustWSports\n\n#WNBA #WomensBasketball",
  "media_embed_url": "https://x.com/JustWSports/status/1951476427423097045/video/1"
}
```
**Note**: The media_embed_url must be placed at the END of the tweet content for proper embedding!

---

**Priority**: CRITICAL - @wirereportwnba needs to start posting
**Brain Server**: 45.77.66.197:8080 (working)
**WNBA Server**: 155.138.211.147 (needs attention)
**Queue Status**: 5 valid tweets ready to post