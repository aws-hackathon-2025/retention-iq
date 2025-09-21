<script setup>
import { fetchUrl } from "../composables/fetchUrl.js";
import { computed, ref } from "vue";
import { useRoute } from "vue-router";

const isLoading = ref(false);

const customer = ref({});
const route = useRoute();

(async () => {
  isLoading.value = true;
  const customerHeaders = new Headers();
  customerHeaders.append("x-api-key", import.meta.env.VITE_API_KEY);
  const customerRaw = await fetchUrl(import.meta.env.VITE_GET_CUSTOMER_ENDPOINT + `?id=${route.params.id}`, "GET", customerHeaders);
  customer.value = JSON.parse(customerRaw.body);
  isLoading.value = false;
})();

// Form copy (so editing doesn’t mutate original immediately)
const editedCustomer = computed(() => {
  return { ...customer.value };
});

// Fake prediction result
const prediction = ref(null);

// intervention type
const interventionType = ref(null);

const creatingIntervention = ref(false);

const predictChurn = async () => {
  const queryString = new URLSearchParams(editedCustomer.value).toString();
  const customerHeaders = new Headers();
  customerHeaders.append("x-api-key", import.meta.env.VITE_API_KEY);
  const predictionRaw = await fetchUrl(import.meta.env.VITE_GET_PREDICTION_ENDPOINT + `?${queryString}`, "GET", customerHeaders);
  prediction.value = JSON.parse(predictionRaw.body);
  console.log(prediction.value);
}

const updateInterventionType = async (type) => {
  interventionType.value = type;
  await createIntervention();
}

const createIntervention = async () => {
  creatingIntervention.value = true;
  const customerHeaders = new Headers();
  const body = {
    id: customer.value.id,
    emailType: interventionType.value
  }
  customerHeaders.append("x-api-key", import.meta.env.VITE_API_KEY);
  customerHeaders.append("Content-Type", "application/json");
  const predictionRaw = await fetchUrl(import.meta.env.VITE_CREATE_INTERVENTION_ENDPOINT, "POST", customerHeaders, null, JSON.stringify(body));
  const resultMessage = JSON.parse(predictionRaw.body)?.message;
  alert(resultMessage);

  creatingIntervention.value = false;
}

const formatPercentage = (prob) => {
  return prob ? `${Math.round((prob * 100) * 100) / 100}%` : "N/A";
}
</script>

