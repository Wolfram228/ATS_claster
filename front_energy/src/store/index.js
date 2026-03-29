import { createStore } from 'vuex';
import { getAccessToken, getApiBaseUrl, getSavedUser, isAuth } from '../utils/auth';

// YYYY-MM-DD в ЛОКАЛЬНОЙ таймзоне
function ymdLocal(d = new Date()) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

function getLastDayRange() {
  const today = ymdLocal(new Date())
  return { from: today, to: today }
}

function getPrevDayRange() {
  // "вчера" по локальному календарю
  const d = new Date()
  d.setDate(d.getDate() - 1)
  const yesterday = ymdLocal(d)

  return { from: yesterday, to: yesterday }
}

function normalizeBoats(data) {
    if (!Array.isArray(data)) return [];

    const unique = [];
    for (const row of data) {
        let exists = false;

        for (let i = 0; i < unique.length; i++) {
        const u = unique[i];

        if (
            u.timestamp === row.timestamp &&
            u.region === row.region &&
            u.hour === row.hour
        ) {
            exists = true;
            break;
        }
        }
        if (!exists) unique.push(row);
    }

    // сортировка: дата → регион → час
    unique.sort((a, b) => {
        const ta = String(a.timestamp);
        const tb = String(b.timestamp);
        const tCmp = ta.localeCompare(tb);
        if (tCmp !== 0) return tCmp;

        const ra = String(a.region || '');
        const rb = String(b.region || '');
        const rCmp = ra.localeCompare(rb, 'ru');
        if (rCmp !== 0) return rCmp;

        const ha = Number(a.hour);
        const hb = Number(b.hour);
        if (!Number.isNaN(ha) && !Number.isNaN(hb)) {
        return ha - hb;
        }
        return 0;
    });

    return unique;
}

async function fetchTableData({ from, to, region = '', hour = '', page, signal } = {}) {
    const params = new URLSearchParams({
        from,
        to,
    });

    if (region) {
        params.append('region', region);
    }

    if (hour) {
        params.append('hour', hour);
    }

    if (page) {
        params.append('page', String(page));
    }

    const token = getAccessToken();
    const headers = token
        ? { Authorization: `Bearer ${token}` }
        : {};

    const response = await fetch(`${getApiBaseUrl()}/api/table-data/?${params.toString()}`, {
        headers,
        signal,
    });

    if (!response.ok) {
        throw new Error(`Ошибка загрузки данных: ${response.status}`);
    }

    return response.json();
}

