// ─────────────────────────────────────────────────────────────────────────────
// In index.html, FIND the block that starts with:
//   /* ═══ CORS proxy + fetch helpers ═══ */
//   const PROXY_WRAPPERS = [
// and ends at the closing } of fetchViaProxy.
// REPLACE the entire block with what's below.
// ─────────────────────────────────────────────────────────────────────────────


/* ═══ Vercel API fetch helpers ═══
   Calls /api/proxy (Vercel serverless function) instead of third-party proxies.
   Works automatically once deployed to Vercel — no extra config needed.
═══════════════════════════════════════════════════════════════════════════════*/

// Relative URL — works on any Vercel domain automatically
const LOCAL_API = '/api/proxy';

function buildFinishedURL(name, page=0, limit=9999, search='', difficulty=''){
  return `https://www.ravenkog.com/api/players/maps?playerName=${encodeURIComponent(name)}&page=${page}&limit=${limit}&sortField=lastFinish&sortOrder=-1&search=${encodeURIComponent(search)}&difficulty=${encodeURIComponent(difficulty)}`;
}

function buildUnfinishedURL(name, page=0, limit=9999){
  return `https://www.ravenkog.com/api/players/unfinished-maps?playerName=${encodeURIComponent(name)}&page=${page}&limit=${limit}&sortField=releaseDate&sortOrder=-1&search=&difficulty=`;
}

/**
 * Fetches any ravenkog.com URL through the Vercel serverless proxy.
 * Replaces the old PROXY_WRAPPERS / fetchViaProxy approach.
 */
async function fetchViaProxy(url, ms=9000){
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), ms);

  try {
    const res = await fetch(
      `${LOCAL_API}?url=${encodeURIComponent(url)}`,
      { signal: controller.signal }
    );
    clearTimeout(timer);

    if(!res.ok) throw new Error(`Proxy returned HTTP ${res.status} for: ${url}`);
    return await res.text();

  } catch(err){
    clearTimeout(timer);
    if(err.name === 'AbortError')
      throw new Error(`Request timed out (${ms}ms): ${url}`);
    throw err;
  }
}
