<template>
  <div class="p-6">
    <!-- Header -->
    <div class="flex items-center mb-6">
      <h2 class="flex-1 text-xl font-semibold">All Customers</h2>
      <span class="px-3 py-1 text-xs font-semibold text-blue-600 rounded-full bg-blue-50">
        Showing {{ customers.length }} customers
      </span>
    </div>

    <!-- Customers Table -->
    <div class="overflow-auto">
      <table
        v-if="customers.length"
        class="w-full text-sm border border-gray-200 rounded-lg shadow-sm"
      >
        <thead class="text-xs text-gray-500 border-b border-gray-300 bg-gray-50">
          <tr class="text-left">
            <th class="py-2 px-3">Customer</th>
            <th class="px-3">Score</th>
            <th class="px-3">Satisfaction Score</th>
            <th class="px-3">Contract Type</th>
            <th class="px-3">Interventions</th>
            <th class="px-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr
            v-for="user in customers"
            :key="user.id"
            class="hover:bg-gray-50"
          >
            <td class="py-2 px-3">
              <strong class="block">{{ user.name }}</strong>
              <span class="text-xs text-gray-400">
                {{ String(user.id).padStart(3, "0") }}
              </span>
            </td>
            <td
              class="px-3 text-emerald-600"
              :class="{ 'text-rose-600': user.probability > 0.75 }"
            >
              <div class="flex items-center gap-x-1">
                <span
                  class="size-1.5 rounded-full block bg-emerald-600"
                  :class="{ 'bg-rose-600': user.probability > 0.75 }"
                ></span>
                <span>{{ Math.round(user.probability * 10000) / 100 }}%</span>
              </div>
            </td>
            <td class="px-3">
              <span>{{ user.satisfactionScore }}</span>
            </td>
            <td class="px-3">
              <span class="capitalize">{{ user.contractType }}</span>
            </td>
            <td class="px-3">{{ user.interventionCount }}</td>
            <td class="px-3">
              <button
                class="px-2 py-1 text-sm text-blue-600 bg-blue-50 rounded-xl active:bg-blue-200 hover:bg-blue-100 duration-50 hover:cursor-pointer"
              >
                Open
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div
        v-else
        class="flex items-center justify-center h-40"
      >
        <span class="text-sm text-gray-400">
          No customers found.
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from "vue";

// State
const customers = ref([
  // Example data (replace with API later)
  {
    id: 1,
    name: "Pamela Lyon",
    probability: 0.0014,
    satisfactionScore: 3,
    contractType: "two year",
    interventionCount: 0,
  },
  {
    id: 2,
    name: "Dustin Shaw",
    probability: 0.1,
    satisfactionScore: 3,
    contractType: "one year",
    interventionCount: 0,
  },
]);
</script>
