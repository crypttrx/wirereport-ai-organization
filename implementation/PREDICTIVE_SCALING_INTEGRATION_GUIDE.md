# 📈 Predictive Scaling Module Integration Guide

## Overview

The Predictive Scaling Module provides advanced ML-based predictive scaling capabilities for the Wire Report swarm architecture. It analyzes historical data, time patterns, and sports events to automatically scale agent pools for optimal performance while respecting resource constraints and Twitter API limits.

## Key Features

- **🔮 ML-Based Predictions**: ARIMA and exponential smoothing models for load forecasting
- **📅 Time Pattern Analysis**: Hourly, daily, and weekly scaling patterns
- **🏆 Sports Event Integration**: Game times, breaking news, and seasonal patterns
- **⚖️ Resource Constraint Enforcement**: Respects CPU (80%), Memory (70%) limits
- **🐦 API Limit Awareness**: Considers 17 tweets/day limit in scaling decisions
- **📊 Comprehensive Analytics**: Visualization and performance tracking
- **🔧 Manual Override Support**: Special event handling and emergency controls

## Quick Start

### 1. Basic Integration

```python
from agents.modules.predictive_scaling import (
    get_predictive_scaling_module,
    ResourceConstraints,
    integrate_with_orchestrator
)

# Define resource constraints
constraints = ResourceConstraints(
    max_cpu_percent=80.0,
    max_memory_percent=70.0,
    max_total_agents=150
)

# Initialize the module
scaling_module = await get_predictive_scaling_module(constraints=constraints)

# Integrate with existing orchestrator
await integrate_with_orchestrator(master_orchestrator, constraints)
```

### 2. Event-Driven Scaling

```python
from agents.modules.predictive_scaling import (
    handle_breaking_news,
    handle_game_start,
    EventType
)

# Handle breaking news
await handle_breaking_news("NBA", "trade")

# Handle game start
await handle_game_start("NFL", "playoff")

# Custom event scaling
await scaling_module.trigger_event_scaling(
    EventType.BREAKING_NEWS, 
    "WNBA", 
    multiplier=2.5, 
    duration_hours=3
)
```

### 3. Manual Overrides

```python
# Disable scaling for maintenance
scaling_module.add_manual_override("NBA", {
    "disable_scaling": True,
    "reason": "Maintenance window"
})

# Set minimum agents
scaling_module.add_manual_override("HQ", {
    "min_agents": 25,
    "max_agents": 45
})

# Remove override
scaling_module.remove_manual_override("NBA")
```

## Integration Points

### 1. Master Orchestrator Integration

```python
# In master_orchestrator.py
from agents.modules.predictive_scaling import integrate_with_orchestrator

class MasterOrchestrator:
    async def __init__(self):
        # ... existing initialization ...
        
        # Add predictive scaling
        self.scaling_module = await integrate_with_orchestrator(self)
        
        # Register callbacks
        self.scaling_module.register_callback(
            "scaling_executed", 
            self._handle_scaling_event
        )
    
    async def _handle_scaling_event(self, event_data):
        """Handle scaling events"""
        league = event_data['league']
        agents_change = event_data['event']['agents_after'] - event_data['event']['agents_before']
        
        logger.info(f"Scaling executed for {league}: {agents_change:+d} agents")
        
        # Update internal state
        self._update_agent_registry(league, event_data['event']['agents_after'])
```

### 2. Performance Monitor Integration

```python
# In performance_monitor.py
from agents.modules.predictive_scaling import integrate_with_performance_monitor

class AdvancedPerformanceMonitor:
    async def __init__(self):
        # ... existing initialization ...
        
        # Add predictive scaling integration
        self.scaling_module = await integrate_with_performance_monitor(self)
    
    async def _collect_metrics(self):
        # ... existing metric collection ...
        
        # Feed data to scaling module
        load_pattern = LoadPattern(
            timestamp=datetime.now(),
            league="system",
            # ... other metrics ...
        )
        self.scaling_module.load_history.append(load_pattern)
```

