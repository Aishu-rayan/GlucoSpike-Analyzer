import { useState } from 'react';
import { motion } from 'framer-motion';
import { Salad, Eye, EyeOff, Loader2, ArrowRight, Check } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

interface RegisterProps {
  onSwitchToLogin: () => void;
}

export function Register({ onSwitchToLogin }: RegisterProps) {
  const { register } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const passwordRequirements = [
    { met: password.length >= 6, text: 'At least 6 characters' },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setIsLoading(true);

    try {
      await register(username, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#0f1410] p-4">
      {/* Background */}
      <div className="fixed inset-0 bg-gradient-to-br from-sage-900/20 via-transparent to-coral-900/10 pointer-events-none" />
      
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', duration: 0.5 }}
            className="w-16 h-16 rounded-2xl bg-gradient-to-br from-sage-500 to-sage-600 flex items-center justify-center mx-auto mb-4 shadow-xl"
          >
            <Salad className="w-8 h-8 text-white" />
          </motion.div>
          <h1 className="text-2xl font-bold text-sage-100">Create an account</h1>
          <p className="text-sage-400 mt-1">Start your journey to better nutrition</p>
        </div>

        {/* Form */}
        <div className="bg-sage-900/50 border border-sage-800/50 rounded-2xl p-6 backdrop-blur-lg">
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="p-3 rounded-lg bg-coral-900/30 border border-coral-500/30 text-coral-200 text-sm"
              >
                {error}
              </motion.div>
            )}

            <div>
              <label className="block text-sm font-medium text-sage-300 mb-2">
                Username
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-sage-800/50 border border-sage-700/50 text-sage-100 placeholder-sage-500 focus:outline-none focus:ring-2 focus:ring-sage-500/50 focus:border-transparent"
                placeholder="Choose a username"
                required
                minLength={3}
                autoComplete="username"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-300 mb-2">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-sage-800/50 border border-sage-700/50 text-sage-100 placeholder-sage-500 focus:outline-none focus:ring-2 focus:ring-sage-500/50 focus:border-transparent pr-12"
                  placeholder="Create a password"
                  required
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-sage-400 hover:text-sage-200"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
              {/* Password requirements */}
              <div className="mt-2 space-y-1">
                {passwordRequirements.map((req, i) => (
                  <div key={i} className="flex items-center gap-2 text-xs">
                    <Check className={`w-3 h-3 ${req.met ? 'text-sage-400' : 'text-sage-600'}`} />
                    <span className={req.met ? 'text-sage-400' : 'text-sage-600'}>{req.text}</span>
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-sage-300 mb-2">
                Confirm Password
              </label>
              <input
                type={showPassword ? 'text' : 'password'}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-3 rounded-xl bg-sage-800/50 border border-sage-700/50 text-sage-100 placeholder-sage-500 focus:outline-none focus:ring-2 focus:ring-sage-500/50 focus:border-transparent"
                placeholder="Confirm your password"
                required
                autoComplete="new-password"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-sage-600 to-sage-500 text-white font-medium hover:from-sage-500 hover:to-sage-400 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  Create Account
                  <ArrowRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-sage-400 text-sm">
              Already have an account?{' '}
              <button
                onClick={onSwitchToLogin}
                className="text-sage-300 hover:text-sage-100 font-medium transition-colors"
              >
                Sign in
              </button>
            </p>
          </div>
        </div>
      </motion.div>
    </div>
  );
}

