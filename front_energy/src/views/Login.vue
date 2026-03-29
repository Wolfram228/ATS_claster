<template>
  <div class="page">
    <div class="card">
      <h1 class="title">Вход</h1>
      <p class="subtitle">Введите логин и пароль для доступа к личному кабинету.</p>

      <form class="form" @submit.prevent="onSubmit">
        <label class="field">
          <span class="label">Логин</span>
          <input
            v-model.trim="login"
            class="input"
            placeholder="например, admin"
            autocomplete="username"
            :disabled="loading"
          />
        </label>

        <label class="field">
          <span class="label">Пароль</span>
          <input
            v-model="password"
            class="input"
            type="password"
            placeholder="••••••••"
            autocomplete="current-password"
            :disabled="loading"
          />
        </label>

        <button class="btn" type="submit" :disabled="loading || !login || !password">
          {{ loading ? "Входим..." : "Войти" }}
        </button>

        <p v-if="errorMessage" class="error">
          {{ errorMessage }}
        </p>

        <p class="hint">
          Нет аккаунта?
          <router-link to="/register">Зарегистрироваться</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue"
import { useRouter } from "vue-router"
import { fetchProfile, loginUser } from "../utils/auth"
import store from '../store';

const router = useRouter()

const login = ref("")
const password = ref("")
const loading = ref(false)
const errorMessage = ref("")

async function onSubmit() {
  errorMessage.value = ""
  loading.value = true

  try {
    await loginUser({
      username: login.value,
      password: password.value,
    })

    store.commit("SET_AUTHENTICATED", true)

    try {
      const profile = await fetchProfile()
      store.commit("SET_USER", profile)
    } catch (profileError) {
      console.warn("Profile fetch failed after login", profileError)
      store.commit("SET_USER", null)
    }

    router.push("/lk")
  } catch (error) {
    errorMessage.value = error.message || "Не удалось выполнить вход"
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.page{
  min-height: calc(100vh - 70px);
  display:grid;
  place-items:center;
  padding:30px 16px;
  background:#f6f7fb;
}

.card{
  width:100%;
  max-width:440px;
  background:#fff;
  border:1px solid rgba(0,0,0,.08);
  border-radius:14px;
  box-shadow:0 10px 30px rgba(0,0,0,.08);
  padding:22px;
}

.title{ margin:0; font-size:22px; font-weight:800; }

.subtitle{
  margin:8px 0 18px;
  color:#6b7280;
  font-size:13px;
}

.form{
  display:grid;
  gap:12px;
}

.field{
  display:grid;
  gap:6px;
}

.label{
  font-size:12px;
  font-weight:600;
  color:#374151;
}

.input{
  height:42px;
  border-radius:10px;
  border:1px solid rgba(0,0,0,.14);
  padding:0 12px;
  outline:none;
}

.input:focus{
  border-color:rgba(59,130,246,.55);
  box-shadow:0 0 0 4px rgba(59,130,246,.14);
}

.btn{
  height:44px;
  border-radius:10px;
  border:none;
  background:#2563eb;
  color:#fff;
  font-weight:800;
  cursor:pointer;
}

.hint{
  margin:4px 0 0;
  font-size:12px;
  color:#6b7280;
}

.error{
  margin: 0;
  font-size: 13px;
  color: #dc2626;
}
</style>
