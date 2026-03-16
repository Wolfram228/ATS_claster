<template>
    <v-container v-if="!inited">Загрузка данных...</v-container>
    <v-container v-else>
        <v-row>
            <v-col cols="12" md="10">
                <v-menu location="top" class="flex-grow-1 me-3">
                    <template v-slot:activator="{ props }">
                        <!-- <v-btn color="blue-grey-lighten-5" class="mb-1" v-bind="props" min-height="55px" block> {{ selectedRegionPrev }} </v-btn> -->
                        <v-btn color="blue-grey-lighten-5" class="mb-1" v-bind="props" min-height="55px" block> {{ selectedRegionPrevBeforeConfirmed || "Выбор региона" }} </v-btn>
                    </template>

                    <v-list style="max-height: 300px">
                        <v-list-item
                        v-for="(regionPrev, id) in regionsPrev"
                        :key="id"
                        :value="id"
                        v-on:click="selectedRegionPrevBeforeConfirmed = regionPrev.value"
                        >
                        <v-list-item-title>{{ regionPrev.value }}</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
            </v-col>
            <v-col cols="12" md="2">
                <v-btn color="blue-grey-lighten-1" @click="changeRegionPrev" min-height="55px" block> Применить </v-btn>
                <div v-if="selectedRegionPrevBeforeConfirmed && selectedRegionPrev !== selectedRegionPrevBeforeConfirmed" class="text-error mt-2">Вы не применили изменения</div>
            </v-col>
        </v-row>
        <v-row>
            <div v-if="!selectedRegionPrevBeforeConfirmed" class="text-body-2 text-grey-darken-1" style="text-align: center; width: 100%"> Текущий регион: {{ this.selectedRegionPrev }} </div>
            <v-col 
            cols="12" 
            sm="6"
            lg="3"
            v-for="i in infoArray">
                <InfoCard>
                    <template v-slot:title>{{ i.title }}</template>
                    <template v-slot:info1> {{ i.info1 }}</template>
                    <template v-slot:info2> {{ i.info2 }}</template>
                    <template v-slot:percentage>
                        <div 
                            class="text-caption" 
                            :class="i.percentage.startsWith('-') ? 'text-error' : 'text-success'"
                        >
                            {{ i.percentage }}
                        </div>
                    </template>
                </InfoCard>
            </v-col>
        </v-row>
        <!--<v-row>
            <div class="text-body-2 text-grey-darken-1 mt-1" align="left">*Данные приведены за период {{ getLastDayRange }} (в сравнении с {{ getPrevDayRange }})</div>
        </v-row>-->
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
                    <div class="text-body-2 text-grey-darken-1 mt-1" align="left">Потребление электроэнергии за выбранный период</div>
                    <div class="text-body-2 text-grey-darken-1 mt-6" align="left">Интерактивные графики</div>
                    <v-container>
                        <v-row>
                            <v-col cols="12" md="4">
                                <v-btn :color="GraphType === 1 ? 'blue-grey-lighten-1' : 'blue-grey-lighten-5'" v-on:click="GraphType = 1" block> Объём по времени </v-btn>
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-btn :color="GraphType === 2 ? 'blue-grey-lighten-1' : 'blue-grey-lighten-5'" v-on:click="GraphType = 2" block> Цена по времени </v-btn>
                            </v-col>
                            <v-col cols="12" md="4">
                                <v-btn :color="GraphType === 3 ? 'blue-grey-lighten-1' : 'blue-grey-lighten-5'" v-on:click="GraphType = 3" block> Объём и цена по времени </v-btn>
                            </v-col>
                        </v-row>
                    </v-container>
                    <v-container>
                        <v-row>
                            <v-col cols="12" md="3">
                                <v-text-field
                                v-model="draftDateBefore"
                                label="Отображать с:"
                                type="date"
                                hide-details
                                ></v-text-field>
                            </v-col>
                            <v-col cols="12" md="3">
                                <v-text-field
                                v-model="draftDateAfter"
                                label="Отображать до:"
                                type="date"
                                hide-details
                                ></v-text-field>
                            </v-col>
                            <v-col cols="12" md="3">
                                <v-menu location="top" class="flex-grow-1 me-3">
                                    <template v-slot:activator="{ props }">
                                        <!-- <v-btn color="blue-grey-lighten-5" v-bind="props" min-height="55px" block> {{ selectedRegion }} </v-btn> -->
                                        <v-btn color="blue-grey-lighten-5" v-bind="props" min-height="55px" block> {{ selectedRegionBeforeConfirmed || "Выбор региона" }} </v-btn>
                                    </template>

                                    <v-list style="max-height: 300px">
                                        <v-list-item
                                        v-for="(region, id) in regions"
                                        :key="id"
                                        :value="id"
                                        v-on:click="selectedRegionBeforeConfirmed = region.value"
                                        >
                                        <v-list-item-title>{{ region.value }}</v-list-item-title>
                                        </v-list-item>
                                    </v-list>
                                </v-menu>
                            </v-col>
                            <v-col cols="12" md="3">
                                <v-btn color="blue-grey-lighten-1" :disabled="isDateInvalid" @click="fetchData" min-height="55px" block> Применить </v-btn>
                                <div v-if="isDateInvalid" class="text-error mt-2"> Введена некорректная дата </div>
                                <div 
                                v-if="(!isDateInvalid) && (isDateChanged || (selectedRegionBeforeConfirmed && selectedRegion !== selectedRegionBeforeConfirmed))" 
                                class="text-error mt-2">
                                Вы не применили изменения
                                </div>
                            </v-col>
                        </v-row>
                    </v-container>
                    <v-container v-if="loading===true">
                        Загрузка данных...
                    </v-container>
                    <v-container v-else>
                        <div v-if="!selectedRegionBeforeConfirmed" class="text-body-2 text-grey-darken-1" align="center">Текущий регион: {{ this.selectedRegion }}</div>
                        <!-- Первый график -->
                        <VChart v-if="GraphType === 1"
                            :option="volumeOptions"
                            class="mt-3"
                            style="height: 400px; border: 1px solid rgba(0,0,0,0.2);"
                        />
                        <!-- Второй график -->
                        <VChart v-else-if="GraphType === 2"
                            :option="priceOptions"
                            class="mt-3"
                            style="height: 400px; border: 1px solid rgba(0,0,0,0.2);"
                        />
                        <!-- Третий график -->
                        <VChart v-else-if="GraphType === 3"
                            :option="combinedOptions"
                            class="mt-3"
                            style="height: 400px; border: 1px solid rgba(0,0,0,0.2);"
                        />
                    </v-container>
                </v-card>
            </v-col>
        </v-row>
    </v-container>
