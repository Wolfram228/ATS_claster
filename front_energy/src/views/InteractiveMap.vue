<template>
  <!-- Убрали fluid, чтобы ширина совпадала с другими страницами -->
  <v-container class="map-page pa-4">
    
    <!-- Шапка страницы (вместо синего v-app-bar) -->
    <v-card
      class="pa-4 mb-4"
      elevation="1"
      rounded="lg"
      variant="outlined"
      style="border-color: rgba(0, 0, 0, 0.2)"
    >
      <div class="text-h5 font-weight-bold" align="left">
        <!-- Выводим выбранный регион вместо статичного заголовка -->
        {{ selectedRegion ? `Регион: ${selectedRegion}` : 'Интерактивная карта РФ' }}
      </div>
      <div class="text-body-2 text-grey-darken-1 mt-1" align="left">
        Выберите доступный регион на карте, чтобы увидеть структуру его генерации.
      </div>
    </v-card>

    <!-- Контейнер для карты и диаграмм (занимает всё оставшееся место) -->
    <v-row class="ma-0 content-row" no-gutters>
      
      <!-- ЛЕВАЯ КОЛОНКА: карта (увеличили до 8 колонок) -->
      <v-col cols="12" md="8" class="map-col pr-md-2">
        <div class="map-wrapper" ref="mapContainer">
          <div v-html="svgContent"></div>
        </div>
      </v-col>

      <!-- ПРАВАЯ КОЛОНКА: диаграммы (уменьшили до 4 колонок) -->
      <v-col cols="12" md="4" class="charts-col pl-md-2">
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

    availableRegions() {
      return (this.$store.getters.staticRegions || []).map(r => r.value)
    },

    selectedRegion: {
      get() {
        return this.$store.state.selectedRegionBeforeConfirmed
      },
      set(region) {
        this.$store.commit('SET_SELECTED_REGION_BEFORE_CONFIRMED', region)
        this.$store.commit('SET_SELECTED_REGION_PREV', region)
        this.$store.dispatch('fetchLastDayBoats')
        this.$store.dispatch('fetchPrevDayBoats')
        this.highlightRegion(region)
      },
    },

    boatsForRegion() {
      const region = this.selectedRegion
      if (!region) return []
      return (this.lastDayBoats || []).filter(r => r.region === region)
    },

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

  watch: {
    inited(newVal) {
      if (newVal) {
        this.$nextTick(() => {
          this.addRegionClickHandlers()
          if (this.selectedRegion) {
            this.highlightRegion(this.selectedRegion)
          }
        })
      }
    }
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
      const available = this.availableRegions

      paths.forEach(path => {
        const regionName = path.getAttribute('title')
        const isAvailable = available.includes(regionName)

        if (!isAvailable) {
          path.style.cursor = 'default'
          path.style.fill = '#e0e0e0'
          path.style.pointerEvents = 'none'
          
          path.onmouseenter = null
          path.onmouseleave = null
          path.onclick = null
          return
        }

        path.style.cursor = 'pointer'
        path.style.fill = '#90caf9'
        path.style.transition = '0.2s ease'
        path.style.pointerEvents = 'auto'

        path.onmouseenter = () => {
          if (this.selectedRegion !== regionName) {
            path.style.fill = '#42a5f5'
          }
        }
        
        path.onmouseleave = () => {
          if (this.selectedRegion !== regionName) {
            path.style.fill = '#90caf9'
          }
        }
        
        path.onclick = () => {
          this.selectedRegion = regionName
        }
      })
    },

    highlightRegion(regionTitle) {
      const paths = this.$refs.mapContainer.querySelectorAll('path[id]')
      const available = this.availableRegions

      paths.forEach(path => {
        const pathTitle = path.getAttribute('title')
        
        if (!available.includes(pathTitle)) {
          path.style.fill = '#e0e0e0'
        } else if (pathTitle === regionTitle) {
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
/* Контейнер страницы растягиваем на всю доступную высоту за вычетом глобальной шапки (64px) */
.map-page {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 64px);
  box-sizing: border-box;
  background-color: #fafbfc; /* Легкий фон, как у других страниц */
}

/* Ряд с картой и диаграммами занимает всё оставшееся место */
.content-row {
  flex: 1;
  min-height: 0; /* Важно для правильного сжатия flex-элементов */
}

/* Карта */
.map-col {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eef3f8;
  border-radius: 8px; /* Скругление как у карточек */
  border: 1px solid rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.map-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 10px;
}

.map-wrapper svg {
  max-width: 100%;
  max-height: 100%;
}

/* Диаграммы */
.charts-col {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px; /* Отступ между диаграммами */
}

.chart-box {
  flex: 1 1 0;
  min-height: 0;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.1);
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
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid rgba(0, 0, 0, 0.1);
}

/* На узких экранах (мобильных) отключаем жесткую высоту, чтобы контент разворачивался */
@media (max-width: 959px) {
  .map-page {
    height: auto;
  }
  
  .map-col, .charts-col {
    height: auto;
    min-height: 400px;
  }
  
  .map-col {
    margin-bottom: 16px;
  }

  .chart-box {
    height: 350px;
    flex: none;
  }
}
</style>
