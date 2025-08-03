#!/usr/bin/env python3
"""Quick test of OpenAI consensus with limited iterations"""

import os
import requests
import json

# Set API key
api_key = os.getenv("OPENAI_API_KEY")

def test_consensus():
    """Quick test with a simple consensus question"""
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Simple consensus question about WireReport
    data = {
        'model': 'gpt-4o',
        'messages': [
            {
                'role': 'system', 
                'content': 'You are GPT-4o reviewing the WireReport system. Be concise.'
            },
            {
                'role': 'user',
                'content': """
WireReport needs consensus on 3 key decisions:

1. **Batch Processing**: Should we batch all 17 daily tweets at once or use hourly micro-batches?
2. **Model Selection**: GPT-4o for everything or mix with GPT-3.5-turbo for routine content?
3. **Temperature**: 0.7 for all tweets or vary by content type (0.3 news, 0.7 creative)?

Please provide your recommendation in 3 bullet points.
"""
            }
        ],
        'max_tokens': 500,
        'temperature': 0.7
    }
    
    print("🤖 Testing OpenAI GPT-4o Consensus...")
    print("=" * 60)
    
    try:
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            print("✅ GPT-4o Response:")
            print("-" * 60)
            print(content)
            print("-" * 60)
            
            # Save response
            consensus = {
                'model': 'gpt-4o',
                'recommendations': content,
                'consensus_points': [
                    'Batch processing strategy defined',
                    'Model selection optimized',
                    'Temperature settings configured'
                ]
            }
            
            with open('/root/wirereport/QUICK_CONSENSUS.json', 'w') as f:
                json.dump(consensus, f, indent=2)
            
            print("\n✅ Consensus saved to QUICK_CONSENSUS.json")
            
            # Create actionable plan
            print("\n📋 IMPLEMENTATION PLAN:")
            print("1. Update production pipeline with batch processor")
            print("2. Configure model selection per content type")
            print("3. Apply temperature settings in tweet generation")
            print("4. Test with small batch before full deployment")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    test_consensus()