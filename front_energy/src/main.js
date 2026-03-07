import { createApp } from 'vue'
import App from './App.vue'
import './style.css'

import vuetify from "./vuetify"
import router from "./router"

import '@mdi/font/css/materialdesignicons.css'

import store from './store';

// ECharts + vue-echarts
import { use } from 'echarts/core';
import { CanvasRenderer } from 'echarts/renderers';
import { PieChart, LineChart } from 'echarts/charts';
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components';
import VChart from 'vue-echarts';

// регистрируем части ECharts
use([
  CanvasRenderer,
  PieChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
]);

const app = createApp(App)

app.use(router)
app.use(vuetify)
app.use(store)
app.component('VChart', VChart)

//store.dispatch('initBoats');

app.mount('#app')