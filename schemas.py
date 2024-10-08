from pydantic import BaseModel
import json
from datetime import date
from typing import Optional

class Nature_Of_Work(BaseModel):
    work_id:int
    work_name:str
    work_status:int

class User_table(BaseModel):
    user_id:int
    username:str
    password:str
    role:str
    firstname:str
    lastname:str
    location:str
    user_status:int

class tds(BaseModel):
    tds_id:int
    tds:str
    tds_status:int

class gst(BaseModel):
    gst_id:int
    gst:str
    gst_status:int


#-----------------------lOGIN LOGOUT TRACKING------------------------------------------

class UserStatus(BaseModel):
    username: str
    login_time: str
    logout_time: str
    login_date: str
    duration: str
    status: str

class FetchTotalTimeResponse(BaseModel):
    message: str
    user_id: int
    service_id: int
    date: str  
    total_inprogress_time: str
    total_hold_time: str
    total_break_time: str
    total_meeting_time: str
    total_call_time: str
    total_ideal_time: str