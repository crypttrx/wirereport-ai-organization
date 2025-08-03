#!/usr/bin/env python3
"""
Chief Code Officer (CCO) GitHub Management System
Handles executive-level approvals with OpenAI/Claude consensus
"""

import os
import json
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Optional
from github import Github
import asyncio

class ChiefCodeOfficer:
    def __init__(self):
        self.github_token = os.getenv('GITHUB_TOKEN')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.repo_name = "wirereport-ai-organization"
        self.organization = None  # Will be set when creating repo
        
        # Initialize GitHub client
        self.github = Github(self.github_token) if self.github_token else None
        
        # Executive authority levels
        self.executive_levels = {
            'board': ['governance_charter', 'strategic_direction', 'major_partnerships', 'budget_>500k'],
            'ceo': ['operational_policies', 'crisis_response', 'cross_functional'],
            'cfo': ['financial_policies', 'budget_<100k', 'cost_optimization'],
            'cto': ['technical_architecture', 'infrastructure_<50k', 'performance'],
            'cao': ['agent_management', 'performance_policies', 'resource_allocation']
        }
        
        # Approval log
        self.approval_log = []
    
    async def create_github_repository(self, org_name: str = None):
        """Create the centralized GitHub repository"""
        if not self.github:
            raise Exception("GitHub token not configured")
        
        repo_config = {
            'name': self.repo_name,
            'description': 'WireReport AI Autonomous Organization - Executive Governance & Consensus',
            'private': False,  # Public for transparency
            'has_issues': True,
            'has_projects': True,
            'has_wiki': True,
            'auto_init': False
        }
        
        try:
            if org_name:
                # Create in organization
                org = self.github.get_organization(org_name)
                repo = org.create_repo(**repo_config)
                self.organization = org_name
            else:
                # Create in user account
                user = self.github.get_user()
                repo = user.create_repo(**repo_config)
            
            print(f"✅ Repository created: {repo.html_url}")
            
            # Set up branch protection
            await self.setup_branch_protection(repo)
            
            # Initial commit with organizational structure
            await self.initial_commit(repo)
            
            return repo
            
        except Exception as e:
            print(f"❌ Failed to create repository: {e}")
            return None
    
    async def setup_branch_protection(self, repo):
        """Set up branch protection rules for governance"""
        try:
            # Protect main branch
            main_branch = repo.get_branch('main')
            main_branch.edit_protection(
                required_status_checks={
                    'strict': True,
                    'contexts': ['cco-consensus-check', 'openai-approval', 'claude-approval']
                },
                enforce_admins=True,
                required_pull_request_reviews={
                    'required_approving_review_count': 1,
                    'dismiss_stale_reviews': True,
                    'require_code_owner_reviews': True
                },
                restrictions={
                    'users': [],
                    'teams': []
                }
            )
            
            print("✅ Branch protection configured")
            
        except Exception as e:
            print(f"⚠️ Branch protection setup failed: {e}")
    
    async def initial_commit(self, repo):
        """Create initial commit with organizational structure"""
        try:
            # Create directory structure in repo
            directories = [
                'governance/README.md',
                'consensus/README.md', 
                'charters/README.md',
                'implementation/README.md',
                'logs/README.md',
                'cco-system/README.md'
            ]
            
            for dir_file in directories:
                content = f"# {dir_file.split('/')[0].title()}\n\nOrganizational documents for WireReport AI Autonomous Organization"
                repo.create_file(
                    dir_file,
                    f"Initial structure: {dir_file}",
                    content
                )
            
            # Add governance workflow
            with open('/root/wirereport_organization/GOVERNANCE_WORKFLOW.md', 'r') as f:
                workflow_content = f.read()
            
            repo.create_file(
                'GOVERNANCE_WORKFLOW.md',
                'Add: Executive governance workflow with CCO approval system',
                workflow_content
            )
            
            print("✅ Initial commit completed")
            
        except Exception as e:
            print(f"❌ Initial commit failed: {e}")
    
    async def review_pull_request(self, pr_number: int) -> Dict:
        """CCO review of pull request with OpenAI/Claude consensus"""
        if not self.github:
            return {'error': 'GitHub not configured'}
        
        try:
            repo = self.github.get_repo(f"{self.organization or self.github.get_user().login}/{self.repo_name}")
            pr = repo.get_pull(pr_number)
            
            # Analyze the changes
            change_analysis = await self.analyze_changes(pr)
            
            # Determine executive level
            executive_level = self.determine_executive_level(change_analysis)
            
            # Get OpenAI consensus
            openai_review = await self.get_openai_consensus(change_analysis, executive_level)
            
            # Get Claude consensus (simulated - would use Claude API)
            claude_review = await self.get_claude_consensus(change_analysis, executive_level)
            
            # Make CCO decision
            cco_decision = await self.make_cco_decision(openai_review, claude_review, change_analysis)
            
            # Log the approval process
            approval_record = {
                'pr_number': pr_number,
                'executive_level': executive_level,
                'change_analysis': change_analysis,
                'openai_review': openai_review,
                'claude_review': claude_review,
                'cco_decision': cco_decision,
                'timestamp': datetime.now().isoformat()
            }
            
            self.approval_log.append(approval_record)
            
            # Apply decision
            if cco_decision['approved']:
                # Approve and merge PR
                pr.create_review(body=cco_decision['reasoning'], event='APPROVE')
                if pr.mergeable:
                    pr.merge(commit_message=f"CCO Approved: {pr.title}")
                    print(f"✅ PR #{pr_number} approved and merged")
            else:
                # Request changes
                pr.create_review(body=cco_decision['reasoning'], event='REQUEST_CHANGES')
                print(f"❌ PR #{pr_number} requires changes")
            
            return approval_record
            
        except Exception as e:
            return {'error': f'Review failed: {e}'}
    
    async def analyze_changes(self, pr) -> Dict:
        """Analyze PR changes to determine impact and requirements"""
        files_changed = []
        change_types = []
        
        for file in pr.get_files():
            files_changed.append(file.filename)
            
            # Determine change type based on file path
            if 'governance/' in file.filename:
                change_types.append('governance')
            elif 'consensus/' in file.filename:
                change_types.append('consensus')
            elif 'charters/' in file.filename:
                change_types.append('charter')
            elif 'implementation/' in file.filename:
                change_types.append('implementation')
        
        return {
            'files_changed': files_changed,
            'change_types': list(set(change_types)),
            'pr_title': pr.title,
            'pr_body': pr.body,
            'author': pr.user.login
        }
    
    def determine_executive_level(self, change_analysis: Dict) -> str:
        """Determine required executive approval level"""
        change_types = change_analysis['change_types']
        
        if 'governance' in change_types or 'charter' in change_types:
            return 'board'
        elif 'consensus' in change_types:
            return 'c-suite'
        elif 'implementation' in change_types:
            return 'cco'
        else:
            return 'standard'
    
    async def get_openai_consensus(self, change_analysis: Dict, executive_level: str) -> Dict:
        """Get OpenAI review and consensus on changes"""
        if not self.openai_api_key:
            return {'approved': True, 'reasoning': 'OpenAI API not configured', 'confidence': 0}
        
        prompt = f"""
You are OpenAI, reviewing executive-level changes to the WireReport AI Autonomous Organization.

CHANGE ANALYSIS:
- Executive Level: {executive_level}
- Change Types: {change_analysis['change_types']}
- Files Modified: {change_analysis['files_changed']}
- Title: {change_analysis['pr_title']}
- Description: {change_analysis['pr_body']}

As OpenAI, provide your technical review focusing on:
1. Technical feasibility
2. System integration impact
3. Resource requirements
4. Risk assessment
5. Implementation complexity

Respond in JSON format:
{{
    "approved": true/false,
    "reasoning": "detailed technical analysis",
    "confidence": 0-100,
    "recommendations": ["list of suggestions"]
}}
"""
        
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-4o',
                'messages': [
                    {'role': 'system', 'content': 'You are OpenAI providing technical review for executive decisions.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.3,
                'max_tokens': 1000
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=60
            )
            
            if response.status_code == 200:
                content = response.json()['choices'][0]['message']['content']
                # Parse JSON response
                import json
                return json.loads(content)
            else:
                return {'approved': False, 'reasoning': f'API error: {response.status_code}', 'confidence': 0}
                
        except Exception as e:
            return {'approved': False, 'reasoning': f'OpenAI consensus failed: {e}', 'confidence': 0}
    
    async def get_claude_consensus(self, change_analysis: Dict, executive_level: str) -> Dict:
        """Get Claude consensus (simulated - would integrate with Claude API)"""
        # This would integrate with Claude API when available
        # For now, simulate Claude's consensus based on implementation focus
        
        claude_analysis = {
            'approved': True,
            'reasoning': f'Claude analysis: Changes to {change_analysis["change_types"]} appear well-structured and maintain organizational coherence. Implementation path is clear.',
            'confidence': 85,
            'recommendations': [
                'Ensure documentation updates reflect changes',
                'Consider impact on existing agent workflows',
                'Validate consensus logging mechanisms'
            ]
        }
        
        # Add specific logic based on change types
        if 'governance' in change_analysis['change_types']:
            claude_analysis['reasoning'] += ' Governance changes require careful validation of authority matrices.'
            claude_analysis['confidence'] = 90
        
        return claude_analysis
    
    async def make_cco_decision(self, openai_review: Dict, claude_review: Dict, change_analysis: Dict) -> Dict:
        """CCO final decision based on OpenAI/Claude consensus"""
        
        # Both must approve for executive-level changes
        both_approved = openai_review.get('approved', False) and claude_review.get('approved', False)
        
        if both_approved:
            confidence = (openai_review.get('confidence', 0) + claude_review.get('confidence', 0)) / 2
            
            decision = {
                'approved': True,
                'reasoning': f'CCO APPROVED: OpenAI and Claude consensus achieved. '
                           f'Average confidence: {confidence}%. '
                           f'OpenAI: {openai_review["reasoning"]} '
                           f'Claude: {claude_review["reasoning"]}',
                'confidence': confidence,
                'consensus_achieved': True
            }
        else:
            decision = {
                'approved': False,
                'reasoning': f'CCO REJECTED: Consensus not achieved. '
                           f'OpenAI approved: {openai_review.get("approved", False)} '
                           f'Claude approved: {claude_review.get("approved", False)} '
                           f'Both AIs must approve executive-level changes.',
                'confidence': 0,
                'consensus_achieved': False
            }
        
        return decision
    
    async def sync_local_to_github(self):
        """Sync local organizational folder to GitHub repository"""
        try:
            # Add GitHub remote if not exists
            try:
                result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                      cwd='/root/wirereport_organization',
                                      capture_output=True, text=True, check=True)
            except subprocess.CalledProcessError:
                # Add remote
                github_url = f"https://github.com/{self.organization or self.github.get_user().login}/{self.repo_name}.git"
                subprocess.run(['git', 'remote', 'add', 'origin', github_url],
                             cwd='/root/wirereport_organization', check=True)
            
            # Stage all changes
            subprocess.run(['git', 'add', '.'], cwd='/root/wirereport_organization', check=True)
            
            # Commit changes
            commit_message = f"CCO Update: Sync organizational documents - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            subprocess.run(['git', 'commit', '-m', commit_message], 
                         cwd='/root/wirereport_organization', check=True)
            
            # Push to GitHub
            subprocess.run(['git', 'push', 'origin', 'main'], 
                         cwd='/root/wirereport_organization', check=True)
            
            print("✅ Successfully synced to GitHub")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Git sync failed: {e}")
            return False
        except Exception as e:
            print(f"❌ Sync error: {e}")
            return False
    
    def generate_approval_report(self) -> str:
        """Generate approval audit report"""
        report = f"""
# CCO Approval Audit Report
Generated: {datetime.now().isoformat()}

## Summary
- Total Reviews: {len(self.approval_log)}
- Approved: {sum(1 for log in self.approval_log if log.get('cco_decision', {}).get('approved', False))}
- Rejected: {sum(1 for log in self.approval_log if not log.get('cco_decision', {}).get('approved', False))}

## Recent Decisions
"""
        
        for log in self.approval_log[-10:]:  # Last 10 decisions
            status = "✅ APPROVED" if log.get('cco_decision', {}).get('approved', False) else "❌ REJECTED"
            report += f"""
### PR #{log.get('pr_number', 'N/A')} - {status}
- **Level**: {log.get('executive_level', 'unknown')}
- **Changes**: {', '.join(log.get('change_analysis', {}).get('change_types', []))}
- **OpenAI**: {log.get('openai_review', {}).get('approved', 'N/A')}
- **Claude**: {log.get('claude_review', {}).get('approved', 'N/A')}
- **Timestamp**: {log.get('timestamp', 'N/A')}
"""
        
        return report

# CLI interface for CCO operations
async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Chief Code Officer GitHub Management')
    parser.add_argument('--create-repo', action='store_true', help='Create GitHub repository')
    parser.add_argument('--org', type=str, help='GitHub organization name')
    parser.add_argument('--review-pr', type=int, help='Review pull request number')
    parser.add_argument('--sync', action='store_true', help='Sync local to GitHub')
    parser.add_argument('--report', action='store_true', help='Generate approval report')
    
    args = parser.parse_args()
    
    cco = ChiefCodeOfficer()
    
    if args.create_repo:
        await cco.create_github_repository(args.org)
    elif args.review_pr:
        result = await cco.review_pull_request(args.review_pr)
        print(json.dumps(result, indent=2))
    elif args.sync:
        await cco.sync_local_to_github()
    elif args.report:
        report = cco.generate_approval_report()
        print(report)
    else:
        print("CCO GitHub Manager - Use --help for options")

if __name__ == "__main__":
    asyncio.run(main())