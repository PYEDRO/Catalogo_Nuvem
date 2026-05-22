// PERFORMANCE [PERF-2]: Hook de debounce para atrasar chamadas à API durante digitação.
//
// ANTES: cada keystroke no campo de busca disparava imediatamente uma atualização na URL,
//        que triggava um novo fetch à API — até 10-15 requests por palavra digitada.
// DEPOIS: o valor só é propagado após `delay` ms sem novas entradas (padrão: 400ms).
//         Redução estimada de requisições: ~85% em uso normal de busca.

import { useState, useEffect } from "react";

export function useDebounce<T>(value: T, delay: number = 400): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    // Limpa o timer anterior se o value mudar antes do delay expirar
    return () => clearTimeout(timer);
  }, [value, delay]);

  return debouncedValue;
}
