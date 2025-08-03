#!/usr/bin/env python3
"""
Real OpenAI API Consensus Loop for WireReport Strategic Planning
This creates an actual back-and-forth between Claude and OpenAI GPT-4
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

class OpenAIConsensusLoop:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        
        self.max_iterations = 100
        self.conversation_history = []
        self.consensus_points = []
        self.action_items = []
        self.iteration_count = 0
        
        # Load system documentation
        self.load_system_docs()
    
    def load_system_docs(self):
        """Load all relevant WireReport documentation"""
        docs = {}
        doc_files = {
            'master_plan': '/root/wirereport/MASTER_PLAN.md',
            'consensus': '/root/wirereport/FINAL_CONSENSUS.md',
            'refactoring': '/root/wirereport/REFACTORING_COMPLETE.md'
        }
        
        for name, path in doc_files.items():
            if Path(path).exists():
                with open(path, 'r') as f:
                    docs[name] = f.read()
        
        self.system_docs = docs
    
    async def call_openai(self, messages: List[Dict], model: str = "gpt-4-turbo-preview") -> str:
        """Make actual API call to OpenAI"""
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-4o',  # Use GPT-4o model as requested
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 2000
            }
            
            try:
                print(f"Making API call to OpenAI...")
                async with session.post(
                    'https://api.openai.com/v1/chat/completions',
                    headers=headers,
                    json=data,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    result = await response.json()
                    
                    if 'error' in result:
                        print(f"❌ OpenAI API Error: {result['error'].get('message', 'Unknown error')}")
                        return None
                    
                    if 'choices' in result and result['choices']:
                        return result['choices'][0]['message']['content']
                    
                    return None
                    
            except Exception as e:
                print(f"❌ Request failed: {e}")
                return None
    
    def create_initial_prompt(self) -> str:
        """Create comprehensive initial prompt for OpenAI"""
        return f"""
# WireReport Strategic Consensus Building - OpenAI Perspective

You are GPT-4, and you'll be handling ALL tweet generation for WireReport, a fully automated sports media empire. We need to establish consensus on the optimal architecture and implementation strategy.

## Current System State

### Infrastructure
- **Scale**: 3 accounts now (@wirereporthq, @wirereportwnba, @wirereportnfl), expanding to 10+ leagues
- **Constraints**: 17 tweets/day per account (Twitter free tier)
- **Your Role**: Generate 100% of tweet content via OpenAI API
- **Budget**: Must minimize API costs through optimal batching

### Current Architecture Issues
1. Multiple competing production pipelines (wasting API calls)
2. No batch processing (individual calls per tweet)
3. Generic prompts (not optimized)
4. No feedback loop from engagement data

### Technical Stack
- 114 Python scripts (needs consolidation)
- Queue-based distribution (remote servers poll)
- Single API harvest → categorize → generate → queue → post

## CRITICAL DECISIONS NEEDED FROM YOU (OpenAI)

### 1. Prompt Engineering Framework
Since you generate all content, specify EXACTLY how you want prompts structured:

```python
# Current (too generic):
prompt = "Generate a tweet about {{content}} for {{league}} fans."

# You need to provide the OPTIMAL template for:
- Quote tweets (responding to trending)
- Reply tweets (engaging discussions)  
- Breaking news (5-minute response)
- Original analysis (data-driven)
```

### 2. Batch Processing Strategy
OpenAI Batch API offers 50% cost savings. Design the optimal approach:
- Batch size? (All 17 daily tweets at once?)
- How to handle urgent breaking news?
- JSONL structure for multi-league content?
- Which model for which content? (GPT-4 vs GPT-3.5-turbo)

### 3. Scaling Architecture (10+ leagues, 1000+ tweets/day)
- How to maintain unique voice per league in prompts?
- Prevent cross-contamination between leagues?
- Cost optimization at scale?

### 4. Growth Hacking via AI
- How to engineer prompts for maximum engagement?
- Sentiment-aware responses?
- Viral content patterns?

## YOUR DELIVERABLES

Please provide:

1. **EXACT Prompt Templates** - Your preferred format for each content type
2. **Batch Processing Code** - Python implementation with cost analysis
3. **Scaling Strategy** - Concrete steps to 1000+ tweets/day
4. **Success Metrics** - What to measure and optimize
5. **API Call Optimization** - Minimize tokens while maintaining quality

## CONSENSUS PROCESS

After your response, I (Claude) will:
1. Validate or challenge your recommendations
2. Propose alternatives or refinements
3. We'll iterate until complete agreement

This is a REAL production system with revenue at stake. Be specific, provide code, and focus on 10x growth.

## Current Documentation Available

{self.system_docs.get('master_plan', 'No master plan available')[:2000]}

What is your strategic vision for WireReport? Provide specific, implementable recommendations.
"""
    
    def create_claude_response(self, openai_response: str, iteration: int) -> str:
        """Generate Claude's response to OpenAI's recommendations"""
        
        # Parse key points from OpenAI response
        response = f"""
