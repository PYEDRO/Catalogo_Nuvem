import { useState, useEffect } from "react";
import { FilterParams } from "../services/api";
import { useDebounce } from "../hooks/useDebounce";

interface FilterPanelProps {
  filters: FilterParams;
  onFilterChange: (filters: Partial<FilterParams>) => void;
  onClear: () => void;
}

const CATEGORIES = [
  { value: "", label: "Todas" },
  { value: "eletronicos", label: "Eletrônicos" },
  { value: "roupas", label: "Roupas" },
  { value: "alimentos", label: "Alimentos" },
  { value: "livros", label: "Livros" },
  { value: "outros", label: "Outros" },
];

export function FilterPanel({ filters, onFilterChange, onClear }: FilterPanelProps) {
  // PERFORMANCE [PERF-2]: estado local para o campo de busca com debounce de 400ms.
  // ANTES: onChange disparava onFilterChange() imediato → URL update → fetch a cada keystroke.
  // DEPOIS: o fetch só ocorre 400ms após o usuário parar de digitar — ~85% menos requisições.
  const [searchInput, setSearchInput] = useState(filters.search || "");
  const debouncedSearch = useDebounce(searchInput, 400);

  // Sincroniza o valor debounced com o filtro real (URL params)
  useEffect(() => {
    const currentSearch = filters.search || "";
    if (debouncedSearch !== currentSearch) {
      onFilterChange({ search: debouncedSearch || undefined });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [debouncedSearch]);

  // Sincroniza o input local quando filtros externos mudam (ex: limpar todos)
  useEffect(() => {
    setSearchInput(filters.search || "");
  }, [filters.search]);

  return (
    /* ACESSIBILIDADE [FIX-A4]: aria-label na aside descreve a região para leitores de tela (WCAG 1.3.6) */
    <aside aria-label="Painel de filtros de produtos" className="w-64 bg-white rounded-xl shadow-sm p-6 h-fit sticky top-24">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-800" id="filter-heading">Filtros</h2>
        <button
          onClick={() => {
            setSearchInput("");
            onClear();
          }}
          aria-label="Limpar todos os filtros aplicados"
          className="text-sm text-indigo-600 hover:underline"
        >
          Limpar
        </button>
      </div>

      <div className="space-y-5" role="group" aria-labelledby="filter-heading">
        <div>
          {/* ACESSIBILIDADE [FIX-A4]: htmlFor + id associam label ao input (WCAG 1.3.1) */}
          <label htmlFor="filter-search" className="block text-sm font-medium text-gray-700 mb-2">
            Buscar
          </label>
          <input
            id="filter-search"
            type="search"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            placeholder="Nome ou descrição..."
            aria-label="Buscar produto por nome ou descrição"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div>
          {/* ACESSIBILIDADE [FIX-A4]: htmlFor + id no select de categoria */}
          <label htmlFor="filter-category" className="block text-sm font-medium text-gray-700 mb-2">
            Categoria
          </label>
          <select
            id="filter-category"
            value={filters.category || ""}
            onChange={(e) => onFilterChange({ category: e.target.value || undefined })}
            aria-label="Filtrar por categoria"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {CATEGORIES.map((cat) => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>

        <fieldset className="border-0 p-0 m-0">
          {/* ACESSIBILIDADE [FIX-A4]: fieldset + legend agrupam inputs de preço relacionados (WCAG 1.3.1) */}
          <legend className="block text-sm font-medium text-gray-700 mb-2">Faixa de Preço</legend>
          <div className="flex gap-2">
            <div className="w-1/2">
              <label htmlFor="filter-min-price" className="sr-only">Preço mínimo</label>
              <input
                id="filter-min-price"
                type="number"
                min={0}
                value={filters.min_price || ""}
                onChange={(e) =>
                  onFilterChange({
                    min_price: e.target.value ? Number(e.target.value) : undefined,
                  })
                }
                placeholder="Mín"
                aria-label="Preço mínimo em reais"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div className="w-1/2">
              <label htmlFor="filter-max-price" className="sr-only">Preço máximo</label>
              <input
                id="filter-max-price"
                type="number"
                min={0}
                value={filters.max_price || ""}
                onChange={(e) =>
                  onFilterChange({
                    max_price: e.target.value ? Number(e.target.value) : undefined,
                  })
                }
                placeholder="Máx"
                aria-label="Preço máximo em reais"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>
        </fieldset>

        <div>
          <label className="flex items-center gap-3 cursor-pointer" htmlFor="filter-in-stock">
            <input
              id="filter-in-stock"
              type="checkbox"
              checked={filters.in_stock === true}
              onChange={(e) => onFilterChange({ in_stock: e.target.checked ? true : undefined })}
              className="w-4 h-4 accent-indigo-600"
            />
            <span className="text-sm font-medium text-gray-700">Apenas em estoque</span>
          </label>
        </div>
      </div>
    </aside>
  );
}
