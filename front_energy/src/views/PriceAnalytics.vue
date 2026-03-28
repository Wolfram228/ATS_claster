<template>
    <v-container fluid class="pa-4">
        <v-card
            class="pa-4 mb-4"
            elevation="1"
            rounded="lg"
            variant="outlined"
            style="border-color: rgba(0, 0, 0, 0.2)"
        >
            <div class="text-h5 font-weight-bold" align="left">Параметры анализа</div>
            <div class="text-body-2 text-grey-darken-1 mt-1" align="left">
                Средневзвешенные цены продажи электроэнергии по регионам и федеральным округам
            </div>

            <v-container class="px-0 pt-6">
                <v-row>
                    <v-col cols="12" md="3">
                        <v-text-field
                            v-model="dateFrom"
                            label="Дата с"
                            type="date"
                            hide-details
                        />
                    </v-col>

                    <v-col cols="12" md="3">
                        <v-text-field
                            v-model="dateTo"
                            label="Дата по"
                            type="date"
                            hide-details
                        />
                    </v-col>

                    <v-col cols="12" md="2">
                        <v-select
                            v-model="aggregation"
                            :items="aggregationItems"
                            item-title="title"
                            item-value="value"
                            label="Агрегация"
                            hide-details
                        />
                    </v-col>

                    <v-col cols="12" md="4">
                        <v-btn
                            color="blue-grey-lighten-1"
                            min-height="55px"
                            block
                            :loading="priceAnalyticsLoading"
                            :disabled="isDateInvalid"
                            @click="loadData"
                        >
                            Применить
                        </v-btn>

                        <div v-if="isDateInvalid" class="text-error mt-2">
                            Введён некорректный диапазон дат
                        </div>

                        <div
                            v-else-if="hasPendingChanges"
                            class="text-error mt-2"
                        >
                            Вы не применили изменения
                        </div>
                    </v-col>
                </v-row>

                <v-row class="mt-1">
                    <v-col cols="12" md="6">
                        <v-select
                            v-model="selectedDistrictsDraft"
                            :items="districtItems"
                            label="Федеральные округа"
                            multiple
                            chips
                            clearable
                            hide-details
                        />
                    </v-col>

                    <v-col cols="12" md="6">
                        <v-select
                            v-model="selectedRegionsDraft"
                            :items="availableRegionItemsDraft"
                            label="Регионы"
                            multiple
                            chips
                            clearable
                            hide-details
                        />
                    </v-col>
                </v-row>
            </v-container>
        </v-card>

        <v-row v-if="priceAnalyticsError">
            <v-col cols="12">
                <v-alert type="error" variant="tonal">
                    Ошибка загрузки данных
                </v-alert>
            </v-col>
        </v-row>

        <v-card
            v-if="loadedOnce"
            class="pa-4 mb-4"
            elevation="1"
            rounded="lg"
            variant="outlined"
            style="border-color: rgba(0, 0, 0, 0.2)"
        >
            <div class="text-h5 font-weight-bold" align="left">Таблицы</div>
            <div class="text-body-2 text-grey-darken-1 mt-1" align="left">
                Сводные значения средних цен и объёмов
            </div>

            <v-container class="px-0 pt-6">
                <v-row>
                    <v-col cols="12" md="6">
                        <v-btn
                            :color="tableView === 'regions' ? 'blue-grey-lighten-1' : 'blue-grey-lighten-5'"
                            block
                            @click="tableView = 'regions'"
                        >
                            По регионам
                        </v-btn>
                    </v-col>
                    <v-col cols="12" md="6">
                        <v-btn
                            :color="tableView === 'districts' ? 'blue-grey-lighten-1' : 'blue-grey-lighten-5'"
                            block
                            @click="tableView = 'districts'"
                        >
                            По федеральным округам
                        </v-btn>
                    </v-col>
                </v-row>
            </v-container>

            <v-container class="px-0 pt-4">
                <v-container v-if="priceAnalyticsLoading">
                    Загрузка данных...
                </v-container>

                <v-container v-else-if="!currentTableHasRows">
                    <v-alert type="info" variant="tonal">
                        Нет данных по выбранным параметрам
                    </v-alert>
                </v-container>

                <v-container v-else class="px-0">
                    <v-data-table
                        v-if="tableView === 'regions'"
                        :headers="regionHeaders"
                        :items="regionTableRows"
                        density="comfortable"
                        items-per-page="15"
                    />

                    <v-data-table
                        v-else
                        :headers="districtHeaders"
                        :items="districtTableRows"
                        density="comfortable"
                        items-per-page="15"
                    />
                </v-container>
            </v-container>
        </v-card>

        <v-card
            v-if="loadedOnce"
            class="pa-4"
            elevation="1"
            rounded="lg"
            variant="outlined"
            style="border-color: rgba(0, 0, 0, 0.2)"
        >
            <div class="text-h5 font-weight-bold" align="left">Графики</div>
            <div class="text-body-2 text-grey-darken-1 mt-1" align="left">
                Динамика средних цен по выбранной агрегации
            </div>

            <v-container class="px-0 pt-6">
                <v-row>
                    <v-col cols="12" md="6">
                        <v-btn
                            :color="chartView === 'regions' ? 'blue-grey-lighten-1' : 'blue-grey-lighten-5'"
                            block
                            @click="chartView = 'regions'"
                        >
                            По регионам
                        </v-btn>
                    </v-col>
                    <v-col cols="12" md="6">
                        <v-btn
                            :color="chartView === 'districts' ? 'blue-grey-lighten-1' : 'blue-grey-lighten-5'"
                            block
                            @click="chartView = 'districts'"
                        >
                            По федеральным округам
                        </v-btn>
                    </v-col>
                </v-row>
            </v-container>

            <v-container class="px-0 pt-4">
                <v-container v-if="priceAnalyticsLoading">
                    Загрузка данных...
                </v-container>

                <v-container v-else-if="!currentChartHasRows">
                    <v-alert type="info" variant="tonal">
                        Нет данных по выбранным параметрам
                    </v-alert>
                </v-container>

                <v-container v-else class="px-0">
                    <VChart
                        v-if="chartView === 'regions'"
                        :option="regionChartOption"
                        class="mt-3"
                        style="height: 420px; border: 1px solid rgba(0,0,0,0.2);"
                    />

                    <VChart
                        v-else
                        :option="districtChartOption"
                        class="mt-3"
                        style="height: 420px; border: 1px solid rgba(0,0,0,0.2);"
                    />
                </v-container>
            </v-container>
        </v-card>
    </v-container>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'