<template>
  <div class="p-4" v-if="!isLoading">
    <!-- Customer Details -->
    <div class="space-y-8">
      <!-- Main details -->
      <div class="grid gap-6 p-4 bg-gray-100 rounded-md lg:grid-cols-3">
        <div class="col-span-2">
          <h2 class="mb-4 text-xl font-semibold">Customer Details</h2>
          <div class="grid grid-cols-2 text-sm gap-y-3 gap-x-6">
            <div>
              <span class="block text-gray-500">Name</span>
              <span class="font-medium">{{ customer.name }}</span>
            </div>
            <div>
              <span class="block text-gray-500">ID</span>
              <span class="font-mono">#{{ String(customer.id).padStart(3, "0") }}</span>
            </div>
            <div>
              <span class="block text-gray-500">Contract Type</span>
              <span class="capitalize">{{ customer.contractType }}</span>
            </div>
            <div>
              <span class="block text-gray-500">Satisfaction Score</span>
              <span>{{ customer.satisfactionScore }}</span>
            </div>
            <div>
              <span class="block text-gray-500">Monthly Charge</span>
              <span>${{ customer.monthlyCharge }}</span>
            </div>
            <div>
              <span class="block text-gray-500">Total Revenue</span>
              <span>${{ customer.totalRevenue }}</span>
            </div>
          </div>
        </div>
        <div class="border-t border-gray-300 lg:pl-6 lg:border-t-0 lg:border-l">
          <h2 class="mb-4 text-xl font-semibold">Churn Overview</h2>
          <div class="space-y-2 text-sm">
            <div>
              <span class="block text-gray-500">Churn Probability</span>
              <span class="font-medium" :class="{ 'text-rose-600': customer.probability > 0.75 }">
                {{ formatPercentage(customer.probability) }}
              </span>
            </div>
            <div>
              <span class="block text-gray-500">Actually Churned?</span>
              <span class="font-medium"
                :class="{ 'text-rose-600': customer.churn === 1, 'text-emerald-600': customer.churn === 0 }">
                {{ customer.churn === 1 ? "Yes" : "No" }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Predict New Churn -->
      <div class="p-4 bg-gray-100 rounded-md">
        <h2 class="mb-4 text-xl font-semibold">Predict New Churn</h2>
        <div class="grid gap-6 md:grid-cols-2">
          <div>
            <label class="block text-sm font-medium text-gray-600">ID</label>
            <input :value="String(editedCustomer.id).padStart(3, '0')" type="text" disabled
              class="w-full px-3 py-2 mt-1 text-sm text-gray-500 duration-100 bg-gray-200 border-2 border-transparent rounded-lg outline-none focus:border-primary" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600">Name</label>
            <input :value="editedCustomer.name" type="text" disabled
              class="w-full px-3 py-2 mt-1 text-sm text-gray-500 duration-100 bg-gray-200 border-2 border-transparent rounded-lg outline-none focus:border-primary" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600">Contract Type</label>
            <select v-model="editedCustomer.contractType"
              class="w-full px-3 py-2 mt-1 text-sm duration-100 bg-gray-200 border-2 border-transparent rounded-lg outline-none focus:border-primary">
              <option value="monthly">Monthly</option>
              <option value="one year">One Year</option>
              <option value="two year">Two Year</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600">Satisfaction Score</label>
            <input v-model.number="editedCustomer.satisfactionScore" type="number" min="1" max="5"
              class="w-full px-3 py-2 mt-1 text-sm duration-100 bg-gray-200 border-2 border-transparent rounded-lg outline-none focus:border-primary" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600">Monthly Charge</label>
            <input v-model.number="editedCustomer.monthlyCharge" type="number" step="0.01"
              class="w-full px-3 py-2 mt-1 text-sm duration-100 bg-gray-200 border-2 border-transparent rounded-lg outline-none focus:border-primary invalid:!border-rose-600" />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-600">Total Revenue</label>
            <input v-model.number="editedCustomer.totalRevenue" type="number" step="0.01"
              class="w-full px-3 py-2 mt-1 text-sm duration-100 bg-gray-200 border-2 border-transparent rounded-lg outline-none focus:border-primary invalid:!border-rose-600" />
          </div>
        </div>

        <!-- Predict Button -->
        <div class="mt-6">
          <button @click="(async () => await predictChurn())()"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-xl hover:bg-blue-700 active:bg-blue-800">
            Predict Churn
          </button>
        </div>

        <!-- Prediction Result -->
        <div v-if="prediction !== null" class="flex flex-col gap-4 mt-4 text-sm md:flex-row">
          <div class="w-full p-4 border md:w-1/2 rounded-xl bg-blue-50">
            <span class="block font-semibold text-blue-700">Churn Probability</span>
            <span class="text-lg font-bold" :class="{
              'text-rose-600': customer.probability > 75,
              'text-emerald-600': customer.probability <= 20,
            }">
              {{ formatPercentage(customer.probability) }}
            </span>
          </div>
          <div class="w-full p-4 border md:w-1/2 rounded-xl bg-blue-50">
            <span class="block font-semibold text-blue-700">New Churn Probability</span>
            <span class="text-lg font-bold" :class="{
              'text-rose-600': prediction > 75,
              'text-emerald-600': prediction <= 20,
            }">
              {{ formatPercentage(prediction) }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Intervention Suggestions -->
    <div class="p-4 bg-gray-100 rounded-md mt-8">
      <h2 class="mb-4 text-xl font-semibold">Interventions Suggestions</h2>
      <div class="flex flex-col gap-4 md:flex-row">
        <div @click="(async () => updateInterventionType('support'))()"
          class="flex items-center justify-center w-full h-32 p-4 duration-100 bg-white border-2 border-gray-200 rounded-md md:w-1/2 hover:cursor-pointer hover:border-primary"
          :class="{ '!bg-gray-200': creatingIntervention }">
          Send a Support Email
        </div>
        <div @click="(async () => updateInterventionType('discount'))()"
          class="flex items-center justify-center w-full h-32 p-4 duration-100 bg-white border-2 border-gray-200 rounded-md md:w-1/2 hover:cursor-pointer hover:border-primary"
          :class="{ '!bg-gray-200': creatingIntervention }">
          Send a 20% Discount
        </div>
      </div>
    </div>
  </div>
  <div class="p-4 text-center text-gray-400" v-else>
    Loading customer details...
  </div>
</template>
