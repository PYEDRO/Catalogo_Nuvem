import { FilterParams } from "../services/api";

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
  return (
    <aside className="w-64 bg-white rounded-xl shadow-sm p-6 h-fit sticky top-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-semibold text-gray-800">Filtros</h2>
        <button onClick={onClear} className="text-sm text-indigo-600 hover:underline">
          Limpar
        </button>
      </div>

      <div className="space-y-5">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Buscar</label>
          <input
            type="text"
            value={filters.search || ""}
            onChange={(e) => onFilterChange({ search: e.target.value })}
            placeholder="Nome ou descrição..."
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Categoria</label>
          <select
            value={filters.category || ""}
            onChange={(e) => onFilterChange({ category: e.target.value || undefined })}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {CATEGORIES.map((cat) => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Faixa de Preço</label>
          <div className="flex gap-2">
            <input
              type="number"
              value={filters.min_price || ""}
              onChange={(e) =>
                onFilterChange({
                  min_price: e.target.value ? Number(e.target.value) : undefined,
                })
              }
              placeholder="Mín"
              className="w-1/2 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <input
              type="number"
              value={filters.max_price || ""}
              onChange={(e) =>
                onFilterChange({
                  max_price: e.target.value ? Number(e.target.value) : undefined,
                })
              }
              placeholder="Máx"
              className="w-1/2 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>

        <div>
          <label className="flex items-center gap-3 cursor-pointer">
            <input
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
