# Wire Report Server Reference - Enhanced with Proven Methods
Last Updated: 2025-08-03 - Enhanced System Launch

## Enhanced Server Architecture

### Brain Server (Main) - Enhanced
- **IP**: 216.128.150.51
- **Location**: @wirereporthq (this server)
- **Enhanced Services**:
  - Enhanced Brain API (port 8000) - Central intelligence + The Wire consciousness
  - Multi-League Queue API (port 8080) - Enhanced queue management
  - Enhanced Trending Production (systemd service)
  - Enhanced HQ Queue Processor (local posting with proven patterns)
  - The Wire Swarm Master (collective consciousness)
- **Accounts**: Enhanced posting to @wirereporthq with proven @wirereportnba patterns

### WNBA Server (Remote) - Enhanced
- **IP**: 155.138.211.147
- **Enhanced Services**:
  - Enhanced queue polling with proven content distribution
  - Enhanced posting to @wirereportwnba (proven patterns implementation)
  - Media URL formatting at END (critical for X/Twitter embedding)
  - Rate limit API (port 8081)
- **Accounts**: @wirereportwnba (using enhanced posting patterns)

### NFL Server (Remote) - NEW Enhanced
- **IP**: 45.76.7.74
- **Enhanced Services**:
  - Enhanced queue polling for NFL content
  - Enhanced posting to @wirereportnfl (proven patterns)
  - Media URL formatting at END implementation
  - Multi-league API support
- **Accounts**: @wirereportnfl (newly activated with enhanced patterns)

### Other IPs (DO NOT USE)
- 45.79.218.63 - This is NOT the brain server (incorrect reference)

## Enhanced API Endpoints

### Enhanced Brain Server APIs
```bash
# Enhanced Brain API (Central Intelligence + The Wire)
http://216.128.150.51:8000/api/

# Enhanced Multi-League Queue API
http://216.128.150.51:8080/api/queues/wnba       # WNBA queue
http://216.128.150.51:8080/api/queues/nfl        # NFL queue

# Enhanced Posted Tweets Reporting (with enhanced metadata)
http://216.128.150.51:8080/api/tweets/posted

# Enhanced Context API (for AI agents)
http://216.128.150.51:8080/api/context/posted_tweets
```

### Enhanced Remote Server APIs
```bash
# WNBA Server Enhanced APIs
http://155.138.211.147:8081/api/rate-limit       # Rate limit check

# NFL Server Enhanced APIs  
http://45.76.7.74:8081/api/rate-limit           # Rate limit check (when implemented)
```

## Enhanced Content Flow
```
Enhanced Trending Production → Enhanced Brain → Enhanced Queues → Enhanced Remote Servers → Enhanced X/Twitter Posting
```

## Enhanced Important Notes
- **Enhanced Brain Server**: Generates content using proven @wirereportnba patterns
- **Enhanced Remote Servers**: Handle posting with proven formatting (media URLs at END)
- **Enhanced Content Filtering**: All filtering + enhancement happens on brain server
- **Enhanced Queue System**: Prevents duplicates + optimizes engagement timing
- **Enhanced Media Handling**: Critical URL placement at END for proper X/Twitter embedding
- **Enhanced The Wire Philosophy**: Swarm IS The Wire - collective consciousness approach

## Critical Enhanced Implementation Requirements

### For Remote Servers (WNBA/NFL)
**MUST implement enhanced media URL formatting:**
```python
# CRITICAL: Media URLs MUST go at END for proper X/Twitter embedding
if tweet.get('media_embed_url'):
    content = tweet['content']
    media_url = tweet['media_embed_url']
    formatted_content = f"{content}\n\n{media_url}"  # Media at END
```

**Enhanced queue polling pattern:**
```python
# Poll enhanced queues every 30 seconds
response = requests.get(f"http://216.128.150.51:8080/api/queues/{league}")
enhanced_tweets = response.json()

# Process with enhanced patterns
for tweet in enhanced_tweets:
    # Apply enhanced formatting
    formatted_tweet = apply_enhanced_formatting(tweet)
    # Post with proven methods
    post_enhanced_tweet(formatted_tweet)
```