# Architecture Overview: Phases 1-4

**Last Updated:** June 2, 2026
**Completion:** 47% (Phases 1-4 Complete)

---

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│                                                                 │
│  Next.js 15.0.3 + React 19 + TypeScript 5.7.2                  │
│  ├─ Home Page (page.tsx)                                       │
│  ├─ Layouts (layout.tsx)                                       │
│  ├─ API Routes (future)                                        │
│  └─ Global Styling (globals.css)                               │
│                                                                 │
│  Testing:                                                       │
│  ├─ Vitest 2.1.8 (jsdom environment)                           │
│  ├─ @testing-library/react                                    │
│  ├─ Playwright E2E                                             │
│  └─ 70% coverage target                                        │
└────────────────────┬─────────────────────────────────────────┘
                     │
                     │ HTTPS/TLS
                     │ Trace ID Header
                     │ Content-Type: application/json
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY LAYER                            │
│                                                                 │
│  FastAPI 0.115.6 (Uvicorn 0.32.1)                              │
│  ├─ Host: localhost:8000                                       │
│  ├─ Docs: /docs (Swagger UI)                                   │
│  └─ ReDoc: /redoc                                              │
│                                                                 │
│  Request Pipeline (Middleware Stack):                          │
│  1. Trace ID Middleware → X-Trace-ID header                    │
│  2. CORS Middleware → Origin whitelist                         │
│  3. Trusted Host Middleware (production)                       │
│  4. Security Headers Middleware                                │
│  5. Rate Limit Middleware (slowapi)                            │
│  6. Request Logging Middleware                                 │
│  7. Exception Handlers (RFC 7807)                              │
│                                                                 │
│  Error Responses:                                              │
│  ├─ RFC 7807 Problem Details format                           │
│  ├─ Error codes (AUTH_001, RESOURCE_001, etc)                │
│  ├─ Field-level validation errors                             │
│  └─ Trace ID correlation                                      │
└────────────────────┬─────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
    ┌─────────┐  ┌──────────┐  ┌──────────┐
    │ Auth    │  │ v1 API   │  │ Dev      │
    │ Routes  │  │ Routes   │  │ Routes   │
    │         │  │          │  │ (debug)  │
    └────┬────┘  └────┬─────┘  └────┬─────┘
         │            │             │
      ┌──▼────────────▼─────────────▼──┐
      │     API Layer Details          │
      │                                │
      │ Authentication Routes:         │
      │  POST /auth/login              │
      │  POST /auth/register (501)     │
      │  POST /auth/refresh (501)      │
      │                                │
      │ v1 API Routes:                 │
      │  GET /v1/twins/{user_id}       │
      │  POST /v1/simulations          │
      │  GET /v1/career/{user_id}      │
      │                                │
      │ Core Routes:                   │
      │  GET /health (10/min limit)    │
      │  GET /memory/{user_id}         │
      │  POST /incidents/generate      │
      │  POST /incidents/eval-command  │
      │  GET /architecture/analyze     │
      │  WS /ws/simulations/{id}       │
      │  GET /metrics (Prometheus)     │
      │                                │
      │ Development Routes:            │
      │  GET /dev/settings             │
      │  GET /dev/me (auth required)   │
      └────────┬──────────────────────┘
               │
               ▼
    ┌──────────────────────────────────┐
    │  BUSINESS LOGIC LAYER            │
    │                                  │
    │  Config Module (config.py):      │
    │  ├─ Environment detection        │
    │  ├─ JWT secret management        │
    │  ├─ Database DSN loading         │
    │  ├─ CORS origins parsing         │
    │  ├─ Rate limit settings          │
    │  └─ Singleton pattern (@cache)   │
    │                                  │
    │  Security Module (security.py):  │
    │  ├─ RBAC decorators              │
    │  ├─ get_current_user()           │
    │  ├─ require_role(*roles)         │
    │  └─ Token validation             │
    │                                  │
    │  Auth Module (auth.py):          │
    │  ├─ hash_password()              │
    │  ├─ verify_password()            │
    │  ├─ create_access_token()        │
    │  ├─ decode_access_token()        │
    │  └─ Token expiration (24h)       │
    │                                  │
    │  Services Module (services.py):  │
    │  ├─ build_demo_twin()            │
    │  ├─ create_simulation()          │
    │  ├─ generate_incident()          │
    │  ├─ evaluate_command()           │
    │  ├─ predict_career()             │
    │  └─ analyze_repository()         │
    └────────┬──────────────────────┘
             │
             ▼
    ┌──────────────────────────────────┐
    │    CONNECTION LAYER              │
    │  (Database Access Layer)         │
    │                                  │
    │  Database Module (database.py):  │
    │  ├─ create_db_engine()           │
    │  ├─ Connection pooling:          │
    │  │  ├─ Production: 20/40         │
    │  │  ├─ Development: 5/10         │
    │  │  └─ Testing: NullPool         │
    │  ├─ Health checks (pre-ping)     │
    │  ├─ Keepalive (30s)              │
    │  ├─ Connection recycling (1h)    │
    │  └─ SessionLocal factory         │
    │                                  │
    │  Pagination Module:              │
    │  ├─ PaginationParams (query)     │
    │  ├─ PaginatedResponse (response) │
    │  ├─ CursorPaginationParams       │
    │  └─ CursorPaginatedResponse      │
    │                                  │
    │  Error Module (errors.py):       │
    │  ├─ ErrorDetail (RFC 7807)       │
    │  ├─ Error code registry          │
    │  ├─ create_error_response()      │
    │  └─ 11 error types               │
    └────────┬──────────────────────┘
             │
             ▼
    ┌──────────────────────────────────┐
    │    PERSISTENCE LAYER             │
    │                                  │
    │  SQLAlchemy 2.0.25 + ORM         │
    │                                  │
    │  Models (models.py):             │
    │  ├─ User (auth)                  │
    │  │  ├─ id (PK)                   │
    │  │  ├─ email (unique, indexed)   │
    │  │  ├─ password_hash             │
    │  │  ├─ full_name                 │
    │  │  ├─ roles (engineer/admin)    │
    │  │  ├─ is_active (indexed)       │
    │  │  ├─ is_verified               │
    │  │  ├─ created_at                │
    │  │  └─ updated_at                │
    │  │                               │
    │  ├─ EngineerTwinORM (profile)    │
    │  │  ├─ id (PK)                   │
    │  │  ├─ user_id (FK, unique)      │
    │  │  ├─ title                     │
    │  │  ├─ skill_scores_json         │
    │  │  ├─ *_score fields (8)        │
    │  │  ├─ memory_count              │
    │  │  ├─ graph_nodes               │
    │  │  ├─ vector_embeddings         │
    │  │  ├─ created_at                │
    │  │  └─ updated_at                │
    │  │                               │
    │  ├─ EngineerMemoryORM (records)  │
    │  │  ├─ id (PK)                   │
    │  │  ├─ user_id (FK, indexed)     │
    │  │  ├─ twin_id (FK)              │
    │  │  ├─ kind (indexed)            │
    │  │  ├─ summary                   │
    │  │  ├─ signal_strength           │
    │  │  ├─ details_json              │
    │  │  ├─ created_at                │
    │  │  └─ updated_at                │
    │  │                               │
    │  └─ AuditLog (security)          │
    │     ├─ id (PK)                   │
    │     ├─ user_id (FK, indexed)     │
    │     ├─ action (indexed)          │
    │     ├─ resource                  │
    │     ├─ resource_id               │
    │     ├─ status_code               │
    │     ├─ details_json              │
    │     ├─ ip_address                │
    │     ├─ user_agent                │
    │     └─ created_at (indexed)      │
    │                                  │
    │  Alembic Migrations (alembic/):  │
    │  ├─ env.py (migration env)       │
    │  ├─ versions/                    │
    │  │  └─ 001_initial_schema.py     │
    │  │     ├─ Create users table     │
    │  │     ├─ Create twins table     │
    │  │     ├─ Create memories table  │
    │  │     ├─ Create audit_logs      │
    │  │     ├─ Add indexes (8)        │
    │  │     └─ Add FKs                │
    │  └─ alembic.ini (config)         │
    └────────┬──────────────────────┘
             │
             ▼
    ┌──────────────────────────────────┐
    │   DATA STORAGE LAYER             │
    │                                  │
    │  PostgreSQL 16                   │
    │  ├─ users (auth)                 │
    │  ├─ engineer_twins (profiles)    │
    │  ├─ engineer_memories (records)  │
    │  ├─ audit_logs (security)        │
    │  ├─ Indexes: 8                   │
    │  ├─ Foreign keys: 4              │
    │  └─ Schema version control       │
    │                                  │
    │  Backup Strategy:                │
    │  ├─ scripts/backup_database.sh   │
    │  ├─ pg_dump full backup          │
    │  ├─ Compression (gzip)           │
    │  ├─ S3 upload capable            │
    │  ├─ 30-day retention             │
    │  └─ Integrity checks             │
    │                                  │
    │  Future Data Stores:             │
    │  ├─ Neo4j 5 (knowledge graphs)   │
    │  ├─ Qdrant (vector search)       │
    │  ├─ Redis 7 (caching)            │
    │  └─ Kafka 3.8 (events)           │
    └──────────────────────────────────┘
