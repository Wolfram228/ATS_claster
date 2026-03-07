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
        path: '/reports', 
        name: 'reports', 
        component: () => import("../views/Reports.vue") 
    },
    {
        path: '/table',
        name: 'table',
        component: () => import("../views/Table.vue")

    },
    {
        path: "/reportInfo/:reportId",
        name: "reportInfo",
        component: () => import("../views/ReportInfo.vue"),
        props: route => ({...route.params, reportId: parseInt(route.params.id)}),
    },
    {
        path: "/:pathMatch(.*)*",
        name: "NotFound",
        component: () => import("../views/NotFound.vue")
    }
]

export default createRouter({
  history: createWebHistory(),
  routes
})