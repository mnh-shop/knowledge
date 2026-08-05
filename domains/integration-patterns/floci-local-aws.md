---
name: floci-local-aws
type: integration-pattern
tag: [floci, aws, emulator, localstack, quarkus, java, docker, integration-patterns, testing, ci, testcontainers]
description: "Local AWS emulation with Floci — AWS wire-protocol matrix, storage modes, Docker-backed service map, TLS mode, config surface, and compatibility testing patterns"
---

# Integration Pattern: Floci Local AWS Emulation

## Overview

Floci (`floci/floci:latest`, port 4566) is a free MIT-licensed local AWS emulator that replaces LocalStack Community for development, testing, and CI. This pattern documents how Floci achieves drop-in AWS compatibility: real AWS wire protocols, a pluggable storage layer, and real Docker containers where fidelity matters — plus the operational surface (TLS, config, health/admin endpoints) and the compatibility-testing story.

```text
AWS SDK / CLI / IaC (Java · Python · Node · Go · Terraform · CDK · OpenTofu)
        │  HTTP :4566 (AWS wire protocol)          │ HTTPS :4566 (TLS mode, same port)
        ▼                                          ▼
┌─────────────────────────────── Floci ───────────────────────────────┐
│ Router ──┬─ AwsQueryController (Query → XML)                        │
│          ├─ AwsJson11Controller (JSON 1.1, X-Amz-Target)            │
│          ├─ AwsJsonCborController (smithy-rpc-v2-cbor, DynamoDB)    │
│          ├─ JAX-RS (REST JSON / REST XML: S3, Lambda, API GW)       │
│          └─ TCP proxies (ElastiCache RESP, RDS JDBC, Neptune)       │
│ ServiceRegistry + ResolvedServiceCatalog → 68 service packages      │
│ StorageFactory → memory · persistent · hybrid · wal (account-aware) │
└──────────────┬──────────────────────────────────────────────────────┘
               │ Docker API (docker.sock mount)
               ▼
   Docker Engine: Lambda · RDS · ElastiCache · Neptune · DocumentDB ·
                  MSK · ECS · EC2 · EKS · OpenSearch · CodeBuild · ECR
                  Athena → DuckDB sidecar · CUR → floci-duck sidecar
```

## Wire-Protocol Matrix

Floci implements real AWS wire protocols (not convenience APIs), so any AWS-compatible client works unchanged:

| Protocol | Implementation | Request → Response | Services |
|---|---|---|---|
| **Query** | `AwsQueryController` (496 lines) | form-encoded POST + `Action` → XML | SQS, SNS, IAM, STS, SES, RDS, ElastiCache, CloudFormation, CloudWatch Metrics, EC2, ELB v2, Auto Scaling, Elastic Beanstalk |
| **JSON 1.1** | `AwsJson11Controller` (260 lines) | POST + `X-Amz-Target` → JSON | SSM, EventBridge, CloudWatch Logs, KMS, Kinesis, Cognito, Secrets Manager, ACM, ECS, ECR, Glue, Athena, Firehose, CodePipeline, CodeBuild, CodeDeploy, MemoryDB, and more |
| **JSON/CBOR** | `AwsJsonCborController` | binary CBOR (smithy-rpc-v2-cbor) | DynamoDB |
| **REST JSON** | JAX-RS controllers | REST paths → JSON | Lambda management, API Gateway v2, SES v2, Bedrock Runtime |
| **REST XML** | JAX-RS `S3Controller` | REST paths → XML | S3, S3 Control |
| **TCP** | proxy containers | raw protocol | ElastiCache (RESP), RDS (JDBC), Neptune (Gremlin WebSocket) |

**TLS mode** (`FLOCI_TLS_ENABLED`): a Vert.x proxy (`config/TlsProxyServer.java`) listens on 4566 and sniffs the first byte of each connection — `0x16` (TLS ClientHello) routes to the HTTPS backend (internal 4511), anything else to HTTP (internal 4510). Both `http://localhost:4566` and `https://localhost:4566` work on the same port (LocalStack parity). Supports self-signed cert auto-generation and an optional AWS-443 bind for CDK `cfn-response` callbacks.

## Storage Modes (Speed ↔ Durability)

Configured via `FLOCI_STORAGE_MODE` (default `memory`) or per-service; created by `core/storage/StorageFactory.java` (145 lines):

| Mode | Behavior | Best for |
|---|---|---|
| `memory` | In RAM only; lost on stop | CI, ephemeral tests |
| `persistent` | Loaded at startup; flushed on every write | Simple state preservation |
| `hybrid` | In-memory + async flush every 5s | Local development |
| `wal` | Write-ahead log; every mutation logged before responding | Maximum durability |

**Account-aware isolation**: backends are wrapped in `AccountAwareStorageBackend` — resources are namespaced by the calling credential's account ID (12-digit AKID → account ID; otherwise `FLOCI_DEFAULT_ACCOUNT_ID`, default `000000000000`). STS temporary credentials resolve to the assumed role's account, so the cross-account assume-role-then-provision pattern works locally.

