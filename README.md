# 🛸 EngineerOS: Staff-Level Engineering Command Center

EngineerOS is an enterprise-grade, telemetric digital twin cockpit for software engineers. It models an engineer's technical profile, distributed systems mastery, incident response decisions, architecture pattern preferences, and long-term career growth trajectory as a living, data-driven virtual twin.

---

## 🏗️ Clean Architecture & System Design

EngineerOS is designed around the principles of **Domain-Driven Design (DDD)**, clean separation of concerns, and resilient real-time state synchronization.

```
                      ┌──────────────────────────────────────────┐
                      │          Next.js Client (3000)           │
                      └───────────────┬──────────────────────────┘
                                      │ (JWT / HTTPS / WSS)
                                      ▼
                      ┌──────────────────────────────────────────┐
                      │          FastAPI Gateway (8000)          │
                      └───────────────┬──────────────────────────┘
                                      │
             ┌────────────────────────┴────────────────────────┐
             ▼                                                 ▼
        ┌───────────┐                                     ┌───────────┐
        │Middleware │                                     │  Service  │
        │(Trace/ID) │                                     │   Layer   │
        └───────────┘                                     └─────┬─────┘
                                                                │
                               ┌────────────────────────────────┼────────────────────────────────┐
                               ▼                                ▼                                ▼
                  ┌──────────────────────────┐     ┌──────────────────────────┐     ┌──────────────────────────┐
                  │       Domain Layer       │     │     Repository Layer     │     │        Events Bus        │
                  │(Entities, VO, Exception) │     │(Base, Twin, User, Memory)│     │(Publish/Subscribe/Handl) │
                  └──────────────────────────┘     └────────────┬─────────────┘     └──────────────────────────┘
                                                                │
                                                                ▼
                                                   ┌──────────────────────────┐
                                                   │    SQLite / SQLAlchemy   │
                                                   └──────────────────────────┘
```

### 1. Backend Clean Architecture (FastAPI & SQLAlchemy 2.0)
* **Domain Layer** (`backend/app/domain/`): Pure business logic. Defines entities (`EngineerProfile`, `MemoryEntry`), Value Objects (`SkillLevel`, `ReputationScore`), custom domain exceptions (`DuplicateEntity`), and domain events. Fully decoupled from framework and database dependencies.
* **Repository Pattern** (`backend/app/repositories/`): Data access abstraction isolating business operations from raw database queries.
* **Database Connection Pooling** (`backend/app/database.py`): Configures enterprise-grade SQLAlchemy connection pooling. Uses environment-specific configurations (larger pool sizes and overflow thresholds in production; SQLite `StaticPool` in development).
* **Asynchronous Event Bus** (`backend/app/events/`): Implements an async pub/sub system to run side-effects (e.g. logging metrics, updating database twin stats, recording audit logs) out-of-band to optimize response times.
* **JWT Security & Token Blacklist** (`backend/app/security.py`): Custom authentication dependencies verifying role-based access controls (RBAC) and validating JWT tokens against an in-memory token blacklist (supporting instantaneous session revocation).
* **RFC 7807 Problem Details Standard** (`backend/app/errors.py`): Implements structured error payloads for API clients, guaranteeing zero sensitive information leakage in production.
* **Unified Trace ID Correlation**: Middleware automatically injects an `X-Trace-ID` UUID header into every response and links it to Sentry telemetry for unified error tracking.

### 2. Frontend Cockpit Architecture (Next.js 15.5 & Three.js WebGL)
* **Zustand-Style Global Auth Store** (`app/hooks/useAuth.ts`): Implements a lightweight reactive subscription pattern that coordinates user credentials, loading states, and error alerts. Syncs immediately between all hook instances, removing rendering lags or refresh flashes.
* **Latest Ref Hook Pattern** (`app/hooks/useWebSocket.ts`): Stores message callbacks inside a mutable `useRef`. This decouples WebSocket state updates from connection hooks, terminating connection drops and infinite reconnect loops during component lifecycle updates.
* **High-Performance 3D Physics Tracking** (`app/components/TwinGraph.tsx`): Bypasses Next.js re-render cycles by storing cursor positions in a stable `useRef` directly queried by the Three.js animate loop, maintaining a constant **60fps** under hover loads.
* **Hydration Mismatch Resolution**: Postpones token extraction from `localStorage` until client-mount time inside `useEffect`, preventing React hydration crashes on SSR page layouts.

