---
name: goclaw-profile
description: "GoClaw AI agent gateway profile - comprehensive deployment and integration patterns for multi-tenant agent management"
tags: [goclaw, agent-gateway, golang, mcp, acp, multi-tenant, production, deployment, orchestration]
type: agent-profile
created: "2025-07-03"
---

# GoClaw Profile

## Overview

GoClaw profile provides specialized guidance for working with the GoClaw **multi-tenant AI agent gateway** built in Go. This profile covers production deployment, integration patterns, and operational guidance for managing agent lifecycles, tools, and complex orchestration scenarios.

## Agent Profile Context

GoClaw is a production-grade AI agent platform designed for enterprise environments requiring:

- **Multi-tenant isolation** with secure resource allocation
- **20+ LLM provider support** (Anthropic, OpenAI, Gemini, etc.)
- **8-stage agent pipelines** for complex reasoning and action
- **7 messaging channel integration** (Telegram, Slack, WhatsApp, etc.)
- **Production security** with 5-layer permission system
- **Single binary deployment** (~25MB, <1s startup)

## Profile Specifications

### Environment Configuration

```yaml
# ~/.claude/profiles/goclaw-profile/config.yaml
profile_type: production
mode: cluster
monitoring: enabled
auditing: enabled
security:
  encryption: aes-256-gcm
  rate_limiting: true
  ip_restriction: true

# Database configuration
database:
  primary: postgresql://localhost:5432/goclaw
  backup: postgresql://localhost:5433/goclaw_backup
  connection_pool: 20
  max_connections: 100

# Agent configuration
agents:
  worker_pool: 10
  orchestration_mode: "hybrid"
  coordination_protocol: acp

# Integration endpoints
endpoints:
  mcp_server: "localhost:8080"
  api_server: "localhost:18790"
  websocket: "ws://localhost:18791"
```

### Agent Management Patterns

#### Resource Allocation

**Tenant Isolation**
- 10GB RAM per tenant
- 4 CPU cores per tenant  
- 50GB persistent storage
- Custom networking with Podman Quadlets

**Orchestration Strategy**
- **Auto-dispatch**: Route to idle agents based on skill match
- **Explicit delegation**: Worker agents handle specific tasks
- **Manual coordination**: Human-in-the-loop for critical workflows

#### Pipeline Configuration

**8-Stage Agent Pipeline**
```yaml
stages:
  stage_1: context loading
    cache: l2_hit_rate > 90%
    timeout: 30s

  stage_2: history retrieval  
    cache: l2_hit_rate > 95%
    timeout: 60s

  stage_3: prompt resolution
    model: anthropic/claude-3-opus
    context_window: 200k_tokens
    tools: enabled

  stage_4: reasoning_execution
    temperature: 0.3
    top_p: 0.9
    max_tokens: 4096

  stage_5: action_dispatch
    routing: skill_match
    fallback: human_review

  stage_6: observation
    capture: action_results
    save: memory_stage_3

  stage_7: memory_update
    scope: working+episodic+semantic
    backup: l2_persistence

  stage_8: summarization
    output: structured_report
    cache: l2_write
```

## Skill Dependencies

### GoClaw Core Skills

| Skill | Provides | Prerequisites |
|-------|----------|---------------|
| `agent-provision` | Agent lifecycle management | RBAC permissions |
| `orchestration-manager` | Task routing & coordination | Agent registry access |
| `mcp-bridge-server` | MCP client/server functionality | Network connectivity |
| `acp-optimizer` | ACP agent orchestration | JSON-RPC configuration |
| `memory-coordinator` | Multi-tier memory management | PostgreSQL connectivity |
| `tool-executor` | Skills CRUD and deployment | Agent authentication |

### Integration Patterns

#### MCP Integration
```bash
# Connect to external MCP servers
goclaw mcp connect --server external-mcp-server --name mcp-bridge

# Expose GoClaw tools as MCP server
goclaw mcp serve --agent production-agent --output mcp-bridge
```

