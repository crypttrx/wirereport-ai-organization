# WireReport Architecture Simplification Plan
## Based on Successful NBAWireReport System

### 🎯 **CORE PRINCIPLE**
Extract the **proven simplicity** from NBAWireReport and apply it league-agnostically while maintaining the **exact same logic flow** that makes @wirereportnba successful.

---

## 📊 **SUCCESSFUL NBA SYSTEM ANALYSIS**

### **Core Workflow (PROVEN)**
```
1. nba_data_fetcher.py → Fetches live NBA data via RapidAPI
2. fetch_cached_tweets.py → Gets trending tweets from Twitter handles
3. nba_tweet_generator.py → Processes content with OpenAI + filters
4. tweet_poster.py → Posts to @wirereportnba
5. breaking_news_pipeline.py → Handles urgent content
```

### **Key Success Factors**
- ✅ **Time-based execution**: Only runs during game hours (12:00-02:00 ET)
- ✅ **Rate limit awareness**: Checks API limits before posting
- ✅ **Engagement thresholds**: Age-based filtering (5min/15min/30min/60min/1440min)
- ✅ **Content quality**: OpenAI validation with specific prompts
- ✅ **League-specific handles**: NBA teams, reporters, league accounts
- ✅ **Direct posting**: No complex queue systems

---

## 🔧 **IMPLEMENTATION PLAN**

### **Phase 1: Core Script Standardization**
Extract these **exact patterns** from NBAWireReport:

#### **1. League-Agnostic Data Fetcher**
```python
# /root/wirereport/scripts/league_data_fetcher.py (NEW)
# Based on: /root/NBAWireReport/scripts/nba_data_fetcher.py

def fetch_league_data(league_config):
    """
    Fetches data for any league using config-specified:
    - API endpoints (RapidAPI NBA, ESPN, etc.)
    - Data structure mappings
    - Team/player mappings
    """
```

#### **2. Universal Tweet Generator**
```python
# /root/wirereport/scripts/universal_tweet_generator.py (NEW)
# Based on: /root/NBAWireReport/scripts/nba_tweet_generator.py

def generate_tweets_for_league(league_id):
    """
    Uses league config to:
    - Load league-specific time weights
    - Apply league-specific prompts
    - Use league-specific handles
    - Follow league-specific posting schedule
    """
```

#### **3. Standardized Tweet Poster**
```python
# Already exists but needs NBA logic integration
# /root/wirereport/scripts/tweet_poster.py (ENHANCE)
# Apply exact logic from: /root/NBAWireReport/scripts/tweet_poster.py
```

### **Phase 2: Configuration-Driven Differentiation**

#### **League Configuration Structure** (Apply NBA pattern)
```python
# /root/wirereport/config/league_configs/league_config_nba.py
LEAGUE_CONFIG = {
    # Exact NBA system patterns
    "league": "NBA",
    "active_hours": [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 0, 1, 2],
    "engagement_thresholds": [
        {"max_age": 5, "favorite_count": 15, "retweet_count": 5},
        {"max_age": 15, "favorite_count": 50, "retweet_count": 15},
        {"max_age": 30, "favorite_count": 100, "retweet_count": 40},
        {"max_age": 60, "favorite_count": 200, "retweet_count": 75},
        {"max_age": 1440, "favorite_count": 500, "retweet_count": 200}
    ],
    "twitter_handles": {
        "teams": ["Lakers", "Warriors", "Celtics", "Bucks", ...],
        "reporters": ["MarcJSpears", "BenGolliver", "sam_amick", ...],
        "league_official": ["NBA", "NBAPR", "nbastats"]
    },
    "openai_prompt": "You are writing tweets for @WireReportNBA...",
    "posting_endpoint": "http://localhost:8000/post",
    "rate_limits": {"tweets_per_hour": 20, "daily_limit": 100}
}
```

### **Phase 3: Workflow Standardization**

#### **Master Orchestrator Script**
```python
# /root/wirereport/scripts/league_orchestrator.py (NEW)

def run_league_cycle(league_id):
    """
    Runs the EXACT NBA workflow for any league:
    1. Check if in active hours for this league
    2. Fetch league data
    3. Get cached tweets from league handles  
    4. Generate content with league-specific prompts
    5. Post using league-specific endpoints
    6. Log results
    """
```

---

## 🔄 **MIGRATION STRATEGY**

### **Step 1: Extract NBA Logic** ✅
- Copy exact functions from working NBA scripts
- Preserve all timing, filtering, and posting logic
- Maintain identical error handling

### **Step 2: Parameterize by League**
- Replace hardcoded "NBA" with config["league"]
- Replace hardcoded handles with config["twitter_handles"]
- Replace hardcoded prompts with config["openai_prompt"]

### **Step 3: Test Consistency**
- Run NBA config through new system
- Verify identical behavior to original
- Ensure @wirereportnba maintains same quality

### **Step 4: Scale to Other Leagues**
- Apply same logic with different configs
- WNBA gets WNBA-specific handles/prompts/timing
- NFL gets NFL-specific configuration
- All maintain the same proven workflow

---

## 🎯 **SUCCESS METRICS**

### **Consistency Validation**
- [ ] NBA tweets maintain same style/quality
- [ ] Posting frequency matches original system
- [ ] Engagement patterns remain consistent
- [ ] No degradation in content quality

### **Scalability Validation**
- [ ] WNBA uses same logic with different config
- [ ] NFL config ready for deployment
- [ ] Each league maintains distinct voice
- [ ] Central logic remains unchanged

---

## 🚀 **IMMEDIATE NEXT STEPS**

1. **Extract Core NBA Functions**
   - Copy proven logic from nba_tweet_generator.py
   - Copy exact filtering from breaking_news_pipeline.py
   - Copy posting logic from tweet_poster.py

2. **Create Universal Scripts**
   - league_data_fetcher.py (config-driven)
   - universal_tweet_generator.py (config-driven)
   - league_orchestrator.py (master workflow)

3. **Enhance League Configs**
   - Add NBA-proven patterns to all league configs
   - Ensure each league has complete configuration
   - Maintain exact NBA thresholds for NBA config

4. **Test and Validate**
   - Run NBA through new system
   - Compare output quality
   - Ensure posting frequency matches

**GOAL**: Keep the **exact logic** that makes @wirereportnba successful, but make it **league-configurable** so every league (WNBA, NFL, etc.) benefits from the same proven workflow.