# Wire Report Comprehensive Update Plan

## Executive Summary

This document provides a detailed update plan for the Wire Report system based on a comprehensive code review. The system shows excellent architectural design but requires immediate attention to security vulnerabilities and scalability improvements.

## Critical Issues Summary

### 🔴 **CRITICAL SECURITY VULNERABILITIES**
- Hardcoded API credentials (Twitter, OpenAI, RapidAPI)
- API keys exposed in logs
- Weak authentication mechanisms
- Sensitive data in plaintext files

### 🟠 **HIGH PRIORITY ISSUES**
- Performance bottlenecks in synchronous operations
- Single-threaded architecture limiting scalability
- Tight coupling between modules
- Missing error validation for external APIs

### 🟡 **MEDIUM PRIORITY ISSUES**
- File-based state management causing race conditions
- Inconsistent error handling patterns
- Missing integration tests
- Redundant demonstration code in production

## Phase 1: Immediate Security Remediation (Week 1)

### Day 1-2: Secure Credential Management

#### 1.1 Remove Hardcoded Credentials
```bash
# Create secure environment configuration
cat > /root/wirereport/.env.template << 'EOF'
# Twitter OAuth 2.0
TWITTER_CLIENT_ID=
TWITTER_CLIENT_SECRET=
TWITTER_CONSUMER_KEY=
TWITTER_CONSUMER_SECRET=
TWITTER_ACCESS_TOKEN=
TWITTER_ACCESS_TOKEN_SECRET=

# OpenAI
OPENAI_API_KEY=

# RapidAPI
RAPIDAPI_KEY=

# Telegram
TELEGRAM_BOT_TOKEN=

# Brain API
BRAIN_API_SECRET_KEY=
EOF
```

#### 1.2 Update Configuration Module
```python
# /root/wirereport/config/secure_config.py
import os
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import json
from pathlib import Path

class SecureConfig:
    """Secure configuration management with encryption."""
    
    def __init__(self):
        load_dotenv()
        self._encryption_key = self._get_or_create_key()
        self._cipher = Fernet(self._encryption_key)
        
    def _get_or_create_key(self):
        """Get or create encryption key."""
        key_path = Path.home() / '.wirereport' / 'secret.key'
        key_path.parent.mkdir(exist_ok=True)
        
        if key_path.exists():
            return key_path.read_bytes()
        else:
            key = Fernet.generate_key()
            key_path.write_bytes(key)
            os.chmod(key_path, 0o600)
            return key
    
    def get_twitter_config(self):
        """Get Twitter configuration securely."""
        return {
            'client_id': os.getenv('TWITTER_CLIENT_ID'),
            'client_secret': os.getenv('TWITTER_CLIENT_SECRET'),
            'consumer_key': os.getenv('TWITTER_CONSUMER_KEY'),
            'consumer_secret': os.getenv('TWITTER_CONSUMER_SECRET'),
            'access_token': self._decrypt_if_needed(
                os.getenv('TWITTER_ACCESS_TOKEN')
            ),
            'access_token_secret': self._decrypt_if_needed(
                os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
            )
        }
    
    def get_openai_key(self):
        """Get OpenAI API key."""
        return os.getenv('OPENAI_API_KEY')
    
    def _decrypt_if_needed(self, value):
        """Decrypt value if it's encrypted."""
        if value and value.startswith('gAAAAA'):  # Fernet encrypted
            try:
                return self._cipher.decrypt(value.encode()).decode()
            except:
                return value
        return value
```

