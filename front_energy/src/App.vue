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
export default {
  components: { Title, NavigationBar },
}
</script>
