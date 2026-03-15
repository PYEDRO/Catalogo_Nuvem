import { CatalogGrid } from "../components/CatalogGrid";
import { FilterPanel } from "../components/FilterPanel";
import { useCatalog } from "../hooks/useCatalog";

export function Home() {
  const { data, loading, error, filters, updateFilters, clearFilters } = useCatalog();

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Catálogo de Produtos</h1>
        {data && (
          <p className="text-gray-500 mt-1">
            {data.total} produto{data.total !== 1 ? "s" : ""} encontrado{data.total !== 1 ? "s" : ""}
          </p>
        )}
      </div>

      <div className="flex gap-8">
        <FilterPanel filters={filters} onFilterChange={updateFilters} onClear={clearFilters} />

        <main className="flex-1">
          <CatalogGrid products={data?.items || []} loading={loading} error={error} />

          {data && data.total_pages > 1 && (
            <div className="flex justify-center gap-2 mt-8">
              {Array.from({ length: data.total_pages }, (_, i) => i + 1).map((p) => (
                <button
                  key={p}
                  onClick={() => updateFilters({ page: p })}
                  className={`w-10 h-10 rounded-lg text-sm font-medium transition-colors ${
                    p === data.page
                      ? "bg-indigo-600 text-white"
                      : "bg-white text-gray-600 border border-gray-300 hover:border-indigo-400"
                  }`}
                >
                  {p}
                </button>
              ))}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
