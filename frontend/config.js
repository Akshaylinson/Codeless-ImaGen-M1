const raw = window.APP_CONFIG || {};
const defaultOrigin = window.location.origin;

window.APP_CONFIG = {
  APP_NAME: raw.APP_NAME || 'CodelessAI Smart Image Editor',
  APP_ENV: raw.APP_ENV || 'development',
  BASE_URL: raw.BASE_URL || defaultOrigin,
  API_BASE_URL: raw.API_BASE_URL ? `${raw.API_BASE_URL}${raw.API_PREFIX || '/api'}` : `${defaultOrigin}/api`,
  STATIC_BASE_URL: raw.STATIC_BASE_URL ? `${raw.STATIC_BASE_URL}${raw.STATIC_URL || '/static'}` : `${defaultOrigin}/static`,
  PUBLIC_BASE_URL: raw.PUBLIC_BASE_URL || defaultOrigin,
  FRONTEND_URL: raw.FRONTEND_URL || defaultOrigin,
  API_PREFIX: raw.API_PREFIX || '/api',
  STATIC_URL: raw.STATIC_URL || '/static',
  ENABLE_HTTPS: Boolean(raw.ENABLE_HTTPS),
};
