<template>
  <v-container fluid class="price-page pa-4">
    <v-card
      class="section-card pa-5 mb-4"
      elevation="2"
      rounded="xl"
    >
      <div class="page-title" align="left">
        Моделирование цены электроэнергии
      </div>

      <div class="page-subtitle" align="left">
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
            <v-card
              class="factors-card pa-4"
              elevation="0"
              rounded="xl"
              variant="outlined"
            >
              <div class="d-flex align-center justify-space-between mb-2">
                <div class="section-title small-title">Факторы модели</div>
                <v-chip color="blue-grey-lighten-4" variant="flat" class="soft-chip">Рекомендуемый набор выбран</v-chip>
              </div>

              <div class="section-subtitle mb-4" align="left">
                Для временных признаков используется циклическое кодирование. Месяц учитывается как дамми-переменная.
                Температура подтягивается из внешнего погодного источника по региону и часу.
              </div>

              <v-row>
                <v-col v-for="factor in factors" :key="factor.value" cols="12" md="6">
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
            <v-btn
              block
              class="action-btn"
              min-height="52"
              color="blue-grey-lighten-1"
              :loading="priceAnalyticsLoading || weatherLoading"
              :disabled="isDateInvalid"
              @click="loadData"
            >
              Загрузить данные
            </v-btn>
          </v-col>

          <v-col cols="12" md="4">
            <v-btn
              block
              class="action-btn"
              min-height="52"
              color="blue-lighten-1"
              :loading="priceAnalyticsLoading || weatherLoading"
              :disabled="isDateInvalid"
              @click="showStatistics"
            >
              Показать статистику
            </v-btn>
          </v-col>

          <v-col cols="12" md="4">
            <v-btn
              block
              class="action-btn"
              min-height="52"
              color="green-lighten-1"
              :loading="priceAnalyticsLoading || weatherLoading"
              :disabled="isDateInvalid"
              @click="buildForecast"
            >
              Построить прогноз
            </v-btn>
          </v-col>
        </v-row>

        <div v-if="isDateInvalid" class="text-error mt-3">
          Введён некорректный диапазон дат.
        </div>

        <div v-if="hasPendingChanges" class="text-error mt-3">
          Вы изменили параметры, но ещё не загрузили данные.
        </div>
      </v-container>
    </v-card>

    <v-alert v-if="priceAnalyticsError" type="error" variant="tonal" class="status-alert mb-4">
      Ошибка загрузки данных проекта. Проверьте авторизацию и доступность сервера.
    </v-alert>

    <v-alert v-if="weatherError" type="warning" variant="tonal" class="status-alert mb-4">
      {{ weatherError }}
    </v-alert>

    <v-alert v-if="loadedOnce && temperatureCoverage.total > 0" type="info" variant="tonal" class="status-alert mb-4">
      Температура загружена для {{ temperatureCoverage.loaded }} из {{ temperatureCoverage.total }} наблюдений.
    </v-alert>

    <v-alert v-if="loadedOnce && !filteredRows.length" type="info" variant="tonal" class="status-alert mb-4">
      Нет данных по выбранному региону и периоду.
    </v-alert>

    <v-alert
      v-if="loadedOnce && filteredRows.length > 0 && filteredRows.length < 168"
      type="warning"
      variant="tonal"
      class="status-alert mb-4"
    >
      Для более устойчивого прогноза рекомендуется выбирать период не менее 7 дней.
    </v-alert>

    <v-card
      v-if="statistics"
      class="section-card pa-5 mb-4"
      elevation="2"
      rounded="xl"
    >
      <div class="section-title" align="left">Описательная статистика</div>
      <div class="section-subtitle" align="left">
        Расчёт выполнен по фактическим данным для выбранного региона.
      </div>

      <v-table class="mt-4 data-table-clean">
        <tbody>
          <tr><td>Регион</td><td>{{ selectedRegion }}</td></tr>
          <tr><td>Количество наблюдений</td><td>{{ statistics.count }}</td></tr>
          <tr><td>Средняя цена продажи</td><td>{{ formatNumber(statistics.avgPrice) }} руб./МВт·ч</td></tr>
          <tr><td>Минимальная цена продажи</td><td>{{ formatNumber(statistics.minPrice) }} руб./МВт·ч</td></tr>
          <tr><td>Максимальная цена продажи</td><td>{{ formatNumber(statistics.maxPrice) }} руб./МВт·ч</td></tr>
          <tr><td>Стандартное отклонение цены</td><td>{{ formatNumber(statistics.stdPrice) }} руб./МВт·ч</td></tr>
          <tr><td>Средний объём</td><td>{{ formatNumber(statistics.avgVolume) }} МВт·ч</td></tr>
          <tr><td>Суммарный объём</td><td>{{ formatNumber(statistics.totalVolume) }} МВт·ч</td></tr>
          <tr><td>Средняя температура</td><td>{{ formatNumber(statistics.avgTemperature) }} °C</td></tr>
        </tbody>
      </v-table>
    </v-card>

    <v-card
      v-if="correlationMatrix"
      class="section-card pa-5 mb-4"
      elevation="2"
      rounded="xl"
    >
      <div class="section-title" align="left">Корреляционный анализ</div>
      <div class="section-subtitle" align="left">
        Матрица корреляций показывает силу линейной связи между ценой и выбранными объясняющими переменными, а также между самими объясняющими переменными.
      </div>

      <div class="correlation-scroll mt-4">
        <v-table class="correlation-table">
          <thead>
            <tr>
              <th>Переменная</th>
              <th v-for="header in correlationMatrix.headers" :key="header">{{ header }}</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="row in correlationMatrix.rows" :key="row.label">
              <td class="font-weight-bold">{{ row.label }}</td>
              <td
                v-for="cell in row.values"
                :key="cell.key"
                :style="getCorrelationCellStyle(cell.value)"
              >
                {{ formatCorrelation(cell.value) }}
              </td>
            </tr>
          </tbody>
        </v-table>
      </div>
    </v-card>

    <v-card
      v-if="correlationMatrix"
      class="section-card pa-5 mb-4"
      elevation="2"
      rounded="xl"
    >
      <div class="section-title" align="left">График корреляций с ценой</div>
      <div class="section-subtitle" align="left">
        Линейный график показывает коэффициенты корреляции выбранных объясняющих переменных с целевой переменной.
      </div>

      <VChart
        :option="correlationChartOption"
        class="mt-4 chart-frame"
        style="height: 420px;"
      />
    </v-card>

    <v-card
      v-if="forecast"
      class="section-card pa-5 mb-4"
      elevation="2"
      rounded="xl"
    >
      <div class="d-flex align-center justify-space-between">
        <div>
          <div class="section-title" align="left">Результат моделирования</div>
          <div class="section-subtitle" align="left">
            Модель строится как множественная линейная регрессия. Обучение выполняется на 80% наблюдений,
            проверка качества - на оставшихся 20%.
          </div>
        </div>

        <v-chip :color="forecast.qualityColor" variant="flat" class="font-weight-bold quality-chip">
          {{ forecast.qualityLabel }}
        </v-chip>
      </div>

      <v-table class="mt-4 data-table-clean">
        <tbody>
          <tr><td>Метод</td><td>МНК / OLS, множественная линейная регрессия</td></tr>
          <tr><td>Регион</td><td>{{ selectedRegion }}</td></tr>
          <tr><td>Целевая переменная</td><td>{{ targetVariable }}</td></tr>
          <tr><td>Использованные факторы</td><td>{{ forecast.usedFactors.join(', ') }}</td></tr>
          <tr><td>Объём обучающей выборки</td><td>{{ forecast.trainCount }}</td></tr>
          <tr><td>Объём тестовой выборки</td><td>{{ forecast.testCount }}</td></tr>
          <tr><td>R² на тестовой выборке</td><td>{{ formatNumber(forecast.r2, 4) }}</td></tr>
          <tr><td>MAE</td><td>{{ formatNumber(forecast.mae) }} руб./МВт·ч</td></tr>
          <tr><td>RMSE</td><td>{{ formatNumber(forecast.rmse) }} руб./МВт·ч</td></tr>
          <tr><td>Средняя прогнозируемая цена на тестовом периоде</td><td>{{ formatNumber(forecast.avgPredictedPrice) }} руб./МВт·ч</td></tr>
        </tbody>
      </v-table>

      <v-alert v-if="forecast.r2 < 0" type="warning" variant="tonal" class="mt-4">
        Значение R² ниже нуля означает, что на выбранном периоде модель уступает базовому прогнозу по среднему значению.
        Для повышения качества прогноза рекомендуется выбрать больший период или расширить набор факторов.
      </v-alert>

      <v-alert v-if="forecast.skippedFactors.length" type="warning" variant="tonal" class="mt-4">
        Следующие выбранные факторы отсутствуют в текущих данных и не были использованы:
        {{ forecast.skippedFactors.join(', ') }}.
      </v-alert>
    </v-card>

    <v-card
      v-if="forecastChartRows.length"
      class="section-card pa-5 mb-4"
      elevation="2"
      rounded="xl"
    >
      <div class="section-title" align="left">График фактической и прогнозной цены</div>
      <div class="section-subtitle" align="left">
        Сравнение фактической и прогнозной цены по часам тестового периода.
      </div>

      <VChart
        :option="forecastChartOption"
        class="mt-4 chart-frame"
        style="height: 420px;"
      />
    </v-card>

    <v-card
      v-if="hourlyForecastRows.length"
      class="section-card pa-5 mb-4"
      elevation="2"
      rounded="xl"
    >
      <div class="section-title" align="left">Почасовой прогноз</div>
      <div class="section-subtitle" align="left">
        Прогноз построен для каждого часа тестового периода. В таблице показаны фактическая и прогнозная цены.
      </div>

      <v-data-table
        class="mt-4 data-table-clean"
        :headers="hourlyForecastHeaders"
        :items="hourlyForecastRows"
        density="comfortable"
        items-per-page="24"
      />
    </v-card>
  </v-container>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'

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
      targetVariable: 'Price / price_sell - цена продажи электроэнергии',
      targetVariables: ['Price / price_sell - цена продажи электроэнергии'],
      factors: [
        { label: 'Объём / full_plan', value: 'full_plan' },
        { label: 'Цена предыдущего часа', value: 'previousPrice' },
        { label: 'Циклический час суток', value: 'hourCycle' },
        { label: 'Циклический день недели', value: 'dayCycle' },
        { label: 'Месяц / дамми-переменные', value: 'monthDummy' },
        { label: 'Температура / temperature', value: 'temperature' },
        { label: 'Выработка ГЭС / HPP', value: 'HPP' },
        { label: 'Выработка ТЭС / CHP или NPP', value: 'CHP' },
        { label: 'Потребление / Q_cons', value: 'Q_cons' },
        { label: 'Экспорт / Q_exp', value: 'Q_exp' },
        { label: 'Импорт / Q_imp', value: 'Q_imp' },
      ],
      selectedFactors: ['full_plan', 'previousPrice', 'hourCycle', 'dayCycle', 'monthDummy', 'temperature'],
      hourlyForecastHeaders: [
        { title: 'Дата и час', key: 'dateTime', align: 'center' },
        { title: 'Фактическая цена, руб./МВт·ч', key: 'actualPrice', align: 'center' },
        { title: 'Прогнозная цена, руб./МВт·ч', key: 'predictedPrice', align: 'center' },
        { title: 'Ошибка, руб./МВт·ч', key: 'error', align: 'center' },
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

    correlationChartRows() {
      if (!this.correlationMatrix) return []

      const priceRow = this.correlationMatrix.rows.find(row => row.label === 'Цена')
      if (!priceRow) return []

      return priceRow.values
        .map((cell, index) => ({
          label: this.correlationMatrix.headers[index],
          value: cell.value,
        }))
        .filter(item => item.label !== 'Цена' && Number.isFinite(item.value))
    },

    correlationChartOption() {
      const rows = this.correlationChartRows
      const values = rows.map(row => Number(row.value.toFixed(2)))

      return {
        tooltip: {
          trigger: 'axis',
          backgroundColor: 'rgba(255, 255, 255, 0.96)',
          borderColor: 'rgba(0, 0, 0, 0.16)',
          borderWidth: 1,
          textStyle: {
            color: '#263238',
          },
          formatter: params => {
            const item = params[0]
            const value = Number(item.value).toFixed(2)
            return `${item.marker} ${item.name}<br/>r = <b>${value}</b>`
          },
        },
        legend: {
          top: 0,
          data: ['Корреляция с ценой'],
        },
        grid: {
          left: 60,
          right: 25,
          top: 60,
          bottom: 80,
        },
        xAxis: {
          type: 'category',
          boundaryGap: false,
          data: rows.map(row => row.label),
          axisTick: {
            alignWithLabel: true,
          },
          axisLabel: {
            interval: 0,
            rotate: 25,
          },
        },
        yAxis: {
          type: 'value',
          name: 'r',
          min: -1,
          max: 1,
          interval: 0.25,
          splitLine: {
            lineStyle: {
              color: 'rgba(0, 0, 0, 0.08)',
            },
          },
        },
        series: [
          {
            name: 'Корреляция с ценой',
            type: 'line',
            smooth: true,
            showSymbol: true,
            symbol: 'circle',
            symbolSize: 9,
            data: values,
            lineStyle: {
              width: 3,
              color: '#5470C6',
            },
            itemStyle: {
              color: '#ffffff',
              borderColor: '#5470C6',
              borderWidth: 2,
            },
            areaStyle: {
              color: 'rgba(84, 112, 198, 0.12)',
            },
            label: {
              show: true,
              position: 'top',
              color: '#455A64',
              fontWeight: 600,
              formatter: params => Number(params.value).toFixed(2),
            },
            markLine: {
              symbol: 'none',
              silent: true,
              lineStyle: {
                color: 'rgba(0, 0, 0, 0.45)',
                type: 'dashed',
                width: 1,
              },
              label: {
                show: true,
                formatter: 'нулевая связь',
                color: '#757575',
              },
              data: [{ yAxis: 0 }],
            },
          },
        ],
      }
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
          { name: 'Фактическая цена', type: 'line', smooth: true, data: this.forecastChartRows.map(row => row.actual) },
          { name: 'Прогнозная цена', type: 'line', smooth: true, data: this.forecastChartRows.map(row => row.predicted) },
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

      const prices = rows.map(row => this.getPrice(row)).filter(value => Number.isFinite(value))
      const volumes = rows.map(row => this.getVolume(row)).filter(value => Number.isFinite(value))
      const temperatures = rows.map(row => this.toNumber(row.temperature)).filter(value => Number.isFinite(value))

      this.statistics = {
        count: prices.length,
        avgPrice: this.mean(prices),
        minPrice: Math.min(...prices),
        maxPrice: Math.max(...prices),
        stdPrice: this.std(prices),
        avgVolume: this.mean(volumes),
        totalVolume: this.sum(volumes),
        avgTemperature: temperatures.length ? this.mean(temperatures) : NaN,
      }

      this.buildCorrelationAnalysis(rows)
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

      if (rows.length < 24) {
        alert('Недостаточно данных для построения модели. Выберите больший период.')
        return
      }

      this.buildCorrelationAnalysis(rows)
      const dataset = this.prepareDataset(rows)

      if (dataset.rows.length < 24 || !dataset.usedFactors.length) {
        alert('Недостаточно подходящих факторов для построения модели.')
        return
      }

      const result = this.fitLinearRegression(dataset.rows, dataset.usedFactors)
      if (!result) {
        alert('Не удалось построить модель. Попробуйте выбрать меньше факторов.')
        return
      }

      const quality = this.getQualityInfo(result.r2)
      this.forecast = {
        avgPredictedPrice: result.avgPredictedPrice,
        lastPredictedPrice: result.lastPredictedPrice,
        r2: result.r2,
        mae: result.mae,
        rmse: result.rmse,
        trainCount: result.trainCount,
        testCount: result.testCount,
        qualityLabel: quality.label,
        qualityColor: quality.color,
        usedFactors: dataset.usedFactors.map(value => this.getFactorLabel(value)),
        skippedFactors: dataset.skippedFactors.map(value => this.getFactorLabel(value)),
      }

      this.hourlyForecastRows = result.testPredictionRows.map(item => ({
        dateTime: this.getDateTimeLabel(item.source),
        actualPrice: this.formatNumber(item.actual),
        predictedPrice: this.formatNumber(item.predicted),
        error: this.formatNumber(item.error),
      }))

      this.forecastChartRows = result.testPredictionRows.map(item => ({
        dateTime: this.getDateTimeLabel(item.source),
        actual: Number(item.actual.toFixed(2)),
        predicted: Number(item.predicted.toFixed(2)),
      }))
    },

    prepareDataset(rows) {
      const rowsWithLag = rows.map((row, index) => {
        const previousRow = index > 0 ? rows[index - 1] : null
        const previousPrice = previousRow ? this.getPrice(previousRow) : NaN
        return { row, previousPrice }
      })

      const selected = [...this.selectedFactors]
      const expandedFactors = []

      for (const factor of selected) {
        if (factor === 'hourCycle') {
          expandedFactors.push('hourSin', 'hourCos')
        } else if (factor === 'dayCycle') {
          expandedFactors.push('daySin', 'dayCos')
        } else if (factor === 'monthDummy') {
          for (let month = 2; month <= 12; month++) expandedFactors.push(`month_${month}`)
        } else {
          expandedFactors.push(factor)
        }
      }

      const usedFactors = expandedFactors.filter(factor => {
        const values = rowsWithLag.map(item => this.getFactorValue(item, factor)).filter(value => Number.isFinite(value))
        const uniqueValues = new Set(values)
        return values.length >= Math.min(24, rows.length - 1) && uniqueValues.size > 1
      })

      const skippedFactors = expandedFactors.filter(factor => !usedFactors.includes(factor) && !factor.startsWith('month_'))

      const preparedRows = rowsWithLag
        .map(item => {
          const y = this.getPrice(item.row)
          const x = usedFactors.map(factor => this.getFactorValue(item, factor))
          return { y, x, source: item.row }
        })
        .filter(item => Number.isFinite(item.y) && item.x.every(value => Number.isFinite(value)))

      return { rows: preparedRows, usedFactors, skippedFactors }
    },

    fitLinearRegression(datasetRows, usedFactors) {
      const yValues = datasetRows.map(item => item.y)
      const xValues = datasetRows.map(item => item.x)
      const featureCount = usedFactors.length
      const rowCount = datasetRows.length
      if (rowCount <= featureCount + 5) return null

      const means = []
      const stds = []

      for (let j = 0; j < featureCount; j++) {
        const column = xValues.map(row => row[j])
        const mean = this.mean(column)
        const std = this.std(column) || 1
        means.push(mean)
        stds.push(std)
      }

      const design = xValues.map(row => [1, ...row.map((value, index) => (value - means[index]) / stds[index])])
      const splitIndex = Math.max(Math.floor(rowCount * 0.8), featureCount + 5)
      if (splitIndex >= rowCount) return null

      const xTrain = design.slice(0, splitIndex)
      const yTrain = yValues.slice(0, splitIndex)
      const xTest = design.slice(splitIndex)
      const yTest = yValues.slice(splitIndex)
      const beta = this.calculateOlsCoefficients(xTrain, yTrain)
      if (!beta) return null

      const testPredictions = xTest.map(row => this.dot(row, beta))
      const errors = testPredictions.map((prediction, index) => prediction - yTest[index])
      const mae = this.mean(errors.map(error => Math.abs(error)))
      const rmse = Math.sqrt(this.mean(errors.map(error => error * error)))
      const yTestMean = this.mean(yTest)
      const ssRes = errors.reduce((sum, error) => sum + error * error, 0)
      const ssTot = yTest.reduce((sum, value) => sum + Math.pow(value - yTestMean, 2), 0)
      const r2 = ssTot ? 1 - ssRes / ssTot : 0

      const testPredictionRows = testPredictions.map((prediction, index) => {
        const datasetIndex = splitIndex + index
        const actual = yTest[index]
        return {
          source: datasetRows[datasetIndex].source,
          actual,
          predicted: prediction,
          error: prediction - actual,
        }
      })

      return {
        avgPredictedPrice: this.mean(testPredictions),
        lastPredictedPrice: testPredictions[testPredictions.length - 1],
        r2,
        mae,
        rmse,
        trainCount: yTrain.length,
        testCount: yTest.length,
        testPredictionRows,
      }
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

    getPrice(row) {
      return this.toNumber(row.price_sell ?? row.Price ?? row.price ?? row.priceSell)
    },

    getVolume(row) {
      return this.toNumber(row.full_plan ?? row.volume ?? row.Q_cons ?? row.q_cons)
    },

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

      if (factor === 'hourSin') {
        const hour = this.getHour(row)
        return Number.isFinite(hour) ? Math.sin((2 * Math.PI * hour) / 24) : NaN
      }

      if (factor === 'hourCos') {
        const hour = this.getHour(row)
        return Number.isFinite(hour) ? Math.cos((2 * Math.PI * hour) / 24) : NaN
      }

      if (factor === 'daySin') {
        const day = this.getDayOfWeek(row)
        return Number.isFinite(day) ? Math.sin((2 * Math.PI * day) / 7) : NaN
      }

      if (factor === 'dayCos') {
        const day = this.getDayOfWeek(row)
        return Number.isFinite(day) ? Math.cos((2 * Math.PI * day) / 7) : NaN
      }

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
        full_plan: 'Объём / full_plan',
        previousPrice: 'Цена предыдущего часа',
        hourCycle: 'Циклический час суток',
        hourSin: 'Час суток sin',
        hourCos: 'Час суток cos',
        dayCycle: 'Циклический день недели',
        daySin: 'День недели sin',
        dayCos: 'День недели cos',
        monthDummy: 'Месяц / дамми-переменные',
        month_2: 'Февраль',
        month_3: 'Март',
        month_4: 'Апрель',
        month_5: 'Май',
        month_6: 'Июнь',
        month_7: 'Июль',
        month_8: 'Август',
        month_9: 'Сентябрь',
        month_10: 'Октябрь',
        month_11: 'Ноябрь',
        month_12: 'Декабрь',
        temperature: 'Температура / temperature',
        HPP: 'Выработка ГЭС / HPP',
        CHP: 'Выработка ТЭС / CHP или NPP',
        Q_cons: 'Потребление / Q_cons',
        Q_exp: 'Экспорт / Q_exp',
        Q_imp: 'Импорт / Q_imp',
      }
      return labels[value] || value
    },

    getQualityInfo(r2) {
      if (r2 >= 0.7) return { label: 'Высокое качество', color: 'green-lighten-1' }
      if (r2 >= 0.3) return { label: 'Среднее качество', color: 'blue-lighten-1' }
      if (r2 >= 0) return { label: 'Низкое качество', color: 'orange-lighten-1' }
      return { label: 'Нестабильная модель', color: 'red-lighten-2' }
    },

    toNumber(value) {
      if (value === null || value === undefined || value === '') return NaN
      if (typeof value === 'number') return Number.isFinite(value) ? value : NaN
      const normalized = String(value).replace(/\s/g, '').replace(',', '.')
      const number = Number(normalized)
      return Number.isFinite(number) ? number : NaN
    },

    sum(values) {
      return values.reduce((acc, value) => acc + value, 0)
    },

    mean(values) {
      if (!values.length) return 0
      return this.sum(values) / values.length
    },

    std(values) {
      if (values.length < 2) return 0
      const avg = this.mean(values)
      const variance = this.mean(values.map(value => Math.pow(value - avg, 2)))
      return Math.sqrt(variance)
    },

    dot(a, b) {
      return a.reduce((sum, value, index) => sum + value * b[index], 0)
    },

    transpose(matrix) {
      return matrix[0].map((_, colIndex) => matrix.map(row => row[colIndex]))
    },

    multiplyMatrices(a, b) {
      return a.map(row => {
        return b[0].map((_, colIndex) => {
          return row.reduce((sum, value, rowIndex) => sum + value * b[rowIndex][colIndex], 0)
        })
      })
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
      return Number(value).toLocaleString('ru-RU', {
        minimumFractionDigits: digits,
        maximumFractionDigits: digits,
      })
    },
  },
}
</script>