#### 1.3 Secure Logging Configuration
```python
# /root/wirereport/utils/secure_logging.py
import logging
import re
from typing import Any

class SecureFormatter(logging.Formatter):
    """Formatter that masks sensitive data."""
    
    # Patterns to mask
    SENSITIVE_PATTERNS = [
        (r'(api[_-]?key|token|secret|password)\s*[=:]\s*["\']?([^"\'\s]+)',
         r'\1=***REDACTED***'),
        (r'sk-[a-zA-Z0-9]{48}', 'sk-***REDACTED***'),
        (r'Bearer\s+[a-zA-Z0-9\-._~+/]+', 'Bearer ***REDACTED***'),
    ]
    
    def format(self, record):
        msg = super().format(record)
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            msg = re.sub(pattern, replacement, msg, flags=re.IGNORECASE)
        return msg

def setup_secure_logging():
    """Configure secure logging for the application."""
    handler = logging.StreamHandler()
    handler.setFormatter(SecureFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logging.root.handlers = [handler]
    logging.root.setLevel(logging.INFO)
```

### Day 3-4: API Authentication Enhancement

#### 1.4 Implement Proper API Authentication
```python
# /root/wirereport/auth/api_auth.py
import jwt
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify

class APIAuth:
    """Enhanced API authentication system."""
    
    def __init__(self, secret_key=None):
        self.secret_key = secret_key or secrets.token_urlsafe(64)
        self.tokens = {}  # In production, use Redis
        
    def generate_token(self, server_id: str, expiry_hours: int = 24):
        """Generate JWT token for server."""
        payload = {
            'server_id': server_id,
            'exp': datetime.utcnow() + timedelta(hours=expiry_hours),
            'iat': datetime.utcnow(),
            'jti': secrets.token_urlsafe(16)
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        self.tokens[server_id] = {
            'token': token,
            'jti': payload['jti'],
            'expires': payload['exp']
        }
        
        return token
    
    def verify_token(self, token: str):
        """Verify JWT token."""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=['HS256']
            )
            
            # Check if token is revoked
            server_id = payload['server_id']
            if server_id in self.tokens:
                stored = self.tokens[server_id]
                if stored['jti'] != payload['jti']:
                    return None, "Token revoked"
                    
            return payload, None
            
        except jwt.ExpiredSignatureError:
            return None, "Token expired"
        except jwt.InvalidTokenError:
            return None, "Invalid token"
    
    def require_auth(self, f):
        """Decorator for protected endpoints."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({'error': 'No authorization header'}), 401
                
            try:
                token = auth_header.split(' ')[1]  # Bearer <token>
                payload, error = self.verify_token(token)
                
                if error:
                    return jsonify({'error': error}), 401
                    
                request.auth_payload = payload
                return f(*args, **kwargs)
                
            except Exception as e:
                return jsonify({'error': 'Authentication failed'}), 401
                
        return decorated_function
```

### Day 5: Security Audit Script

#### 1.5 Create Security Audit Tool
```bash
#!/bin/bash
# /root/wirereport/scripts/security_audit.sh

echo "=== Wire Report Security Audit ==="

# Check for hardcoded secrets
echo "Checking for hardcoded secrets..."
grep -r -i -E "(api[_-]?key|token|secret|password)\s*=\s*[\"'][^\"']+[\"']" \
    --include="*.py" \
    --exclude-dir=".git" \
    --exclude-dir="__pycache__" \
    /root/wirereport/ 2>/dev/null | \
    grep -v "example\|template\|test" | \
    wc -l

# Check file permissions
echo "Checking file permissions..."
find /root/wirereport -type f -name "*.json" -o -name "*.env" | \
    xargs ls -la | grep -E "^-rw-rw-|^-rw-r--r--"

# Check for sensitive data in logs
echo "Checking logs for sensitive data..."
grep -r -E "sk-[a-zA-Z0-9]{48}|Bearer\s+[a-zA-Z0-9]+" \
    /root/wirereport/logs/ 2>/dev/null | wc -l

echo "=== Audit Complete ==="
```

## Phase 2: Performance & Scalability (Week 2-3)

### 2.1 Async Architecture Improvements

