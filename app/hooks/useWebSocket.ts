/**
 * useWebSocket — Resilient WebSocket hook for real-time simulation events.
 *
 * Features:
 * - Auto-reconnect with exponential backoff (up to 5 retries)
 * - Connection state tracking (connecting, open, closed, error)
 * - Type-safe message handling
 * - Heartbeat / ping-pong keep-alive
 * - Clean disconnect on unmount
 */

"use client";

import { useCallback, useEffect, useRef, useState } from "react";

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type WSState = "idle" | "connecting" | "open" | "closed" | "error";

export interface SimulationEvent {
  simulation_id: string;
  type: "agent" | "metric" | "mentor" | "system";
  role?: string;
  name?: string;
  value?: string;
  message?: string;
}

export interface UseWebSocketOptions {
  /** Auto-connect on mount. Default: false */
  autoConnect?: boolean;
  /** Maximum reconnect attempts. Default: 5 */
  maxRetries?: number;
  /** Base reconnect delay in ms. Default: 1000 */
  reconnectDelay?: number;
  /** Heartbeat interval in ms. Default: 30000 */
  heartbeatInterval?: number;
  /** Callback when a message is received */
  onMessage?: (event: SimulationEvent) => void;
  /** Callback when connection opens */
  onOpen?: () => void;
  /** Callback when connection closes */
  onClose?: () => void;
  /** Callback on error */
  onError?: (error: Event) => void;
}

export interface UseWebSocketResult {
  state: WSState;
  lastEvent: SimulationEvent | null;
  events: SimulationEvent[];
  connect: (simulationId: string) => void;
  disconnect: () => void;
  send: (data: unknown) => void;
  clearEvents: () => void;
}

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

const WS_BASE_URL =
  process.env.NEXT_PUBLIC_WS_URL || "ws://127.0.0.1:8000";

// ---------------------------------------------------------------------------
// Hook
// ---------------------------------------------------------------------------

export function useWebSocket(
  options: UseWebSocketOptions = {}
): UseWebSocketResult {
  const {
    maxRetries = 5,
    reconnectDelay = 1000,
    heartbeatInterval = 30000,
    onMessage,
    onOpen,
    onClose,
    onError,
  } = options;

  const [state, setState] = useState<WSState>("idle");
  const [lastEvent, setLastEvent] = useState<SimulationEvent | null>(null);
  const [events, setEvents] = useState<SimulationEvent[]>([]);

  const wsRef = useRef<WebSocket | null>(null);
  const retriesRef = useRef(0);
  const heartbeatRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const mountedRef = useRef(true);
  const simulationIdRef = useRef<string | null>(null);

  // Store latest callbacks in a mutable ref to keep connect/disconnect stable
  const callbacksRef = useRef({ onMessage, onOpen, onClose, onError });
  useEffect(() => {
    callbacksRef.current = { onMessage, onOpen, onClose, onError };
  }, [onMessage, onOpen, onClose, onError]);

  // ---- Cleanup helpers ----

  const clearHeartbeat = useCallback(() => {
    if (heartbeatRef.current) {
      clearInterval(heartbeatRef.current);
      heartbeatRef.current = null;
    }
  }, []);

  const cleanup = useCallback(() => {
    clearHeartbeat();
    if (wsRef.current) {
      wsRef.current.onopen = null;
      wsRef.current.onmessage = null;
      wsRef.current.onerror = null;
      wsRef.current.onclose = null;
      if (
        wsRef.current.readyState === WebSocket.OPEN ||
        wsRef.current.readyState === WebSocket.CONNECTING
      ) {
        wsRef.current.close(1000, "Client disconnect");
      }
      wsRef.current = null;
    }
  }, [clearHeartbeat]);

  // ---- Connect ----

  const connect = useCallback(
    (simulationId: string) => {
      cleanup();
      simulationIdRef.current = simulationId;
      retriesRef.current = 0;

      const doConnect = () => {
        if (!mountedRef.current) return;

        setState("connecting");
        const url = `${WS_BASE_URL}/ws/simulations/${encodeURIComponent(simulationId)}`;
        const ws = new WebSocket(url);
        wsRef.current = ws;

        ws.onopen = () => {
          if (!mountedRef.current) return;
          setState("open");
          retriesRef.current = 0;
          callbacksRef.current.onOpen?.();

          // Start heartbeat
          heartbeatRef.current = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
              ws.send(JSON.stringify({ type: "ping" }));
            }
          }, heartbeatInterval);
        };

        ws.onmessage = (msgEvent) => {
          if (!mountedRef.current) return;
          try {
            const data = JSON.parse(msgEvent.data) as SimulationEvent;
            setLastEvent(data);
            setEvents((prev) => [...prev, data].slice(-100)); // Keep last 100
            callbacksRef.current.onMessage?.(data);
          } catch {
            console.warn("[WS] Failed to parse message:", msgEvent.data);
          }
        };

        ws.onerror = (err) => {
          if (!mountedRef.current) return;
          setState("error");
          callbacksRef.current.onError?.(err);
        };

        ws.onclose = (closeEvent) => {
          if (!mountedRef.current) return;
          clearHeartbeat();
          setState("closed");
          callbacksRef.current.onClose?.();

          // Auto-reconnect on abnormal closure
          if (
            closeEvent.code !== 1000 &&
            retriesRef.current < maxRetries &&
            simulationIdRef.current
          ) {
            retriesRef.current += 1;
            const delay = reconnectDelay * Math.pow(2, retriesRef.current - 1);
            console.info(
              `[WS] Reconnecting in ${delay}ms (attempt ${retriesRef.current}/${maxRetries})`
            );
            setTimeout(doConnect, delay);
          }
        };
      };

      doConnect();
    },
    [cleanup, clearHeartbeat, heartbeatInterval, maxRetries, reconnectDelay]
  );

  // ---- Disconnect ----

  const disconnect = useCallback(() => {
    simulationIdRef.current = null;
    cleanup();
    setState("idle");
  }, [cleanup]);

  // ---- Send ----

  const send = useCallback((data: unknown) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(typeof data === "string" ? data : JSON.stringify(data));
    } else {
      console.warn("[WS] Cannot send — socket is not open");
    }
  }, []);

  // ---- Clear events ----

  const clearEvents = useCallback(() => {
    setEvents([]);
    setLastEvent(null);
  }, []);

  // ---- Cleanup on unmount ----

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
      cleanup();
    };
  }, [cleanup]);

  return { state, lastEvent, events, connect, disconnect, send, clearEvents };
}