```

---

## Request Flow Diagram

```
User Request
    │
    ▼
┌─────────────────────────────┐
│  HTTPS/TLS Connection       │
│  Trace ID Generated         │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Trace ID Middleware        │
│  Store: request.state       │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  CORS Middleware            │
│  Check origin whitelist     │
│  Return appropriate CORS    │
│  headers or reject          │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Trusted Host Middleware    │
│  (production only)          │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Rate Limit Middleware      │
│  Check: 100 req/min global  │
│  Check: per-endpoint limits │
│  429 if exceeded            │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Security Headers Middleware│
│  Add: X-*, CSP, HSTS        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Request Logging Middleware │
│  Log: method, path, agent   │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Route Handler              │
│  Example: POST /auth/login  │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Auth Handler               │
│  1. Parse credentials       │
│  2. Query database          │
│  3. Verify password         │
│  4. Create JWT token        │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Response Generation        │
│  Status: 200                │
│  Body: {access_token}       │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Response Logging Middleware│
│  Log: status, duration      │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Security Headers Added     │
│  Trace ID Header Added      │
└────────┬────────────────────┘
         │
         ▼
         User Response
```

---

## Testing Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Test Pyramid                                            │
├──────────────────────────────────────────────────────────┤
│                                                          │
│                    E2E Tests (8)                        │
│                  ┌─────────────┐                        │
│                  │ Playwright  │                        │
│                  │ multi-browser                       │
│                  │ real flows  │                        │
│                  └─────────────┘                        │
│                 /               \                       │
│        Integration Tests (30+)                         │
│      ┌──────────────────────────┐                      │
│      │ pytest + TestClient      │                      │
│      │ with service mocks       │                      │
│      │ endpoint coverage        │                      │
│      └──────────────────────────┘                      │
│     /                            \                     │
│  Unit Tests (50+)                                     │
│  ┌─────────────────────────────────────────────┐      │
│  │ pytest: auth, security, config              │      │
│  │ fast, no external deps                      │      │
│  │ pure function tests                         │      │
│  └─────────────────────────────────────────────┘      │
│                                                        │
└──────────────────────────────────────────────────────┘

Frontend Testing:
┌──────────────────────────────────────────────────────────┐
│  Component Tests (Vitest)                               │
│  ├─ React components                                    │
│  ├─ Event handling                                      │
│  ├─ State management                                    │
│  └─ API mocking                                         │
│                                                          │
│  E2E Tests (Playwright)                                 │
│  ├─ User flows                                          │
│  ├─ Multi-browser                                       │
│  ├─ Screenshots on failure                              │
│  └─ Trace mode debugging                                │
└──────────────────────────────────────────────────────────┘

CI/CD Pipeline:
┌──────────────────────────────────────────────────────────┐
│  GitHub Actions (7 Jobs, parallel)                       │
│                                                          │
│  Backend Tests        Frontend Tests                    │
│  ├─ pytest           ├─ tsc                            │
│  ├─ coverage 70%     ├─ eslint                         │
│  └─ Codecov          ├─ vitest                         │
│                      └─ Codecov                        │
│                                                          │
│  Code Quality       Security Scanning                   │
│  ├─ black           ├─ Bandit                          │
│  ├─ ruff            ├─ npm audit                       │
│  └─ diffs           └─ Safety                          │
│                                                          │
│  Docker Build       E2E Tests                          │
│  ├─ api image       ├─ Playwright                      │
│  └─ web image       └─ 3+ browsers                     │
│                                                          │
│  Report                                                │
│  └─ GitHub summary                                     │
└──────────────────────────────────────────────────────────┘
```

