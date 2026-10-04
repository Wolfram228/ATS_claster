<template>
    <span class="hint-formula">
        <button
            type="button"
            class="hint-formula__trigger"
            :aria-expanded="visible"
            aria-label="Показать формулу"
            @click.stop="toggle"
        >
            ?
        </button>

        <transition name="hint-formula-fade">
            <span
                v-if="visible"
                class="hint-formula__content"
                @click.stop
            >
                <slot />
            </span>
        </transition>
    </span>
</template>

<script>
export default {
    name: 'HintFormula',

    data() {
        return {
            visible: false,
        }
    },

    methods: {
        toggle() {
            this.visible = !this.visible
        },
        close() {
            this.visible = false
        },
    },

    mounted() {
        document.addEventListener('click', this.close)
    },

    beforeUnmount() {
        document.removeEventListener('click', this.close)
    },
}
</script>

<style scoped>
.hint-formula {
    position: relative;
    display: inline-flex;
    align-items: center;
    vertical-align: middle;
}

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

.hint-formula__content {
    position: absolute;
    bottom: calc(100% + 10px);
    right: 0;
    z-index: 1000;
    width: 280px;
    padding: 12px 16px;
    background-color: #fff;
    color: #333;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    font-size: 13px;
    line-height: 1.5;
    text-align: center;
    white-space: normal;
    box-sizing: border-box;
}

.hint-formula__content::after {
    content: '';
    position: absolute;
    top: 100%;
    right: 6px;
    border-width: 8px;
    border-style: solid;
    border-color: #fff transparent transparent transparent;
}

.hint-formula-fade-enter-active,
.hint-formula-fade-leave-active {
    transition: opacity 0.15s ease, transform 0.15s ease;
}
.hint-formula-fade-enter-from,
.hint-formula-fade-leave-to {
    opacity: 0;
    transform: translateY(5px);
}
</style>