#### Convert Synchronous Operations
```python
# /root/wirereport/agents/async_swarm_master.py
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Any

class AsyncSwarmMaster:
    """Asynchronous swarm master with proper concurrency."""
    
    def __init__(self):
        self.session = None
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.semaphore = asyncio.Semaphore(50)  # Limit concurrent operations
        
    async def initialize(self):
        """Initialize async resources."""
        self.session = aiohttp.ClientSession(
            connector=aiohttp.TCPConnector(limit=100)
        )
        
    async def process_sports_parallel(self, sports: List[str]):
        """Process multiple sports in parallel."""
        tasks = []
        
        for sport in sports:
            task = self._process_sport_with_limit(sport)
            tasks.append(task)
            
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle results and exceptions
        for sport, result in zip(sports, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process {sport}: {result}")
            else:
                await self._handle_sport_result(sport, result)
                
    async def _process_sport_with_limit(self, sport: str):
        """Process sport with concurrency limit."""
        async with self.semaphore:
            return await self._process_sport(sport)
            
    async def _process_sport(self, sport: str):
        """Process individual sport asynchronously."""
        # Fetch data
        data = await self._fetch_sport_data(sport)
        
        # Generate content in parallel
        content_tasks = [
            self._generate_content(item, sport) 
            for item in data[:5]  # Limit items
        ]
        
        contents = await asyncio.gather(*content_tasks)
        
        return {
            'sport': sport,
            'contents': contents,
            'timestamp': datetime.now()
        }
```

### 2.2 Implement Redis-Based Queue System

#### Replace File-Based Queues
```python
# /root/wirereport/queues/redis_queue.py
import redis
import json
import asyncio
from typing import Dict, List, Any, Optional
import aioredis

class RedisQueueManager:
    """Redis-based queue system for scalability."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = None
        
    async def initialize(self):
        """Initialize Redis connection."""
        self.redis = await aioredis.create_redis_pool(self.redis_url)
        
    async def enqueue(self, queue_name: str, item: Dict[str, Any]):
        """Add item to queue."""
        serialized = json.dumps(item)
        await self.redis.lpush(f"queue:{queue_name}", serialized)
        
        # Publish notification
        await self.redis.publish(f"queue:{queue_name}:new", "1")
        
    async def dequeue(self, queue_name: str, timeout: int = 0) -> Optional[Dict[str, Any]]:
        """Get item from queue with optional blocking."""
        if timeout:
            result = await self.redis.brpop(f"queue:{queue_name}", timeout=timeout)
        else:
            result = await self.redis.rpop(f"queue:{queue_name}")
            
        if result:
            _, data = result if timeout else (None, result)
            return json.loads(data)
        return None
        
    async def get_queue_size(self, queue_name: str) -> int:
        """Get current queue size."""
        return await self.redis.llen(f"queue:{queue_name}")
        
    async def acknowledge(self, queue_name: str, item_id: str):
        """Acknowledge processed item."""
        await self.redis.setex(
            f"ack:{queue_name}:{item_id}",
            3600,  # 1 hour TTL
            "1"
        )
        
    async def is_acknowledged(self, queue_name: str, item_id: str) -> bool:
        """Check if item was acknowledged."""
        return await self.redis.exists(f"ack:{queue_name}:{item_id}")
```

### 2.3 Horizontal Scaling Architecture

#### Implement Distributed Swarm
```python
# /root/wirereport/distributed/swarm_coordinator.py
import asyncio
from typing import List, Dict, Any
import consul
import socket

class DistributedSwarmCoordinator:
    """Coordinator for distributed swarm instances."""
    
    def __init__(self, consul_host: str = "localhost"):
        self.consul = consul.Consul(host=consul_host)
        self.instance_id = f"swarm-{socket.gethostname()}-{os.getpid()}"
        self.is_leader = False
        
    async def register_instance(self):
        """Register this swarm instance."""
        self.consul.agent.service.register(
            name="wirereport-swarm",
            service_id=self.instance_id,
            port=9999,
            check=consul.Check.tcp("localhost", 9999, "10s")
        )
        
    async def elect_leader(self):
        """Participate in leader election."""
        session_id = self.consul.session.create(
            lock_delay=10,
            ttl=30
        )
        
        lock_key = "wirereport/swarm/leader"
        
        # Try to acquire leader lock
        acquired = self.consul.kv.put(
            lock_key,
            self.instance_id,
            acquire=session_id
        )
        
        self.is_leader = acquired
        
        if self.is_leader:
            logger.info(f"Instance {self.instance_id} elected as leader")
            
    async def distribute_work(self, tasks: List[Dict[str, Any]]):
        """Distribute work across swarm instances."""
        instances = self._get_healthy_instances()
        
        # Partition tasks
        partitions = self._partition_tasks(tasks, len(instances))
        
        # Assign to instances
        for instance, partition in zip(instances, partitions):
            await self._assign_tasks_to_instance(instance, partition)
            
    def _get_healthy_instances(self) -> List[str]:
        """Get list of healthy swarm instances."""
        _, services = self.consul.health.service("wirereport-swarm", passing=True)
        return [s['Service']['ID'] for s in services]
```

