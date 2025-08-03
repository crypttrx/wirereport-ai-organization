# WNBA Server Update: Implementing @wirereportnba Posting Rules

## Overview
The brain server has analyzed @wirereportnba's posting patterns and created centralized posting rules. The WNBA server needs to update its posting logic to follow these rules when processing tweets from the queue.

## Required Updates

### 1. Media URL Formatting
The brain server stores `media_embed_url` as a separate field in the queue. The WNBA server MUST format media URLs at the END of tweet content before posting:

```python
# In your posting logic, add this formatting:
def format_tweet_for_posting(tweet_data):
    content = tweet_data.get('content', '')
    media_url = tweet_data.get('media_embed_url')
    
    if media_url:
        # Add photo credit if applicable
        if "/photo/" in media_url and tweet_data.get('source'):
            content += f"\n\n📷 via @{tweet_data['source'].lstrip('@')}"
        
        # Add media URL at end for X/Twitter embedding
        content += f"\n{media_url}"
    
    return content
```

### 2. Tweet Type Priorities
Respect the priority field in queued tweets:
- breaking/breaking_news: priority 10
- quote/quote_tweet: priority 5
- reply: priority 3
- general content: priority 1

Process higher priority tweets first when multiple tweets are in queue.

### 3. Duplicate Prevention
Before posting, check:
- Hash field for exact duplicates
- Source tweet ID to prevent reposting same source
- Posted tweets history via brain API

```python
# Check with brain server before posting
def check_duplicate(tweet_data):
    # Call brain API endpoint
    response = requests.get(
        f"http://45.33.23.224:8080/api/context/posted_tweets?league=WNBA&hours=48",
        headers={"X-Server-IP": "155.138.211.147"}
    )
    
    if response.ok:
        posted_tweets = response.json()
        tweet_hash = tweet_data.get('hash')
        source_id = tweet_data.get('source_tweet_id')
        
        for posted in posted_tweets:
            if tweet_hash and posted.get('hash') == tweet_hash:
                return True
            if source_id and str(posted.get('source_tweet_id')) == str(source_id):
                return True
    
    return False
```

### 4. Reply Formatting
For reply tweets (type="reply"):
- Use `in_reply_to_id` field to thread properly
- Never exceed 280 characters
- Format as Twitter API v2 reply:

```python
payload = {
    "text": formatted_content,
    "reply": {"in_reply_to_tweet_id": tweet_data.get('in_reply_to_id')}
}
```

### 5. Quote Tweet Formatting
For quote tweets (type="quote" or "quote_tweet"):
- Extract tweet ID from `quoted_url` field
- Use `quote_tweet_id` in payload:

```python
import re

def format_quote_tweet(tweet_data):
    quoted_url = tweet_data.get('quoted_url', '')
    match = re.search(r"/status/(\d+)", quoted_url)
    
    if match:
        quote_tweet_id = match.group(1)
        payload = {
            "text": formatted_content,
            "quote_tweet_id": quote_tweet_id
        }
```

### 6. Reporting Posted Tweets
After successfully posting, immediately report back to brain:

```python
def report_posted_tweet(tweet_data, twitter_response):
    report_data = {
        "queue_id": tweet_data.get('id'),
        "twitter_id": twitter_response.get('data', {}).get('id'),
        "content": tweet_data.get('content'),
        "posted_at": datetime.utcnow().isoformat(),
        "account": "@wirereportwnba",
        "league": "WNBA",
        "type": tweet_data.get('type', 'general'),
        "source_tweet_id": tweet_data.get('source_tweet_id'),
        "hash": tweet_data.get('hash')
    }
    
    response = requests.post(
        "http://45.33.23.224:8080/api/tweets/posted",
        json=report_data,
        headers={"X-Server-IP": "155.138.211.147"}
    )
```

### 7. Rate Limit Integration
Before processing tweets, check your local rate limits AND report them to brain:

```python
# Your existing rate limit check
remaining = check_twitter_rate_limit()

# Report to brain for coordination
requests.post(
    "http://45.33.23.224:8081/api/rate_limit/update",
    json={
        "account": "@wirereportwnba",
        "remaining": remaining,
        "reset_time": reset_timestamp
    }
)
```

### 8. Stale Content Detection
Skip tweets with live-game keywords if they're too old:

```python
LIVE_KEYWORDS = [
    "currently", "right now", "ongoing", "closing minutes",
    "live look", "halftime", "3rd quarter", "tip-off"
]

def is_stale(tweet_data):
    content = tweet_data.get('content', '').lower()
    created_at = tweet_data.get('created_at')
    
    if any(keyword in content for keyword in LIVE_KEYWORDS):
        if created_at:
            tweet_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age_minutes = (datetime.utcnow() - tweet_time).total_seconds() / 60
            if age_minutes > 20:
                return True
    
    return False
```

## Implementation Checklist

1. [ ] Update tweet formatting to place media URLs at end
2. [ ] Implement priority-based queue processing
3. [ ] Add duplicate checking before posting
4. [ ] Update reply formatting for Twitter API v2
5. [ ] Update quote tweet formatting
6. [ ] Implement posted tweet reporting to brain
7. [ ] Add rate limit reporting to brain
8. [ ] Add stale content detection
9. [ ] Test with different tweet types from queue

## Testing

After implementing, test with:
1. A regular tweet with media_embed_url
2. A reply tweet with in_reply_to_id
3. A quote tweet with quoted_url
4. A breaking news tweet (high priority)

## Questions?
The brain server tracks all posting rules centrally. Any questions about specific rules should reference the @wirereportnba patterns we're following for consistency across all Wire Report accounts.