const DISTRICT_BY_REGION = {
    'Алтайский край': 'Сибирский ФО',
    'Архангельская область': 'Северо-Западный ФО',
    'Астраханская область': 'Южный ФО',
    'Белгородская область': 'Центральный ФО',
    'Брянская область': 'Центральный ФО',
    'Владимирская область': 'Центральный ФО',
    'Волгоградская область': 'Южный ФО',
    'Вологодская область': 'Северо-Западный ФО',
    'Воронежская область': 'Центральный ФО',
    'Город Севастополь': 'Южный ФО',
    'Забайкальский край': 'Дальневосточный ФО',
    'Ивановская область': 'Центральный ФО',
    'Иркутская область': 'Сибирский ФО',
    'Кабардино-Балкарская Республика': 'Северо-Кавказский ФО',
    'Калужская область': 'Центральный ФО',
    'Карачаево-Черкесская Республика': 'Северо-Кавказский ФО',
    'Кемеровская область': 'Сибирский ФО',
    'Кировская область': 'Приволжский ФО',
    'Костромская область': 'Центральный ФО',
    'Краснодарский край': 'Южный ФО',
    'Красноярский край': 'Сибирский ФО',
    'Курганская область': 'Уральский ФО',
    'Курская область': 'Центральный ФО',
    'Ленинградская область': 'Северо-Западный ФО',
    'Липецкая область': 'Центральный ФО',
    'Московская область': 'Центральный ФО',
    'Мурманская область': 'Северо-Западный ФО',
    'Нижегородская область': 'Приволжский ФО',
    'Новгородская область': 'Северо-Западный ФО',
    'Новосибирская область': 'Сибирский ФО',
    'Омская область': 'Сибирский ФО',
    'Оренбургская область': 'Приволжский ФО',
    'Орловская область': 'Центральный ФО',
    'Пензенская область': 'Приволжский ФО',
    'Пермский край': 'Приволжский ФО',
    'Псковская область': 'Северо-Западный ФО',
    'Республика Алтай': 'Сибирский ФО',
    'Республика Башкортостан': 'Приволжский ФО',
    'Республика Бурятия': 'Дальневосточный ФО',
    'Республика Дагестан': 'Северо-Кавказский ФО',
    'Республика Ингушетия': 'Северо-Кавказский ФО',
    'Республика Калмыкия': 'Южный ФО',
    'Республика Карелия': 'Северо-Западный ФО',
    'Республика Коми': 'Северо-Западный ФО',
    'Республика Крым': 'Южный ФО',
    'Республика Марий Эл': 'Приволжский ФО',
    'Республика Мордовия': 'Приволжский ФО',
    'Республика Северная Осетия-Алания': 'Северо-Кавказский ФО',
    'Республика Татарстан': 'Приволжский ФО',
    'Республика Тыва': 'Сибирский ФО',
    'Республика Хакасия': 'Сибирский ФО',
    'Ростовская область': 'Южный ФО',
    'Рязанская область': 'Центральный ФО',
    'Самарская область': 'Приволжский ФО',
    'Саратовская область': 'Приволжский ФО',
    'Свердловская область': 'Уральский ФО',
    'Смоленская область': 'Центральный ФО',
    'Ставропольский край': 'Северо-Кавказский ФО',
    'Тамбовская область': 'Центральный ФО',
    'Тверская область': 'Центральный ФО',
    'Томская область': 'Сибирский ФО',
    'Тульская область': 'Центральный ФО',
    'Тюменская область': 'Уральский ФО',
    'Удмуртская Республика': 'Приволжский ФО',
    'Ульяновская область': 'Приволжский ФО',
    'Челябинская область': 'Уральский ФО',
    'Чеченская Республика': 'Северо-Кавказский ФО',
    'Чувашская Республика-Чувашия': 'Приволжский ФО',
    'Ярославская область': 'Центральный ФО',
}

