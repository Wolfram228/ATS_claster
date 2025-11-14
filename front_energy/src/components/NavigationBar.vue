<template>
    <v-app-bar app>
        <v-container fluid>
            <v-row justify="center" align="center" class="nav-row" dense>
                <div v-for="link in links" class="nav-link">
                    <router-link :to=link.to>
                        <v-btn class="nav-btn"> {{ link.name }}</v-btn>
                    </router-link>
                </div>

                    <!--
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
                    -->
            </v-row>
        </v-container>
    </v-app-bar>
</template>

<script>
export default {
    data() {
        return {
            links: [
                {to: "/", name: "Главная"},
                {to: "/reports", name: "Отчёты"},
                {to: "/reportInfo/1", name: "Информация"},
                {to: "/table", name: "Таблица"},
            ]
        }
    }
}
</script>

<style scoped>
.router-link-active {
    color: rgb(6, 4, 119);
}

.nav-row {
  display: flex;
  flex-wrap: nowrap; /* запрет переноса */
  justify-content: center; /* по центру экрана */
}

.nav-link {
  flex-shrink: 1;       /* позволяет кнопке сжиматься */
  min-width: 80px;      /* минимальная ширина кнопки */
}

.nav-btn {
  white-space: nowrap;    /* текст в одну строку */
  padding-left: 8px;      /* уменьшаем внутренние отступы для маленьких экранов */
  padding-right: 8px;
  font-size: 14px;        /* можно уменьшать на мобильных через медиазапросы */
  width: 100%;
  box-sizing: border-box;
}
</style>