### 3. League Configuration Integration

```python
# In league_config_*.py files
PREDICTIVE_SCALING = {
    "enabled": True,
    "base_agents": 10,
    "max_agents": 30,
    "scaling_sensitivity": 0.7,
    "peak_hours": [18, 19, 20, 21, 22],
    "game_day_multiplier": 2.5,
    "breaking_news_multiplier": 3.0,
    "seasonal_pattern": {
        10: 1.0, 11: 1.2, 12: 1.3,  # Season progression
        # ... monthly multipliers ...
    }
}
```

## League-Specific Configurations

### NBA Configuration
```python
NBA_PROFILE = LeagueScalingProfile(
    league="NBA",
    category=LeagueCategory.MAJOR_LEAGUE,
    daily_tweet_limit=17,
    peak_hours=[18, 19, 20, 21, 22, 23],  # Evening games
    game_day_multiplier=2.5,
    breaking_news_multiplier=3.0,
    base_agents=15,
    max_agents=40,
    scaling_sensitivity=0.7
)
```

### WNBA Configuration
```python
WNBA_PROFILE = LeagueScalingProfile(
    league="WNBA",
    category=LeagueCategory.SECONDARY_LEAGUE,
    daily_tweet_limit=17,
    peak_hours=[15, 16, 17, 18, 19, 20],  # Afternoon games
    game_day_multiplier=2.0,
    breaking_news_multiplier=2.5,
    base_agents=8,
    max_agents=25,
    scaling_sensitivity=0.6
)
```

## Event Handling Patterns

### 1. Breaking News Detection

```python
async def handle_breaking_news_detection(news_data):
    """Handle detected breaking news"""
    league = determine_league(news_data)
    importance = assess_news_importance(news_data)
    
    if importance == "high":
        await handle_breaking_news(league, "major")
    elif importance == "medium":
        await scaling_module.trigger_event_scaling(
            EventType.BREAKING_NEWS, 
            league, 
            multiplier=2.0, 
            duration_hours=1
        )
```

### 2. Game Schedule Integration

```python
async def prepare_for_scheduled_games():
    """Prepare for upcoming games"""
    upcoming_games = get_games_next_2_hours()
    
    for game in upcoming_games:
        league = game['league']
        importance = game.get('importance', 'regular')
        
        # Pre-scale 30 minutes before game
        schedule_time = game['start_time'] - timedelta(minutes=30)
        
        asyncio.create_task(
            schedule_scaling_for_game(league, importance, schedule_time)
        )

async def schedule_scaling_for_game(league, importance, when):
    """Schedule scaling for a specific game"""
    wait_time = (when - datetime.now()).total_seconds()
    if wait_time > 0:
        await asyncio.sleep(wait_time)
    
    multiplier = 3.0 if importance == "playoff" else 2.0
    await handle_game_start(league, importance)
```

### 3. Seasonal Adjustments

```python
async def apply_seasonal_adjustments():
    """Apply seasonal scaling adjustments"""
    current_month = datetime.now().month
    
    for league, profile in scaling_module.league_profiles.items():
        seasonal_mult = profile.seasonal_pattern.get(current_month, 1.0)
        
        if seasonal_mult < 0.5:  # Off-season
            scaling_module.add_manual_override(league, {
                "max_agents": max(profile.base_agents, int(profile.max_agents * 0.6)),
                "reason": f"Off-season scaling for {league}"
            })
        elif seasonal_mult > 1.5:  # High season
            scaling_module.add_manual_override(league, {
                "min_agents": int(profile.base_agents * 1.2),
                "reason": f"High season scaling for {league}"
            })
```

## Monitoring and Analytics

### 1. Real-time Status Monitoring

