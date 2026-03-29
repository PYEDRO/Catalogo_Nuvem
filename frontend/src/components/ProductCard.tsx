import { Product } from "../services/api";

interface ProductCardProps {
  product: Product;
  onEdit?: (product: Product) => void;
  onDelete?: (id: string) => void;
  isAdmin?: boolean;
}

export function ProductCard({ product, onEdit, onDelete, isAdmin }: ProductCardProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow overflow-hidden border border-gray-100">
      {product.image_url ? (
        <img src={product.image_url} alt={product.name} className="w-full h-48 object-cover" />
      ) : (
        <div className="w-full h-48 bg-gradient-to-br from-indigo-100 to-purple-100 flex items-center justify-center">
          <span className="text-4xl">📦</span>
        </div>
      )}

      <div className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-semibold text-gray-900 text-base leading-tight line-clamp-2">{product.name}</h3>
          <span
            className={`ml-2 text-xs px-2 py-1 rounded-full shrink-0 ${
              product.in_stock ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"
            }`}
          >
            {product.in_stock ? "Em estoque" : "Esgotado"}
          </span>
        </div>

        <p className="text-gray-500 text-sm mb-3 line-clamp-2">{product.description}</p>

        <div className="flex items-center justify-between">
          <span className="text-indigo-600 font-bold text-lg">R$ {product.price.toFixed(2)}</span>
          <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded-full capitalize">
            {product.category}
          </span>
        </div>

        {product.tags && product.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-3">
            {product.tags.map((tag) => (
              <span key={tag} className="text-xs bg-indigo-50 text-indigo-600 px-2 py-0.5 rounded-full">
                #{tag}
              </span>
            ))}
          </div>
        )}

        {isAdmin && (
          <div className="flex gap-2 mt-4">
            <button
              onClick={() => onEdit?.(product)}
              className="flex-1 text-sm bg-indigo-50 text-indigo-700 py-2 rounded-lg hover:bg-indigo-100 transition-colors"
            >
              Editar
            </button>
            <button
              onClick={() => onDelete?.(product.id)}
              className="flex-1 text-sm bg-red-50 text-red-700 py-2 rounded-lg hover:bg-red-100 transition-colors"
            >
              Excluir
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
