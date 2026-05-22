import { useState, useRef, ChangeEvent } from "react";
import { Product } from "../services/api";
import { catalogApi } from "../services/api";

type ProductFormData = Omit<Product, "id" | "created_at">;

interface ProductFormProps {
  initialData?: Product;
  onSubmit: (data: ProductFormData) => Promise<void>;
  onCancel: () => void;
}

const CATEGORIES = ["eletronicos", "roupas", "alimentos", "livros", "outros"] as const;

const EMPTY_FORM: ProductFormData = {
  name: "",
  description: "",
  price: 0,
  category: "eletronicos",
  tags: [],
  in_stock: true,
  image_url: "",
};

export function ProductForm({ initialData, onSubmit, onCancel }: ProductFormProps) {
  const [form, setForm] = useState<ProductFormData>(
    initialData
      ? {
          name: initialData.name,
          description: initialData.description,
          price: initialData.price,
          category: initialData.category,
          tags: initialData.tags,
          in_stock: initialData.in_stock,
          image_url: initialData.image_url || "",
        }
      : EMPTY_FORM
  );

  const [tagInput, setTagInput]       = useState("");
  const [imageFile, setImageFile]     = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string>(initialData?.image_url || "");
  const [uploading, setUploading]     = useState(false);
  const [submitting, setSubmitting]   = useState(false);
  const [error, setError]             = useState<string | null>(null);
  const fileRef                       = useRef<HTMLInputElement>(null);

  function handleField<K extends keyof ProductFormData>(key: K, value: ProductFormData[K]) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    const allowed = ["image/jpeg", "image/png", "image/webp"];
    if (!allowed.includes(file.type)) {
      setError("Formato inválido. Use JPG, PNG ou WebP.");
      return;
    }
    if (file.size > 5 * 1024 * 1024) {
      setError("Imagem deve ter no máximo 5MB.");
      return;
    }

    setError(null);
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  }

  function addTag() {
    const tag = tagInput.trim().toLowerCase();
    if (tag && !form.tags.includes(tag)) {
      handleField("tags", [...form.tags, tag]);
    }
    setTagInput("");
  }

  function removeTag(tag: string) {
    handleField("tags", form.tags.filter((t) => t !== tag));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setSubmitting(true);

    try {
      let finalImageUrl = form.image_url;

      // Se há arquivo novo, faz upload primeiro
      if (imageFile) {
        setUploading(true);
        try {
          finalImageUrl = await catalogApi.uploadImage(imageFile);
        } finally {
          setUploading(false);
        }
      }

      await onSubmit({ ...form, image_url: finalImageUrl });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Erro ao salvar produto");
    } finally {
      setSubmitting(false);
    }
  }

  const isLoading = uploading || submitting;

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
          ❌ {error}
        </div>
      )}

      {/* Imagem */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">Imagem do Produto</label>
        <div
          onClick={() => fileRef.current?.click()}
          className="relative border-2 border-dashed border-gray-200 rounded-xl overflow-hidden cursor-pointer hover:border-indigo-400 transition-colors group"
          style={{ height: 160 }}
        >
          {imagePreview ? (
            <>
              <img src={imagePreview} alt="preview" className="w-full h-full object-cover" />
              <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                <span className="text-white text-sm font-medium">Trocar imagem</span>
              </div>
            </>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-gray-400 gap-2">
              <span className="text-3xl">🖼️</span>
              <span className="text-sm">Clique para selecionar</span>
              <span className="text-xs">JPG, PNG ou WebP · máx. 5MB</span>
            </div>
          )}
        </div>
        <input
          ref={fileRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={handleFileChange}
          className="hidden"
        />
        {/* Fallback: URL externa */}
        <input
          type="url"
          value={form.image_url}
          onChange={(e) => {
            handleField("image_url", e.target.value);
            if (e.target.value) setImagePreview(e.target.value);
          }}
          placeholder="Ou cole uma URL de imagem externa"
          className="mt-2 w-full border border-gray-200 rounded-lg px-3 py-2 text-sm text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Nome */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
        <input
          type="text"
          value={form.name}
          onChange={(e) => handleField("name", e.target.value)}
          required
          placeholder="Ex: Tênis Esportivo"
          className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
        />
      </div>

      {/* Descrição */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Descrição *</label>
        <textarea
          value={form.description}
          onChange={(e) => handleField("description", e.target.value)}
          required
          rows={3}
          placeholder="Descreva o produto..."
          className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
        />
      </div>

      {/* Preço + Categoria */}
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Preço (R$) *</label>
          <input
            type="number"
            min="0"
            step="0.01"
            value={form.price}
            onChange={(e) => handleField("price", parseFloat(e.target.value) || 0)}
            required
            className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Categoria *</label>
          <select
            value={form.category}
            onChange={(e) => handleField("category", e.target.value)}
            className="w-full border border-gray-300 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Tags */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
        <div className="flex gap-2 mb-2">
          <input
            type="text"
            value={tagInput}
            onChange={(e) => setTagInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") { e.preventDefault(); addTag(); } }}
            placeholder="Digite uma tag e pressione Enter"
            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
          <button
            type="button"
            onClick={addTag}
            className="bg-gray-100 text-gray-700 px-3 py-2 rounded-lg text-sm hover:bg-gray-200 transition-colors"
          >
            Adicionar
          </button>
        </div>
        {form.tags.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {form.tags.map((tag) => (
              <span
                key={tag}
                className="flex items-center gap-1 bg-indigo-50 text-indigo-700 text-xs px-2 py-1 rounded-full"
              >
                #{tag}
                <button
                  type="button"
                  onClick={() => removeTag(tag)}
                  className="hover:text-red-500 leading-none"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        )}
      </div>

      {/* Em estoque */}
      <div className="flex items-center gap-3">
        <input
          type="checkbox"
          id="in_stock"
          checked={form.in_stock}
          onChange={(e) => handleField("in_stock", e.target.checked)}
          className="w-4 h-4 accent-indigo-600"
        />
        <label htmlFor="in_stock" className="text-sm font-medium text-gray-700 cursor-pointer">
          Produto em estoque
        </label>
      </div>

      {/* Ações */}
      <div className="flex gap-3 pt-2 border-t border-gray-100">
        <button
          type="button"
          onClick={onCancel}
          disabled={isLoading}
          className="flex-1 border border-gray-300 text-gray-700 py-2.5 rounded-xl text-sm font-medium hover:bg-gray-50 transition-colors disabled:opacity-50"
        >
          Cancelar
        </button>
        <button
          type="submit"
          disabled={isLoading}
          className="flex-1 bg-indigo-600 text-white py-2.5 rounded-xl text-sm font-medium hover:bg-indigo-700 transition-colors disabled:opacity-60 flex items-center justify-center gap-2"
        >
          {uploading && <span className="animate-spin">⏳</span>}
          {uploading ? "Enviando imagem..." : submitting ? "Salvando..." : "Salvar Produto"}
        </button>
      </div>
    </form>
  );
}
