import { ref } from "vue";

export const dashboardSummary = ref(null);

export const updateDashboardSummary = (obj) => {
  dashboardSummary.value = obj;
};
