import { Product } from "../services/api";
import { ProductCard } from "./ProductCard";

interface CatalogGridProps {
  products: Product[];
  loading: boolean;
  error: string | null;
  isAdmin?: boolean;
  onEdit?: (product: Product) => void;
  onDelete?: (id: string) => void;
}

export function CatalogGrid({ products, loading, error, isAdmin, onEdit, onDelete }: CatalogGridProps) {
  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="bg-gray-100 rounded-xl h-72 animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-16 text-red-500">
        <p className="text-lg font-medium">Erro ao carregar produtos</p>
        <p className="text-sm mt-2">{error}</p>
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="text-center py-16 text-gray-400">
        <p className="text-5xl mb-4">🔍</p>
        <p className="text-lg font-medium">Nenhum produto encontrado</p>
        <p className="text-sm mt-2">Tente ajustar os filtros</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {products.map((product) => (
        <ProductCard
          key={product.id}
          product={product}
          isAdmin={isAdmin}
          onEdit={onEdit}
          onDelete={onDelete}
        />
      ))}
    </div>
  );
}
