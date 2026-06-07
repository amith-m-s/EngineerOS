/**
 * useAnimatedValue — Spring-based number animation hook.
 *
 * Smoothly animates between numeric values using requestAnimationFrame
 * with configurable easing. Perfect for KPI counters, progress bars,
 * and score displays that feel alive.
 */

"use client";

import { useEffect, useRef, useState } from "react";

export interface UseAnimatedValueOptions {
  /** Animation duration in ms. Default: 800 */
  duration?: number;
  /** Easing function. Default: easeOutExpo */
  easing?: (t: number) => number;
  /** Decimal places to round to. Default: 0 */
  decimals?: number;
}

// Easing functions
export const easings = {
  linear: (t: number) => t,
  easeOutExpo: (t: number) => (t === 1 ? 1 : 1 - Math.pow(2, -10 * t)),
  easeOutCubic: (t: number) => 1 - Math.pow(1 - t, 3),
  easeInOutCubic: (t: number) =>
    t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
  spring: (t: number) => {
    const c4 = (2 * Math.PI) / 3;
    return t === 0
      ? 0
      : t === 1
        ? 1
        : Math.pow(2, -10 * t) * Math.sin((t * 10 - 0.75) * c4) + 1;
  },
};

export function useAnimatedValue(
  targetValue: number,
  options: UseAnimatedValueOptions = {}
): number {
  const {
    duration = 800,
    easing = easings.easeOutExpo,
    decimals = 0,
  } = options;

  const [displayValue, setDisplayValue] = useState(targetValue);
  const startValueRef = useRef(targetValue);
  const frameRef = useRef<number | null>(null);

  useEffect(() => {
    const startValue = startValueRef.current;
    const delta = targetValue - startValue;

    if (Math.abs(delta) < 0.001) {
      setDisplayValue(targetValue);
      startValueRef.current = targetValue;
      return;
    }

    const startTime = performance.now();

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const easedProgress = easing(progress);

      const current = startValue + delta * easedProgress;
      const factor = Math.pow(10, decimals);
      setDisplayValue(Math.round(current * factor) / factor);

      if (progress < 1) {
        frameRef.current = requestAnimationFrame(animate);
      } else {
        startValueRef.current = targetValue;
      }
    };

    frameRef.current = requestAnimationFrame(animate);

    return () => {
      if (frameRef.current !== null) {
        cancelAnimationFrame(frameRef.current);
      }
    };
  }, [targetValue, duration, easing, decimals]);

  return displayValue;
}
