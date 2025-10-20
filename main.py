from fastapi import FastAPI
from supabase import create_client, Client
from datetime import datetime, timezone

app = FastAPI()

# ====== Supabase setup ======
SUPABASE_URL = "https://ihsnizlrqokbvahydwee.supabase.co"
SUPABASE_KEY = "sb_publishable_kemkVfHNkEIerLZnCiuAew_JeDVvyF9"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# ====== functions ======


# ====== 1. รถเข้า ======


# ====== 2. รถออก ======


# ====== 3. ดูสถานะลานจอด ======