## Phase 3: Code Quality & Testing (Week 3-4)

### 3.1 Comprehensive Testing Framework

#### Unit Test Structure
```python
# /root/wirereport/tests/test_swarm_master.py
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from agents.swarm_master_runner import SwarmMasterRunner

class TestSwarmMaster:
    """Comprehensive tests for swarm master."""
    
    @pytest.fixture
    async def swarm_master(self):
        """Create test swarm master instance."""
        master = SwarmMasterRunner()
        await master.initialize_enhancements()
        yield master
        await master.cleanup()
        
    @pytest.mark.asyncio
    async def test_parallel_sport_processing(self, swarm_master):
        """Test parallel processing of multiple sports."""
        sports = ['NBA', 'NFL', 'MLB']
        
        with patch.object(swarm_master, '_fetch_sport_data') as mock_fetch:
            mock_fetch.return_value = {'games': []}
            
            start_time = asyncio.get_event_loop().time()
            await swarm_master.process_sports_parallel(sports)
            duration = asyncio.get_event_loop().time() - start_time
            
            # Should process in parallel, not sequential
            assert duration < 1.0  # Assuming each would take 0.5s
            assert mock_fetch.call_count == len(sports)
            
    @pytest.mark.asyncio
    async def test_error_recovery(self, swarm_master):
        """Test error recovery mechanisms."""
        with patch.object(swarm_master, '_fetch_sport_data') as mock_fetch:
            mock_fetch.side_effect = Exception("API Error")
            
            # Should not crash
            await swarm_master.process_sports_parallel(['NBA'])
            
            # Should trigger self-healing
            assert swarm_master.self_healing.get_failure_count('NBA') > 0
```

#### Integration Tests
```python
# /root/wirereport/tests/integration/test_full_pipeline.py
import pytest
from testcontainers.redis import RedisContainer
from testcontainers.postgres import PostgresContainer

class TestFullPipeline:
    """Integration tests for complete pipeline."""
    
    @pytest.fixture(scope="class")
    def redis_container(self):
        """Spin up Redis container for testing."""
        with RedisContainer() as redis:
            yield redis
            
    @pytest.fixture(scope="class")
    def postgres_container(self):
        """Spin up Postgres container for testing."""
        with PostgresContainer("postgres:13") as postgres:
            yield postgres
            
    @pytest.mark.integration
    async def test_end_to_end_content_generation(self, redis_container, postgres_container):
        """Test complete content generation pipeline."""
        # Setup
        redis_url = redis_container.get_connection_url()
        postgres_url = postgres_container.get_connection_url()
        
        # Initialize system
        swarm = await create_test_swarm(redis_url, postgres_url)
        
        # Simulate game event
        game_event = {
            'type': 'score_update',
            'game_id': 'test_123',
            'home_score': 100,
            'away_score': 98,
            'time_remaining': '0:05'
        }
        
        # Process through pipeline
        result = await swarm.process_game_event(game_event)
        
        # Verify
        assert result['tweet_generated']
        assert 'close game' in result['content'].lower()
        assert result['significance_score'] > 0.8
```

### 3.2 Error Handling Standardization

