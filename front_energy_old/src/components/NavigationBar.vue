<template>
    <v-app-bar app>
        <v-row justify="center" align="center">
            <router-link to="/">
                <v-btn> Главная </v-btn>
            </router-link>
            <router-link to="/reports">
                <v-btn> Отчёты </v-btn>
            </router-link>
            <router-link to="/reportInfo/1">
                <v-btn> Информация </v-btn>
            </router-link>
            <router-link to="/table">
                <v-btn> Таблица </v-btn>
            </router-link>
        </v-row>
    </v-app-bar>
</template>

<style scoped>
.router-link-active {
    color: rgb(6, 4, 119);
}
</style>