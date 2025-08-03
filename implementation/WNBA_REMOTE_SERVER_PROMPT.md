# URGENT: Wire Report WNBA Remote Server Fix Needed

## Current Issue
The @wirereportwnba account hasn't been posting despite having 6 tweets in the queue. The remote server at 155.138.211.147 is polling the brain server but acknowledging 0 items, indicating a processing issue.

## Problem Identified
1. **Malformed Tweet in Queue**: Tweet ID `swarm_WNBA_20250801_232004` has content as an object instead of a string:
   ```json
   "content": {
     "status": "completed",
     "task_id": "830fe65c5393175b"
   }
   ```
   This should be a string containing the actual tweet text.

2. **Connection Issue**: The brain server cannot reach the WNBA rate limit API at http://155.138.211.147:8081/api/rate-limit/status

## Server Details
- **Brain Server Queue API**: http://45.77.66.197:8080
- **WNBA Remote Server**: 155.138.211.147
- **Expected Rate Limit API**: http://155.138.211.147:8081

## Current Queue Status
The brain server has 6 tweets ready for @wirereportwnba:
- 1 test tweet
- 2 game updates (one malformed)
- 2 trending news (one with media)
- 1 Wire Report 2.0 announcement

## Actions Needed on WNBA Remote Server

### 1. Fix Queue Processing
Update the tweet processing code to handle/skip malformed tweets:

```python
# In your queue processing logic, add validation:
for tweet in queue_data:
    # Skip if content is not a string
    if not isinstance(tweet.get('content'), str):
        logger.warning(f"Skipping malformed tweet {tweet.get('id')}: content is not a string")
        continue
    
    # Process valid tweets
    content = tweet['content']
    # ... rest of processing
```

### 2. Verify Queue Polling
Check that your polling is working correctly:
```bash
# Test queue endpoint manually
curl http://45.77.66.197:8080/api/queues/wnba

# Should return tweets, not empty array
```

### 3. Fix Acknowledgment
Ensure you're acknowledging the correct tweet IDs after posting:
```python
# After successful posting:
ack_data = {
    "tweet_ids": [tweet['id'] for tweet in successfully_posted],
    "server_ip": "155.138.211.147"
}
response = requests.post(
    "http://45.77.66.197:8080/api/queues/wnba/ack",
    json=ack_data
)
```

### 4. Start/Fix Rate Limit API
The rate limit API at port 8081 is not responding. Please ensure it's running:
```bash
# Check if service is running
systemctl status wirereport-wnba-ratelimit

# Or check what's on port 8081
sudo netstat -tlnp | grep 8081
```

### 5. Report Posted Tweets
After posting, report back to brain server:
```python
report_data = {
    "queue_id": tweet['id'],
    "twitter_id": response_from_twitter['id'],
    "content": tweet['content'],
    "posted_at": datetime.now().isoformat(),
    "account": "@wirereportwnba",
    "league": "WNBA"
}
response = requests.post(
    "http://45.77.66.197:8080/api/tweets/posted",
    json=report_data
)
```

## Quick Debug Commands

Run these on the WNBA remote server:

```bash
# 1. Test queue fetch
curl http://45.77.66.197:8080/api/queues/wnba | jq .

# 2. Check your posting script logs
tail -f /path/to/your/posting/logs

# 3. Manually test posting with first valid tweet
# (Skip the malformed one)

# 4. Check if rate limit service is running
ps aux | grep -E "rate|limit|8081"
```

## Expected Resolution
Once fixed, the WNBA remote server should:
1. Successfully fetch tweets from the queue
2. Skip/handle the malformed tweet
3. Post the 5 valid tweets
4. Acknowledge posted tweets back to brain server
5. Report successful posts for context tracking

## Contact
If you need the malformed tweet removed from the queue on the brain server side, let me know and I can clean it up.

---

**Priority**: HIGH - @wirereportwnba needs to start posting ASAP
**Queue Status**: 6 tweets waiting (5 valid, 1 malformed)