</template>

<script>
import InfoCard from "../components/InfoCard.vue"
import { mapState, mapActions } from "vuex"

const generatorFields = [
    { key: "plan_GES", label: "ГЭС" },
    { key: "plan_AES", label: "АЭС" },
    { key: "plan_TES", label: "ТЭС" },
    { key: "plan_SES", label: "СЭС" },
    { key: "plan_VES", label: "ВЭС" },
    { key: "plan_other", label: "прочие ВИЭ" },
]

export default {
    components: { InfoCard },

    data() {
        return {
        GraphType: 1,
        //selectedRegionBeforeConfirmed: undefined,
        //selectedRegion: undefined,

        selectedRegionPrevBeforeConfirmed: undefined,
        selectedRegionPrev: undefined,

        draftDateBefore: null,
        draftDateAfter: null,
        }
    },

    computed: {
        ...mapState({
            boatsRaw: state => state.changableDateBoats,
            boatsWithRegionRaw: state => state.boatsWithRegion,
            lastDayBoatsRaw: state => state.lastDayBoats,
            prevDayBoatsRaw: state => state.prevDayBoats,

            loading: state => state.loading,
            inited: state => state.inited,
            hasChangableData: state => state.hasChangableData
        }),
        

        regions() {
            return [
                { id: 0, value: "Все регионы" },
                ...this.$store.getters.staticRegions
            ]
        },
        regionsPrev() {
            return this.$store.getters.regionsPrev;
        },

        selectedRegion: {
            get() {
                return this.$store.state.selectedRegion
            },
            set(region) {
                this.$store.commit("SET_SELECTED_REGION", region)
            }
        },
        selectedRegionBeforeConfirmed: {
            get() {
                return this.$store.state.selectedRegionBeforeConfirmed
            },
            set(region) {
                this.$store.commit("SET_SELECTED_REGION_BEFORE_CONFIRMED", region)
            }
        },

        isDateChanged() {
            return ( this.draftDateBefore !== this.$store.state.selectedDateBefore || this.draftDateAfter !== this.$store.state.selectedDateAfter )
        },

        isDateInvalid() {
            const from = this.draftDateBefore
            const to = this.draftDateAfter

            if (!from || !to) return true

            // строгая проверка формата (и реальной даты)
            const fromYmd = this.ymdLocal(from)
            const toYmd = this.ymdLocal(to)
            if (!fromYmd || !toYmd) return true

            const today = this.ymdLocal(new Date())
            if (!today) return true

            const d = new Date()
            d.setFullYear(d.getFullYear() - 3)
            const minDate = this.ymdLocal(d)
            if (!minDate) return true

            // "от" не может быть завтра или позже
            if (fromYmd > today) return true

            // "от" не старше 3 лет назад
            if (fromYmd < minDate) return true

            // диапазон
            if (fromYmd > toYmd) return true

            return false
        },

        // данные для графика
        boats() {
            const regionActive = this.selectedRegion && this.selectedRegion !== 'Все регионы'

            // при выбранном регионе стор кладёт данные сюда
            if (regionActive) return this.boatsWithRegionRaw || []

            return this.boatsRaw || []
        },

        // последние сутки (для текущих значений в InfoCard)
        lastDayBoats() {
            if (!this.selectedRegionPrev || this.selectedRegionPrev === 'Все регионы') {
                return this.lastDayBoatsRaw || []
            }
            return (this.lastDayBoatsRaw || []).filter(b => b.region === this.selectedRegionPrev)
        },

        // предыдущие сутки (для динамики)
        prevDayBoats() {
            if (!this.selectedRegionPrev || this.selectedRegionPrev === 'Все регионы') {
                return this.prevDayBoatsRaw || []
            }
            return (this.prevDayBoatsRaw || []).filter(b => b.region === this.selectedRegionPrev)
        },

        // агрегаты по часам для графиков
        hourlyStats() {
            return this.buildHourlyStats(this.boats)
        },

        // ось X для графиков почасовая
        dates() {
            return this.hourlyStats.map(d => d.date)
        },

        // агрегаты по часам для InfoCard (текущие и предыдущие сутки)
        lastDayStats() {
            return this.buildHourlyStats(this.lastDayBoats)
        },
        prevDayStats() {
            return this.buildHourlyStats(this.prevDayBoats)
        },

        // KPI по последним суткам
        totalConsumption() {
            return this.lastDayStats.reduce((s, d) => s + d.consumption, 0)
        },
        avgDailyConsumption() {
            return this.lastDayStats.length
            ? this.totalConsumption / this.lastDayStats.length
            : 0
        },
        peakDailyConsumption() {
            return this.lastDayStats.reduce((m, d) => Math.max(m, d.consumption), 0, )
        },
        efficiency() {
            if (!this.peakDailyConsumption) return 0
            return (this.avgDailyConsumption / this.peakDailyConsumption) * 100
        },

        // KPI по предыдущим суткам (для динамики)
        prevTotalConsumption() {
            return this.prevDayStats.reduce((s, d) => s + d.consumption, 0)
        },
        prevAvgDailyConsumption() {
            return this.prevDayStats.length
            ? this.prevTotalConsumption / this.prevDayStats.length
            : 0
        },
        prevPeakDailyConsumption() {
            return this.prevDayStats.reduce((m, d) => Math.max(m, d.consumption), 0, )
        },
        prevEfficiency() {
            if (!this.prevPeakDailyConsumption) return 0
            return (this.prevAvgDailyConsumption / this.prevPeakDailyConsumption) * 100
        },

        // тексты для InfoCard
        totalConsumptionText() {
            return `${this.formatNumber(this.totalConsumption, 0)} МВт/ч`
        },
        avgDailyConsumptionText() {
            return `${this.formatNumber(this.avgDailyConsumption, 0)} МВт/ч`
        },
        peakDailyConsumptionText() {
            return `${this.formatNumber(this.peakDailyConsumption, 0)} МВт/ч`
        },
        efficiencyText() {
            return `${this.formatNumber(this.efficiency, 1)} %`
        },

        // массив для рендеринга InfoCard
        infoArray() {
            const totalPct = this.formatDeltaPercent(
                this.prevTotalConsumption,
                this.totalConsumption,
            )
            const avgPct = this.formatDeltaPercent(
                this.prevAvgDailyConsumption,
                this.avgDailyConsumption,
            )
            const peakPct = this.formatDeltaPercent(
                this.prevPeakDailyConsumption,
                this.peakDailyConsumption,
            )
            const effPct = this.formatDeltaPercent(
                this.prevEfficiency,
                this.efficiency,
            )

            return [
                {
                    title: 'Общее потребление',
                    info1: this.totalConsumptionText,
                    info2: 'за текущие сутки',
                    percentage: totalPct,
                },
                {
                    title: 'Среднее потребление',
                    info1: this.avgDailyConsumptionText,
                    info2: 'за час',
                    percentage: avgPct,
                },
                {
                    title: 'Пиковое потребление',
                    info1: this.peakDailyConsumptionText,
                    info2: 'за час',
                    percentage: peakPct,
                },
                {
                    title: 'Эффективность',
                    info1: this.efficiencyText,
                    info2: 'за текущие сутки',
                    percentage: effPct,
                },
            ]
        },
        generatorVolumeSeries() {
            const dates = this.dates
            const indexByDate = new Map(dates.map((d, i) => [d, i]))

            const sums = {}
            for (const { key } of generatorFields) {
                sums[key] = new Array(dates.length).fill(0)
            }

            for (const row of this.boats || []) {
                if (!row.timestamp) continue

                const datePart = String(row.timestamp).slice(0, 10) // "2025-12-07"

                // ЧАС БЕРЁМ ИЗ row.hour
                const hour = Number(row.hour ?? row.HH ?? row.hour_id ?? 0) || 0
                const hourStr = String(hour).padStart(2, '0')        // "00".."23"

                const label = `${datePart} ${hourStr}:00`            // "2025-12-07 13:00"

                const idx = indexByDate.get(label)
                if (idx == null) continue

                for (const { key } of generatorFields) {
                    const val = Number(row[key]) || 0
                    sums[key][idx] += val
                }
            }

            return generatorFields.map(({ key, label }) => ({
                name: label,
                type: 'line',
                smooth: true,
                data: sums[key],
            }))
        },

        // --- ГРАФИК 1: объём по времени (почасовой) ---
        volumeOptions() {
            const dates = this.dates
            const bigRange = dates.length > 24 * 7 // больше недели

            return {
                tooltip: {
                    trigger: 'axis',
                    formatter(params) {
                        if (!params.length) return ''
                        const date = params[0].axisValue
                        const lines = params.map(p => {
                            const val = Number(p.value) || 0
                            return `${p.marker} ${p.seriesName}: ${val.toFixed(2)} МВт/ч`
                        })
                        return `${date}<br>${lines.join('<br>')}`
                    },
                },
                legend: {
                    type: 'scroll',
                },
                xAxis: {
                    type: 'category',
                    data: dates,
                    axisLabel: {
                        formatter(value) {
                            // value: "2025-12-06 13:00"
                            const day = value.slice(5, 10)   // "12-06"
                            const time = value.slice(11, 16) // "13:00"

                            if (bigRange) {
                                // большой диапазон: только день по полуночи
                                if (value.endsWith('00:00')) {
                                    return day
                                }
                                return ''
                            }
                            // маленький диапазон: день + время
                            return `${day}\n${time}`
                        },
                    },
                },
                yAxis: {
                    type: 'value',
                    name: 'Объём, МВт/ч',
                },
                series: this.generatorVolumeSeries,
            }
        },

        // --- ГРАФИК 2: цена по времени (почасовой) ---
        priceOptions() {
            const dates = this.dates
            const bigRange = dates.length > 24 * 7

            return {
                tooltip: {
                    trigger: "axis",
                    formatter(params) {
                        if (!params.length) return ""
                        const date = params[0].axisValue
                        const lines = params.map(p => {
                            const val = Number(p.value) || 0
                            return `${p.marker} ${p.seriesName}: ${val.toFixed(2)} руб/МВт·ч`
                        })
                        return `${date}<br>${lines.join("<br>")}`
                    },
                },
                xAxis: {
                    type: "category",
                    data: dates,
                    axisLabel: {
                        formatter(value) {
                            const day = value.slice(5, 10)
                            const time = value.slice(11, 16)

                            if (bigRange) {
                                if (value.endsWith('00:00')) {
                                    return day
                                }
                                return ''
                            }
                            return `${day}\n${time}`
                        },
                    },
                },
                yAxis: {
                    type: "value",
                    name: "Цена, руб/МВт·ч",
                },
                series: [
                    {
                        name: "Цена покупки",
                        type: "line",
                        smooth: true,
                        data: this.hourlyStats.map(d => d.priceBuy),
                    },
                    {
                        name: "Цена продажи",
                        type: "line",
                        smooth: true,
                        data: this.hourlyStats.map(d => d.priceSell),
                    },
                ],
            }
        },

        // --- ГРАФИК 3: объём и цена по времени (почасовой) ---
        combinedOptions() {
            const dates = this.dates
            const bigRange = dates.length > 24 * 7

            const volumeSeries = this.generatorVolumeSeries.map(s => ({
                ...s,
                yAxisIndex: 0,
            }))

            const priceSeries = [
                {
                    name: 'Цена покупки',
                    type: 'line',
                    smooth: true,
                    data: this.hourlyStats.map(d => d.priceBuy),
                    yAxisIndex: 1,
                },
                {
                    name: 'Цена продажи',
                    type: 'line',
                    smooth: true,
                    data: this.hourlyStats.map(d => d.priceSell),
                    yAxisIndex: 1,
                },
            ]

            return {
                tooltip: {
                    trigger: 'axis',
                    formatter(params) {
                        if (!params.length) return ""

                        const label = params[0].axisValue
                        const lines = params.map(p => {
                            const raw = Number(p.value) || 0
                            const isPrice = p.seriesName.includes("Цена")
                            const unit = isPrice ? " руб/МВт·ч" : " МВт/ч"
                            const val = raw.toFixed(2)
                            return `${p.marker} ${p.seriesName}: ${val}${unit}`
                        })

                        return `${label}<br>${lines.join("<br>")}`
                    },
                },
                legend: {
                    type: 'scroll',
                },
                xAxis: {
                    type: 'category',
                    data: dates,
                    axisLabel: {
                        formatter(value) {
                            const day = value.slice(5, 10)
                            const time = value.slice(11, 16)

                            if (bigRange) {
                                if (value.endsWith('00:00')) {
                                    return day
                                }
                                return ''
                            }
                            return `${day}\n${time}`
                        },
                    },
                },
                yAxis: [
                    { type: 'value', name: 'Объём, МВт/ч' },
                    { type: 'value', name: 'Цена, руб/МВт·ч' },
                ],
                series: [...volumeSeries, ...priceSeries],
            }
        },
    },

    methods: {
        /*...mapActions({
            fetchData: 'fetchChangableBoats',
        }),*/

        fetchData() {
            if (this.isDateInvalid) return

            const regionChanged = this.selectedRegionBeforeConfirmed !== this.selectedRegion
            //const regionActive = this.selectedRegionBeforeConfirmed && this.selectedRegionBeforeConfirmed !== 'Все регионы'

            if (((!regionChanged || !this.selectedRegionBeforeConfirmed) && !this.isDateChanged)) return

            if (this.isDateChanged) this.applyDates()
            if (regionChanged && this.selectedRegionBeforeConfirmed) this.selectedRegion = this.selectedRegionBeforeConfirmed

            this.$store.dispatch("fetchChangableBoats")
        },

        // YYYY-MM-DD в ЛОКАЛЬНОЙ таймзоне
        ymdLocal(input = new Date()) {
            let d = input

            // если пришла строка YYYY-MM-DD — аккуратно превращаем в Date (локально)
            if (typeof d === 'string') {
                const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(d)
                if (!m) return null
                const y = Number(m[1])
                const mo = Number(m[2]) - 1
                const day = Number(m[3])
                d = new Date(y, mo, day) // локальная полночь
            }

            // если всё ещё не Date — выходим
            if (!(d instanceof Date) || Number.isNaN(d.getTime())) return null

            const y = d.getFullYear()
            const m = String(d.getMonth() + 1).padStart(2, '0')
            const day = String(d.getDate()).padStart(2, '0')
            return `${y}-${m}-${day}`
        },

        changeRegionPrev() {
            if (this.selectedRegionPrevBeforeConfirmed) {
                this.selectedRegionPrev = this.selectedRegionPrevBeforeConfirmed;
            }
        },

        // агрегация по часам: для графиков (объём + средняя цена за час)
        buildHourlyStats(boats) {
            const map = new Map()

            for (const row of (boats || [])) {
                if (!row.timestamp) continue

                const datePart = String(row.timestamp).slice(0, 10)

                const hour = Number(row.hour ?? row.HH ?? row.hour_id ?? 0) || 0
                const hourStr = String(hour).padStart(2, '0')
                const label = `${datePart} ${hourStr}:00`           // "2025-12-07 13:00"

                let item = map.get(label)
                if (!item) {
                    item = {
                        date: label,
                        consumption: 0,
                        priceBuySum: 0,
                        priceSellSum: 0,
                        count: 0,
                        priceBuy: 0,
                        priceSell: 0,
                    }
                    map.set(label, item)
                }

                item.consumption += generatorFields.reduce(
                    (sum, { key }) => sum + (Number(row[key]) || 0),
                    0,
                )

                const priceBuy = Number(row.price_buy) || 0
                const priceSell = Number(row.price_sell) || 0
                item.priceBuySum += priceBuy
                item.priceSellSum += priceSell
                item.count += 1
            }

            const result = Array.from(map.values()).sort((a, b) =>
                a.date.localeCompare(b.date),
            )

            for (const r of result) {
                r.priceBuy = r.count ? r.priceBuySum / r.count : 0
                r.priceSell = r.count ? r.priceSellSum / r.count : 0
            }

            return result
        },

        // формат динамики в процентах
        formatDeltaPercent(prev, curr) {
            const prevNum = Number(prev) || 0
            const currNum = Number(curr) || 0

            if (!prevNum) {
            return '0.0%'
            }

            const delta = ((currNum - prevNum) / prevNum) * 100
            const sign = delta >= 0 ? '+' : '-'
            return `${sign}${Math.abs(delta).toFixed(1)}%`
        },

        formatNumber(value, fractionDigits = 0) {
            const num = Number(value) || 0
            return num.toLocaleString('ru-RU', {
            minimumFractionDigits: fractionDigits,
            maximumFractionDigits: fractionDigits,
            })
        },
        applyDates() {
            this.$store.commit('SET_SELECTED_DATE_BEFORE', this.draftDateBefore);
            this.$store.commit('SET_SELECTED_DATE_AFTER', this.draftDateAfter);
        }
    },

    created() {
        if (!this.$store.state.inited) {
            this.$store.dispatch('initBoats');
        }
        
        const regionActive = this.selectedRegion && this.selectedRegion !== 'Все регионы';
        if (!regionActive) this.selectedRegion = this.regions[0]?.value;;

        this.selectedRegionPrev = this.regionsPrev[0]?.value;

        this.draftDateAfter = this.$store.state.selectedDateAfter
        this.draftDateBefore = this.$store.state.selectedDateBefore

    },
}
</script>