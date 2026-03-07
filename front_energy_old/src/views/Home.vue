<template>
    <v-container>
        <v-card
        variant="outlined"
        rounded="lg"
        elevation="1" 
        style="border-color: rgba(0, 0, 0, 0.2)">
            <v-card-text>
                <div class="text-h5 font-weight-bold" align="center">Динамика потребления</div>
                <v-row justify="center">
                    <v-img :src=graph alt="" max-height="500px" max-width="500px" class="mt-4" style="border: 1px solid rgba(0, 0, 0, 0.2);" />
                </v-row>
                <div class="text-h5 font-weight-bold mt-5" align="center">Объёмы по генераторам: 2025-10-10 vs 2025-10-11</div>
                <v-img :src=graph2 alt="" max-height="500px" class="mt-1" style="border: 1px solid rgba(0, 0, 0, 0.2);" />
            </v-card-text>
        </v-card>
    </v-container>
</template>

<script>
import graph from "../assets/home-graph.png"
import graph2 from "../assets/home-graph2.png"
export default {
    data() {
        return {
            graph,
            graph2
        }
    }
}
</script>