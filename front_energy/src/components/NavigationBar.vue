<template>
    <v-app-bar app flat class="app-bar-clean">
        <v-container class="px-0 px-md-4">
            <div class="nav-scroll-container">
                <div
                    v-for="link in links"
                    :key="link.to"
                    class="nav-link"
                >
                    <router-link :to="link.to">
                        <v-btn class="nav-btn">{{ link.name }}</v-btn>
                    </router-link>
                </div>
            </div>
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

/* Контейнер для свайпа */
.nav-scroll-container {
    display: flex;
    align-items: center;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none; 
    justify-content: center; /* По центру на десктопе */
    padding: 8px 0;
}

.nav-scroll-container::-webkit-scrollbar {
    display: none;
}

/* На мобильных прижимаем влево для удобного свайпа */
@media (max-width: 959px) {
    .nav-scroll-container {
        justify-content: flex-start;
        padding: 8px 16px;
    }
}

.nav-link {
    flex-shrink: 0;
    margin: 0 2px;
}

/* Твои старые стили кнопок */
.nav-btn {
    white-space: nowrap;
    padding-left: 8px;
    padding-right: 8px;
    font-size: 14px;
    width: 100%;
    box-sizing: border-box;
    text-transform: none;
}

.router-link-active .nav-btn {
    font-weight: 700;
}
</style>
