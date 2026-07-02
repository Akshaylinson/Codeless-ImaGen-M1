const runtime = window.APP_CONFIG || {};
const defaultOrigin = window.location.origin;

export const APP_CONFIG = {
  APP_NAME: runtime.APP_NAME || 'CodelessAI Smart Image Editor',
  APP_ENV: runtime.APP_ENV || 'development',
  BASE_URL: runtime.BASE_URL || defaultOrigin,
  API_BASE_URL: runtime.API_BASE_URL || `${defaultOrigin}/api`,
  STATIC_BASE_URL: runtime.STATIC_BASE_URL || `${defaultOrigin}/static`,
  PUBLIC_BASE_URL: runtime.PUBLIC_BASE_URL || defaultOrigin,
  FRONTEND_URL: runtime.FRONTEND_URL || defaultOrigin,
  API_PREFIX: runtime.API_PREFIX || '/api',
  STATIC_URL: runtime.STATIC_URL || '/static',
  ENABLE_HTTPS: Boolean(runtime.ENABLE_HTTPS),
};

const TOKEN_KEY = 'codelessai_token';

export function getToken() {
  return localStorage.getItem(TOKEN_KEY) || '';
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

export async function apiFetch(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = getToken();
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (!(options.body instanceof FormData) && options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }
  const requestPath = path.startsWith('http://') || path.startsWith('https://')
    ? path
    : `${APP_CONFIG.API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;
  const response = await fetch(requestPath, {
    ...options,
    headers,
  });
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const payload = await response.json();
      detail = payload.detail || payload.message || detail;
    } catch {}
    throw new Error(detail);
  }
  const contentType = response.headers.get('content-type') || '';
  if (contentType.includes('application/json')) return response.json();
  return response;
}