---

## 🔒 Setup & Local Execution

### 1. Environment Configuration
Create your local environment file at the root:
```bash
cp .env.example .env.local
```

> [!IMPORTANT]
> **Windows Port Mapping & IPv6 Resolution**: On Windows machines, `localhost` often attempts resolving to the IPv6 loopback `[::1]:8000`, which might collide with other background system services. To bypass this, always define the API host explicitly as the IPv4 loopback `127.0.0.1`:
> * `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`
> * `NEXT_PUBLIC_WS_URL=ws://127.0.0.1:8000`

### 2. Dependency Installation
**Frontend (Next.js):**
```bash
npm install
```

**Backend (Python virtual environment):**
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Database Migration
Apply the database schemas to the SQLite dev database:
```bash
cd backend
.venv\Scripts\activate
python -m alembic upgrade head
```

### 4. Running the Development Servers

**FastAPI Backend Server:**
```bash
cd backend
.venv\Scripts\activate
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```
* Interactive Swagger docs are accessible at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

**Next.js Frontend Client:**
```bash
npm run dev
```
* Command cockpit is accessible at: [http://localhost:3000](http://localhost:3000)

### 5. Seeded Sandbox Credentials
On the login overlay screen, select **"Initialize Sandbox Demo"** to auto-fill the sandbox account credentials:
* **Security Token (Email)**: `demo@engineeros.io`
* **Access Key (Password)**: `demo1234`

---

## 🧪 Testing & Code Quality

* **Backend Test Suite (pytest)**: Includes unit tests, integration tests, and security tests.
  ```bash
  cd backend
  .venv\Scripts\python -m pytest --cov=app tests/
  ```
  *Current status*: **50/50 tests passing** with **72% total code coverage** (exceeding the 70% threshold).
* **Frontend Type-Check (tsc)**: Fully validated type compilation.
  ```bash
  npx tsc --noEmit
  ```
* **Frontend Production Build**: Bundles optimization files.
  ```bash
  npm run build
  ```

---

## 🚀 API Endpoint Reference & Schemas

### Endpoint Routing Matrix

| Endpoint | Method | Authentication | Rate Limit | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| `/auth/register` | `POST` | None | None | Register a new engineering profile. |
| `/auth/login` | `POST` | None | None | Authenticate credentials and get a signed JWT. |
| `/auth/refresh` | `POST` | None | None | Refresh token session. |
| `/auth/logout` | `POST` | JWT Bearer | None | Invalidate session token (blacklists token). |
| `/health` | `GET` | None | 10 req/min | Health check + database connection check. |
| `/twin/{user_id}` | `GET` | None | 30 req/min | Retrieve the digital twin scores and telemetry. |
| `/memory/{user_id}` | `GET` | None | 30 req/min | List active engineering memory nodes. |
| `/simulations` | `POST` | None | 20 req/min | Start a new SRE/incident simulation. |
| `/incidents/generate` | `POST` | None | 10 req/min | Create incident details for the cockpit. |
| `/incidents/evaluate-command` | `POST` | None | 20 req/min | Submit SRE commands for evaluation. |
| `/architecture/analyze` | `GET` | None | 15 req/min | Map code architecture risks and hot spots. |
| `/career/{user_id}` | `GET` | None | 30 req/min | Get promotion/interview readiness stats. |
| `/ws/simulations/{id}` | `WS` | None | None | Live WebSocket stream for simulation dialogues. |
| `/metrics` | `GET` | None | None | Prometheus telemetry exports. |

### Request Payload Schemas

* **`POST /auth/register`**
  ```json
  {
    "email": "engineer@engineeros.io",
    "password": "securePassword123",
    "full_name": "Senior Developer"
  }
  ```

* **`POST /auth/login`**
  ```json
  {
    "email": "demo@engineeros.io",
    "password": "demo1234"
  }
  ```

* **`POST /simulations`**
  ```json
  {
    "scenario": "Netflix-style regional outage",
    "difficulty": "senior",
    "minutes": 45
  }
  ```

* **`POST /incidents/evaluate-command`**
  ```json
  {
    "user_id": "demo_user",
    "command": "check p99, cache hit rate, deploy diff",
    "scenario": "Netflix-style regional outage",
    "elapsed_seconds": 0
  }
  ```