---

## Database Architecture

```
PostgreSQL 16 (Primary Data Store)
├─ Connection Pool
│  ├─ Pool size: 20 (prod), 5 (dev), 0 (test)
│  ├─ Max overflow: 40 (prod), 10 (dev)
│  ├─ Pre-ping: enabled (health check)
│  ├─ Recycle: 3600s (1 hour)
│  └─ Keepalive: every 30s
│
├─ Schema (4 core tables)
│  ├─ users (authentication)
│  │  ├─ id (PK)
│  │  ├─ email (unique, indexed)
│  │  ├─ password_hash (bcrypt)
│  │  ├─ roles (comma-separated)
│  │  ├─ is_active (indexed)
│  │  ├─ created_at
│  │  └─ updated_at
│  │
│  ├─ engineer_twins (profiles)
│  │  ├─ id (PK)
│  │  ├─ user_id (FK, unique, indexed)
│  │  ├─ title
│  │  ├─ skill_scores_json
│  │  ├─ debugging_score
│  │  ├─ architecture_score
│  │  ├─ reliability_score
│  │  ├─ leadership_score
│  │  ├─ system_design_score
│  │  ├─ memory_count
│  │  ├─ graph_nodes
│  │  ├─ vector_embeddings
│  │  ├─ created_at
│  │  └─ updated_at
│  │
│  ├─ engineer_memories (records)
│  │  ├─ id (PK)
│  │  ├─ user_id (FK, indexed)
│  │  ├─ twin_id (FK)
│  │  ├─ kind (indexed) [mistake|decision|project]
│  │  ├─ summary (text)
│  │  ├─ signal_strength (0-100)
│  │  ├─ details_json
│  │  ├─ created_at
│  │  └─ updated_at
│  │
│  └─ audit_logs (security)
│     ├─ id (PK)
│     ├─ user_id (FK, indexed)
│     ├─ action (indexed) [login|create|update]
│     ├─ resource [users|twins|memories]
│     ├─ resource_id
│     ├─ status_code
│     ├─ details_json
│     ├─ ip_address
│     ├─ user_agent
│     └─ created_at (indexed)
│
├─ Indexes (8 total)
│  ├─ users.email (unique)
│  ├─ users.is_active
│  ├─ engineer_twins.user_id (unique)
│  ├─ engineer_memories.user_id
│  ├─ engineer_memories.kind
│  ├─ audit_logs.user_id
│  ├─ audit_logs.action
│  └─ audit_logs.created_at
│
├─ Foreign Keys (4 total)
│  ├─ engineer_twins → users
│  ├─ engineer_memories → users
│  ├─ engineer_memories → engineer_twins
│  └─ audit_logs → users
│
├─ Migration History (Alembic)
│  ├─ 001_initial_schema
│  │  ├─ Create users
│  │  ├─ Create engineer_twins
│  │  ├─ Create engineer_memories
│  │  ├─ Create audit_logs
│  │  ├─ Add indexes
│  │  └─ Add foreign keys
│  └─ (future migrations here)
│
└─ Backup Strategy
   ├─ Tool: pg_dump
   ├─ Compression: gzip
   ├─ Frequency: daily (scheduled)
   ├─ Retention: 30 days
   ├─ Upload: S3 capable
   └─ Verification: checksum + header
```

