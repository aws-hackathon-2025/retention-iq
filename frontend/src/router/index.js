import { createWebHistory, createRouter } from "vue-router";
import Dashboard from "../views/Dashboard.vue";

const routes = [
  { path: "/", component: Dashboard },
  { path: "/customers", component: () => import("../views/Customers.vue") },
];

export const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});
