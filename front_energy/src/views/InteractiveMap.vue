<template>
  <v-container fluid class="map-page pa-0">
    <v-app-bar color="primary" dark flat>
      <v-app-bar-title>Интерактивная карта РФ</v-app-bar-title>
    </v-app-bar>

    <v-row class="ma-0 fill-height" no-gutters>
      <!-- ЛЕВАЯ КОЛОНКА: карта -->
      <v-col cols="12" md="7" class="map-col">
        <div class="map-wrapper" ref="mapContainer">
          <div v-html="svgContent"></div>
        </div>

        <v-card v-if="selectedRegion" class="region-info" elevation="6">
          <v-card-title class="text-body-1">{{ selectedRegion }}</v-card-title>
        </v-card>
      </v-col>

      <!-- ПРАВАЯ КОЛОНКА: диаграммы -->
      <v-col cols="12" md="5" class="charts-col">
        <div v-if="!inited" class="chart-placeholder">
          Загрузка данных для графиков...
        </div>

        <template v-else>
          <div v-if="!selectedRegion" class="chart-placeholder">
            Выберите регион на карте, чтобы увидеть диаграммы
          </div>

          <template v-else>
            <div class="chart-box">
              <VChart :option="pieOptions" autoresize class="chart-fill" />
            </div>

            <div v-if="!prevDayLoading" class="chart-box">
              <VChart :option="pieOptionsPrev" autoresize class="chart-fill" />
            </div>
          </template>
        </template>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ruSvg from '../assets/ru_regions.svg?raw'
import { mapState } from 'vuex'

const generatorFields = [
  { key: 'plan_GES',   label: 'ГЭС' },
  { key: 'plan_AES',   label: 'АЭС' },
  { key: 'plan_TES',   label: 'ТЭС' },
  { key: 'plan_SES',   label: 'СЭС' },
  { key: 'plan_VES',   label: 'ВЭС' },
  { key: 'plan_other', label: 'прочие ВИЭ' },
]

export default {
  name: 'InteractiveMap',

  data() {
    return {
      svgContent: ruSvg,
    }
  },

  computed: {
    ...mapState({
      lastDayBoats:   state => state.lastDayBoats,
      prevDayBoats:   state => state.prevDayBoats,
      inited:         state => state.inited,
      prevDayLoading: state => state.prevDayLoading,
    }),

    selectedRegion: {
      get() {
        return this.$store.state.selectedRegionBeforeConfirmed
      },
      set(region) {
        this.$store.commit('SET_SELECTED_REGION_BEFORE_CONFIRMED', region)
        this.highlightRegion(region)
      },
    },

    // отфильтрованные данные для текущих суток
    boatsForRegion() {
      const region = this.selectedRegion
      if (!region) return []
      return (this.lastDayBoats || []).filter(r => r.region === region)
    },

    // отфильтрованные данные для предыдущих суток
    prevBoatsForRegion() {
      const region = this.selectedRegion
      if (!region) return []
      return (this.prevDayBoats || []).filter(r => r.region === region)
    },

    pieData() {
      const sumByField = field =>
        this.boatsForRegion.reduce((acc, row) => acc + (row[field] || 0), 0)

      return generatorFields.map(g => ({
        name: g.label,
        value: sumByField(g.key),
      }))
    },

    pieDataPrev() {
      const sumByField = field =>
        this.prevBoatsForRegion.reduce((acc, row) => acc + (row[field] || 0), 0)

      return generatorFields.map(g => ({
        name: g.label,
        value: sumByField(g.key),
      }))
    },

    pieOptions() {
      return {
        title: {
          text: 'Динамика потребления за текущие сутки',
          left: 'center',
          textStyle: { fontSize: 14, fontWeight: 600 },
        },
        tooltip: {
          trigger: 'item',
          formatter: params => {
            const value = Number(params.value)
            return `${params.marker} ${params.name}: ${value.toFixed(2)} МВт·ч (${params.percent}%)`
          },
        },
        legend: { bottom: 0 },
        series: [
          {
            type: 'pie',
            radius: '65%',
            center: ['50%', '55%'],
            data: this.pieData,
            emptyCircleStyle: { color: '#e0e0e0' },
          },
        ],
      }
    },

    pieOptionsPrev() {
      return {
        title: {
          text: 'Динамика потребления за предыдущие сутки',
          left: 'center',
          textStyle: { fontSize: 14, fontWeight: 600 },
        },
        tooltip: {
          trigger: 'item',
          formatter: params => {
            const value = Number(params.value)
            return `${params.marker} ${params.name}: ${value.toFixed(2)} МВт·ч (${params.percent}%)`
          },
        },
        legend: { bottom: 0 },
        series: [
          {
            type: 'pie',
            radius: '65%',
            center: ['50%', '55%'],
            data: this.pieDataPrev,
            emptyCircleStyle: { color: '#e0e0e0' },
          },
        ],
      }
    },
  },

  mounted() {
    this.addRegionClickHandlers()
    if (this.selectedRegion) {
      this.highlightRegion(this.selectedRegion)
    }
  },

  methods: {
    addRegionClickHandlers() {
      const paths = this.$refs.mapContainer.querySelectorAll('path[id]')
      paths.forEach(path => {
        path.style.cursor = 'pointer'
        path.style.fill = '#90caf9'
        path.style.transition = '0.2s ease'

        path.addEventListener('mouseenter', () => {
          if (this.selectedRegion !== path.getAttribute('title')) {
            path.style.fill = '#42a5f5'
          }
        })
        path.addEventListener('mouseleave', () => {
          if (this.selectedRegion !== path.getAttribute('title')) {
            path.style.fill = '#90caf9'
          }
        })

        path.addEventListener('click', () => {
          this.selectedRegion = path.getAttribute('title')
        })
      })
    },

    highlightRegion(regionTitle) {
      const paths = this.$refs.mapContainer.querySelectorAll('path[id]')
      paths.forEach(path => {
        if (path.getAttribute('title') === regionTitle) {
          path.style.fill = '#ef5350'
        } else {
          path.style.fill = '#90caf9'
        }
      })
    },
  },
}
</script>

<style scoped>
.map-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f4f6f9;
  overflow: hidden;
}

/* Карта и диаграммы — одной высоты (вычитаем app-bar) */
.map-col,
.charts-col {
  height: calc(100vh - 64px);
}

.map-col {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eef3f8;
  border-right: 1px solid rgba(0, 0, 0, 0.06);
}

.map-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
  box-sizing: border-box;
}

.map-wrapper svg {
  max-width: 95%;
  max-height: 95%;
}

.region-info {
  position: absolute;
  bottom: 20px;
  left: 20px;
  width: 280px;
  background: white;
}

/* Правая колонка — диаграммы столбиком, делят высоту пополам */
.charts-col {
  display: flex;
  flex-direction: column;
  padding: 8px;
  gap: 8px;
  background: #fafbfc;
  box-sizing: border-box;
}

.chart-box {
  flex: 1 1 0;
  min-height: 0;
  overflow: hidden;
}

.chart-fill {
  width: 100%;
  height: 100%;
}

.chart-placeholder {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  font-size: 14px;
  text-align: center;
  padding: 16px;
}

/* На узких экранах — не фиксируем высоту, даём развернуться по содержимому */
@media (max-width: 959px) {
  .map-page {
    height: auto;
    overflow: visible;
  }

  .map-col,
  .charts-col {
    height: auto;
  }

  .map-col {
    min-height: 60vh;
  }

  .chart-box {
    flex: none;
    height: 320px;
  }
}
</style>