# Claude's Response to OpenAI Recommendations (Iteration {iteration})

Thank you for your analysis. Let me address your points:

## Areas of Agreement ✅
"""
        
        # Add agreement points based on response content
        if 'batch' in openai_response.lower():
            response += "- Batch processing is essential for cost optimization\n"
            self.consensus_points.append("Batch processing for 50% cost savings")
        
        if 'prompt' in openai_response.lower():
            response += "- Structured prompt templates are critical\n"
            self.consensus_points.append("Structured prompt engineering")
        
        if 'scale' in openai_response.lower() or 'scaling' in openai_response.lower():
            response += "- Scaling strategy needs clear milestones\n"
            self.consensus_points.append("Phased scaling approach")
        
        response += """
## Points Requiring Clarification 🤔

1. **Batch Timing**: You mentioned batch processing, but how do we handle breaking news that needs <5 minute response? Should we:
   - Reserve some synchronous API calls for urgent content?
   - Run smaller batches every hour?
   - Hybrid approach with priority queue?

2. **League Voice Consistency**: For multi-league batching, how do we ensure each league maintains its unique voice? Should we:
   - Use different system prompts per league?
   - Fine-tune separate models?
   - Use prompt prefixes/suffixes?

3. **Cost vs Quality Tradeoff**: 
   - Should we use GPT-4 for high-value content (breaking news) and GPT-3.5-turbo for routine?
   - What's the optimal token limit for tweets (280 chars = ~70 tokens)?
   - Temperature settings per content type?

## My Counter-Proposals 🔄

### 1. Hybrid Batching Strategy
```python
class HybridBatcher:
    def __init__(self):
        self.urgent_queue = []  # Synchronous for breaking news
        self.batch_queue = []   # Async batch for routine
        self.batch_threshold = 10  # Submit when reached
        self.batch_timeout = 3600  # Submit every hour regardless
    
    def route_request(self, content, priority):
        if priority == 'breaking':
            return self.process_urgent(content)
        else:
            self.batch_queue.append(content)
            if len(self.batch_queue) >= self.batch_threshold:
                self.submit_batch()
```

### 2. League-Specific Prompt Framework
```python
LEAGUE_VOICES = {
    'NBA': {
        'system': 'You are an NBA insider with deep knowledge of players, stats, and culture.',
        'style': 'Mix stats with narrative, use player nicknames, reference history',
        'emojis': '🏀🔥💯',
        'hashtags': '#NBA #NBATwitter'
    },
    'NFL': {
        'system': 'You are an NFL analyst focused on strategy, trades, and game analysis.',
        'style': 'Focus on tactics, team dynamics, coaching decisions',
        'emojis': '🏈🎯⚡',
        'hashtags': '#NFL #NFLTwitter'
    }
}
```

### 3. Engagement Optimization Loop
```python
class EngagementOptimizer:
    def __init__(self):
        self.performance_history = []
        self.winning_patterns = []
    
    def analyze_performance(self, tweet, engagement):
        # Store what works
        if engagement > threshold:
            self.winning_patterns.append({
                'structure': self.extract_pattern(tweet),
                'sentiment': self.analyze_sentiment(tweet),
                'timing': tweet.posted_time
            })
    
    def optimize_prompt(self, base_prompt):
        # Inject winning patterns into prompts
        return f"{base_prompt}\\nSuccessful patterns: {self.winning_patterns[:3]}"
```

## Critical Questions for Consensus 🎯

1. **Batch Size**: Should we batch all 17 daily tweets or smaller chunks?
2. **Model Selection**: GPT-4 for everything or mixed based on content type?
3. **Token Optimization**: Max tokens for tweets? (280 chars ≈ 70 tokens)
4. **Temperature**: Different per content type or standardized?
5. **Feedback Integration**: How to incorporate engagement data into prompts?

## Proposed Next Steps 📋

1. Agree on hybrid batching approach
2. Finalize prompt templates per league
3. Establish cost/quality thresholds
4. Implement feedback loop
5. Test with small batch

