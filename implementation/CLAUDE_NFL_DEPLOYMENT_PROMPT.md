# Claude Prompt for NFL Server Deployment

**Send this prompt to Claude to deploy the NFL server update:**

---

I need to deploy the NFL server update. The NFL server (45.76.7.74) is currently a snapshot of the WNBA server and needs to be updated to work with @wirereportnfl instead of @wirereportwnba.

Please run this deployment script on the NFL server:

```bash
#!/bin/bash
# NFL Server Update Script - Run on 45.76.7.74
set -e

echo "🏈 Starting NFL Server Update..."

# Backup current configuration
BACKUP_DIR="/root/backups/pre_nfl_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r /root/wirereportwnba "$BACKUP_DIR/" 2>/dev/null || true

# 1. Update Twitter API credentials for @wirereportnfl
cat > /root/wirereportwnba/.env << 'EOF'
TWITTER_API_KEY=5CaGiqPltj2NkxscbrAabwUA3
TWITTER_API_SECRET=qkuwxXs6K1OvVYTkYeswDLGZj87QFgF6kXIajjfL2sHs1AqJ3J
TWITTER_ACCESS_TOKEN=1897655242386202624-KZHM840F4HGfdK1qFKQvGTjvbcXzHE
TWITTER_ACCESS_TOKEN_SECRET=iYHyKr6XhWtcSQlvXjO7UI3AliYFXdOhWKKEWEXOczFVb
TWITTER_HANDLE=@wirereportnfl
LEAGUE=NFL
BRAIN_SERVER_IP=216.128.150.51
BRAIN_SERVER_PORT=8080
QUEUE_ENDPOINT=/api/queues/nfl
ACK_ENDPOINT=/api/queues/nfl/ack
DAILY_TWEET_LIMIT=17
EOF

# 2. Update all configuration files
find /root/wirereportwnba -name "*.py" -type f -exec sed -i 's/@wirereportwnba/@wirereportnfl/g' {} \;
find /root/wirereportwnba -name "*.py" -type f -exec sed -i 's/wirereportwnba/wirereportnfl/g' {} \;

# 3. Update queue endpoints
if [ -f "/root/wirereportwnba/queue_processor.py" ]; then
    sed -i 's|/api/queues/wnba|/api/queues/nfl|g' /root/wirereportwnba/queue_processor.py
    sed -i 's|/api/queues/wnba/ack|/api/queues/nfl/ack|g' /root/wirereportwnba/queue_processor.py
fi

# 4. Update systemd services
find /etc/systemd/system -name "wirereport-*.service" -exec sed -i 's/wirereportwnba/wirereportnfl/g' {} \;

# 5. Test connection and restart services
systemctl daemon-reload
systemctl restart wirereport-queue 2>/dev/null || true

echo "✅ NFL Server Update Complete!"
echo "Testing NFL queue endpoint..."
curl -s "http://216.128.150.51:8080/api/queues/nfl" | head -n 5
```

**After running this script:**

1. The NFL server will be configured for @wirereportnfl
2. It will poll `/api/queues/nfl` from the brain server (216.128.150.51:8080)
3. All Twitter credentials will be updated for the NFL account
4. The queue processor will restart and begin pulling NFL tweets

**To verify deployment:**
- Check service status: `systemctl status wirereport-queue`
- Monitor logs: `journalctl -u wirereport-queue -f`
- Test queue polling: `curl http://216.128.150.51:8080/api/queues/nfl`

This completes the NFL deployment as the first league expansion for Wire Report.

---

## Current Status

✅ **Brain Server (216.128.150.51)**: 
- NFL enabled in league configuration
- API server supports `/api/queues/nfl` endpoint
- Swarm master configured with @wirereportnfl account
- NFL queue file created and ready

⏳ **NFL Server (45.76.7.74)**: 
- Needs deployment script above to update from WNBA clone
- After deployment will poll NFL queue every 30 seconds
- Will post to @wirereportnfl with 17 tweets/day limit

## Next Steps After NFL Deployment

1. **Verify Operation**: Monitor NFL server logs and queue activity
2. **Content Generation**: Swarm will begin generating NFL content automatically
3. **Future Leagues**: Use same pattern for MLB, NHL, MLS, CFB, CBB deployments
4. **Scale Management**: Each league operates independently with 17 tweet daily limits