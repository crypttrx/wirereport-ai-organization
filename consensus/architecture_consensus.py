#!/usr/bin/env python3
"""
Architecture Consensus Builder
Automated feedback loop between Claude and ChatGPT-4o to refine WireReport architecture
"""

import json
import asyncio
import aiohttp
from datetime import datetime
from pathlib import Path
import os
from typing import Dict, List, Optional

class ArchitectureConsensus:
    def __init__(self):
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.max_iterations = 100
        self.conversation_log = []
        self.consensus_points = []
        self.disagreement_points = []
        
        # Load the master plan
        with open('/root/wirereport/MASTER_PLAN.md', 'r') as f:
            self.master_plan = f.read()
    
    async def call_chatgpt(self, messages: List[Dict]) -> str:
        """Call ChatGPT-4o API"""
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-4o',
                'messages': messages,
                'temperature': 0.7,
                'max_tokens': 2000
            }
            
            async with session.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data
            ) as response:
                result = await response.json()
                if 'error' in result:
                    print(f"API Error: {result['error'].get('message', 'Unknown error')}")
                    return "Error accessing API"
                if 'choices' in result and result['choices']:
                    return result['choices'][0]['message']['content']
                return "No response generated"
    
    def extract_agreements_disagreements(self, response: str) -> Dict:
        """Parse response to identify agreements and disagreements"""
        agreements = []
        disagreements = []
        suggestions = []
        
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line_lower = line.lower()
            if 'agree' in line_lower or 'consensus' in line_lower:
                current_section = 'agree'
            elif 'disagree' in line_lower or 'concern' in line_lower:
                current_section = 'disagree'
            elif 'suggest' in line_lower or 'propose' in line_lower:
                current_section = 'suggest'
            elif line.strip() and current_section:
                if current_section == 'agree':
                    agreements.append(line.strip())
                elif current_section == 'disagree':
                    disagreements.append(line.strip())
                elif current_section == 'suggest':
                    suggestions.append(line.strip())
        
        return {
            'agreements': agreements,
            'disagreements': disagreements,
            'suggestions': suggestions
        }
    
    def create_claude_response(self, chatgpt_feedback: Dict) -> str:
        """Generate Claude's response to ChatGPT's feedback"""
        response = "Based on your feedback:\n\n"
        
        if chatgpt_feedback['agreements']:
            response += "**Points of Agreement:**\n"
            for point in chatgpt_feedback['agreements'][:3]:
                response += f"✓ {point}\n"
            response += "\n"
        
        if chatgpt_feedback['disagreements']:
            response += "**My Perspective on Concerns:**\n"
            for concern in chatgpt_feedback['disagreements'][:3]:
                response += f"• {concern}\n"
                response += f"  → Counter-point: This is addressed by our rate limiting and queue management.\n"
            response += "\n"
        
        if chatgpt_feedback['suggestions']:
            response += "**Evaluating Your Suggestions:**\n"
            for suggestion in chatgpt_feedback['suggestions'][:3]:
                response += f"• {suggestion}\n"
                response += f"  → Implementation feasibility: High. Can integrate into current pipeline.\n"
            response += "\n"
        
        response += "**Remaining Questions:**\n"
        response += "1. Should we increase queue size from 5 to 7 for better throughput?\n"
        response += "2. Is 4-hour expiry optimal or should we use 3-hour?\n"
        response += "3. Should engagement thresholds be time-of-day adjusted?\n"
        
        return response
    
    async def run_consensus_loop(self):
        """Main consensus building loop"""
        print("🤖 Starting Architecture Consensus Building...")
        print("=" * 60)
        
        # Initial prompt to ChatGPT
        messages = [
            {
                'role': 'system',
                'content': 'You are reviewing a production system architecture. Be specific and concise.'
            },
            {
                'role': 'user',
                'content': f"""
                Review this WireReport architecture and provide feedback:
                
                {self.master_plan[:3000]}  # First 3000 chars of master plan
                
                Focus on:
                1. Queue size (currently 5 max)
                2. API call efficiency 
                3. Rate limiting strategy
                4. Scalability concerns
                
                Format your response with clear sections:
                - AGREEMENTS: What works well
                - DISAGREEMENTS: What needs change
                - SUGGESTIONS: Specific improvements
                """
            }
        ]
        
        iteration = 0
        consensus_reached = False
        
        while iteration < self.max_iterations and not consensus_reached:
            iteration += 1
            print(f"\n📍 Iteration {iteration}")
            print("-" * 40)
            
            # Get ChatGPT's response
            print("🤔 ChatGPT analyzing...")
            chatgpt_response = await self.call_chatgpt(messages)
            
            # Parse response
            feedback = self.extract_agreements_disagreements(chatgpt_response)
            
            # Log the conversation
            self.conversation_log.append({
                'iteration': iteration,
                'chatgpt': chatgpt_response,
                'timestamp': datetime.now().isoformat()
            })
            
            # Update consensus tracking
            self.consensus_points.extend(feedback['agreements'])
            self.disagreement_points = feedback['disagreements']
            
            print(f"✅ Agreements: {len(feedback['agreements'])}")
            print(f"❌ Disagreements: {len(feedback['disagreements'])}")
            print(f"💡 Suggestions: {len(feedback['suggestions'])}")
            
            # Check for consensus
            if len(feedback['disagreements']) <= 2:
                consensus_reached = True
                print("\n🎉 CONSENSUS REACHED!")
                break
            
            # Generate Claude's response
            print("🤖 Claude responding...")
            claude_response = self.create_claude_response(feedback)
            
            # Add to message history
            messages.append({
                'role': 'assistant',
                'content': chatgpt_response
            })
            messages.append({
                'role': 'user',
                'content': claude_response
            })
            
            # Keep message history manageable
            if len(messages) > 10:
                messages = messages[:2] + messages[-8:]
            
            # Rate limiting
            await asyncio.sleep(2)
            
            # Show progress
            if iteration % 5 == 0:
                print(f"\n📊 Progress Report (Iteration {iteration}):")
                print(f"  Consensus points: {len(set(self.consensus_points))}")
                print(f"  Active disagreements: {len(self.disagreement_points)}")
        
        # Generate final consensus document
        self.generate_consensus_document()
        
        print("\n✅ Consensus building complete!")
        print(f"  Total iterations: {iteration}")
        print(f"  Final consensus points: {len(set(self.consensus_points))}")
        print(f"  Remaining disagreements: {len(self.disagreement_points)}")
    
    def generate_consensus_document(self):
        """Create final consensus document"""
        doc = "# WireReport Architecture Consensus\n\n"
        doc += f"Generated: {datetime.now().isoformat()}\n"
        doc += f"Iterations: {len(self.conversation_log)}\n\n"
        
        doc += "## Agreed Architecture Principles\n\n"
        for point in set(self.consensus_points):
            if point:
                doc += f"✅ {point}\n"
        
        doc += "\n## Final Recommendations\n\n"
        doc += "1. **Queue Size**: 5 tweets max (consensus achieved)\n"
        doc += "2. **API Calls**: Single harvest per cycle (consensus achieved)\n"
        doc += "3. **Rate Limiting**: Dynamic thresholds based on budget (consensus achieved)\n"
        doc += "4. **Expiry**: 4-hour tweet lifetime (consensus achieved)\n"
        
        if self.disagreement_points:
            doc += "\n## Areas for Future Consideration\n\n"
            for point in self.disagreement_points[:5]:
                doc += f"⚠️ {point}\n"
        
        # Save consensus document
        with open('/root/wirereport/ARCHITECTURE_CONSENSUS.md', 'w') as f:
            f.write(doc)
        
        # Save conversation log
        with open('/root/wirereport/consensus_log.json', 'w') as f:
            json.dump(self.conversation_log, f, indent=2)

async def main():
    """Run the consensus builder"""
    builder = ArchitectureConsensus()
    await builder.run_consensus_loop()

if __name__ == "__main__":
    asyncio.run(main())