# WNBA Remote Server - Fix Tweet Processing Issue

## Current Status
Your server IS successfully connecting to the brain server and receiving tweets, but you're not processing them. The connection is working - the issue is in your processing logic.

## What's Happening (From Logs)
1. ✅ Your server (155.138.211.147) connects to brain server (216.128.150.51:8080)
2. ✅ You receive 796 bytes of queue data with 5 tweets
3. ❌ You process 0 tweets and acknowledge 0 items
4. ❌ No tweets are posted to @wirereportwnba

## The Fix - Check Your Processing Script

### 1. Verify JSON Structure
The API returns this structure:
```json
{
  "queue": [  // ← Note: it's "queue" not "tweets"
    {
      "id": "trending_win_20250802_012030",
      "content": "🏆 Victory! The Sun pick up their FIFTH WIN...",
      "league": "WNBA",
      "account": "@wirereportwnba",
      "priority": 8,
      "metadata": {...}
    },
    // ... more tweets
  ],
  "count": 5,
  "total_in_queue": 5
}
```

### 2. Fix Your Code
Make sure you're extracting tweets correctly:
```python
# WRONG - if you're doing this:
tweets = response.json()  # This gives you the wrapper object

# CORRECT - do this instead:
data = response.json()
tweets = data.get('queue', [])  # Extract the actual tweet list
```

### 3. Check Media Handling
One tweet has media that MUST be at the END:
```python
# For tweet with media_embed_url:
if 'media_embed_url' in tweet:
    media_url = tweet['media_embed_url']
    content = tweet['content']
    # Ensure media URL is at the END for proper embedding
    final_content = f"{content}\n\n{media_url}"
```

### 4. Debug Your Loop
Add logging to see what's happening:
```python
response = requests.get("http://216.128.150.51:8080/api/queues/wnba")
print(f"Status: {response.status_code}")
data = response.json()
print(f"Keys in response: {data.keys()}")
tweets = data.get('queue', [])
print(f"Number of tweets: {len(tweets)}")

posted_ids = []
for tweet in tweets:
    print(f"Processing tweet: {tweet['id']}")
    # Your posting logic here
    success = post_to_twitter(tweet)
    if success:
        posted_ids.append(tweet['id'])
        print(f"Posted: {tweet['id']}")
    else:
        print(f"Failed: {tweet['id']}")

# Acknowledge
if posted_ids:
    ack_data = {
        "tweet_ids": posted_ids,
        "server_ip": "155.138.211.147"
    }
    requests.post(
        "http://216.128.150.51:8080/api/queues/wnba/ack",
        json=ack_data
    )
```

## Queue Format Specification

### Required Tweet Structure
Every tweet in the queue MUST have these fields:
```json
{
  "id": "unique_identifier",           // REQUIRED: Unique ID for tracking
  "content": "Tweet text here...",     // REQUIRED: Must be a STRING (not object!)
  "league": "WNBA",                    // REQUIRED: League identifier
  "account": "@wirereportwnba",        // REQUIRED: Target account
  "created_at": "2025-08-02T...",      // REQUIRED: ISO timestamp
  "content_type": "game_update",       // REQUIRED: Type of content
  "priority": 8,                       // REQUIRED: 1-10 (10 = highest)
  "metadata": {                        // OPTIONAL: Additional data
    "source": "trending_monitor",
    "engagement_score": 817
  },
  "media_embed_url": "https://..."     // OPTIONAL: Media URL (must go at END!)
}
```

### Common Format Issues to Avoid
❌ **WRONG - Content as object** (this was causing failures):
```json
{
  "content": {
    "status": "completed",
    "task_id": "830fe65c5393175b"
  }
}
```

✅ **CORRECT - Content as string**:
```json
{
  "content": "🏀 WNBA Update: The league continues to showcase incredible talent!"
}
```

### Media Embedding Rules
If a tweet has `media_embed_url`, you MUST:
1. Place the URL at the VERY END of the tweet
2. Add proper spacing (usually `\n\n`) before the URL
3. Keep attribution (via @source) BEFORE the URL

