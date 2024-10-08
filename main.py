import logging
import threading
from fastapi import Depends,FastAPI,HTTPException,Form,UploadFile,Response
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
# from typing import Annotated
from typing_extensions import Annotated,List

import pandas as pd
from src import crud, models, schemas
from src.database import SessionLocal, engine
from fastapi.responses import StreamingResponse
import json
import io
from io import BytesIO
import csv
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from urllib.parse import unquote
import base64
import uuid

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "" with the origins you want to allow
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Add other HTTP methods as needed
    allow_headers=["*"],  # Allow all headers
)
# ----------------------------------------------------------------------------------------

@app.post("/insert_nature_of_work",response_model=str)
def nature_of_work(work_name:Annotated[str,Form()],db: Session = Depends(get_db)):
     return crud.insert_nature_of_work(db,work_name)

@app.get("/get_nature_of_work",response_model=List[schemas.Nature_Of_Work])
def nature_of_work(db: Session = Depends(get_db)):
     return crud.get_nature_of_work(db)

@app.delete("/delete_nature_of_work",response_model=str)
def nature_of_work(work_id:Annotated[int,Form()],db: Session = Depends(get_db)):
     return crud.delete_nature_of_work(db,work_id)

@app.put("/update_nature_of_work",response_model=str)
def nature_of_work(work_id:Annotated[int,Form()],work_name:Annotated[str,Form()],db: Session = Depends(get_db)):
     return crud.update_nature_of_work(db,work_name,work_id)

# ----------------------------------------------------------------------------------------

@app.post("/insert_user",response_model=str)
def insert_user(username:Annotated[str,Form()],role:Annotated[str,Form()],firstname:Annotated[str,Form()],lastname:Annotated[str,Form()],location:Annotated[str,Form()],db:Session=Depends(get_db)):
     return crud.insert_user(db,username,role,firstname,lastname,location)

@app.get("/get_user",response_model=List[schemas.User_table])
def nature_of_work(db:Session = Depends(get_db)):
     return crud.get_user(db)

@app.delete("/delete_user",response_model=str)
def nature_of_work(user_id:Annotated[int,Form()],db: Session = Depends(get_db)):
     return crud.delete_user(db,user_id)

@app.put("/update_user",response_model=str)
def nature_of_work(user_id:Annotated[int,Form()],user_name:Annotated[str,Form()],user_role:Annotated[str,Form()],db: Session = Depends(get_db)):
     return crud.update_user(db,user_id,user_name,user_role)

# ----------------------------------------------------------------------------------------

@app.post("/login_user",response_model=List[schemas.User_table])
def login_user(username:Annotated[str,Form()],password:Annotated[str,Form()],db:Session=Depends(get_db)):
     return crud.login_check(db,username,password)

# ----------------------------------------------------------------------------------------

@app.post("/tl_insert",response_model=str)
def tl (name_of_entity:Annotated[str,Form()],gst_or_tan:Annotated[str,Form()],gst_tan:Annotated[str,Form()],client_grade:Annotated[str,Form()],Priority:Annotated[str,Form()],Assigned_By:Annotated[int,Form()],estimated_d_o_d:Annotated[str,Form()],estimated_time:Annotated[str,Form()],Assigned_To:Annotated[int,Form()],Scope:Annotated[str,Form()],nature_of_work:Annotated[int,Form()],From:Annotated[str,Form()],Actual_d_o_d:Annotated[str,Form()],db:Session=Depends(get_db)):
     return crud.tl_insert(db,name_of_entity,gst_or_tan,gst_tan,client_grade,Priority,Assigned_By,estimated_d_o_d,estimated_time,Assigned_To,Scope,nature_of_work,From,Actual_d_o_d)

@app.post("/tl_insert_bulk",response_model=str)
def tl_insert_bulk(file:UploadFile,db:Session=Depends(get_db)):
     return crud.tl_insert_bulk(db,file)

# ----------------------------------------------------------------------------------------

