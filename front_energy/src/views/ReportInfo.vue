<template>
    <v-container>
        <v-row>
            <v-col 
            cols="3" 
            sm="6"
            lg="3"
            v-for="ri in reportInfo">
                <InfoCard>
                    <template v-slot:title>{{ ri.title }}</template>
                    <template v-slot:info1> {{ ri.info1 }}</template>
                    <template v-slot:info2> {{ ri.info2 }}</template>
                    <template v-slot:percentage>
                        <div 
                        class="text-caption" 
                        :class="ri.percentage.startsWith('-') ? 'text-error' : 'text-success'"
                        >
                            {{ ri.percentage }}
                        </div>
                    </template>
                </InfoCard>
            </v-col>
        </v-row>
        <v-row>
            <v-col>
                <v-card
                class="pa-4"
                elevation="1"
                rounded="lg"
                variant="outlined"
                style="border-color: rgba(0, 0, 0, 0.2)"
                >
                    <div class="text-h5 font-weight-bold" align="left">Динамика потребления</div>
                    <div class="text-body-2 text-grey-darken-1 mt-1" align="left">Потребление электроэнергии за 2024 год</div>
                    <div class="text-body-2 text-grey-darken-1 mt-6" align="left">Интерактивные графики</div>
                    <v-container class="d-flex">
                        <v-btn class="flex-grow-1 me-3" color="blue-grey-lighten-5" v-on:click="GraphType = 1"> Объём по времени </v-btn>
                        <v-btn class="flex-grow-1 me-3" color="blue-grey-lighten-5" v-on:click="GraphType = 2"> Цена по времени </v-btn>
                        <v-btn class="flex-grow-1 me-3" color="blue-grey-lighten-5" v-on:click="GraphType = 3"> Объём и цена по времени </v-btn>
                    </v-container>
                    <v-container class="d-flex">
                        <v-text-field
                        v-model="selectedDateBefore"
                        label="Отображать с:"
                        type="date"
                        class="flex-grow-1 me-3"
                        ></v-text-field>
                        <v-text-field
                        v-model="selectedDateAfter"
                        label="Отображать до:"
                        type="date"
                        class="flex-grow-1 me-3"
                        ></v-text-field>
                        <v-menu :location="center" class="flex-grow-1 me-3">
                            <template v-slot:activator="{ props }">
                                <v-btn color="blue-grey-lighten-5" v-bind="props" min-height="55px"> {{ selectedRegion }} </v-btn>
                            </template>

                            <v-list>
                                <v-list-item
                                v-for="(region, id) in regions"
                                :key="id"
                                :value="id"
                                v-on:click="selectedRegion = region.value"
                                >
                                <v-list-item-title>{{ region.value }}</v-list-item-title>
                                </v-list-item>
                            </v-list>
                        </v-menu>
                    </v-container>

                    <!-- Первый график -->
                    <v-container v-if="GraphType === 1">
                        <v-img :src="graph2" max-height="600px" class="mt-3" cover style="border: 1px solid rgba(0, 0, 0, 0.2);" />
                    </v-container>
                    <!-- Второй график -->
                    <v-container v-if="GraphType === 2">
                        <v-img :src="graph2" max-height="600px" class="mt-3" cover style="border: 1px solid rgba(0, 0, 0, 0.2);" />
                    </v-container>
                    <!-- Третий график -->
                    <v-container v-if="GraphType === 3">
                        <v-img :src="graph2" max-height="600px" class="mt-3" cover style="border: 1px solid rgba(0, 0, 0, 0.2);" />
                    </v-container>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import InfoCard from "../components/InfoCard.vue"
import reportInfo from "../assets/reportInfo.json"
import graph2 from "../assets/graph2.jpg"
import regions from "../assets/regions.json"

export default {
    props: {
        reportId: {type: Number, required: true}
    },
    components: {InfoCard},
    data() {
        return {
            reportInfo,
            GraphType: 1,
            selectedDateBefore: undefined,
            selectedDateAfter: undefined,
            graph2,
            regions,
            selectedRegion: undefined,
        }
    },
    created() {
        this.selectedRegion = regions[0].value
    }
}
</script>