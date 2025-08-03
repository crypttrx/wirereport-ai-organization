# WireReport Master Plan - The Definitive Guide
**Date: August 3, 2025**
**Status: STOP REFACTORING - STABILIZE AND EXECUTE**

## 🎯 Core Mission
Generate 17 high-quality tweets per day per account (@wirereporthq, @wirereportwnba, @wirereportnfl) using proven @wirereportnba formatting patterns.

---

## 📍 WHERE WE STAND RIGHT NOW

### ✅ What's Working
1. **Queue API System** (`/root/wirereport_api/`)
   - Port 8080 serving queues to remote servers
   - WNBA server (155.138.211.147) polling successfully
   - NFL server (45.76.7.74) configured and ready
   - Queue files properly structured

2. **@WireReportNBA Proven Patterns**
   - Quote tweet formatting with "via @" attribution
   - Media URLs at END of content (critical for embedding)
   - Third-person voice, no "we/I/our"
   - 1-2 emojis max, strategic placement
   - Verified content only (no hallucinations)

3. **Remote Server Architecture**
   - HQ: Local processing via OAuth 1.0a
   - WNBA: Remote server polls queue every 30s
   - NFL: Remote server polls queue every 30s

### ❌ Current Problems
1. **Too Many Production Services Running**
   ```
   wirereport-production.service         ← Duplicate
   wirereport-trending.service           ← Duplicate
   wirereport-unified-production.service ← Keep this one
   wirereport-media-production.service   ← Stopped
   ```

2. **Multiple Scripts Doing Same Thing**
   - `complete_production_system.py`
   - `full_production_pipeline.py`
   - `media_enhanced_production.py`
   - `trending_production_24_7.py`
   - `verified_production_pipeline.py`
   
3. **Unclear Which Pipeline to Use**
   - No single source of truth
   - Each script has slightly different logic
   - Wasting API calls with duplicates

4. **Queue Overflow**
   - Generating too many tweets (20+ in queue)
   - Not respecting 17/day limit
   - Old tweets expiring before posting

---

## 📋 THE DEFINITIVE PLAN

### Phase 1: Stop the Bleeding (IMMEDIATE)
1. **Stop ALL duplicate services**
   ```bash
   systemctl stop wirereport-production.service
   systemctl stop wirereport-trending.service
   systemctl disable wirereport-production.service
   systemctl disable wirereport-trending.service
   ```

2. **Pick ONE production pipeline**
   - Use: `verified_production_pipeline.py` (has all verification)
   - Why: Already integrates Senior Editor, fact-checking, proper formatting

3. **Enforce Queue Limits**
   - Max 5 tweets per queue at any time
   - 4-hour expiry for old tweets
   - Check rate limits BEFORE generating

### Phase 2: Consolidate Production (THIS WEEK)

#### The ONE Production Pipeline Architecture:
```
                    ┌─────────────────────┐
                    │  SINGLE API CALL    │
                    │  Harvest Trending   │
                    │  (All Leagues)      │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Categorize by      │
                    │  League (NBA/WNBA/  │
                    │  NFL/Multi)         │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Check Rate Limits  │
                    │  for Each Account   │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Apply Engagement   │
                    │  Thresholds Based   │
                    │  on Budget          │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Senior Editor      │
                    │  Verification       │
                    │  (No Hallucinations)│
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Format with        │
                    │  @WireReportNBA     │
                    │  Patterns           │
                    └──────────┬──────────┘
                               │
                    ┌──────────▼──────────┐
                    │  Add to Queues      │
                    │  (Max 5 per queue)  │
                    └─────────────────────┘
```

### Phase 3: Core Features to Preserve

#### 1. **@WireReportNBA Formatting** (NEVER CHANGE)
```python
# Quote Tweet Format
content = f'"{engaging_commentary}" {1-2_emojis} #{relevant_hashtags}'
if media_url:
    content = f"{content}\n\nvia @{original_author}\n{media_url}"

# Reply Format  
content = f"{thoughtful_response} {emoji} #{hashtag}"

# Breaking News Format
content = f"🚨 {news} {details} #{team}"
```

