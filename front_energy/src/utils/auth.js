const USER_KEY = 'user'
const AUTH_FLAG_KEY = 'auth_flag'

// --- Флаг авторизации (не хранит сам JWT) ---
export function setAuthFlag(isAuthenticated) {
  if (isAuthenticated) {
    localStorage.setItem(AUTH_FLAG_KEY, '1')
  } else {
    localStorage.removeItem(AUTH_FLAG_KEY)
  }
}

export function isAuth() {
  return localStorage.getItem(AUTH_FLAG_KEY) === '1'
}

// --- Пользователь ---
export function saveUser(user) {
  if (user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  }
}

export function getSavedUser() {
  const rawUser = localStorage.getItem(USER_KEY)
  if (!rawUser) return null
  try {
    return JSON.parse(rawUser)
  } catch (error) {
    return null
  }
}

export function clearTokens() {
  localStorage.removeItem(USER_KEY)
  localStorage.removeItem(AUTH_FLAG_KEY)
}

// --- Обновление токена (Refresh) ---
let refreshPromise = null;

export async function refreshAccess() {
  // Защита от одновременных запросов на обновление токена
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    try {
      const response = await fetch('/api/token/refresh/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Refresh failed');
      }
      setAuthFlag(true);
    } catch (error) {
      setAuthFlag(false);
     clearTokens();
      // Сообщаем приложению, что сессия истекла
      window.dispatchEvent(new Event('session-expired'));
      throw error;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

// --- Обертка над fetch с автоматическим обновлением токена ---
export async function authFetch(url, options = {}) {
  const fetchOptions = {
    ...options,
    credentials: 'include', // Всегда отправляем куки
    headers: {
      ...(options.headers || {}),
    },
  };

  let response = await fetch(url, fetchOptions);

  // Если access-токен протух (401), пробуем обновить его и повторить запрос
  if (response.status === 401) {
    try {
      await refreshAccess();
      // Если обновление успешно, повторяем исходный запрос
      response = await fetch(url, fetchOptions);
    } catch (error) {
      // Если обновить не удалось, возвращаем оригинальный 401 ответ
      return response;
    }
  }

  return response;
}

// --- Авторизация ---
export async function loginUser(credentials) {
  const response = await fetch('/api/token/', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  });

  if (!response.ok) {
    throw new Error('Не удалось выполнить вход');
  }

  const data = await response.json();
  setAuthFlag(true);
  return data;
}

export async function registerUser(payload) {
  const response = await fetch('/api/auth/register/', {
    method: 'POST',
    credentials: 'include',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error('Не удалось выполнить регистрацию');
  }

  const data = await response.json();
  setAuthFlag(true);
  return data;
}

export async function logout() {
  try {
    await fetch('/api/auth/logout/', {
      method: 'POST',
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
      },
    });
  } finally {
    clearTokens();
  }
}

// --- Профили ---
export async function fetchProfile() {
  const response = await authFetch('/api/auth/profile/');

  if (!response.ok) {
    throw new Error('Не удалось загрузить профиль');
  }

  const user = await response.json();
  saveUser(user);
  return user;
}

export async function fetchExtendedProfile() {
  const response = await authFetch('/api/profile/');

  if (!response.ok) {
    throw new Error('Не удалось загрузить расширенный профиль');
  }

  return response.json();
}

export async function updateExtendedProfile(payload) {
  const response = await authFetch('/api/profile/', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error('Не удалось сохранить профиль');
  }

  return response.json();
}

// --- Проверка авторизации ---
export async function checkAuth() {
  if (!isAuth()) {
    return false
  }

  try {
    const response = await authFetch('/api/auth/profile/')
    
    if (!response.ok) {
      clearTokens()
      return false
    }
    
    return true
  } catch (error) {
    return false
  }
}