export default {
    name: 'PriceAnalytics',

    data() {
        const { yesterday, today } = this.getInitialRange()

        return {
            loadedOnce: false,

            dateFrom: yesterday,
            dateTo: today,
            appliedDateFrom: yesterday,
            appliedDateTo: today,

            aggregation: 'day',
            appliedAggregation: 'day',
            aggregationItems: [
                { title: 'Сутки', value: 'day' },
                { title: 'Неделя', value: 'week' },
                { title: 'Месяц', value: 'month' },
            ],

            selectedDistrictsDraft: ['Сибирский ФО'],
            selectedRegionsDraft: ['Иркутская область'],

            appliedDistricts: ['Сибирский ФО'],
            appliedRegions: ['Иркутская область'],

            tableView: 'regions',
            chartView: 'regions',

            regionHeaders: [
                { title: 'Регион', key: 'region', align: "end" },
                { title: 'Федеральный округ', key: 'district', align: "end" },
                { title: 'Средняя цена продажи, руб./МВт·ч', key: 'avgPrice', align: "end" },
                { title: 'Суммарный объём выработки, МВт·ч', key: 'volume', align: "end" },
            ],

            districtHeaders: [
                { title: 'Федеральный округ', key: 'district', align: "end" },
                { title: 'Средняя цена продажи, руб./МВт·ч', key: 'avgPrice', align: "end" },
                { title: 'Суммарный объём выработки, МВт·ч', key: 'volume', align: "end" },
            ],
        }
    },

    computed: {
        ...mapState({
            priceAnalyticsRows: state => state.priceAnalyticsRows,
            priceAnalyticsLoading: state => state.priceAnalyticsLoading,
            priceAnalyticsError: state => state.priceAnalyticsError,
        }),
        ...mapGetters({
            storeRegions: 'staticRegions',
        }),

        districtItems() {
            return [
                'Центральный ФО',
                'Северо-Западный ФО',
                'Южный ФО',
                'Северо-Кавказский ФО',
                'Приволжский ФО',
                'Уральский ФО',
                'Сибирский ФО',
                'Дальневосточный ФО',
            ]
        },

        allRegionItems() {
            return this.storeRegions.map(item => item.value)
        },

        availableRegionItemsDraft() {
            if (!this.selectedDistrictsDraft.length) {
                return this.allRegionItems
            }

            return this.allRegionItems.filter(region => {
                return this.selectedDistrictsDraft.includes(this.getDistrict(region))
            })
        },

        isDateInvalid() {
            return !this.dateFrom || !this.dateTo || this.dateFrom > this.dateTo
        },

        hasPendingChanges() {
            return (
                this.dateFrom !== this.appliedDateFrom ||
                this.dateTo !== this.appliedDateTo ||
                this.aggregation !== this.appliedAggregation ||
                JSON.stringify([...this.selectedDistrictsDraft].sort()) !== JSON.stringify([...this.appliedDistricts].sort()) ||
                JSON.stringify([...this.selectedRegionsDraft].sort()) !== JSON.stringify([...this.appliedRegions].sort())
            )
        },

        /*filteredRows() {
            return this.priceAnalyticsRows.filter(row => {
                const region = row.region || ''
                const district = this.getDistrict(region)

                const districtOk = !this.appliedDistricts.length || this.appliedDistricts.includes(district)
                const regionOk = !this.appliedRegions.length || this.appliedRegions.includes(region)

                return districtOk && regionOk
            })
        },*/
        filteredRowsByDistricts() {
            return this.priceAnalyticsRows.filter(row => {
                const district = this.getDistrict(row.region || '')
                return !this.appliedDistricts.length || this.appliedDistricts.includes(district)
            })
        },

        filteredRowsByRegions() {
            return this.priceAnalyticsRows.filter(row => {
                const region = row.region || ''
                const district = this.getDistrict(region)

                const districtOk = !this.appliedDistricts.length || this.appliedDistricts.includes(district)
                const regionOk = !this.appliedRegions.length || this.appliedRegions.includes(region)

                return districtOk && regionOk
            })
        },

        regionTableRows() {
            const grouped = this.groupBy(this.filteredRowsByRegions, row => row.region || 'Не указан')

            return Object.keys(grouped)
                .map(region => {
                    const rows = grouped[region]
                    return {
                        region,
                        district: this.getDistrict(region),
                        avgPrice: this.formatNumber(this.getWeightedPrice(rows)),
                        volume: this.formatNumber(this.getTotalVolume(rows)),
                    }
                })
                .sort((a, b) => a.region.localeCompare(b.region, 'ru'))
        },

        districtTableRows() {
            const grouped = this.groupBy(this.filteredRowsByDistricts, row => this.getDistrict(row.region || ''))

            return Object.keys(grouped)
                .map(district => {
                    const rows = grouped[district]
                    return {
                        district,
                        avgPrice: this.formatNumber(this.getWeightedPrice(rows)),
                        volume: this.formatNumber(this.getTotalVolume(rows)),
                    }
                })
                .sort((a, b) => a.district.localeCompare(b.district, 'ru'))
        },

        regionChartOption() {
            const buckets = this.getSortedBuckets(this.filteredRowsByRegions)
            const grouped = this.groupBy(this.filteredRowsByRegions, row => row.region || 'Не указан')

            const series = Object.keys(grouped)
                .sort((a, b) => a.localeCompare(b, 'ru'))
                .map(region => ({
                    name: region,
                    type: 'line',
                    smooth: true,
                    data: buckets.map(bucket => {
                        const rows = grouped[region].filter(row => this.getBucketKey(row.timestamp) === bucket)
                        return rows.length ? Number(this.getWeightedPrice(rows).toFixed(2)) : null
                    }),
                }))

            return {
                tooltip: { trigger: 'axis' },
                legend: { top: 0 },
                grid: { left: 50, right: 20, top: 60, bottom: 50 },
                xAxis: {
                    type: 'category',
                    data: buckets,
                },
                yAxis: {
                    type: 'value',
                    name: 'руб./МВт·ч',
                },
                series,
            }
        },

        districtChartOption() {
            const buckets = this.getSortedBuckets(this.filteredRowsByDistricts)
            const grouped = this.groupBy(this.filteredRowsByDistricts, row => this.getDistrict(row.region || ''))

            const series = Object.keys(grouped)
                .sort((a, b) => a.localeCompare(b, 'ru'))
                .map(district => ({
                    name: district,
                    type: 'line',
                    smooth: true,
                    data: buckets.map(bucket => {
                        const rows = grouped[district].filter(row => this.getBucketKey(row.timestamp) === bucket)
                        return rows.length ? Number(this.getWeightedPrice(rows).toFixed(2)) : null
                    }),
                }))

            return {
                tooltip: { trigger: 'axis' },
                legend: { top: 0 },
                grid: { left: 50, right: 20, top: 60, bottom: 50 },
                xAxis: {
                    type: 'category',
                    data: buckets,
                },
                yAxis: {
                    type: 'value',
                    name: 'руб./МВт·ч',
                },
                series,
            }
        },
        // Проверки на пустые данные
        hasRegionTableRows() {
            return this.regionTableRows.length > 0
        },
        hasDistrictTableRows() {
            return this.districtTableRows.length > 0
        },
        hasRegionChartRows() {
            return this.filteredRowsByRegions.length > 0
        },
        hasDistrictChartRows() {
            return this.filteredRowsByDistricts.length > 0
        },
        currentTableHasRows() {
            return this.tableView === 'regions'
                ? this.hasRegionTableRows
                : this.hasDistrictTableRows
        },
        currentChartHasRows() {
            return this.chartView === 'regions'
                ? this.hasRegionChartRows
                : this.hasDistrictChartRows
        },
    },

    methods: {
        ...mapActions(['fetchPriceAnalyticsRows']),

        getInitialRange() {
            const today = new Date()
            const yesterday = new Date()
            yesterday.setDate(today.getDate() - 1)

            return {
                yesterday: this.toDateString(yesterday),
                today: this.toDateString(today),
            }
        },

        toDateString(date) {
            const y = date.getFullYear()
            const m = String(date.getMonth() + 1).padStart(2, '0')
            const d = String(date.getDate()).padStart(2, '0')
            return `${y}-${m}-${d}`
        },

        async loadData() {
            if (this.isDateInvalid) return

            if (!this.loadedOnce || (this.appliedDateFrom !== this.dateFrom || this.appliedDateTo !== this.dateTo)) {
                await this.fetchPriceAnalyticsRows({
                    from: this.dateFrom,
                    to: this.dateTo,
                })
            }

            this.appliedDateFrom = this.dateFrom
            this.appliedDateTo = this.dateTo
            this.appliedAggregation = this.aggregation
            this.appliedDistricts = [...this.selectedDistrictsDraft]
            this.appliedRegions = [...this.selectedRegionsDraft]

            this.loadedOnce = true
        },

        toNumber(value) {
            const num = Number(value)
            return Number.isFinite(num) ? num : 0
        },

        getDistrict(region) {
            return DISTRICT_BY_REGION[region] || 'Не определён'
        },

        groupBy(items, keyGetter) {
            return items.reduce((acc, item) => {
                const key = keyGetter(item)
                if (!acc[key]) acc[key] = []
                acc[key].push(item)
                return acc
            }, {})
        },

        getWeightedPrice(rows) {
            const numerator = rows.reduce((sum, row) => {
                return sum + this.toNumber(row.price_sell) * this.toNumber(row.full_plan)
            }, 0)

            const denominator = rows.reduce((sum, row) => {
                return sum + this.toNumber(row.full_plan)
            }, 0)

            return denominator ? numerator / denominator : 0
        },

        getTotalVolume(rows) {
            return rows.reduce((sum, row) => {
                return sum + this.toNumber(row.full_plan)
            }, 0)
        },

        formatNumber(value) {
            return Number(value || 0).toLocaleString('ru-RU', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
            })
        },

        getBucketKey(timestamp) {
            if (!timestamp) return ''

            const date = new Date(timestamp)
            if (Number.isNaN(date.getTime())) return String(timestamp)

            if (this.appliedAggregation === 'day') {
                return String(timestamp).slice(0, 10)
            }

            if (this.appliedAggregation === 'month') {
                const y = date.getFullYear()
                const m = String(date.getMonth() + 1).padStart(2, '0')
                return `${y}-${m}`
            }

            const temp = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()))
            const dayNum = temp.getUTCDay() || 7
            temp.setUTCDate(temp.getUTCDate() + 4 - dayNum)
            const yearStart = new Date(Date.UTC(temp.getUTCFullYear(), 0, 1))
            const weekNum = Math.ceil((((temp - yearStart) / 86400000) + 1) / 7)

            return `${temp.getUTCFullYear()}-W${String(weekNum).padStart(2, '0')}`
        },

        getSortedBuckets(rows) {
            const buckets = Array.from(new Set(rows.map(row => this.getBucketKey(row.timestamp))))
            return buckets.sort((a, b) => a.localeCompare(b, 'ru'))
        },
    },

    watch: {
        selectedDistrictsDraft() {
            if (!this.selectedDistrictsDraft.length) return

            this.selectedRegionsDraft = this.selectedRegionsDraft.filter(region => {
                return this.selectedDistrictsDraft.includes(this.getDistrict(region))
            })
        },
    },

    created() {
        if (this.priceAnalyticsRows.length > 0) {
            this.loadedOnce = true;
        }
    }
}
</script>