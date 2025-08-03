#!/usr/bin/env python3
"""
CCO Webhook Server for GitHub Integration
Automatically reviews PRs when created/updated
"""

import json
import asyncio
from datetime import datetime
from flask import Flask, request, jsonify
import hmac
import hashlib
import os
from cco_github_manager import ChiefCodeOfficer

app = Flask(__name__)

# Configuration
WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', 'cco-webhook-secret-2025')
CCO_PORT = int(os.getenv('CCO_WEBHOOK_PORT', '8090'))

# Initialize CCO
cco = ChiefCodeOfficer()

def verify_signature(payload_body, secret_token, signature_header):
    """Verify GitHub webhook signature"""
    if not signature_header:
        return False
    
    hash_object = hmac.new(
        secret_token.encode('utf-8'),
        msg=payload_body,
        digestmod=hashlib.sha256
    )
    expected_signature = "sha256=" + hash_object.hexdigest()
    
    return hmac.compare_digest(expected_signature, signature_header)

@app.route('/cco/webhook', methods=['POST'])
def handle_github_webhook():
    """Handle GitHub webhook events for CCO review"""
    
    # Verify signature
    signature = request.headers.get('X-Hub-Signature-256')
    if not verify_signature(request.data, WEBHOOK_SECRET, signature):
        return jsonify({'error': 'Invalid signature'}), 403
    
    # Parse event
    event_type = request.headers.get('X-GitHub-Event')
    payload = request.json
    
    print(f"📨 GitHub webhook: {event_type}")
    
    # Handle pull request events
    if event_type == 'pull_request':
        return handle_pull_request_event(payload)
    
    # Handle push events to main (for sync validation)
    elif event_type == 'push':
        return handle_push_event(payload)
    
    return jsonify({'message': 'Event not handled'}), 200

def handle_pull_request_event(payload):
    """Handle pull request webhook events"""
    
    action = payload.get('action')
    pr = payload.get('pull_request', {})
    pr_number = pr.get('number')
    
    print(f"   PR #{pr_number}: {action}")
    
    # Actions that trigger CCO review
    review_actions = ['opened', 'synchronize', 'ready_for_review']
    
    if action in review_actions:
        # Trigger CCO review asynchronously
        asyncio.create_task(trigger_cco_review(pr_number, action))
        
        return jsonify({
            'message': f'CCO review triggered for PR #{pr_number}',
            'action': action
        }), 200
    
    return jsonify({'message': f'No action needed for {action}'}), 200

def handle_push_event(payload):
    """Handle push events to main branch"""
    
    ref = payload.get('ref')
    
    if ref == 'refs/heads/main':
        commits = payload.get('commits', [])
        print(f"   📤 {len(commits)} commits pushed to main")
        
        # Log executive changes
        for commit in commits:
            message = commit.get('message', '')
            if any(keyword in message.lower() for keyword in ['executive', 'governance', 'board', 'ceo', 'cfo', 'cto']):
                print(f"   🏛️ Executive change detected: {message[:50]}...")
        
        return jsonify({'message': 'Push event logged'}), 200
    
    return jsonify({'message': 'Non-main branch push ignored'}), 200

async def trigger_cco_review(pr_number: int, action: str):
    """Trigger CCO review process"""
    
    try:
        print(f"🤖 Starting CCO review for PR #{pr_number}")
        
        # Perform CCO review
        result = await cco.review_pull_request(pr_number)
        
        if 'error' in result:
            print(f"❌ CCO review failed: {result['error']}")
        else:
            approved = result.get('cco_decision', {}).get('approved', False)
            status = "✅ APPROVED" if approved else "❌ REJECTED"
            print(f"   {status}: PR #{pr_number}")
            
            # Log the decision
            log_cco_decision(pr_number, result)
    
    except Exception as e:
        print(f"❌ CCO review error: {e}")

def log_cco_decision(pr_number: int, result: dict):
    """Log CCO decision to file"""
    
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'pr_number': pr_number,
        'decision': result.get('cco_decision', {}),
        'executive_level': result.get('executive_level'),
        'consensus_achieved': result.get('cco_decision', {}).get('consensus_achieved', False)
    }
    
    # Append to log file
    log_file = '/root/wirereport_organization/logs/cco_decisions.jsonl'
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

@app.route('/cco/status', methods=['GET'])
def get_cco_status():
    """Get CCO system status"""
    
    # Count recent decisions
    log_file = '/root/wirereport_organization/logs/cco_decisions.jsonl'
    recent_decisions = 0
    
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                recent_decisions = sum(1 for line in f)
    except:
        pass
    
    status = {
        'cco_active': True,
        'webhook_port': CCO_PORT,
        'recent_decisions': recent_decisions,
        'openai_configured': bool(os.getenv('OPENAI_API_KEY')),
        'github_configured': bool(os.getenv('GITHUB_TOKEN')),
        'timestamp': datetime.now().isoformat()
    }
    
    return jsonify(status)

@app.route('/cco/decisions', methods=['GET'])
def get_recent_decisions():
    """Get recent CCO decisions"""
    
    log_file = '/root/wirereport_organization/logs/cco_decisions.jsonl'
    decisions = []
    
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                lines = f.readlines()
                # Get last 20 decisions
                for line in lines[-20:]:
                    decisions.append(json.loads(line.strip()))
    except Exception as e:
        return jsonify({'error': f'Failed to read decisions: {e}'}), 500
    
    return jsonify({
        'decisions': decisions,
        'count': len(decisions)
    })

@app.route('/cco/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'CCO Webhook Server',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("🏛️ Starting CCO Webhook Server")
    print(f"   Port: {CCO_PORT}")
    print(f"   Webhook URL: http://localhost:{CCO_PORT}/cco/webhook")
    print(f"   Status URL: http://localhost:{CCO_PORT}/cco/status")
    print(f"   Health URL: http://localhost:{CCO_PORT}/cco/health")
    
    app.run(host='0.0.0.0', port=CCO_PORT, debug=False)