<script setup>
import { computed, ref } from 'vue';

const users = [
  {
    id: "C001",
    email: "maya@example.com",
    name: "Maya Wong",
    tenureMonths: 36,
    monthlyCharge: 89.99,
    satisfactionScore: 3,
    premiumFeatures: true,
    seniorCitizen: false,
    contractMonthToMonth: true,
    contractOneYear: false,
    contractTwoYearsPlus: false,
    married: true,
    dependents: 0,
    churnProbability: 0.82, // predicted by model
    reason: "Low satisfaction score, frequent billing issues.",
    interventions: [
      { type: "discount", value: "20%", date: "2025-08-20" },
      { type: "support_call", value: "resolved billing issue", date: "2025-09-05" }
    ],
  },
  {
    id: "C002",
    email: "liam@example.com",
    name: "Liam Tan",
    tenureMonths: 12,
    monthlyCharge: 59.99,
    satisfactionScore: 4,
    premiumFeatures: false,
    seniorCitizen: false,
    contractMonthToMonth: true,
    contractOneYear: false,
    contractTwoYearsPlus: false,
    married: false,
    dependents: 0,
    churnProbability: 0.65,
    reason: "Medium satisfaction score, short tenure.",
    interventions: [
      { type: "coupon", value: "15%", date: "2025-09-01" }
    ],
  },
  {
    id: "C003",
    email: "aisha@example.com",
    name: "Aisha Rahman",
    tenureMonths: 5,
    monthlyCharge: 39.99,
    satisfactionScore: 5,
    premiumFeatures: false,
    seniorCitizen: false,
    contractMonthToMonth: false,
    contractOneYear: true,
    contractTwoYearsPlus: false,
    married: true,
    dependents: 2,
    churnProbability: 0.22,
    reason: "High satisfaction score, short tenure.",
    interventions: [],
  },
  {
    id: "C004",
    email: "david@example.com",
    name: "David Lee",
    tenureMonths: 60,
    monthlyCharge: 120.00,
    satisfactionScore: 5,
    premiumFeatures: true,
    seniorCitizen: true,
    contractMonthToMonth: false,
    contractOneYear: false,
    contractTwoYearsPlus: true,
    married: true,
    dependents: 1,
    churnProbability: 0.12,
    reason: "Long tenure, high satisfaction score, senior citizen.",
    interventions: [
      { type: "loyalty_reward", value: "Free upgrade", date: "2025-08-15" }
    ],
  },
  {
    id: "C005",
    email: "sophia@example.com",
    name: "Sophia Chen",
    tenureMonths: 24,
    monthlyCharge: 75.50,
    satisfactionScore: 1,
    premiumFeatures: true,
    seniorCitizen: false,
    contractMonthToMonth: true,
    contractOneYear: false,
    contractTwoYearsPlus: false,
    married: false,
    dependents: 0,
    churnProbability: 0.91,
    reason: "Very low satisfaction score, frequent complaints.",
    interventions: [
      { type: "support_call", value: "follow-up on complaints", date: "2025-09-03" }
    ],
  },
];

const truncate = (text, max = 50) => {
  const trimmed = text.substring(0, max + 1);
  return text.length > max ? trimmed + '...' : trimmed;
};

const highRiskUserCount = users.reduce((acc, user) => user.churnProbability > 0.75 ? acc + 1 : acc, 0);

const churnRiskFilter = ref('all');
const interventionFilter = ref('all');

const churnRiskRanges = {
  'all': { low: 0, high: 1 },
  'high': { low: 0.75, high: 1 },
  'medium': { low: 0.5, high: 0.75 },
  'low': { low: 0, high: 0.5 }
};
const interventionMapper = {
  'all': null,
  'true': true,
  'false': false,
};

