import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export function Navbar() {
  const { user, role, logout } = useAuth();

  return (
    <>
      {/* ACESSIBILIDADE [FIX-A2]: skip-to-content link — permite usuários de teclado/leitor de tela pular a nav diretamente para o conteúdo principal (WCAG 2.4.1) */}
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:top-2 focus:left-2 focus:z-[100] focus:bg-indigo-600 focus:text-white focus:px-4 focus:py-2 focus:rounded-lg focus:text-sm focus:font-medium"
      >
        Pular para o conteúdo principal
      </a>

      {/* ACESSIBILIDADE [FIX-A2]: aria-label descreve a finalidade da nav para leitores de tela (WCAG 4.1.2) */}
      <nav aria-label="Navegação principal" className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <Link to="/" aria-label="Ir para a página inicial do Catálogo Inteligente" className="text-xl font-bold text-indigo-600">
              Catálogo Inteligente
            </Link>

            <div className="flex items-center gap-4" role="menubar" aria-label="Menu do usuário">
              {user ? (
                <>
                  <span className="text-sm text-gray-600" aria-label={`Usuário autenticado: ${user.email}`}>
                    {user.email}
                  </span>
                  {role === "admin" && (
                    <Link
                      to="/admin"
                      aria-label="Acessar painel administrativo"
                      className="text-sm bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
                    >
                      Admin
                    </Link>
                  )}
                  <button
                    onClick={logout}
                    aria-label="Sair da conta"
                    className="text-sm text-gray-600 hover:text-red-600 transition-colors"
                  >
                    Sair
                  </button>
                </>
              ) : (
                <Link
                  to="/login"
                  aria-label="Fazer login na conta"
                  className="text-sm bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
                >
                  Entrar
                </Link>
              )}
            </div>
          </div>
        </div>
      </nav>
    </>
  );
}
