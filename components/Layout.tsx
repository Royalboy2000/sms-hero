import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { MessageSquare, Menu, X, Smartphone, LogIn, LogOut, User, LayoutDashboard } from 'lucide-react';
import { WHATSAPP_CONTACT, renderIcon } from '../constants';
import { useCurrency } from '../context/CurrencyContext';
import { useAuth } from '../context/AuthContext';
import EmailCapture from './EmailCapture';
import AuthModal from './AuthModal';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = React.useState(false);
  const { currency, toggleCurrency } = useCurrency();
  const { user, logout } = useAuth();
  const location = useLocation();

  const isActive = (path: string) => location.pathname === path;

  return (
    <div className="min-h-screen flex flex-col bg-background text-zinc-300 font-sans">
      {/* Navigation */}
      <nav className="fixed w-full top-0 z-50 border-b border-white/5 bg-background/80 backdrop-blur-xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center">
              <Link to="/" className="flex items-center gap-2 group">
                <div className="relative">
                   <div className="absolute inset-0 bg-emerald-500 blur opacity-40 group-hover:opacity-60 transition-opacity duration-300 rounded-lg"></div>
                   <div className="relative bg-zinc-900 border border-emerald-500/20 p-2 rounded-lg">
                     <MessageSquare className="h-5 w-5 text-emerald-500" />
                   </div>
                </div>
                <span className="font-bold text-xl tracking-tight text-white group-hover:text-emerald-500 transition-colors">
                  SMS<span className="text-emerald-500">Kenya</span>
                </span>
              </Link>
            </div>

            <div className="hidden md:block">
              <div className="ml-12 flex items-baseline space-x-1">
                <Link
                  to="/"
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                    isActive('/') ? 'text-white bg-zinc-800' : 'text-zinc-400 hover:text-white hover:bg-zinc-900'
                  }`}
                >
                  Home
                </Link>
                <Link
                  to="/app"
                  className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                    isActive('/app') ? 'text-white bg-zinc-800' : 'text-zinc-400 hover:text-white hover:bg-zinc-900'
                  }`}
                >
                  Shop
                </Link>
                {user && (
                   <Link
                   to="/dashboard"
                   className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 ${
                     isActive('/dashboard') ? 'text-white bg-zinc-800' : 'text-zinc-400 hover:text-white hover:bg-zinc-900'
                   }`}
                 >
                   Dashboard
                 </Link>
                )}
              </div>
            </div>

            <div className="hidden md:flex items-center gap-4">
              <button
                onClick={toggleCurrency}
                className="px-4 py-2 rounded-full bg-zinc-900 border border-zinc-700 text-zinc-300 text-xs font-bold hover:text-white hover:border-emerald-500/50 transition-all"
              >
                {currency === 'KES' ? '🇰🇪 KES' : '🇺🇸 USD'}
              </button>

              {user ? (
                <div className="flex items-center gap-2">
                   <Link to="/dashboard" className="px-4 py-2 rounded-full bg-zinc-800 text-zinc-300 text-sm flex items-center gap-2 hover:bg-zinc-700 transition-colors">
                      <User className="w-4 h-4" />
                      {user.username}
                   </Link>
                   <button onClick={logout} className="p-2.5 rounded-full bg-zinc-900 border border-white/5 text-zinc-400 hover:text-red-400 transition-colors">
                      <LogOut className="w-4 h-4" />
                   </button>
                </div>
              ) : (
                <button
                  onClick={() => setIsAuthModalOpen(true)}
                  className="px-6 py-2.5 rounded-full bg-zinc-900 border border-zinc-700 text-white text-sm font-bold hover:border-emerald-500 transition-all flex items-center gap-2"
                >
                  <LogIn className="w-4 h-4" />
                  Login
                </button>
              )}

              <Link
                to="/app"
                className="bg-white text-black hover:bg-zinc-200 px-6 py-2.5 rounded-full text-sm font-bold transition-all shadow-[0_0_20px_rgba(255,255,255,0.1)] flex items-center gap-2"
              >
                Order Now
                <Smartphone className="w-4 h-4" />
              </Link>
            </div>

            <div className="-mr-2 flex md:hidden">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="inline-flex items-center justify-center p-2 rounded-md text-zinc-400 hover:text-white hover:bg-zinc-800 focus:outline-none"
              >
                {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-zinc-800 bg-black">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
              <Link
                to="/"
                onClick={() => setIsMenuOpen(false)}
                className="block px-3 py-3 rounded-md text-base font-medium text-zinc-300 hover:text-white hover:bg-zinc-900"
              >
                Home
              </Link>
              <Link
                to="/app"
                onClick={() => setIsMenuOpen(false)}
                className="block px-3 py-3 rounded-md text-base font-medium text-zinc-300 hover:text-white hover:bg-zinc-900"
              >
                Shop
              </Link>
              {user && (
                 <Link
                 to="/dashboard"
                 onClick={() => setIsMenuOpen(false)}
                 className="block px-3 py-3 rounded-md text-base font-medium text-zinc-300 hover:text-white hover:bg-zinc-900"
               >
                 Dashboard
               </Link>
              )}
              <button
                onClick={() => {
                    toggleCurrency();
                    setIsMenuOpen(false);
                }}
                className="block w-full text-left px-3 py-3 rounded-md text-base font-medium text-zinc-300 hover:text-white hover:bg-zinc-900"
              >
                Switch to {currency === 'KES' ? 'USD' : 'KES'}
              </button>

              {!user ? (
                 <button
                 onClick={() => {
                     setIsAuthModalOpen(true);
                     setIsMenuOpen(false);
                 }}
                 className="block w-full text-left px-3 py-3 rounded-md text-base font-medium text-zinc-300 hover:text-white hover:bg-zinc-900"
               >
                 Login / Register
               </button>
              ) : (
                <button
                onClick={() => {
                    logout();
                    setIsMenuOpen(false);
                }}
                className="block w-full text-left px-3 py-3 rounded-md text-base font-medium text-red-400 hover:bg-zinc-900"
              >
                Logout
              </button>
              )}

              <Link
                 to="/app"
                 onClick={() => setIsMenuOpen(false)}
                 className="block px-3 py-3 mt-4 text-center rounded-md text-base font-medium bg-emerald-600 text-white"
              >
                Order Now
              </Link>
            </div>
          </div>
        )}
      </nav>

      <main className="flex-grow pt-20">
        {children}
      </main>

      <AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />

      <footer className="bg-black border-t border-white/5 py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-8">
            <div className="text-center md:text-left">
              <span className="font-bold text-lg text-white">SMS<span className="text-emerald-500">Kenya</span></span>
              <p className="text-zinc-500 text-sm mt-2 max-w-xs">
                Premium Concierge SMS verification services in Kenya.
              </p>
            </div>
            <div className="flex gap-8">
              <a href="#" className="text-zinc-500 hover:text-emerald-500 text-sm transition-colors">Terms of Service</a>
              <a href="#" className="text-zinc-500 hover:text-emerald-500 text-sm transition-colors">Privacy Policy</a>
              <a href={`https://wa.me/${WHATSAPP_CONTACT}`} className="text-zinc-500 hover:text-emerald-500 text-sm transition-colors">Contact Support</a>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-white/5 text-center text-xs text-zinc-600">
            © 2026 SMSKenya Inc. All rights reserved.
          </div>
        </div>
      </footer>

      {/* Email Capture Popup */}
      <EmailCapture />

      {/* Floating WhatsApp Button */}
      <a
        href={`https://wa.me/${WHATSAPP_CONTACT}`}
        target="_blank"
        rel="noopener noreferrer"
        className="fixed bottom-6 right-6 z-50 flex items-center gap-3 bg-[#25D366] hover:bg-[#20bd5a] text-white px-5 py-3 rounded-full shadow-lg hover:shadow-xl transition-all hover:scale-105 group"
      >
        <div className="w-6 h-6 flex items-center justify-center">
            {renderIcon('whatsapp', 'w-6 h-6 text-white')}
        </div>
        <span className="font-bold text-sm hidden sm:block">Need help? Chat with us.</span>
        <span className="font-bold text-sm sm:hidden">Chat</span>
      </a>
    </div>
  );
};

export default Layout;