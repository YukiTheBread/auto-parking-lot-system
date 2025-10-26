# FastAPI Backend for Auto Parking Lot System App (WIP)
This is a FastAPI application that provides functionality for our project.

## Make sure you have the following installed:
- Python 3.12+
- Git

# วิธีรัน backend (ให้สร้าง table สำหรับเก็บข้อมูลก่อน)
```bash
pip install -r requirements.txt
```

รัน backend:
```bash
uvicorn main:app --reload
```

เปิด Swagger UI ที่:
http://127.0.0.1:8000/docs


# ฝั่ง supabase
## สร้าง table
(หากใช้จาก dashboard)
ให้ไปที่ Project ของคุณ
ที่ https://supabase.com/dashboard
จาก sidebar ซ้าย → ไปที่ “SQL Editor”
กดปุ่ม “New Query”
วาง SQL ด้านล่างนี้ลงไป
จากนั้นกด ▶️ Run เพื่อรันคำสั่ง

```bash
CREATE TABLE public.ParkingLot_Data (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL UNIQUE,
  lot_id bigint NOT NULL,
  plate_number text NOT NULL,
  is_out boolean NOT NULL DEFAULT false,
  check_in timestamp with time zone NOT NULL DEFAULT now(),
  check_out timestamp with time zone,
  parking_fee integer,
  paid boolean NOT NULL DEFAULT false,
  CONSTRAINT ParkingLot_Data_pkey PRIMARY KEY (id),
  CONSTRAINT ParkingLot_Data_lot_id_fkey FOREIGN KEY (lot_id) REFERENCES public.ParkingLot_Status(parking_lot_id)
);
CREATE TABLE public.ParkingLot_Status (
  id integer GENERATED ALWAYS AS IDENTITY NOT NULL,
  parking_lot_id bigint NOT NULL UNIQUE,
  current_customer integer NOT NULL DEFAULT 0,
  latest_update_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT ParkingLot_Status_pkey PRIMARY KEY (id)
);
```
## ตารางจะอยู่ที่ schema public ใน supabase


## สร้าง function
```bash
-- เพิ่มจำนวนรถในลาน
create or replace function increment_customer(lot bigint)
returns integer as $$
update "ParkingLot_Status"
set current_customer = current_customer + 1
where parking_lot_id = lot
returning current_customer;
$$ language sql;

-- ลดจำนวนรถในลาน (แต่ไม่ให้ติดลบ)
create or replace function decrement_customer(lot bigint)
returns integer as $$
update "ParkingLot_Status"
set current_customer = greatest(current_customer - 1, 0)
where parking_lot_id = lot
returning current_customer;
$$ language sql;
```