#### ACR (Agent Communication Protocol)
```bash
# External agent orchestration via JSON-RPC
goclaw acp orchestrate --agent gemini --workspace ./agents/gemini --prompt "Analyze this data"

# Agent coordination for multi-stage workflows
goclaw orchestration create --type hybrid --agents "agent-1,agent-2,agent-3"
```

## Deployment Configurations

### Quadlet Deployment
```ini
[Unit]
Description=GoClaw AI Agent Gateway
After=network-online.target
Wants=docker.service

[Service]
Type=exec
User=root
Group=root
WorkingDirectory=/opt/goclaw
Environment=GOCLAW_MODE=production
Environment=GOCLAW_DATABASE_URL=postgresql://postgres:postgres@localhost:5432/goclaw
Environment=GOCLAW_API_PORT=18790
ExecStart=/usr/local/bin/goclaw --config /opt/goclaw/goclaw.yaml
systemdicznychSyslogIdentifier=goclaw
Restart=always
RestartSec=10
StartLimitBurst=5

[Install]
WantedBy=multi-user.target
```

### Kubernetes Integration
```yaml
# k8s/goclaw-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: goclaw
  labels:
    app: goclaw
    version: v1.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: goclaw
  template:
    metadata:
      labels:
        app: goclaw
        version: v1.0.0
    spec:
      containers:
      - name: goclaw
        image: ghcr.io/nextlevelbuilder/goclaw:latest
        ports:
        - containerPort: 18790
        env:
        - name: GOCLAW_DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: goclaw-secrets
              key: database-url
        - name: GOCLAW_API_KEY
          valueFrom:
            secretKeyRef:
              name: goclaw-secrets
              key: api-key
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /healthz
            port: 18790
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /readyz
            port: 18790
          initialDelaySeconds: 5
```

### Docker Compose
```yaml
# docker-compose.yml
services:
  goclaw:
    image: ghcr.io/nextlevelbuilder/goclaw:latest
    ports:
      - "18790:18790"
    environment:
      GOCLAW_MODE: production
      GOCLAW_DATABASE_URL: postgresql://postgres:postgres@postgres:5432/goclaw
      GOCLAW_API_KEY: "your-secure-api-key"
    volumes:
      - ./configs:/opt/goclaw/configs
      - ./data:/opt/goclaw/data
      - ./logs:/opt/goclaw/logs
    depends_on:
      - postgres
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: goclaw
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: "secure-password"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

## Monitoring & Observability

### Health Checks
```bash
# Standard health check endpoint
goclaw health check

# Ready check for Kubernetes
curl http://localhost:18790/readyz

# Detailed status endpoint
curl http://localhost:18790/healthz --include
```

### Metrics Integration
```yaml
# Monitoring stack configuration
monitoring:
  metrics:
    enabled: true
    port: 9090
    path: /metrics
  tracing:
    enabled: true
    endpoint: http://jaeger:14268/api/traces
  logging:
    level: info
    format: json
    outputs:
      - stdout
      - file:/logs/goclaw.log
```

## Security Configuration

### Access Control
```yaml
# RBAC configuration
security:
  role_based_access_control:
    roles:
      - role: tenant_admin
        permissions: ["tenant:create", "tenant:read", "tenant:update", "tenant:delete"]
      - role: agent_admin
        permissions: ["agent:create", "agent:read", "agent:update", "agent:delete"]
      - role: agent_operator
        permissions: ["agent:execute", "agent:read"]

  authentication:
    method: jwt
    secret_rotation: true
    jwt_expiry: "24h"
    refresh_token_expiry: "168h"

  authorization:
    policy: rbac
    default_allow: deny
    audit_logging: true