```python
async def monitor_scaling_status():
    """Monitor scaling system status"""
    while True:
        status = scaling_module.get_scaling_status()
        
        # Log key metrics
        logger.info(f"Total agents: {status['total_agents']}")
        logger.info(f"Resource utilization: CPU {status['current_cpu']:.1f}%, Memory {status['current_memory']:.1f}%")
        
        # Check for issues
        if status['total_agents'] > status['max_total_agents'] * 0.9:
            logger.warning("Approaching maximum agent capacity")
        
        # Alert on failed scalings
        failed_scalings = [e for e in scaling_module.scaling_history 
                          if not e.success and (datetime.now() - e.timestamp).hours < 1]
        
        if len(failed_scalings) > 3:
            logger.error(f"Multiple scaling failures in last hour: {len(failed_scalings)}")
        
        await asyncio.sleep(300)  # Check every 5 minutes
```

### 2. Performance Reporting

```python
async def generate_daily_scaling_report():
    """Generate daily scaling performance report"""
    report = await scaling_module.generate_scaling_report()
    
    # Extract key metrics
    efficiency = report['system_overview']['scaling_efficiency_percent']
    total_events = report['system_overview']['total_scaling_events']
    
    logger.info(f"Daily Scaling Report:")
    logger.info(f"  Efficiency: {efficiency:.1f}%")
    logger.info(f"  Scaling Events: {total_events}")
    
    # Save detailed report
    timestamp = datetime.now().strftime("%Y%m%d")
    report_path = f"/root/wirereport/data/scaling_reports/daily_report_{timestamp}.json"
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2, default=str)
```

### 3. Visualization Dashboard

```python
async def create_scaling_dashboard():
    """Create real-time scaling dashboard"""
    # Generate visualization
    viz_path = await scaling_module.create_visualization(hours=24)
    
    # Get current status
    status = scaling_module.get_scaling_status()
    accuracy = scaling_module.get_prediction_accuracy()
    
    dashboard_data = {
        "timestamp": datetime.now().isoformat(),
        "status": status,
        "accuracy": accuracy,
        "visualization": str(viz_path),
        "alerts": get_scaling_alerts(),
        "recommendations": await scaling_module._generate_optimization_recommendations()
    }
    
    return dashboard_data
```

## Error Handling and Resilience

### 1. Graceful Degradation

```python
class ScalingErrorHandler:
    @staticmethod
    async def handle_prediction_failure(league, error):
        """Handle prediction model failures"""
        logger.error(f"Prediction failed for {league}: {error}")
        
        # Fall back to profile-based prediction
        profile = scaling_module.league_profiles[league]
        fallback_prediction = await scaling_module._profile_based_prediction(
            league, datetime.now()
        )
        
        return fallback_prediction
    
    @staticmethod
    async def handle_scaling_failure(league, error):
        """Handle agent scaling failures"""
        logger.error(f"Scaling failed for {league}: {error}")
        
        # Record failure
        failure_event = ScalingEvent(
            event_id=f"failure_{int(time.time())}",
            timestamp=datetime.now(),
            trigger=ScalingTrigger.EMERGENCY,
            direction=ScalingDirection.MAINTAIN,
            agents_before=scaling_module.current_agents.get(league, 0),
            agents_after=scaling_module.current_agents.get(league, 0),
            predicted_load=0,
            success=False,
            notes=f"Scaling failure: {error}"
        )
        
        scaling_module.scaling_history.append(failure_event)
        
        # Disable scaling temporarily
        scaling_module.add_manual_override(league, {
            "disable_scaling": True,
            "reason": f"Temporary disable due to failure: {error}",
            "expires_at": datetime.now() + timedelta(minutes=30)
        })
```

### 2. Resource Protection

