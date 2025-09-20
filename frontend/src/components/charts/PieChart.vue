<script setup>
import { Chart as ChartJS, Title, Tooltip, Legend, ArcElement } from "chart.js";
import { Pie } from "vue-chartjs";
import { computed } from "vue";

// Register Chart.js components
ChartJS.register(Title, Tooltip, Legend, ArcElement);

// Props from parent
const props = defineProps({
  chartData: {
    type: Object,
    required: true
  },
  chartOptions: {
    type: Object,
    default: () => ({
      responsive: true,
      maintainAspectRatio: false, // <-- allows resizing
      plugins: {
        legend: {
          position: "bottom"
        },
        title: {
          display: true,
          text: "Customer Churn Categories"
        }
      }
    })
  }
});

// Ensure reactivity if chartData changes
const reactiveChartData = computed(() => props.chartData);
</script>

<template>
  <Pie :data="reactiveChartData" :options="chartOptions" />
</template>
