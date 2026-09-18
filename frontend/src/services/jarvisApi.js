// services/jarvisApi.js
// Thin client for the existing FastAPI backend. No command logic lives here
// beyond forwarding to the backend — the backend owns all system actions.

const BASE_URL = "http://127.0.0.1:8000";
const REQUEST_TIMEOUT_MS = 8000;

async function withTimeout(promise, ms) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ms);
  try {
    return await promise(controller.signal);
  } finally {
    clearTimeout(timer);
  }
}

/**
 * GET /health
 * Returns { online: boolean, raw: any|null, error: string|null }
 */
export async function checkHealth() {
  try {
    const res = await withTimeout(
      (signal) => fetch(`${BASE_URL}/health`, { method: "GET", signal }),
      REQUEST_TIMEOUT_MS
    );
    if (!res.ok) {
      return { online: false, raw: null, error: `HTTP ${res.status}` };
    }
    let raw = null;
    try {
      raw = await res.json();
    } catch {
      raw = null;
    }
    return { online: true, raw, error: null };
  } catch (err) {
    return {
      online: false,
      raw: null,
      error: err?.name === "AbortError" ? "TIMEOUT" : "UNREACHABLE",
    };
  }
}

/**
 * POST /chat
 * body: { message: command }
 * Returns { ok: boolean, data: any|null, error: string|null }
 */
export async function sendCommand(command) {
  try {
    const res = await withTimeout(
      (signal) =>
        fetch(`${BASE_URL}/chat`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message: command }),
          signal,
        }),
      REQUEST_TIMEOUT_MS
    );
    if (!res.ok) {
      return { ok: false, data: null, error: `HTTP ${res.status}` };
    }
    let data = null;
    try {
      data = await res.json();
    } catch {
      data = null;
    }
    return { ok: true, data, error: null };
  } catch (err) {
    return {
      ok: false,
      data: null,
      error: err?.name === "AbortError" ? "TIMEOUT" : "UNREACHABLE",
    };
  }
}

export const JARVIS_API_BASE_URL = BASE_URL;
