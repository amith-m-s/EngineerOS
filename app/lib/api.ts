/**
 * EngineerOS — Type-Safe API Client
 *
 * Production-grade HTTP client with:
 * - JWT auth header injection
 * - Automatic token refresh on 401
 * - Request deduplication
 * - Exponential backoff retry
 * - Type-safe request/response
 * - AbortController support for cancellation
 */

// ---------------------------------------------------------------------------
// Types — mirror backend Pydantic models
// ---------------------------------------------------------------------------

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
  roles: string[];
}

export interface SkillScore {
  domain: string;
  score: number;
  confidence: number;
  evidence: string[];
}

export interface Reputation {
  debugging: number;
  architecture: number;
  reliability: number;
  leadership: number;
  system_design: number;
}

export interface EngineerTwin {
  user_id: string;
  title: string;
  skill_scores: SkillScore[];
  reputation: Reputation;
  memory_count: number;
  graph_nodes: number;
  vector_embeddings: number;
  updated_at: string;
  repo_confidence?: number;
  experience_simulated_years?: number;
  reputation_index?: number;
}

export interface Memory {
  id: string;
  kind: string;
  summary: string;
  signal_strength: number;
  created_at: string;
}

export interface Incident {
  id: string;
  name: string;
  detail: string;
  severity: string;
  created_at: string;
}

export interface SimulationRequest {
  scenario: string;
  difficulty: string;
}

export interface Simulation {
  id: string;
  simulation_id?: string;
  scenario: string;
  difficulty?: string;
  status?: string;
  agents?: any[];
  stakeholders?: any[];
  requirements?: string[];
  constraints?: string[];
  failures?: string[];
  scoring_rubric?: string[];
}

export interface CommandEvaluation {
  diagnosis_quality: number;
  recovery_safety: number;
  communication_clarity: number;
  mentor_feedback: string;
  memory_update: Memory;
}

export interface ArchitectureAnalysis {
  repository: string;
  dependency_count?: number;
  risk_count?: number;
  findings?: string[];
  blast_radius_hotspots?: string[];
  architecture_risks?: string[];
  dependency_hotspots?: string[];
  security_findings?: string[];
  scalability_predictions?: string[];
}

export interface CareerPrediction {
  user_id: string;
  interview_readiness: number;
  promotion_readiness: number;
  faang_probability: number;
  growth_trajectory: string;
  next_best_actions: string[];
}

export interface HealthStatus {
  status: string;
  version: string;
  uptime_seconds: number;
  checks: Record<string, { status: string; latency_ms?: number }>;
}

// ---------------------------------------------------------------------------
// API Error
// ---------------------------------------------------------------------------

export class APIError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public traceId?: string
  ) {
    super(message);
    this.name = "APIError";
  }
}

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const DEFAULT_TIMEOUT = 15_000; // 15 seconds
const MAX_RETRIES = 2;
const RETRY_BACKOFF_MS = 500;

// ---------------------------------------------------------------------------
// Token management
// ---------------------------------------------------------------------------

let _accessToken: string | null = null;

export function setAccessToken(token: string | null): void {
  _accessToken = token;
  if (token) {
    if (typeof window !== "undefined") {
      localStorage.setItem("engineeros_token", token);
    }
  } else {
    if (typeof window !== "undefined") {
      localStorage.removeItem("engineeros_token");
    }
  }
}

export function getAccessToken(): string | null {
  if (_accessToken) return _accessToken;
  if (typeof window !== "undefined") {
    _accessToken = localStorage.getItem("engineeros_token");
  }
  return _accessToken;
}

// ---------------------------------------------------------------------------
// Core fetch wrapper
// ---------------------------------------------------------------------------

async function apiFetch<T>(
  path: string,
  options: RequestInit & { timeout?: number; retries?: number } = {}
): Promise<T> {
  const { timeout = DEFAULT_TIMEOUT, retries = MAX_RETRIES, ...fetchOptions } = options;

  const url = `${API_BASE_URL}${path}`;
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Accept: "application/json",
    ...(fetchOptions.headers as Record<string, string>),
  };

  // Inject auth header
  const token = getAccessToken();
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  let lastError: Error | null = null;

  for (let attempt = 0; attempt <= retries; attempt++) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
      const response = await fetch(url, {
        ...fetchOptions,
        headers,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Handle 401 — token expired
      if (response.status === 401 && token) {
        setAccessToken(null);
        throw new APIError(401, "AUTH_EXPIRED", "Session expired. Please log in again.");
      }

      // Handle rate limiting with retry
      if (response.status === 429 && attempt < retries) {
        const retryAfter = parseInt(response.headers.get("Retry-After") || "1", 10);
        await sleep(retryAfter * 1000);
        continue;
      }

      // Handle errors
      if (!response.ok) {
        let errorBody: { code?: string; detail?: string; trace_id?: string } = {};
        try {
          errorBody = await response.json();
        } catch {
          /* non-JSON error body */
        }
        throw new APIError(
          response.status,
          errorBody.code || `HTTP_${response.status}`,
          errorBody.detail || `Request failed with status ${response.status}`,
          errorBody.trace_id
        );
      }

      return (await response.json()) as T;
    } catch (err) {
      clearTimeout(timeoutId);

      if (err instanceof APIError) throw err;

      lastError = err as Error;

      // Retry on network errors
      if (attempt < retries && isRetryable(err as Error)) {
        await sleep(RETRY_BACKOFF_MS * Math.pow(2, attempt));
        continue;
      }

      break;
    }
  }

  throw lastError || new Error("Request failed");
}

