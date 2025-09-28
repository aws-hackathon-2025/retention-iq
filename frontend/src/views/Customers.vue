<script setup>
import { computed, ref } from "vue";

// --- Dummy customers ---
const customers = ref([
  { id: 1, name: "Alice", probability: 0.8, satisfactionScore: 2, contractType: "monthly", interventionCount: 1 },
  { id: 2, name: "Bob", probability: 0.3, satisfactionScore: 4, contractType: "yearly", interventionCount: 0 },
  { id: 3, name: "Charlie", probability: 0.6, satisfactionScore: 3, contractType: "monthly", interventionCount: 2 },
  { id: 4, name: "Diana", probability: 0.15, satisfactionScore: 5, contractType: "yearly", interventionCount: 0 },
  { id: 5, name: "Ethan", probability: 0.9, satisfactionScore: 1, contractType: "monthly", interventionCount: 3 },
  { id: 6, name: "Fiona", probability: 0.25, satisfactionScore: 4, contractType: "yearly", interventionCount: 0 },
  { id: 7, name: "George", probability: 0.55, satisfactionScore: 3, contractType: "monthly", interventionCount: 1 },
  { id: 8, name: "Hannah", probability: 0.05, satisfactionScore: 5, contractType: "yearly", interventionCount: 0 }
]);

const isLoading = ref(false);
const isLoadingMore = ref(false);

const churnRiskFilter = ref("all");
const interventionFilter = ref("all");
const sortFilter = ref("risk");
const sortDirection = ref("ascending");

const churnRiskRanges = {
  all: { low: 0, high: 1 },
  high: { low: 0.75, high: 1 },
  medium: { low: 0.2, high: 0.75 },
  low: { low: 0, high: 0.2 }
};
const interventionMapper = {
  all: null,
  true: true,
  false: false
};
const sortingFunctions = {
  id(cA, cB) {
    return sortDirection.value === "ascending"
      ? cB.id - cA.id
      : cA.id - cB.id;
  },
  risk(cA, cB) {
    return sortDirection.value === "ascending"
      ? cB.probability - cA.probability
      : cA.probability - cB.probability;
  },
  satisfaction(cA, cB) {
    return sortDirection.value === "ascending"
      ? cB.satisfactionScore - cA.satisfactionScore
      : cA.satisfactionScore - cB.satisfactionScore;
  },
  interventions(cA, cB) {
    return sortDirection.value === "ascending"
      ? cB.interventionCount - cA.interventionCount
      : cA.interventionCount - cB.interventionCount;
  }
};

const filteredCustomers = computed(() => {
  if (!customers.value) return customers.value;

  const { low, high } = churnRiskRanges[churnRiskFilter.value];
  const interventionOption = interventionMapper[interventionFilter.value];

  const filtered = customers.value.filter(customer => {
    const inRiskRange =
      customer.probability > low && customer.probability <= high;
    const interventionMatch =
      interventionOption === null ||
      (interventionOption === true && customer.interventionCount > 0) ||
      (interventionOption === false && customer.interventionCount === 0);

    return inRiskRange && interventionMatch;
  });

  const sortFn = sortingFunctions[sortFilter.value];
  return filtered.sort(sortFn);
});

// --- Dummy load more just appends more fake users ---
const loadMoreUsers = async () => {
  isLoadingMore.value = true;
  await new Promise(resolve => setTimeout(resolve, 500)); // fake delay
  const nextId = customers.value.length + 1;
  customers.value = [
    ...customers.value,
    { id: nextId, name: `User${nextId}`, probability: Math.random(), satisfactionScore: Math.ceil(Math.random() * 5), contractType: Math.random() > 0.5 ? "monthly" : "yearly", interventionCount: Math.floor(Math.random() * 3) }
  ];
  isLoadingMore.value = false;
};
</script>


