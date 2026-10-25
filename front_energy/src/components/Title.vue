<template>
    <v-app-bar app flat class="app-bar-clean" extension-height="52">
        <!-- Верхняя строка: Логотип + Кнопки -->
        <v-container class="px-2 px-md-4 d-flex align-center w-100">
            <!-- Логотип и название -->
            <div class="d-flex align-center flex-shrink-0">
                <v-img :src="icon" class="logo-img me-2" />
                <div class="d-flex flex-column" align="left">
                    <p class="title1">ТокАналитика</p>
                    <p class="title2 d-none d-sm-block">Анализ рынка электроэнергии</p>
                </div>
            </div>

            <!-- Навигация (на десктопе) -->
            <div class="nav-row d-none d-md-flex flex-grow-1 px-4">
                <div v-for="link in links" :key="link.to" class="nav-link">
                    <router-link :to="link.to">
                        <v-btn class="nav-btn">{{ link.name }}</v-btn>
                    </router-link>
                </div>
            </div>

            <!-- Распорка (на мобильных, чтобы прижать кнопки вправо) -->
            <v-spacer class="d-md-none" />

            <!-- Кнопки справа -->
            <div class="d-flex align-center flex-shrink-0">
                <a href="/docs/ru/sub-section/overview.html" class="me-3 d-none d-sm-block">
                    <v-btn class="doc-link" size="small">Документация</v-btn>
                </a>
                
                <router-link to="/lk">
                    <v-btn color="primary" variant="outlined" class="profile-btn" size="small">
                        <v-icon left size="small">mdi-account</v-icon>
                        <span class="d-none d-sm-inline">Личный кабинет</span>
                    </v-btn>
                </router-link>
            </div>
        </v-container>

        <!-- Навигация (на мобильных и планшетах) -->
        <v-app-bar-extension class="d-md-none py-0">
            <div class="nav-row w-100 h-100 px-2">
                <div v-for="link in links" :key="link.to" class="nav-link">
                    <router-link :to="link.to">
                        <v-btn class="nav-btn">{{ link.name }}</v-btn>
                    </router-link>
                </div>
            </div>
        </v-app-bar-extension>
    </v-app-bar>
</template>

<script>
import icon from "../assets/logo.png"

export default {
    data() {
        return {
            icon,
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
    border-bottom: 1px solid rgba(0, 0, 0, 0.08) !important;
}

/* --- Стили для Title --- */
.logo-img {
    width: 32px;
    height: 32px;
    object-fit: contain;
}
@media (min-width: 600px) {
    .logo-img { width: 48px; height: 48px; }
}

.title1 {
    margin: 0;
    font-weight: bold;
    font-size: 1.1rem;
    font-family: monospace;
    color: rgb(7, 0, 100);
    line-height: 1.2;
}
@media (min-width: 600px) {
    .title1 { font-size: 1.4rem; }
}

.title2 {
    margin: 0;
    font-size: 0.8rem;
    color: rgb(0, 6, 94);
    line-height: 1.2;
}

p { margin: 0; }

.doc-link :deep(.v-btn__overlay),
.doc-link :deep(.v-btn__underlay) {
    opacity: 0 !important;
}
a { color: rgb(39, 9, 146); text-decoration: none; }
.profile-btn {
    border-color: rgb(7, 0, 100);
    color: rgb(7, 0, 100);
    font-size: 0.75rem;
}

/* --- Стили для Навигации --- */
.nav-row {
    display: flex;
    flex-wrap: nowrap;
    justify-content: center;
    align-items: center;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    height: 100%;
}
.nav-row::-webkit-scrollbar {
    display: none;
}

.nav-link {
    flex-shrink: 0;
    min-width: 80px;
    padding: 0 2px;
}

.nav-btn {
    white-space: nowrap;
    padding-left: 8px;
    padding-right: 8px;
    font-size: 14px;
    width: 100%;
    box-sizing: border-box;
    text-transform: none; /* Убирает CAPS, если нужно чтобы было как в навигации */
}

/* На мобильных прижимаем влево для свайпа */
@media (max-width: 959px) {
    .nav-row {
        justify-content: flex-start;
        padding: 0 8px;
    }
}
</style>
