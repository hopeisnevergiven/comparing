from urllib.parse import parse_qs, urlparse, unquote
import requests
import json

ALLOWED_HOST = "://ravenkog.com"
TIMEOUT      = 8  # تقليله لضمان عدم تجاوز حد الخطة المجانية لـ Vercel

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

# هذا الهيكل المطور والمتوافق مع بيئة Vercel Serverless لـ Python
def handler(request):
    # إعداد ترويسات الاستجابة الافتراضية لمنع مشاكل الـ CORS
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    # التعامل مع طلبات الـ OPTIONS (CORS preflight)
    if request.method == "OPTIONS":
        return {"statusCode": 200, "headers": cors_headers, "body": ""}

    # التأكد من أن الطلب من نوع GET فقط
    if request.method != "GET":
        return {
            "statusCode": 405,
            "headers": cors_headers,
            "body": json.dumps({"error": "Method not allowed"})
        }

    # استخراج الرابط المطلوب من المعاملات (Query Parameters)
    query_params = parse_qs(urlparse(request.path).query)
    url = unquote(query_params.get("url", [""])[0]).strip()

    # التحقق من وجود الرابط وصحته
    if not url:
        return {
            "statusCode": 400,
            "headers": cors_headers,
            "body": json.dumps({"error": "Missing ?url= parameter"})
        }

    if urlparse(url).netloc != ALLOWED_HOST:
        return {
            "statusCode": 403,
            "headers": cors_headers,
            "body": json.dumps({"error": f"Only {ALLOWED_HOST} URLs are allowed"})
        }

    # إرسال الطلب الفعلي إلى الموقع المستهدف
    try:
        resp = requests.get(url, headers=FORWARD_HEADERS, timeout=TIMEOUT)
        
        # دمج ترويسات CORS مع الترويسة القادمة من الموقع المستهدف
        response_headers = cors_headers.copy()
        response_headers["Content-Type"] = resp.headers.get("Content-Type", "application/json")
        
        return {
            "statusCode": resp.status_code,
            "headers": response_headers,
            "body": resp.text
        }

    except requests.Timeout:
        return {"statusCode": 504, "headers": cors_headers, "body": json.dumps({"error": "ravenkog.com timed out"})}
    except requests.ConnectionError:
        return {"statusCode": 502, "headers": cors_headers, "body": json.dumps({"error": "Could not reach ravenkog.com"})}
    except Exception as exc:
        return {"statusCode": 500, "headers": cors_headers, "body": json.dumps({"error": str(exc)})}
