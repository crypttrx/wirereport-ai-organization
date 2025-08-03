#!/usr/bin/env python3
"""
GitHub Repository Setup for WireReport AI Organization
Creates centralized repo for OpenAI/Claude collaboration
"""

import os
import sys
import asyncio
from cco_github_manager import ChiefCodeOfficer

async def setup_github_repository():
    """Complete setup of GitHub repository with CCO governance"""
    
    print("🏛️ WireReport AI Organization - GitHub Setup")
    print("=" * 60)
    
    # Check for required environment variables
    github_token = os.getenv('GITHUB_TOKEN')
    openai_key = os.getenv('OPENAI_API_KEY')
    
    if not github_token:
        print("❌ GITHUB_TOKEN environment variable required")
        print("   1. Go to GitHub Settings > Developer settings > Personal access tokens")
        print("   2. Create token with repo, admin:org permissions")
        print("   3. export GITHUB_TOKEN='your_token_here'")
        return False
    
    if not openai_key:
        print("⚠️ OPENAI_API_KEY not set - OpenAI consensus will be disabled")
    
    # Initialize CCO
    cco = ChiefCodeOfficer()
    
    # Get repository details
    print("\n📋 Repository Configuration:")
    org_name = input("GitHub Organization (leave empty for personal account): ").strip()
    if not org_name:
        org_name = None
    
    repo_name = input(f"Repository name [wirereport-ai-organization]: ").strip()
    if not repo_name:
        repo_name = "wirereport-ai-organization"
    
    cco.repo_name = repo_name
    
    print(f"\n🚀 Creating repository...")
    print(f"   Name: {repo_name}")
    print(f"   Organization: {org_name or 'Personal Account'}")
    
    # Create repository
    repo = await cco.create_github_repository(org_name)
    if not repo:
        print("❌ Failed to create repository")
        return False
    
    print(f"✅ Repository created: {repo.html_url}")
    
    # Set up local git remote
    print("\n🔗 Configuring local git remote...")
    try:
        import subprocess
        
        # Remove existing origin if exists
        try:
            subprocess.run(['git', 'remote', 'remove', 'origin'], 
                         cwd='/root/wirereport_organization', 
                         capture_output=True)
        except:
            pass
        
        # Add new origin
        github_url = repo.clone_url
        subprocess.run(['git', 'remote', 'add', 'origin', github_url],
                     cwd='/root/wirereport_organization', check=True)
        
        print("✅ Git remote configured")
        
    except Exception as e:
        print(f"⚠️ Git remote setup failed: {e}")
    
    # Initial sync to GitHub
    print("\n📤 Syncing to GitHub...")
    sync_success = await cco.sync_local_to_github()
    
    if sync_success:
        print("✅ Initial sync completed")
    else:
        print("⚠️ Sync failed - may need manual push")
    
    # Setup complete
    print("\n" + "=" * 60)
    print("🎉 GitHub Repository Setup Complete!")
    print("=" * 60)
    print(f"Repository: {repo.html_url}")
    print("\nNext steps:")
    print("1. Set up GitHub Actions for automated CCO reviews")
    print("2. Configure webhooks for real-time PR monitoring")
    print("3. Add team members with appropriate permissions")
    print("4. Test the CCO approval workflow")
    
    print("\nCCO Commands:")
    print("- Review PR: python cco_github_manager.py --review-pr <number>")
    print("- Sync files: python cco_github_manager.py --sync") 
    print("- Generate report: python cco_github_manager.py --report")
    
    return True

async def test_cco_workflow():
    """Test the CCO workflow with a sample change"""
    print("\n🧪 Testing CCO Workflow...")
    
    # Create a test branch and change
    import subprocess
    
    try:
        # Create test branch
        subprocess.run(['git', 'checkout', '-b', 'test/cco-workflow'], 
                     cwd='/root/wirereport_organization', check=True)
        
        # Make a test change
        test_file = '/root/wirereport_organization/test-change.md'
        with open(test_file, 'w') as f:
            f.write("""# Test CCO Workflow

This is a test change to validate the Chief Code Officer approval system.

## Change Details
- Type: Test executive-level change
- Authority Level: CCO approval required
- Consensus: OpenAI + Claude consensus required

This change should trigger the full CCO review process.
""")
        
        # Commit test change
        subprocess.run(['git', 'add', test_file], 
                     cwd='/root/wirereport_organization', check=True)
        subprocess.run(['git', 'commit', '-m', 'Test: CCO workflow validation'], 
                     cwd='/root/wirereport_organization', check=True)
        
        # Push test branch
        subprocess.run(['git', 'push', 'origin', 'test/cco-workflow'], 
                     cwd='/root/wirereport_organization', check=True)
        
        print("✅ Test branch created and pushed")
        print("   Branch: test/cco-workflow")
        print("   File: test-change.md")
        print("\nTo complete test:")
        print("1. Create PR from test/cco-workflow to main on GitHub")
        print("2. Run: python cco_github_manager.py --review-pr <PR_NUMBER>")
        print("3. Observe CCO approval process")
        
        # Return to main branch
        subprocess.run(['git', 'checkout', 'main'], 
                     cwd='/root/wirereport_organization', check=True)
        
    except Exception as e:
        print(f"❌ Test setup failed: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Setup GitHub repository for WireReport AI Organization')
    parser.add_argument('--test', action='store_true', help='Create test CCO workflow')
    
    args = parser.parse_args()
    
    if args.test:
        asyncio.run(test_cco_workflow())
    else:
        success = asyncio.run(setup_github_repository())
        if not success:
            sys.exit(1)