#### Create Error Handler Module
```python
# /root/wirereport/utils/error_handler.py
import logging
import traceback
from typing import Callable, Any, Optional
from functools import wraps
import asyncio

class WireReportError(Exception):
    """Base exception for Wire Report."""
    pass

class APIError(WireReportError):
    """API related errors."""
    pass

class QueueError(WireReportError):
    """Queue processing errors."""
    pass

class ContentGenerationError(WireReportError):
    """Content generation errors."""
    pass

def handle_errors(
    default_return: Any = None,
    log_errors: bool = True,
    reraise: bool = False,
    error_types: tuple = (Exception,)
):
    """Decorator for consistent error handling."""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except error_types as e:
                if log_errors:
                    logger.error(
                        f"Error in {func.__name__}: {str(e)}",
                        exc_info=True,
                        extra={
                            'function': func.__name__,
                            'args': str(args)[:200],
                            'error_type': type(e).__name__
                        }
                    )
                if reraise:
                    raise
                return default_return
                
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except error_types as e:
                if log_errors:
                    logger.error(
                        f"Error in {func.__name__}: {str(e)}",
                        exc_info=True
                    )
                if reraise:
                    raise
                return default_return
                
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

class ErrorReporter:
    """Centralized error reporting system."""
    
    def __init__(self):
        self.error_counts = defaultdict(int)
        self.error_callbacks = []
        
    def report_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        severity: str = "ERROR"
    ):
        """Report error with context."""
        error_type = type(error).__name__
        self.error_counts[error_type] += 1
        
        error_data = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'message': str(error),
            'severity': severity,
            'context': context,
            'traceback': traceback.format_exc()
        }
        
        # Log error
        logger.error(f"Error reported: {error_type}", extra=error_data)
        
        # Trigger callbacks
        for callback in self.error_callbacks:
            try:
                callback(error_data)
            except Exception as e:
                logger.error(f"Error in error callback: {e}")
                
    def add_callback(self, callback: Callable):
        """Add error notification callback."""
        self.error_callbacks.append(callback)
```

## Phase 4: Architecture Improvements (Week 4-5)

### 4.1 Event-Driven Architecture

#### Implement Event Bus
```python
# /root/wirereport/events/event_bus.py
import asyncio
from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class Event:
    """Base event class."""
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime = None
    source: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
            
    def to_json(self) -> str:
        """Serialize event to JSON."""
        return json.dumps({
            'event_type': self.event_type,
            'data': self.data,
            'timestamp': self.timestamp.isoformat(),
            'source': self.source
        })

class EventBus:
    """Central event bus for decoupled communication."""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_queue = asyncio.Queue()
        self.running = False
        
    def subscribe(self, event_type: str, handler: Callable):
        """Subscribe to event type."""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        
    def unsubscribe(self, event_type: str, handler: Callable):
        """Unsubscribe from event type."""
        if event_type in self.subscribers:
            self.subscribers[event_type].remove(handler)
            
    async def publish(self, event: Event):
        """Publish event to bus."""
        await self.event_queue.put(event)
        
    async def start(self):
        """Start event processing."""
        self.running = True
        asyncio.create_task(self._process_events())
        
    async def _process_events(self):
        """Process events from queue."""
        while self.running:
            try:
                event = await asyncio.wait_for(
                    self.event_queue.get(),
                    timeout=1.0
                )
                
                # Get subscribers for this event type
                handlers = self.subscribers.get(event.event_type, [])
                handlers.extend(self.subscribers.get('*', []))  # Wildcard
                
                # Execute handlers in parallel
                tasks = [
                    self._execute_handler(handler, event)
                    for handler in handlers
                ]
                
                await asyncio.gather(*tasks, return_exceptions=True)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                
    async def _execute_handler(self, handler: Callable, event: Event):
        """Execute event handler safely."""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                await asyncio.get_event_loop().run_in_executor(
                    None, handler, event
                )
        except Exception as e:
            logger.error(f"Error in event handler: {e}")
```