@app.post("/tm_get",response_model=list)
def tm_get(user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.get_work(db,user_id)

@app.post("/tl_get",response_model=list)
def tm_get(picked_date:Annotated[str,Form()],to_date:Annotated[str,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.get_work_tl(picked_date,to_date,db,user_id)

# ----------------------------------------------------------------------------------------

@app.post("/start")
def start(service_id:Annotated[int,Form()],type_of_activity:Annotated[str,Form()],no_of_items:Annotated[str,Form()],db:Session=Depends(get_db)):
     return crud.start(db,service_id,type_of_activity,no_of_items)

@app.post("/reallocated")
def reallocated(service_id:Annotated[int,Form()],remarks:Annotated[str,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.reallocated(db,service_id,remarks,user_id)

# ----------------------------------------------------------------------------------------

@app.post("/get_count",response_model=list)
def get_count(user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.get_count(db,user_id)

@app.post("/get_count_tl",response_model=list)
def get_count_tl(user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.get_count_tl(db,user_id)

# ----------------------------------------------------------------------------------------

# @app.get("/break_check")
# def break_check(db:Session=Depends(get_db)):
#      return crud.get_break_time_info(db)

# ----------------------------------------------------------------------------------------

@app.post("/get_reports")
async def get_reports(response:Response,fields:Annotated[str,Form()],db:Session=Depends(get_db)):
     df = await crud.get_reports(db,fields)
     excel_output = BytesIO()
     with pd.ExcelWriter(excel_output, engine='xlsxwriter') as writer:
          df.to_excel(writer, index=False, sheet_name='Sheet1')
     excel_output.seek(0)
     response.headers["Content-Disposition"] = "attachment; filename=data.xlsx"
     response.headers["Content-Type"] = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
     return Response(content=excel_output.getvalue(), media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@app.post("/break_start")
def break_start(service_id:Annotated[int,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.break_start(db,service_id,'',user_id)

@app.post("/break_end")
def break_end(service_id:Annotated[int,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.break_end(db,service_id,user_id)

@app.post("/call_start")
def call_start(service_id:Annotated[int,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.call_start(db,service_id,'',user_id)

@app.post("/call_end")
def call_end(service_id:Annotated[int,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.call_end(db,service_id,user_id)

@app.post("/end_of_day_start")
def end_of_day_start(service_id:Annotated[int,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.end_of_day_start(db,service_id,'',user_id)

@app.post("/end_of_day_end")
def end_of_day_end(service_id:Annotated[int,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.end_of_day_end(db,service_id,user_id)

@app.post("/hold_start")
def hold_start(service_id:Annotated[int,Form()],remarks:Annotated[str,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.hold_start(db,service_id,remarks,user_id)

@app.post("/hold_end")
def hold_end(service_id:Annotated[int,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.hold_end(db,service_id,user_id)

@app.post("/meeting_start")
def meeting_start(service_id:Annotated[int,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.meeting_start(db,service_id,'',user_id)

@app.post("/meeting_end")
def meeting_end(service_id:Annotated[int,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.meeting_end(db,service_id,user_id)

@app.post("/Completed")
def Completed(service_id:Annotated[int,Form()],count:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.Completed(db,service_id,'',count)

@app.post("/User_Wise_Day_Wise_Part_1")
def User_Wise_Day_Wise_Part_1(picked_date:Annotated[str,Form()],to_date:Annotated[str,Form()],db:Session=Depends(get_db)):
     return crud.User_Wise_Day_Wise_Part_1(db,picked_date,to_date)

@app.post("/insert_tds",response_model=str)
def tds(tds:Annotated[str,Form()],db: Session = Depends(get_db)):
     return crud.insert_tds(db,tds)

@app.get("/get_tds",response_model=List[schemas.tds])
def tds(db: Session = Depends(get_db)):
     return crud.get_tds(db)

@app.delete("/delete_tds",response_model=str)
def tds(tds_id:Annotated[int,Form()],db: Session = Depends(get_db)):
     return crud.delete_tds(db,tds_id)

@app.put("/update_tds",response_model=str)
def tds(tds_id:Annotated[int,Form()],tds:Annotated[str,Form()],db: Session = Depends(get_db)):
     return crud.update_tds(db,tds,tds_id)

@app.post("/insert_gst",response_model=str)
def gst(gst:Annotated[str,Form()],db: Session = Depends(get_db)):
     return crud.insert_gst(db,gst)

@app.get("/get_gst",response_model=List[schemas.gst])
def gst(db: Session = Depends(get_db)):
     return crud.get_gst(db)

@app.delete("/delete_gst",response_model=str)
def gst(gst_id:Annotated[int,Form()],db: Session = Depends(get_db)):
     return crud.delete_gst(db,gst_id)

@app.put("/update_gst",response_model=str)
def gst(gst_id:Annotated[int,Form()],gst:Annotated[str,Form()],db: Session = Depends(get_db)):
     return crud.update_gst(db,gst,gst_id)

@app.delete("/delete_entity",response_model=str)
def delete_entity(record_service_id:Annotated[int,Form()],db: Session = Depends(get_db)):
     return crud.delete_entity(db,record_service_id)

@app.post("/reallocated_end")
def reallocated_end(service_id:Annotated[int,Form()],user_id:Annotated[int,Form()],db:Session=Depends(get_db)):
     return crud.reallocated_end(db,service_id,user_id)


@app.post("/reportsnew")
def lastfivereports(picked_date:Annotated[str,Form()],to_date:Annotated[str,Form()],report_name:Annotated[str,Form()],db:Session=Depends(get_db)):
     return crud.lastfivereports(db,picked_date,to_date,report_name)

@app.post("/Hold_Wise_Part")
def Hold_Wise_Part(picked_date:Annotated[str,Form()],to_date:Annotated[str,Form()],db:Session=Depends(get_db)):
     return crud.Hold_Wise_Day_Wise_Part(db,picked_date,to_date)


@app.post("/reportstotal")
def totalfivereports(picked_date:Annotated[str,Form()],to_date:Annotated[str,Form()],report_name:Annotated[str,Form()],db:Session=Depends(get_db)):
     return crud.totalfivereports(db,picked_date,to_date,report_name)

def base64_decode(encoded_str):
    decoded_bytes = base64.b64decode(encoded_str)
    return decoded_bytes

def decrypt_data(key: bytes, enc_data: str) -> bytes:
    enc_data_bytes = base64_decode(enc_data)
    iv = enc_data_bytes[:AES.block_size]
    ct = enc_data_bytes[AES.block_size:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    pt = unpad(cipher.decrypt(ct), AES.block_size)
    return pt


private_key = b'MAHIMA1234560987'

@app.post("/login_user_check")
def login_user_check(token:Annotated[str,Form()],db:Session=Depends(get_db)):
     encripted_data = unquote(token)
     decrypted_data = json.loads(decrypt_data(private_key, encripted_data))

     token = decrypted_data['token']
     employeeid = decrypted_data['user']
     name = decrypted_data['name']
     location1 = decrypted_data['location']
     user_type = decrypted_data['user_type']

     if user_type == "customer":
          pass
     else:
          return crud.login_check(db,employeeid,"jaa")
     

@app.post("/scopes/")
def scope_add(scope:Annotated[str,Form()],db: Session = Depends(get_db)):
     return crud.scope_add(scope,db)

@app.delete("/scope_delete/")
def scope_delete(scope_id:Annotated[int,Form()],db: Session = Depends(get_db)):
     return crud.scope_delete(scope_id,db)

@app.get("/get_scope")
def gst(db: Session = Depends(get_db)):
     return crud.get_scope(db)


@app.put("/update_scopes")
def update_scope(scope_id:Annotated[int,Form()], new_scope:Annotated[str,Form()], db: Session = Depends(get_db)):
    result = crud.scope_update(scope_id, new_scope, db)
    if result == "Success":
        return "Success"
    elif result == "Scope not found":
        raise HTTPException(status_code=404, detail="Scope not found")
    else:
        raise HTTPException(status_code=500, detail="Failed to update scope")
    
@app.post("/sub_scopes/")
def sub_scope_add(scope_id:Annotated[int,Form()], sub_scope:Annotated[str,Form()],db: Session = Depends(get_db)):
     return crud.sub_scope_add(scope_id,sub_scope,db)

@app.delete("/sub_scope_delete/")
def sub_scope_delete(sub_scope_id:Annotated[int,Form()],db: Session = Depends(get_db)):
     return crud.sub_scope_delete(sub_scope_id,db)

@app.put("/update_sub_scopes")
def update_sub_scope(sub_scope_id:Annotated[int,Form()], new_scope:Annotated[str,Form()], db: Session = Depends(get_db)):
    result = crud.sub_scope_update(sub_scope_id,new_scope, db)
    
    if result == "Success":
        return "Success"
    elif result == "Scope not found":
        raise HTTPException(status_code=404, detail="Scope not found")
    else:
        raise HTTPException(status_code=500, detail="Failed to update scope")
    
@app.post("/get_sub_scope")
def subscope(scope_id:Annotated[int,Form()],db: Session = Depends(get_db)):
     return crud.get_sub_scope(scope_id,db)

@app.post("/logintime")
def logintime_add(logtime:Annotated[str,Form()],userid:Annotated[int,Form()],db: Session = Depends(get_db)):
     return crud.logintime_add(logtime,userid,db)

@app.post("/logouttime")
def logout_time_add(logouttime:Annotated[str,Form()],userid:Annotated[int,Form()],db: Session = Depends(get_db)):
     return crud.logout_time_add(logouttime,userid,db)

@app.post("/entityadd")
def entityadd(entityname:Annotated[str,Form()],tanorgst:Annotated[str,Form()],tanvalue:Annotated[str,Form()],db: Session = Depends(get_db)):
     return crud.entityadd(entityname,tanorgst,tanvalue,db)

@app.get("/get_entitydata")
def gst(db: Session = Depends(get_db)):
     return crud.get_entity_data(db)

@app.post("/get_filter_entitydata")
def get_filter_entitydata(id:Annotated[int,Form()],db: Session = Depends(get_db)):
     return crud.get_filter_entitydata(id,db)




#   # -------------------------------------break,hold,work in progres,call and metting automatic------------------------------

# @app.on_event("startup")
# async def startup_event():
#       def thread_target():
#           db = SessionLocal()  
          
#           try:
#               crud.time_check_loop(db)
#           finally:
#               db.close()
      
#       thread = threading.Thread(target=thread_target)
#       thread.daemon = True 
#       thread.start()
      
      
      
#   # -------------------------------------logout automatic------------------------------
  
  
# @app.on_event("startup")
# async def startup_event():
#       db = SessionLocal()  
#       try:
#           def thread_target_logout():
#               db = SessionLocal()  # Create a new session for the thread
#               try:
#                   # Start the time check logout in a separate thread
#                   crud.time_check_logout(db)
#               except Exception as e:
#                   logging.error(f"Error in time_check_logout: {e}")
#               finally:
#                   db.close()
  
#           # Start the time check logout in a separate thread
#           logout_thread = threading.Thread(target=thread_target_logout)
#           logout_thread.daemon = True  # Daemonize thread to ensure it exits when the main program does
#           logout_thread.start()
#       except Exception as e:
#           logging.error(f"Error during startup: {e}")
#       finally:
#           db.close()


@app.post("/idealtimecalculation")
def idealtimecalculation(userid: Annotated[int, Form()], check_status: Annotated[str, Form()], db: Session = Depends(get_db)):
    return crud.idealtime(userid, check_status, db)


@app.post("/calculate_total_time")
def calculate_total_time(
   picked_date:Annotated[str,Form()],to_date:Annotated[str,Form()],db: Session = Depends(get_db)
):

    # Call the CRUD function to calculate total time for all users
    total_time = crud.calculate_total_time_for_all_users(picked_date, to_date, db)

    return total_time 

#-----------------------lOGIN LOGOUT TRACKING------------------------------------------
@app.post("/get_user_status", response_model=List[schemas.UserStatus])
def get_filtered_user_status(
    picked_date: Annotated[str, Form()],
    to_date: Annotated[str, Form()],
    db: Session = Depends(get_db)
):
    return crud.get_user_status(picked_date, to_date, db)
#-----------------------lOGIN LOGOUT TRACKING------------------------------------------


#-----------------------------------hold automation for missing date----pip install APScheduler--------------------------
from apscheduler.schedulers.background import BackgroundScheduler
import logging

def job_wrapper_update_start_time():
    db = SessionLocal()  # Create a new session
    try:
        # Call your function here (e.g., update start time logic)
        print("Updating start time...")
        crud.fetch_hold_data(db)
        # Add your logic to update the start time
    except Exception as e:
        print(f"Error updating start time: {e}")
    finally:
        db.close()  # Ensure the session is closed

# Set up a scheduler
scheduler = BackgroundScheduler()

# Add the job to the scheduler
scheduler.add_job(
    job_wrapper_update_start_time,
    trigger='cron',
    hour=15,  # Runs daily at 23 PM or night 11 PM
    minute=57,  # Run exactly at the start of the hour
    timezone='Asia/Kolkata'  # Set the timezone to Asia/Kolkata
)

# Start the scheduler and print a message
scheduler.start()
print("Scheduler started for hold missing date.")

# Optionally, you can add a shutdown handler to stop the scheduler gracefully
def shutdown_scheduler():
    scheduler.shutdown()
    print("Scheduler stopped for hold missing date.")
    logging.info("Scheduler stopped for hold missing date.")

# Example of how you might call shutdown_scheduler when needed
# shutdown_scheduler()  # Uncomment this line when you want to stop the scheduler.

# --------------------------------end



# ---------------------------Work status  automatic break,hold,work in progres,call and metting------------------------------

from apscheduler.schedulers.background import BackgroundScheduler

def time_check_loop():
    db = SessionLocal()
    try:
        crud.check_and_update_work_status(db)
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    # Start the scheduler when FastAPI starts
    scheduler = BackgroundScheduler()

    # Schedule the job to run every day at 8:55 PM IST
    scheduler.add_job(
        time_check_loop,  # function to call
        trigger='cron',  # cron scheduling
        hour=21,  # 21 PM or night 9 PM
        minute=0,  # 0 minutes
        timezone='Asia/Kolkata'  # Set the timezone to IST
    )

    # Start the scheduler
    scheduler.start()
    logging.info("Scheduler started for 9:00 PM IST.")

    # Ensure the scheduler shuts down with the application
    @app.on_event("shutdown")
    async def shutdown_event():
        scheduler.shutdown()
        logging.info("Scheduler stopped.")

# ------------------------------------- automatic------------------------------


# -------------------------------------logout automatic------------------------------
  
from apscheduler.schedulers.background import BackgroundScheduler

def time_check_logout(db: Session):
    crud.time_check_logout(db)

@app.on_event("startup")
async def startup_event():
    # Start the scheduler on FastAPI startup
    
    scheduler = BackgroundScheduler()

    # Schedule the job to run every day at 21:00 IST (9 PM)
    scheduler.add_job(
        lambda: time_check_logout(SessionLocal()),
        trigger='cron',
        hour=21,
        minute=1,
        timezone='Asia/Kolkata'
    )
    
    # Start the scheduler
    scheduler.start()

    logging.info("Scheduler started for 9 PM IST.")

    # Ensuring proper shutdown
    @app.on_event("shutdown")
    async def shutdown_event():
        scheduler.shutdown()
        logging.info("Scheduler stopped.")
# --------------------------------end

# # ------------------------hold
# @app.post("/hold/")
# def hold_action(user_id: Annotated[int, Form()], service_id: Annotated[int, Form()], db: Session = Depends(get_db)):
#     return crud.hold_action(db, user_id, service_id)

# @app.post("/calculate_total_time_hold/")
# def get_total_time(
#     picked_date: Annotated[str, Form()],
#     to_date: Annotated[str, Form()],
#     db: Session = Depends(get_db)
# ):
#     # Call the function from crud to get the total time
#     hold_total_time = crud.calculate_total_time_hold(db, picked_date, to_date)
#     return hold_total_time

# # ------------------------break
# @app.post("/break/")
# def break_action(user_id: Annotated[int, Form()], service_id: Annotated[int, Form()], db: Session = Depends(get_db)):
#     return crud.break_action(db, user_id, service_id)

# @app.post("/calculate_total_time_break/")
# def get_total_time(
#     picked_date: Annotated[str, Form()],
#     to_date: Annotated[str, Form()],
#     db: Session = Depends(get_db)
# ):
#     # Call the function from crud to get the total time
#     break_total_time = crud.calculate_total_time_break(db, picked_date, to_date)
#     return break_total_time

# # ------------------------meeting
# @app.post("/meeting/")
# def meeting_action(user_id: Annotated[int, Form()], service_id: Annotated[int, Form()], db: Session = Depends(get_db)):
#     return crud.meeting_action(db, user_id, service_id)

# @app.post("/calculate_total_time_meeting/")
# def get_total_time(
#     picked_date: Annotated[str, Form()],
#     to_date: Annotated[str, Form()],
#     db: Session = Depends(get_db)
# ):
#     # Call the function from crud to get the total time
#     meet_total_time = crud.calculate_total_time_meeting(db, picked_date, to_date)
#     return meet_total_time

# # ------------------------call
# @app.post("/call/")
# def call_action(user_id: Annotated[int, Form()], service_id: Annotated[int, Form()], db: Session = Depends(get_db)):
#     return crud.call_action(db, user_id, service_id)

# @app.post("/calculate_total_time_call/")
# def get_total_time(
#     picked_date: Annotated[str, Form()],
#     to_date: Annotated[str, Form()],
#     db: Session = Depends(get_db)
# ):
#     # Call the function from crud to get the total time
#     call_total_time = crud.calculate_total_time_call(db, picked_date, to_date)
#     return call_total_time

# # ------------------------inprogress
# @app.post("/inprogress/")
# def inprogress_action(user_id: Annotated[int, Form()], service_id: Annotated[int, Form()], db: Session = Depends(get_db)):
#     return crud.inprogress_action(db, user_id, service_id)

# @app.post("/calculate_total_time_inprogress/")
# def get_total_time(
#     picked_date: Annotated[str, Form()],
#     to_date: Annotated[str, Form()],
#     db: Session = Depends(get_db)
# ):
#     # Call the function from crud to get the total time
#     inprogress_total_time = crud.calculate_total_time_inprogress(db, picked_date, to_date)
#     return inprogress_total_time

# # -----------------------

# @app.post("/fetch-total-time/", response_model=schemas.FetchTotalTimeResponse)
# def fetch_total_time(user_id: int, service_id: int, db: Session = Depends(get_db)):
#     total_time_record = crud.calculate_and_store_total_times(db, user_id, service_id)

#     if total_time_record:  # If total_time_record has valid data
#         return schemas.FetchTotalTimeResponse(
#             message="Success",
#             user_id=user_id,
#             service_id=service_id,
#             date=total_time_record.date.isoformat(),  # Convert date to ISO format string
#             total_inprogress_time=total_time_record.total_inprogress_time or "0:00:00",
#             total_hold_time=total_time_record.total_hold_time or "0:00:00",
#             total_break_time=total_time_record.total_break_time or "0:00:00",
#             total_meeting_time=total_time_record.total_meeting_time or "0:00:00",
#             total_call_time=total_time_record.total_call_time or "0:00:00",
#             total_ideal_time=total_time_record.total_ideal_time or "0:00:00"
#         )
#     else:
#         return schemas.FetchTotalTimeResponse(
#             message="No records found",
#             user_id=user_id,
#             service_id=service_id,
#             date="N/A",
#             total_inprogress_time="0:00:00",
#             total_hold_time="0:00:00",
#             total_break_time="0:00:00",
#             total_meeting_time="0:00:00",
#             total_call_time="0:00:00",
#             total_ideal_time="0:00:00"
#        )