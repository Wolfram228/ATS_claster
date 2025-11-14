<template>
    <v-app-bar app>
        <v-app-bar-title>
            <div class="d-flex align-center">
                <v-img :src="icon" max-width="45" class="me-2" />
                <div d-flex flex-column align="left">
                    <p class="title1"> ATSEnergo </p>
                    <p class="title2">Анализ рынка электроэнергии</p>
                </div>
            </div>
        </v-app-bar-title>
    </v-app-bar>
</template>

<script>
import icon from "../assets/icon.png"
export default {
    data() {
        return {
            icon
        }
    }
}
</script>

<style scoped>
.title1 {
    font-weight: bold;
    font-size:larger;
    font-family: monospace;
    color: rgb(7, 0, 100)
}
.title2 {
    font-size: medium;
    color: rgb(0, 6, 94)
}
p {
    margin: 0
}
</style>