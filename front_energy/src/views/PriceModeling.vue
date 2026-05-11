<template>
  <v-container fluid class="pa-4">
    <v-card
      class="pa-4 mb-4"
      elevation="1"
      rounded="lg"
      variant="outlined"
      style="border-color: rgba(0, 0, 0, 0.2)"
    >
      <div class="text-h5 font-weight-bold" align="left">
        Моделирование цены электроэнергии
      </div>

      <div class="text-body-2 text-grey-darken-1 mt-1" align="left">
        Построение прогноза цены продажи электроэнергии на основе выбранного региона,
        доступных факторов и метода наименьших квадратов / OLS.
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

          <v-col cols="12" md="3">
            <v-select
              v-model="selectedRegion"
              :items="regionItems"
              label="Регион"
              hide-details
            />
          </v-col>

          <v-col cols="12" md="3">
            <v-select
              v-model="targetVariable"
              :items="targetVariables"
              label="Целевая переменная"
              hide-details
            />
          </v-col>
        </v-row>

        <v-row class="mt-4">
          <v-col cols="12">
            <v-card
              class="pa-4"
              elevation="0"
              variant="outlined"
              style="border-color: rgba(0, 0, 0, 0.15)"
            >
              <div class="d-flex align-center justify-space-between mb-2">
                <div class="text-h6 font-weight-bold">
                  Факторы модели
                </div>

                <v-chip color="blue-grey-lighten-4" variant="flat">
                  Рекомендуемый набор выбран
                </v-chip>
              </div>

              <div class="text-body-2 text-grey-darken-1 mb-4" align="left">
                Для временных признаков используется циклическое кодирование, чтобы корректно учитывать повторяемость часов суток и дней недели.
              </div>

              <v-row>
                <v-col
                  v-for="factor in factors"
                  :key="factor.value"
                  cols="12"
                  md="6"
                >
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
              min-height="50"
              color="blue-grey-lighten-1"
              :loading="priceAnalyticsLoading"
              :disabled="isDateInvalid"
              @click="loadData"
            >
              Загрузить данные
            </v-btn>
          </v-col>

          <v-col cols="12" md="4">
            <v-btn
              block
              min-height="50"
              color="blue-lighten-1"
              :loading="priceAnalyticsLoading"
              :disabled="isDateInvalid"
              @click="showStatistics"
            >
              Показать статистику
            </v-btn>
          </v-col>

          <v-col cols="12" md="4">
            <v-btn
              block
              min-height="50"
              color="green-lighten-1"
              :loading="priceAnalyticsLoading"
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

    <v-alert
      v-if="priceAnalyticsError"
      type="error"
      variant="tonal"
      class="mb-4"
    >
      Ошибка загрузки данных. Проверьте авторизацию и доступность сервера.
    </v-alert>

    <v-alert
      v-if="loadedOnce && !filteredRows.length"
      type="info"
      variant="tonal"
      class="mb-4"
    >
      Нет данных по выбранному региону и периоду.
    </v-alert>

    <v-alert
      v-if="loadedOnce && filteredRows.length > 0 && filteredRows.length < 168"
      type="warning"
      variant="tonal"
      class="mb-4"
    >
      Для более устойчивого прогноза рекомендуется выбирать период не менее 7 дней.
    </v-alert>

    <v-card
      v-if="statistics"
      class="pa-4 mb-4"
      elevation="1"
      rounded="lg"
      variant="outlined"
      style="border-color: rgba(0, 0, 0, 0.2)"
    >
      <div class="text-h5 font-weight-bold" align="left">
        Описательная статистика
      </div>

      <div class="text-body-2 text-grey-darken-1 mt-1" align="left">
        Расчёт выполнен по фактическим данным для выбранного региона.
      </div>

      <v-table class="mt-4">
        <tbody>
          <tr>
            <td>Регион</td>
            <td>{{ selectedRegion }}</td>
          </tr>
          <tr>
            <td>Количество наблюдений</td>
            <td>{{ statistics.count }}</td>
          </tr>
          <tr>
            <td>Средняя цена продажи</td>
            <td>{{ formatNumber(statistics.avgPrice) }} руб./МВт·ч</td>
          </tr>
          <tr>
            <td>Минимальная цена продажи</td>
            <td>{{ formatNumber(statistics.minPrice) }} руб./МВт·ч</td>
          </tr>
          <tr>
            <td>Максимальная цена продажи</td>
            <td>{{ formatNumber(statistics.maxPrice) }} руб./МВт·ч</td>
          </tr>
          <tr>
            <td>Стандартное отклонение цены</td>
            <td>{{ formatNumber(statistics.stdPrice) }} руб./МВт·ч</td>
          </tr>
          <tr>
            <td>Средний объём</td>
            <td>{{ formatNumber(statistics.avgVolume) }} МВт·ч</td>
          </tr>
          <tr>
            <td>Суммарный объём</td>
            <td>{{ formatNumber(statistics.totalVolume) }} МВт·ч</td>
          </tr>
        </tbody>
      </v-table>
    </v-card>

    <v-card
      v-if="forecast"
      class="pa-4 mb-4"
      elevation="1"
      rounded="lg"
      variant="outlined"
      style="border-color: rgba(0, 0, 0, 0.2)"
    >
      <div class="d-flex align-center justify-space-between">
        <div>
          <div class="text-h5 font-weight-bold" align="left">
            Результат моделирования
          </div>

          <div class="text-body-2 text-grey-darken-1 mt-1" align="left">
            Модель строится как множественная линейная регрессия. Обучение выполняется на 80% наблюдений,
            проверка качества — на оставшихся 20%.
          </div>
        </div>

        <v-chip
          :color="forecast.qualityColor"
          variant="flat"
          class="font-weight-bold"
        >
          {{ forecast.qualityLabel }}
        </v-chip>
      </div>

      <v-table class="mt-4">
        <tbody>
          <tr>
            <td>Метод</td>
            <td>МНК / OLS, множественная линейная регрессия</td>
          </tr>
          <tr>
            <td>Регион</td>
            <td>{{ selectedRegion }}</td>
          </tr>
          <tr>
            <td>Целевая переменная</td>
            <td>{{ targetVariable }}</td>
          </tr>
          <tr>
            <td>Использованные факторы</td>
            <td>{{ forecast.usedFactors.join(', ') }}</td>
          </tr>
          <tr>
            <td>Объём обучающей выборки</td>
            <td>{{ forecast.trainCount }}</td>
          </tr>
          <tr>
            <td>Объём тестовой выборки</td>
            <td>{{ forecast.testCount }}</td>
          </tr>
          <tr>
            <td>R² на тестовой выборке</td>
            <td>{{ formatNumber(forecast.r2, 4) }}</td>
          </tr>
          <tr>
            <td>MAE</td>
            <td>{{ formatNumber(forecast.mae) }} руб./МВт·ч</td>
          </tr>
          <tr>
            <td>RMSE</td>
            <td>{{ formatNumber(forecast.rmse) }} руб./МВт·ч</td>
          </tr>
        </tbody>
      </v-table>

      <v-alert
        v-if="forecast.r2 < 0"
        type="warning"
        variant="tonal"
        class="mt-4"
      >
        Значение R² ниже нуля означает, что на выбранном периоде модель уступает базовому прогнозу по среднему значению.
        Для повышения качества прогноза рекомендуется выбрать больший период или расширить набор факторов.
      </v-alert>

      <v-alert
        v-if="forecast.skippedFactors.length"
        type="warning"
        variant="tonal"
        class="mt-4"
      >
        Следующие выбранные факторы отсутствуют в текущих данных и не были использованы:
        {{ forecast.skippedFactors.join(', ') }}.
      </v-alert>

      <div class="forecast-result mt-6">
        Прогнозируемая цена: {{ formatNumber(forecast.price) }} руб./МВт·ч
      </div>

      <div class="text-body-2 text-grey-darken-1 mt-2 text-center">
        Прогноз рассчитан для последнего наблюдения выбранного периода.
      </div>
    </v-card>
  </v-container>
