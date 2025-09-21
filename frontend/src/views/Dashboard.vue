<script setup>
import { computed, ref } from 'vue';
import { fetchUrl } from '../composables/fetchUrl';
import BarChart from '../components/charts/BarChart.vue';
import PieChart from '../components/charts/PieChart.vue';
import { customers } from '../state/customers.js';
import { dashboardSummary, updateDashboardSummary } from '../state/dashboard-summary.js';

const isLoading = ref(false);

(async () => {
  // Update isloading
  isLoading.value = true;

  const fetchReqs = [];

  // Create a fetch request for dashboard summary
  if (!dashboardSummary.value) {
    const dashboardHeaders = new Headers();
    dashboardHeaders.append("x-api-key", import.meta.env.VITE_API_KEY);
    const dashboardFetch = fetchUrl(import.meta.env.VITE_DASHBOARD_SUMMARY_ENDPOINT, "GET", dashboardHeaders);
    fetchReqs.push(dashboardFetch);
  }

  // Create a fetch request for customers
  if (!customers.value) {
    const customerHeaders = new Headers();
    customerHeaders.append("x-api-key", import.meta.env.VITE_API_KEY);
    const customerFetch = fetchUrl(import.meta.env.VITE_GET_CUSTOMERS_ENDPOINT + "?skip=0&limit=20", "GET", customerHeaders);
    fetchReqs.push(customerFetch);
  }

  // Collect all results
  let dashboardRaw, customersRaw;
  const fetchResults = await Promise.all(fetchReqs);
  if (fetchResults.length === 2) {
    // fetch both customers and dashboard
    [dashboardRaw, customersRaw] = fetchResults;

    const customerData = JSON.parse(customersRaw.body);
    customers.value = customerData;

    const data = JSON.parse(dashboardRaw.body);
    updateDashboardSummary(data);

  } else if (!dashboardSummary.value) {
    // Update dashboard details
    dashboardRaw = fetchResults[0];
    const data = JSON.parse(dashboardRaw.body);
    updateDashboardSummary(data);

  } else if (!customers.value) {
    // Update customers
    customersRaw = fetchResults[0];
    const customerData = JSON.parse(customersRaw.body);
    customers.value = customerData;
  }

  // Update isloading
  isLoading.value = false;
})();

const chartData = computed(() => {
  if (!dashboardSummary.value || !dashboardSummary.value.satisfactionCounts) return;

  return {
    labels: [1, 2, 3, 4, 5],
    datasets: [
      {
        label: "Number of Customers",
        backgroundColor: "#3b82f6",
        data: Object.values(dashboardSummary.value.satisfactionCounts)
      }
    ]
  };
});

const churnBreakdown = computed(() => {
  if (!dashboardSummary.value || !dashboardSummary.value.riskCounts) return;

  return {
    labels: ["Low Risk", "Medium Risk", "High Risk"],
    datasets: [
      {
        data: [dashboardSummary.value.riskCounts["Low Risk"], dashboardSummary.value.riskCounts["Medium Risk"], dashboardSummary.value.riskCounts["High Risk"]],
        backgroundColor: ["#1E3A8A", "#93C5FD", "#E5E7EB"]
      }
    ]
  };
});

const interventionBreakdown = computed(() => {
  if (!dashboardSummary.value || !dashboardSummary.value.interventionCounts) return;

  return {
    labels: ["No Interventions Taken", "Interventions Taken"],
    datasets: [
      {
        data: [dashboardSummary.value.interventionCounts["noInterventionCount"], dashboardSummary.value.interventionCounts["interventionCount"]],
        backgroundColor: ["#1E3A8A", "#93C5FD"]
      }
    ]
  };
});

const churnRiskFilter = ref('all');
const interventionFilter = ref('all');

const churnRiskRanges = {
  'all': { low: 0, high: 1 },
  'high': { low: 0.75, high: 1 },
  'medium': { low: 0.2, high: 0.75 },
  'low': { low: 0, high: 0.2 }
};
const interventionMapper = {
  'all': null,
  'true': true,
  'false': false,
};

const filteredCustomers = computed(() => {
  if (!customers.value) return customers.value;

  // return customers.value;
  const { low, high } = churnRiskRanges[churnRiskFilter.value];
  const interventionOption = interventionMapper[interventionFilter.value];

  return customers.value.filter(customer => {
    // Ensure customer is inside of the risk range
    const inRiskRange = customer.probability > low && customer.probability <= high;

    // Ensure the intervention is matched correctly
    const interventionMatch =
      interventionOption === null ||
      (interventionOption === true && customer.interventionCount > 0) ||
      (interventionOption === false && customer.interventionCount === 0);

    // return respective match
    return inRiskRange && interventionMatch;
  }).sort((cA, cB) => cB.probability - cA.probability);
});

</script>

