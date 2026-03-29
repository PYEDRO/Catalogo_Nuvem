import { useState, useEffect, useCallback } from "react";
import { catalogApi, PaginatedResponse, FilterParams } from "../services/api";
import { useSearchParams } from "react-router-dom";

export function useCatalog() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [data, setData] = useState<PaginatedResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const getFiltersFromURL = (): FilterParams => ({
    category: searchParams.get("category") || undefined,
    min_price: searchParams.get("min_price")
      ? Number(searchParams.get("min_price"))
      : undefined,
    max_price: searchParams.get("max_price")
      ? Number(searchParams.get("max_price"))
      : undefined,
    in_stock:
      searchParams.get("in_stock") === "true"
        ? true
        : searchParams.get("in_stock") === "false"
        ? false
        : undefined,
    search: searchParams.get("search") || undefined,
    page: searchParams.get("page") ? Number(searchParams.get("page")) : 1,
    page_size: 12,
  });

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const filters = getFiltersFromURL();
      const result = await catalogApi.getProducts(filters);
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao buscar produtos");
    } finally {
      setLoading(false);
    }
  }, [searchParams]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  const updateFilters = (newFilters: Partial<FilterParams>) => {
    const current = Object.fromEntries(searchParams.entries());
    const updated = { ...current } as Record<string, string>;

    Object.entries(newFilters).forEach(([key, value]) => {
      if (value === undefined || value === "") {
        delete updated[key];
      } else {
        updated[key] = String(value);
      }
    });

    updated.page = "1";
    setSearchParams(updated);
  };

  const clearFilters = () => {
    setSearchParams({});
  };

  return {
    data,
    loading,
    error,
    filters: getFiltersFromURL(),
    updateFilters,
    clearFilters,
    refetch: fetchProducts,
  };
}
