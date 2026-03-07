<template>
  <v-container fluid class="map-page pa-0">
    <v-app-bar color="primary" dark flat>
      <v-app-bar-title>Интерактивная карта РФ</v-app-bar-title>
    </v-app-bar>

    <div class="map-wrapper" ref="mapContainer">
      <div v-html="svgContent"></div>
    </div>

    <v-card v-if="selectedRegion" class="region-info" elevation="6">
      <v-card-title>{{ selectedRegion }}</v-card-title>
    </v-card>
  </v-container>
</template>

<script>
import ruSvg from '../assets/ru_regions.svg?raw'

export default {
  name: 'InteractiveMap',

  data() {
    return {
      svgContent: ruSvg
    }
  },

  computed: {
    selectedRegion: {
      get() {
        return this.$store.state.selectedRegionBeforeConfirmed
      },
      set(region) {
        this.$store.commit('SET_SELECTED_REGION_BEFORE_CONFIRMED', region)
        this.highlightRegion(region)
      }
    }
  },

  mounted() {
    this.addRegionClickHandlers()
    // при загрузке, если регион уже выбран в Vuex, подсветим его
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

        // hover
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

        // click
        path.addEventListener('click', () => {
          this.selectedRegion = path.getAttribute('title')
        })
      })
    },

    highlightRegion(regionTitle) {
      const paths = this.$refs.mapContainer.querySelectorAll('path[id]')
      paths.forEach(path => {
        if (path.getAttribute('title') === regionTitle) {
          path.style.fill = '#ef5350' // выбранный регион
        } else {
          path.style.fill = '#90caf9' // все остальные
        }
      })
    }
  }
}
</script>

<style scoped>
.map-page {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f4f6f9;
}

.map-wrapper {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #eef3f8;
}

.map-wrapper svg {
  max-width: 90%;
  max-height: 90%;
}

.region-info {
  position: absolute;
  bottom: 20px;
  left: 20px;
  width: 300px;
}
</style>