<template>
  <div class="grid grid-cols-1 gap-4 p-4">
    <!-- Left main section -->
    <div class="space-y-4">
      <div class="p-4 bg-white shadow rounded-2xl min-h-[396px]">
        <div class="flex items-center justify-between mb-4">
          <div>
            <div class="text-sm text-gray-500">Overview</div>
            <h2 class="text-lg font-semibold">Proactive Customer Retention Dashboard</h2>
          </div>
          <div class="flex gap-6 text-right">
            <div>
              <div class="text-sm text-gray-500">Total customers</div>
              <div class="text-xl font-bold">{{ dashboardSummary?.totalCount }}</div>
            </div>
            <div>
              <div class="text-sm text-gray-500">High-risk customers</div>
              <div class="text-xl font-bold">
                {{ dashboardSummary?.highProbCount }}
              </div>
            </div>
            <div>
              <div class="text-sm text-gray-500">Predicted churn rate</div>
              <div class="text-xl font-bold text-emerald-600"
                :class="{ 'text-red-600': Math.round((dashboardSummary?.highProbCount / dashboardSummary?.totalCount) * 100) > 75 }">
                {{
                  Math.round((dashboardSummary?.highProbCount / dashboardSummary?.totalCount) * 100) || '--'
                }}%
              </div>
            </div>
          </div>
        </div>
        <div class="grid items-center grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div class="sm:col-span-2">
            <div v-if="isLoading">
              <div class="w-full h-64 bg-gray-200 rounded-lg animate-pulse"></div>
              <div class="w-1/2 h-4 mx-auto mt-2 bg-gray-200 rounded-md animate-pulse"></div>
            </div>
            <BarChart :chart-data="chartData" v-else class="w-full" />
          </div>
          <div>
            <div v-if="isLoading">
              <div class="mx-auto bg-gray-200 rounded-full size-60 animate-pulse"></div>
              <div class="w-1/2 h-4 mx-auto mt-2 bg-gray-200 rounded-md animate-pulse"></div>
            </div>

            <PieChart :chart-data="churnBreakdown" v-else />
          </div>
          <div>
            <div v-if="isLoading">
              <div class="mx-auto bg-gray-200 rounded-full size-60 animate-pulse"></div>
              <div class="w-1/2 h-4 mx-auto mt-2 bg-gray-200 rounded-md animate-pulse"></div>
            </div>

            <PieChart :chart-data="interventionBreakdown" v-else />
          </div>
        </div>
      </div>

      <div class="p-4 bg-white shadow rounded-2xl">
        <div class="grid lg:grid-cols-3 gap-x-4 gap-y-8">
          <div class=" lg:pr-4 lg:border-r lg:border-gray-300">
            <h6 class="mb-3 font-semibold">Filter Current Results</h6>
            <div class="grid grid-cols-2 gap-4 lg:grid-cols-1">
              <div>
                <span class="block text-sm font-semibold">Churn Risk</span>
                <span class="block mb-2 text-xs font-semibold text-gray-500">Risk of the customer churning.</span>
                <select name="risk" class="w-full px-2 py-1 text-sm bg-gray-200 rounded-md" v-model="churnRiskFilter">
                  <option value="all">All Risks</option>
                  <option value="high">High Risk (> 75%)</option>
                  <option value="medium">Medium Risk (20% - 75%)</option>
                  <option value="low">Low Risk (< 20%)</option>
                </select>
              </div>
              <div>
                <span class="block text-sm font-semibold">Intervened</span>
                <span class="block mb-2 text-xs font-semibold text-gray-500">Actions taken to reduce churn.</span>
                <select name="reason" class="w-full px-2 py-1 text-sm bg-gray-200 rounded-md"
                  v-model="interventionFilter">
                  <option value="all">Any</option>
                  <option value="true">Interventions Taken</option>
                  <option value="false">No Interventions</option>
                </select>
              </div>
            </div>
          </div>
          <div class="lg:col-span-2">
            <div class="flex items-center mb-3">
              <h6 class="flex-1 font-semibold">Customers</h6>
              <span class="px-2 py-1 text-xs font-semibold text-blue-600 rounded-full bg-blue-50">
                Showing {{ filteredCustomers?.length }} of {{ dashboardSummary?.totalCount }}
              </span>
              <button
                class="px-2 py-1 ml-4 text-xs text-blue-600 bg-blue-50 rounded-xl active:bg-blue-200 hover:bg-blue-100 duration-50 hover:cursor-pointer"
                @click="$router.push('/customers')">
                View All
              </button>
            </div>

            <div class="overflow-auto max-h-80">
              <table class="w-full text-sm" v-if="filteredCustomers?.length">
                <thead class="text-xs text-gray-500 border-b border-gray-300">
                  <tr class="text-left">
                    <th class="py-2">Customer</th>
                    <th>Score</th>
                    <th>Satisfaction Score</th>
                    <th>Contract Type</th>
                    <th>Interventions</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-300">
                  <tr v-for="customer, index in filteredCustomers" :key="index">
                    <td>
                      <strong class="block">{{ customer.name }}</strong>
                      <span class="text-xs text-gray-400">{{ String(customer.id).padStart(3, "0") }}</span>
                    </td>
                    <td class="text-emerald-600" :class="{ 'text-rose-600': customer.probability > 0.75 }">
                      <div class="flex items-center gap-x-1">
                        <span class="size-1.5 rounded-full block bg-emerald-600"
                          :class="{ 'bg-rose-600': customer.probability > 0.75 }"></span>
                        <span>{{ Math.round((customer.probability * 100) * 100) / 100 }}%</span>
                      </div>
                    </td>
                    <td><span>{{ customer.satisfactionScore }}</span></td>
                    <td><span class="capitalize">{{ customer.contractType }}</span></td>
                    <td>{{ customer.interventionCount }}</td>
                    <td>
                      <button
                        class="px-2 py-1 text-sm text-blue-600 bg-blue-50 rounded-xl active:bg-blue-200 hover:bg-blue-100 duration-50 hover:cursor-pointer"
                        @click="$router.push(`/customer/${customer.id}`)">
                        Open
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-else class="flex items-center justify-center h-40">
                <span class="text-sm text-gray-400">
                  No customers found, maybe try different filters?
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>