#### 2. **Queue API Endpoints** (NEVER CHANGE)
- `/api/queues/wnba` - WNBA server polls
- `/api/queues/nfl` - NFL server polls
- `/api/tweets/posted` - Report posted tweets
- `/api/context/posted_tweets` - Context for AI

#### 3. **Media URL Handling** (CRITICAL)
```python
# ALWAYS at END of tweet for proper embedding
formatted_content = f"{tweet_text}\n\n{media_embed_url}"
```

### Phase 4: Production Settings

#### Rate Management
```python
DAILY_LIMIT = 17  # Per account
MAX_QUEUE_SIZE = 5  # Never exceed
TWEET_EXPIRY_HOURS = 4  # Remove old tweets

# Dynamic Thresholds
if available_slots > 10:
    min_engagement = 500
elif available_slots >= 5:
    min_engagement = 2000
else:
    min_engagement = 5000
```

#### Content Sources (Priority Order)
1. **Trending Tweets** (90% of content)
   - Real tweets with high engagement
   - Quote, reply, or get inspired by

2. **Breaking News** (5% of content)
   - RSS feeds from ESPN, BR, CBS
   - Rapid response within 5 minutes

3. **Alternative Content** (5% of content)
   - YouTube podcasts
   - Reddit discussions
   - Historical "on this day"

---

## 🚦 WHAT TO RUN (DEFINITIVE LIST)

### Keep Running:
```bash
✅ wirereport-brain.service          # Brain API (port 8000)
✅ wirereport-wnba-api.service       # Queue API (port 8080)
✅ wirereport-hq-queue.service       # HQ posting agent
✅ wirereport-telegram.service       # Control center
✅ wirereport-unified-production     # ONE production pipeline
```

### Stop/Disable:
```bash
❌ wirereport-production.service     # Duplicate
❌ wirereport-trending.service       # Duplicate
❌ wirereport-media-production       # Old version
❌ Any cron jobs for production      # Use systemd only
```

---

## 📊 Success Metrics

### Daily Targets
- **Tweets Posted**: 17 per account (not more, not less)
- **Engagement Rate**: >5% (replies, likes, retweets)
- **Hallucination Rate**: 0% (all verified content)
- **API Efficiency**: <50 OpenAI calls per day

### Queue Health
- **Queue Size**: ≤5 tweets at any time
- **Tweet Age**: <4 hours old
- **Verification**: 100% verified_content=true

---

## 🛑 RULES - NEVER BREAK THESE

1. **NEVER** change the @wirereportnba formatting patterns
2. **NEVER** move media URLs from end of tweet
3. **NEVER** break the queue API for remote servers
4. **NEVER** generate more than 5 tweets per queue
5. **NEVER** make multiple API calls for same content
6. **ALWAYS** verify content before posting
7. **ALWAYS** check rate limits before generating
8. **ALWAYS** use "via @" for media attribution

---

## 🔄 Daily Operation Flow

### Every 5 Minutes:
1. Check rate limits for all accounts
2. If slots available AND queue <5:
   - Make ONE API call for trending content
   - Filter by engagement threshold
   - Verify with Senior Editor
   - Format with proven patterns
   - Add to appropriate queue

### Every 30 Seconds:
- Remote servers poll their queues
- HQ processor checks local queue
- Posted tweets reported back

### Every Hour:
- Clean expired tweets from queues
- Sync rate limit tracking
- Log performance metrics

---

## 📝 Next Steps (IN ORDER)

1. **TODAY**: Stop duplicate services
2. **TODAY**: Verify queue API still working
3. **TODAY**: Set queue limit to 5
4. **TOMORROW**: Test remote server polling
5. **THIS WEEK**: Monitor and stabilize
6. **NEXT WEEK**: Optimize based on metrics

---

## 🎯 End Goal

A stable, efficient system that:
- Generates exactly 17 quality tweets per day per account
- Uses proven @wirereportnba formatting
- Makes minimal API calls
- Never hallucinates
- Runs without manual intervention
- Scales easily to new leagues

**STOP REFACTORING. START EXECUTING.**