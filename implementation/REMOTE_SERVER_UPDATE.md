# Remote Server Update Instructions
Generated: 2025-08-02 5:20 PM EDT

## Critical Updates for @wirereportwnba Server (155.138.211.147)
## Brain Server Location: 216.128.150.51

### 1. Smart Rate Limiting Implementation
**IMPORTANT**: Rate limit checks count against your API limit! We've implemented smart local tracking to minimize API calls.

### 2. Key Changes to Implement

#### A. Update Queue Processor
Your queue processor should:
1. Track posted tweets locally (don't call Twitter API to check limits)
2. Record each successful post timestamp
3. Use rolling 24-hour window (not daily reset)

#### B. Rate Limit Tracking
```python
# Add to your queue processor
class LocalRateLimiter:
    def __init__(self):
        self.posted_tweets = []  # List of timestamps
        self.daily_limit = 17
        
    def can_post(self):
        # Remove tweets older than 24 hours
        cutoff = datetime.now() - timedelta(hours=24)
        self.posted_tweets = [t for t in self.posted_tweets if t > cutoff]
        return len(self.posted_tweets) < self.daily_limit
    
    def record_post(self):
        self.posted_tweets.append(datetime.now())
```

#### C. Media URL Formatting
**CRITICAL**: Media URLs must be placed at the END of tweets for proper embedding:
```python
if tweet.get('media_embed_url'):
    content = tweet['content']
    media_url = tweet['media_embed_url']
    formatted_content = f"{content}\n\n{media_url}"  # Media at END
```

### 3. Stop Broadcasting Rate Limits
Since rate limit checks cost API calls:
- Only check when absolutely necessary (e.g., after errors)
- Don't broadcast rate limits back to brain server frequently
- Track locally and sync periodically instead

### 4. Current Status
- Your account (@wirereportwnba) has ~7 tweets remaining in current 24h window
- @wirereporthq is rate limited until 8:11 PM EDT

### 5. Sync Command
Run this periodically to sync with brain server:
```bash
# Get current queue
curl http://216.128.150.51:8080/api/queues/wnba

# Report posted tweet (only after successful post)
curl -X POST http://216.128.150.51:8080/api/tweets/posted \
  -H "Content-Type: application/json" \
  -d '{"twitter_id": "...", "content": "...", "account": "@wirereportwnba"}'
```

### 6. Testing Recommendation
Before going live:
1. Test with a single tweet
2. Verify local tracking works
3. Ensure media URLs format correctly
4. Confirm posts report back to brain

### 7. Error Handling
If you hit rate limits:
- Calculate when oldest tweet expires (24 hours after posting)
- Wait until then to resume
- Don't repeatedly check API status

## For Other Future League Servers

When setting up new league servers (@wirereportnfl, etc.):
1. Use the same local rate limiting approach
2. Each account gets 17 tweets per rolling 24-hour window
3. Track posts locally, minimize API calls
4. Always format media URLs at the end
5. Report successful posts back to brain server

## Questions?
Contact brain server admin or check `/root/wirereport/CLAUDE.md` for latest architecture updates.