<template>
  <v-app>
    <Title />
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
import Title from "./components/Title.vue"
import { isAuth, checkAuth, clearTokens, getSavedUser } from "./utils/auth"
import store from "./store"

const publicPages = ["/", "/login", "/register"]

export default {
  components: { Title },
  methods: {
    handleSessionExpired() {
      clearTokens()
      store.commit("SET_AUTHENTICATED", false)
      store.commit("SET_USER", null)
      
      if (publicPages.includes(this.$route.path)) {
        return
      }
      
      this.$router.push({
        path: "/login",
        query: {
          reason: "expired",
          redirect: this.$route.fullPath,
        },
      })
    },
  },
  async created() {
    // Слушаем событие истечения сессии (вызывается из authFetch в auth.js)
    window.addEventListener("session-expired", this.handleSessionExpired)
    
    if (isAuth()) {
      try {
        const isValid = await checkAuth()
        if (!isValid) {
          this.handleSessionExpired()
        } else {
          const user = getSavedUser()
          if (user) {
            store.commit("SET_USER", user)
          }
          store.commit("SET_AUTHENTICATED", true)
        }
      } catch (error) {
        console.error("Auth check error:", error)
      }
    }
  },
  beforeUnmount() {
    // Обязательно отписываемся от события при уничтожении компонента
    window.removeEventListener("session-expired", this.handleSessionExpired)
  },
}
</script>

<style>
body {
  background-color: #ffffff !important;
}
</style>
