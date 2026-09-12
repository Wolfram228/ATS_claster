<template>
  <v-app>
    <Title />
    <NavigationBar />
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
import Title from "./components/Title.vue"
import NavigationBar from "./components/NavigationBar.vue";
import { isAuth, checkAuth, clearTokens, getSavedUser } from "./utils/auth";
import store from "./store";

export default {
  components: { Title, NavigationBar },
  async created() {
    if (isAuth()) {
      try {
        const isValid = await checkAuth();
        
        if (!isValid) {
          clearTokens();
          store.commit("SET_AUTHENTICATED", false);
          store.commit("SET_USER", null);
          if (this.$route.path !== "/login" && this.$route.path !== "/register") {
            this.$router.push("/login");
          }
        } else {
          const user = getSavedUser();
          if (user) {
            store.commit("SET_USER", user);
            store.commit("SET_AUTHENTICATED", true);
          }
        }
      } catch (error) {
        console.error("Auth check error:", error);
      }
    }
  }
}
</script>
