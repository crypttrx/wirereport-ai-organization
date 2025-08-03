#\!/bin/bash
# Set up environment and run consensus loop

# Find and export OpenAI API key
export OPENAI_API_KEY="$OPENAI_API_KEY"

# Run the consensus loop
cd /root/wirereport
python3 openai_consensus_loop.py
