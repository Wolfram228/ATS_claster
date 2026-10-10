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
        <v-card v-if="!inited" class="pa-4" variant="outlined" rounded="lg">
          <v-card-text>Загрузка данных для графиков...</v-card-text>
        </v-card>

        <template v-else>
          <v-card v-if="!selectedRegion" class="pa-4" variant="outlined" rounded="lg">
            <v-card-text class="text-center text-grey-darken-1">
              Выберите регион на карте, чтобы увидеть диаграммы
            </v-card-text>
          </v-card>

          <template v-else>
            <v-card variant="outlined" rounded="lg" class="pa-2">
              <VChart :option="pieOptions" style="width: 100%; height: 340px;" />
            </v-card>

            <v-card
              v-if="!prevDayLoading"
              variant="outlined"
              rounded="lg"
              class="pa-2"
            >
              <VChart :option="pieOptionsPrev" style="width: 100%; height: 340px;" />
            </v-card>
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
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f4f6f9;
}

/* Левая колонка — карта */
.map-col {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 70vh;
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
}

.map-wrapper svg {
  max-width: 95%;
  max-height: 82vh;
}

.region-info {
  position: absolute;
  bottom: 20px;
  left: 20px;
  width: 280px;
  background: white;
}

/* Правая колонка — диаграммы */
.charts-col {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 12px;
  max-height: 100vh;
  overflow-y: auto;
  background: #fafbfc;
}
</style>