</template>

<script>
import { mapState, mapGetters, mapActions } from 'vuex'

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

      selectedRegion: 'Иркутская область',
      targetVariable: 'Price / price_sell — цена продажи электроэнергии',

      targetVariables: [
        'Price / price_sell — цена продажи электроэнергии',
      ],

      factors: [
        { label: 'Объём / full_plan', value: 'full_plan' },
        { label: 'Цена предыдущего часа', value: 'previousPrice' },
        { label: 'Циклический час суток', value: 'hourCycle' },
        { label: 'Циклический день недели', value: 'dayCycle' },
        { label: 'Выработка ГЭС / HPP', value: 'HPP' },
        { label: 'Выработка ТЭС / CHP или NPP', value: 'CHP' },
        { label: 'Потребление / Q_cons', value: 'Q_cons' },
        { label: 'Экспорт / Q_exp', value: 'Q_exp' },
        { label: 'Импорт / Q_imp', value: 'Q_imp' },
        { label: 'Температура / temperature', value: 'temperature' },
      ],

      selectedFactors: [
        'full_plan',
        'previousPrice',
        'hourCycle',
        'dayCycle',
      ],

      statistics: null,
      forecast: null,
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

    regionItems() {
      if (!Array.isArray(this.storeRegions) || !this.storeRegions.length) {
        return ['Иркутская область']
      }

      return this.storeRegions.map(item => item.value)
    },

    isDateInvalid() {
      return !this.dateFrom || !this.dateTo || this.dateFrom > this.dateTo
    },

    hasPendingChanges() {
      if (!this.loadedOnce) return false

      return (
        this.dateFrom !== this.appliedDateFrom ||
        this.dateTo !== this.appliedDateTo
      )
    },

    filteredRows() {
      return this.priceAnalyticsRows
        .filter(row => {
          const region = row.region || ''
          return region === this.selectedRegion
        })
        .filter(row => Number.isFinite(this.getPrice(row)))
        .sort((a, b) => {
          const timeCompare = String(a.timestamp || '').localeCompare(String(b.timestamp || ''))

          if (timeCompare !== 0) {
            return timeCompare
          }

          return this.getHour(a) - this.getHour(b)
        })
    },
  },

  methods: {
    ...mapActions(['fetchPriceAnalyticsRows']),

    getInitialRange() {
      const today = new Date()
      const from = new Date()

      from.setDate(today.getDate() - 14)

      return {
        from: this.toDateString(from),
        to: this.toDateString(today),
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

      await this.fetchPriceAnalyticsRows({
        from: this.dateFrom,
        to: this.dateTo,
      })

      this.appliedDateFrom = this.dateFrom
      this.appliedDateTo = this.dateTo
      this.loadedOnce = true
      this.statistics = null
      this.forecast = null
    },

    async ensureDataLoaded() {
      if (
        !this.loadedOnce ||
        this.dateFrom !== this.appliedDateFrom ||
        this.dateTo !== this.appliedDateTo
      ) {
        await this.loadData()
      }
    },

    async showStatistics() {
      await this.ensureDataLoaded()

      const rows = this.filteredRows

      if (!rows.length) {
        this.statistics = null
        return
      }

      const prices = rows
        .map(row => this.getPrice(row))
        .filter(value => Number.isFinite(value))

      const volumes = rows
        .map(row => this.getVolume(row))
        .filter(value => Number.isFinite(value))

      this.statistics = {
        count: prices.length,
        avgPrice: this.mean(prices),
        minPrice: Math.min(...prices),
        maxPrice: Math.max(...prices),
        stdPrice: this.std(prices),
        avgVolume: this.mean(volumes),
        totalVolume: this.sum(volumes),
      }
    },

    async buildForecast() {
      await this.ensureDataLoaded()

      const rows = this.filteredRows

      if (rows.length < 24) {
        alert('Недостаточно данных для построения модели. Выберите больший период.')
        return
      }

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

      const quality = this.getQualityInfo(result.r2, result.mae, result.rmse)

      this.forecast = {
        price: Math.max(0, result.forecastPrice),
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
    },

    prepareDataset(rows) {
      const rowsWithLag = rows.map((row, index) => {
        const previousRow = index > 0 ? rows[index - 1] : null
        const previousPrice = previousRow ? this.getPrice(previousRow) : NaN

        return {
          row,
          previousPrice,
        }
      })

      const selected = [...this.selectedFactors]

      const expandedFactors = []

      for (const factor of selected) {
        if (factor === 'hourCycle') {
          expandedFactors.push('hourSin', 'hourCos')
        } else if (factor === 'dayCycle') {
          expandedFactors.push('daySin', 'dayCos')
        } else {
          expandedFactors.push(factor)
        }
      }

      const usedFactors = expandedFactors.filter(factor => {
        const values = rowsWithLag
          .map(item => this.getFactorValue(item, factor))
          .filter(value => Number.isFinite(value))

        return values.length >= Math.min(24, rows.length - 1)
      })

      const skippedFactors = expandedFactors.filter(factor => !usedFactors.includes(factor))

      const preparedRows = rowsWithLag
        .map(item => {
          const y = this.getPrice(item.row)
          const x = usedFactors.map(factor => this.getFactorValue(item, factor))

          return { y, x, source: item.row }
        })
        .filter(item => {
          return Number.isFinite(item.y) && item.x.every(value => Number.isFinite(value))
        })

      return {
        rows: preparedRows,
        usedFactors,
        skippedFactors,
      }
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

      const design = xValues.map(row => {
        const normalized = row.map((value, index) => {
          return (value - means[index]) / stds[index]
        })

        return [1, ...normalized]
      })

      const splitIndex = Math.max(
        Math.floor(rowCount * 0.8),
        featureCount + 5
      )

      if (splitIndex >= rowCount) return null

      const xTrain = design.slice(0, splitIndex)
      const yTrain = yValues.slice(0, splitIndex)

      const xTest = design.slice(splitIndex)
      const yTest = yValues.slice(splitIndex)

      const beta = this.calculateOlsCoefficients(xTrain, yTrain)

      if (!beta) return null

      const testPredictions = xTest.map(row => this.dot(row, beta))

      const errors = testPredictions.map((prediction, index) => {
        return prediction - yTest[index]
      })

      const mae = this.mean(errors.map(error => Math.abs(error)))
      const rmse = Math.sqrt(this.mean(errors.map(error => error * error)))

      const yTestMean = this.mean(yTest)
      const ssRes = errors.reduce((sum, error) => sum + error * error, 0)
      const ssTot = yTest.reduce((sum, value) => {
        return sum + Math.pow(value - yTestMean, 2)
      }, 0)

      const r2 = ssTot ? 1 - ssRes / ssTot : 0

      const lastX = design[design.length - 1]
      const forecastPrice = this.dot(lastX, beta)

      return {
        forecastPrice,
        r2,
        mae,
        rmse,
        trainCount: yTrain.length,
        testCount: yTest.length,
      }
    },

    calculateOlsCoefficients(xRows, yValues) {
      const xT = this.transpose(xRows)
      const xTx = this.multiplyMatrices(xT, xRows)
      const xTy = this.multiplyMatrixVector(xT, yValues)

      for (let i = 0; i < xTx.length; i++) {
        xTx[i][i] += 1e-6
      }

      const inverse = this.invertMatrix(xTx)

      if (!inverse) return null

      return this.multiplyMatrixVector(inverse, xTy)
    },

    getPrice(row) {
      return this.toNumber(
        row.price_sell ??
        row.Price ??
        row.price ??
        row.priceSell
      )
    },

    getVolume(row) {
      return this.toNumber(
        row.full_plan ??
        row.volume ??
        row.Q_cons ??
        row.q_cons
      )
    },

    getHour(row) {
      const directHour = this.toNumber(row.hour)

      if (Number.isFinite(directHour)) {
        return directHour
      }

      const date = new Date(row.timestamp)
      return Number.isNaN(date.getTime()) ? NaN : date.getHours()
    },

    getDayOfWeek(row) {
      const date = new Date(row.timestamp)
      return Number.isNaN(date.getTime()) ? NaN : date.getDay()
    },

    getFactorValue(item, factor) {
      const row = item.row

      if (factor === 'full_plan') {
        return this.getVolume(row)
      }

      if (factor === 'previousPrice') {
        return item.previousPrice
      }

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

      const aliases = {
        HPP: ['HPP', 'hpp', 'hydro', 'ges'],
        CHP: ['CHP', 'NPP', 'chp', 'npp', 'tes'],
        Q_cons: ['Q_cons', 'q_cons', 'consumption'],
        Q_exp: ['Q_exp', 'q_exp', 'export'],
        Q_imp: ['Q_imp', 'q_imp', 'import'],
        temperature: ['temperature', 'Temperature', 'temp'],
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
        HPP: 'Выработка ГЭС / HPP',
        CHP: 'Выработка ТЭС / CHP или NPP',
        Q_cons: 'Потребление / Q_cons',
        Q_exp: 'Экспорт / Q_exp',
        Q_imp: 'Импорт / Q_imp',
        temperature: 'Температура / temperature',
      }

      return labels[value] || value
    },

    getQualityInfo(r2, mae, rmse) {
      if (r2 >= 0.7) {
        return {
          label: 'Высокое качество',
          color: 'green-lighten-1',
        }
      }

      if (r2 >= 0.3) {
        return {
          label: 'Среднее качество',
          color: 'blue-lighten-1',
        }
      }

      if (r2 >= 0) {
        return {
          label: 'Низкое качество',
          color: 'orange-lighten-1',
        }
      }

      if (mae < rmse) {
        return {
          label: 'Требуется больше факторов',
          color: 'orange-lighten-1',
        }
      }

      return {
        label: 'Нестабильная модель',
        color: 'red-lighten-2',
      }
    },

    toNumber(value) {
      if (value === null || value === undefined || value === '') {
        return NaN
      }

      if (typeof value === 'number') {
        return Number.isFinite(value) ? value : NaN
      }

      const normalized = String(value)
        .replace(/\s/g, '')
        .replace(',', '.')

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
      return matrix[0].map((_, colIndex) => {
        return matrix.map(row => row[colIndex])
      })
    },

    multiplyMatrices(a, b) {
      return a.map(row => {
        return b[0].map((_, colIndex) => {
          return row.reduce((sum, value, rowIndex) => {
            return sum + value * b[rowIndex][colIndex]
          }, 0)
        })
      })
    },

    multiplyMatrixVector(matrix, vector) {
      return matrix.map(row => {
        return row.reduce((sum, value, index) => {
          return sum + value * vector[index]
        }, 0)
      })
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
          if (Math.abs(augmented[k][i]) > Math.abs(augmented[maxRow][i])) {
            maxRow = k
          }
        }

        if (Math.abs(augmented[maxRow][i]) < 1e-12) {
          return null
        }

        const temp = augmented[i]
        augmented[i] = augmented[maxRow]
        augmented[maxRow] = temp

        const pivot = augmented[i][i]

        for (let j = 0; j < 2 * n; j++) {
          augmented[i][j] /= pivot
        }

        for (let k = 0; k < n; k++) {
          if (k === i) continue

          const factor = augmented[k][i]

          for (let j = 0; j < 2 * n; j++) {
            augmented[k][j] -= factor * augmented[i][j]
          }
        }
      }

      return augmented.map(row => row.slice(n))
    },

    formatNumber(value, digits = 2) {
      if (!Number.isFinite(Number(value))) {
        return '0'
      }

      return Number(value).toLocaleString('ru-RU', {
        minimumFractionDigits: digits,
        maximumFractionDigits: digits,
      })
    },
  },
}
</script>

<style scoped>
.forecast-result {
  font-size: 26px;
  font-weight: 700;
  color: #1b5e20;
  text-align: center;
}

td:first-child {
  font-weight: 600;
  width: 45%;
}

td {
  padding: 10px 16px;
}
</style>