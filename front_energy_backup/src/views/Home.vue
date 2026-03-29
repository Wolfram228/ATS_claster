<template>
    <v-container>
        <v-card
        variant="outlined"
        rounded="lg"
        elevation="1" 
        style="border-color: rgba(0, 0, 0, 0.2)">
            <v-card-text v-if="!inited">Загрузка данных для графиков...</v-card-text>
            <v-card-text v-else>
                <!-- <div class="text-h5 font-weight-bold" align="center">Динамика потребления</div> -->
                <v-row justify="center">
                    <div class="text-body-2 text-grey-darken-1" style="text-align: center; width: 100%"> *Данные на странице представлены по региону {{ this.selectedRegionPrev }} </div>
                    <v-col cols="12" md="6">
                        <!-- печенька за текущие сутки (lastDayBoats) -->
                        <VChart :option="pieOptions" style="width: 100%; height: 400px;" />
                    </v-col>
                    <v-col cols="12" md="6" v-if="!prevDayLoading">
                        <!-- печенька за предыдущие сутки (prevDayBoats) -->
                        <VChart :option="pieOptionsPrev" style="width: 100%; height: 400px;" />
                    </v-col>
                </v-row>
                <v-row justify="center">
                    <!-- <div class="text-h5 font-weight-bold mt-5" align="center">Объёмы по генераторам: 2025-10-10 vs 2025-10-11</div> -->
                    <VChart :option="lineOptions" style="width: 100%; height: 400px;" />
                </v-row>
            </v-card-text>
        </v-card>
    </v-container>
</template>

<script>
import { mapState } from 'vuex';

const generatorFields = [
    { key: 'plan_GES', label: 'ГЭС' },
    { key: 'plan_AES', label: 'АЭС' },
    { key: 'plan_TES', label: 'ТЭС' },
    { key: 'plan_SES', label: 'СЭС' },
    { key: 'plan_VES', label: 'ВЭС' },
    { key: 'plan_other', label: 'прочие ВИЭ' }
];

export default {
    name: 'Home',

    computed: {
        ...mapState({
            boats: state => state.lastDayBoats,
            prevBoats: state => state.prevDayBoats,
            inited: state => state.inited,
            lastDayLoading: state => state.lastDayLoading,
            prevDayLoading: state => state.prevDayLoading
        }),
        selectedRegionPrev: {
            get() {
                return this.$store.state.selectedRegionPrev
            },
            set(region) {
                this.$store.commit("SET_SELECTED_REGION_PREV", region)
            }
        },

        // список часов (0–23), по которым есть данные (за два дня)
        hours() {
            const all = [...this.boats, ...this.prevBoats];
            const set = new Set(all.map(r => r.hour));
            return Array.from(set).sort((a, b) => a - b);
        },

        // список дат 'YYYY-MM-DD' в диапазоне (предыдущие + текущие сутки)
        dates() {
            const all = [...this.boats, ...this.prevBoats];
            const set = new Set(
                all
                .filter(r => typeof r.timestamp === 'string')
                .map(r => r.timestamp.slice(0, 10))
            );
            return Array.from(set).sort();
        },

        pieData() {
            const sumByField = field => this.boats.reduce((acc, row) => acc + (row[field] || 0), 0);

            return generatorFields.map(g => ({
                name: g.label,
                value: sumByField(g.key)
            }));
        },

        pieOptions() {
            return {
                title: {
                    text: 'Динамика потребления за текущие сутки',
                    left: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: params => {
                        const marker = params.marker;
                        const name = params.name;            // {b}
                        const value = Number(params.value);  // {c}
                        const percent = params.percent;      // {d}

                        return `${marker} ${name}: ${value.toFixed(2)} МВт·ч (${percent}%)`;
                    }
                },
                legend: {

                },
                series: [
                    {
                        type: 'pie',
                        radius: '70%',
                        data: this.pieData
                    }
                ]
            };
        },

        pieDataPrev() {
            const sumByField = field =>
                this.prevBoats.reduce((acc, row) => acc + (row[field] || 0), 0);

            return generatorFields.map(g => ({
                name: g.label,
                value: sumByField(g.key)
            }));
        },

        pieOptionsPrev() {
            return {
                title: {
                    text: 'Динамика потребления за предыдущие сутки',
                    left: 'center'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: params => {
                        const marker = params.marker;
                        const name = params.name;
                        const value = Number(params.value);
                        const percent = params.percent;

                        return `${marker} ${name}: ${value.toFixed(2)} МВт·ч (${percent}%)`;
                    }
                },
                legend: {

                },
                series: [
                    {
                        type: 'pie',
                        radius: '70%',
                        data: this.pieDataPrev
                    }
                ]
            };
        },

        lineSeries() {
            const series = [];

            this.dates.forEach(date => {
                const rowsForDate = [...this.boats, ...this.prevBoats].filter(r =>
                    String(r.timestamp).startsWith(date)
                );

                generatorFields.forEach(gen => {
                    const data = this.hours.map(hour => {
                        // суммируем по всем регионам для (дата, час)
                        const valueForHour = rowsForDate
                            .filter(r => r.hour === hour)
                            .reduce((sum, r) => sum + (Number(r[gen.key]) || 0), 0,);

                        return valueForHour;
                    });

                    series.push({
                        name: `${gen.label} ${date}`,
                        type: 'line',
                        smooth: true,
                        data,
                    });
                });
            });

            return series;
        },

        lineOptions() {
            return {
                title: {
                    text: this.dates.length
                        ? `Объёмы по генераторам: ${this.dates.join(' vs ')}`
                        : 'Объёмы по генераторам',
                    left: 'center',
                    top: 0
                },
                tooltip: { 
                    trigger: 'axis',
                    formatter: params => {
                        let hour = params[0].axisValue; // подпись по оси X (час)

                        let lines = params.map(p => {
                            const marker = p.marker;
                            const name = p.seriesName;       // название серии
                            const value = Number(p.value);   // значение точки

                            return `${marker} ${name}: ${value.toFixed(2)} МВт·ч`;
                        });

                        return `Час: ${hour}<br>` + lines.join('<br>');
                    }
                },
                legend: { top: 25 },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    name: 'Час',
                    data: this.hours
                },
                yAxis: {
                    type: 'value',
                    name: 'Объём, МВт·ч'
                },
                series: this.lineSeries
            };
        }
    },
    created() {
        if (!this.$store.state.inited) {
            this.$store.dispatch('initBoats');
        }
    }
};
</script>