```python
async def monitor_resource_constraints():
    """Monitor and enforce resource constraints"""
    current_cpu, current_memory = await scaling_module._get_current_resource_usage()
    
    # Emergency scale-down if resources critical
    if current_cpu > 90 or current_memory > 85:
        logger.critical("Critical resource usage - emergency scale-down")
        
        # Scale down all leagues proportionally
        for league in scaling_module.league_profiles.keys():
            current_agents = scaling_module.current_agents.get(league, 0)
            target_agents = max(1, int(current_agents * 0.7))  # 30% reduction
            
            emergency_prediction = ScalingPrediction(
                timestamp=datetime.now(),
                predicted_load=target_agents,
                confidence_interval=(target_agents, target_agents),
                recommended_agents=target_agents,
                current_agents=current_agents,
                scaling_direction=ScalingDirection.SCALE_DOWN,
                trigger_type=ScalingTrigger.EMERGENCY,
                reasoning="Emergency resource protection",
                resource_requirements={}
            )
            
            await scaling_module._perform_scaling(league, emergency_prediction)
```

## Best Practices

### 1. Configuration Management

- Store league profiles in configuration files
- Use environment variables for resource constraints
- Version control scaling configurations
- Test configuration changes in staging first

### 2. Monitoring and Alerting

- Set up alerts for scaling failures
- Monitor prediction accuracy regularly
- Track resource utilization trends
- Log all scaling decisions with reasoning

### 3. Performance Optimization

- Retrain models regularly with fresh data
- Adjust scaling sensitivity based on performance
- Cache predictions to reduce computation
- Use efficient data structures for historical data

### 4. Integration Testing

- Test scaling with mock orchestrator
- Validate resource constraint enforcement
- Verify API limit considerations
- Test error handling and recovery

## Production Deployment

### 1. Environment Setup

```bash
# Install dependencies
pip install numpy pandas scikit-learn matplotlib seaborn statsmodels

# Set environment variables
export SCALING_ENABLED=true
export MAX_CPU_PERCENT=80
export MAX_MEMORY_PERCENT=70
export MAX_TOTAL_AGENTS=200
```

### 2. Service Configuration

```ini
# /etc/systemd/system/wirereport-scaling.service
[Unit]
Description=Wire Report Predictive Scaling Service
After=network.target

[Service]
Type=simple
User=wirereport
WorkingDirectory=/root/wirereport
ExecStart=/usr/bin/python3 -m agents.modules.predictive_scaling
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 3. Health Checks

```python
async def health_check():
    """Scaling system health check"""
    try:
        status = scaling_module.get_scaling_status()
        
        checks = {
            "system_running": status['running'],
            "prediction_cache_healthy": status['prediction_cache_size'] > 0,
            "recent_scaling_events": len(scaling_module.scaling_history) > 0,
            "model_accuracy": scaling_module.get_prediction_accuracy().get('accuracy_percentage', 0) > 50
        }
        
        health_score = sum(checks.values()) / len(checks) * 100
        
        return {
            "status": "healthy" if health_score > 75 else "degraded" if health_score > 50 else "unhealthy",
            "score": health_score,
            "checks": checks
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
```

## Troubleshooting

### Common Issues

1. **High Resource Usage**: Check agent spawn rate and implement cooling periods
2. **Poor Prediction Accuracy**: Retrain models with more recent data
3. **Scaling Lag**: Reduce prediction interval or increase sensitivity
4. **API Limit Breaches**: Adjust agent-to-tweet ratios per league

### Debug Commands

```python
# Check system status
status = scaling_module.get_scaling_status()

# View recent scaling events
events = list(scaling_module.scaling_history)[-10:]

# Check prediction accuracy
accuracy = scaling_module.get_prediction_accuracy()

# Export debug data
debug_path = await scaling_module.export_scaling_data()
```

## Conclusion

The Predictive Scaling Module provides powerful, intelligent scaling capabilities that adapt to sports schedules, breaking news, and resource constraints. By following this integration guide, you can implement proactive scaling that optimizes performance while respecting system limits and API constraints.

For support or questions, review the demo script at `/root/wirereport/demo_predictive_scaling.py` or check the module source code for detailed implementation examples.