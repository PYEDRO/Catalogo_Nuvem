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
      /* ACESSIBILIDADE [FIX-A3]: role="status" + aria-busy="true" anuncia estado de carregamento
         para leitores de tela. aria-label descreve o que está sendo carregado (WCAG 4.1.3). */
      <div
        role="status"
        aria-busy="true"
        aria-label="Carregando produtos..."
        className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6"
      >
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="bg-gray-100 rounded-xl h-72 animate-pulse" aria-hidden="true" />
        ))}
        <span className="sr-only">Carregando produtos, aguarde...</span>
      </div>
    );
  }

  if (error) {
    return (
      /* ACESSIBILIDADE [FIX-A3]: role="alert" anuncia erros imediatamente para leitores de tela (WCAG 4.1.3) */
      <div role="alert" aria-live="assertive" className="text-center py-16 text-red-500">
        <p className="text-lg font-medium">Erro ao carregar produtos</p>
        <p className="text-sm mt-2">{error}</p>
      </div>
    );
  }

  if (products.length === 0) {
    return (
      <div className="text-center py-16 text-gray-400" role="status" aria-label="Nenhum produto encontrado">
        {/* aria-hidden no emoji — puramente decorativo */}
        <p className="text-5xl mb-4" aria-hidden="true">🔍</p>
        <p className="text-lg font-medium">Nenhum produto encontrado</p>
        <p className="text-sm mt-2">Tente ajustar os filtros</p>
      </div>
    );
  }

  return (
    /* ACESSIBILIDADE [FIX-A3]: role="list" explícito para grid de produtos — melhora semântica
       para tecnologias assistivas que podem ignorar grid CSS como lista (WCAG 1.3.1) */
    <ul
      role="list"
      aria-label="Lista de produtos"
      className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 list-none p-0 m-0"
    >
      {products.map((product) => (
        <li key={product.id}>
          <ProductCard
            product={product}
            isAdmin={isAdmin}
            onEdit={onEdit}
            onDelete={onDelete}
          />
        </li>
      ))}
    </ul>
  );
}
