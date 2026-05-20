const ACCESS_TOKEN_KEY = 'access'
const REFRESH_TOKEN_KEY = 'refresh'
const USER_KEY = 'user'

export function getAccessToken() {
  return localStorage.getItem(ACCESS_TOKEN_KEY)
}

export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY)
}

export function setTokens(tokens = {}) {
  if (tokens.access) {
    localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access)
  }

  if (tokens.refresh) {
    localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh)
  }
}

export function saveTokens(access, refresh) {
  setTokens({ access, refresh })
}

export function clearTokens() {
  localStorage.removeItem(ACCESS_TOKEN_KEY)
  localStorage.removeItem(REFRESH_TOKEN_KEY)
  localStorage.removeItem(USER_KEY)
}

export function isAuth() {
  return Boolean(getAccessToken())
}

export function saveUser(user) {
  if (user) {
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  }
}

export function getSavedUser() {
  const rawUser = localStorage.getItem(USER_KEY)

  if (!rawUser) {
    return null
  }

  try {
    return JSON.parse(rawUser)
  } catch (error) {
    return null
  }
}

export async function authFetch(url, options = {}) {
  const token = getAccessToken()

  const headers = {
    ...(options.headers || {}),
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`
  }

  return fetch(url, {
    ...options,
    headers,
  })
}

export async function loginUser(credentials) {
  const response = await fetch('/api/token/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  })

  if (!response.ok) {
    throw new Error('Не удалось выполнить вход')
  }

  const data = await response.json()
  setTokens({
    access: data.access,
    refresh: data.refresh,
  })

  return data
}

export async function registerUser(payload) {
  const response = await fetch('/api/auth/register/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error('Не удалось выполнить регистрацию')
  }

  return response.json()
}

export async function fetchProfile() {
  const response = await authFetch('/api/auth/profile/')

  if (!response.ok) {
    throw new Error('Не удалось загрузить профиль')
  }

  const user = await response.json()
  saveUser(user)
  return user
}

export async function fetchExtendedProfile() {
  const response = await authFetch('/api/profile/')

  if (!response.ok) {
    throw new Error('Не удалось загрузить расширенный профиль')
  }

  return response.json()
}

export async function updateExtendedProfile(payload) {
  const response = await authFetch('/api/profile/', {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    throw new Error('Не удалось сохранить профиль')
  }

  return response.json()
}

export async function logout() {
  const refresh = getRefreshToken()

  try {
    if (refresh) {
      await authFetch('/api/auth/logout/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh }),
      })
    }
  } finally {
    clearTokens()
  }
}