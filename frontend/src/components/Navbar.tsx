import { Link } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";

export function Navbar() {
  const { user, role, logout } = useAuth();

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <Link to="/" className="text-xl font-bold text-indigo-600">
            Catálogo Inteligente
          </Link>

          <div className="flex items-center gap-4">
            {user ? (
              <>
                <span className="text-sm text-gray-600">{user.email}</span>
                {role === "admin" && (
                  <Link
                    to="/admin"
                    className="text-sm bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
                  >
                    Admin
                  </Link>
                )}
                <button
                  onClick={logout}
                  className="text-sm text-gray-600 hover:text-red-600 transition-colors"
                >
                  Sair
                </button>
              </>
            ) : (
              <Link
                to="/login"
                className="text-sm bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
              >
                Entrar
              </Link>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}
