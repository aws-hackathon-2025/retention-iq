export const fetchUrl = async (url, method, headers, isLoading) => {
  try {
    isLoading.value = true;
    const res = await fetch(url, { method, headers });
    const data = await res.json();
    return data;
  } catch (e) {
    alert(e);
  } finally {
    isLoading.value = false;
  }
};