export default createStore({
    state() {
        return {
            // фиксированные последние и предпоследние 2 дня
            lastDayBoats: [],
            prevDayBoats: [],

            // изменяемые наборы
            changableDateBoats: [],
            boatsWithRegion: [],

            selectedRegion: "Иркутская область",
            selectedRegionBeforeConfirmed: "Иркутская область",
            selectedRegionPrev: "Иркутская область",

            selectedHour: "Все часы",

            // текущие даты (инициализируются в initBoats)
            selectedDateBefore: undefined,
            selectedDateAfter: undefined,

            loading: false,
            lastDayLoading: false,
            prevDayLoading: false,
            errorMessage: null,
            abortController: null,

            staticRegions: [
                "Алтайский край","Архангельская область","Астраханская область","Белгородская область","Брянская область",
                "Владимирская область","Волгоградская область","Вологодская область","Воронежская область","Город Севастополь",
                "Забайкальский край","Ивановская область","Иркутская область","Кабардино-Балкарская Республика",
                "Калужская область","Карачаево-Черкесская Республика","Кемеровская область","Кировская область",
                "Костромская область","Краснодарский край","Красноярский край","Курганская область",
                "Курская область","Ленинградская область","Липецкая область","Московская область","Мурманская область","Нижегородская область","Новгородская область",
                "Новосибирская область","Омская область","Оренбургская область","Орловская область",
                "Пензенская область","Пермский край","Псковская область","Республика Алтай",
                "Республика Башкортостан","Республика Бурятия","Республика Дагестан","Республика Ингушетия",
                "Республика Калмыкия","Республика Карелия","Республика Коми","Республика Крым",
                "Республика Марий Эл","Республика Мордовия","Республика Северная Осетия-Алания","Республика Татарстан",
                "Республика Тыва","Республика Хакасия","Ростовская область","Рязанская область",
                "Самарская область","Саратовская область","Свердловская область","Смоленская область",
                "Ставропольский край","Тамбовская область","Тверская область","Томская область",
                "Тульская область","Тюменская область","Удмуртская Республика","Ульяновская область",
                "Челябинская область","Чеченская Республика","Чувашская Республика-Чувашия","Ярославская область"
            ], // для геттера staticRegions

            // статус инициализации
            inited: false,
            lastDayDateInited: false,
            hasChangableData: false,
            isAuthenticated: isAuth(),
            user: getSavedUser(),

            // Вкладка аналитики цен
            priceAnalyticsRows: [],
            priceAnalyticsLoading: false,
            priceAnalyticsError: null,
        };
    },

    getters: {
        // регионы для изменяемого набора (changableDateBoats)
        regions(state) {
            const set = new Set();

            for (const row of state.changableDateBoats) {
                if (row.region && typeof row.region === 'string') {
                    set.add(row.region.trim());
                }
            }

            // отсортированный массив
            const sorted = Array.from(set).sort((a, b) =>
                a.localeCompare(b, 'ru')
            );

            return [
                { id: 0, value: "Все регионы" },
                ...sorted.map((name, i) => ({
                    id: i + 1,
                    value: name
                }))
            ];
        },
        staticRegions(state) {
            const sorted = [...state.staticRegions].sort((a, b) =>
            a.localeCompare(b, 'ru')
            )

            return sorted.map((name, i) => ({
                id: i + 1,
                value: name
            }))
        },

        // регионы для lastDayBoats + prevDayBoats
        /*regionsPrev(state) {
            const set = new Set();

            const all = [
                ...state.lastDayBoats,
                ...state.prevDayBoats
            ];

            for (const row of all) {
                if (row.region && typeof row.region === 'string') {
                    set.add(row.region.trim());
                }
            }

            const sorted = Array.from(set).sort((a, b) =>
                a.localeCompare(b, 'ru')
            );

            return [
                { id: 0, value: "Все регионы" },
                ...sorted.map((name, i) => ({
                    id: i + 1,
                    value: name
                }))
            ];
        }*/
    },

    mutations: {
        SET_LAST_DAY_BOATS(state, boats) {
            state.lastDayBoats = boats;
        },
        SET_PREV_DAY_BOATS(state, boats) {
            state.prevDayBoats = boats
        },
        SET_CHANGABLE_BOATS(state, boats) {
            state.changableDateBoats = boats;
        },
        SET_BOATS_WITH_REGION(state, boats) {
            state.boatsWithRegion = boats;
        },

        SET_SELECTED_DATE_BEFORE(state, value) {
            state.selectedDateBefore = value;
        },
        SET_SELECTED_DATE_AFTER(state, value) {
            state.selectedDateAfter = value;
        },
        SET_SELECTED_REGION(state, value) {
            state.selectedRegion = value;
        },
        SET_SELECTED_REGION_BEFORE_CONFIRMED(state, value) {
            state.selectedRegionBeforeConfirmed = value;
        },
        SET_SELECTED_REGION_PREV(state, value) {
            state.selectedRegionPrev = value;
        },

        SET_SELECTED_HOUR(state, value) {
            state.selectedHour = value;
        },

        SET_LOADING(state, value) {
            state.loading = value;
        },
        SET_LAST_DAY_LOADING(state, value) {
            state.lastDayLoading = value;
        },
        SET_PREV_DAY_LOADING(state, value) {
            state.prevDayLoading = value;
        },
        SET_ERROR(state, error) {
            state.errorMessage = error;
        },
        SET_ABORT_CONTROLLER(state, controller) {
            state.abortController = controller;
        },
        SET_AUTHENTICATED(state, value) {
            state.isAuthenticated = value;
        },
        SET_USER(state, value) {
            state.user = value;
        },
        SET_INITED(state, value) {
            state.inited = value;
        },
        SET_LAST_DAY_DATE_INITED(state, value) {
            state.lastDayDateInited = value;
        },
        SET_HAS_CHANGABLE_DATA(state, value) {
            state.hasChangableData = value;
        },
        // Вкладка аналитики цен
        SET_PRICE_ANALYTICS_ROWS(state, value) {
            state.priceAnalyticsRows = value;
        },
        SET_PRICE_ANALYTICS_LOADING(state, value) {
            state.priceAnalyticsLoading = value;
        },
        SET_PRICE_ANALYTICS_ERROR(state, value) {
            state.priceAnalyticsError = value;
        },
    },

    actions: {
        initLastDayDate({ state, commit }) {
            if (state.lastDayDateInited) return; // уже инициализирована

            const { from, to } = getLastDayRange();
            commit('SET_SELECTED_DATE_BEFORE', from);
            commit('SET_SELECTED_DATE_AFTER', to);

            commit('SET_LAST_DAY_DATE_INITED', true)
        },
        // 1) Глобальный стартовый запрос при загрузке приложения / первом входе на Information.vue
        async initBoats({ state, commit, dispatch }) {
            if (state.inited) return;

            if (!state.selectedDateBefore || !state.selectedDateAfter) { // на всякий случай
                dispatch('initLastDayDate');
            }

            // Инфокарточки: всегда грузим lastDay (today) ОДНИМ запросом
            // (не зависит от выбранной даты/региона)
            await dispatch('fetchLastDayBoats');

            //  Графики (home/information): решаем, нужен ли запрос
            const { from, to } = getLastDayRange();
            const selectedIsToday = state.selectedDateBefore === from && state.selectedDateAfter === to;
            const regionActive = state.selectedRegion && state.selectedRegion !== 'Все регионы';
            const regionsEqual = state.selectedRegion === state.selectedRegionPrev;

            // Если дата today + регионы одинаковые - можно переиспользовать lastDayBoats без запроса
            if (selectedIsToday && regionsEqual) {
                if (regionActive) {
                    commit('SET_CHANGABLE_BOATS', []);
                    commit('SET_HAS_CHANGABLE_DATA', true);
                    commit('SET_BOATS_WITH_REGION', state.lastDayBoats);
                } else {
                    commit('SET_CHANGABLE_BOATS', state.lastDayBoats);
                    commit('SET_HAS_CHANGABLE_DATA', true);
                    commit('SET_BOATS_WITH_REGION', []);
                }
            } else {
                // иначе проверяем: не лежат ли в сторе уже актуальный данные (например, с Table.vue)
                const alreadyHasRegionData = regionActive && Array.isArray(state.boatsWithRegion) && state.boatsWithRegion.length > 0;
                const alreadyHasAllRegionsData = !regionActive && Array.isArray(state.changableBoats) && state.changableBoats.length > 0;

                if (!alreadyHasRegionData && !alreadyHasAllRegionsData) {
                // данных ещё нет - делаем реальный запрос
                await dispatch('fetchBoatsCore', { mode: 'change' });
                }
            }

            // 3) Prev day: всегда отдельный запрос
            await dispatch('fetchPrevDayBoats');

            // 4) Финал
            commit('SET_INITED', true);
        },

        // 2) Запрос при смене дат / региона
        async fetchChangableBoats({ dispatch }) {
            await dispatch('fetchBoatsCore', {
                mode: 'change'
            });
        },

        // 4) Общая реализация запросов
        async fetchBoatsCore({ state, commit }, { mode }) {
            // отмена предыдущего запроса
            if (state.abortController) {
                state.abortController.abort();
            }

            const controller = new AbortController();
            commit('SET_ABORT_CONTROLLER', controller);
            const { signal } = controller;

            try {
                commit('SET_HAS_CHANGABLE_DATA', false);
                commit('SET_LOADING', true);
                commit('SET_ERROR', null);

                if (!state.selectedDateBefore || !state.selectedDateAfter) return
                console.log('timestamp before selected:', state.selectedDateBefore);
                console.log('timestamp after selected:', state.selectedDateAfter);

                const regionActive = state.selectedRegion && state.selectedRegion !== 'Все регионы';
                if (regionActive) console.log('region selected:', state.selectedRegion);
                
                const hourActive = state.selectedHour !== undefined && state.selectedHour !== null && state.selectedHour !== '' && state.selectedHour !== 'Все часы';
                if (hourActive) {
                    console.log('hour selected:', state.selectedHour);
                }

                const json = await fetchTableData({
                    from: state.selectedDateBefore,
                    to: state.selectedDateAfter,
                    region: regionActive ? state.selectedRegion : '',
                    hour: hourActive ? state.selectedHour : '',
                    signal,
                });

                // если за это время стартовал новый запрос – выходим
                if (controller !== state.abortController) return;
                const data = json.data || [];

                const boats = normalizeBoats(data);

                console.log('API LENGTH:', data.length);
                console.log('API UNIQUE LENGTH:', boats.length);

                if (mode === 'change') {
                    if (regionActive) {
                        commit('SET_BOATS_WITH_REGION', boats);
                        commit('SET_CHANGABLE_BOATS', [])
                    } else {
                        commit('SET_CHANGABLE_BOATS', boats);
                        commit('SET_BOATS_WITH_REGION', []);
                    }

                    commit('SET_HAS_CHANGABLE_DATA', true);
                }
            } catch (error) {
                if (controller === state.abortController) {
                    console.error('fetchBoatsCore error', error);
                    commit('SET_ERROR', error);
                }
            } finally {
                if (controller === state.abortController) {
                    commit('SET_LOADING', false);
                    commit('SET_ABORT_CONTROLLER', null);
                }
            }
        },
        async fetchLastDayBoats({ state, commit }) {
            const { from, to } = getLastDayRange();

            try {
                commit('SET_LAST_DAY_LOADING', true);
                console.log('last day timestamp before (info page):', from);
                console.log('last day timestamp after (info page):', to);

                const regionPrevActive = state.selectedRegionPrev && state.selectedRegionPrev !== 'Все регионы';
                if (regionPrevActive) console.log('prev region selected:', state.selectedRegionPrev);

                const json = await fetchTableData({
                    from,
                    to,
                    region: regionPrevActive ? state.selectedRegionPrev : '',
                });
                const data = json.data || [];
                const normalized = normalizeBoats(data);

                console.log('API LAST DAY LENGTH (info page):', data.length);
                console.log('API UNIQUE LAST DAY LENGTH (info page):', normalized.length);

                commit('SET_LAST_DAY_BOATS', normalized);
            } catch (e) {
                console.error('fetchLastDayBoats error', e);
                commit('SET_LAST_DAY_BOATS', []);
                commit('SET_ERROR', e);
            } finally {
                commit('SET_LAST_DAY_LOADING', false);
            }
        },
        async fetchPrevDayBoats({ state, commit }) {
            const { from, to } = getPrevDayRange();

            try {
                commit('SET_PREV_DAY_LOADING', true);
                console.log('prev day timestamp before (info page):', from);
                console.log('prev day timestamp after (info page):', to);

                const regionPrevActive = state.selectedRegionPrev && state.selectedRegionPrev !== 'Все регионы';
                if (regionPrevActive) console.log('prev region selected:', state.selectedRegionPrev);

                const json = await fetchTableData({
                    from,
                    to,
                    region: regionPrevActive ? state.selectedRegionPrev : '',
                });
                const data = json.data || [];
                const normalized = normalizeBoats(data);

                console.log('API PREV DAY LENGTH (info page):', data.length);
                console.log('API UNIQUE PREV DAY LENGTH (info page):', normalized.length);

                commit('SET_PREV_DAY_BOATS', normalized);
            } catch (e) {
                console.error('fetchPrevDayBoats error', e);
                commit('SET_PREV_DAY_BOATS', []); // на всякий случай очищаем
                commit('SET_ERROR', e);
            } finally {
                commit('SET_PREV_DAY_LOADING', false);
            }
        },
        // Вкладка аналитики цен
        async fetchPriceAnalyticsRows({ commit }, { from, to }) {
            try {
                commit('SET_PRICE_ANALYTICS_LOADING', true)
                commit('SET_PRICE_ANALYTICS_ERROR', null)

                console.log('selected timestamp before (price page):', from);
                console.log('selected timestamp after (price page):', to);

                let page = 1
                let hasNext = true
                const allRows = []

                while (hasNext) {
                    console.log('current pagination page:', page);

                    const json = await fetchTableData({
                        from,
                        to,
                        page,
                    })
                    const data = Array.isArray(json.data) ? json.data : []

                    console.log('API LENGTH (price page):', data.length);

                    const pagination = json.pagination || {}

                    allRows.push(...data)

                    hasNext = Boolean(pagination.has_next)
                    page += 1
                }

                commit('SET_PRICE_ANALYTICS_ROWS', allRows)
            } catch (error) {
                console.error('fetchPriceAnalyticsRows error', error)
                commit('SET_PRICE_ANALYTICS_ROWS', [])
                commit('SET_PRICE_ANALYTICS_ERROR', error)
            } finally {
                commit('SET_PRICE_ANALYTICS_LOADING', false)
            }
        },
    }
});

