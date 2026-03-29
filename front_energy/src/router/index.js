import { createRouter, createWebHistory } from 'vue-router'
import { isAuth } from "../utils/auth";

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
        path: "/login",
        name: "login",
        component: () => import("../views/Login.vue"),
    },
    {
        path: "/register",
        name: "register",
        component: () => import("../views/Register.vue"),
    },
    {
        path: "/lk",
        name: "lk",
        component: () => import("../views/LK.vue"),
        meta: { requiresAuth: true },
    },
    {
        path: "/:pathMatch(.*)*",
        name: "NotFound",
        component: () => import("../views/NotFound.vue")
    }
]
const router = createRouter({
    history: createWebHistory(),
    routes,
    scrollBehavior() {
        return { top: 0 }
    }
})

router.beforeEach((to) => {
  const publicPages = ["/login", "/register"]
  const isPublic = publicPages.includes(to.path)

  if (!isPublic && !isAuth()) {
    return { path: "/login" }
  }
})

export default router