### 4.2 Microservices Architecture

#### Service Registry
```python
# /root/wirereport/services/service_registry.py
import aiohttp
from typing import Dict, List, Optional
import asyncio

class ServiceRegistry:
    """Service discovery and registration."""
    
    def __init__(self, consul_url: str = "http://localhost:8500"):
        self.consul_url = consul_url
        self.services: Dict[str, List[str]] = {}
        self.health_check_interval = 30
        
    async def register_service(
        self,
        name: str,
        service_id: str,
        address: str,
        port: int,
        health_endpoint: str = "/health"
    ):
        """Register a service."""
        service_data = {
            "ID": service_id,
            "Name": name,
            "Address": address,
            "Port": port,
            "Check": {
                "HTTP": f"http://{address}:{port}{health_endpoint}",
                "Interval": "10s"
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.put(
                f"{self.consul_url}/v1/agent/service/register",
                json=service_data
            ) as response:
                response.raise_for_status()
                
    async def discover_service(self, name: str) -> Optional[str]:
        """Discover a healthy service instance."""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.consul_url}/v1/health/service/{name}?passing"
            ) as response:
                if response.status == 200:
                    services = await response.json()
                    if services:
                        # Return first healthy instance
                        service = services[0]
                        addr = service['Service']['Address']
                        port = service['Service']['Port']
                        return f"http://{addr}:{port}"
        return None
```

### 4.3 Monitoring & Observability

#### Implement OpenTelemetry
```python
# /root/wirereport/monitoring/telemetry.py
from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc import (
    trace_exporter,
    metrics_exporter
)
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.instrumentation.aiohttp_client import AioHttpClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor

class TelemetryManager:
    """Centralized telemetry management."""
    
    def __init__(self, service_name: str = "wirereport"):
        self.service_name = service_name
        self.tracer = None
        self.meter = None
        
    def initialize(self, otlp_endpoint: str = "localhost:4317"):
        """Initialize telemetry providers."""
        # Setup tracing
        trace_provider = TracerProvider()
        trace_exporter_instance = trace_exporter.OTLPSpanExporter(
            endpoint=otlp_endpoint
        )
        trace_provider.add_span_processor(
            BatchSpanProcessor(trace_exporter_instance)
        )
        trace.set_tracer_provider(trace_provider)
        self.tracer = trace.get_tracer(self.service_name)
        
        # Setup metrics
        metrics_provider = MeterProvider()
        metrics_exporter_instance = metrics_exporter.OTLPMetricExporter(
            endpoint=otlp_endpoint
        )
        metrics_provider.add_metric_reader(
            PeriodicExportingMetricReader(metrics_exporter_instance)
        )
        metrics.set_meter_provider(metrics_provider)
        self.meter = metrics.get_meter(self.service_name)
        
        # Instrument libraries
        AioHttpClientInstrumentor().instrument()
        RedisInstrumentor().instrument()
        
        # Create custom metrics
        self.tweet_counter = self.meter.create_counter(
            "tweets_generated",
            description="Number of tweets generated"
        )
        
        self.api_latency = self.meter.create_histogram(
            "api_latency",
            description="API call latency in milliseconds"
        )
        
    def trace_operation(self, operation_name: str):
        """Decorator for tracing operations."""
        def decorator(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                with self.tracer.start_as_current_span(operation_name) as span:
                    try:
                        result = await func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(
                            Status(StatusCode.ERROR, str(e))
                        )
                        span.record_exception(e)
                        raise
                        
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                with self.tracer.start_as_current_span(operation_name) as span:
                    try:
                        result = func(*args, **kwargs)
                        span.set_status(Status(StatusCode.OK))
                        return result
                    except Exception as e:
                        span.set_status(
                            Status(StatusCode.ERROR, str(e))
                        )
                        span.record_exception(e)
                        raise
                        
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        return decorator
```

## Phase 5: Production Deployment (Week 5-6)

### 5.1 Containerization

