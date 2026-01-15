import redis
from dotenv import load_dotenv
import os

# تحميل متغيرات البيئة من .env
load_dotenv()

# إنشاء الاتصال بـ Redis
r = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=int(os.getenv("REDIS_PORT")),
    password=os.getenv("REDIS_PASSWORD"),
    decode_responses=True
)

# اختبار الاتصال
try:
    r.ping()
    print("✅ Redis متصل بنجاح!")
except redis.exceptions.ConnectionError:
    print("❌ Redis غير متصل")