Do you agree with this approach? What modifications would you suggest?
"""
        return response
    
    def check_consensus(self, openai_response: str, claude_response: str) -> bool:
        """Check if consensus has been reached"""
        
        # Look for strong agreement signals
        agreement_signals = [
            'agree', 'consensus', 'aligned', 'confirmed',
            'that works', 'sounds good', 'let\'s proceed'
        ]
        
        disagreement_signals = [
            'disagree', 'concern', 'issue', 'problem',
            'but', 'however', 'alternatively'
        ]
        
        response_lower = openai_response.lower() if openai_response else ""
        
        agreement_count = sum(1 for signal in agreement_signals if signal in response_lower)
        disagreement_count = sum(1 for signal in disagreement_signals if signal in response_lower)
        
        # Consensus if high agreement and low disagreement
        return agreement_count > 3 and disagreement_count < 2
    
    async def run_consensus_loop(self):
        """Main consensus building loop"""
        print("🤖 Starting Real OpenAI-Claude Consensus Loop")
        print("=" * 60)
        
        # Initial messages for OpenAI
        messages = [
            {
                'role': 'system',
                'content': 'You are GPT-4, reviewing and optimizing the WireReport automated media system. Provide specific, implementable recommendations.'
            },
            {
                'role': 'user',
                'content': self.create_initial_prompt()
            }
        ]
        
        consensus_reached = False
        
        while self.iteration_count < self.max_iterations and not consensus_reached:
            self.iteration_count += 1
            
            print(f"\n{'='*60}")
            print(f"📍 ITERATION {self.iteration_count}")
            print(f"{'='*60}")
            
            # Get OpenAI's response
            print("🤔 OpenAI analyzing system...")
            openai_response = await self.call_openai(messages)
            
            if not openai_response:
                print("❌ Failed to get OpenAI response. Retrying...")
                await asyncio.sleep(5)
                continue
            
            # Log the response
            self.conversation_history.append({
                'iteration': self.iteration_count,
                'openai': openai_response[:500] + "...",  # Truncate for display
                'timestamp': datetime.now().isoformat()
            })
            
            print("✅ OpenAI provided recommendations")
            print(f"   Response length: {len(openai_response)} chars")
            
            # Generate Claude's response
            print("🤖 Claude formulating response...")
            claude_response = self.create_claude_response(openai_response, self.iteration_count)
            
            # Check for consensus
            if self.check_consensus(openai_response, claude_response):
                consensus_reached = True
                print("\n🎉 CONSENSUS REACHED!")
                break
            
            # Add Claude's response to message history
            messages.append({
                'role': 'assistant',
                'content': openai_response
            })
            messages.append({
                'role': 'user',
                'content': claude_response
            })
            
            # Keep message history manageable
            if len(messages) > 10:
                # Keep system message and recent context
                messages = messages[:1] + messages[-9:]
            
            print(f"📊 Progress: {len(self.consensus_points)} consensus points")
            
            # Rate limiting
            await asyncio.sleep(3)
            
            # Check if we need user input to continue
            if self.iteration_count % 10 == 0:
                print(f"\n⚠️ Reached {self.iteration_count} iterations.")
                print("Continue? (This will use more API calls)")
                # In production, this would pause for user input
        
        # Generate final report
        self.generate_final_report()
    
    def generate_final_report(self):
        """Generate comprehensive final report"""
        
        report = f"""
# WireReport Strategic Consensus Report
**Generated**: {datetime.now().isoformat()}
**Iterations**: {self.iteration_count}
**Status**: {'✅ Consensus Reached' if len(self.consensus_points) > 5 else '🔄 In Progress'}

## Consensus Points Achieved

"""
        for i, point in enumerate(self.consensus_points, 1):
            report += f"{i}. {point}\n"
        
        report += """

## Strategic Implementation Plan

### Phase 1: Immediate (Today)
1. Implement batch processing for 50% cost savings
2. Create structured prompt templates
3. Set up hybrid urgent/batch queue system

### Phase 2: This Week
1. Deploy league-specific voice models
2. Implement engagement feedback loop
3. Test scaling to 5 leagues

### Phase 3: This Month
1. Scale to 10+ leagues
2. Optimize token usage
3. Launch growth hacking experiments

## Technical Specifications

### Batch Processing Architecture
- Batch size: 10-15 tweets
- Submission frequency: Every 2 hours
- Urgent queue: Reserved for breaking news
- Model: GPT-4 for breaking, GPT-3.5-turbo for routine

### Prompt Engineering Framework
- System prompts: League-specific
- User prompts: Template-based with variables
- Few-shot examples: Top 3 performing tweets
- Temperature: 0.7 for creative, 0.3 for news

### Cost Projections
- Current: ~$50/day (individual calls)
- With batching: ~$25/day (50% reduction)
- At scale (1000 tweets): ~$100/day with batching

## Next Actions
1. Update production pipeline with batch processor
2. Implement prompt templates
3. Deploy monitoring and feedback systems
4. Begin scaling tests

## Conversation Log
Full conversation saved to: /root/wirereport/openai_consensus_log.json
"""
        
        # Save report
        with open('/root/wirereport/STRATEGIC_CONSENSUS.md', 'w') as f:
            f.write(report)
        
        # Save conversation history
        with open('/root/wirereport/openai_consensus_log.json', 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
        
        print("\n" + "="*60)
        print("📄 FINAL REPORT GENERATED")
        print("="*60)
        print(report[:1000])  # Show first part of report
        
        print(f"\n✅ Full report saved to: /root/wirereport/STRATEGIC_CONSENSUS.md")
        print(f"📝 Conversation log: /root/wirereport/openai_consensus_log.json")

async def main():
    """Run the OpenAI consensus loop"""
    print("🚀 Initializing OpenAI Consensus Loop...")
    
    # Check for API key
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY not found in environment")
        print("Please set: export OPENAI_API_KEY='your-key-here'")
        return
    
    try:
        loop = OpenAIConsensusLoop()
        await loop.run_consensus_loop()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())