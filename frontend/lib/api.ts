const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function safeFetch(url, options = {}) {
  const res = await fetch(url, options);
  const data = await res.json();
  return data;
}

export async function getInsights() {
  const res = await safeFetch(${API_BASE_URL}/insights);
  return {
    success: true,
    data: res.data || {}
  };
}

export async function uploadDocument(file) {
  const formData = new FormData();
  formData.append("file", file);

  const res = await fetch(${API_BASE_URL}/upload, {
    method: "POST",
    body: formData,
  });

  return await res.json();
}
