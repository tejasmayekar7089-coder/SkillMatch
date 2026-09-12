import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../../services/authService';

export const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('alex.morgan@university.edu');
  const [password, setPassword] = useState('password123');
  const [role, setRole] = useState<'student' | 'admin'>('student');
  const [errorMessage, setErrorMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setLoading(true);
    try {
      await authService.login(email, password, role);
      if (role === 'admin') {
        navigate('/admin');
      } else {
        navigate('/dashboard');
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Login failed. Please verify your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleRoleToggle = (selectedRole: 'student' | 'admin') => {
    setRole(selectedRole);
    setErrorMessage('');
    if (selectedRole === 'admin') {
      setEmail('admin@skillmatch.edu');
      setPassword('AdminPassword123!');
    } else {
      setEmail('alex.morgan@university.edu');
      setPassword('password123');
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center items-center px-space-md py-space-xl">
      <div className="w-full max-w-md bg-surface-container-lowest rounded-2xl shadow-lg border border-outline-variant/30 p-space-xl space-y-space-lg">
        <div className="text-center space-y-2">
          <Link to="/" className="inline-block">
            <img src="/assets/logo.svg" alt="SkillMatch" className="h-9 w-auto mx-auto" />
          </Link>
          <h1 className="font-headline-lg text-on-surface font-bold">Welcome Back</h1>
          <p className="font-body-sm text-secondary">Log in to view your verified matches and applications</p>
        </div>

        {/* Role Toggle */}
        <div className="flex p-1 rounded-xl bg-surface-container-low">
          <button
            type="button"
            onClick={() => handleRoleToggle('student')}
            className={`flex-1 py-1.5 rounded-lg font-label-sm font-semibold transition-colors ${
              role === 'student' ? 'bg-surface-container-lowest text-primary shadow-sm' : 'text-secondary'
            }`}
          >
            Student Login
          </button>
          <button
            type="button"
            onClick={() => handleRoleToggle('admin')}
            className={`flex-1 py-1.5 rounded-lg font-label-sm font-semibold transition-colors ${
              role === 'admin' ? 'bg-surface-container-lowest text-primary shadow-sm' : 'text-secondary'
            }`}
          >
            Admin Portal
          </button>
        </div>

        {errorMessage && (
          <div className="p-3 rounded-xl bg-error/10 border border-error/20 text-error font-body-sm text-center">
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleLogin} className="space-y-space-md">
          <div className="space-y-1">
            <label className="font-label-sm text-on-surface font-medium">University Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full h-11 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
              required
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between items-center">
              <label className="font-label-sm text-on-surface font-medium">Password</label>
              <a href="#" className="font-label-xs text-primary hover:underline">
                Forgot?
              </a>
            </div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full h-11 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full h-11 rounded-xl bg-primary hover:bg-primary-container text-on-primary font-label-md font-bold transition-colors shadow-sm disabled:opacity-70"
          >
            {loading ? 'Signing in...' : role === 'admin' ? 'Access Admin Portal' : 'Continue to Dashboard'}
          </button>
        </form>

        <p className="text-center font-body-sm text-secondary">
          Don't have an account?{' '}
          <Link to="/register" className="text-primary font-semibold hover:underline">
            Register for Free
          </Link>
        </p>
      </div>
    </div>
  );
};
