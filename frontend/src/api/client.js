import axios from "axios";

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "",
});

export async function getRiskDashboard() {
  const { data } = await client.get("/api/risk-dashboard");
  return data;
}

export async function startExcavation(assetUrn, assetName) {
  const { data } = await client.post("/api/excavate", {
    asset_urn: assetUrn,
    asset_name: assetName,
  });
  return data;
}

export async function getExcavationJob(jobId) {
  const { data } = await client.get(`/api/excavate/${jobId}`);
  return data;
}

export async function getAllKnowledge() {
  const { data } = await client.get("/api/knowledge");
  return data;
}

export async function getDependencyGraph() {
  const { data } = await client.get("/api/dependency-graph");
  return data;
}

export async function getAssetDetail(assetUrn) {
  const { data } = await client.get(`/api/asset-detail/${encodeURIComponent(assetUrn)}`);
  return data;
}

export async function getPendingReview() {
  const { data } = await client.get("/api/pending-review");
  return data;
}

export async function approvePendingReview(assetUrn) {
  const { data } = await client.post(`/api/pending-review/${encodeURIComponent(assetUrn)}/approve`);
  return data;
}

export async function rejectPendingReview(assetUrn) {
  const { data } = await client.post(`/api/pending-review/${encodeURIComponent(assetUrn)}/reject`);
  return data;
}

export async function searchAssets(query) {
  const { data } = await client.get("/api/search", { params: { q: query } });
  return data;
}

export default client;