---

## API Versioning Strategy

```
v0 (Legacy - to be deprecated)
├─ /health
├─ /twin/{user_id}
├─ /memory/{user_id}
├─ /simulations
├─ /incidents/*
├─ /architecture/analyze
├─ /career/{user_id}
├─ /ws/simulations/{id}
└─ Status: Maintained for backward compatibility

v1 (Current - stable)
├─ GET /v1/twins/{user_id}
│  ├─ Auth required: yes
│  ├─ Rate limit: 30/min
│  └─ Status: 200
├─ POST /v1/simulations
│  ├─ Auth required: yes
│  ├─ Rate limit: 20/min
│  ├─ Status: 201 Created
│  └─ Body: SimulationRequest
└─ GET /v1/career/{user_id}
   ├─ Auth required: yes
   ├─ Rate limit: 30/min
   └─ Status: 200

v2 (Future)
├─ Expanded fields
├─ New endpoints
├─ Breaking changes allowed
└─ Rollout: TBD

Migration Path:
v0 (now) ──┐
           ├─→ v0 Deprecated (6 months)
           ├─→ v0 Removed (12 months)
           │
v1 (now) ──┤
           ├─→ v1 Stable (current)
           └─→ v1 Deprecated (after v2 GA)

v2 (future)──┤
             └─→ v2 Stable (future)
```

---

## Security Architecture

