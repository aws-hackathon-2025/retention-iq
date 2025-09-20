<script setup>
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from "chart.js";
import { computed } from "vue";
import { Bar } from "vue-chartjs";

// Register Chart.js modules
ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

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
          display: false,
        },
        title: {
          display: true,
          text: "Customer Satisfaction Distribution"
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: "Satisfaction Score"
          }
        },
        y: {
          title: {
            display: true,
            text: "Number of Customers"
          }
        }
      }
    })
  }
});

const reactiveChartData = computed(() => props.chartData);
</script>

<template>
  <Bar :data="reactiveChartData" :options="chartOptions" />
</template>
