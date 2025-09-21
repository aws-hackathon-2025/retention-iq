export const fetchUrl = async (
  url,
  method,
  headers,
  isLoading = null,
  body = null
) => {
  try {
    if (isLoading) isLoading.value = true;
    const res = await fetch(url, { method, headers, body });
    const data = await res.json();
    return data;
  } catch (e) {
    alert(e);
  } finally {
    if (isLoading) isLoading.value = false;
  }
};
