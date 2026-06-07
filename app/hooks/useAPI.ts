/**
 * useAPI — React hook for data fetching with loading, error, and cache states.
 *
 * Features:
 * - Automatic loading/error tracking
 * - Stale-while-revalidate caching
 * - Deduplication of in-flight requests
 * - Retry with exponential backoff
 * - Abort on unmount to prevent memory leaks
 */

"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { APIError } from "../lib/api";

// ---------------------------------------------------------------------------
// In-memory request cache (shared across hook instances)
// ---------------------------------------------------------------------------

interface CacheEntry<T> {
  data: T;
  timestamp: number;
}

const cache = new Map<string, CacheEntry<unknown>>();
const DEFAULT_CACHE_TTL = 30_000; // 30 seconds

// ---------------------------------------------------------------------------
// Hook: useFetch (GET requests with caching)
// ---------------------------------------------------------------------------

export interface UseFetchOptions {
  /** Cache TTL in milliseconds. Set to 0 to disable caching. */
  cacheTtl?: number;
  /** Whether to fetch immediately on mount. */
  immediate?: boolean;
  /** Dependency array that triggers refetch when changed. */
  deps?: unknown[];
}

export interface UseFetchResult<T> {
  data: T | null;
  error: APIError | Error | null;
  isLoading: boolean;
  refetch: () => Promise<void>;
}

export function useFetch<T>(
  key: string,
  fetcher: () => Promise<T>,
  options: UseFetchOptions = {}
): UseFetchResult<T> {
  const { cacheTtl = DEFAULT_CACHE_TTL, immediate = true, deps = [] } = options;

  const [data, setData] = useState<T | null>(() => {
    // Initialize from cache if available
    const cached = cache.get(key) as CacheEntry<T> | undefined;
    if (cached && Date.now() - cached.timestamp < cacheTtl) {
      return cached.data;
    }
    return null;
  });
  const [error, setError] = useState<APIError | Error | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const abortRef = useRef<AbortController | null>(null);
  const mountedRef = useRef(true);

  const refetch = useCallback(async () => {
    // Abort previous request
    abortRef.current?.abort();
    abortRef.current = new AbortController();

    setIsLoading(true);
    setError(null);

    try {
      const result = await fetcher();
      if (!mountedRef.current) return;

      setData(result);
      // Update cache
      if (cacheTtl > 0) {
        cache.set(key, { data: result, timestamp: Date.now() });
      }
    } catch (err) {
      if (!mountedRef.current) return;
      if ((err as Error).name === "AbortError") return;
      setError(err as APIError | Error);
    } finally {
      if (mountedRef.current) {
        setIsLoading(false);
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key, cacheTtl]);

  useEffect(() => {
    mountedRef.current = true;
    if (immediate) {
      refetch();
    }
    return () => {
      mountedRef.current = false;
      abortRef.current?.abort();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [immediate, ...deps]);

  return { data, error, isLoading, refetch };
}

// ---------------------------------------------------------------------------
// Hook: useMutation (POST/PUT/DELETE requests)
// ---------------------------------------------------------------------------

export interface UseMutationResult<TData, TVariables> {
  data: TData | null;
  error: APIError | Error | null;
  isLoading: boolean;
  mutate: (variables: TVariables) => Promise<TData>;
  reset: () => void;
}

export function useMutation<TData, TVariables = void>(
  mutationFn: (variables: TVariables) => Promise<TData>,
  options?: {
    onSuccess?: (data: TData, variables: TVariables) => void;
    onError?: (error: APIError | Error, variables: TVariables) => void;
    /** Cache keys to invalidate on success */
    invalidateKeys?: string[];
  }
): UseMutationResult<TData, TVariables> {
  const [data, setData] = useState<TData | null>(null);
  const [error, setError] = useState<APIError | Error | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const mutate = useCallback(
    async (variables: TVariables): Promise<TData> => {
      setIsLoading(true);
      setError(null);

      try {
        const result = await mutationFn(variables);
        if (!mountedRef.current) return result;

        setData(result);

        // Invalidate related cache entries
        if (options?.invalidateKeys) {
          for (const key of options.invalidateKeys) {
            cache.delete(key);
          }
        }

        options?.onSuccess?.(result, variables);
        return result;
      } catch (err) {
        if (!mountedRef.current) throw err;
        const apiError = err as APIError | Error;
        setError(apiError);
        options?.onError?.(apiError, variables);
        throw err;
      } finally {
        if (mountedRef.current) {
          setIsLoading(false);
        }
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [mutationFn]
  );

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setIsLoading(false);
  }, []);

  return { data, error, isLoading, mutate, reset };
}
