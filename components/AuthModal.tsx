import React, { useState } from 'react';
import { X, LogIn, UserPlus, ShieldCheck, Loader2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const endpoint = isLogin ? '/api/login' : '/api/register';

    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        if (isLogin) {
          login(data.token, data.user);
          onClose();
        } else {
          setIsLogin(true);
          setError('Registration successful! Please login.');
        }
      } else {
        setError(data.message || 'Something went wrong');
      }
    } catch (err) {
      setError('Failed to connect to server');
    } finally {
      setIsLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[200] flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-300">
      <div className="relative w-full max-w-md bg-zinc-950 border border-white/10 rounded-[2.5rem] shadow-2xl overflow-hidden p-8">
        <button onClick={onClose} className="absolute top-6 right-6 p-2 hover:bg-white/5 rounded-full transition-colors text-zinc-500 hover:text-white">
          <X className="w-6 h-6" />
        </button>

        <div className="flex flex-col items-center mb-8">
          <div className="w-16 h-16 bg-emerald-500/10 border border-emerald-500/20 rounded-2xl flex items-center justify-center mb-4">
            <ShieldCheck className="w-8 h-8 text-emerald-500" />
          </div>
          <h2 className="text-2xl font-bold text-white">{isLogin ? 'Welcome Back' : 'Create Account'}</h2>
          <p className="text-sm text-zinc-500 mt-1">{isLogin ? 'Login to manage your numbers' : 'Join SMSKenya today'}</p>
        </div>

        {error && (
          <div className={`p-4 rounded-xl text-sm mb-6 ${error.includes('successful') ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20' : 'bg-red-500/10 text-red-500 border border-red-500/20'}`}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-2 ml-1">Username</label>
            <input
              required
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 rounded-2xl px-4 py-4 text-white focus:outline-none focus:border-emerald-500/50 transition-all"
              placeholder="Your username"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-zinc-500 uppercase tracking-widest mb-2 ml-1">Password</label>
            <input
              required
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-zinc-900 border border-zinc-800 rounded-2xl px-4 py-4 text-white focus:outline-none focus:border-emerald-500/50 transition-all"
              placeholder="••••••••"
            />
          </div>

          <button
            disabled={isLoading}
            type="submit"
            className="w-full flex items-center justify-center gap-3 px-8 py-4 bg-emerald-600 hover:bg-emerald-500 text-white font-bold rounded-2xl transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed group"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                {isLogin ? <LogIn className="w-5 h-5" /> : <UserPlus className="w-5 h-5" />}
                {isLogin ? 'Login' : 'Register'}
              </>
            )}
          </button>
        </form>

        <div className="mt-8 pt-8 border-t border-white/5 text-center">
          <button
            onClick={() => {
                setIsLogin(!isLogin);
                setError('');
            }}
            className="text-sm text-zinc-400 hover:text-emerald-500 transition-colors"
          >
            {isLogin ? "Don't have an account? Register" : "Already have an account? Login"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default AuthModal;