const filterUsers = computed(() => {
  const { low, high } = churnRiskRanges[churnRiskFilter.value];
  const interventionOption = interventionMapper[interventionFilter.value];

  return users.filter(user => {
    // Ensure user is inside of the risk range
    const inRiskRange = user.churnProbability > low && user.churnProbability <= high;

    // Ensure the intervention is matched correctly
    const interventionMatch =
      interventionOption === null ||
      (interventionOption === true && user.interventions.length > 0) ||
      (interventionOption === false && user.interventions.length === 0);

    // return respective match
    return inRiskRange && interventionMatch;
  });
});

</script>

<template>
  <div class="grid grid-cols-1 gap-4 p-4">
    <!-- Left main section -->
    <div class="space-y-4">
      <div class="p-4 bg-white shadow rounded-2xl">
        <div class="flex items-center justify-between mb-4">
          <div>
            <div class="text-sm text-gray-500">Overview</div>
            <h2 class="text-lg font-semibold">Proactive Customer Retention Dashboard</h2>
          </div>
          <div class="flex gap-6 text-right">
            <div>
              <div class="text-sm text-gray-500">Total customers</div>
              <div class="text-xl font-bold">{{ users.length }}</div>
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
                :class="{ 'text-red-600': Math.round((highRiskUserCount / users.length) * 100) > 75 }">
                {{ Math.round((highRiskUserCount / users.length) * 100) }}%
              </div>
            </div>
          </div>
        </div>
        <div class="grid items-center grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div class="flex items-center justify-center h-48 text-gray-400 bg-gray-100 rounded-lg sm:col-span-2">
            [Chart Placeholder]
          </div>
          <div class="flex items-center justify-center h-48 p-3 text-gray-400 bg-gray-100 rounded-xl">
            [Chart Placeholder]
          </div>
          <div class="flex items-center justify-center h-48 p-3 text-gray-400 bg-gray-100 rounded-xl">
            [Chart Placeholder]
          </div>
        </div>
      </div>

      <div class="p-4 bg-white shadow rounded-2xl">
        <div class="grid lg:grid-cols-3 gap-x-4 gap-y-8">
          <div class=" lg:pr-4 lg:border-r lg:border-gray-300">
            <h6 class="mb-3 font-semibold">Filters</h6>
            <div class="grid grid-cols-2 gap-4 lg:grid-cols-1">
              <div>
                <span class="block text-sm font-semibold">Churn Risk</span>
                <span class="block mb-2 text-xs font-semibold text-gray-500">Risk of the customer churning.</span>
                <select name="risk" class="w-full px-2 py-1 text-sm bg-gray-200 rounded-md" v-model="churnRiskFilter">
                  <option value="all">All Risks</option>
                  <option value="high">High Risk (> 75%)</option>
                  <option value="medium">Medium Risk (50% - 75%)</option>
                  <option value="low">Low Risk (< 50%)</option>
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
            <div class="flex items-center justify-between mb-3">
              <h6 class="font-semibold">Customers</h6>
              <span class="px-2 py-1 text-xs font-semibold text-blue-600 rounded-full bg-blue-50">Auto-scored</span>
            </div>

            <div class="overflow-auto max-h-80">
              <table class="w-full text-sm" v-if="filterUsers.length">
                <thead class="text-xs text-gray-500 border-b border-gray-300">
                  <tr class="text-left">
                    <th class="py-2">Customer</th>
                    <th>Score</th>
                    <th>Reason</th>
                    <th>Interventions</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody class="divide-y divide-gray-300">
                  <tr v-for="user, index in filterUsers" :key="index">
                    <td>
                      <strong class="block">{{ user.name }}</strong>
                      <span class="text-xs text-gray-400">{{ user.email }}</span>
                    </td>
                    <td class="text-emerald-600" :class="{ 'text-rose-600': user.churnProbability > 0.75 }">
                      <div class="flex items-center gap-x-1">
                        <span class="size-1.5 rounded-full block bg-emerald-600"
                          :class="{ 'bg-rose-600': user.churnProbability > 0.75 }"></span>
                        <span>{{ user.churnProbability * 100 }}%</span>
                      </div>
                    </td>
                    <td><span>{{ truncate(user.reason, 50) }}</span></td>
                    <td>{{ user.interventions[0]?.type || "None" }}</td>
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