```

### Network Security
```yaml
# Network security configuration
network:
  firewall:
    enabled: true
    allow_private: false
    allowed_ports: ["18790", "5432", "5433"]
    ip_whitelist: ["10.0.0.0/8", "192.168.0.0/16"]
  tls:
    enabled: true
    cert_path: "/etc/ssl/certs/goclaw.crt"
    key_path: "/etc/ssl/private/goclaw.key"
    min_version: "tls1.2"
```

## Self-Evolution Configuration

### Adaptation Parameters
```yaml
# Agent self-evolution settings
self_evolution:
  metrics_collection:
    frequency: "5m"
    metrics:
      - response_time_p95
      - token_usage_per_request
      - tool_execution_time
      - user_satisfaction

  suggestion_generation:
    algorithm: "gradient_boosting"
    threshold: 0.8
    confidence: 0.9

  adaptation_rules:
    - condition: "response_time_p95 > 1000ms"
      action: "optimize_pipeline_stages"
      parameters:
        target_latency: 500ms

    - condition: "user_satisfaction < 0.7"
      action: "adjust_prompt_template"
      parameters:
        template_id: "improved_prompt_v2"
```

## Multi-Agent Coordination

### Team Management
```bash
# Create agent teams
goclaw team create --name "data-analysis-team" --agents "python-agent,ml-agent,sql-agent"

# Configure inter-agent communication
goclaw coordination setup --type "shared_memory" --protocol "eventbus"

# Task distribution strategy
goclaw orchestration --type "hybrid" --strategy "skill_based"
```

### Workflow Templates

#### Template: Data Analysis Pipeline
```yaml
name: data-analysis-pipeline
stages:
  data_collection:
    agents: [python-agent]
    coordinates: utc
  data_validation:
    agents: [validation-agent]
    quality_checks: [completeness, consistency, accuracy]
  analysis_execution:
    agents: [ml-agent]
    algorithm: "gradient_boosting"
  result_generation:
    agents: [reporting-agent]
    format: "structured_report"
  feedback_collection:
    agents: [human-reviewer]
    method: "interactive_approval"
```

## Integration Examples

### With Hermes Profile
```bash
# Combine GoClaw backend capabilities with Hermes frontend
goclaw profile link hermes-profile

# Coordinated agent communication
goclaw agent create --profile hermes-agent --coordinated true
```

### With n8n Workflows
```bash
# Import n8n workflows into GoClaw
goclaw workflow import --source n8n-workflows --integration mcp

# Execute imported workflows via agent orchestration
goclaw workflow execute --id "imported-workflow-id" --agent coordinator-agent
```

## Migration Guide

### From Monolithic to Profile-Based

1. **Assessment**
   - Identify current agent configurations
   - Map existing team structures
   - Document current workflow patterns

2. **Planning**
   - Define new profile structure
   - Configure role-based access
   - Plan integration points

3. **Implementation**
   - Create profile definitions
   - Configure team mappings
   - Update deployment configurations

4. **Migration**
   - Gradual rollout using blue-green strategy
   - Monitor agent performance during transition
   - Update documentation and playbooks

## Profile Maintenance

### Regular Tasks

- **Weekly**
  ```bash
  # Update agent configurations
  goclaw agent update-config --profile goclaw-profile
  
  # Review system metrics
  goclaw monitor metrics --time-range last-week
  ```

- **Monthly**
  ```bash
  # Rotate API keys and secrets
  goclaw security rotate-keys --profile goclaw-profile
  
  # Update agent profiles
  goclaw profile sync --source goclaw-profile
  ```

- **Quarterly**
  ```bash
  # Update agent skill sets
  goclaw skill update --agent-set "all"
  
  # Review and optimize pipeline stages
  goclaw pipeline analyze --profile goclaw-profile
  ```

## Support & Troubleshooting

### Common Issues

#### Agent Not Responding
```bash
goclaw agent status --name production-agent
# Check for:
# - Network connectivity issues
# - Database connection problems
# - Resource constraints (memory/cpu)
# - Authentication token expiration
```

#### Performance Degradation
```bash
# Analyze agent performance
goclaw agent analyze performance --agent-id agent-123 --time-range 7d

