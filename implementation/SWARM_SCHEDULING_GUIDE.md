# Swarm-Managed Intelligent Scheduling Guide

This guide explains the migration from cron-based scheduling to swarm-managed intelligent scheduling that respects the 17-tweet daily limit.

---

## Problem Analysis

### Issue with Burst Posting
- 4 test tweets posted simultaneously to @wirereporthq
- No intelligent spacing or rate limit consideration
- Cron-based system doesn't understand tweet budgets
- Need intelligent distribution across 24-hour cycle

### wirereportnba Schedule Analysis
The existing wirereportnba cron schedule shows aggressive posting (100 tweets/day dev plan):
- Main queue flusher: Every 2 minutes (up to 25 tweets)
- WNBA tweets: Every 10 minutes  
- Breaking news: Every 16 minutes
- Reply bot: Every 40 minutes during peak hours
- Data fetching: Every 2-15 minutes depending on peak/off-peak

This approach would exhaust the 17-tweet limit in ~2 hours without intelligence.

---

## Solution: Swarm-Managed Scheduling

### New Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Schedule Orchestrator                       │
│              (Tier 2 Orchestrator)                        │
└─────────────────────┬───────────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───▼────┐    ┌──────▼──────┐    ┌─────▼─────┐
│Content │    │Rate Limit   │    │Intelligent│
│Tasks   │    │Tracking     │    │Queue      │
│        │    │(17/day)     │    │Processor  │
└────────┘    └─────────────┘    └───────────┘
```

### Key Features

1. **Rate Limit Awareness**
   - Tracks daily usage: X/17 tweets posted
   - Calculates remaining budget in real-time
   - Distributes remaining tweets across remaining hours

2. **Intelligent Timing Distribution**
   - Peak hours (10 PM - 6 AM ET): More frequent posting
   - Off-peak hours (6 AM - 10 PM ET): Reduced frequency
   - Adaptive intervals based on queue size and time remaining

3. **Content Quality Optimization**
   - Priority-based selection (breaking news first)
   - Content type diversity (mix of updates, highlights, insights)
   - Duplicate prevention across 24-hour window
   - Time-appropriate content (live updates during peak, historical during off-peak)

4. **Dynamic Interval Calculation**
   ```python
   # Example calculation
   remaining_tweets = 17 - posted_today
   hours_remaining = 24 - current_hour
   optimal_interval = (hours_remaining * 60) / remaining_tweets
   
   # Apply peak/off-peak multipliers
   if is_peak_hours():
       optimal_interval *= 0.7  # More frequent
   else:
       optimal_interval *= 1.3  # Less frequent
   ```

---

## Implementation Components

### 1. Schedule Orchestrator
**File**: `/root/wirereport/agents/tier2_orchestrators/schedule_orchestrator.py`

**Responsibilities**:
- Manages all scheduled tasks
- Replaces cron jobs with intelligent scheduling
- Coordinates with rate limit tracking
- Optimizes timing based on current state

**Key Functions**:
```python
async def get_adaptive_content_interval(self) -> int:
    """Calculate intelligent content generation interval."""
    total_remaining = sum(daily_limits) - sum(daily_usage)
    hours_remaining = 24 - current_hour
    return calculate_optimal_posting_rate()

async def content_generation_task(self):
    """Generate content only when budget allows."""
    if total_remaining <= 0:
        return  # Skip if daily limit reached
```

### 2. Intelligent Queue Processor
**File**: `/root/wirereport/agents/tier3_specialists/infrastructure/intelligent_queue_processor.py`

**Responsibilities**:
- Smart tweet selection from queues
- Content scoring and optimization
- Duplicate prevention
- Optimal timing calculation

**Key Features**:
```python
async def select_optimal_tweets(self, queue_data, count, account):
    """Select best tweets based on multiple factors."""
    # Scoring factors:
    # - Priority (40% weight)
    # - Content type (25% weight)  
    # - Recency (15% weight)
    # - Engagement prediction (10% weight)
    # - Time appropriateness (10% weight)
```

### 3. Migration Script
**File**: `/root/wirereport/scripts/disable_existing_crons.sh`

**Purpose**:
- Safely disable existing cron jobs
- Backup current crontab
- Keep only essential system tasks
- Verify swarm services are running

---

## Migration Process

### Step 1: Verify Swarm is Running
```bash
# Check services
systemctl status wirereport-swarm
systemctl status wirereport-brain
systemctl status wirereport-wnba-api

# Check logs
journalctl -u wirereport-swarm -f
```

### Step 2: Run Migration Script
```bash
# Execute migration (backs up existing crontab)
/root/wirereport/scripts/disable_existing_crons.sh