#### Create Dockerfile
```dockerfile
# /root/wirereport/Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 wirereport && \
    chown -R wirereport:wirereport /app

USER wirereport

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV WIREREPORT_ENV=production

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health').raise_for_status()"

# Default command
CMD ["python", "-m", "agents.swarm_master_runner"]
```

#### Docker Compose Configuration
```yaml
# /root/wirereport/docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: wirereport
      POSTGRES_USER: wirereport
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U wirereport"]
      interval: 5s
      timeout: 3s
      retries: 5

  swarm-master:
    build: .
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://wirereport:${POSTGRES_PASSWORD}@postgres/wirereport
    env_file:
      - .env
    depends_on:
      redis:
        condition: service_healthy
      postgres:
        condition: service_healthy
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 2G

  brain-api:
    build: .
    command: ["python", "-m", "agents.brain_api_server"]
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://wirereport:${POSTGRES_PASSWORD}@postgres/wirereport
    env_file:
      - .env
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - postgres
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - brain-api

volumes:
  redis_data:
  postgres_data:
```

### 5.2 Kubernetes Deployment

#### Kubernetes Manifests
```yaml
# /root/wirereport/k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: wirereport-swarm
  labels:
    app: wirereport
    component: swarm
spec:
  replicas: 3
  selector:
    matchLabels:
      app: wirereport
      component: swarm
  template:
    metadata:
      labels:
        app: wirereport
        component: swarm
    spec:
      containers:
      - name: swarm-master
        image: wirereport/swarm:latest
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "2"
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: wirereport-secrets
              key: redis-url
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: wirereport-secrets
              key: database-url
        livenessProbe:
          httpGet:
            path: /health
            port: 9999
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 9999
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: wirereport-brain
spec:
  selector:
    app: wirereport
    component: brain
  ports:
  - port: 8000
    targetPort: 8000
  type: LoadBalancer
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: wirereport-swarm-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: wirereport-swarm
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Implementation Timeline

### Week 1: Security & Foundation
- Day 1-2: Secure credential management
- Day 3-4: API authentication enhancement
- Day 5: Security audit and validation

### Week 2: Performance & Async
- Day 1-3: Async architecture conversion
- Day 4-5: Redis queue implementation

### Week 3: Testing & Quality
- Day 1-2: Unit test framework
- Day 3-4: Integration tests
- Day 5: Error handling standardization

### Week 4: Architecture
- Day 1-2: Event-driven architecture
- Day 3-4: Service registry and discovery
- Day 5: Monitoring implementation

### Week 5: Containerization
- Day 1-2: Docker setup
- Day 3-4: Docker Compose orchestration
- Day 5: Local testing

### Week 6: Production Deployment
- Day 1-2: Kubernetes manifests
- Day 3-4: Production deployment
- Day 5: Validation and monitoring

## Success Metrics

### Security
- ✓ Zero hardcoded credentials
- ✓ All API endpoints authenticated
- ✓ Sensitive data encrypted
- ✓ Security audit passing

### Performance
- ✓ 3x improvement in throughput
- ✓ <100ms average response time
- ✓ Horizontal scaling capability
- ✓ 99.9% uptime

### Quality
- ✓ >80% test coverage
- ✓ Zero critical bugs
- ✓ Standardized error handling
- ✓ Comprehensive logging

### Architecture
- ✓ Microservices deployed
- ✓ Event-driven communication
- ✓ Full observability
- ✓ Auto-scaling enabled

## Conclusion

This comprehensive update plan addresses all critical issues while building on the Wire Report system's excellent architectural foundation. The phased approach ensures minimal disruption to the 24/7 production system while delivering significant improvements in security, performance, scalability, and maintainability.

Key outcomes:
1. **Immediate security fixes** protect sensitive data
2. **Performance improvements** enable 3x throughput
3. **Horizontal scaling** supports growth
4. **Comprehensive testing** ensures reliability
5. **Modern architecture** enables future enhancements

The system will be transformed into a enterprise-grade, cloud-native platform capable of handling significant growth while maintaining the reliability required for sports content automation.