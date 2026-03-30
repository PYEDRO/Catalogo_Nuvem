import axios from "axios";
import { auth } from "../config/firebase";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
  timeout: 10000,
});

api.interceptors.request.use(async (config) => {
  const user = auth.currentUser;
  if (user) {
    const token = await user.getIdToken();
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message = error.response?.data?.detail || "Ocorreu um erro inesperado";
    return Promise.reject(new Error(message));
  }
);

export interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  category: string;
  tags: string[];
  in_stock: boolean;
  image_url?: string;
  created_at?: string;
}

export interface PaginatedResponse {
  items: Product[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface FilterParams {
  category?: string;
  min_price?: number;
  max_price?: number;
  in_stock?: boolean;
  search?: string;
  page?: number;
  page_size?: number;
}

export const catalogApi = {
  getProducts: async (filters: FilterParams): Promise<PaginatedResponse> => {
    const params = Object.fromEntries(
      Object.entries(filters).filter(([, v]) => v !== undefined && v !== "")
    );
    const response = await api.get("/catalog/products", { params });
    return response.data;
  },

  getProduct: async (id: string): Promise<Product> => {
    const response = await api.get(`/catalog/products/${id}`);
    return response.data;
  },

  createProduct: async (product: Omit<Product, "id" | "created_at">): Promise<Product> => {
    const response = await api.post("/catalog/products", product);
    return response.data;
  },

  updateProduct: async (id: string, product: Partial<Product>): Promise<Product> => {
    const response = await api.put(`/catalog/products/${id}`, product);
    return response.data;
  },

  deleteProduct: async (id: string): Promise<void> => {
    await api.delete(`/catalog/products/${id}`);
  },

  uploadImage: async (file: File): Promise<string> => {
    const formData = new FormData();
    formData.append("file", file);

    const response = await api.post("/catalog/products/upload-image", formData, {
      headers: {
      
      },
      timeout: 30000, 
    });

    return response.data.image_url as string;
  },
};

export default api;
