# WireReport NBA-Proven System Workflow

## System Architecture After Optimization (37% Code Reduction)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                             ENTRY POINTS                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│   run_all_leagues.py ──────► league_orchestrator.py ◄────── Cron Jobs          │
│   (Main Controller)          (7-Step NBA Workflow)         (Scheduled)         │
│                                                                                 │
└────────────────────────────────────┬───────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        CONFIGURATION & TRENDING SYSTEM                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────┐                 ┌─────────────────────────────┐  │
│  │    CONFIGURATION        │                 │    TRENDING SYSTEM          │  │
│  ├─────────────────────────┤                 ├─────────────────────────────┤  │
│  │ • config.py (API Keys)  │                 │ • real_trending_fetcher.py  │  │
│  │ • enhanced_league_mgr   │                 │ • universal_trending_proc   │  │
│  │ • league_configs/*      │                 │ • Media Embedding           │  │
│  └─────────────────────────┘                 └─────────────────────────────┘  │
│                    │                                        │                   │
└────────────────────┴────────────────────────────────────────┴──────────────────┘
                                             │
                                             ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         CORE NBA-PROVEN WORKFLOW (7 Steps)                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐    ┌──────┐
│  │ Load │ ─► │Check │ ─► │Check │ ─► │Check │ ─► │Trend │ ─► │Fetch │ ─► │ Gen  │
│  │Config│    │Enable│    │Hours │    │Limits│    │Proc  │    │Data  │    │Tweet│
│  └──────┘    └──────┘    └──────┘    └──────┘    └──────┘    └──────┘    └──────┘
│     1           2           3           4           5           6           7   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                           │                                    │
                           ▼                                    ▼
         ┌─────────────────────────────────┐    ┌─────────────────────────────────┐
         │        DATA SOURCES             │    │         PROCESSING              │
         ├─────────────────────────────────┤    ├─────────────────────────────────┤
         │ • universal_data_fetcher.py     │    │ • universal_tweet_generator.py  │
         │ • RapidAPI (NBA/Sports)         │    │ • OpenAI GPT Integration        │
         │ • ESPN API (WNBA)               │    │ • League-Specific Prompts       │
         │ • Twitter API v2                │    │ • Rate Limiting & Validation    │
         └─────────────────────────────────┘    └─────────────────────────────────┘
                                                               │
                                                               ▼
                          ┌─────────────────────────────────────────────────────┐
                          │                    OUTPUT                            │
                          ├─────────────────────────────────────────────────────┤
                          │           • Direct Twitter Posting                   │
                          │           • OAuth 2.0 Authentication                 │
                          │           • @wirereporthq / League Accounts          │
                          └─────────────────────────────────────────────────────┘

## Key Features After Cleanup

┌─────────────────────────────────────────────────────────────────────────────────┐
│ ✓ Real Twitter Fetching  ✓ NBA Engagement Scoring  ✓ Media Embedding           │
│ ✓ Source Attribution     ✓ Multi-League Support    ✓ 24/7 Operation            │
└─────────────────────────────────────────────────────────────────────────────────┘

## Data Flow

1. **Entry** → User/Cron triggers `run_all_leagues.py`
2. **Orchestration** → Calls `league_orchestrator.py` for each enabled league
3. **Configuration** → Loads league-specific settings and API keys
4. **Validation** → Checks if league is enabled, within active hours, under limits
5. **Trending** → Fetches real tweets via RapidAPI, scores engagement (NBA algorithm)
6. **Data** → Fetches fresh sports data from APIs (games, scores, stats)
7. **Generation** → Creates tweets using OpenAI with league-specific prompts
8. **Posting** → Direct posting to Twitter via OAuth 2.0

## Simplified Architecture Benefits

- **37% fewer files** - Removed redundant fetchers/generators
- **No queue overhead** - Direct posting is more reliable
- **Single data flow** - One path for all leagues
- **Proven patterns** - Uses exact NBA system that works
- **Easy debugging** - Clear linear flow with logging

## Rate Limiting Strategy

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│ League Intervals │ ──► │ Twitter API      │ ──► │ Adaptive Delays  │
│ (2-5 minutes)    │     │ (300 posts/3hr)  │     │ (on 429 errors)  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```
```