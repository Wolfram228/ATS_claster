<template>
  <v-app>
    <Title v-if="isAuthenticated" />
    <NavigationBar v-if="isAuthenticated" />
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script>
import Title from "./components/Title.vue"
import NavigationBar from "./components/NavigationBar.vue";
export default {
  components: { Title, NavigationBar },
  computed: {
    isAuthenticated() {
      return this.$store.state.isAuthenticated
    }
  }
}
</script>
