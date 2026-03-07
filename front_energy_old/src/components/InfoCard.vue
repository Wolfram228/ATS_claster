<template>
    <v-card
    class="pa-4"
    min-width="250"
    elevation="1"
    rounded="lg"
    variant="outlined"
    style="border-color: rgba(0, 0, 0, 0.2)"
    >
        <div class="text-body-2 text-grey-darken-1" align="left">
            <slot name="title">
                Среднесуточное
            </slot>
        </div>

        <div class="text-h5 font-weight-bold mt-2" align="left">
            <slot name="info1">
                78.2 кВт·ч
            </slot>
        </div>

        <div class="d-flex justify-space-between align-end mt-4">
            <div class="text-caption text-grey-darken-1">
                <slot name="info2">
                    в день
                </slot>
            </div>
            <slot name="percentage">
                <div class="text-caption text-error">
                        ↘ -0.8%
                </div>
            </slot>
        </div>
    </v-card>
</template>

<script>

</script>