# Verify new minimal crontab
crontab -l
```

### Step 3: Monitor Intelligent Scheduling
```bash
# Watch schedule orchestrator logs
grep "Schedule Orchestrator" /root/wirereport/logs/*.log

# Monitor queue processing
grep "Intelligent queue processing" /root/wirereport/logs/*.log

# Check rate limit tracking
grep "Usage tracking" /root/wirereport/logs/*.log
```

---

## Schedule Comparison

### Before (Cron-Based)
```bash
# Aggressive, budget-unaware posting
*/2 * * * * tweet_poster.py --queue --max 25    # Every 2 min, up to 25 tweets
*/10 * * * * wnba_tweet_generator.py             # Every 10 min
6,22,38,54 * * * * breaking_news_pipeline.py    # Every 16 min
```
**Problem**: Could post 17 tweets in first hour, leaving nothing for remaining 23 hours.

### After (Swarm-Managed)
```python
# Intelligent, rate-limit aware scheduling
content_interval = calculate_adaptive_interval()  # Dynamic 10-120 minutes
queue_processing = calculate_dynamic_interval()   # Based on queue size + budget
breaking_news = 16  # Still frequent for urgent content
```
**Benefit**: Distributes 17 tweets intelligently across 24 hours.

---

## Expected Posting Pattern

### Optimal Distribution (17 tweets/day)
```
Time Range     | Tweets | Interval | Reasoning
---------------|--------|----------|------------------
12AM - 6AM     | 6      | ~60 min  | Peak sports hours
6AM - 12PM     | 3      | ~120 min | Morning content
12PM - 6PM     | 3      | ~120 min | Afternoon updates  
6PM - 12AM     | 5      | ~72 min  | Evening engagement
```

### Content Type Mix
```
Breaking News: 3-4 tweets  (Priority 10, immediate posting)
Game Updates:  4-5 tweets  (Priority 8-9, during/after games)
Highlights:    3-4 tweets  (Priority 7-8, peak hours)
Insights:      2-3 tweets  (Priority 6-7, off-peak)
Historical:    1-2 tweets  (Priority 5-6, morning)
Replies:       1-2 tweets  (Priority 4-5, peak only)
```

---

## Monitoring & Validation

### Key Metrics to Watch

1. **Daily Usage Tracking**
   ```bash
   # Check current usage
   grep "Usage tracking updated" /root/wirereport/logs/swarm.log | tail -1
   ```

2. **Posting Intervals**
   ```bash
   # Monitor actual posting times
   grep "Successfully posted" /root/wirereporthq/logs/hq_queue_processor.log
   ```

3. **Queue Intelligence**
   ```bash
   # Watch intelligent selection
   grep "Selected.*tweets for" /root/wirereport/logs/*.log
   ```

4. **Rate Limit Compliance**
   ```bash
   # Ensure daily limit respected
   grep "daily limit" /root/wirereport/logs/*.log
   ```

### Alert Conditions

- **Budget Exhausted Early**: If 17 tweets posted before 6 PM
- **No Posting Activity**: If no tweets for >3 hours during peak
- **Queue Overflow**: If queue size >50 items
- **Rate Limit Violations**: If hitting Twitter rate limits

---

## Rollback Procedure

If issues arise, you can revert to cron-based scheduling:

```bash
# 1. Stop swarm services
systemctl stop wirereport-swarm

# 2. Restore original crontab
crontab /root/wirereport/backups/crontab_backup_YYYYMMDD_HHMMSS.txt

# 3. Restart cron
systemctl restart cron

# 4. Verify restoration
crontab -l
```

---

## Benefits of Swarm Scheduling

1. **Budget Compliance**: Never exceeds 17 tweets/day
2. **Intelligent Distribution**: Spreads content across 24 hours
3. **Content Quality**: Prioritizes high-value content
4. **Adaptive Timing**: Adjusts to sports schedules and peak hours
5. **Error Recovery**: Handles failures gracefully
6. **Performance Monitoring**: Tracks success rates and optimization
7. **Duplicate Prevention**: Avoids similar content posting
8. **Context Awareness**: Considers recent posting history

---

## Next Steps

1. **Deploy Schedule Orchestrator**: Integrate with swarm master
2. **Run Migration Script**: Disable existing crons safely
3. **Monitor Initial Performance**: Watch first 24-hour cycle
4. **Tune Parameters**: Adjust intervals based on performance
5. **Validate Rate Limits**: Confirm 17-tweet compliance
6. **Optimize Content Mix**: Ensure diverse, engaging posts

This intelligent scheduling system ensures the Wire Report accounts operate efficiently within Twitter's free plan limits while maintaining high-quality, well-timed content distribution.

*Last Updated: August 2, 2025*