<template>
  <div class="p-6">
    <!-- Filters -->
    <div class="p-4 mb-4 bg-gray-100 rounded-md">
      <div>
        <h6 class="mb-3 text-xl font-semibold">Filters and Sorting</h6>
      </div>
      <div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
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
          <select name="reason" class="w-full px-2 py-1 text-sm bg-gray-200 rounded-md">
            <option value="all">Any</option>
            <option value="true">Interventions Taken</option>
            <option value="false">No Interventions</option>
          </select>
        </div>
        <div>
          <span class="block text-sm font-semibold">Sorting Property</span>
          <span class="block mb-2 text-xs font-semibold text-gray-500">What property to sort on.</span>
          <select name="reason" class="w-full px-2 py-1 text-sm bg-gray-200 rounded-md" v-model="sortFilter">
            <option value="id">Customer ID</option>
            <option value="risk">Churn Probability</option>
            <option value="satisfaction">Satisfaction Score</option>
            <option value="interventions">Number of Interventions</option>
          </select>
        </div>
        <div>
          <span class="block text-sm font-semibold">Sorting Direction</span>
          <span class="block mb-2 text-xs font-semibold text-gray-500">Which direction to sort in.</span>
          <select name="reason" class="w-full px-2 py-1 text-sm bg-gray-200 rounded-md" v-model="sortDirection">
            <option value="ascending">Ascending</option>
            <option value="descending">Descending</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Header -->
    <div class="flex items-center mb-6">
      <h2 class="flex-1 text-xl font-semibold">All Customers</h2>
      <span class="px-3 py-1 text-xs font-semibold text-blue-600 rounded-full bg-blue-50">
        Showing {{ customers?.length }} customers
      </span>
    </div>

    <!-- Customers Table -->
    <div class="overflow-auto">
      <table v-if="!isLoading" class="w-full text-sm border border-gray-200 rounded-lg shadow-sm">
        <thead class="text-xs text-gray-500 border-b border-gray-300 bg-gray-50">
          <tr class="text-left">
            <th class="px-3 py-2">Customer</th>
            <th class="px-3">Score</th>
            <th class="px-3">Satisfaction Score</th>
            <th class="px-3">Contract Type</th>
            <th class="px-3">Interventions</th>
            <th class="px-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="customer in filteredCustomers" :key="customer.id" class="hover:bg-gray-50">
            <td class="px-3 py-2">
              <strong class="block">{{ customer.name }}</strong>
              <span class="text-xs text-gray-400">
                {{ String(customer.id).padStart(3, "0") }}
              </span>
            </td>
            <td class="px-3 text-emerald-600" :class="{ 'text-rose-600': customer.probability > 0.75 }">
              <div class="flex items-center gap-x-1">
                <span class="size-1.5 rounded-full block bg-emerald-600"
                  :class="{ 'bg-rose-600': customer.probability > 0.75 }"></span>
                <span>{{ Math.round(customer.probability * 10000) / 100 }}%</span>
              </div>
            </td>
            <td class="px-3">
              <span>{{ customer.satisfactionScore }}</span>
            </td>
            <td class="px-3">
              <span class="capitalize">{{ customer.contractType }}</span>
            </td>
            <td class="px-3">{{ customer.interventionCount }}</td>
            <td class="px-3">
              <button
                class="px-2 py-1 text-sm text-blue-600 bg-blue-50 rounded-xl active:bg-blue-200 hover:bg-blue-100 duration-50 hover:cursor-pointer"
                @click="$router.push(`/customer/${customer.id}`)">
                Open
              </button>
            </td>
          </tr>
        </tbody>
      </table>


      <!-- Empty State -->
      <div v-else class="flex items-center justify-center h-40">
        <span class="text-sm text-gray-400">
          Loading Customers...
        </span>
      </div>

      <button v-if="!isLoadingMore && !isLoading"
        class="block px-2 py-1 mx-auto mt-8 text-sm text-blue-600 bg-blue-50 rounded-xl active:bg-blue-200 hover:bg-blue-100 duration-50 hover:cursor-pointer"
        @click="(async () => await loadMoreUsers())">
        Load More
      </button>
      <div class="py-1 mt-8 text-sm text-center text-gray-400" v-else v-if="!isLoading">
        Loading customers...
      </div>
    </div>
  </div>
</template>
