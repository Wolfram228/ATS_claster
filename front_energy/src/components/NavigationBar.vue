<template>
    <v-app-bar app flat class="app-bar-clean">
        <v-container>
            <v-row justify="center" align="center" class="nav-row" dense>
                <div
                    v-for="link in links"
                    :key="link.to"
                    class="nav-link"
                >
                    <router-link :to="link.to">
                        <v-btn class="nav-btn">{{ link.name }}</v-btn>
                    </router-link>
                </div>
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
                {to: "/information", name: "Информация"},
                {to: "/table", name: "Таблица"},
                {to: "/interactiveMap", name: "Карта"},
                {to: "/price-analytics", name: "Аналитика цен"},
                {to: "/price-modeling", name: "Моделирование цены"}
            ]
        }
    }
}
</script>

<style scoped>
.app-bar-clean {
    box-shadow: none !important;
    border-bottom: none !important;
}

.router-link-active {
    color: rgb(6, 4, 119);
}

.nav-row {
    display: flex;
    flex-wrap: nowrap;
    justify-content: center;
    /* ТОЛЬКО для адаптивности — прокрутка, остальное как было */
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
}

.nav-row::-webkit-scrollbar {
    display: none;
}

.nav-link {
    flex-shrink: 1;
    min-width: 80px;
}

.nav-btn {
    white-space: nowrap;
    padding-left: 8px;
    padding-right: 8px;
    font-size: 14px;
    width: 100%;
    box-sizing: border-box;
}

/* На мобильных прижимаем влево, чтобы прокрутка работала от начала */
@media (max-width: 959px) {
    .nav-row {
        justify-content: flex-start;
        padding: 0 8px;
    }
    .nav-link {
        flex-shrink: 0;
    }
}
</style>