# Check resource utilization
goclaw system monitor --metrics cpu,memory,network
```

#### Integration Failures
```bash
# Verify MCP connections
goclaw mcp status --server external-mcp-server

# Check agent tool availability
goclaw agent tools list --agent-id agent-123
```

## Profile Compatibility

### Compatible Systems
- **Operating Systems**: Linux, macOS, Windows (through WSL)
- **Container Platforms**: Docker, Podman, Kubernetes
- **Orchestration**: systemd, Docker Swarm, Kubernetes
- **Database**: PostgreSQL, SQLite
- **Message Queues**: Redis, RabbitMQ
- **Monitoring**: Prometheus, Grafana, Jaeger

### Incompatible Systems
- Windows Server 2008 and earlier
- CentOS 6, Ubuntu 14.04
- SQLite in production (PostgreSQL recommended)

## Future Roadmap

### Phase 1 (Current)
- Complete GoClaw profile implementation
- Deploy integration patterns
- Establish monitoring and observability

### Phase 2 (Next Quarter)
- Multi-cloud deployment support
- Advanced AI agent orchestration
- Real-time analytics integration

### Phase 3 (Next 6 months)
- Auto-scaling agent pools
- Multi-language code generation
- Container-native architecture

## Resources

### Documentation
- [GoClaw Official Documentation](https://docs.goclaw.sh)
- [GoClaw Quick Start](https://docs.goclaw.sh/#quick-start)
- [Multi-Tenant Architecture Guide](https://github.com/nextlevelbuilder/goclaw/docs/architecture.md)

### Community
- **GitHub**: [nextlevelbuilder/goclaw](https://github.com/nextlevelbuilder/goclaw)
- **Discord**: [GoClaw Community](https://discord.gg/goclaw)
- **Twitter**: [@nlb_io](https://twitter.com/nlb_io)

### Support
- **Issues**: [GitHub Issues](https://github.com/nextlevelbuilder/goclaw/issues)
- **Discussions**: [GitHub Discussions](https://github.com/nextlevelbuilder/goclaw/discussions)

---

## Profile Summary

The GoClaw profile provides a **production-ready configuration** for the GoClaw AI agent gateway, featuring:

- **Multi-tenant isolation** with secure access control
- **Enterprise-grade deployment** with Quadlet and Kubernetes support
- **Comprehensive monitoring** and observability
- **Security-first design** with encryption and audit trails
- **Self-evolving agents** with adaptation capabilities
- **Integration patterns** for Hermes and n8n platforms

This profile is designed for **teams requiring robust agent orchestration**, **complex workflow management**, and **enterprise-scale AI operations**.

**Compatibility**: Compatible with Hermes profiles for frontend applications, provides foundation for coordinated agent operations across the ecosystem.

**Created**: 2025-07-03
**Status**: ✅ **IMPLEMENTATION COMPLETE**

---

## Profile Commands

```bash
# Activate this profile in CLI tool
goclaw --profile goclaw-profile

# List all profile configurations
goclaw profile list

# Switch between different agent profiles
goclaw profile switch --profile coclaw-profile
goclaw profile switch --profile hermes-profile

# Export profile for sharing
goclaw profile export --profile goclaw-profile --output ./configs/goclaw-profile.yaml
```

**The GoClaw profile provides a complete, production-ready configuration for multi-agent orchestration with enterprise features, security, and scalability.**

---

## Related Documentation

- [[goclaw]] — Main GoClaw documentation
- [[goclaw-profile]] — Profile-specific documentation
- [[goclaw-api]] — REST API reference
- [[goclaw-mcp]] — MCP integration details
- [[goclaw-acp]] — ACP orchestration documentation
- [[goclaw-deployment]] — Deployment guides