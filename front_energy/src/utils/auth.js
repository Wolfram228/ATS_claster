export const TOKEN_KEY = "token";
export const REFRESH_TOKEN_KEY = "refreshToken";
export const USER_KEY = "authUser";

const defaultApiBase = "https://cloud-a.istu.edu";

export function getApiBaseUrl() {
  return (import.meta.env.VITE_API_BASE_URL || defaultApiBase).replace(/\/$/, "");
}

export function getAccessToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function isAuth() {
  return !!getAccessToken();
}

export function setTokens({ access, refresh }) {
  if (access) {
    localStorage.setItem(TOKEN_KEY, access);
  }

  if (refresh) {
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh);
  }
}

export function clearTokens() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

export function saveUser(user) {
  localStorage.setItem(USER_KEY, JSON.stringify(user));
}

export function getSavedUser() {
  const raw = localStorage.getItem(USER_KEY);

  if (!raw) {
    return null;
  }

  try {
    return JSON.parse(raw);
  } catch {
    localStorage.removeItem(USER_KEY);
    return null;
  }
}

export function clearUser() {
  localStorage.removeItem(USER_KEY);
}

export async function authFetch(path, options = {}) {
  const token = await ensureValidAccessToken();
  let response = await authorizedRequest(path, options, token);

  if (response.status === 401) {
    const refreshedToken = await refreshAccessToken();
    response = await authorizedRequest(path, options, refreshedToken);
  }

  if (!response.ok) {
    if (response.status === 401) {
      handleUnauthorized();
    }

    throw await createApiError(response);
  }

  return response;
}

export async function loginUser({ username, password }) {
  const response = await fetch(`${getApiBaseUrl()}/api/token/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      username,
      password,
    }),
  });

  if (!response.ok) {
    throw await createApiError(response, "Неверный логин или пароль");
  }

  const data = await response.json();
  setTokens(data);

  return data;
}

export async function registerUser(payload) {
  const response = await fetch(`${getApiBaseUrl()}/api/auth/register/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw await createApiError(response, "Не удалось зарегистрироваться");
  }

  return response.json();
}

export async function fetchProfile() {
  const response = await authFetch("/api/auth/profile/");
  const data = await response.json();
  saveUser(data);
  return data;
}

export async function fetchExtendedProfile() {
  const response = await authFetch("/api/profile/");
  return response.json();
}

export async function updateExtendedProfile(payload) {
  const response = await authFetch("/api/profile/", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });

  return response.json();
}

export async function logoutRequest() {
  const refresh = getRefreshToken();

  try {
    await authFetch("/api/auth/logout/", {
      method: "POST",
      body: JSON.stringify(refresh ? { refresh } : {}),
    });
  } catch (error) {
    console.warn("Logout request failed", error);
  }
}

export async function logout() {
  await logoutRequest();
  clearTokens();
  clearUser();
}

async function ensureValidAccessToken() {
  const token = getAccessToken();

  if (!token) {
    handleUnauthorized();
    return null;
  }

  if (!isTokenExpired(token)) {
    return token;
  }

  return refreshAccessToken();
}

async function refreshAccessToken() {
  const refresh = getRefreshToken();

  if (!refresh) {
    handleUnauthorized();
    throw new Error("Сессия истекла. Войдите снова.");
  }

  const response = await fetch(`${getApiBaseUrl()}/api/token/refresh/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ refresh }),
  });

  if (!response.ok) {
    handleUnauthorized();
    throw await createApiError(response, "Сессия истекла. Войдите снова.");
  }

  const data = await response.json();

  if (!data.access) {
    handleUnauthorized();
    throw new Error("Сессия истекла. Войдите снова.");
  }

  setTokens({
    access: data.access,
    refresh: data.refresh || refresh,
  });

  return data.access;
}

async function authorizedRequest(path, options = {}, token) {
  const headers = new Headers(options.headers || {});

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (options.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  return fetch(`${getApiBaseUrl()}${path}`, {
    ...options,
    headers,
  });
}

function isTokenExpired(token) {
  const payload = parseJwtPayload(token);

  if (!payload?.exp) {
    return false;
  }

  const now = Math.floor(Date.now() / 1000);
  return payload.exp <= now + 15;
}

function parseJwtPayload(token) {
  try {
    const [, payload] = token.split(".");

    if (!payload) {
      return null;
    }

    const base64 = payload.replace(/-/g, "+").replace(/_/g, "/");
    const normalized = base64.padEnd(Math.ceil(base64.length / 4) * 4, "=");
    return JSON.parse(atob(normalized));
  } catch {
    return null;
  }
}

function handleUnauthorized() {
  clearTokens();
  clearUser();

  if (typeof window !== "undefined" && window.location.pathname !== "/login") {
    window.location.assign("/login");
  }
}

async function createApiError(response, fallbackMessage = "Ошибка запроса") {
  let message = fallbackMessage;

  try {
    const data = await response.json();
    message = extractErrorMessage(data) || fallbackMessage;
  } catch {
    if (response.statusText) {
      message = response.statusText;
    }
  }

  const error = new Error(message);
  error.status = response.status;

  return error;
}

function extractErrorMessage(data) {
  if (!data) {
    return "";
  }

  if (typeof data === "string") {
    return data;
  }

  if (Array.isArray(data)) {
    return data.map(extractErrorMessage).filter(Boolean).join(" ");
  }

  if (typeof data.detail === "string") {
    return data.detail;
  }

  for (const value of Object.values(data)) {
    const nested = extractErrorMessage(value);
    if (nested) {
      return nested;
    }
  }

  return "";
}
