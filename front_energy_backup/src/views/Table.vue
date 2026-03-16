<template>
    <v-container>
        <v-row>
            <v-col cols="12" md="3">
                <v-text-field
                v-model="draftDateBefore"
                label="Отображать с:"
                type="date"
                hide-details
                ></v-text-field>
            </v-col>
            <v-col cols="12" md="3">
                <v-text-field
                v-model="draftDateAfter"
                label="Отображать до:"
                type="date"
                hide-details
                ></v-text-field>
            </v-col>
            <v-col cols="12" md="3">
                <v-menu location="bottom">
                    <template v-slot:activator="{ props }">
                        <!-- <v-btn color="blue-grey-lighten-5" v-bind="props" min-height="55px" block> {{ filters.region || regions[0].value }} </v-btn> -->
                        <v-btn color="blue-grey-lighten-5" v-bind="props" min-height="55px" block> {{ selectedRegionBeforeConfirmed || "Выбор региона" }} </v-btn>
                    </template>

                    <!-- нужно реализовать список выбором из существующих в API значений -->
                    <v-list style="max-height: 300px">
                        <v-list-item
                        v-for="(region, id) in regions"
                        :key="id"
                        :value="id"
                        v-on:click="selectedRegionBeforeConfirmed = region.value"
                        >
                        <v-list-item-title>{{ region.value }}</v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
            </v-col>
            <v-col cols="12" md="3">
                <v-btn color="blue-grey-lighten-1" :disabled="isDateInvalid || !selectedRegionBeforeConfirmed" @click="fetchData" min-height="55px" block> Применить </v-btn>
                <div v-if="isDateInvalid" class="text-error mt-2"> Введена некорректная дата </div>
                <div v-if="!selectedRegionBeforeConfirmed" class="text-error mt-2"> Регион не выбран </div>
                <div 
                v-if="(!isDateInvalid && selectedRegionBeforeConfirmed) && (isDateChanged || (selectedRegion !== selectedRegionBeforeConfirmed))" 
                class="text-error mt-2">
                Вы не применили изменения</div>
            </v-col>
        </v-row>
        <v-row>
            <v-col cols="12" class="d-flex align-center">
                <v-menu class="w-50" :close-on-content-click="false">
                    <template #activator="{ props }">
                        <v-btn v-bind="props" color="blue-grey-lighten-5" block>Выбор столбцов</v-btn>
                    </template>
                    <v-list
                    density="compact"
                    class="d-flex flex-wrap"
                    style="max-height: 300px;">
                        <v-list-item
                        v-for="h in headers.filter(h => !leftHeaderKeys.includes(h.key))"
                        :key="h.key"
                        density="compact">
                            <template #prepend>
                                <v-list-item-action>
                                    <v-checkbox
                                    v-model="visibleColumnKeys"
                                    :value="h.key"
                                    hide-details
                                    density="compact"
                                    />
                                </v-list-item-action>
                            </template>
                            <v-list-item-title>
                                {{ h.title }}
                            </v-list-item-title>
                        </v-list-item>
                    </v-list>
                </v-menu>
            </v-col>
        </v-row>
        <v-row class="mt-1">
            <v-col cols="12" md="6" class="d-flex align-center">
                <v-btn v-if="!showTable" color="blue-grey-lighten-1" block @click="showTableChange" :disabled="!isSelectedRegionActive"> Отобразить таблицу </v-btn>
                <v-btn v-else color="blue-grey-lighten-1" block @click="showTableChange"> Скрыть таблицу </v-btn>
            </v-col>
            <v-col cols="12" md="6" class="d-flex align-center">
                <v-btn color="blue-grey-lighten-1" block @click="exportToExcel" :disabled="!isSelectedRegionActive"> Экспорт в Excel </v-btn>
            </v-col>
            <div v-if="!isSelectedRegionActive" class="text-error mt-2" style="text-align: center; width: 100%"> Выбраны не все параметры </div>
        </v-row>
        <v-row v-if="showTable">
            <div class="dtv-wrap table-x">
                <v-data-table-virtual
                class="my-dtv vertical-lines"
                :headers="visibleHeaders"
                :items="sortedItems"
                height="740"
                item-value="date"
                fixed-header
                style="border: 1px solid rgba(0, 0, 0, 0.2);">
                    <template #headers="{ columns }">
                        <tr>
                        <!-- левые колонки -->
                            <th
                            v-for="key in visibleLeftHeaderKeys"
                            :key="key"
                            rowspan="2"
                            class="px-2"
                            >
                                <div class="flex flex-col items-start">
                                    <span class="cursor-pointer select-none" @click="setSort(key)">
                                        {{ getHeader(key).title }}
                                        <v-icon v-if="sortKey === key"> {{ sortDesc ? 'mdi-menu-down' : 'mdi-menu-up' }}</v-icon>
                                        <v-icon v-else> {{ 'mdi-minus' }} </v-icon>
                                    </span>
                                    <v-text-field
                                    v-if="!noHeaderFilterKeys.includes(key)"
                                    v-model="filters[key]"
                                    density="compact"
                                    variant="underlined"
                                    hide-details
                                    class="mt-1 w-32">
                                    </v-text-field>
                                </div>
                            </th>
                        <!-- центральные групповые колонки -->
                            <th
                            v-for="group in visibleStationGroups"
                            :key="group.title"
                            :colspan="group.visibleKeys.length"
                            class="text-center"
                            >
                                {{ group.title }}
                            </th>
                        <!-- правые колонки-->
                            <th
                            v-for="key in visibleRightHeaderKeys"
                            :key="key"
                            rowspan="2"
                            class="px-2"
                            >
                                <div class="flex flex-col items-start">
                                    <span class="cursor-pointer select-none" @click="setSort(key)">
                                        {{ getHeader(key).title }}
                                        <v-icon v-if="sortKey === key"> {{ sortDesc ? 'mdi-menu-down' : 'mdi-menu-up' }}</v-icon>
                                        <v-icon v-else> {{ 'mdi-minus' }} </v-icon>
                                    </span>
                                    <v-text-field
                                    v-model="filters[key]"
                                    density="compact"
                                    variant="underlined"
                                    hide-details
                                    class="mt-1 w-32">
                                    </v-text-field>
                                </div>
                            </th>
                        </tr>
                        <!-- вторая строка для центральных колонок -->
                        <tr>
                            <template v-for="group in visibleStationGroups" :key="group.title + '-cols'">
                                <th
                                v-for="key in group.visibleKeys"
                                :key="key"
                                >
                                    <div class="flex flex-col items-start">
                                        <span class="cursor-pointer select-none" @click="setSort(key)">
                                            {{ getHeader(key).title.split('(')[0] }}
                                            <v-icon v-if="sortKey === key"> {{ sortDesc ? 'mdi-menu-down' : 'mdi-menu-up' }}</v-icon>
                                            <v-icon v-else> {{ 'mdi-minus' }} </v-icon>
                                        </span>
                                        <v-text-field
                                        v-model="filters[key]"
                                        density="compact"
                                        variant="underlined"
                                        hide-details
                                        class="mt-1 w-32">
                                        </v-text-field>
                                    </div>
                                </th>
                            </template>
                        </tr>
                    </template>
                    <template #no-data>
                        <div class="text-center pa-4">
                            <span>Данные отсутствуют</span>
                        </div>
                    </template>
                </v-data-table-virtual>
                <v-overlay
                    :model-value="loading"
                    contained
                    persistent
                    class="dtv-overlay">
                        <div class="dtv-overlay-content">
                        <v-progress-circular indeterminate size="28" />
                        <div class="dtv-overlay-text">Загрузка данных...</div>
                    </div>
                </v-overlay>
            </div>
        </v-row>
    </v-container>