<style scoped>
.price-page {
  background: linear-gradient(180deg, #f7f9fb 0%, #ffffff 40%);
}

.section-card {
  border: 1px solid rgba(23, 43, 77, 0.14);
  box-shadow: 0 3px 14px rgba(23, 43, 77, 0.08) !important;
  overflow: hidden;
}

.page-title {
  font-size: 26px;
  line-height: 1.25;
  font-weight: 800;
  color: #263238;
  letter-spacing: 0.2px;
}

.page-subtitle,
.section-subtitle {
  color: #6b7280;
  font-size: 14px;
  line-height: 1.55;
}

.section-title {
  font-size: 22px;
  line-height: 1.25;
  font-weight: 800;
  color: #263238;
  letter-spacing: 0.15px;
}

.small-title {
  font-size: 18px;
}

.factors-card {
  background: #fbfcfd;
  border-color: rgba(23, 43, 77, 0.14) !important;
}

.soft-chip,
.quality-chip {
  border-radius: 999px;
  letter-spacing: 0.2px;
}

.action-btn {
  border-radius: 8px;
  font-weight: 800;
  letter-spacing: 1px;
  box-shadow: 0 3px 10px rgba(23, 43, 77, 0.14);
}

.status-alert {
  border-radius: 12px;
  border: 1px solid rgba(23, 43, 77, 0.08);
}

.chart-frame {
  border: 1px solid rgba(23, 43, 77, 0.14);
  border-radius: 14px;
  padding: 10px;
  background: #ffffff;
}

.correlation-scroll {
  overflow-x: auto;
  border: 1px solid rgba(23, 43, 77, 0.10);
  border-radius: 14px;
  background: #ffffff;
}

.correlation-table th,
.correlation-table td {
  text-align: center;
  padding: 12px 14px;
  white-space: nowrap;
}

.correlation-table td:first-child {
  text-align: left;
  font-weight: 700;
  color: #263238;
}

.data-table-clean {
  border: 1px solid rgba(23, 43, 77, 0.10);
  border-radius: 14px;
  overflow: hidden;
}

.data-table-clean td:first-child {
  font-weight: 700;
  color: #263238;
  width: 45%;
}

.data-table-clean td {
  padding: 12px 18px;
}

:deep(.v-field) {
  border-radius: 8px;
}

:deep(.v-selection-control__input) {
  transform: scale(0.95);
}

:deep(.v-data-table-footer) {
  border-top: 1px solid rgba(23, 43, 77, 0.10);
}
</style>
