import { createRouter, createWebHistory } from 'vue-router'

const routes = [
    {
        path: '/',
        name: 'home',
        component: () => import("../views/Home.vue")
    },
    {
        path: '/home',
        redirect: "/"
    },
    {
        path: '/table',
        name: 'table',
        component: () => import("../views/Table.vue")

    },
    {
        path: "/information",
        name: "information",
        component: () => import("../views/Information.vue"),
        // props: route => ({...route.params, reportId: parseInt(route.params.id)}),
    },
    {
        path: "/interactiveMap",
        name: "interactiveMap",
        component: () => import("../views/InteractiveMap.vue"),
    },
    {
        path: '/price-analytics',
        name: 'priceAnalytics',
        component: () => import("../views/PriceAnalytics.vue")
    },
    {
        path: "/:pathMatch(.*)*",
        name: "NotFound",
        component: () => import("../views/NotFound.vue")
    }
]

export default createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior() {
        return { top: 0 }
    }
})