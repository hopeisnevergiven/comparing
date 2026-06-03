from fastapi import FastAPI, Query, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from urllib.parse import urlparse, unquote
import requests

app = FastAPI()

# تفعيل الـ CORS بشكل كامل وآمن لمنع أي حظر من المتصفح
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

ALLOWED_HOST = "://ravenkog.com"
TIMEOUT = 8

FORWARD_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept":          "application/json, text/html, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer":         f"https://{ALLOWED_HOST}/",
}

@app.get("/api/proxy")
def proxy_handler(url: str = Query(None)):
    if not url:
        raise HTTPException(status_code=400, detail="Missing ?url= parameter")
    
    decoded_url = unquote(url).strip()
    parsed_url = urlparse(decoded_url)
    
    if parsed_url.netloc != ALLOWED_HOST:
        raise HTTPException(status_code=403, detail=f"Only {ALLOWED_HOST} URLs are allowed")
    
    try:
        resp = requests.get(decoded_url, headers=FORWARD_HEADERS, timeout=TIMEOUT)
        
        # إرجاع نفس النتيجة القادمة من السيرفر مع الحفاظ على الـ Content-Type الافتراضي
        return Response(
            content=resp.content,
            status_code=resp.status_code,
            media_type=resp.headers.get("Content-Type", "application/json")
        )
        
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="ravenkog.com timed out")
    except requests.ConnectionError:
        raise HTTPException(status_code=502, detail="Could not reach ravenkog.com")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
