const TOKEN_STORAGE_KEY = 'skillmatch_token';
const USER_STORAGE_KEY = 'skillmatch_user';

export function resolveApiBaseUrl(): string {
  const envUrl =
    (import.meta as any).env?.VITE_API_URL ||
    (import.meta as any).env?.VITE_API_BASE_URL;

  if (!envUrl || typeof envUrl !== 'string' || envUrl.trim() === '') {
    return '/api';
  }

  const cleanUrl = envUrl.trim().replace(/\/+$/, '');
  if (!cleanUrl.endsWith('/api')) {
    return `${cleanUrl}/api`;
  }
  return cleanUrl;
}

export const API_BASE_URL = resolveApiBaseUrl();

export function buildApiUrl(endpoint: string): string {
  if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) {
    return endpoint;
  }
  const base = API_BASE_URL.replace(/\/+$/, '');
  let path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;

  if (base.endsWith('/api') && path.startsWith('/api/')) {
    path = path.slice(4);
  } else if (base.endsWith('/api') && path === '/api') {
    path = '';
  }

  return `${base}${path}`;
}

export const tokenStorage = {
  get: (): string | null => {
    try {
      return localStorage.getItem(TOKEN_STORAGE_KEY);
    } catch {
      return null;
    }
  },
  set: (token: string): void => {
    try {
      localStorage.setItem(TOKEN_STORAGE_KEY, token);
    } catch {}
  },
  remove: (): void => {
    try {
      localStorage.removeItem(TOKEN_STORAGE_KEY);
      localStorage.removeItem(USER_STORAGE_KEY);
    } catch {}
  },
};

export const userStorage = {
  get: (): any | null => {
    try {
      const stored = localStorage.getItem(USER_STORAGE_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  },
  set: (user: any): void => {
    try {
      localStorage.setItem(USER_STORAGE_KEY, JSON.stringify(user));
    } catch {}
  },
};

export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = buildApiUrl(endpoint);

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  };

  const token = tokenStorage.get();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = `Request failed with status ${response.status}`;
    if (response.status === 405) {
      errorDetail = `HTTP 405 Method Not Allowed: The API request to '${url}' was rejected by the static host. In production, ensure VITE_API_URL is configured in your Vercel Project Settings pointing to your deployed FastAPI backend.`;
    } else {
      try {
        const errorJson = await response.json();
        if (typeof errorJson.detail === 'string') {
          errorDetail = errorJson.detail;
        } else if (Array.isArray(errorJson.detail)) {
          errorDetail = errorJson.detail.map((d: any) => d.msg || JSON.stringify(d)).join(', ');
        } else if (errorJson.message) {
          errorDetail = errorJson.message;
        }
      } catch {
        // Use fallback errorDetail
      }
    }
    throw new Error(errorDetail);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}