```
Attack Surface Mitigation:

┌─ Authentication Layer
│  ├─ JWT tokens (signed with HS256)
│  ├─ Expiration: 24 hours
│  ├─ bcrypt passwords (salt rounds: 12)
│  ├─ Timing attack resistant
│  └─ Token validation on every request
│
├─ Authorization Layer
│  ├─ Role-based access control (RBAC)
│  ├─ 3 roles: engineer, reviewer, admin
│  ├─ Per-endpoint role checks
│  ├─ Decorator pattern: @require_role()
│  └─ Audit logging of access
│
├─ Transport Layer
│  ├─ HTTPS/TLS (enforced in prod)
│  ├─ CORS whitelist
│  ├─ Trusted hosts (prod)
│  └─ Security headers:
│     ├─ X-Content-Type-Options: nosniff
│     ├─ X-Frame-Options: DENY
│     ├─ X-XSS-Protection: 1; mode=block
│     ├─ Strict-Transport-Security: max-age=31536000
│     ├─ Referrer-Policy: strict-origin-when-cross-origin
│     └─ Content-Security-Policy: default-src 'self'
│
├─ Input Validation Layer
│  ├─ Pydantic models (all endpoints)
│  ├─ Type checking (mypy)
│  ├─ Field validation (email, password, etc)
│  ├─ Length limits
│  ├─ SQL injection protection (SQLAlchemy)
│  └─ XSS protection (no raw HTML)
│
├─ Rate Limiting
│  ├─ Global: 100 req/min
│  ├─ Per-endpoint: 10-30 req/min
│  ├─ Sliding window
│  ├─ Key: client IP
│  └─ 429 response
│
├─ Logging & Monitoring
│  ├─ Structured JSON logs
│  ├─ All requests logged
│  ├─ Request/response tracking
│  ├─ Error tracking (Sentry)
│  ├─ Audit trail (audit_logs table)
│  ├─ Sensitive data redaction
│  └─ Trace ID correlation
│
├─ Secrets Management
│  ├─ Environment variables only
│  ├─ No hardcoded credentials
│  ├─ .env.local (git ignored)
│  ├─ docker-compose env substitution
│  ├─ Secret rotation ready
│  └─ Vault integration ready (Phase 5)
│
└─ Error Handling
   ├─ RFC 7807 Problem Details
   ├─ No stack traces in production
   ├─ Generic error messages
   ├─ Detailed internal logs
   ├─ Error code registry
   └─ Sentry alerts
```

---

## Data Flow Examples

### Authentication Flow
```
1. User Input → Frontend
   {email: "demo@engineeros.io", password: "demo1234"}

2. POST /auth/login → API
   ├─ Pydantic validation
   ├─ Rate limit check (10 req/min)
   ├─ Database query: User.query(email)
   ├─ bcrypt.verify(password)
   └─ Generate JWT token

3. JWT Token → Frontend
   {
     "access_token": "eyJ0eXAiOiJKV1...",
     "token_type": "bearer",
     "expires_in": 86400
   }

4. Authorization Header
   GET /v1/twins/user-123
   Header: Authorization: Bearer eyJ0eXAiOiJKV1...
```

### Request Tracing Flow
```
1. Request arrives with/without X-Trace-ID
   GET /v1/twins/user-123
   [X-Trace-ID: custom-id OR auto-generated UUID]

2. Trace ID Middleware
   └─ request.state.trace_id = header or UUID

3. All downstream operations
   ├─ Log entries tagged with trace_id
   ├─ Error responses include trace_id
   ├─ Response header: X-Trace-ID

4. Client receives
   ├─ Response header: X-Trace-ID
   ├─ Can use for support tickets
   ├─ Can correlate with server logs
   └─ Full request lifecycle tracked

5. Log correlation
   grep "trace-id-123" /logs/engineeros.log
   │
   └─ All logs for request visible
```

### Pagination Flow
```
1. Client Request
   GET /v1/engineers?page=2&limit=20&sort_by=created_at&sort_order=desc
   
   Query parsed:
   {
     "page": 2,
     "limit": 20,
     "sort_by": "created_at",
     "sort_order": "desc"
   }

2. Database Query
   SELECT * FROM engineers
   ORDER BY created_at DESC
   OFFSET (2-1)*20 = 20
   LIMIT 20

3. Count Query
   SELECT COUNT(*) FROM engineers
   └─ Returns: 1000

4. Response
   {
     "items": [...20 engineers...],
     "total": 1000,
     "page": 2,
     "limit": 20,
     "pages": 50,
     "has_next": true,
     "has_prev": true
   }

5. Client Navigation
   ├─ if has_next: show "Next >"
   ├─ if has_prev: show "< Previous"
   └─ Show page 2 of 50
```

---

**End of Architecture Documentation**

Last Updated: June 2, 2026
Version: 1.0 (Phases 1-4)
