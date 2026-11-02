import { useState, useEffect } from 'react';

/**
 * Custom hook to debounce rapidly changing state (e.g. search input).
 * Prevents redundant network queries during fast typing.
 *
 * @param {any} value Value to debounce
 * @param {number} delay Delay in milliseconds (default: 300ms)
 * @returns {any} Debounced value
 */
export function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

export default useDebounce;

