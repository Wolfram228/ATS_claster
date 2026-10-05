<template>
    <v-menu
        v-model="visible"
        :close-on-content-click="false"
        location="top end"
        offset="10"
    >
        <template #activator="{ props }">
            <button
                v-bind="props"
                type="button"
                class="hint-formula__trigger"
                aria-label="Показать формулу"
            >
                ?
            </button>
        </template>

        <div class="hint-formula__content">
            <slot />
        </div>
    </v-menu>
</template>

<script>
export default {
    name: 'HintFormula',

    data() {
        return {
            visible: false,
        }
    },
}
</script>

<style>
.hint-formula__content {
    width: 440px;
    padding: 12px 16px;
    background-color: #fff;
    color: #333;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    font-size: 13px;
    text-align: center;
    box-sizing: border-box;
}
</style>

<style scoped>
.hint-formula__trigger {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 18px;
    height: 18px;
    padding: 0;
    border: none;
    border-radius: 50%;
    background-color: #4285f4;
    color: #fff;
    font-size: 12px;
    font-weight: bold;
    line-height: 1;
    cursor: pointer;
    transition: background-color 0.2s ease;
}

.hint-formula__trigger:hover {
    background-color: #3367d6;
}
</style>
