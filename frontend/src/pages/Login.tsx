import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/");
    } catch {
      setError("E-mail ou senha inválidos");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Entrar</h1>
        <p className="text-gray-500 text-sm mb-6">Acesse sua conta para continuar</p>

        {/* ACESSIBILIDADE [FIX-A1]: role="alert" anuncia erros automaticamente para leitores de tela */}
        {error && (
          <div
            role="alert"
            aria-live="assertive"
            className="bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3 mb-4"
          >
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4" noValidate aria-label="Formulário de login">
          <div>
            {/* ACESSIBILIDADE [FIX-A1]: htmlFor vinculado ao id do input — associação explícita exigida por WCAG 1.3.1 */}
            <label htmlFor="login-email" className="block text-sm font-medium text-gray-700 mb-1">
              E-mail
            </label>
            <input
              id="login-email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              aria-required="true"
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="seu@email.com"
            />
          </div>

          <div>
            {/* ACESSIBILIDADE [FIX-A1]: htmlFor vinculado ao id do input — associação explícita exigida por WCAG 1.3.1 */}
            <label htmlFor="login-password" className="block text-sm font-medium text-gray-700 mb-1">
              Senha
            </label>
            <input
              id="login-password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              aria-required="true"
              className="w-full border border-gray-300 rounded-lg px-4 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            aria-busy={loading}
            className="w-full bg-indigo-600 text-white py-2.5 rounded-lg font-medium hover:bg-indigo-700 disabled:opacity-60 transition-colors"
          >
            {loading ? "Entrando..." : "Entrar"}
          </button>
        </form>
      </div>
    </div>
  );
}