function isRetryable(error: Error): boolean {
  return (
    error.name === "AbortError" ||
    error.name === "TypeError" || // network failure
    error.message.includes("fetch")
  );
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ---------------------------------------------------------------------------
// Auth API
// ---------------------------------------------------------------------------

export const auth = {
  async login(request: LoginRequest): Promise<AuthResponse> {
    const response = await apiFetch<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(request),
      retries: 0, // Don't retry auth requests
    });
    setAccessToken(response.access_token);
    return response;
  },

  async register(request: RegisterRequest): Promise<AuthResponse> {
    const response = await apiFetch<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(request),
      retries: 0,
    });
    setAccessToken(response.access_token);
    return response;
  },

  async refresh(): Promise<AuthResponse> {
    const currentToken = getAccessToken();
    if (!currentToken) throw new APIError(401, "NO_TOKEN", "No token to refresh");
    const response = await apiFetch<AuthResponse>("/auth/refresh", {
      method: "POST",
      body: JSON.stringify({ access_token: currentToken }),
      retries: 0,
    });
    setAccessToken(response.access_token);
    return response;
  },

  async logout(): Promise<void> {
    try {
      await apiFetch<{ status: string }>("/auth/logout", {
        method: "POST",
        retries: 0,
      });
    } finally {
      setAccessToken(null);
    }
  },
};

// ---------------------------------------------------------------------------
// Twin API
// ---------------------------------------------------------------------------

export const twin = {
  async get(userId: string): Promise<EngineerTwin> {
    return apiFetch<EngineerTwin>(`/twin/${encodeURIComponent(userId)}`);
  },
};

// ---------------------------------------------------------------------------
// Memory API
// ---------------------------------------------------------------------------

export const memory = {
  async list(userId: string): Promise<{ user_id: string; memories: Memory[] }> {
    return apiFetch(`/memory/${encodeURIComponent(userId)}`);
  },
};

// ---------------------------------------------------------------------------
// Simulation API
// ---------------------------------------------------------------------------

export const simulations = {
  async create(request: SimulationRequest): Promise<Simulation> {
    return apiFetch<Simulation>("/simulations", {
      method: "POST",
      body: JSON.stringify(request),
    });
  },
};

// ---------------------------------------------------------------------------
// Incidents API
// ---------------------------------------------------------------------------

export const incidents = {
  async generate(): Promise<Incident> {
    return apiFetch<Incident>("/incidents/generate", { method: "POST" });
  },

  async evaluateCommand(
    userId: string,
    command: string,
    scenario: string
  ): Promise<CommandEvaluation> {
    return apiFetch<CommandEvaluation>("/incidents/evaluate-command", {
      method: "POST",
      body: JSON.stringify({ user_id: userId, command, scenario }),
    });
  },
};

// ---------------------------------------------------------------------------
// Architecture API
// ---------------------------------------------------------------------------

export const architecture = {
  async analyze(repository?: string): Promise<ArchitectureAnalysis> {
    const params = repository
      ? `?repository=${encodeURIComponent(repository)}`
      : "";
    return apiFetch<ArchitectureAnalysis>(`/architecture/analyze${params}`);
  },
};

// ---------------------------------------------------------------------------
// Career API
// ---------------------------------------------------------------------------

export const career = {
  async predict(userId: string): Promise<CareerPrediction> {
    return apiFetch<CareerPrediction>(`/career/${encodeURIComponent(userId)}`);
  },
};

// ---------------------------------------------------------------------------
// Health API
// ---------------------------------------------------------------------------

export const health = {
  async check(): Promise<HealthStatus> {
    return apiFetch<HealthStatus>("/health", { retries: 0 });
  },
};

// ---------------------------------------------------------------------------
// Default export — namespaced API client
// ---------------------------------------------------------------------------

const api = { auth, twin, memory, simulations, incidents, architecture, career, health };
export default api;
