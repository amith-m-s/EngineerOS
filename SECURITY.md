# Security and Architecture Documentation

## Overview

EngineerOS implements enterprise-grade security patterns to protect engineer data, prevent unauthorized access, and maintain audit trails. This document outlines security architecture, threat model, and best practices.

## Security Architecture

### 1. Authentication (JWT-based)

**Current Implementation:**
- JWT (JSON Web Tokens) with HS256 algorithm
- Token expiration: 24 hours (configurable)
- Secure password hashing with bcrypt

**Token Structure:**
```json
{
  "user_id": "engineer_123",
  "email": "engineer@example.com",
  "roles": ["engineer", "reviewer"],
  "exp": 1719000000,
  "iat": 1718913600
}
```

**Best Practices:**
- Store JWT_SECRET_KEY in secrets management (AWS Secrets Manager, HashiCorp Vault)
- Rotate secrets quarterly
- Use HTTPS for all token transmission
- Implement token refresh mechanism for long-lived sessions
- Never expose JWT in URLs or logs

**Roadmap:**
- Implement OAuth2 with Auth0/Cognito for SSO
- Add refresh token rotation
- Support OIDC for enterprise integrations

### 2. Authorization (Role-Based Access Control)

**Current Implementation:**
- Role-based access control (RBAC) decorator
- Roles assigned per user: `engineer`, `reviewer`, `admin`
- Role enforcement at endpoint level

**Example Usage:**
```python
@app.post("/admin/incidents/reset")
async def reset_incidents(
    current_user: TokenData = Depends(require_role("admin"))
):
    # Only admins can reset incidents
    pass
```

**Roles:**
- `engineer`: Read own twin, simulations; create incidents
- `reviewer`: Read all twins, approve incidents, manage runbooks
- `admin`: Full system access, user management, security policies

**Roadmap:**
- Implement Attribute-Based Access Control (ABAC)
- Fine-grained permissions per resource
- Multi-tenant isolation

### 3. API Security

**CORS (Cross-Origin Resource Sharing):**
- Whitelist origins: `http://localhost:3000`, `http://localhost:3001`
- In production: restrict to your domain only
- Max age: 600 seconds

**Rate Limiting:**
- Global: 100 requests per 60 seconds
- Health: 10 requests per minute
- Simulations: 20 requests per minute
- Incidents: 10 requests per minute

**Input Validation:**
- Pydantic models enforce type safety
- Field constraints (min, max, pattern)
- Sanitization of user inputs
- Error responses with RFC 7807 problem details

**Security Headers:**
```
X-Content-Type-Options: nosniff          # Prevent MIME sniffing
X-Frame-Options: DENY                    # Prevent clickjacking
X-XSS-Protection: 1; mode=block          # Browser XSS filter
Strict-Transport-Security: max-age=...   # Force HTTPS (prod only)
Referrer-Policy: strict-origin-...       # Control referrer info
Content-Security-Policy: default-src...  # Control resource loading
```

### 4. Data Protection

**At Rest:**
- PostgreSQL: Encrypted tablespaces (PGCRYPTO extension)
- Neo4j: Enable encryption in production
- Redis: Use Redis Sentinel with encryption
- Kafka: Enable SSL/TLS for brokers

**In Transit:**
- HTTPS/TLS 1.2+ for all API traffic
- Database connections over encrypted channels
- Message queue encryption (SSL/TLS)

**PII Handling:**
- Encrypt sensitive engineer data in database
- Mask PII in logs (use structured logging)
- GDPR compliance: Data deletion on request

**Roadmap:**
- Implement field-level encryption for sensitive attributes
- Add database backup encryption
- Implement key rotation

### 5. Secrets Management

**Current Implementation:**
- Environment variables via `.env.local` (local dev only)
- Docker Compose uses `.env` files
- Settings validated at startup via Pydantic

**Environment Variables (Required):**
- `JWT_SECRET_KEY`: JWT signing key
- `POSTGRES_PASSWORD`: Database password
- `NEO4J_PASSWORD`: Graph database password

**Best Practices:**
- ✅ Use `.env.example` as template
- ✅ Add `.env*` to `.gitignore`
- ❌ Never commit actual `.env.local` files
- ❌ Never log or print secrets
- ✅ Rotate credentials monthly

**Roadmap:**
- Implement AWS Secrets Manager integration
- Support HashiCorp Vault
- Add secret rotation automation
- Implement secret versioning

### 6. Audit Logging

**Current Implementation:**
- Structured JSON logging with timestamps
- All API requests logged with method, path, status
- Security events logged (auth failures, authorization denials)
- Exception tracking with Sentry

