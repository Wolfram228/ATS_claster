<template>
    <v-container class="pa-4">
        <!-- Блок 1: Настройки -->
        <v-card class="pa-4 mb-4" elevation="1" rounded="lg" variant="outlined" style="border-color: rgba(0, 0, 0, 0.2)">
            <div class="text-h5 font-weight-bold" align="left">Моделирование цены электроэнергии</div>
            <div class="text-body-2 text-grey-darken-1 mt-1" align="left">
                Построение прогноза цены продажи электроэнергии на основе выбранного региона,
                доступных факторов, температуры и метода наименьших квадратов / OLS.
            </div>

            <v-container class="px-0 pt-6">
                <v-row>
                    <v-col cols="12" md="3">
                        <v-text-field v-model="dateFrom" label="Дата с" type="date" hide-details />
                    </v-col>
                    <v-col cols="12" md="3">
                        <v-text-field v-model="dateTo" label="Дата по" type="date" hide-details />
                    </v-col>
                    <v-col cols="12" md="3">
                        <v-select v-model="selectedRegion" :items="regionItems" label="Регион" hide-details />
                    </v-col>
                    <v-col cols="12" md="3">
                        <v-select v-model="targetVariable" :items="targetVariables" label="Целевая переменная" hide-details />
                    </v-col>
                </v-row>

                <v-row class="mt-4">
                    <v-col cols="12">
                        <v-card class="pa-4" elevation="0" rounded="lg" variant="outlined" style="border-color: rgba(0, 0, 0, 0.12)">
                            <div class="d-flex align-center justify-space-between mb-2">
                                <div class="text-h6 font-weight-bold">Факторы модели</div>
                                <v-chip color="blue-grey-lighten-4" variant="flat">Рекомендуемый набор выбран</v-chip>
                            </div>
                            <div class="text-body-2 text-grey-darken-1 mb-4" align="left">
                                Для временных признаков используется циклическое кодирование. Месяц учитывается как дамми-переменная.
                                Температура подтягивается из внешнего погодного источника по региону и часу.
                            </div>

                            <v-row>
                                <v-col v-for="factor in factors" :key="factor.value" cols="12" md="6">
                                    <v-checkbox v-model="selectedFactors" :label="factor.label" :value="factor.value" hide-details />
                                </v-col>
                            </v-row>
                        </v-card>
                    </v-col>
                </v-row>

                <v-row class="mt-4 align-center">
                    <v-col cols="12" md="3">
                        <v-btn block min-height="52" color="blue-grey-lighten-1" :loading="priceAnalyticsLoading || weatherLoading" :disabled="isDateInvalid" @click="loadData">
                            Загрузить данные
                        </v-btn>
                    </v-col>
                    <v-col cols="12" md="3">
                        <v-btn block min-height="52" color="blue-lighten-1" :loading="priceAnalyticsLoading || weatherLoading" :disabled="isDateInvalid" @click="showStatistics">
                            Показать статистику
                        </v-btn>
                    </v-col>
                    <!-- Блок выбора метода прогноза -->
                    <v-col cols="12" md="6">
                        <div class="d-flex align-center">
                            <span class="text-body-2 font-weight-bold me-2">Метод прогноза:</span>
                            <v-btn-group density="compact" variant="outlined">
                                <v-btn :color="forecastMethod === 'ar' ? 'green-lighten-1' : ''" @click="forecastMethod = 'ar'">Авторегрессия (AR)</v-btn>
                                <v-btn :color="forecastMethod === 'ols' ? 'green-lighten-1' : ''" @click="forecastMethod = 'ols'">Мультифакторный (OLS)</v-btn>
                            </v-btn-group>
                        </div>
                        <div class="mt-2 d-flex">
                            <v-btn block min-height="52" color="green-lighten-1" :loading="priceAnalyticsLoading || weatherLoading" :disabled="isDateInvalid" @click="buildForecast">
                                Построить прогноз
                            </v-btn>
                        </div>
                    </v-col>
                </v-row>

                <div v-if="isDateInvalid" class="text-error mt-3">Введён некорректный диапазон дат.</div>
                <div v-if="hasPendingChanges" class="text-error mt-3">Вы изменили параметры, но ещё не загрузили данные.</div>
            </v-container>
        </v-card>

        <!-- Уведомления -->
        <v-alert v-if="priceAnalyticsError" type="error" variant="tonal" class="mb-4">
            Ошибка загрузки данных проекта. Проверьте авторизацию и доступность сервера.
        </v-alert>
        <v-alert v-if="weatherError" type="warning" variant="tonal" class="mb-4">{{ weatherError }}</v-alert>
        <v-alert v-if="loadedOnce && temperatureCoverage.total > 0" type="info" variant="tonal" class="mb-4">
            Температура загружена для {{ temperatureCoverage.loaded }} из {{ temperatureCoverage.total }} наблюдений.
        </v-alert>
        <v-alert v-if="loadedOnce && !filteredRows.length" type="info" variant="tonal" class="mb-4">
            Нет данных по выбранному региону и периоду.
        </v-alert>
        <v-alert v-if="loadedOnce && filteredRows.length > 0 && filteredRows.length < 168" type="warning" variant="tonal" class="mb-4">
            Для более устойчивого прогноза рекомендуется выбирать период не менее 7 дней.
        </v-alert>

        <!-- Блок 2: Статистика -->
        <v-card v-if="statistics" class="pa-4 mb-4" elevation="1" rounded="lg" variant="outlined" style="border-color: rgba(0, 0, 0, 0.2)">
            <div class="text-h5 font-weight-bold" align="left">Описательная статистика</div>
            <div class="text-body-2 text-grey-darken-1 mt-1" align="left">Расчёт выполнен по фактическим данным для выбранного региона.</div>
            <div class="text-body-2 text-grey-darken-1 mt-1 mb-4" align="left">
                Регион: {{ appliedRegion }} · Период: {{ formatDisplayDate(appliedDateFrom) }} — {{ formatDisplayDate(appliedDateTo) }}
            </div>

            <div class="correlation-scroll mt-4">
                <v-table class="text-center">
                    <thead>
                        <tr>
                            <th class="text-left font-weight-bold">Показатель</th>
                            <th v-for="variable in statistics.variables" :key="variable.key" class="font-weight-bold">{{ variable.label }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="text-left">Количество наблюдений</td>
                            <td v-for="variable in statistics.variables" :key="variable.key">{{ formatDescribeValue(variable.n, 0) }}</td>
                        </tr>
                        <tr>
                            <td class="text-left">Среднее значение</td>
                            <td v-for="variable in statistics.variables" :key="variable.key">{{ formatDescribeValue(variable.mean, 2) }}</td>
                        </tr>
                        <tr>
                            <td class="text-left">Стандартное отклонение</td>
                            <td v-for="variable in statistics.variables" :key="variable.key">{{ formatDescribeValue(variable.sd, 2) }}</td>
                        </tr>
                        <tr>
                            <td class="text-left">Минимум / Максимум</td>
                            <td v-for="variable in statistics.variables" :key="variable.key">
                                {{ formatDescribeValue(variable.min, 2) }} / {{ formatDescribeValue(variable.max, 2) }}
                            </td>
                        </tr>
                    </tbody>
                </v-table>
            </div>
        </v-card>

        <!-- Блок 3: Корреляция -->
        <v-card v-if="correlationMatrix" class="pa-4 mb-4" elevation="1" rounded="lg" variant="outlined" style="border-color: rgba(0, 0, 0, 0.2)">
            <div class="text-h5 font-weight-bold" align="left">Корреляционный анализ</div>
            <div class="text-body-2 text-grey-darken-1 mt-1" align="left">
                Матрица корреляций показывает силу линейной связи между ценой и выбранными объясняющими переменными.
            </div>

            <div class="correlation-scroll mt-4">
                <v-table class="text-center">
                    <thead>
                        <tr>
                            <th class="text-left font-weight-bold">Переменная</th>
                            <th v-for="header in correlationMatrix.headers" :key="header" class="font-weight-bold">{{ header }}</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="row in correlationMatrix.rows" :key="row.label">
                            <td class="text-left font-weight-bold">{{ row.label }}</td>
                            <td v-for="cell in row.values" :key="cell.key" :style="getCorrelationCellStyle(cell.value)">
                                {{ formatCorrelation(cell.value) }}
                            </td>
                        </tr>
                    </tbody>
                </v-table>
            </div>
        </v-card>

        <!-- Блок 4: Результат прогноза -->
        <v-card v-if="forecast" class="pa-4 mb-4" elevation="1" rounded="lg" variant="outlined" style="border-color: rgba(0, 0, 0, 0.2)">
            <div class="d-flex align-center justify-space-between flex-wrap">
                <div class="d-flex align-center flex-wrap mb-2">
                    <div class="text-h5 font-weight-bold me-2" align="left">Результат моделирования</div>
                    <!-- Подсказка с адаптивным дизайном -->
                    <div class="d-flex align-center flex-shrink-0">
                        <HintFormula>
                            <div style="font-size: 13px; text-align: left; min-width: 200px;">
                                <strong>Авторегрессия (AR):</strong> Прогноз строится на основе предыдущих 24 часов цены. Не учитывает внешние факторы.<br><br>
                                <strong>Мультифакторный (OLS):</strong> Использует выбранные факторы. Для будущих периодов факторы берутся как средние за последние 24 часа.
                            </div>
                        </HintFormula>
                    </div>
                </div>
                <v-chip v-if="forecast.qualityColor" :color="forecast.qualityColor" variant="flat" class="font-weight-bold mb-2">
                    {{ forecast.qualityLabel }}
                </v-chip>
            </div>
            
            <div class="text-body-2 text-grey-darken-1 mt-1" align="left">
                Метод: {{ forecastMethod === 'ar' ? 'Авторегрессия' : 'Множественная линейная регрессия (OLS)' }}.
                Прогноз на {{ forecastHorizon }} часов вперёд.
            </div>

            <v-table class="mt-4">
                <tbody>
                    <tr><td class="font-weight-bold" style="width: 45%">Регион</td><td>{{ selectedRegion }}</td></tr>
                    <tr><td class="font-weight-bold">Целевая переменная</td><td>{{ targetVariable }}</td></tr>
                    <tr v-if="forecast.usedFactors"><td class="font-weight-bold">Использованные факторы</td><td>{{ forecast.usedFactors.join(', ') }}</td></tr>
                    <tr><td class="font-weight-bold">Исторических данных (часов)</td><td>{{ forecast.trainCount }}</td></tr>
                    <tr><td class="font-weight-bold">Горизонт прогноза (часов)</td><td>{{ forecastHorizon }}</td></tr>
                    <tr><td class="font-weight-bold">R² на исторических данных</td><td>{{ formatNumber(forecast.r2, 4) }}</td></tr>
                    <tr><td class="font-weight-bold">Средняя прогнозируемая цена</td><td>{{ formatNumber(forecast.avgPredictedPrice) }} руб./МВт·ч</td></tr>
                </tbody>
            </v-table>

            <v-alert v-if="forecast.skippedFactors && forecast.skippedFactors.length" type="warning" variant="tonal" class="mt-4">
                Следующие факторы отсутствуют и не были использованы: {{ forecast.skippedFactors.join(', ') }}.
            </v-alert>
        </v-card>

        <!-- Блок 5: График -->
        <v-card v-if="forecastChartRows.length" class="pa-4 mb-4" elevation="1" rounded="lg" variant="outlined" style="border-color: rgba(0, 0, 0, 0.2)">
            <div class="text-h5 font-weight-bold" align="left">График фактической и прогнозной цены</div>
            <div class="text-body-2 text-grey-darken-1 mt-1 mb-4" align="left">
                Сравнение фактической и прогнозной цены. Прогноз начинается после последней фактической точки.
            </div>
            <VChart :option="forecastChartOption" style="height: 420px; border: 1px solid rgba(0,0,0,0.2);" />
        </v-card>

        <!-- Блок 6: Таблица прогноза -->
        <v-card v-if="hourlyForecastRows.length" class="pa-4 mb-4" elevation="1" rounded="lg" variant="outlined" style="border-color: rgba(0, 0, 0, 0.2)">
            <div class="text-h5 font-weight-bold" align="left">Почасовой прогноз</div>
            <div class="text-body-2 text-grey-darken-1 mt-1 mb-4" align="left">
                Прогноз построен для каждого часа на {{ forecastHorizon }} часов вперёд.
            </div>
            <v-data-table :headers="hourlyForecastHeaders" :items="hourlyForecastRows" density="comfortable" items-per-page="24" />
        </v-card>
    </v-container>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'
import HintFormula from '../components/HintFormula.vue'

const REGION_COORDINATES = { /* ... (оставь свой словарь координат без изменений) ... */ }

export default {
    name: 'PriceModeling',
    components: { HintFormula },

    data() {
        const { from, to } = this.getInitialRange()

        return {
            loadedOnce: false,
            dateFrom: from,
            dateTo: to,
            appliedDateFrom: '',
            appliedDateTo: '',
            appliedRegion: '',
            selectedRegion: 'Иркутская область',
            targetVariable: 'Цена продажи электроэнергии',
            targetVariables: ['Цена продажи электроэнергии'],
            
            forecastMethod: 'ar', // 'ar' или 'ols'
            forecastHorizon: 24,  // на сколько часов прогнозируем

            factors: [
                { label: 'Объём', value: 'full_plan' },
                { label: 'Цена предыдущего часа', value: 'previousPrice' },
                { label: 'Циклический час суток', value: 'hourCycle' },
                { label: 'Циклический день недели', value: 'dayCycle' },
                { label: 'Месяц', value: 'monthDummy' },
                { label: 'Температура', value: 'temperature' },
                { label: 'Выработка ГЭС', value: 'HPP' },
                { label: 'Выработка ТЭС', value: 'CHP' },
                { label: 'Потребление', value: 'Q_cons' },
                { label: 'Экспорт', value: 'Q_exp' },
                { label: 'Импорт', value: 'Q_imp' },
            ],
            selectedFactors: ['full_plan', 'previousPrice', 'hourCycle', 'dayCycle', 'monthDummy', 'temperature'],
            
            hourlyForecastHeaders: [
                { title: 'Дата и час', key: 'dateTime', align: 'center' },
                { title: 'Прогнозная цена, руб./МВт·ч', key: 'predictedPrice', align: 'center' },
            ],
            weatherLoading: false,
            weatherError: null,
            temperatureByDateHour: {},
            statistics: null,
            correlationMatrix: null,
            forecast: null,
            hourlyForecastRows: [],
            forecastChartRows: [],
        }
    },

    computed: {
        ...mapState({
            priceAnalyticsRows: state => state.priceAnalyticsRows,
            priceAnalyticsLoading: state => state.priceAnalyticsLoading,
            priceAnalyticsError: state => state.priceAnalyticsError,
        }),
        ...mapGetters({ storeRegions: 'staticRegions' }),

        regionItems() {
            if (!Array.isArray(this.storeRegions) || !this.storeRegions.length) return ['Иркутская область']
            return this.storeRegions.map(item => item.value)
        },

        isDateInvalid() {
            return !this.dateFrom || !this.dateTo || this.dateFrom > this.dateTo
        },

        hasPendingChanges() {
            if (!this.loadedOnce) return false
            return this.dateFrom !== this.appliedDateFrom || this.dateTo !== this.appliedDateTo || this.selectedRegion !== this.appliedRegion
        },

        enrichedRows() {
            return this.priceAnalyticsRows.map(row => {
                const key = this.getDateHourKey(row)
                const temperature = this.temperatureByDateHour[key]
                return { ...row, temperature: Number.isFinite(temperature) ? temperature : null }
            })
        },

        filteredRows() {
            return this.enrichedRows
                .filter(row => (row.region || '') === this.selectedRegion)
                .filter(row => Number.isFinite(this.getPrice(row)))
                .sort((a, b) => {
                    const timeCompare = String(a.timestamp || '').localeCompare(String(b.timestamp || ''))
                    if (timeCompare !== 0) return timeCompare
                    return this.getHour(a) - this.getHour(b)
                })
        },

        temperatureCoverage() {
            const total = this.filteredRows.length
            if (!total) return { loaded: 0, total: 0 }
            const loaded = this.filteredRows.filter(row => Number.isFinite(this.toNumber(row.temperature))).length
            return { loaded, total }
        },

        forecastChartOption() {
            return {
                tooltip: { trigger: 'axis' },
                legend: { top: 0 },
                grid: { left: 60, right: 25, top: 60, bottom: 70 },
                dataZoom: [{ type: 'inside' }, { type: 'slider', bottom: 20 }],
                xAxis: { type: 'category', data: this.forecastChartRows.map(row => row.dateTime) },
                yAxis: { type: 'value', name: 'руб./МВт·ч' },
                series: [
                    { 
                        name: 'Фактическая цена', 
                        type: 'line', 
                        smooth: true, 
                        data: this.forecastChartRows.map(row => row.actual),
                        connectNulls: false // Чтобы линия истории не соединялась с прогнозом
                    },
                    { 
                        name: 'Прогнозная цена', 
                        type: 'line', 
                        smooth: true, 
                        data: this.forecastChartRows.map(row => row.predicted),
                        connectNulls: false
                    },
                ],
            }
        },
    },

    methods: {
        ...mapActions(['fetchPriceAnalyticsRows']),

        getInitialRange() {
            const today = new Date()
            const from = new Date()
            from.setDate(today.getDate() - 14)
            return { from: this.toDateString(from), to: this.toDateString(today) }
        },

        toDateString(date) {
            const y = date.getFullYear()
            const m = String(date.getMonth() + 1).padStart(2, '0')
            const d = String(date.getDate()).padStart(2, '0')
            return `${y}-${m}-${d}`
        },

        async loadData() {
            if (this.isDateInvalid) return
            this.weatherError = null
            this.temperatureByDateHour = {}
            await this.fetchPriceAnalyticsRows({ from: this.dateFrom, to: this.dateTo })
            await this.fetchTemperatureRows({ region: this.selectedRegion, from: this.dateFrom, to: this.dateTo })
            this.appliedDateFrom = this.dateFrom
            this.appliedDateTo = this.dateTo
            this.appliedRegion = this.selectedRegion
            this.loadedOnce = true
            this.statistics = null
            this.correlationMatrix = null
            this.forecast = null
            this.hourlyForecastRows = []
            this.forecastChartRows = []
        },

        async fetchTemperatureRows({ region, from, to }) {
            const coordinates = REGION_COORDINATES[region]
            if (!coordinates) {
                this.weatherError = `Для региона "${region}" пока нет координат для загрузки температуры.`
                this.temperatureByDateHour = {}
                return
            }
            try {
                this.weatherLoading = true
                const params = new URLSearchParams({
                    latitude: String(coordinates.latitude),
                    longitude: String(coordinates.longitude),
                    start_date: from,
                    end_date: to,
                    hourly: 'temperature_2m',
                    timezone: 'auto',
                })
                const response = await fetch(`https://archive-api.open-meteo.com/v1/archive?${params.toString()}`)
                if (!response.ok) throw new Error(`Ошибка загрузки температуры: ${response.status}`)
                const json = await response.json()
                const times = json?.hourly?.time || []
                const temperatures = json?.hourly?.temperature_2m || []
                const result = {}
                for (let i = 0; i < times.length; i++) {
                    const key = this.getWeatherTimeKey(times[i])
                    const value = this.toNumber(temperatures[i])
                    if (key && Number.isFinite(value)) result[key] = value
                }
                this.temperatureByDateHour = result
                if (!Object.keys(result).length) this.weatherError = 'Температура не была получена из внешнего источника по выбранному периоду.'
            } catch (error) {
                console.error('fetchTemperatureRows error', error)
                this.weatherError = 'Не удалось загрузить температуру из внешнего погодного источника. Модель будет построена без температуры.'
                this.temperatureByDateHour = {}
            } finally {
                this.weatherLoading = false
            }
        },

        getWeatherTimeKey(time) {
            if (!time) return ''
            const [datePart, hourPart = '00:00'] = String(time).split('T')
            const hour = Number(String(hourPart).slice(0, 2))
            if (!datePart || !Number.isFinite(hour)) return ''
            return `${datePart}_${hour}`
        },

        getDateHourKey(row) {
            const date = String(row.timestamp || '').slice(0, 10)
            const hour = this.getHour(row)
            if (!date || !Number.isFinite(hour)) return ''
            return `${date}_${hour}`
        },

        async ensureDataLoaded() {
            if (!this.loadedOnce || this.dateFrom !== this.appliedDateFrom || this.dateTo !== this.appliedDateTo || this.selectedRegion !== this.appliedRegion) {
                await this.loadData()
            }
        },

        async showStatistics() {
            await this.ensureDataLoaded()
            const rows = this.filteredRows
            if (!rows.length) {
                this.statistics = null
                this.correlationMatrix = null
                return
            }
            const priceValues = rows.map(r => this.getPrice(r)).filter(Number.isFinite)
            const volumeValues = rows.map(r => this.getVolume(r)).filter(Number.isFinite)
            const temperatureValues = rows.map(r => this.toNumber(r.temperature)).filter(Number.isFinite)

            this.statistics = {
                variables: [
                    this.describeVariable('price_sell', 'Цена продажи', priceValues),
                    this.describeVariable('full_plan', 'Объём', volumeValues),
                    this.describeVariable('temperature', 'Температура', temperatureValues),
                ],
            }
            this.buildCorrelationAnalysis(rows)
        },

        describeVariable(key, label, values) {
            const finite = values.filter(v => Number.isFinite(v))
            if (finite.length < 2) {
                return { key, label, n: finite.length, mean: NaN, sd: NaN, median: NaN, trimmed: NaN, mad: NaN, min: NaN, max: NaN, range: NaN, skew: NaN, kurtosis: NaN, se: NaN }
            }
            const min = Math.min(...finite)
            const max = Math.max(...finite)
            const m = this.mean(finite)
            const s2 = this.sum(finite.map(v => (v - m) ** 2)) / (finite.length - 1)
            const sd = Math.sqrt(s2)
            return {
                key, label, n: finite.length, mean: m, sd, median: this.median(finite), trimmed: this.trimmedMean(finite, 0.1),
                mad: this.medianAbsoluteDeviation(finite), min, max, range: max - min, skew: this.skewness(finite),
                kurtosis: this.kurtosis(finite), se: sd / Math.sqrt(finite.length),
            }
        },

        buildCorrelationAnalysis(rows) {
            const rowsWithLag = rows.map((row, index) => {
                const previousRow = index > 0 ? rows[index - 1] : null
                const previousPrice = previousRow ? this.getPrice(previousRow) : NaN
                return { row, previousPrice }
            })
            const variables = this.getCorrelationVariables(rowsWithLag)
            const usableVariables = variables.filter(variable => {
                const values = variable.values.filter(value => Number.isFinite(value))
                const uniqueValues = new Set(values)
                return values.length >= 10 && uniqueValues.size > 1
            })
            if (usableVariables.length < 2) {
                this.correlationMatrix = null
                return
            }
            this.correlationMatrix = {
                headers: usableVariables.map(variable => variable.label),
                rows: usableVariables.map(rowVariable => ({
                    label: rowVariable.label,
                    values: usableVariables.map(colVariable => ({
                        key: `${rowVariable.key}_${colVariable.key}`,
                        value: this.pearsonCorrelation(rowVariable.values, colVariable.values),
                    })),
                })),
            }
        },

        getCorrelationVariables(rowsWithLag) {
            const variables = [{ key: 'price_sell', label: 'Цена', values: rowsWithLag.map(item => this.getPrice(item.row)) }]
            const selected = [...this.selectedFactors]
            if (selected.includes('full_plan')) variables.push({ key: 'full_plan', label: 'Объём', values: rowsWithLag.map(item => this.getVolume(item.row)) })
            if (selected.includes('previousPrice')) variables.push({ key: 'previousPrice', label: 'Пред. цена', values: rowsWithLag.map(item => item.previousPrice) })
            if (selected.includes('hourCycle')) variables.push({ key: 'hour', label: 'Час', values: rowsWithLag.map(item => this.getHour(item.row)) })
            if (selected.includes('dayCycle')) variables.push({ key: 'dayOfWeek', label: 'День недели', values: rowsWithLag.map(item => this.getDayOfWeek(item.row)) })
            if (selected.includes('monthDummy')) variables.push({ key: 'month', label: 'Месяц', values: rowsWithLag.map(item => this.getMonth(item.row)) })
            if (selected.includes('temperature')) variables.push({ key: 'temperature', label: 'Температура', values: rowsWithLag.map(item => this.getFactorValue(item, 'temperature')) })
            if (selected.includes('HPP')) variables.push({ key: 'HPP', label: 'ГЭС', values: rowsWithLag.map(item => this.getFactorValue(item, 'HPP')) })
            if (selected.includes('CHP')) variables.push({ key: 'CHP', label: 'ТЭС', values: rowsWithLag.map(item => this.getFactorValue(item, 'CHP')) })
            if (selected.includes('Q_cons')) variables.push({ key: 'Q_cons', label: 'Потребление', values: rowsWithLag.map(item => this.getFactorValue(item, 'Q_cons')) })
            if (selected.includes('Q_exp')) variables.push({ key: 'Q_exp', label: 'Экспорт', values: rowsWithLag.map(item => this.getFactorValue(item, 'Q_exp')) })
            if (selected.includes('Q_imp')) variables.push({ key: 'Q_imp', label: 'Импорт', values: rowsWithLag.map(item => this.getFactorValue(item, 'Q_imp')) })
            return variables
        },

        pearsonCorrelation(valuesA, valuesB) {
            const pairs = []
            for (let i = 0; i < valuesA.length; i++) {
                const a = valuesA[i]
                const b = valuesB[i]
                if (Number.isFinite(a) && Number.isFinite(b)) pairs.push([a, b])
            }
            if (pairs.length < 2) return NaN
            const aValues = pairs.map(pair => pair[0])
            const bValues = pairs.map(pair => pair[1])
            const meanA = this.mean(aValues)
            const meanB = this.mean(bValues)
            const numerator = pairs.reduce((sum, pair) => sum + (pair[0] - meanA) * (pair[1] - meanB), 0)
            const denominatorA = Math.sqrt(aValues.reduce((sum, value) => sum + Math.pow(value - meanA, 2), 0))
            const denominatorB = Math.sqrt(bValues.reduce((sum, value) => sum + Math.pow(value - meanB, 2), 0))
            const denominator = denominatorA * denominatorB
            return denominator ? numerator / denominator : NaN
        },

        formatCorrelation(value) {
            if (!Number.isFinite(Number(value))) return '—'
            return Number(value).toFixed(2)
        },

        getCorrelationCellStyle(value) {
            if (!Number.isFinite(Number(value))) return { backgroundColor: 'rgba(0, 0, 0, 0.03)' }
            const normalized = Math.min(Math.abs(value), 1)
            const opacity = 0.12 + normalized * 0.45
            if (value > 0) return { backgroundColor: `rgba(76, 175, 80, ${opacity})` }
            if (value < 0) return { backgroundColor: `rgba(244, 67, 54, ${opacity})` }
            return { backgroundColor: 'rgba(0, 0, 0, 0.03)' }
        },

        async buildForecast() {
            await this.ensureDataLoaded()
            const rows = this.filteredRows
            if (rows.length < 48) {
                alert('Недостаточно данных. Нужно минимум 48 часов.')
                return
            }

            if (this.forecastMethod === 'ar') {
                this.buildAutoRegressiveForecast(rows)
            } else {
                this.buildExogenousForecast(rows)
            }
        },

        buildAutoRegressiveForecast(rows) {
            const lags = 24 // Берем 24 предыдущих часа
            const prices = rows.map(r => this.getPrice(r)).filter(Number.isFinite)
            
            const X = []
            const y = []
            for (let i = lags; i < prices.length; i++) {
                X.push(prices.slice(i - lags, i))
                y.push(prices[i])
            }

            const beta = this.calculateOlsCoefficients(X, y)
            if (!beta) {
                alert('Не удалось обучить AR-модель.')
                return
            }

            // Итеративный прогноз
            const forecastPrices = []
            const history = [...prices]
            for (let step = 0; step < this.forecastHorizon; step++) {
                const lastLags = history.slice(-lags)
                const nextPrice = this.dot(lastLags, beta)
                forecastPrices.push(nextPrice)
                history.push(nextPrice)
            }

            // Сборка данных для графика
            const histSlice = rows.slice(-48) // Показываем последние 48 часов истории
            const histDates = histSlice.map(r => this.getDateTimeLabel(r))
            const histPrices = histSlice.map(r => this.getPrice(r))

            const lastDate = new Date(rows[rows.length - 1].timestamp)
            const futureDates = this.generateFutureTimestamps(this.forecastHorizon, lastDate)

            this.forecastChartRows = [
                ...histDates.map((date, idx) => ({ dateTime: date, actual: histPrices[idx], predicted: null })),
                // Чтобы линия прогноза соединилась с историей, последнюю историческую точку дублируем в прогноз
                { dateTime: histDates[histDates.length - 1], actual: null, predicted: histPrices[histPrices.length - 1] },
                ...futureDates.map((date, idx) => ({ dateTime: date, actual: null, predicted: Number(forecastPrices[idx].toFixed(2)) }))
            ]

            // Убираем дубликат последней даты для ECharts (чтобы не было двух точек на оси)
            const uniqueChartRows = []
            const seenDates = new Set()
            this.forecastChartRows.forEach(r => {
                if (!seenDates.has(r.dateTime)) {
                    uniqueChartRows.push({ dateTime: r.dateTime, actual: r.actual, predicted: r.predicted })
                    seenDates.add(r.dateTime)
                } else {
                    // Если дата дублируется, объединяем значения
                    const existing = uniqueChartRows.find(x => x.dateTime === r.dateTime)
                    if (existing) {
                        existing.predicted = r.predicted
                    }
                }
            })
            this.forecastChartRows = uniqueChartRows

            this.hourlyForecastRows = futureDates.map((date, idx) => ({
                dateTime: date,
                predictedPrice: this.formatNumber(forecastPrices[idx]),
            }))

            this.forecast = {
                trainCount: prices.length,
                usedFactors: ['Предыдущие 24 часа цены'],
                r2: NaN, // R2 для AR мы не считаем на тесте, так как цель - прогноз
                qualityColor: 'blue-lighten-1',
                qualityLabel: 'Прогноз AR построен',
                avgPredictedPrice: this.mean(forecastPrices),
                skippedFactors: [],
            }
        },

        buildExogenousForecast(rows) {
            const rowsWithLag = rows.map((row, index) => {
                const previousRow = index > 0 ? rows[index - 1] : null
                const previousPrice = previousRow ? this.getPrice(previousRow) : NaN
                return { row, previousPrice }
            })

            const selected = [...this.selectedFactors]
            const expandedFactors = []

            for (const factor of selected) {
                if (factor === 'hourCycle') expandedFactors.push('hourSin', 'hourCos')
                else if (factor === 'dayCycle') expandedFactors.push('daySin', 'dayCos')
                else if (factor === 'monthDummy') { for (let month = 2; month <= 12; month++) expandedFactors.push(`month_${month}`) }
                else expandedFactors.push(factor)
            }

            const usedFactors = expandedFactors.filter(factor => {
                const values = rowsWithLag.map(item => this.getFactorValue(item, factor)).filter(value => Number.isFinite(value))
                return values.length >= 24 && new Set(values).size > 1
            })

            const preparedRows = rowsWithLag
                .map(item => {
                    const y = this.getPrice(item.row)
                    const x = usedFactors.map(factor => this.getFactorValue(item, factor))
                    return { y, x, source: item.row }
                })
                .filter(item => Number.isFinite(item.y) && item.x.every(value => Number.isFinite(value)))

            if (preparedRows.length < 24) {
                alert('Недостаточно данных для OLS-модели с выбранными факторами.')
                return
            }

            const yValues = preparedRows.map(item => item.y)
            const xValues = preparedRows.map(item => item.x)
            
            const means = []
            const stds = []
            for (let j = 0; j < usedFactors.length; j++) {
                const column = xValues.map(row => row[j])
                const mean = this.mean(column)
                const std = this.std(column) || 1
                means.push(mean)
                stds.push(std)
            }

            const design = xValues.map(row => [1, ...row.map((value, index) => (value - means[index]) / stds[index])])
            const beta = this.calculateOlsCoefficients(design, yValues)
            if (!beta) {
                alert('Не удалось обучить OLS-модель.')
                return
            }

            // Усредняем экзогенные факторы за последние 24 часа для будущего прогноза
            const last24Rows = rowsWithLag.slice(-24)
            const futureFactorsAvg = {}
            // Временные признаки мы вычислим отдельно для каждого часа, а вот температуру и объем усредним
            const avgFactors = ['full_plan', 'temperature', 'HPP', 'CHP', 'Q_cons', 'Q_exp', 'Q_imp']
            avgFactors.forEach(f => {
                const vals = last24Rows.map(item => this.getFactorValue(item, f)).filter(Number.isFinite)
                futureFactorsAvg[f] = vals.length ? this.mean(vals) : NaN
            })

            const lastDate = new Date(rows[rows.length - 1].timestamp)
            const futureDates = this.generateFutureTimestamps(this.forecastHorizon, lastDate)
            
            const forecastPrices = []

            futureDates.forEach(dateStr => {
                // Создаем фейковую строку для извлечения временных признаков
                const [datePart, timePart] = dateStr.split(' ')
                const [year, month, day] = datePart.split('-').map(Number)
                const hour = Number(timePart.split(':')[0])
                const fakeDate = new Date(year, month - 1, day, hour)
                
                const fakeRow = {
                    timestamp: dateStr,
                    hour: hour,
                    temperature: futureFactorsAvg.temperature,
                    full_plan: futureFactorsAvg.full_plan,
                    plan_GES: futureFactorsAvg.HPP,
                    plan_TES: futureFactorsAvg.CHP,
                    plan_consumption: futureFactorsAvg.Q_cons,
                    plan_export: futureFactorsAvg.Q_exp,
                    plan_import: futureFactorsAvg.Q_imp,
                }
                
                // previousPrice для будущего берем как предыдущий прогноз
                const prevPrice = forecastPrices.length ? forecastPrices[forecastPrices.length - 1] : rows[rows.length - 1] ? this.getPrice(rows[rows.length - 1]) : 0
                const itemForFactor = { row: fakeRow, previousPrice: prevPrice }

                const x = usedFactors.map(factor => {
                    const val = this.getFactorValue(itemForFactor, factor)
                    return Number.isFinite(val) ? val : 0
                })
                
                const designRow = [1, ...x.map((value, index) => (value - means[index]) / stds[index])]
                const pred = this.dot(designRow, beta)
                forecastPrices.push(pred)
            })

            // Сборка данных для графика
            const histSlice = rows.slice(-48)
            const histDates = histSlice.map(r => this.getDateTimeLabel(r))
            const histPrices = histSlice.map(r => this.getPrice(r))

            this.forecastChartRows = [
                ...histDates.map((date, idx) => ({ dateTime: date, actual: histPrices[idx], predicted: null })),
                { dateTime: histDates[histDates.length - 1], actual: null, predicted: histPrices[histPrices.length - 1] },
                ...futureDates.map((date, idx) => ({ dateTime: date, actual: null, predicted: Number(forecastPrices[idx].toFixed(2)) }))
            ]

            const uniqueChartRows = []
            const seenDates = new Set()
            this.forecastChartRows.forEach(r => {
                if (!seenDates.has(r.dateTime)) {
                    uniqueChartRows.push({ dateTime: r.dateTime, actual: r.actual, predicted: r.predicted })
                    seenDates.add(r.dateTime)
                } else {
                    const existing = uniqueChartRows.find(x => x.dateTime === r.dateTime)
                    if (existing) existing.predicted = r.predicted
                }
            })
            this.forecastChartRows = uniqueChartRows

            this.hourlyForecastRows = futureDates.map((date, idx) => ({
                dateTime: date,
                predictedPrice: this.formatNumber(forecastPrices[idx]),
            }))

            this.forecast = {
                trainCount: yValues.length,
                usedFactors: usedFactors.map(v => this.getFactorLabel(v)),
                r2: NaN,
                qualityColor: 'green-lighten-1',
                qualityLabel: 'Прогноз OLS построен',
                avgPredictedPrice: this.mean(forecastPrices),
                skippedFactors: expandedFactors.filter(f => !usedFactors.includes(f) && !f.startsWith('month_')).map(v => this.getFactorLabel(v)),
            }
        },

        generateFutureTimestamps(count, startDate) {
            const result = []
            for (let i = 1; i <= count; i++) {
                const d = new Date(startDate.getTime() + i * 3600 * 1000)
                const y = d.getFullYear()
                const m = String(d.getMonth() + 1).padStart(2, '0')
                const day = String(d.getDate()).padStart(2, '0')
                const h = String(d.getHours()).padStart(2, '0')
                result.push(`${y}-${m}-${day} ${h}:00`)
            }
            return result
        },

        calculateOlsCoefficients(xRows, yValues) {
            const xT = this.transpose(xRows)
            const xTx = this.multiplyMatrices(xT, xRows)
            const xTy = this.multiplyMatrixVector(xT, yValues)
            for (let i = 0; i < xTx.length; i++) xTx[i][i] += 1e-6
            const inverse = this.invertMatrix(xTx)
            if (!inverse) return null
            return this.multiplyMatrixVector(inverse, xTy)
        },

        getPrice(row) { return this.toNumber(row.price_sell ?? row.Price ?? row.price ?? row.priceSell) },
        getVolume(row) { return this.toNumber(row.full_plan ?? row.volume ?? row.Q_cons ?? row.q_cons) },
        getHour(row) {
            const directHour = this.toNumber(row.hour)
            if (Number.isFinite(directHour)) return directHour
            const date = new Date(row.timestamp)
            return Number.isNaN(date.getTime()) ? NaN : date.getHours()
        },
        getDayOfWeek(row) {
            const date = new Date(row.timestamp)
            return Number.isNaN(date.getTime()) ? NaN : date.getDay()
        },
        getMonth(row) {
            const date = new Date(row.timestamp)
            return Number.isNaN(date.getTime()) ? NaN : date.getMonth() + 1
        },
        getDateTimeLabel(row) {
            const date = row.timestamp || ''
            const hour = this.getHour(row)
            if (!Number.isFinite(hour)) return date
            return `${date} ${String(hour).padStart(2, '0')}:00`
        },

        getFactorValue(item, factor) {
            const row = item.row
            if (factor === 'full_plan') return this.getVolume(row)
            if (factor === 'previousPrice') return item.previousPrice
            if (factor === 'temperature') return this.toNumber(row.temperature)
            if (factor === 'hourSin') { const hour = this.getHour(row); return Number.isFinite(hour) ? Math.sin((2 * Math.PI * hour) / 24) : NaN }
            if (factor === 'hourCos') { const hour = this.getHour(row); return Number.isFinite(hour) ? Math.cos((2 * Math.PI * hour) / 24) : NaN }
            if (factor === 'daySin') { const day = this.getDayOfWeek(row); return Number.isFinite(day) ? Math.sin((2 * Math.PI * day) / 7) : NaN }
            if (factor === 'dayCos') { const day = this.getDayOfWeek(row); return Number.isFinite(day) ? Math.cos((2 * Math.PI * day) / 7) : NaN }
            if (factor.startsWith('month_')) {
                const monthNumber = Number(factor.replace('month_', ''))
                const currentMonth = this.getMonth(row)
                if (!Number.isFinite(currentMonth) || !Number.isFinite(monthNumber)) return NaN
                return currentMonth === monthNumber ? 1 : 0
            }
            const aliases = {
                HPP: ['plan_GES', 'HPP', 'hpp', 'hydro', 'ges'],
                CHP: ['plan_TES', 'CHP', 'NPP', 'chp', 'npp', 'tes'],
                Q_cons: ['plan_consumption', 'Q_cons', 'q_cons', 'consumption'],
                Q_exp: ['plan_export', 'Q_exp', 'q_exp', 'export'],
                Q_imp: ['plan_import', 'Q_imp', 'q_imp', 'import'],
            }
            const fields = aliases[factor] || [factor]
            for (const field of fields) {
                if (row[field] !== undefined && row[field] !== null) {
                    const value = this.toNumber(row[field])
                    if (Number.isFinite(value)) return value
                }
            }
            return NaN
        },

        getFactorLabel(value) {
            const labels = {
                full_plan: 'Объём', previousPrice: 'Цена предыдущего часа', hourCycle: 'Циклический час суток',
                hourSin: 'Час суток sin', hourCos: 'Час суток cos', dayCycle: 'Циклический день недели',
                daySin: 'День недели sin', dayCos: 'День недели cos', monthDummy: 'Месяц',
                month_2: 'Февраль', month_3: 'Март', month_4: 'Апрель', month_5: 'Май', month_6: 'Июнь', month_7: 'Июль',
                month_8: 'Август', month_9: 'Сентябрь', month_10: 'Октябрь', month_11: 'Ноябрь', month_12: 'Декабрь',
                temperature: 'Температура', HPP: 'Выработка ГЭС', CHP: 'Выработка ТЭС', Q_cons: 'Потребление',
                Q_exp: 'Экспорт', Q_imp: 'Импорт',
            }
            return labels[value] || value
        },

        toNumber(value) {
            if (value === null || value === undefined || value === '') return NaN
            if (typeof value === 'number') return Number.isFinite(value) ? value : NaN
            const normalized = String(value).replace(/\s/g, '').replace(',', '.')
            const number = Number(normalized)
            return Number.isFinite(number) ? number : NaN
        },
        sum(values) { return values.reduce((acc, value) => acc + value, 0) },
        mean(values) { return values.length ? this.sum(values) / values.length : 0 },
        std(values) {
            if (values.length < 2) return 0
            const avg = this.mean(values)
            return Math.sqrt(this.mean(values.map(value => Math.pow(value - avg, 2))))
        },
        median(values) {
            const sorted = [...values].sort((a, b) => a - b)
            const n = sorted.length
            if (!n) return NaN
            const mid = Math.floor(n / 2)
            if (n % 2 === 0) return (sorted[mid - 1] + sorted[mid]) / 2
            return sorted[mid]
        },
        trimmedMean(values, trim = 0.1) {
            const n = values.length
            const sorted = [...values].sort((a, b) => a - b)
            const k = Math.floor(n * trim)
            return this.mean(sorted.slice(k, n - k))
        },
        medianAbsoluteDeviation(values) {
            const med = this.median(values)
            return this.median(values.map(v => Math.abs(v - med))) * 1.4826
        },
        skewness(values) {
            const n = values.length
            if (n < 3) return NaN
            const m = this.mean(values)
            const s = this.std(values)
            return Math.sqrt(n * (n - 1)) / (n - 2) * (this.sum(values.map(x => ((x - m) / s) ** 3)) / n)
        },
        kurtosis(values) {
            const n = values.length
            if (n < 4) return NaN
            const m = this.mean(values)
            const s = this.std(values)
            return n * (n + 1) / ((n - 1) * (n - 2) * (n - 3)) * this.sum(values.map(x => ((x - m) / s) ** 4)) - 3 * (n - 1) ** 2 / ((n - 2) * (n - 3))
        },
        formatDisplayDate(iso) {
            if (!iso) return ''
            const match = String(iso).match(/^(\d{4})-(\d{2})-(\d{2})/)
            return match ? `${match[3]}.${match[2]}.${match[1]}` : ''
        },
        dot(a, b) { return a.reduce((sum, value, index) => sum + value * b[index], 0) },
        transpose(matrix) { return matrix[0].map((_, colIndex) => matrix.map(row => row[colIndex])) },
        multiplyMatrices(a, b) {
            return a.map(row => b[0].map((_, colIndex) => row.reduce((sum, value, rowIndex) => sum + value * b[rowIndex][colIndex], 0)))
        },
        multiplyMatrixVector(matrix, vector) {
            return matrix.map(row => row.reduce((sum, value, index) => sum + value * vector[index], 0))
        },
        invertMatrix(matrix) {
            const n = matrix.length
            const augmented = matrix.map((row, i) => {
                const identityRow = Array(n).fill(0)
                identityRow[i] = 1
                return [...row, ...identityRow]
            })
            for (let i = 0; i < n; i++) {
                let maxRow = i
                for (let k = i + 1; k < n; k++) {
                    if (Math.abs(augmented[k][i]) > Math.abs(augmented[maxRow][i])) maxRow = k
                }
                if (Math.abs(augmented[maxRow][i]) < 1e-12) return null
                const temp = augmented[i]
                augmented[i] = augmented[maxRow]
                augmented[maxRow] = temp
                const pivot = augmented[i][i]
                for (let j = 0; j < 2 * n; j++) augmented[i][j] /= pivot
                for (let k = 0; k < n; k++) {
                    if (k === i) continue
                    const factor = augmented[k][i]
                    for (let j = 0; j < 2 * n; j++) augmented[k][j] -= factor * augmented[i][j]
                }
            }
            return augmented.map(row => row.slice(n))
        },
        formatNumber(value, digits = 2) {
            if (!Number.isFinite(Number(value))) return '0'
            return Number(value).toLocaleString('ru-RU', { minimumFractionDigits: digits, maximumFractionDigits: digits })
        },
        formatDescribeValue(value, digits) {
            if (!Number.isFinite(Number(value))) return '—'
            if (digits === 0) return String(Math.round(Number(value)))
            return Number(value).toLocaleString('ru-RU', { minimumFractionDigits: digits, maximumFractionDigits: digits })
        },
    },
}
</script>

<style scoped>
/* Стили для таблиц и скролла оставляем как были */
.correlation-scroll {
    overflow-x: auto;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    background: #ffffff;
}
.correlation-scroll :deep(.v-table) { border: none; }
:deep(.v-field) { border-radius: 8px; }
:deep(.v-selection-control__input) { transform: scale(0.95); }

/* Фикс для HintFormula, чтобы не сжималась */
.d-flex.align-center.flex-shrink-0 {
    flex-shrink: 0 !important;
}
</style>
