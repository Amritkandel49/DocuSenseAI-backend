# Phase I: Environment Orchestration - Technical Notes and Key Takeaways

This document serves as a reference manual and technical log for Phase I of the DocuSense AI project. It outlines the precise commands, infrastructure architectural decisions, configuration mechanisms, and database engine modifications performed to construct the backend foundation.

---

## 1. Architectural Blueprint and Component Overview

The backend infrastructure utilizes isolated runtime environments managed via Docker Compose. The environment consists of two core stateful engines running within a unified virtual network:

| Component | Technical Role | Engine/Image | Context |
| :--- | :--- | :--- | :--- |
| **Relational & Vector Store** | Primary database managing relational metadata and operational metrics along with embedded structural data. | `pgvector/pgvector:pg16` | Persistent Storage |
| **In-Memory Store** | High-speed cache and atomic queuing broker for background worker operations. | `redis:7-alpine` | Volatile Memory Cache |

---

## 2. Environment Isolation & Configuration Security

To prevent security vulnerabilities caused by committing secrets to source control, the environment employs a separated variable injection architecture.

### The Decoupling Workflow

1. **The Secret Registry (`.env`):** A plain-text local ledger mapping critical variables to physical strings. This file is explicitly tracking-banned by appending it to the `.gitignore` asset.
2. **The Blueprint (`docker-compose.yml`):** A tracking-safe specification containing zero hardcoded production values, referencing variable handles instead.
3. **The Engine Resolution:** During initialization, the container execution runtime evaluates environment variables natively from `.env` and compiles the service manifests programmatically.

### Critical Syntax Conventions

* **String Evaluation Rules:** String literals inside `.env` require no bounding tokens unless special syntactic punctuation or hash marks (`#`) are introduced.
* **Hash Mark Truncation Guard:** If a password payload includes a native bash comment indicator (`#`), wrapping the sequence in explicit double quotes (`"..."`) prevents runtime truncations.

---

## 3. Operational Command Reference

### Docker Infrastructure Orchestration

**Validate Decoupled Variables:**

```bash
docker compose config
```

Parses the manifest, resolves interpolations from `.env`, and returns the final structural map for validity verification.

**Spin-up Detached Daemons:**

```bash
docker compose up -d
```

The detached flag (`-d`) splits container processes from the interactive stdout pipeline of the current terminal shell, maintaining state inside persistent system daemons.

**Inspect Active Namespace:**

```bash
docker ps -a
```

Queries the running engine for all local allocations. Returns process statuses, mapping bindings, container names, and current up-times.

### Port Conflicts and Resolution (Linux Environment)

If port initialization throws a native socket binding error (`bind: address already in use`), it implies a host-level system process is already operating on that specific network interface.

**Investigate Sockets:**

```bash
sudo lsof -i :5432
```

Queries the Linux networking layer to isolate the unique PID binding port 5432.

**Halt Host Daemons:**

```bash
sudo systemctl stop postgresql
```

Suspends background instances running at the host OS layer, liberating network resources for Docker allocation.

---

## 4. Database Optimization & Feature Engineering

### The `docker exec` Lifecycle

Interacting with specific diagnostic tools wrapped inside isolated environments requires programmatic entry points:

```bash
docker exec -it docusense_postgres psql -U postgres -d docusense_db
```

* **`exec`:** Instructs the daemon to fork an independent process stream inside an active container ecosystem.
* **`-i` (interactive):** Hooks standard shell input pipelines to the target runtime.
* **`-t` (pseudo-TTY):** Allocates structural terminal rendering and typography processing.
* **`psql -U ... -d ...`:** Directly boots the database console client targeting specific database clusters and security user roles.

### Extension Initialization

Standard relational tables are unequipped to calculate cosine similarities or handle text embeddings natively. Activating mathematical arrays requires loading specific shared memory extensions:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

* **SQL Termination Syntax:** Statements within interactive CLI utilities queue indefinitely until a terminating semicolon (`;`) is encountered. A continuing hyphen marker (`-`) indicates the SQL query engine is waiting for syntax closure.
* **Verification:** Successful execution issues a `CREATE EXTENSION` message confirming the pgvector index engines are loaded into memory.

### Exiting Interactive Client Prompts

```sql
\q
```

The escape character backslash (`\`) commands the local terminal wrapper to interpret the subsequent string as a control command rather than a table schema query, terminating the interactive connection cleanly.

---

## 5. In-Memory Subsystem Health Evaluation

Validation of the volatile memory cache engine avoids heavy application testing layers by querying the service using simple ping sequences:

```bash
docker exec -it docusense_redis redis-cli ping
```

**Evaluation Criteria:** A structured response containing the string `PONG` establishes that the database cluster has established socket connections, successfully read local RAM tables, and is functional.

---

## 6. Key Takeaways and Architectural Patterns

* **Uniform Configuration:** Environmental configuration consistency across developers is achieved entirely by committing the standard file templates while keeping sensitive localized files tracking-banned.
* **Network Encapsulation:** Shared networks managed inside Compose schemas allow independent containers to securely resolve addresses by standard service naming keywords instead of manual IP assignments.
* **AI Processing Readiness:** Enabling vector extensions transforms a traditional relational SQL data structure into an optimization-ready mathematical store capable of executing dense geometric algorithms across multi-dimensional embedding matrices.
