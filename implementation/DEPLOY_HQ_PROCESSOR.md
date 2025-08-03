
# HQ Queue Processor Deployment Instructions for Claude

To deploy the HQ Queue Processor on the brain server:

1. First, add the deployment endpoint to the existing API server by adding this to `/root/wirereport_api/wnba_api_server.py`:

```python
# Add after other imports
import base64
import tarfile
import subprocess
from pathlib import Path

# Add these endpoints to your existing FastAPI app

@app.post("/api/deploy/package")
async def deploy_package(request: Request):
    """Receive and deploy a package"""
    
    try:
        data = await request.json()
        
        # Create upload directory
        upload_dir = Path("/root/wirereport_api/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Decode and save package
        package_content = base64.b64decode(data['content_base64'])
        package_path = upload_dir / data['filename']
        
        with open(package_path, 'wb') as f:
            f.write(package_content)
            
        # Extract package
        extract_dir = upload_dir / f"extract_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        extract_dir.mkdir(exist_ok=True)
        
        with tarfile.open(package_path, 'r:gz') as tar:
            tar.extractall(extract_dir)
            
        # Run deployment
        deploy_script = extract_dir / "setup.sh"
        result = subprocess.run(
            ["/bin/bash", str(deploy_script)],
            capture_output=True,
            text=True,
            cwd=str(extract_dir)
        )
        
        if result.returncode == 0:
            return {
                "status": "success",
                "message": f"Package deployed successfully",
                "stdout": result.stdout
            }
        else:
            return {
                "status": "error",
                "message": f"Deployment failed",
                "stderr": result.stderr
            }
            
    except Exception as e:
        return {"status": "error", "message": str(e)}
```

2. Restart the API service to load the new endpoint:
```bash
systemctl restart wirereport-wnba-api
```

3. Run the deployment script from this server:
```bash
python3 /root/wirereport/deploy_hq_processor.py
```

This will:
- Send the package to the brain server API
- Extract and install the HQ queue processor
- Set up the systemd service
- Start processing tweets from the HQ queue

The processor will:
- Poll `/root/wirereport_api/data/queues/hq_queue.json` every 30 seconds
- Post tweets directly to @wirereporthq using local OAuth
- Track processed tweets to avoid duplicates
- Log all activity to `/root/wirereporthq/logs/hq_queue_processor.log`
