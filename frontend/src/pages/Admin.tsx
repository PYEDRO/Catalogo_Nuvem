import { useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { catalogApi, Product } from "../services/api";
import { ProductForm } from "../components/ProductForm";

type ModalState =
  | { mode: "closed" }
  | { mode: "create" }
  | { mode: "edit"; product: Product };

export function Admin() {
  const { user } = useAuth();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [modal, setModal] = useState<ModalState>({ mode: "closed" });
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  async function fetchProducts() {
    setLoading(true);
    setError(null);
    try {
      const data = await catalogApi.getProducts({ page_size: 100 });
      setProducts(data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao carregar produtos");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { fetchProducts(); }, []);

  function showSuccess(msg: string) {
    setSuccessMsg(msg);
    setTimeout(() => setSuccessMsg(null), 3000);
  }

  async function handleDelete(id: string) {
    if (!confirm("Confirma exclusão do produto?")) return;
    setDeletingId(id);
    try {
      await catalogApi.deleteProduct(id);
      setProducts((prev) => prev.filter((p) => p.id !== id));
      showSuccess("Produto excluído com sucesso.");
    } catch (err) {
      alert(err instanceof Error ? err.message : "Erro ao excluir");
    } finally {
      setDeletingId(null);
    }
  }

  async function handleFormSubmit(data: Omit<Product, "id" | "created_at">) {
    try {
      if (modal.mode === "create") {
        const created = await catalogApi.createProduct(data);
        setProducts((prev) => [created, ...prev]);
        showSuccess("Produto criado com sucesso!");
      } else if (modal.mode === "edit") {
        const updated = await catalogApi.updateProduct(modal.product.id, data);
        setProducts((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
        showSuccess("Produto atualizado com sucesso!");
      }
      setModal({ mode: "closed" });
    } catch (err) {
      throw err; // re-throw para o form exibir o erro
    }
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Painel Administrativo</h1>
          <p className="text-gray-500 mt-1 text-sm">
            {user?.email} · {products.length} produto{products.length !== 1 ? "s" : ""} cadastrado{products.length !== 1 ? "s" : ""}
          </p>
        </div>
        <button
          onClick={() => setModal({ mode: "create" })}
          className="flex items-center gap-2 bg-indigo-600 text-white px-5 py-2.5 rounded-xl font-medium hover:bg-indigo-700 transition-colors shadow-sm"
        >
          <span className="text-lg leading-none">+</span>
          Novo Produto
        </button>
      </div>

      {/* Toast de sucesso */}
      {successMsg && (
        <div className="mb-6 bg-green-50 border border-green-200 text-green-700 text-sm rounded-xl px-4 py-3 flex items-center gap-2">
          <span>✅</span> {successMsg}
        </div>
      )}

      {/* Erro */}
      {error && (
        <div className="mb-6 bg-red-50 border border-red-200 text-red-700 text-sm rounded-xl px-4 py-3">
          ❌ {error}
        </div>
      )}

      {/* Loading skeleton */}
      {loading && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="bg-gray-100 rounded-xl h-40 animate-pulse" />
          ))}
        </div>
      )}

      {/* Tabela de produtos */}
      {!loading && products.length === 0 && !error && (
        <div className="text-center py-20 text-gray-400">
          <p className="text-5xl mb-4">📦</p>
          <p className="text-lg font-medium">Nenhum produto cadastrado</p>
          <p className="text-sm mt-1">Clique em "Novo Produto" para começar</p>
        </div>
      )}

      {!loading && products.length > 0 && (
        <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b border-gray-100">
              <tr>
                <th className="text-left px-4 py-3 text-gray-500 font-medium">Produto</th>
                <th className="text-left px-4 py-3 text-gray-500 font-medium">Categoria</th>
                <th className="text-left px-4 py-3 text-gray-500 font-medium">Preço</th>
                <th className="text-left px-4 py-3 text-gray-500 font-medium">Estoque</th>
                <th className="text-right px-4 py-3 text-gray-500 font-medium">Ações</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-50">
              {products.map((product) => (
                <tr key={product.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      {product.image_url ? (
                        <img
                          src={product.image_url}
                          alt={product.name}
                          className="w-10 h-10 rounded-lg object-cover border border-gray-100"
                        />
                      ) : (
                        <div className="w-10 h-10 rounded-lg bg-indigo-50 flex items-center justify-center text-lg">
                          📦
                        </div>
                      )}
                      <div>
                        <p className="font-medium text-gray-900">{product.name}</p>
                        <p className="text-xs text-gray-400 line-clamp-1 max-w-xs">{product.description}</p>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <span className="bg-gray-100 text-gray-600 px-2 py-0.5 rounded-full text-xs capitalize">
                      {product.category}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-medium text-gray-900">
                    R$ {product.price.toFixed(2)}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                        product.in_stock
                          ? "bg-green-100 text-green-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {product.in_stock ? "Em estoque" : "Esgotado"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => setModal({ mode: "edit", product })}
                        className="text-xs bg-indigo-50 text-indigo-700 px-3 py-1.5 rounded-lg hover:bg-indigo-100 transition-colors"
                      >
                        Editar
                      </button>
                      <button
                        onClick={() => handleDelete(product.id)}
                        disabled={deletingId === product.id}
                        className="text-xs bg-red-50 text-red-700 px-3 py-1.5 rounded-lg hover:bg-red-100 transition-colors disabled:opacity-50"
                      >
                        {deletingId === product.id ? "..." : "Excluir"}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal */}
      {modal.mode !== "closed" && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between px-6 pt-6 pb-4 border-b border-gray-100">
              <h2 className="text-lg font-bold text-gray-900">
                {modal.mode === "create" ? "Novo Produto" : "Editar Produto"}
              </h2>
              <button
                onClick={() => setModal({ mode: "closed" })}
                className="text-gray-400 hover:text-gray-600 text-xl leading-none"
              >
                ✕
              </button>
            </div>
            <div className="px-6 py-5">
              <ProductForm
                initialData={modal.mode === "edit" ? modal.product : undefined}
                onSubmit={handleFormSubmit}
                onCancel={() => setModal({ mode: "closed" })}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