Example:
```
🔥 Amazing play by A'ja Wilson!

📸 via @WNBA

#WomensBasketball

https://x.com/WNBA/status/123456/video/1
```

## Current Queue Contents (5 Tweets Ready)

1. **Victory Tweet** (ID: trending_win_20250802_012030)
   - Sun's 5th win vs defending champs

2. **Ally Schlegel Goal** (ID: trending_goal_20250802_012500)
   - Has media_embed_url that MUST go at END of tweet!

3. **Wire Report 2.0 Announcement** (ID: wr2_teaser_wnba_20250802_014134)
   - Product launch tweet

4. **WNBA Update** (ID: swarm_WNBA_20250801_232644)
   - General coverage tweet

5. **Test Tweet** (ID: test_wnba_content_20250801_225600)
   - Enhanced context system tweet

## Validation Code to Add

Add this validation to your processing script to prevent format issues:

```python
def validate_tweet(tweet):
    """Validate tweet format before processing."""
    required_fields = ['id', 'content', 'league', 'account', 'created_at', 'content_type', 'priority']
    
    # Check required fields
    for field in required_fields:
        if field not in tweet:
            print(f"❌ Missing required field: {field}")
            return False
    
    # CRITICAL: Ensure content is a string
    if not isinstance(tweet.get('content'), str):
        print(f"❌ Tweet {tweet.get('id')} has invalid content type: {type(tweet.get('content'))}")
        return False
    
    # Ensure content is not empty
    if not tweet.get('content', '').strip():
        print(f"❌ Tweet {tweet.get('id')} has empty content")
        return False
    
    # Check priority is valid
    priority = tweet.get('priority', 0)
    if not isinstance(priority, int) or priority < 1 or priority > 10:
        print(f"⚠️ Tweet {tweet.get('id')} has invalid priority: {priority}")
    
    return True

# In your main loop:
for tweet in tweets:
    if not validate_tweet(tweet):
        print(f"Skipping invalid tweet: {tweet.get('id', 'unknown')}")
        continue
    
    # Process valid tweet
    if 'media_embed_url' in tweet:
        # Format with media at END
        content = tweet['content'] + "\n\n" + tweet['media_embed_url']
    else:
        content = tweet['content']
    
    # Post to Twitter...
```

## Quick Test Commands

Run these on your server to debug:

```bash
# 1. Test queue fetch manually
curl http://216.128.150.51:8080/api/queues/wnba | jq .

# 2. Check if you see "queue" key with 5 tweets
curl http://216.128.150.51:8080/api/queues/wnba | jq '.queue | length'

# 3. Get first tweet content
curl http://216.128.150.51:8080/api/queues/wnba | jq '.queue[0].content'

# 4. Check your script logs
tail -f /path/to/your/posting/script/logs
```

## Common Queue Processing Errors and Solutions

### Error 1: Processing 0 tweets despite receiving data
**Symptom**: Logs show "Processing 0 tweets, acknowledging 0" but received 796 bytes
**Cause**: Not extracting the 'queue' key from response
**Fix**:
```python
# Wrong:
tweets = response.json()  # This is the wrapper object!

# Correct:
data = response.json()
tweets = data['queue']  # Extract the actual tweet array
```

### Error 2: Tweet content is not a string
**Symptom**: TypeError or posting failure
**Cause**: Malformed tweet where content is an object instead of string
**Fix**: Always validate content type before processing

### Error 3: Media URL not embedding
**Symptom**: Tweet posts but media doesn't show
**Cause**: Media URL not at the END of tweet
**Fix**: Always append media_embed_url at the very end

## Expected Fix Result

Once you fix the JSON parsing:
1. Your script will see 5 tweets in the queue
2. Post each one to @wirereportwnba
3. Acknowledge the posted IDs
4. @wirereportwnba will start tweeting!

## Rate Limit Note

Your rate limit API on port 8081 is timing out. Either:
- Fix the service on port 8081, OR
- Tell us what port it's actually running on

---

**Priority**: URGENT - The connection works, just fix the JSON parsing!
**Brain Server**: 216.128.150.51:8080 (working fine)
**Your Server**: 155.138.211.147 (connecting fine, processing broken)