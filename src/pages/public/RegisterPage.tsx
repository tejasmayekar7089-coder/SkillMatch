import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../../services/authService';

export const RegisterPage: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [university, setUniversity] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');
    setLoading(true);
    try {
      await authService.register({
        name,
        email,
        password,
        university,
        role: 'student',
      });
      navigate('/onboarding');
    } catch (err: any) {
      setErrorMessage(err.message || 'Registration failed. Please check your information.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col justify-center items-center px-space-md py-space-xl">
      <div className="w-full max-w-md bg-surface-container-lowest rounded-2xl shadow-lg border border-outline-variant/30 p-space-xl space-y-space-lg">
        <div className="text-center space-y-2">
          <Link to="/" className="inline-block">
            <img src="/assets/logo.svg" alt="SkillMatch" className="h-9 w-auto mx-auto" />
          </Link>
          <h1 className="font-headline-lg text-on-surface font-bold">Create Student Account</h1>
          <p className="font-body-sm text-secondary">Join verified students discovering precision opportunities</p>
        </div>

        {errorMessage && (
          <div className="p-3 rounded-xl bg-error/10 border border-error/20 text-error font-body-sm text-center">
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-space-md">
          <div className="space-y-1">
            <label className="font-label-sm text-on-surface font-medium">Full Name</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g. Alex Morgan"
              className="w-full h-11 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="font-label-sm text-on-surface font-medium">University / Institutional Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="alex@university.edu"
              className="w-full h-11 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="font-label-sm text-on-surface font-medium">College / University Name</label>
            <input
              type="text"
              value={university}
              onChange={(e) => setUniversity(e.target.value)}
              placeholder="e.g. National Institute of Technology"
              className="w-full h-11 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
              required
            />
          </div>

          <div className="space-y-1">
            <label className="font-label-sm text-on-surface font-medium">Create Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Minimum 6 characters"
              className="w-full h-11 px-3 rounded-xl bg-surface-container-low border border-outline-variant/40 font-body-sm text-on-surface focus:outline-none focus:border-primary"
              required
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full h-11 rounded-xl bg-primary hover:bg-primary-container text-on-primary font-label-md font-bold transition-colors shadow-sm disabled:opacity-70"
          >
            {loading ? 'Creating Account...' : 'Create Account & Continue'}
          </button>
        </form>

        <p className="text-center font-body-sm text-secondary">
          Already registered?{' '}
          <Link to="/login" className="text-primary font-semibold hover:underline">
            Log In
          </Link>
        </p>
      </div>
    </div>
  );
};