## Docker-Backed Service Map

Real containers are used where in-process emulation would reduce fidelity (requires `-v /var/run/docker.sock:/var/run/docker.sock`):

| Service | Default image | What is real |
|---|---|---|
| Lambda | `public.ecr.aws/lambda/<runtime>` | Runtime env, warm pool (`WarmPool.java`: reuse, idle eviction, `FLOCI_SERVICES_LAMBDA_EPHEMERAL=true`), hot-reload bind-mount |
| RDS | `postgres:16-alpine` / `mysql:8.0` / `mariadb:11` | Real engines, IAM auth, JDBC access |
| ElastiCache | `valkey/valkey:8` | Redis/Valkey protocol, SigV4 auth |
| Neptune | `tinkerpop/gremlin-server:3.7.3` (or `neo4j:5-community`) | Gremlin WebSocket / openCypher Bolt |
| DocumentDB | `mongo:7.0` | MongoDB wire protocol |
| MSK | `redpandadata/redpanda:latest` | Kafka-compatible broker |
| ECS / EC2 / EKS | user image / AMI-mapped / `rancher/k3s:latest` | Container lifecycle, k3s Kube API |
| OpenSearch | `opensearchproject/opensearch:2` | Full OpenSearch engine |
| CodeBuild | user image | Real buildspec execution, logs, S3 artifacts |
| ECR | `registry:2` | Real OCI registry (docker push/pull); admin GC endpoint `/_floci/ecr/gc` |
| Athena / CUR | DuckDB sidecar (`floci-duck`) | Real SQL over S3/Glue; Parquet emission |

## Config Surface

All settings via `FLOCI_` env vars (`EmulatorConfig.java`, 1645 lines):

- **Basics**: `FLOCI_PORT` (4566), `FLOCI_DEFAULT_REGION` (us-east-1), `FLOCI_DEFAULT_ACCOUNT_ID`, `FLOCI_BASE_URL`, `FLOCI_HOSTNAME`, `FLOCI_STORAGE_MODE` / `FLOCI_STORAGE_PERSISTENT_PATH`
- **`FLOCI_SERVICES_*`**: per-service overrides — `FLOCI_SERVICES_LAMBDA_DOCKER_NETWORK`, `FLOCI_SERVICES_<SVC>_DEFAULT_IMAGE`, `FLOCI_SERVICES_RDS_MOCK`, per-service `dockerNetwork`, Lambda hot-reload bucket config
- **TLS**: `FLOCI_TLS_ENABLED`, `FLOCI_TLS_CERT_PATH`, `FLOCI_TLS_KEY_PATH`, `FLOCI_TLS_SELF_SIGNED`, `FLOCI_TLS_AWS_HTTPS_PORT`
- **Proxy base ports** (docker-compose ranges): ElastiCache 6379-6399, MemoryDB 6400+, RDS 7001-7099, Neptune 8182, OpenSearch 9200-9299
- **LocalStack migration**: `LOCALSTACK_HOST`, `PERSISTENCE=1`, `LAMBDA_DOCKER_NETWORK`, `LAMBDA_REMOVE_CONTAINERS`, `DEBUG=1` translate automatically; `/_localstack/health` and init scripts keep working

## Operations / Observability Endpoints

`/_floci/*` (and `/_localstack/*` parity aliases): `health`, `info`, `init`, `diagnose`, `config`, `state/reset`, `state/nuke`, `ui` (+ `ui/status`). The `/_floci/ecr/gc` admin endpoint reclaims registry disk after image deletes.

## Testing & CI Patterns

- **Testcontainers**: `io.floci:testcontainers-floci` (Java/Maven Central), `@floci/testcontainers` (npm), `testcontainers-floci` (PyPI) — isolated instances per test, no shared state or port conflicts.
- **Compatibility suite** (`compatibility-tests/`): **2,506 tests** across 5 SDKs (Java v2 1,326 · Node v3 449 · Python boto3 311 · Go v2 157 · AWS CLI 205) and 3 IaC tools (Terraform 22 · OpenTofu 16 · CDK 20).
- **Multi-account test pattern**: pass 12-digit AKIDs (`111111111111`, `222222222222`) to exercise account isolation; any non-empty credentials work for single-account flows.
- **CI speed**: native image starts in ~24 ms with ~13 MiB idle memory (~40 MB native binary, ~90 MB image) — practical for per-test-run emulators.

## Related

- [[floci]] — Main wiki entry
- [[opentofu]] — IaC tooling compatible with the local AWS endpoint
- [[localstack]] — The emulator Floci replaces
- [[quadlet-deployment-guide]] — Container deployment patterns usable for hosting Floci
- [[mcp-server-setup]] — MCP servers that can target the local AWS endpoint