**Audit Trail Fields:**
```json
{
  "timestamp": "2024-06-02T12:34:56.789Z",
  "level": "WARNING",
  "logger": "app.security",
  "message": "Unauthorized access attempt",
  "user_id": "engineer_123",
  "action": "GET /admin/users",
  "status_code": 403,
  "ip_address": "192.168.1.1"
}
```

**Retention:**
- Development: 7 days
- Staging: 30 days
- Production: 90 days (minimum compliance requirement)

**Roadmap:**
- Centralized log aggregation (ELK Stack, Datadog, Splunk)
- Real-time alerting on security events
- Compliance dashboards (SOC 2, ISO 27001)

### 7. Error Handling & Exception Tracking

**Current Implementation:**
- Sentry integration for error tracking
- Structured error responses (RFC 7807)
- Validation errors with detailed field info

**Error Response Format:**
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "loc": ["body", "user_id"],
      "msg": "string required",
      "type": "value_error.missing"
    }
  ]
}
```

**Sensitive Info:**
- ✅ Stack traces hidden in production
- ✅ Database errors sanitized
- ✅ SQL queries never exposed
- ✅ File paths masked

## Threat Model

### High-Risk Threats

1. **Unauthorized Access to Engineer Data**
   - Mitigation: JWT authentication + RBAC
   - Detection: Audit logs + anomaly detection

2. **API Abuse / Denial of Service**
   - Mitigation: Rate limiting, WAF
   - Detection: Prometheus metrics, Grafana alerts

3. **Injection Attacks (SQL, NoSQL, Command)**
   - Mitigation: Parameterized queries, Pydantic validation
   - Detection: WAF, input validation errors

4. **Data Breach (Confidentiality)**
   - Mitigation: Encryption at rest + in transit
   - Detection: Secrets scanning, DLP

### Medium-Risk Threats

5. **CSRF (Cross-Site Request Forgery)**
   - Mitigation: SameSite cookies, CORS
   - Detection: Request origin validation

6. **Insecure Deserialization**
   - Mitigation: Pydantic strict mode, type validation
   - Detection: Input sanitization

7. **Hardcoded Secrets**
   - Mitigation: Secrets management, env vars
   - Detection: Secret scanning (git-secrets, Truffles)

### Low-Risk Threats

8. **Session Fixation**
   - Mitigation: Token rotation, HTTPS
   - Detection: Session validation

## Implementation Checklist

### Phase 1: Foundation (Current)
- [x] JWT authentication
- [x] RBAC middleware
- [x] Environment variables for secrets
- [x] CORS + rate limiting
- [x] Input validation
- [x] Security headers
- [x] Structured logging
- [x] Error tracking setup

### Phase 2: Hardening (Next 2 weeks)
- [ ] OAuth2/OIDC integration
- [ ] API key authentication for services
- [ ] Database encryption (PGCRYPTO)
- [ ] TLS for all connections
- [ ] Secret rotation automation
- [ ] DLP (Data Loss Prevention)

### Phase 3: Compliance (Next 4 weeks)
- [ ] SOC 2 controls
- [ ] ISO 27001 alignment
- [ ] GDPR data handling
- [ ] Compliance dashboards
- [ ] Security audit procedures

## Environment-Specific Security

### Development
```
DEBUG=true
ENVIRONMENT=development
JWT_SECRET_KEY=dev-key (short-lived)
CORS_ORIGINS=http://localhost:3000
TLS=optional
```

### Staging
```
DEBUG=false
ENVIRONMENT=staging
JWT_SECRET_KEY=staging-key (rotate weekly)
CORS_ORIGINS=https://staging.engineeros.io
TLS=required
```

### Production
```
DEBUG=false
ENVIRONMENT=production
JWT_SECRET_KEY=prod-key (rotate monthly, AWS Secrets Manager)
CORS_ORIGINS=https://engineeros.io
TLS=required (HSTS enabled)
RATE_LIMIT=stricter
AUDIT_LOG_LEVEL=DEBUG
```

## Incident Response

**If Secrets Compromised:**
1. Immediately rotate JWT_SECRET_KEY
2. Invalidate all active sessions
3. Force re-authentication for all users
4. Audit logs for suspicious activity
5. Post-incident review within 24 hours

**If API Breached:**
1. Enable rate limiting burst protection
2. Block suspicious IP ranges via WAF
3. Enable 2FA for admin accounts
4. Activate incident response plan
5. Notify affected users within 72 hours

## Security Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)

## Contact

Report security issues to: **security@engineeros.io**

Do NOT disclose security vulnerabilities publicly. We follow responsible disclosure practices.
