<template>
    <v-app-bar app flat class="app-bar-clean">
        <div class="nav-row">
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
    align-items: center;
    width: 100%;
    height: 100%;
    padding: 0 8px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    /* Гарантируем, что padding не схлопывается и прокрутка начинается с начала */
    box-sizing: border-box;
}

.nav-row::-webkit-scrollbar {
    display: none;
}

.nav-link {
    flex-shrink: 0;
    min-width: 80px;
    /* Небольшой отступ между кнопками, как было изначально */
    padding: 0 2px;
}

.nav-btn {
    white-space: nowrap;
    padding-left: 8px;
    padding-right: 8px;
    font-size: 14px;
    width: 100%;
    box-sizing: border-box;
}

/* На мобильных — прижимаем влево, но теперь прокрутка работает от самого начала */
@media (max-width: 959px) {
    .nav-row {
        justify-content: flex-start;
    }
    .nav-link {
        flex-shrink: 0;
    }
}
</style>
