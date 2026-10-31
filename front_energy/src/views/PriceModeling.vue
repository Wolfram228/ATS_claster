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
                <v-col v-for="factor in coreFactors" :key="factor.value" cols="12" md="6">
                    <v-checkbox
                        v-model="selectedFactors"
                        :label="factor.label"
                        :value="factor.value"
                        color="blue-lighten-1"
                        hide-details
                    />
                </v-col>
                <v-col v-for="factor in otherFactors" :key="factor.value" cols="12" md="6">
                    <v-checkbox
                        v-model="selectedFactors"
                        :label="factor.label"
                        :value="factor.value"
                        hide-details
                    />
                </v-col>
            </v-row>
        </v-card>
    </v-col>
</v-row>

                <v-row class="mt-4">
                    <v-col cols="12" md="4">
                        <v-select
                            v-model="forecastHorizon"
                            :items="forecastHorizonItems"
                            label="Горизонт прогноза"
                            hide-details
                        />
                    </v-col>
                    <v-col cols="12" md="4">
                        <v-select
                            v-model="trainingWindow"
                            :items="trainingWindowItems"
                            label="Глубина обучения"
                            hide-details
                        />
                    </v-col>
                    <v-col cols="12" md="4">
                        <v-select
                            v-model="arLags"
                            :items="arLagsItems"
                            label="Лаги AR-модели"
                            hide-details
                        />
                    </v-col>
                </v-row>

                <v-row class="mt-4">
                    <v-col cols="12" md="4">
                        <v-btn block min-height="52" color="blue-grey-lighten-1" :loading="priceAnalyticsLoading || weatherLoading" :disabled="isDateInvalid" @click="loadData">
                            Загрузить данные
                        </v-btn>
                    </v-col>
                    <v-col cols="12" md="4">
                        <v-btn block min-height="52" color="blue-lighten-1" :loading="priceAnalyticsLoading || weatherLoading" :disabled="isDateInvalid" @click="showStatistics">
                            Показать статистику
                        </v-btn>
                    </v-col>
                    <v-col cols="12" md="4">
                        <v-btn block min-height="52" color="green-lighten-1" :loading="priceAnalyticsLoading || weatherLoading" :disabled="isDateInvalid" @click="buildForecast">
                            Построить прогноз
                        </v-btn>
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
                            <td class="text-left">Медиана</td>
                            <td v-for="variable in statistics.variables" :key="variable.key">{{ formatDescribeValue(variable.median, 2) }}</td>
                        </tr>
                        <tr>
                            <td class="text-left">Усечённое среднее (10 %)</td>
                            <td v-for="variable in statistics.variables" :key="variable.key">{{ formatDescribeValue(variable.trimmed, 2) }}</td>
                        </tr>
                        <tr>
                            <td class="text-left">Медианное абсолютное отклонение</td>
                            <td v-for="variable in statistics.variables" :key="variable.key">{{ formatDescribeValue(variable.mad, 2) }}</td>
                        </tr>
                        <tr>
                            <td class="text-left">Минимум</td>
                            <td v-for="variable in statistics.variables" :key="variable.key">{{ formatDescribeValue(variable.min, 2) }}</td>
                        </tr>
                        <tr>
                            <td class="text-left">Максимум</td>
                            <td v-for="variable in statistics.variables" :key="variable.key">{{ formatDescribeValue(variable.max, 2) }}</td>
                        </tr>
                        <tr>
                            <td class="text-left">Размах (max − min)</td>
                            <td v-for="variable in statistics.variables" :key="variable.key">{{ formatDescribeValue(variable.range, 2) }}</td>
                        </tr>
                        <tr>
                            <td class="text-left">Асимметрия</td>
                            <td v-for="variable in statistics.variables" :key="variable.key">{{ formatDescribeValue(variable.skew, 3) }}</td>
                        </tr>
                        <tr>
                            <td class="text-left">Эксцесс</td>
                            <td v-for="variable in statistics.variables" :key="variable.key">{{ formatDescribeValue(variable.kurtosis, 3) }}</td>
                        </tr>
                        <tr>
                            <td class="text-left">Стандартная ошибка среднего</td>
                            <td v-for="variable in statistics.variables" :key="variable.key">{{ formatDescribeValue(variable.se, 2) }}</td>
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
        <v-card v-if="currentForecast" class="pa-4 mb-4" elevation="1" rounded="lg" variant="outlined" style="border-color: rgba(0, 0, 0, 0.2)">
            <div class="d-flex align-center justify-space-between flex-wrap mb-4">
                <div class="d-flex align-center flex-wrap">
                    <div class="text-h5 font-weight-bold me-2" align="left">Результат моделирования</div>
                    <div class="d-flex align-center flex-shrink-0">
                        <HintFormula>
                            <div style="font-size: 13px; text-align: left; min-width: 200px;">
                                <strong>Авторегрессия (AR):</strong> прогноз на основе {{ arLags }} предыдущих часов цены.<br><br>
                                <strong>Мультифакторный (OLS):</strong> на основе выбранных факторов; для будущих часов факторы берутся как средние за последние 24 ч.
                            </div>
                        </HintFormula>
                    </div>
                </div>

                <v-btn-group density="compact" variant="outlined">
                    <v-btn :color="selectedForecastView === 'ar' ? 'green-lighten-1' : ''" @click="selectedForecastView = 'ar'">Авторегрессия (AR)</v-btn>
                    <v-btn :color="selectedForecastView === 'ols' ? 'green-lighten-1' : ''" @click="selectedForecastView = 'ols'">Мультифакторный (OLS)</v-btn>
                </v-btn-group>
            </div>

            <div class="text-body-2 text-grey-darken-1 mt-1" align="left">
                Метод: {{ selectedForecastView === 'ar' ? 'Авторегрессия' : 'Множественная линейная регрессия (OLS)' }}.
                Прогноз на {{ forecastHorizon }} часов вперёд.
            </div>

            <v-table class="mt-4">
                <tbody>
                    <tr><td class="font-weight-bold" style="width: 45%">Регион</td><td>{{ selectedRegion }}</td></tr>
                    <tr><td class="font-weight-bold">Целевая переменная</td><td>{{ targetVariable }}</td></tr>
                    <tr v-if="currentForecast.usedFactors"><td class="font-weight-bold">Использованные факторы</td><td>{{ currentForecast.usedFactors.join(', ') }}</td></tr>
                    <tr><td class="font-weight-bold">Исторических данных (часов)</td><td>{{ currentForecast.trainCount }}</td></tr>
                    <tr><td class="font-weight-bold">Горизонт прогноза (часов)</td><td>{{ forecastHorizon }}</td></tr>
                    <tr>
                        <td class="font-weight-bold" colspan="2" style="padding-top: 12px;">Качество модели (backtesting 80/20)</td>
                    </tr>
                    <tr>
                        <td class="pl-6">R² на тестовой выборке</td>
                       <td>{{ formatOptional(currentForecast.backtest?.r2, 4) }}</td>
                    </tr>
                    <tr>
                        <td class="pl-6">MAE (средняя абсолютная ошибка)</td>
                        <td>{{ formatOptional(currentForecast.backtest?.mae) }} руб./МВт·ч</td>
                    </tr>
                    <tr>
                        <td class="pl-6">RMSE (среднеквадратичная ошибка)</td>
                        <td>{{ formatOptional(currentForecast.backtest?.rmse) }} руб./МВт·ч</td>
                    </tr>
                    <tr><td class="font-weight-bold">Средняя прогнозируемая цена</td><td>{{ formatNumber(currentForecast.avgPredictedPrice) }} руб./МВт·ч</td></tr>
                </tbody>
            </v-table>

            <v-alert v-if="currentForecast.skippedFactors && currentForecast.skippedFactors.length" type="warning" variant="tonal" class="mt-4">
                Следующие факторы отсутствуют и не были использованы: {{ currentForecast.skippedFactors.join(', ') }}.
            </v-alert>
        </v-card>

        <!-- Блок 5: График -->
        <v-card v-if="currentChartRows.length" class="pa-4 mb-4" elevation="1" rounded="lg" variant="outlined" style="border-color: rgba(0, 0, 0, 0.2)">
            <div class="text-h5 font-weight-bold" align="left">График фактической и прогнозной цены</div>
            <div class="text-body-2 text-grey-darken-1 mt-1 mb-4" align="left">
               Фактические данные за весь выбранный период и параллельный прогноз по всей истории. Прогноз продолжается в будущее на заданный горизонт.
            </div>
            <VChart :option="forecastChartOption" style="height: 420px; border: 1px solid rgba(0,0,0,0.2);" />
        </v-card>

        <!-- Блок 6: Таблица прогноза -->
        <v-card v-if="currentHourlyRows.length" class="pa-4 mb-4" elevation="1" rounded="lg" variant="outlined" style="border-color: rgba(0, 0, 0, 0.2)">
            <div class="text-h5 font-weight-bold" align="left">Почасовой прогноз</div>
            <div class="text-body-2 text-grey-darken-1 mt-1 mb-4" align="left">
                Прогноз построен для каждого часа на {{ forecastHorizon }} часов вперёд.
            </div>
            <v-data-table :headers="hourlyForecastHeaders" :items="currentHourlyRows" density="comfortable" items-per-page="24" />
        </v-card>
    </v-container>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'
