<template>
    <v-app-bar app flat class="app-bar-clean">
        <v-container class="px-0">
            <!-- Убрали justify="center", чтобы при переполнении скролл начинался слева -->
            <div class="nav-scroll-container">
                <router-link
                    v-for="link in links"
                    :key="link.to"
                    :to="link.to"
                    class="nav-link"
                >
                    <v-btn class="nav-btn" variant="text">{{ link.name }}</v-btn>
                </router-link>
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

/* Контейнер для свайпа */
.nav-scroll-container {
    display: flex;
    align-items: center;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch; /* Плавный скролл на iOS */
    scrollbar-width: none; /* Скрываем скроллбар в Firefox */
    justify-content: flex-start;
    padding: 0 8px;
}

/* Скрываем скроллбар в Chrome/Safari */
.nav-scroll-container::-webkit-scrollbar {
    display: none;
}

/* На десктопе центрируем */
@media (min-width: 960px) {
    .nav-scroll-container {
        justify-content: center;
        padding: 0;
    }
}

.nav-link {
    flex-shrink: 0; /* Запрещаем сжимать кнопки */
    text-decoration: none;
}

.nav-btn {
    white-space: nowrap;
    font-size: 13px;
    padding: 0 12px;
    text-transform: none;
    font-weight: 500;
    color: #444;
}

.router-link-active .nav-btn {
    color: rgb(6, 4, 119);
    font-weight: 700;
    background: rgba(6, 4, 119, 0.05);
}
</style>