</template>

<script>
import ExcelJS from 'exceljs'

import { mapState, mapActions } from 'vuex'

export default {
    data() {
        return {
            headers: [
                {title: 'Дата', key: 'timestamp'},
                {title: 'Субъект РФ', key: 'region'},
                {title: 'Час', key: 'hour'},
                {title: 'ГЭС (план)', key: 'plan_GES'},
                {title: 'АЭС (план)', key: 'plan_AES'},
                {title: 'ТЭС (план)', key: 'plan_TES'},
                {title: 'СЭС (план)', key: 'plan_SES'},
                {title: 'ВЭС (план)', key: 'plan_VES'},
                {title: 'Прочие ВИЭ (план)', key: 'plan_other'},
                {title: 'ГЭС (мин тех)', key: 'techmin_GES'},
                {title: 'АЭС (мин тех)', key: 'techmin_AES'},
                {title: 'ТЭС (мин тех)', key: 'techmin_TES'},
                {title: 'СЭС (мин тех)', key: 'techmin_SES'},
                {title: 'ВЭС (мин тех)', key: 'techmin_VES'},
                {title: 'Прочие ВИЭ (мин тех)', key: 'techmin_other'},
                {title: 'ГЭС (мин техн)', key: 'technomin_GES'},
                {title: 'АЭС (мин техн)', key: 'technomin_AES'},
                {title: 'ТЭС (мин техн)', key: 'technomin_TES'},
                {title: 'СЭС (мин техн)', key: 'technomin_SES'},
                {title: 'ВЭС (мин техн)', key: 'technomin_VES'},
                {title: 'Прочие ВИЭ (мин техн)', key: 'technomin_other'},
                {title: 'ГЭС (макс тех)', key: 'techmax_GES'},
                {title: 'АЭС (макс тех)', key: 'techmax_AES'},
                {title: 'ТЭС (макс тех)', key: 'techmax_TES'},
                {title: 'СЭС (макс тех)', key: 'techmax_SES'},
                {title: 'ВЭС (макс тех)', key: 'techmax_VES'},
                {title: 'Прочие ВИЭ (макс тех)', key: 'techmax_other'},
                {title: 'План потребления, МВт.ч.', key: 'plan_consumption'},
                {title: 'План экспорта, МВт.ч.', key: 'plan_export'},
                {title: 'План импорта, МВт.ч.', key: 'plan_import'},
                {title: 'Цена покупки, руб./МВт.ч.', key: 'price_buy'},
                {title: 'Цена продажи, руб./МВт.ч.', key: 'price_sell'},
                {title: 'Полный план, МВт.ч.', key: 'full_plan'}
            ],
            leftHeaderKeys: ['timestamp', 'region', 'hour'],
            stationGroups: [
                {
                    title: 'Плановый объем производства (по типам станций), МВт.ч.',
                    keys: ['plan_GES', 'plan_AES', 'plan_TES', 'plan_SES', 'plan_VES', 'plan_other']
                },
                {
                    title: 'Суммарные величины технического минимума (по типам станций), МВт.ч.',
                    keys: ['techmin_GES', 'techmin_AES', 'techmin_TES', 'techmin_SES', 'techmin_VES', 'techmin_other']
                },
                {
                    title: 'Суммарные величины технологического минимума (по типам станций), МВт.ч.',
                    keys: ['technomin_GES', 'technomin_AES', 'technomin_TES', 'technomin_SES', 'technomin_VES', 'technomin_other']
                },
                {
                    title: 'Суммарные величины технического максимума (по типам станций), МВт.ч.',
                    keys: ['techmax_GES', 'techmax_AES', 'techmax_TES', 'techmax_SES', 'techmax_VES', 'techmax_other']
                }
            ],
            rightHeaderKeys: ['plan_consumption', 'plan_export', 'plan_import', 'price_buy', 'price_sell', 'full_plan'],
            noHeaderFilterKeys: ['timestamp', 'region'],
            visibleColumnKeys: [],

            //regions,
            filters: {},

            sortKey: null,
            sortDesc: false,

            draftDateBefore: undefined,
            draftDateAfter: undefined,

           
            //selectedRegion: undefined, - в computed, теперь напрямую по VUex

            showTable: false,
            hintVisible: false
        }
    },
    methods: {
        fetchData() {
            if (this.isDateInvalid) return

            const regionChanged = this.selectedRegionBeforeConfirmed !== this.selectedRegion
            const regionActive = this.selectedRegionBeforeConfirmed && this.selectedRegionBeforeConfirmed !== 'Все регионы'

            if ((!regionChanged && !this.isDateChanged) || !regionActive) return

            if (this.isDateChanged) this.applyDates()
            if (regionChanged) this.selectedRegion = this.selectedRegionBeforeConfirmed

            this.$store.dispatch("fetchChangableBoats")
        },
        applyDates() {
            this.$store.commit('SET_SELECTED_DATE_BEFORE', this.draftDateBefore);
            this.$store.commit('SET_SELECTED_DATE_AFTER', this.draftDateAfter);
        },
        formatDateTime(dt) {
            if (!dt) return "";
            return dt.slice(0, 10);
        },
        getHeader(key) {
            return this.headers.find(c => c.key === key) || {};
        },
        isColumnVisible(key) {
            return this.visibleColumnKeys.includes(key);
        },
        /*selectRegion(region) {
            this.selectedRegion = region;
            this.filterRegion(region)
        },
        filterRegion(region) {
            if (region === this.regions[0].value) {
                this.filters.region = '';
                return
            } else this.filters.region = region
        },*/
        matchHourFilter(cell, filter) {
            if (!filter) return true;

            const hour = Number(cell);
            if (!Number.isInteger(hour) || hour < 0 || hour > 23) return false;

            // "0-3, 7, 11-15"
            const parts = filter.split(',');

            for (const rawPart of parts) {
                const part = rawPart.trim();
                if (!part) continue;

                const dashIndex = part.indexOf('-');

                if (dashIndex !== -1) {
                    // Диапазон "a-b"
                    const start = Number(part.slice(0, dashIndex));
                    const end   = Number(part.slice(dashIndex + 1));

                    if (!Number.isNaN(start) && !Number.isNaN(end)) {
                        const from = start < end ? start : end;
                        const to   = start < end ? end   : start;

                        if (hour >= from && hour <= to) {
                            return true;
                        }
                    }
                } else {
                    // Одиночное число "5"
                    const h = Number(part);
                    if (h === hour) {
                    return true;
                    }
                }
            }
            // ни один диапазон/значение не подошёл
            return false;
        },
        setSort(key) {
            if (this.sortKey !== key) {
            // выбрали новый столбец → сортируем по нему по возрастанию
            this.sortKey = key;
            this.sortDesc = false;
            } else if (!this.sortDesc) {
            // второй клик по тому же столбцу → по убыванию
            this.sortDesc = true;
            } else {
            // третий клик → убрать сортировку
            this.sortKey = null;
            this.sortDesc = false;
            }
        },
        async exportToExcel() {
            const items = this.sortedItems
            if (!items || !items.length) return

            const workbook = new ExcelJS.Workbook()
            const worksheet = workbook.addWorksheet('Таблица')

            const headerRow1 = []
            const headerRow2 = []
            const columnKeys = []

            // какие колонки реально видимы
            const leftKeys  = (this.leftHeaderKeys  || []).filter(key => this.visibleColumnKeys.includes(key))
            const rightKeys = (this.rightHeaderKeys || []).filter(key => this.visibleColumnKeys.includes(key))

            const groups = (this.stationGroups || [])
                .map(group => {
                    const visibleKeys = (group.keys || []).filter(key => this.visibleColumnKeys.includes(key))
                    return { ...group, visibleKeys }
                })
                .filter(group => group.visibleKeys.length)

            const leftCount  = leftKeys.length
            const rightCount = rightKeys.length

            // 1) ЛЕВЫЕ КОЛОНКИ: Дата / Субъект / Час и т.п.
            if (leftCount) {
                for (const key of leftKeys) {
                    const header = this.getHeader(key)
                    const title  = header.title || key

                    headerRow1.push(title)
                    headerRow2.push('')   // объединяем по вертикали
                    columnKeys.push(key)
                }
            }

            // 2) ЦЕНТРАЛЬНЫЕ ГРУППЫ (stationGroups) только с видимыми колонками
            if (groups && groups.length) {
                for (const group of groups) {
                    const keys = group.visibleKeys || []
                    if (!keys.length) continue

                    keys.forEach((key, idx) => {
                        const header = this.getHeader(key)
                        let title    = header.title || key

                        // как в шаблоне: до '('
                        const i = title.indexOf('(')
                        if (i !== -1) {
                            title = title.slice(0, i).trim()
                        }

                        // первая строка — название группы только над первым столбцом
                        headerRow1.push(idx === 0 ? group.title : '')
                        headerRow2.push(title)
                        columnKeys.push(key)
                    })
                }
            }

            // 3) ПРАВЫЕ КОЛОНКИ
            if (rightCount) {
                for (const key of rightKeys) {
                    const header = this.getHeader(key)
                    const title  = header.title || key

                    headerRow1.push(title)
                    headerRow2.push('')   // объединяем по вертикали
                    columnKeys.push(key)
                }
            }

            // если пользователь выключил вообще всё — просто выходим
            if (!columnKeys.length) {
                return
            }

            // Добавляем две строки заголовков
            const row1 = worksheet.addRow(headerRow1)
            const row2 = worksheet.addRow(headerRow2)

            const totalCols = columnKeys.length

            // 4) Мерджим левые колонки по вертикали (строки 1–2)
            for (let col = 1; col <= leftCount; col++) {
                worksheet.mergeCells(1, col, 2, col)
            }

            // 5) Мерджим центральные группы по горизонтали (строка 1)
            let col = leftCount + 1
            if (groups && groups.length) {
                for (const group of groups) {
                    const keys = group.visibleKeys || []
                    if (!keys.length) continue

                    const startCol = col
                    const endCol   = col + keys.length - 1

                    worksheet.mergeCells(1, startCol, 1, endCol)

                    col = endCol + 1
                }
            }

            // 6) Мерджим правые колонки по вертикали (строки 1–2)
            if (rightCount) {
                const rightStart = totalCols - rightCount + 1
                for (let c = rightStart; c <= totalCols; c++) {
                    worksheet.mergeCells(1, c, 2, c)
                }
            }

            // 7) ДАННЫЕ (в том же порядке, что в таблице)
            for (const item of items) {
                const rowValues = columnKeys.map(key => {
                    const val = item[key]
                    return val == null ? '' : val
                })
                worksheet.addRow(rowValues)
            }

            // 8) СТИЛИ

            // более светлый бирюзовый
            const headerFill = {
                type: 'pattern',
                pattern: 'solid',
                fgColor: { argb: 'FFE0F7FA' } // светлая бирюза
            }

            const thinBorder = {
                top:    { style: 'thin' },
                left:   { style: 'thin' },
                bottom: { style: 'thin' },
                right:  { style: 'thin' }
            }

            // высота шапки чуть меньше
            row1.height = 18
            row2.height = 18

            ;[row1, row2].forEach(row => {
                row.eachCell(cell => {
                    cell.fill = headerFill
                    cell.font = { bold: true, size: 10 }
                    cell.alignment = { horizontal: 'center', vertical: 'middle', wrapText: true }
                    cell.border = thinBorder
                })
            })

            // рамка для всех остальных ячеек + чуть уже колонки
            worksheet.eachRow((row, rowNumber) => {
                if (rowNumber <= 2) return
                row.height = 16
                row.eachCell(cell => {
                    cell.border = thinBorder
                    cell.alignment = { vertical: 'middle' }
                })
            })

            worksheet.columns.forEach(column => {
                column.width = 11 // чуть компактнее
            })

            // 9) Генерация .xlsx и скачивание
            const buffer = await workbook.xlsx.writeBuffer()
            const blob = new Blob(
                [buffer],
                { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }
            )

            const url  = URL.createObjectURL(blob)
            const link = document.createElement('a')

            const from = this.$store.state.selectedDateBefore || ''
            const to   = this.$store.state.selectedDateAfter || ''

            link.href = url
            link.download = `table_${from}_${to}_${this.selectedRegion}.xlsx` // нормальный excel-формат
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            URL.revokeObjectURL(url)
        },
        showTableChange() {
            this.showTable = !this.showTable
        },
        // YYYY-MM-DD в ЛОКАЛЬНОЙ таймзоне
        ymdLocal(input = new Date()) {
            let d = input

            // если пришла строка YYYY-MM-DD — аккуратно превращаем в Date (локально)
            if (typeof d === 'string') {
            const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(d)
            if (!m) return null
            const y = Number(m[1])
            const mo = Number(m[2]) - 1
            const day = Number(m[3])
            d = new Date(y, mo, day) // локальная полночь
            }

            // если всё ещё не Date — выходим
            if (!(d instanceof Date) || Number.isNaN(d.getTime())) return null

            const y = d.getFullYear()
            const m = String(d.getMonth() + 1).padStart(2, '0')
            const day = String(d.getDate()).padStart(2, '0')
            return `${y}-${m}-${day}`
        },
    },
    computed: {
        ...mapState({
            boats: state => state.boatsWithRegion,
            loading: state => state.loading,
        }),
        selectedRegion: {
            get() {
                return this.$store.state.selectedRegion
            },
            set(region) {
                this.$store.commit("SET_SELECTED_REGION", region)
            }
        },
        selectedRegionBeforeConfirmed: {
            get() {
                return this.$store.state.selectedRegionBeforeConfirmed
            },
            set(region) {
                this.$store.commit("SET_SELECTED_REGION_BEFORE_CONFIRMED", region)
            }
        },
        isSelectedRegionActive() {
            return this.selectedRegion && this.selectedRegion !== "Все регионы" ? true : false
        },
        regions() {
            return this.$store.getters.staticRegions;
        },
        virtualBoats() {
            if (!this.boats) return [];
            return this.boats.map(boat => ({
                ...boat,
                timestamp: this.formatDateTime(boat.timestamp),
            }));
        },
        filteredItems() {
            return this.virtualBoats.filter(item =>
                Object.entries(this.filters).every(([key, value]) => {
                if (!value) return true

                const cell = item[key]

                if (key === "hour") {
                    return this.matchHourFilter(cell, value)
                }

                return cell != null && String(cell).toLowerCase().startsWith(value.toLowerCase())
                })
            )
        },
        sortedItems() {
            const items = [...this.filteredItems];
            if (!this.sortKey) return items;

            const key = this.sortKey;
            const dir = this.sortDesc ? -1 : 1;

            return items.sort((a, b) => {
            const va = a[key];
            const vb = b[key];

            if (va == null && vb == null) return 0;
            if (va == null) return 1;
            if (vb == null) return -1;

            // числа сортируем по числу
            if (typeof va === 'number' && typeof vb === 'number') {
                return (va - vb) * dir;
            }

            // всё остальное — как строки
            return String(va).localeCompare(String(vb), 'ru') * dir;
            });
        },
        // список headers, который пойдёт в саму таблицу (тело)
        visibleHeaders() {
            return this.headers.filter(h => this.isColumnVisible(h.key));
        },

        // левые колонки с учётом видимости
        visibleLeftHeaderKeys() {
            return this.leftHeaderKeys.filter(k => this.isColumnVisible(k));
        },

        // правые колонки с учётом видимости
        visibleRightHeaderKeys() {
            return this.rightHeaderKeys.filter(k => this.isColumnVisible(k));
        },

        // отбрасываем центральные группы, у которых не осталось ни одного столбца
        visibleStationGroups() {
            return this.stationGroups.map(group => {
                const visibleKeys = group.keys.filter(k => this.isColumnVisible(k));
                return {
                ...group,
                visibleKeys,
                };
            }).filter(group => group.visibleKeys.length > 0);
        },
        isDateChanged() {
            return ( this.draftDateBefore !== this.$store.state.selectedDateBefore || this.draftDateAfter !== this.$store.state.selectedDateAfter )
        },

        isDateInvalid() {
            const from = this.draftDateBefore
            const to = this.draftDateAfter

            if (!from || !to) return true

            // строгая проверка формата (и реальной даты)
            const fromYmd = this.ymdLocal(from)
            const toYmd = this.ymdLocal(to)
            if (!fromYmd || !toYmd) return true

            const today = this.ymdLocal(new Date())
            if (!today) return true

            const d = new Date()
            d.setFullYear(d.getFullYear() - 3)
            const minDate = this.ymdLocal(d)
            if (!minDate) return true

            // "от" не может быть завтра или позже
            if (fromYmd > today) return true

            // "от" не старше 3 лет назад
            if (fromYmd < minDate) return true

            // диапазон
            if (fromYmd > toYmd) return true

            return false
        }
    },
    created() {
        if (!this.$store.state.lastDayDateInited) {
            this.$store.dispatch('initLastDayDate');
        }

        if (this.isSelectedRegionActive) {
            this.showTable = true;
            //this.selectedRegionBeforeConfirmed = this.selectedRegion;
        };

        this.visibleColumnKeys = this.headers.map(h => h.key);

        this.draftDateAfter = this.$store.state.selectedDateAfter
        this.draftDateBefore = this.$store.state.selectedDateBefore
    }
}
</script>

<style scoped>
.dtv-wrap {
  position: relative;
}

.dtv-overlay-content {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.vertical-lines :deep(table) {
  border-collapse: collapse;
}

/* и th, и td должны быть position: relative,
   чтобы можно было поставить ::after по правому краю */
.vertical-lines :deep(th),
.vertical-lines :deep(td) {
  position: relative;
}

/* вертикальная линия внутри ячейки */
.vertical-lines :deep(th::after),
.vertical-lines :deep(td::after) {
  content: "";
  position: absolute;
  top: 0;
  right: 0;
  width: 1px;
  height: 100%;
  background: rgba(0, 0, 0, 0.2);
  pointer-events: none;
}

/* опционально – общий контур */
.vertical-lines :deep(.v-table__wrapper) {
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-right: none; 
  position: relative;
}

/* Центрирование содержимого overlay */
:deep(.dtv-overlay .v-overlay__content) {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
}

/* Внутренний блок */
.dtv-overlay-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.9);
}

/* Текст */
.dtv-overlay-text {
  font-size: 14px;
  line-height: 1.2;
}

.table-x {
  max-width: 100%;
  overflow-x: auto;          /* скролл по X в контейнере */
}

</style>