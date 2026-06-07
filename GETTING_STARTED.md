# Getting Started Guide

Complete walkthrough to get EngineerOS running locally with all security features.

## Prerequisites

- **Python 3.12+**
- **Node.js 20+** 
- **Docker & Docker Compose**
- **Git**

## Step 1: Clone & Setup

```bash
# Clone repository
git clone <your-repo-url>
cd new

# Create local environment file
cp .env.example .env.local

# Generate a secure JWT secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Copy the output and update JWT_SECRET_KEY in .env.local
```

## Step 2: Configure Environment

Edit `.env.local` with your settings:

```bash
# Essential for security
JWT_SECRET_KEY=<paste-generated-key-here>
ENVIRONMENT=development
DEBUG=true

# Keep defaults for local dev
POSTGRES_USER=engineeros
POSTGRES_PASSWORD=engineeros
POSTGRES_DB=engineeros
NEO4J_PASSWORD=change_me_in_production

# Frontend connectivity
NEXT_PUBLIC_API_URL=http://localhost:8000
API_CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

**Important:** Never commit `.env.local` to git. It's in `.gitignore`.

## Step 3: Run Full Stack

### Option A: Docker Compose (Recommended)

```bash
# Start all services (PostgreSQL, Neo4j, FastAPI, Next.js, etc.)
docker compose up --build

# In another terminal, check services are healthy
docker compose ps
```

**Services Available:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (user: admin, password: admin)
- Neo4j: http://localhost:7474 (user: neo4j)

### Option B: Local Development (Manual)

**Terminal 1: PostgreSQL + Infrastructure**
```bash
# Start just the databases/services
docker compose up postgres neo4j qdrant redis kafka prometheus grafana
```

**Terminal 2: Python Backend**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run FastAPI server
cd backend
uvicorn app.main:app --reload --port 8000
```

**Terminal 3: Node.js Frontend**
```bash
npm install
npm run dev
```

## Step 4: Test Authentication

### Login Demo (Easiest)

```bash
# Install httpx if needed
pip install httpx

# Run authentication demo
python AUTH_DEMO.py
```

Expected output:
```
✓ Login successful
  User ID: demo_user
  Token: eyJhbGc...

✓ Authenticated request successful
  User: demo_user
  Email: demo@engineeros.io
  Roles: ['engineer']
```

### Manual Login via curl

```bash
# Login
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo@engineeros.io","password":"demo1234"}'

# Response:
# {
#   "access_token": "eyJhbGc...",
#   "token_type": "bearer",
#   "user_id": "demo_user"
# }

# Use token to make authenticated request
curl http://localhost:8000/dev/me \
  -H "Authorization: Bearer eyJhbGc..."

# Response:
# {
#   "user_id": "demo_user",
#   "email": "demo@engineeros.io",
#   "roles": ["engineer"]
# }
```

### Manual Login via Swagger UI

1. Open http://localhost:8000/docs
2. Scroll to **auth** section
3. Click "Try it out" on POST /auth/login
4. Enter:
   ```json
   {
     "email": "demo@engineeros.io",
     "password": "demo1234"
   }
   ```
5. Click "Execute"
6. Copy the `access_token` from response
7. Click green "Authorize" button at top
8. Paste: `Bearer <token>`
9. Now all endpoints will work!

## Step 5: Explore the System

### API Endpoints

**No Auth Required:**
- `GET /health` - Health check
- `GET /metrics` - Prometheus metrics

**Auth Required (test with demo credentials):**
- `GET /dev/me` - Current user info
- `GET /dev/settings` - App configuration (dev only)
- `GET /twin/{user_id}` - Engineer digital twin
- `POST /simulations` - Create simulation
- `WS /ws/simulations/{id}` - Live simulation events

### Monitoring

**Prometheus:**
- Visit http://localhost:9090
- Query: `engineeros_api_requests_total`
- See request counts by route