import HintFormula from '../components/HintFormula.vue'

const REGION_COORDINATES = {
  'Алтайский край': { latitude: 53.35, longitude: 83.76 },
  'Архангельская область': { latitude: 64.54, longitude: 40.52 },
  'Астраханская область': { latitude: 46.35, longitude: 48.04 },
  'Белгородская область': { latitude: 50.60, longitude: 36.59 },
  'Брянская область': { latitude: 53.25, longitude: 34.37 },
  'Владимирская область': { latitude: 56.13, longitude: 40.40 },
  'Волгоградская область': { latitude: 48.71, longitude: 44.51 },
  'Вологодская область': { latitude: 59.22, longitude: 39.89 },
  'Воронежская область': { latitude: 51.66, longitude: 39.20 },
  'Город Севастополь': { latitude: 44.62, longitude: 33.52 },
  'Забайкальский край': { latitude: 52.03, longitude: 113.50 },
  'Ивановская область': { latitude: 56.99, longitude: 40.98 },
  'Иркутская область': { latitude: 52.29, longitude: 104.30 },
  'Кабардино-Балкарская Республика': { latitude: 43.49, longitude: 43.61 },
  'Калужская область': { latitude: 54.51, longitude: 36.26 },
  'Карачаево-Черкесская Республика': { latitude: 44.23, longitude: 42.06 },
  'Кемеровская область': { latitude: 55.35, longitude: 86.09 },
  'Кировская область': { latitude: 58.60, longitude: 49.66 },
  'Костромская область': { latitude: 57.77, longitude: 40.93 },
  'Краснодарский край': { latitude: 45.04, longitude: 38.97 },
  'Красноярский край': { latitude: 56.01, longitude: 92.85 },
  'Курганская область': { latitude: 55.44, longitude: 65.34 },
  'Курская область': { latitude: 51.73, longitude: 36.19 },
  'Ленинградская область': { latitude: 59.94, longitude: 30.31 },
  'Липецкая область': { latitude: 52.61, longitude: 39.59 },
  'Московская область': { latitude: 55.75, longitude: 37.62 },
  'Мурманская область': { latitude: 68.97, longitude: 33.08 },
  'Нижегородская область': { latitude: 56.33, longitude: 44.00 },
  'Новгородская область': { latitude: 58.52, longitude: 31.27 },
  'Новосибирская область': { latitude: 55.03, longitude: 82.92 },
  'Омская область': { latitude: 54.99, longitude: 73.37 },
  'Оренбургская область': { latitude: 51.77, longitude: 55.10 },
  'Орловская область': { latitude: 52.97, longitude: 36.06 },
  'Пензенская область': { latitude: 53.20, longitude: 45.00 },
  'Пермский край': { latitude: 58.01, longitude: 56.25 },
  'Псковская область': { latitude: 57.82, longitude: 28.33 },
  'Республика Алтай': { latitude: 51.96, longitude: 85.96 },
  'Республика Башкортостан': { latitude: 54.74, longitude: 55.97 },
  'Республика Бурятия': { latitude: 51.83, longitude: 107.58 },
  'Республика Дагестан': { latitude: 42.98, longitude: 47.50 },
  'Республика Ингушетия': { latitude: 43.17, longitude: 44.82 },
  'Республика Калмыкия': { latitude: 46.31, longitude: 44.27 },
  'Республика Карелия': { latitude: 61.79, longitude: 34.36 },
  'Республика Коми': { latitude: 61.67, longitude: 50.84 },
  'Республика Крым': { latitude: 44.95, longitude: 34.10 },
  'Республика Марий Эл': { latitude: 56.63, longitude: 47.89 },
  'Республика Мордовия': { latitude: 54.18, longitude: 45.18 },
  'Республика Северная Осетия-Алания': { latitude: 43.02, longitude: 44.68 },
  'Республика Татарстан': { latitude: 55.79, longitude: 49.12 },
  'Республика Тыва': { latitude: 51.72, longitude: 94.44 },
  'Республика Хакасия': { latitude: 53.72, longitude: 91.43 },
  'Ростовская область': { latitude: 47.22, longitude: 39.72 },
  'Рязанская область': { latitude: 54.63, longitude: 39.74 },
  'Самарская область': { latitude: 53.20, longitude: 50.15 },
  'Саратовская область': { latitude: 51.53, longitude: 46.03 },
  'Свердловская область': { latitude: 56.84, longitude: 60.61 },
  'Смоленская область': { latitude: 54.78, longitude: 32.05 },
  'Ставропольский край': { latitude: 45.04, longitude: 41.97 },
  'Тамбовская область': { latitude: 52.72, longitude: 41.45 },
  'Тверская область': { latitude: 56.86, longitude: 35.90 },
  'Томская область': { latitude: 56.48, longitude: 84.95 },
  'Тульская область': { latitude: 54.19, longitude: 37.62 },
  'Тюменская область': { latitude: 57.15, longitude: 65.53 },
  'Удмуртская Республика': { latitude: 56.85, longitude: 53.20 },
  'Ульяновская область': { latitude: 54.31, longitude: 48.40 },
  'Челябинская область': { latitude: 55.16, longitude: 61.40 },
  'Чеченская Республика': { latitude: 43.32, longitude: 45.69 },
  'Чувашская Республика-Чувашия': { latitude: 56.13, longitude: 47.25 },
  'Ярославская область': { latitude: 57.63, longitude: 39.87 },
}

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

            selectedForecastView: 'ar',
            forecastHorizon: 24,
            forecastHorizonItems: [
                { title: '12 часов', value: 12 },
                { title: '24 часа', value: 24 },
                { title: '48 часов', value: 48 },
                { title: '72 часа', value: 72 },
                { title: '1 неделя (168 ч)', value: 168 },
                { title: '2 недели (336 ч)', value: 336 },
            ],

            trainingWindow: 0,
            trainingWindowItems: [
                { title: 'Весь период', value: 0 },
                { title: 'Последние 7 дней', value: 7 },
                { title: 'Последние 14 дней', value: 14 },
                { title: 'Последние 30 дней', value: 30 },
            ],

            arLags: 24,
            arLagsItems: [
                { title: '12 часов', value: 12 },
                { title: '24 часа', value: 24 },
                { title: '48 часов', value: 48 },
                { title: '72 часа', value: 72 },
                { title: '168 часов (неделя)', value: 168 },
            ],

            coreFactors: [
                { label: 'Температура', value: 'temperature' },
                { label: 'Объём', value: 'full_plan' },
                { label: 'Цена продажи', value: 'price_sell' },
                { label: 'Потребление', value: 'Q_cons' },
            ],
            otherFactors: [
                { label: 'Цена предыдущего часа', value: 'previousPrice' },
                { label: 'Циклический час суток', value: 'hourCycle' },
                { label: 'Циклический день недели', value: 'dayCycle' },
                { label: 'Месяц', value: 'monthDummy' },
                { label: 'Выработка ГЭС', value: 'HPP' },
                { label: 'Выработка ТЭС', value: 'CHP' },
                { label: 'Выработка АЭС', value: 'NPP' },
                { label: 'Выработка СЭС', value: 'SES' },
                { label: 'Выработка ВЭС', value: 'VES' },
                { label: 'Выработка прочих ВИЭ', value: 'other' },
                { label: 'Экспорт', value: 'Q_exp' },
                { label: 'Импорт', value: 'Q_imp' },
            ],
            selectedFactors: [
                'temperature', 'full_plan', 'price_sell', 'Q_cons',
                'previousPrice', 'hourCycle', 'dayCycle', 'monthDummy',
            ],

            hourlyForecastHeaders: [
                { title: 'Дата и час', key: 'dateTime', align: 'center' },
                { title: 'Прогнозная цена, руб./МВт·ч', key: 'predictedPrice', align: 'center' },
            ],
            weatherLoading: false,
            weatherError: null,
            temperatureByDateHour: {},
            statistics: null,
            correlationMatrix: null,

            forecastData: { ar: null, ols: null },
            forecastChartData: { ar: [], ols: [] },
            hourlyForecastData: { ar: [], ols: [] },
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

        currentForecast() {
            return this.forecastData[this.selectedForecastView]
        },

        currentChartRows() {
            return this.forecastChartData[this.selectedForecastView]
        },

        currentHourlyRows() {
            return this.hourlyForecastData[this.selectedForecastView]
        },

        forecastChartOption() {
            return {
                tooltip: { trigger: 'axis' },
                legend: { top: 0 },
                grid: { left: 60, right: 25, top: 60, bottom: 70 },
                dataZoom: [{ type: 'inside' }, { type: 'slider', bottom: 20 }],
                xAxis: { type: 'category', data: this.currentChartRows.map(row => row.dateTime) },
                yAxis: { type: 'value', name: 'руб./МВт·ч' },
                series: [
                    {
                        name: 'Фактическая цена',
                        type: 'line',
                        smooth: true,
                        data: this.currentChartRows.map(row => row.actual),
                        connectNulls: false,
                    },
                    {
                        name: 'Прогнозная цена',
                        type: 'line',
                        smooth: true,
                        data: this.currentChartRows.map(row => row.predicted),
                        connectNulls: false,
                    },
                ],
            }
        },
    },

    methods: {
        ...mapActions(['fetchPriceAnalyticsRows']),

        formatOptional(value, digits = 2) {
            if (value === null || value === undefined || !Number.isFinite(Number(value))) return '—'
            return this.formatNumber(value, digits)
        },

        getInitialRange() {
            const today = new Date()
            const from = new Date()
            from.setDate(today.getDate() - 14)
            return { from: this.toDateString(from), to: this.toDateString(today) }
        },

        getTrainingRows(rows) {
            if (!this.trainingWindow) return rows
            const hours = this.trainingWindow * 24
            if (rows.length <= hours) return rows
            return rows.slice(-hours)
        },

        computeMetrics(actuals, predictions) {
            const n = actuals.length
            if (n < 2) return { r2: NaN, mae: NaN, rmse: NaN, n: 0 }
            const errors = actuals.map((a, i) => a - predictions[i])
            const mae = this.mean(errors.map(e => Math.abs(e)))
            const rmse = Math.sqrt(this.mean(errors.map(e => e * e)))
            const meanActual = this.mean(actuals)
            const ssTot = actuals.reduce((s, a) => s + (a - meanActual) ** 2, 0)
            const ssRes = errors.reduce((s, e) => s + e * e, 0)
            const r2 = ssTot ? 1 - ssRes / ssTot : NaN
            return { r2, mae, rmse, n }
        },

        getQualityFromR2(r2) {
            if (!Number.isFinite(r2)) return { label: 'Не оценено', color: 'grey-lighten-1' }
            if (r2 >= 0.7) return { label: 'Высокое качество', color: 'green-lighten-1' }
            if (r2 >= 0.3) return { label: 'Среднее качество', color: 'blue-lighten-1' }
            if (r2 >= 0) return { label: 'Низкое качество', color: 'orange-lighten-1' }
            return { label: 'Нестабильная модель', color: 'red-lighten-2' }
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
            this.forecastData = { ar: null, ols: null }
            this.forecastChartData = { ar: [], ols: [] }
            this.hourlyForecastData = { ar: [], ols: [] }
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
            const selectedSet = new Set(this.selectedFactors)
            const variables = []

            if (selectedSet.has('temperature')) {
                const vals = rows.map(r => this.toNumber(r.temperature)).filter(Number.isFinite)
                variables.push(this.describeVariable('temperature', 'Температура', vals))
            }
            if (selectedSet.has('full_plan')) {
                const vals = rows.map(r => this.getVolume(r)).filter(Number.isFinite)
                variables.push(this.describeVariable('full_plan', 'Объём', vals))
            }
            if (selectedSet.has('price_sell')) {
                const vals = rows.map(r => this.getPrice(r)).filter(Number.isFinite)
                variables.push(this.describeVariable('price_sell', 'Цена продажи', vals))
            }
            if (selectedSet.has('Q_cons')) {
                const vals = rows.map(r => this.getFactorValue({ row: r, previousPrice: NaN }, 'Q_cons')).filter(Number.isFinite)
                variables.push(this.describeVariable('Q_cons', 'Потребление', vals))
            }

            this.statistics = variables.length ? { variables } : null
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
            if (selected.includes('NPP')) variables.push({ key: 'NPP', label: 'АЭС', values: rowsWithLag.map(item => this.getFactorValue(item, 'NPP')) })
            if (selected.includes('SES')) variables.push({ key: 'SES', label: 'СЭС', values: rowsWithLag.map(item => this.getFactorValue(item, 'SES')) })
            if (selected.includes('VES')) variables.push({ key: 'VES', label: 'ВЭС', values: rowsWithLag.map(item => this.getFactorValue(item, 'VES')) })
            if (selected.includes('other')) variables.push({ key: 'other', label: 'Прочие ВИЭ', values: rowsWithLag.map(item => this.getFactorValue(item, 'other')) })
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
            try {
                await this.ensureDataLoaded()
                const rows = this.filteredRows
                
                if (rows.length < 48) {
                    alert(`Недостаточно данных: ${rows.length} часов. Нужно минимум 48.`)
                    return
                }
        
                const arResult = this.buildAutoRegressiveForecast(rows)
                const olsResult = this.buildExogenousForecast(rows)
        
                // Используем spread-оператор для принудительного обновления реактивности Vue
                if (arResult) {
                    this.forecastData = { ...this.forecastData, ar: arResult.forecast }
                    this.forecastChartData = { ...this.forecastChartData, ar: arResult.chartRows }
                    this.hourlyForecastData = { ...this.hourlyForecastData, ar: arResult.hourlyRows }
                }
                if (olsResult) {
                    this.forecastData = { ...this.forecastData, ols: olsResult.forecast }
                    this.forecastChartData = { ...this.forecastChartData, ols: olsResult.chartRows }
                    this.hourlyForecastData = { ...this.hourlyForecastData, ols: olsResult.hourlyRows }
                }
            } catch (error) {
                console.error('Ошибка при построении прогноза:', error)
                alert('Произошла ошибка: ' + (error.message || error))
            }
        },

        buildAutoRegressiveForecast(rows) {
            const lags = this.arLags
            const trainRows = this.getTrainingRows(rows)
            const prices = trainRows.map(r => this.getPrice(r))

            if (prices.length < lags + 24) {
                alert(`Недостаточно данных для AR-модели с ${lags} лагами. Нужно минимум ${lags + 24} часов.`)
                return null
            }

            const totalPoints = prices.length
            const splitIndex = Math.max(Math.floor(totalPoints * 0.8), lags + 5)

            // 1) Бэктест
            const trainX = []
            const trainY = []
            for (let i = lags; i < splitIndex; i++) {
                trainX.push([1, ...prices.slice(i - lags, i)])
                trainY.push(prices[i])
            }

            let backtest = null
            if (trainX.length > 0) {
                const trainBeta = this.calculateOlsCoefficients(trainX, trainY)
                if (trainBeta) {
                    const testX = []
                    const testY = []
                    for (let i = splitIndex; i < totalPoints; i++) {
                        testX.push([1, ...prices.slice(i - lags, i)])
                        testY.push(prices[i])
                    }
                    if (testX.length > 0) {
                        const testPredicted = testX.map(row => this.dot(row, trainBeta))
                        backtest = this.computeMetrics(testY, testPredicted)
                    }
                }
            }

            // 2) Финальная модель на всех данных
            const allX = []
            const allY = []
            for (let i = lags; i < totalPoints; i++) {
                allX.push([1, ...prices.slice(i - lags, i)])
                allY.push(prices[i])
            }
            const beta = this.calculateOlsCoefficients(allX, allY)
            if (!beta) {
                alert('Не удалось обучить AR-модель.')
                return null
            }

            // 3) Итеративный прогноз в будущее
            const forecastPrices = []
            const history = [...prices]
            for (let step = 0; step < this.forecastHorizon; step++) {
                const lastLags = history.slice(-lags)
                const nextPrice = this.dot([1, ...lastLags], beta)
                forecastPrices.push(nextPrice)
                history.push(nextPrice)
            }

            // 4) Данные для графика: прогноз параллельно с фактом на всём периоде
            const chartRows = []
            for (let i = 0; i < totalPoints; i++) {
                const row = trainRows[i]
                const dateTime = this.getDateTimeLabel(row)
                const actual = prices[i]
                let predicted = null
                if (i >= lags) {
                    const lagsSlice = prices.slice(i - lags, i)
                    predicted = Number(this.dot([1, ...lagsSlice], beta).toFixed(2))
                }
                chartRows.push({ dateTime, actual, predicted })
            }

            const lastDate = new Date(trainRows[trainRows.length - 1].timestamp)
            const futureDates = this.generateFutureTimestamps(this.forecastHorizon, lastDate)
            futureDates.forEach((date, idx) => {
                chartRows.push({
                    dateTime: date,
                    actual: null,
                    predicted: Number(forecastPrices[idx].toFixed(2)),
                })
            })

            const quality = this.getQualityFromR2(backtest?.r2)

            return {
                forecast: {
                    trainCount: prices.length,
                    usedFactors: [`Предыдущие ${lags} часов цены`],
                    backtest,
                    qualityColor: quality.color,
                    qualityLabel: quality.label,
                    avgPredictedPrice: this.mean(forecastPrices),
                    skippedFactors: [],
                },
                chartRows,
                hourlyRows: futureDates.map((date, idx) => ({
                    dateTime: date,
                    predictedPrice: this.formatNumber(forecastPrices[idx]),
                })),
            }
        },

        buildExogenousForecast(rows) {
            const trainRows = this.getTrainingRows(rows)

            const rowsWithLag = trainRows.map((row, index) => {
                const previousRow = index > 0 ? trainRows[index - 1] : null
                const previousPrice = previousRow ? this.getPrice(previousRow) : NaN
                return { row, previousPrice }
            })

            const selected = [...this.selectedFactors]
            const expandedFactors = []

            for (const factor of selected) {
                if (factor === 'hourCycle') expandedFactors.push('hourSin', 'hourCos')
                else if (factor === 'dayCycle') expandedFactors.push('daySin', 'dayCos')
                else if (factor === 'monthDummy') { for (let month = 2; month <= 12; month++) expandedFactors.push(`month_${month}`) }
                else if (factor === 'price_sell') { /* пропускаем: это таргет */ }
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
                return null
            }

            const totalPoints = preparedRows.length
            const splitIndex = Math.max(Math.floor(totalPoints * 0.8), 5)
            const featureCount = usedFactors.length

            // 1) Бэктест
            let backtest = null
            if (splitIndex < totalPoints) {
                const trainSlice = preparedRows.slice(0, splitIndex)
                const testSlice = preparedRows.slice(splitIndex)

                const btMeans = []
                const btStds = []
                for (let j = 0; j < featureCount; j++) {
                    const col = trainSlice.map(r => r.x[j])
                    const m = this.mean(col)
                    const s = this.std(col) || 1
                    btMeans.push(m)
                    btStds.push(s)
                }

                const xTrain = trainSlice.map(r => [1, ...r.x.map((v, i) => (v - btMeans[i]) / btStds[i])])
                const yTrain = trainSlice.map(r => r.y)
                const xTest = testSlice.map(r => [1, ...r.x.map((v, i) => (v - btMeans[i]) / btStds[i])])
                const yTest = testSlice.map(r => r.y)

                const trainBeta = this.calculateOlsCoefficients(xTrain, yTrain)
                if (trainBeta) {
                    const testPredicted = xTest.map(row => this.dot(row, trainBeta))
                    backtest = this.computeMetrics(yTest, testPredicted)
                }
            }

            // 2) Финальная модель на всех данных
            const yValues = preparedRows.map(item => item.y)
            const xValues = preparedRows.map(item => item.x)

            const means = []
            const stds = []
            for (let j = 0; j < featureCount; j++) {
                const column = xValues.map(row => row[j])
                const m = this.mean(column)
                const s = this.std(column) || 1
                means.push(m)
                stds.push(s)
            }

            const design = xValues.map(row => [1, ...row.map((value, i) => (value - means[i]) / stds[i])])
            const beta = this.calculateOlsCoefficients(design, yValues)
            if (!beta) {
                alert('Не удалось обучить OLS-модель.')
                return null
            }

            // 3) Средние значения факторов за последние 24 часа — для будущего
            const last24Rows = rowsWithLag.slice(-24)
            const avgFactors = ['full_plan', 'temperature', 'HPP', 'CHP', 'NPP', 'SES', 'VES', 'other', 'Q_cons', 'Q_exp', 'Q_imp']
            const futureFactorsAvg = {}
            avgFactors.forEach(f => {
                const vals = last24Rows.map(item => this.getFactorValue(item, f)).filter(Number.isFinite)
                futureFactorsAvg[f] = vals.length ? this.mean(vals) : NaN
            })

            const lastDate = new Date(trainRows[trainRows.length - 1].timestamp)
            const futureDates = this.generateFutureTimestamps(this.forecastHorizon, lastDate)

            // 4) Прогноз в будущее
            const forecastPrices = []
            futureDates.forEach(dateStr => {
                const [datePart, timePart] = dateStr.split(' ')
                const [year, month, day] = datePart.split('-').map(Number)
                const hour = Number(timePart.split(':')[0])

                const fakeRow = {
                    timestamp: dateStr,
                    hour: hour,
                    temperature: futureFactorsAvg.temperature,
                    full_plan: futureFactorsAvg.full_plan,
                    plan_GES: futureFactorsAvg.HPP,
                    plan_TES: futureFactorsAvg.CHP,
                    plan_AES: futureFactorsAvg.NPP,
                    plan_SES: futureFactorsAvg.SES,
                    plan_VES: futureFactorsAvg.VES,
                    plan_other: futureFactorsAvg.other,
                    plan_consumption: futureFactorsAvg.Q_cons,
                    plan_export: futureFactorsAvg.Q_exp,
                    plan_import: futureFactorsAvg.Q_imp,
                }

                const prevPrice = forecastPrices.length
                    ? forecastPrices[forecastPrices.length - 1]
                    : trainRows[trainRows.length - 1] ? this.getPrice(trainRows[trainRows.length - 1]) : 0

                const itemForFactor = { row: fakeRow, previousPrice: prevPrice }

                const x = usedFactors.map(factor => {
                    const val = this.getFactorValue(itemForFactor, factor)
                    return Number.isFinite(val) ? val : 0
                })

                const designRow = [1, ...x.map((value, i) => (value - means[i]) / stds[i])]
                forecastPrices.push(this.dot(designRow, beta))
            })

            // 5) Данные для графика: прогноз параллельно с фактом на всём периоде
            const predByTimestamp = new Map()
            preparedRows.forEach(item => {
                const x = usedFactors.map(f => this.getFactorValue(item, f))
                const designRow = [1, ...x.map((value, i) => (value - means[i]) / stds[i])]
                predByTimestamp.set(item.source.timestamp, this.dot(designRow, beta))
            })

            const chartRows = trainRows.map(row => {
                const dateTime = this.getDateTimeLabel(row)
                const actual = this.getPrice(row)
                const predicted = predByTimestamp.has(row.timestamp)
                    ? Number(predByTimestamp.get(row.timestamp).toFixed(2))
                    : null
                return { dateTime, actual, predicted }
            })

            futureDates.forEach((date, idx) => {
                chartRows.push({
                    dateTime: date,
                    actual: null,
                    predicted: Number(forecastPrices[idx].toFixed(2)),
                })
            })

            const quality = this.getQualityFromR2(backtest?.r2)

            return {
                forecast: {
                    trainCount: yValues.length,
                    usedFactors: usedFactors.map(v => this.getFactorLabel(v)),
                    backtest,
                    qualityColor: quality.color,
                    qualityLabel: quality.label,
                    avgPredictedPrice: this.mean(forecastPrices),
                    skippedFactors: expandedFactors.filter(f => !usedFactors.includes(f) && !f.startsWith('month_')).map(v => this.getFactorLabel(v)),
                },
                chartRows,
                hourlyRows: futureDates.map((date, idx) => ({
                    dateTime: date,
                    predictedPrice: this.formatNumber(forecastPrices[idx]),
                })),
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
            if (!xRows.length || !xRows[0].length) return null
            
            const xT = this.transpose(xRows)
            const xTx = this.multiplyMatrices(xT, xRows)
            const xTy = this.multiplyMatrixVector(xT, yValues)
            
            for (let i = 0; i < xTx.length; i++) xTx[i][i] += 1e-6
            
            const inverse = this.invertMatrix(xTx)
            if (!inverse) return null
            
            const beta = this.multiplyMatrixVector(inverse, xTy)
            
            // Проверяем, не появились ли NaN после инверсии матрицы
            if (beta.some(value => !Number.isFinite(value))) return null
            
            return beta
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
            if (factor === 'price_sell') return this.getPrice(row)

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
                HPP:    ['plan_GES', 'HPP', 'hpp', 'hydro', 'ges'],
                CHP:    ['plan_TES', 'CHP', 'chp', 'tes'],
                NPP:    ['plan_AES', 'NPP', 'npp', 'nuclear', 'aes'],
                SES:    ['plan_SES', 'SES', 'ses', 'solar'],
                VES:    ['plan_VES', 'VES', 'ves', 'wind'],
                other:  ['plan_other', 'other', 'other_renewable'],
                Q_cons: ['plan_consumption', 'Q_cons', 'q_cons', 'consumption'],
                Q_exp:  ['plan_export', 'Q_exp', 'q_exp', 'export'],
                Q_imp:  ['plan_import', 'Q_imp', 'q_imp', 'import'],
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
                full_plan: 'Объём',
                previousPrice: 'Цена предыдущего часа',
                hourCycle: 'Циклический час суток',
                hourSin: 'Час суток (sin)',
                hourCos: 'Час суток (cos)',
                dayCycle: 'Циклический день недели',
                daySin: 'День недели (sin)',
                dayCos: 'День недели (cos)',
                monthDummy: 'Месяц',
                month_2: 'Февраль', month_3: 'Март', month_4: 'Апрель', month_5: 'Май',
                month_6: 'Июнь', month_7: 'Июль', month_8: 'Август', month_9: 'Сентябрь',
                month_10: 'Октябрь', month_11: 'Ноябрь', month_12: 'Декабрь',
                temperature: 'Температура',
                HPP: 'Выработка ГЭС',
                CHP: 'Выработка ТЭС',
                NPP: 'Выработка АЭС',
                SES: 'Выработка СЭС',
                VES: 'Выработка ВЭС',
                other: 'Выработка прочих ВИЭ',
                Q_cons: 'Потребление',
                Q_exp: 'Экспорт',
                Q_imp: 'Импорт',
                price_sell: 'Цена продажи',
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
.correlation-scroll {
    overflow-x: auto;
    border: 1px solid rgba(0, 0, 0, 0.1);
    border-radius: 8px;
    background: #ffffff;
}
.correlation-scroll :deep(.v-table) { border: none; }
:deep(.v-field) { border-radius: 8px; }
:deep(.v-selection-control__input) { transform: scale(0.95); }

.correlation-scroll :deep(th),
.correlation-scroll :deep(td) {
    text-align: center;
}
.correlation-scroll :deep(th:first-child),
.correlation-scroll :deep(td:first-child) {
    text-align: left;
}

/* Цвет чекбоксов для 4 ключевых факторов — как у кнопки «Показать статистику» */
.core-factor-checkbox :deep(.v-selection-control__input) > .v-icon {
    color: rgb(66, 165, 245) !important; /* blue-lighten-1 */
}
</style>
