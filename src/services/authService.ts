import { apiFetch, tokenStorage, userStorage } from './apiClient';

export interface AuthUser {
  id: string;
  name: string;
  email: string;
  role: 'student' | 'admin';
  avatarUrl: string;
  branch?: string;
  academic_year?: string;
}

export interface RegisterParams {
  name: string;
  email: string;
  password: string;
  university?: string;
  college?: string;
  role?: 'student' | 'admin';
}

export function getSafeAvatarUrl(avatarUrl?: string | null, name = 'User'): string {
  if (avatarUrl && !avatarUrl.includes('aida-public/AB6AXuDJbu')) {
    return avatarUrl;
  }
  const safeName = encodeURIComponent(name.trim() || 'User');
  return `https://ui-avatars.com/api/?name=${safeName}&background=0284c7&color=fff&size=128&bold=true`;
}

class AuthService {
  private currentUser: AuthUser | null = null;

  constructor() {
    // Restore user from storage if present
    const storedUser = userStorage.get();
    if (storedUser) {
      storedUser.avatarUrl = getSafeAvatarUrl(storedUser.avatarUrl, storedUser.name);
      this.currentUser = storedUser;
    }
  }

  getCurrentUser(): AuthUser | null {
    return this.currentUser;
  }

  async login(email: string, password = 'password123', _role: 'student' | 'admin' = 'student'): Promise<AuthUser> {
    try {
      const data = await apiFetch<{
        access_token: string;
        token_type: string;
        user: {
          id: string;
          email: string;
          full_name: string;
          name?: string;
          role: string;
          avatarUrl?: string;
          avatar_url?: string;
          branch?: string;
          academic_year?: string;
        };
      }>('/auth/login', {
        method: 'POST',
        body: JSON.stringify({
          email: email.trim().toLowerCase(),
          password,
        }),
      });

      tokenStorage.set(data.access_token);

      const userName = data.user.full_name || data.user.name || 'User';
      const user: AuthUser = {
        id: data.user.id,
        name: userName,
        email: data.user.email,
        role: data.user.role.toLowerCase() === 'admin' ? 'admin' : 'student',
        avatarUrl: getSafeAvatarUrl(data.user.avatarUrl || data.user.avatar_url, userName),
        branch: data.user.branch,
        academic_year: data.user.academic_year,
      };

      this.currentUser = user;
      userStorage.set(user);
      return user;
    } catch (err) {
      // Fallback for demo / offline preview if server is unavailable
      console.warn('API login failed, checking fallback:', err);
      throw err;
    }
  }

  async register(params: RegisterParams): Promise<AuthUser> {
    const roleUpper = params.role === 'admin' ? 'ADMIN' : 'STUDENT';
    const data = await apiFetch<{
      access_token: string;
      token_type: string;
      user: {
        id: string;
        email: string;
        full_name: string;
        name?: string;
        role: string;
        avatarUrl?: string;
        avatar_url?: string;
        branch?: string;
        academic_year?: string;
      };
    }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({
        email: params.email.trim().toLowerCase(),
        password: params.password,
        full_name: params.name.trim(),
        role: roleUpper,
        college: params.college || params.university,
        university: params.university || params.college,
      }),
    });

    tokenStorage.set(data.access_token);

    const userName = data.user.full_name || data.user.name || params.name;
    const user: AuthUser = {
      id: data.user.id,
      name: userName,
      email: data.user.email,
      role: data.user.role.toLowerCase() === 'admin' ? 'admin' : 'student',
      avatarUrl: getSafeAvatarUrl(data.user.avatarUrl || data.user.avatar_url, userName),
      branch: data.user.branch,
      academic_year: data.user.academic_year,
    };

    this.currentUser = user;
    userStorage.set(user);
    return user;
  }

  async fetchCurrentUser(): Promise<AuthUser | null> {
    const token = tokenStorage.get();
    if (!token) return null;
    try {
      const userRaw = await apiFetch<any>('/auth/me');
      const userName = userRaw.full_name || userRaw.name || 'Student';
      const user: AuthUser = {
        id: userRaw.id,
        name: userName,
        email: userRaw.email,
        role: userRaw.role.toLowerCase() === 'admin' ? 'admin' : 'student',
        avatarUrl: getSafeAvatarUrl(userRaw.avatarUrl || userRaw.avatar_url, userName),
        branch: userRaw.branch,
        academic_year: userRaw.academic_year,
      };
      this.currentUser = user;
      userStorage.set(user);
      return user;
    } catch {
      this.logout();
      return null;
    }
  }

  async logout(): Promise<void> {
    this.currentUser = null;
    tokenStorage.remove();
  }
}

export const authService = new AuthService();