**Grafana:**
- Visit http://localhost:3001
- Login: admin / admin
- Add Prometheus data source (http://prometheus:9090)
- Create dashboards from metrics

**API Logs:**
```bash
# Watch API logs
docker compose logs -f api

# Or from local terminal if running manually
# Logs appear in uvicorn output
```

## Step 6: Development Workflow

### Code Changes

**Backend:**
```bash
# API auto-reloads on file changes (with --reload)
# Edit backend/app/*.py files

# Add new endpoint:
# 1. Create function in appropriate module
# 2. Add @app.post/get/etc decorator
# 3. Define request/response models
# 4. Re-export in main.py if needed
```

**Frontend:**
```bash
# Frontend hot-reloads on file changes
# Edit app/*.tsx files
```

### Database Changes

```bash
# Coming soon: Alembic migrations
# For now, reset database with:
docker compose down -v
docker compose up --build
```

### Run Tests

```bash
# Coming soon: pytest + pytest-cov
# Coming soon: jest + vitest

# Currently: Just open http://localhost:3000 and test manually
```

## Step 7: Understanding Security

### JWT Token Structure

```python
# Decoded token looks like:
{
  "user_id": "demo_user",
  "email": "demo@engineeros.io",
  "roles": ["engineer"],
  "exp": 1719000000,        # Expiration timestamp
  "iat": 1718913600         # Issued at timestamp
}
```

### Rate Limiting

Each endpoint has different limits:
- `/health` - 10 requests/minute
- `/twin/{user_id}` - 30 requests/minute
- `/simulations` - 20 requests/minute
- `/incidents/*` - 10-20 requests/minute

Try hammering an endpoint to see 429 Too Many Requests.

### Security Headers

Every response includes:
```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'...
```

Verify with:
```bash
curl -i http://localhost:8000/health | grep X-
```

## Troubleshooting

### "Connection refused" on localhost:8000

**Solution:** Start the API services
```bash
docker compose up api postgres  # If using Docker
# OR
uvicorn app.main:app --reload  # If running locally
```

### "Invalid JWT Secret Key" error

**Solution:** Generate a new secret in .env.local
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
# Update JWT_SECRET_KEY in .env.local
# Restart API
```

### "Database connection failed"

**Solution:** Ensure PostgreSQL is running
```bash
docker compose ps postgres  # Check if running
docker compose logs postgres  # Check logs
docker compose down -v       # Reset everything
docker compose up postgres   # Start fresh
```

### "Rate limited" on first few requests

**Solution:** Wait 60 seconds or check the rate limit config in `.env.local`:
```
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60
```

### Port 3000 or 8000 already in use

**Solution:** Kill the process using the port
```bash
# macOS/Linux
lsof -i :8000
kill -9 <PID>

# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

## Next Steps

1. **Read [SECURITY.md](./SECURITY.md)** - Full security architecture
2. **Review API docs** - http://localhost:8000/docs
3. **Explore the codebase** - backend/app/ structure
4. **Run AUTH_DEMO.py** - See auth flows in action
5. **Create a feature** - Add your first endpoint with auth

## Performance Tips

### Faster Docker Builds

```bash
# Don't rebuild images if nothing changed
docker compose up  # (without --build)

# Rebuild specific service only
docker compose up --build api
```

### Faster Development

Keep separate terminals:
- Terminal 1: `docker compose up postgres neo4j redis`
- Terminal 2: `uvicorn app.main:app --reload`
- Terminal 3: `npm run dev`

This is faster than rebuilding Docker images.

### Database Performance

```bash
# Connect to PostgreSQL CLI
docker compose exec postgres psql -U engineeros -d engineeros

# Or use local client
psql postgresql://engineeros:engineeros@localhost:5432/engineeros
```

## Key Files

```
.env.local              # Local secrets (NEVER commit)
.env.example            # Template for .env.local
SECURITY.md             # Security architecture & practices
README.md               # Main project documentation
AUTH_DEMO.py            # Example authentication flows
backend/
  app/
    main.py             # FastAPI app & endpoints
    auth.py             # JWT token handling
    security.py         # RBAC & auth dependencies
    config.py           # Settings/env vars
    auth_routes.py      # /auth/* endpoints
    dev_routes.py       # /dev/* endpoints
  Dockerfile            # Backend Docker image
  requirements.txt      # Python dependencies
docker-compose.yml      # Full stack orchestration
```

## Getting Help

- **API Issues?** Check http://localhost:8000/docs
- **Database Issues?** Check `docker compose logs postgres`
- **Auth Issues?** Review SECURITY.md
- **Frontend Issues?** Check browser console (F12)
- **General Help?** Read README.md

---

**Happy coding!** 🚀
