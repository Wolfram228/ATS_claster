<template>
    <v-app-bar app flat class="app-bar-clean">
        <v-container>
            <div class="d-flex align-center w-100">
                <!-- слева: логотип и название -->
                <div class="d-flex align-center">
                    <v-img :src="icon" width="45" height="45" class="me-2" />
                    <div class="d-flex flex-column" align="left">
                        <p class="title1">ТокАналитика</p>
                        <p class="title2">Анализ рынка электроэнергии</p>
                    </div>
                </div>

                <v-spacer />

                <a href="/docs/ru/sub-section/overview.html" class="me-3">
                    <v-btn class="doc-link">Документация</v-btn>
                </a>
                <router-link to="/lk">
                    <v-btn color="primary" variant="outlined" class="profile-btn">
                        <v-icon left>mdi-account</v-icon>
                        Личный кабинет
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
    border-bottom: none !important;
}

.title1 {
    margin: 0;
    font-weight: bold;
    font-size: larger;
    font-family: monospace;
    color: rgb(7, 0, 100);
}
.title2 {
    margin: 0;
    font-size: medium;
    color: rgb(0, 6, 94);
}
p { margin: 0; }
.doc-link :deep(.v-btn__overlay),
.doc-link :deep(.v-btn__underlay) {
    opacity: 0 !important;
}
a { color: rgb(39, 9, 146); }
.profile-btn {
    border-color: rgb(7, 0, 100);
    color: rgb(7, 0, 100);
}
</style>
