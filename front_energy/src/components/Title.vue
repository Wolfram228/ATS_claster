<template>
    <v-app-bar app flat class="app-bar-clean">
        <v-container class="px-2 px-md-4">
            <div class="d-flex align-center w-100">
                <!-- Логотип и название -->
                <div class="d-flex align-center">
                    <!-- Уменьшили логотип. На мобильных 32px, на десктопе 48px -->
                    <v-img :src="icon" class="logo-img me-2" />
                    <div class="d-flex flex-column" align="left">
                        <p class="title1">ТокАналитика</p>
                        <!-- Скрываем подзаголовок на мобильных -->
                        <p class="title2 d-none d-sm-block">Анализ рынка электроэнергии</p>
                    </div>
                </div>

                <v-spacer />

                <!-- Скрываем текст "Документация" на мобильных -->
                <a href="/docs/ru/sub-section/overview.html" class="me-3 d-none d-sm-block">
                    <v-btn class="doc-link" size="small">Документация</v-btn>
                </a>
                
                <!-- Кнопка личного кабинета. На мобильных только иконка, на десктопе текст -->
                <router-link to="/lk">
                    <v-btn color="primary" variant="outlined" class="profile-btn" size="small">
                        <v-icon left size="small">mdi-account</v-icon>
                        <span class="d-none d-sm-inline">Личный кабинет</span>
                    </v-btn>
                </router-link>
            </div>
        </v-container>
    </v-app-bar>
</template>

<script>
import icon from "../assets/logo.png"
export default {
    data() {
        return { icon }
    }
}
</script>

<style scoped>
.app-bar-clean {
    box-shadow: none !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.08) !important; /* Легкая полоска снизу */
}

/* Логотип */
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
</style>
