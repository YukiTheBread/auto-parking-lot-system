from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from supabase import create_client, Client
from datetime import datetime, timezone

app = FastAPI(title="ParkingLot Backend")

# ====== Supabase setup ======
SUPABASE_URL = "your-supabase-url"
SUPABASE_KEY = "your-supabase-key"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ---------- MODELS ----------
class CarIn(BaseModel):
    lot_id: int = Field(..., example=1)
    plate_number: str = Field(..., example="กข1234")

class CarOut(BaseModel):
    plate_number: str = Field(..., example="กข1234")
    lot_id: int = Field(..., example=1)
    parking_fee: int = Field(..., example=20)

class PaymentUpdate(BaseModel):
    plate_number: str = Field(..., example="กข1234")
    paid: bool = Field(..., example=True)

# ---------- ROUTES ----------
@app.post("/checkin")
def car_checkin(data: CarIn):
    """รถเข้าลาน"""
    try:
        # บันทึกข้อมูลรถเข้า
        supabase.table("ParkingLot_Data").insert({
            "lot_id": data.lot_id,
            "plate_number": data.plate_number,
            "check_in": datetime.now(timezone.utc).isoformat(),
            "is_out": False,
            "paid": False
        }).execute()

        # เรียก RPC เพื่ออัปเดตจำนวนลูกค้า
        supabase.rpc("increment_customer", {"lot": data.lot_id}).execute()

        # อัปเดต latest_update_at ของลาน
        supabase.table("ParkingLot_Status").update({
            "latest_update_at": datetime.now(timezone.utc).isoformat()
        }).eq("parking_lot_id", data.lot_id).execute()

        return {"message": "Car checked in successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/checkout")
def car_checkout(data: CarOut):
    """รถออกจากลาน"""
    try:
        # อัปเดตข้อมูลรถ
        supabase.table("ParkingLot_Data").update({
            "check_out": datetime.now(timezone.utc).isoformat(),
            "parking_fee": data.parking_fee,
            "is_out": True
        }).eq("plate_number", data.plate_number)\
          .eq("lot_id", data.lot_id)\
          .eq("is_out", False).execute()

        # เรียก RPC เพื่อลดจำนวนลูกค้า
        supabase.rpc("decrement_customer", {"lot": data.lot_id}).execute()

        # อัปเดต latest_update_at ของลาน
        supabase.table("ParkingLot_Status").update({
            "latest_update_at": datetime.now(timezone.utc).isoformat()
        }).eq("parking_lot_id", data.lot_id).execute()

        return {"message": "Car checked out successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/payment")
def update_payment(data: PaymentUpdate):
    """อัปเดตสถานะการจ่ายเงิน"""
    try:
        supabase.table("ParkingLot_Data").update({
            "paid": data.paid
        }).eq("plate_number", data.plate_number).execute()

        return {"message": "Payment status updated."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{lot_id}")
def get_lot_status(lot_id: int):
    """ดูสถานะลาน"""
    result = supabase.table("ParkingLot_Status").select("*").eq("parking_lot_id", lot_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="Lot not found")
    return result.data[0]

@app.get("/history/{lot_id}")
def get_parking_history(lot_id: int):
    """ดูประวัติการเข้าออกของลานนั้น"""
    result = supabase.table("ParkingLot_Data")\
                     .select("*")\
                     .eq("lot_id", lot_id)\
                     .order("check_in", desc=True).execute()
    return {"data": result.data}

@app.get("/")
def root():
    return {"message": "ParkingLot Backend is running"}