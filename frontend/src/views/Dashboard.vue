<script setup>
import { computed, ref, watch } from 'vue';
import { fetchUrl } from '../composables/fetchUrl';
import BarChart from '../components/charts/BarChart.vue';
import PieChart from '../components/charts/PieChart.vue';

const users = ref([]);

const totalUserCount = ref(0);
const highRiskUserCount = ref(0);
const satisfactionCounts = ref({});
const riskCounts = ref({});
const interventionCounts = ref({});
const isLoading = ref(false);

(async () => {
  // Update isloading
  isLoading.value = true;

  // Create a fetch request for dashboard summary
  const dashboardHeaders = new Headers();
  dashboardHeaders.append("x-api-key", import.meta.env.VITE_API_KEY);
  const dashboardFetch = fetchUrl(import.meta.env.VITE_DASHBOARD_SUMMARY_ENDPOINT, "GET", dashboardHeaders);

  // Create a fetch request for users
  const userHeaders = new Headers();
  userHeaders.append("x-api-key", import.meta.env.VITE_API_KEY);
  const usersFetch = fetchUrl(import.meta.env.VITE_GET_CUSTOMERS_ENDPOINT + "?skip=0&limit=5", "GET", userHeaders);

  // Collect all results
  const [dashboardRaw, usersRaw] = await Promise.all([dashboardFetch, usersFetch]);

  // Update users
  console.log(usersRaw.body);
  const userData = JSON.parse(usersRaw.body);
  users.value = userData;

  // Update dashboard details
  const data = JSON.parse(dashboardRaw.body);
  totalUserCount.value = data.totalCount;
  highRiskUserCount.value = data.highProbCount;
  satisfactionCounts.value = data.satisfactionCounts;
  riskCounts.value = data.riskCounts;
  interventionCounts.value = data.interventionCounts;

  // Update isloading
  isLoading.value = false;
})();

const chartData = ref({
  labels: [1, 2, 3, 4, 5],
  datasets: []
});

const churnBreakdown = ref({
  labels: ["Low Risk", "Medium Risk", "High Risk"],
  datasets: []
});

const interventionBreakdown = ref({
  labels: ["No Interventions Taken", "Interventions Taken"],
  datasets: []
});

watch(satisfactionCounts, (newVal) => {
  chartData.value = {
    labels: [1, 2, 3, 4, 5],
    datasets: [
      {
        label: "Number of Customers",
        backgroundColor: "#3b82f6",
        data: Object.values(newVal)
      }
    ]
  };
});

watch(riskCounts, (newVal) => {
  churnBreakdown.value = {
    labels: ["Low Risk", "Medium Risk", "High Risk"],
    datasets: [
      {
        data: [newVal["Low Risk"], newVal["Medium Risk"], newVal["High Risk"]],
        backgroundColor: ["#1E3A8A", "#93C5FD", "#E5E7EB"]
      }
    ]
  };
});

watch(interventionCounts, (newVal) => {
  console.log(newVal);
  interventionBreakdown.value = {
    labels: ["No Interventions Taken", "Interventions Taken"],
    datasets: [
      {
        data: [newVal["noInterventionCount"], newVal["interventionCount"]],
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

const filterUsers = computed(() => {
  // return users.value;
  const { low, high } = churnRiskRanges[churnRiskFilter.value];
  const interventionOption = interventionMapper[interventionFilter.value];

  return users.value.filter(user => {
    // Ensure user is inside of the risk range
    const inRiskRange = user.probability > low && user.probability <= high;

    // Ensure the intervention is matched correctly
    const interventionMatch =
      interventionOption === null ||
      (interventionOption === true && user.interventionCount > 0) ||
      (interventionOption === false && user.interventionCount === 0);

    // return respective match
    return inRiskRange && interventionMatch;
  });
});

watch(filterUsers, (newVal) => {
  console.log(newVal);
})

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
              <div class="text-xl font-bold">{{ totalUserCount }}</div>
            </div>
            <div>
              <div class="text-sm text-gray-500">High-risk customers</div>
              <div class="text-xl font-bold">
                {{ highRiskUserCount }}
              </div>
            </div>
            <div>
              <div class="text-sm text-gray-500">Predicted churn rate</div>
              <div class="text-xl font-bold text-emerald-600"
                :class="{ 'text-red-600': Math.round((highRiskUserCount / totalUserCount) * 100) > 75 }">
                {{ Math.round((highRiskUserCount / totalUserCount) * 100) }}%
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
                Showing {{ filterUsers.length }} of {{ totalUserCount }}
              </span>
              <button
                class="px-2 py-1 ml-4 text-xs text-blue-600 bg-blue-50 rounded-xl active:bg-blue-200 hover:bg-blue-100 duration-50 hover:cursor-pointer">View
                All</button>
            </div>

            <div class="overflow-auto max-h-80">
              <table class="w-full text-sm" v-if="filterUsers.length">
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
                  <tr v-for="user, index in filterUsers" :key="index">
                    <td>
                      <strong class="block">{{ user.name }}</strong>
                      <span class="text-xs text-gray-400">{{ String(user.id).padStart(3, "0") }}</span>
                    </td>
                    <td class="text-emerald-600" :class="{ 'text-rose-600': user.probability > 0.75 }">
                      <div class="flex items-center gap-x-1">
                        <span class="size-1.5 rounded-full block bg-emerald-600"
                          :class="{ 'bg-rose-600': user.probability > 0.75 }"></span>
                        <span>{{ Math.round((user.probability * 100) * 100) / 100 }}%</span>
                      </div>
                    </td>
                    <td><span>{{ user.satisfactionScore }}</span></td>
                    <td><span class="capitalize">{{ user.contractType }}</span></td>
                    <td>{{ user.interventionCount }}</td>
                    <td>
                      <button
                        class="px-2 py-1 text-sm text-blue-600 bg-blue-50 rounded-xl active:bg-blue-200 hover:bg-blue-100 duration-50 hover:cursor-pointer">Open</button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-else class="flex items-center justify-center h-40">
                <span class="text-sm text-gray-400">
                  No users found, maybe try different filters?
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>