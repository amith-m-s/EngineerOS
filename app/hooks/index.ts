/**
 * EngineerOS — Custom Hooks
 *
 * Barrel export for all custom React hooks.
 */

export { useFetch, useMutation } from "./useAPI";
export type { UseFetchResult, UseMutationResult, UseFetchOptions } from "./useAPI";

export { useWebSocket } from "./useWebSocket";
export type { UseWebSocketResult, SimulationEvent, WSState } from "./useWebSocket";

export { useAuth } from "./useAuth";
export type { UseAuthResult, User } from "./useAuth";

export { useAnimatedValue, easings } from "./useAnimatedValue";
export type { UseAnimatedValueOptions } from "./useAnimatedValue";
