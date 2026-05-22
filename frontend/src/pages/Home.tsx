import { CatalogGrid } from "../components/CatalogGrid";
import { FilterPanel } from "../components/FilterPanel";
import { useCatalog } from "../hooks/useCatalog";

export function Home() {
  const { data, loading, error, filters, updateFilters, clearFilters } = useCatalog();

  return (
    /* ACESSIBILIDADE [FIX-A2 complemento]: id="main-content" para o skip link da Navbar funcionar */
    <div id="main-content" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Catálogo de Produtos</h1>
        {data && (
          /* USABILIDADE [UX-2]: indicador de resultados e paginação — contexto imediato para o usuário */
          <p className="text-gray-500 mt-1" aria-live="polite" aria-atomic="true">
            {data.total} produto{data.total !== 1 ? "s" : ""} encontrado{data.total !== 1 ? "s" : ""}
            {data.total_pages > 1 && (
              <span className="ml-2 text-gray-400 text-sm">
                — página {data.page} de {data.total_pages}
              </span>
            )}
          </p>
        )}
      </div>

      <div className="flex gap-8">
        <FilterPanel filters={filters} onFilterChange={updateFilters} onClear={clearFilters} />

        <main className="flex-1" aria-label="Resultados do catálogo">
          <CatalogGrid products={data?.items || []} loading={loading} error={error} />

          {/* USABILIDADE [UX-2] + ACESSIBILIDADE: paginação com aria-label descritivo e nav semântica */}
          {data && data.total_pages > 1 && (
            <nav aria-label="Paginação de produtos" className="mt-8">
              {/* USABILIDADE [UX-2]: texto de contexto "Página X de Y" acima dos botões */}
              <p className="text-center text-sm text-gray-500 mb-3" aria-live="polite">
                Página <strong>{data.page}</strong> de <strong>{data.total_pages}</strong>
              </p>
              <div className="flex justify-center gap-2" role="list">
                {/* Botão "Anterior" */}
                {data.page > 1 && (
                  <button
                    onClick={() => updateFilters({ page: data.page - 1 })}
                    aria-label="Ir para a página anterior"
                    className="w-10 h-10 rounded-lg text-sm font-medium transition-colors bg-white text-gray-600 border border-gray-300 hover:border-indigo-400"
                  >
                    ‹
                  </button>
                )}

                {Array.from({ length: data.total_pages }, (_, i) => i + 1).map((p) => (
                  <button
                    key={p}
                    onClick={() => updateFilters({ page: p })}
                    aria-label={`Ir para a página ${p}`}
                    aria-current={p === data.page ? "page" : undefined}
                    role="listitem"
                    className={`w-10 h-10 rounded-lg text-sm font-medium transition-colors ${
                      p === data.page
                        ? "bg-indigo-600 text-white"
                        : "bg-white text-gray-600 border border-gray-300 hover:border-indigo-400"
                    }`}
                  >
                    {p}
                  </button>
                ))}

                {/* Botão "Próximo" */}
                {data.page < data.total_pages && (
                  <button
                    onClick={() => updateFilters({ page: data.page + 1 })}
                    aria-label="Ir para a próxima página"
                    className="w-10 h-10 rounded-lg text-sm font-medium transition-colors bg-white text-gray-600 border border-gray-300 hover:border-indigo-400"
                  >
                    ›
                  </button>
                )}
              </div>
            </nav>
          )}
        </main>
      </div>
    </div>
  );
}
