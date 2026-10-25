<template>
    <v-app-bar app flat class="app-bar-clean" extension-height="52">
        <!-- Верхняя строка: Логотип + Кнопки -->
        <v-container class="px-2 px-md-4 d-flex align-center w-100">
            
            <!-- Логотип и название (теперь это ссылка на главную) -->
            <router-link to="/" class="brand-link d-flex align-center flex-shrink-0 text-decoration-none">
                <v-img :src="icon" class="logo-img me-2" />
                <div class="d-flex flex-column" align="left">
                    <p class="title1">ТокАналитика</p>
                    <p class="title2 d-none d-sm-block">Анализ рынка электроэнергии</p>
                </div>
            </router-link>

            <!-- Навигация (на десктопе) -->
            <div class="nav-row d-none d-md-flex flex-grow-1 px-4">
                <div v-for="link in links" :key="link.to" class="nav-link">
                    <router-link :to="link.to" class="text-decoration-none">
                        <v-btn variant="text" class="nav-btn">{{ link.name }}</v-btn>
                    </router-link>
                </div>
            </div>

            <!-- Распорка (на мобильных, чтобы прижать кнопки вправо) -->
            <v-spacer class="d-md-none" />

            <!-- Кнопки справа -->
            <div class="d-flex align-center flex-shrink-0">
                <a href="/docs/ru/sub-section/overview.html" class="me-3 d-none d-sm-block text-decoration-none">
                    <v-btn class="doc-link" size="small">Документация</v-btn>
                </a>
                
                <!-- Кнопка Личного кабинета в виде "пилла" -->
                <router-link to="/lk" class="pill pill--primary">
                    <span class="d-none d-sm-inline">Личный кабинет</span>
                    <span class="pill__dot">
                        <v-icon size="small" color="primary">mdi-account</v-icon>
                    </span>
                </router-link>
            </div>
        </v-container>

        <!-- Навигация (на мобильных и планшетах) -->
        <v-app-bar-extension class="d-md-none py-0">
            <div class="nav-row w-100 h-100 px-2">
                <div v-for="link in links" :key="link.to" class="nav-link">
                    <router-link :to="link.to" class="text-decoration-none">
                        <v-btn variant="text" class="nav-btn">{{ link.name }}</v-btn>
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

/* --- Стили для Логотипа и Названия --- */
.brand-link {
    color: inherit;
}
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

/* --- Стили для кнопки Документации --- */
.doc-link :deep(.v-btn__overlay),
.doc-link :deep(.v-btn__underlay) {
    opacity: 0 !important;
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

/* Возвращаем капс и делаем кнопки как "Документация" */
.nav-btn {
    white-space: nowrap;
    font-size: 14px;
    width: 100%;
    box-sizing: border-box;
    text-transform: uppercase; /* Капс */
    font-weight: 500;
    letter-spacing: 0.0892857143em; /* Стандартный межбуквенный интервал Vuetify для капса */
}

/* Подсветка активной кнопки */
.router-link-active .nav-btn {
    color: rgb(6, 4, 119);
    font-weight: 700;
}

@media (max-width: 959px) {
    .nav-row {
        justify-content: flex-start;
        padding: 0 8px;
    }
}

/* --- Стили для круглого "Пилла" (Личный кабинет) --- */
.pill {
    display: inline-flex;
    align-items: center;
    gap: 14px;
    padding: 6px 6px 6px 20px;
    border-radius: 999px;
    text-decoration: none;
    white-space: nowrap;
    transition: transform 0.2s ease, background-color 0.2s ease;
    font-size: 14px;
    font-weight: 500;
}

.pill:hover { 
    transform: translateY(-2px); 
    background-color: rgb(20, 10, 130); /* Чуть светлее при наведении */
}

/* Тёмно-синяя тема для пилла */
.pill--primary {
    background: rgb(7, 0, 100);
    color: #fff !important;
}

/* Кружок внутри пилла */
.pill__dot {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #fff;
    color: rgb(7, 0, 100);
    display: inline-flex;
    align-items: center;
    justify-content: center;
}

/* На мобильных оставляем только круг с иконкой */
@media (max-width: 599px) {
    .pill {
        padding: 6px;
        gap: 0;
    }
    .pill__dot {
        width: 34px;
        height: 34px;
    }
}
</style>
