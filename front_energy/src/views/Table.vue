<template>
    <v-container>
        <v-row>
            <v-col cols="12" md="4">
                <v-text-field
                v-model="selectedDateBefore"
                label="Отображать с:"
                type="datetime-local"
                hide-details
                ></v-text-field>
            </v-col>
            <v-col cols="12" md="4">
                <v-text-field
                v-model="selectedDateAfter"
                label="Отображать до:"
                type="datetime-local"
                hide-details
                ></v-text-field>
            </v-col>
            <v-col cols="12" md="4">
                <v-menu location="bottom">
                    <template v-slot:activator="{ props }">
                        <v-btn color="blue-grey-lighten-5" v-bind="props" min-height="55px" block> {{ selectedRegion }} </v-btn>
                    </template>

                    <v-list style="max-height: 300px">
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
            </v-col>
        </v-row>
        <v-row>
            <v-data-table-virtual
                :headers="headers"
                :items="virtualBoats"
                height="1055"
                item-value="date"
                fixed-header
                style="border: 1px solid rgba(0, 0, 0, 0.2);"
            >
                <template #headers="{ columns }">
                    <tr>
                    <th v-for="col in columns" :key="col.key" class="px-2">
                        <div class="flex flex-col items-start">
                        <span>{{ col.title }}</span>

                        <!-- 🔸 Фильтр -->
                        <v-text-field
                            v-model="filters[col.key]"
                            density="compact"
                            variant="underlined"
                            hide-details
                            class="mt-1 w-32"
                        />
                        </div>
                    </th>
                    </tr>
                </template>
                <template #no-data>
                    <div class="text-center pa-4">
                        <span v-if="loading">Загрузка данных...</span>
                        <span v-else>Данные отсутствуют</span>
                    </div>
                </template>
            </v-data-table-virtual>
        </v-row>
    </v-container>
</template>

<script>
// import boats from "../assets/energy_data_updated.json"
import regions from "../assets/regions.json"

export default {
    data() {
        return {
            headers: [
                {title: 'Дата', key: 'timestamp'},
                {title: 'Субъект РФ', key: 'region'},
                {title: 'Час', key: 'hour'},
                {title: 'ГЭС', key: 'plan_GES'},
                {title: 'АЭС', key: 'plan_AES'},
                {title: 'ТЭС', key: 'plan_TES'},
                {title: 'СЭС', key: 'plan_SES'},
                {title: 'ВЭС', key: 'plan_VES'},
                {title: 'Прочие ВИЭ', key: 'plan_other'},
                {title: 'ГЭС (мин тех)', key: 'techmin_GES'},
                {title: 'АЭС (мин тех)', key: 'techmin_AES'},
                {title: 'ТЭС (мин тех)', key: 'techmin_TES'},
                {title: 'СЭС (мин тех)', key: 'techmin_SES'},
                {title: 'ВЭС (мин тех)', key: 'techmin_VES'},
                {title: 'Прочие ВИЭ (мин тех)', key: 'techmin_other'},
                {title: 'ГЭС (мин техн)', key: 'technomin_GES'},
                {title: 'АЭС (мин техн)', key: 'technomin_AES'},
                {title: 'ТЭС (мин техн)', key: 'technomin_TES'},
                {title: 'СЭС (мин техн)', key: 'technomin_SES'},
                {title: 'ВЭС (мин техн)', key: 'technomin_VES'},
                {title: 'Прочие ВИЭ (мин техн)', key: 'technomin_other'},
                {title: 'ГЭС (макс тех)', key: 'techmax_GES'},
                {title: 'АЭС (макс тех)', key: 'techmax_AES'},
                {title: 'ТЭС (макс тех)', key: 'techmax_TES'},
                {title: 'СЭС (макс тех)', key: 'techmax_SES'},
                {title: 'ВЭС (макс тех)', key: 'techmax_VES'},
                {title: 'Прочие ВИЭ (макс тех)', key: 'techmax_other'},
                {title: 'План потребления', key: 'plan_consumption'},
                {title: 'План экспорта', key: 'plan_export'},
                {title: 'План импорта', key: 'plan_import'},
                {title: 'Цена покупки', key: 'price_buy'},
                {title: 'Цена продажи', key: 'price_sell'},
                {title: 'Полный план', key: 'full_plan'}
            ],
            boats: undefined,
            regions,
            filters: {},
            selectedRegion: undefined,
            selectedDateBefore: undefined,
            selectedDateAfter: undefined,
            loading: false,
        }
    },
    methods: {
        formatDateTime(dt) {
            return dt.slice(0, 19).replace('T', ' ');
        }
    },
    computed: {
        virtualBoats() {
            if (!this.boats) return [];
            return [...Array(10000).keys()].map(i => {
                // клонируем объект из boats
                const boat = { ...this.boats[i % this.boats.length] }

                boat.timestamp = this.formatDateTime(boat.timestamp);

                return boat
            })
        },
        filteredItems() {
            return this.virtualBoats.filter(item =>
                Object.entries(this.filters).every(([key, value]) => {
                if (!value) return true
                const cell = item[key]
                return cell != null && String(cell).toLowerCase().includes(value.toLowerCase())
                })
            )
        }
    },
    async created() {
        this.selectedRegion = regions[0].value;

        let currentDate = new Date().toISOString().slice(0, 16).replace('T', ' ')
        let afterCurrentDate = new Date(Date.now() + 86400000).toISOString().slice(0, 16).replace('T', ' ')
        this.selectedDateBefore = currentDate; 
        this.selectedDateAfter = afterCurrentDate; 

        try {
            this.loading = true;
            const response = await fetch(`https://cloud-a.istu.edu/api/table?from=${this.selectedDateBefore}&to=${this.selectedDateAfter}`);
            this.boats = await response.json();
        } catch (error) {
            this.errorMessage = error;
        } finally {
            this.loading = false;
        }

        this.headers.forEach(h => {this.filters[h.key] = ''})
    }
}
</script>