from collections import defaultdict
import logging
from typing import Dict, List
from sqlalchemy.orm import Session
from src import report, totaltime
from . import models, schemas
from fastapi import UploadFile,HTTPException
import pandas as pd
import json
from datetime import date,datetime, time,timedelta
import os
from zipfile import ZipFile
import tracemalloc
import shutil
from sqlalchemy import cast, or_,and_,func,Date
import csv
from io import BytesIO
from sqlalchemy.exc import IntegrityError
import pendulum
from datetime import datetime, timedelta
import time
#-------------------------------------------------------------------------------------------

#Function to convert time string to timedelta
def time_str_to_timedelta(time_str):
    (h, m, s) = map(int, time_str.split(':'))
    return timedelta(hours=h, minutes=m, seconds=s)

#-------------------------------------------------------------------------------------------

def insert_nature_of_work(db:Session,work_name_str:str):
   db_nature_of_work = models.Nature_Of_Work(work_name = work_name_str)
   db.add(db_nature_of_work)
   try:
        db.commit()
        return "Success"
   except :
       db.rollback()
       return "Failure"

def get_nature_of_work(db:Session):
    return db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_status==1).all()

def delete_nature_of_work(db:Session,work_id:int):
    db_res = db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_id==work_id).first()
    db_res.work_status = 0
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"

def update_nature_of_work(db:Session,work_name:str,work_id:int):
    db_res = db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_id==work_id).first()
    db_res.work_name = work_name
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"
    
#-------------------------------------------------------------------------------------------

def insert_user(db:Session,username:str,role:str,firstname:str,lastname:str,location:str):
   db_insert_user = models.User_table(username = username,role=role,firstname = firstname,lastname = lastname,location=location)
   db.add(db_insert_user)
   print(db)
   try:
        db.commit()
        return "Success"
   except :
       db.rollback()
       return "Failure"

# def insert_user(db: Session, username: str, role: str, firstname: str, lastname: str, location: str):
#     db_insert_user = models.User_table(username=username, role=role, firstname=firstname, lastname=lastname, location=location)
#     db.add(db_insert_user)
#     print(db)
#     try:
#         db.commit()
#         return "Success"
#     except IntegrityError:
#         db.rollback()
#         return "Failure: Username already exists"
#     except Exception as e:
#         db.rollback()
#         return f"Failure: {str(e)}"
   
def get_user(db:Session):
    return db.query(models.User_table).filter(models.User_table.user_status==1).all()

def delete_user(db:Session,user_id:int):
    db_res = db.query(models.User_table).filter(models.User_table.user_id==user_id).first()
    db_res.user_status = 0
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"
    
def update_user(db:Session,user_id:int,username:str,user_role:str):
    db_res = db.query(models.User_table).filter(models.User_table.user_id==user_id).first()
    db_res.username = username
    db_res.role = user_role
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"

#-------------------------------------------------------------------------------------------

def login_check(db:Session,username:str,password:str):
    db_count = db.query(models.User_table).filter(models.User_table.username==username,models.User_table.password==password,models.User_table.user_status==1).count()
    if db_count > 0:
        return db.query(models.User_table).filter(models.User_table.username==username,models.User_table.password==password,models.User_table.user_status==1).all()
    else:
        return []
    
#-------------------------------------------------------------------------------------------

def tl_insert(db:Session,name_of_entity:str,gst_or_tan:str,gst_tan:str,client_grade:str,Priority:str,Assigned_By:int,estimated_d_o_d:str,estimated_time:str,Assigned_To:int,Scope:str,nature_of_work:int,From:str,Actual_d_o_d:str):
    entity_name = name_of_entity
    entity_name_upper = entity_name.upper()
    # print(entity_name_upper,"---------------------------------------------------------------")
    db_insert_tl = models.TL(name_of_entity=entity_name_upper,gst_or_tan=gst_or_tan,gst_tan=gst_tan,client_grade=client_grade,Priority=Priority,Assigned_By=Assigned_By,estimated_d_o_d=estimated_d_o_d,estimated_time=estimated_time,Assigned_To=Assigned_To,Scope=Scope,nature_of_work=nature_of_work,From=From,Actual_d_o_d=Actual_d_o_d)
    db.add(db_insert_tl)
    try:
        db.commit()
        return "Success"
    except :
       db.rollback()
       return "Failure"
    
#-------------------------------------------------------------------------------------------

def tl_insert_bulk(db:Session,file1:UploadFile):
    tracemalloc.start()
    if file1.filename.endswith('.csv'):
        df1 = pd.read_csv(file1.file)
        print(df1.to_string())
    else:
        raise HTTPException(status_code=400, detail="File format not supported. Please upload CSV (.csv) files.")
    
    for index,row1 in df1.iterrows():

        nature_of_work = row1['nature_of_work']
        assigned_by = row1['Assigned_By']
        assigned_to = row1['Assigned_To']
        db_res_count = db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_name==nature_of_work,models.Nature_Of_Work.work_status==1).count()
        
        

        if db_res_count>0:
            db_res = db.query(models.Nature_Of_Work).filter(models.Nature_Of_Work.work_name==nature_of_work,models.Nature_Of_Work.work_status==1).first()
            nature_of_work_id = db_res.work_id
            db_res_count1 = db.query(models.User_table).filter(models.User_table.username==assigned_by,models.User_table.user_status==1).count()
            if db_res_count1>0:
                db_res = db.query(models.User_table).filter(models.User_table.username==assigned_by,models.User_table.user_status==1).first()
                assigned_by_id = db_res.user_id
                db_res_count2 = db.query(models.User_table).filter(models.User_table.username==assigned_to,models.User_table.user_status==1).count()
                if db_res_count2>0:
                    db_res = db.query(models.User_table).filter(models.User_table.username==assigned_to,models.User_table.user_status==1).first()
                    assigned_to_id = db_res.user_id
                    entity = row1['name_of_entity']
                    entity_name_upper = entity.upper()
                    db_insert_tl = models.TL(name_of_entity=entity_name_upper,gst_or_tan=row1['gst_or_tan'],gst_tan=row1['gst_tan'],client_grade=row1['client_grade'],Priority=row1['Priority'],Assigned_By=int(assigned_by_id),estimated_d_o_d=row1['estimated_d_o_d'],estimated_time=row1['estimated_time'],Assigned_To=int(assigned_to_id),Scope=row1['Scope'],nature_of_work=int(nature_of_work_id),From=row1['From'],Actual_d_o_d=row1['Actual_d_o_d'])
                    db.add(db_insert_tl)
                    try:
                        db.commit()
                    except :
                        db.rollback()
                else:
                    return "Failure"
            else:
                return "Failure"
        else:
            return "Failure"
    return "Success"
        
#-------------------------------------------------------------------------------------------

def get_work(db:Session,user_id:int):
    task_list = []
    db_res = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.status==1,models.TL.work_status != "Re-allocated",models.TL.work_status != "Completed").all()
    
    for row in db_res:
        data = {}
        data['service_id'] = row.Service_ID
        data['name_of_entity'] = row.name_of_entity
        data['gst_or_tan'] = row.gst_or_tan
        data['gst_tan'] = row.gst_tan
        data['client_grade'] = row.client_grade   
        data['Priority'] = row.Priority
        data['Scope'] = row.Scope
       
        # Fetch Assigned_By details
        db_user = db.query(models.User_table).filter(models.User_table.user_id==row.Assigned_By).first()
        if db_user:
            data['Assigned_By'] = db_user.username
            data['Assigned_By_Id'] = db_user.user_id
        else:
            data['Assigned_By'] = '-'
            data['Assigned_By_Id'] = None

        data['Assigned_Date'] = row.Assigned_Date.strftime("%d-%m-%Y %H:%M:%S")
        data['estimated_d_o_d'] = row.estimated_d_o_d
        data['estimated_time'] = row.estimated_time

        # Fetch Assigned_To details
        db_user = db.query(models.User_table).filter(models.User_table.user_id==row.Assigned_To).first()
        if db_user:
            data['Assigned_To'] = db_user.username
            data['Assigned_To_Id'] = db_user.user_id
        else:
            data['Assigned_To'] = '-'
            data['Assigned_To_Id'] = None

        data['nature_of_work'] = row._nature_of_work.work_name
        data['nature_of_work_id'] = row.nature_of_work
        data['From'] = row.From
        data['Actual_d_o_d'] = row.Actual_d_o_d
        data['created_on'] = row.created_on.strftime("%d-%m-%Y ")
        data['type_of_activity'] = row.type_of_activity
        data['work_status'] = row.work_status
        data['no_of_items'] = row.no_of_items
        data['remarks'] = row.remarks
        data['working_time'] = row.working_time
        data['completed_time'] = row.completed_time
        data['reallocated_time'] = row.reallocated_time
        task_list.append(data)
    json_data = json.dumps(task_list)
    return json.loads(json_data)

def commonfunction_get_work_tl(db, db_res):
    task_list = []
    for row in db_res:
        data = {}
        data['service_id'] = row.Service_ID
        data['name_of_entity'] = row.name_of_entity
        data['gst_or_tan'] = row.gst_or_tan
        data['gst_tan'] = row.gst_tan
        data['client_grade'] = row.client_grade
        data['Priority'] = row.Priority
        data['Scope'] = row.Scope    
        # data['created_on'] = row.created_on
        # print(data['created_on'] , "5555555555555555555555555555555555555555555555555")
       
        # data['created_on'] = row.created_on.date()
       
        # Fetch Assigned_By details
        db_user = db.query(models.User_table).filter(models.User_table.user_id==row.Assigned_By).first()
        if db_user:
            data['Assigned_By'] = db_user.firstname + ' ' + db_user.lastname
            data['Assigned_By_Id'] = db_user.user_id
        else:
            data['Assigned_By'] = '-'
            data['Assigned_By_Id'] = None

        data['Assigned_Date'] = row.Assigned_Date.strftime("%d-%m-%Y %H:%M:%S")
        data['estimated_d_o_d'] = row.estimated_d_o_d
        data['estimated_time'] = row.estimated_time

        # Fetch Assigned_To details
        db_user = db.query(models.User_table).filter(models.User_table.user_id==row.Assigned_To).first()
        if db_user:
            data['Assigned_To'] =  db_user.firstname + ' ' + db_user.lastname
            data['Assigned_To_Id'] = db_user.user_id
        else:
            data['Assigned_To'] = '-'
            data['Assigned_To_Id'] = None

        data['nature_of_work'] = row._nature_of_work.work_name
        data['nature_of_work_id'] = row.nature_of_work
        data['From'] = row.From
        data['Actual_d_o_d'] = row.Actual_d_o_d
        data['created_on'] = row.created_on.strftime("%d-%m-%Y ")
        data['type_of_activity'] = row.type_of_activity
        data['work_status'] = row.work_status
        data['no_of_items'] = row.no_of_items
        data['remarks'] = row.remarks
        data['working_time'] = row.working_time
        data['completed_time'] = row.completed_time
        data['reallocated_time'] = row.reallocated_time

        task_list.append(data)

    return json.dumps(task_list)

# def get_work_tl(db:Session,user_id:int):
#     user_roles = db.query(models.User_table).filter(models.User_table.user_id==user_id,models.User_table.user_status==1).all()
#     role = [role.role for role in user_roles]
#     if 'TL' in role:
#         db_res = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.status==1).all()
#         json_data = commonfunction_get_work_tl(db, db_res)
#         return json.loads(json_data)
#     else:
#         db_res = db.query(models.TL).filter(models.TL.status==1).all()
#         json_data = commonfunction_get_work_tl(db, db_res)
#         return json.loads(json_data)



def get_work_tl(picked_date,to_date,db:Session,user_id:int):
    start_date = datetime.strptime(picked_date, "%Y-%m-%d")
    end_date = datetime.strptime(to_date, "%Y-%m-%d")  + timedelta(days=1) - timedelta(seconds=1)
    user_roles = db.query(models.User_table).filter(models.User_table.user_id==user_id,models.User_table.user_status==1).all()
    role = [role.role for role in user_roles]
    if 'TL' in role:
        db_res = db.query(models.TL).filter(
            and_(
                models.TL.Assigned_By == user_id,
                models.TL.status == 1,
                models.TL.created_on >= start_date,
                models.TL.created_on <= end_date
            )
        ).all()
        json_data = commonfunction_get_work_tl(db, db_res)
        return json.loads(json_data)
    else:
        db_res = db.query(models.TL).filter(
            and_(
                models.TL.status == 1,
                models.TL.created_on >= start_date,
                models.TL.created_on <= end_date
            )
        ).all()
        json_data = commonfunction_get_work_tl(db, db_res)
        return json.loads(json_data)

#-------------------------------------------------------------------------------------------

def start(db:Session,service_id:int,type_of_activity:str,no_of_items:str):
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.type_of_activity = type_of_activity
    db_res.no_of_items = no_of_items
    db_res.work_status = "Work in Progress"
    if db_res.working_time == '':
        current_datetime = datetime.now()
        current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        db_res.working_time = current_datetime_str
    db.commit()
    return "Success"

#-------------------------------------------------------------------------------------------

def reallocated(db:Session,service_id:int,remarks:str,user_id:int):
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Re-allocated"
    db_res.remarks = remarks
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    db_res.reallocated_time = current_datetime_str
    db.commit()


    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    
    if db_res:
        # Update the record's fields
        # db_res.work_status = "Re-allocated"
        # db_res.Assigned_To = None
        db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id,models.TL.status==1).all()
        print(db_res)
        for row in db_res:
            
            # data['service_id'] = row.Service_ID
            name_of_entity = row.name_of_entity
            gst_or_tan = row.gst_or_tan
            gst_tan = row.gst_tan
            client_grade = row.client_grade   
            Priority = row.Priority
            Scope = row.Scope
            nature_of_work = row._nature_of_work.work_name
            nature_of_work_id = row.nature_of_work
            From = row.From
            Actual_d_o_d = row.Actual_d_o_d
            created_on = row.created_on.strftime("%d-%m-%Y ")
            type_of_activity = row.type_of_activity
            work_status = "Not Picked"
            no_of_items = row.no_of_items
            remarks_new = row.remarks
            working_time = row.working_time
            completed_time = row.completed_time
            reallocated_time = row.reallocated_time
            Assigned_By = row.Assigned_By
            estimated_d_o_d = row.estimated_d_o_d
            estimated_time = row.estimated_time
            # print(row.name_of_entity,row.gst_or_tan,row.gst_tan,row.client_grade,row.Priority,row.Scope,row._nature_of_work.work_name,row.nature_of_work,row.From,row.Actual_d_o_d)
            db_insert = models.TL(name_of_entity=name_of_entity,gst_or_tan=gst_or_tan,gst_tan=gst_tan,client_grade=client_grade,Priority=Priority,Assigned_By=Assigned_By,estimated_d_o_d=estimated_d_o_d,work_status = work_status ,estimated_time=estimated_time,Assigned_To=user_id,Scope=Scope,nature_of_work=nature_of_work_id,From=From,Actual_d_o_d=Actual_d_o_d)

            db.add(db_insert)
            db.commit()
            current_datetime = datetime.now()
            current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
            db_insert = models.REALLOCATED(Service_ID = service_id,user_id=user_id,re_time_start = current_datetime_str,remarks=remarks)
            db.add(db_insert)
            db.commit()

        return "Success"


def reallocated_end(db:Session,service_id:int,user_id:int):
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Not Picked"
    db_res.Assigned_To = user_id
    
    db.commit()
    # current_datetime = datetime.now()
    # current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    # db_res2 = db.query(models.REALLOCATED).filter(
    #     models.REALLOCATED.Service_ID == service_id,
    #     models.REALLOCATED.user_id == user_id
    # ).order_by(
    #     models.REALLOCATED.id.desc()
    # ).first()
    # db_res2.re_time_end = current_datetime_str
    # db.commit()
    return "Success"

#-------------------------------------------------------------------------------------------

def get_count(db:Session,user_id:int):
    count_list = []
    data = {}
    db_completed_count = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.work_status=="Completed",models.TL.status==1).count()
    data['completed_count'] = db_completed_count

    db_reallocated_count = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.work_status=="Reallocated",models.TL.status==1).count()
    data['reallocated_count'] = db_reallocated_count

    db_not_picked_count = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.work_status=="Not Picked",models.TL.status==1).count()
    data['not_picked_count'] = db_not_picked_count

    db_wip_count = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.work_status=="Work in Progress",models.TL.status==1).count()
    data['wip_count'] = db_wip_count

    db_chargable_count = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.type_of_activity=="CHARGABLE",models.TL.status==1).count()
    data['chargable_count'] = db_chargable_count

    db_non_chargable_count = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.type_of_activity=="Non-Charchable",models.TL.status==1).count()
    data['non_chargable_count'] = db_non_chargable_count

    db_hold_count = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.work_status=="Hold",models.TL.status==1).count()
    data['hold'] = db_hold_count

    db_training = db.query(models.TL).filter(models.TL.Assigned_To==user_id,models.TL.work_status=="End Of Day",models.TL.status==1).count()
    data['Training'] = db_training

    count_list.append(data)
    return count_list

def get_count_tl(db:Session,user_id:int):
    count_list = []
    data = {}
    get_role = db.query(models.User_table).filter(models.User_table.user_id==user_id).all()
    user_role = ''
    if get_role:
        user_role = get_role[0].role
    else:
        print(f"No user found with user_id {user_id}")
    if (user_role == "TL"):
        db_completed_count = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.work_status=="Completed",models.TL.status==1).count()
        data['completed_count'] = db_completed_count

        db_reallocated_count = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.work_status=="Reallocated",models.TL.status==1).count()
        data['reallocated_count'] = db_reallocated_count

        db_not_picked_count = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.work_status=="Not Picked",models.TL.status==1).count()
        data['not_picked_count'] = db_not_picked_count

        db_wip_count = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.work_status=="Work in Progress",models.TL.status==1).count()
        data['wip_count'] = db_wip_count

        db_chargable_count = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.type_of_activity=="CHARGABLE",models.TL.status==1).count()
        data['chargable_count'] = db_chargable_count

        db_non_chargable_count = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.type_of_activity=="Non-Charchable",models.TL.status==1).count()
        data['non_chargable_count'] = db_non_chargable_count

        db_hold_count = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.work_status=="Hold",models.TL.status==1).count()
        data['hold'] = db_hold_count

        db_training = db.query(models.TL).filter(models.TL.Assigned_By==user_id,models.TL.work_status=="End Of Day",models.TL.status==1).count()
        data['Training'] = db_training

        count_list.append(data)
        return count_list
    elif (user_role == "Admin"):
        db_completed_count = db.query(models.TL).filter(models.TL.work_status=="Completed",models.TL.status==1).count()
        data['completed_count'] = db_completed_count

        db_reallocated_count = db.query(models.TL).filter(models.TL.work_status=="Reallocated",models.TL.status==1).count()
        data['reallocated_count'] = db_reallocated_count

        db_not_picked_count = db.query(models.TL).filter(models.TL.work_status=="Not Picked",models.TL.status==1).count()
        data['not_picked_count'] = db_not_picked_count

        db_wip_count = db.query(models.TL).filter(models.TL.work_status=="Work in Progress",models.TL.status==1).count()
        data['wip_count'] = db_wip_count

        db_chargable_count = db.query(models.TL).filter(models.TL.type_of_activity=="CHARGABLE",models.TL.status==1).count()
        data['chargable_count'] = db_chargable_count

        db_non_chargable_count = db.query(models.TL).filter(models.TL.type_of_activity=="Non-Charchable",models.TL.status==1).count()
        data['non_chargable_count'] = db_non_chargable_count

        db_hold_count = db.query(models.TL).filter(models.TL.work_status=="Hold",models.TL.status==1).count()
        data['hold'] = db_hold_count

        db_training = db.query(models.TL).filter(models.TL.work_status=="End Of Day",models.TL.status==1).count()
        data['Training'] = db_training

        count_list.append(data)
        return count_list

#-------------------------------------------------------------------------------------------

def get_break_time_info(db:Session):
    db_res = db.query(models.TL).all()
    user_list = []
    for row in db_res:
        data = {}
        time_format = "%Y-%m-%d %H:%M:%S"
        time = datetime.strptime(row.break_time_str, time_format) 
        if time.hour > 1:
            data['user_name'] = row._user_table1.username
            data['user_id']=row.Assigned_To
            data['break_time'] = row.break_time_str
            user_list.append(data)
            return user_list
        elif time.hour ==1:
            if time.minute>0:
                data['user_name'] = row._user_table1.username
                data['user_id']=row.Assigned_To
                data['break_time'] = row.break_time_str
                user_list.append(data)
                return user_list
            else:
                return []         
        else:
            return user_list
#-------------------------------------------------------------------------------------------

async def get_reports(db:Session,fields:str):
    column_set = fields.split(",")
    db_res = db.query(models.TL).all()
    df = pd.DataFrame([r.__dict__ for r in db_res])
    new_df = df[column_set]
    return new_df

#-------------------------------------------------------------------------------------------

# def break_start(db:Session,service_id:int,remarks:str,user_id:int):
#     db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
#     db_res.work_status = "Break"
#     db.commit()
#     current_datetime = datetime.now()
#     current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
#     db_insert = models.BREAK(Service_ID = service_id,user_id=user_id,break_time_start = current_datetime_str,remarks=remarks)
#     db.add(db_insert)
#     db.commit()
#     return "Success"

def break_start(db: Session, service_id: int, remarks: str, user_id: int):

    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    if db_res.work_status == "Break":
        return "Already on Break"
    db_res.work_status = "Break"
    db.commit()
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    db_insert = models.BREAK(
        Service_ID=service_id,
        user_id=user_id,
        break_time_start=current_datetime_str,
        remarks=remarks
    )
    db.add(db_insert)
    db.commit()

    return "Success"

def break_end(db:Session,service_id:int,user_id:int):
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Work in Progress"
    db.commit()
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    db_res2 = db.query(models.BREAK).filter(
        models.BREAK.Service_ID == service_id,
        models.BREAK.user_id == user_id
    ).order_by(
        models.BREAK.id.desc()
    ).first()
    db_res2.break_time_end = current_datetime_str
    db.commit()
    return "Success"


def call_start(db:Session,service_id:int,remarks:str,user_id:int):
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Clarification Call"
    db.commit()
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    db_insert = models.CALL(Service_ID = service_id,user_id=user_id,call_time_start = current_datetime_str,remarks=remarks)
    db.add(db_insert)
    db.commit()
    return "Success"

def call_end(db:Session,service_id:int,user_id:int):
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Work in Progress"
    db.commit()
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    db_res2 = db.query(models.CALL).filter(
        models.CALL.Service_ID == service_id,
        models.CALL.user_id == user_id
    ).order_by(
        models.CALL.id.desc()
    ).first()
    db_res2.call_time_end = current_datetime_str
    db.commit()
    return "Success"


def end_of_day_start(db:Session,service_id:int,remarks:str,user_id:int):
    
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "End Of Day"
    db.commit()

    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    db_insert = models.END_OF_DAY(Service_ID = service_id,user_id=user_id,end_time_start = current_datetime_str,remarks=remarks)
    db.add(db_insert)
    db.commit()
    
    return "Success"

def end_of_day_end(db:Session,service_id:int,user_id:int):
    
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Work in Progress"
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    db_res.reallocated_time = current_datetime_str
    db.commit()
    
    db_res2 = db.query(models.END_OF_DAY).filter(
        models.END_OF_DAY.Service_ID == service_id,
        models.END_OF_DAY.user_id == user_id
    ).order_by(
        models.END_OF_DAY.id.desc()
    ).first()
    db_res2.end_time_end = current_datetime_str
    db.commit()
    return "Success"


def hold_start(db:Session,service_id:int,remarks:str,user_id:int):
    
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Hold"
    db.commit()

    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    db_insert = models.HOLD(Service_ID = service_id,user_id=user_id,hold_time_start=current_datetime_str,remarks=remarks)
    db.add(db_insert)
    db.commit()
    
    return "Success"

def hold_end(db:Session,service_id:int,user_id:int):
    
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Work in Progress"
    db.commit()
    
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    db_res2 = db.query(models.HOLD).filter(
        models.HOLD.Service_ID == service_id,
        models.HOLD.user_id == user_id
    ).order_by(
        models.HOLD.id.desc()
    ).first()
    db_res2.hold_time_end = current_datetime_str
    db.commit()
    return "Success"


def meeting_start(db:Session,service_id:int,remarks:str,user_id:int):
    
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Meeting"
    db.commit()

    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    db_insert = models.MEETING(Service_ID = service_id,user_id=user_id,meeting_time_start=current_datetime_str,remarks=remarks)
    db.add(db_insert)
    db.commit()
    
    return "Success"

def meeting_end(db:Session,service_id:int,user_id:int):
    
    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Work in Progress"
    db.commit()
    
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    
    db_res2 = db.query(models.MEETING).filter(
        models.MEETING.Service_ID == service_id,
        models.MEETING.user_id == user_id
    ).order_by(
        models.MEETING.id.desc()
    ).first()
    db_res2.meeting_time_end = current_datetime_str
    db.commit()
    return "Success"

def Completed(db:Session,service_id:int,remarks:str,count:str):
    
    current_datetime = datetime.now()
    current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

    db_res = db.query(models.TL).filter(models.TL.Service_ID == service_id).first()
    db_res.work_status = "Completed"
    db_res.no_of_items = count
    db_res.completed_time = current_datetime_str
    db_res.remarks = remarks
    db.commit()
    return "Success"


#----------------------------------------------------------------------------
def User_Wise_Day_Wise_Part_1(db: Session, picked_date: str, to_date: str):
    date_time_formate_string = '%Y-%m-%d %H:%M:%S'
    list_data = []

    date_time1 = datetime.now()
    todatedd = datetime.strptime(to_date, "%Y-%m-%d")

    db_res = db.query(models.TL).filter(models.TL.status == 1,
        or_(
            models.TL.working_time.between(picked_date, to_date),
            models.TL.reallocated_time.between(picked_date, to_date),
            
        )
    ).all()

    for row in db_res:
        data = {}
        data["date"] = datetime.strptime(row.working_time, date_time_formate_string).date()
        data["user"] = row._user_table1.username
        data["Service_ID"] = row.Service_ID
        data["scope"] = row.Scope
        data["subscopes"] = row.From
        data["entity"] = row.name_of_entity
        data["status"] = row.work_status
        data["type_of_activity"] = row.type_of_activity
        data["Nature_of_Work"] = row._nature_of_work.work_name
        data["gst_tan"] = row.gst_tan
        data["estimated_d_o_d"] =  row.estimated_d_o_d
        data["estimated_time"] =  row.estimated_time
        # username = db.query(User_table).filter(User.user_id == row.Assigned_To).first()
        data["member_name"] = row._user_table1.firstname +' '+ row._user_table1.lastname
        
        date_time2 = datetime.strptime(row.working_time, date_time_formate_string)
        time_diff = date_time1 - date_time2
        work_hour_hours_diff = time_diff


        # -----end of the day
        # db_res2 = db.query(models.END_OF_DAY).filter(
        #     models.END_OF_DAY.Service_ID == row.Service_ID,
        #     cast(models.END_OF_DAY.end_time_start, Date) >= todatedd
        # ).all()

        
        
        
        # end_hour_diff = timedelta(hours=0)
        # date_time_format_string = '%Y-%m-%d %H:%M:%S'
        # for row2 in db_res2:
        #     if row2.end_time_end and row2.end_time_start:

        #         print(row.working_time,row2.end_time_end,row2.end_time_start)
                

        #         datetime_obj1 = datetime.strptime(row2.end_time_start, "%Y-%m-%d %H:%M:%S")
        #         datetime_obj2 = datetime.strptime(row2.end_time_end, "%Y-%m-%d %H:%M:%S")

        #         # Calculate the difference
        #         time_difference = datetime_obj2 - datetime_obj1

        #         print(time_difference,'tttttttttttttttttttttttttttttttttttttt')
        #         current_datetime = datetime.now()
        #         current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")


        #         date_time11 = datetime.strptime(row2.end_time_end, date_time_format_string)
        #         date_time22 = datetime.strptime(row2.end_time_start, date_time_format_string)
        #         time_diff = date_time11 - date_time22
        #         end_hour_diff += time_diff
        #         print(time_diff,'tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt')
        #     else:
        #         if not (row.work_status == "Completed" or (row.work_status == "in_progress" or row.work_status == "End Of Day")):
        #             print(row.working_time,row2.end_time_end,row2.end_time_start)
                    

        #             datetime_obj1 = datetime.strptime(row2.end_time_start, "%Y-%m-%d %H:%M:%S")
        #             datetime_obj2 = datetime.strptime(row2.end_time_end, "%Y-%m-%d %H:%M:%S")

        #             # Calculate the difference
        #             time_difference = datetime_obj2 - datetime_obj1

        #             print(time_difference,'tttttttttttttttttttttttttttttttttttttt')
        #             current_datetime = datetime.now()
        #             current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        #             print(current_datetime_str,'####################################################')

        #             print(row.working_time)

        #             datetime_obj1 = datetime.strptime(row2.end_time_start, "%Y-%m-%d %H:%M:%S")
        #             minus = datetime.now()
        #             minus_datetime_str = minus.strftime("%Y-%m-%d %H:%M:%S")

        #             time_difference =  datetime_obj1 - minus_datetime_str


        #             end_hour_diff += time_difference


       
        a = timedelta(hours=0)
        b = timedelta(hours=0)
        if row.work_status == "Reallocated":
            db_res2 = db.query(models.REALLOCATED).filter(
                models.REALLOCATED.Service_ID == row.Service_ID,
                models.REALLOCATED.re_time_start >= picked_date,
                models.REALLOCATED.re_time_end <= to_date
            ).all()

            re_hour_diff = timedelta(hours=0)

            for row2 in db_res2:
                if row2.re_time_start and row2.re_time_end:
                    date_time2r = datetime.strptime(row2.re_time_start, date_time_formate_string)
                    re_time_diff = date_time1 - date_time2r
                    re_hour_diff += re_time_diff
                    data["reallocated"] = re_hour_diff
            a = work_hour_hours_diff
        if row.work_status == "Completed":
            a = work_hour_hours_diff
        else:
            b = work_hour_hours_diff

        # ----- Hold Hour ------
        db_res2 = db.query(models.HOLD).filter(
            models.HOLD.Service_ID == row.Service_ID,
            models.HOLD.hold_time_start >= picked_date,
            models.HOLD.hold_time_end <= to_date
        ).all()

        hold_hour_diff = timedelta(hours=0)

        for row2 in db_res2:
            if row2.hold_time_end and row2.hold_time_start:
                date_time11 = datetime.strptime(row2.hold_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.hold_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                hold_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.hold_time_start, date_time_formate_string)
                    hold_hour_diff +=  time1

        data["hold"] = hold_hour_diff

        # ----- Meeting Hour ------
        db_res2 = db.query(models.MEETING).filter(
            models.MEETING.Service_ID == row.Service_ID,
            models.MEETING.meeting_time_start >= picked_date,
            models.MEETING.meeting_time_end <= to_date
        ).all()

        meet_hour_diff = timedelta(hours=0)

        for row2 in db_res2:
            if row2.meeting_time_end and row2.meeting_time_start:
                date_time11 = datetime.strptime(row2.meeting_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                meet_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                    meet_hour_diff +=   time1



        data["meeting"] = meet_hour_diff

        # ----- Break Hour ------
        db_res2 = db.query(models.BREAK).filter(
            models.BREAK.Service_ID == row.Service_ID,
            models.BREAK.break_time_start >= picked_date,
            models.BREAK.break_time_end <= to_date
        ).all()

        break_hour_diff = timedelta(hours=0)

        for row2 in db_res2:
            if row2.break_time_end and row2.break_time_start:
                date_time11 = datetime.strptime(row2.break_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.break_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                break_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.break_time_start, date_time_formate_string)
                 
                    break_hour_diff += time1

        data["break"] = break_hour_diff

        # ----- Call Hour ------
        db_res2 = db.query(models.CALL).filter(
            models.CALL.Service_ID == row.Service_ID,
            models.CALL.call_time_start >= picked_date,
            models.CALL.call_time_end <= to_date
        ).all()

        call_hour_diff = timedelta(hours=0)

        for row2 in db_res2:
            if row2.call_time_end and row2.call_time_start:
                date_time11 = datetime.strptime(row2.call_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.call_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                call_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.call_time_start, date_time_formate_string)
                   
                    call_hour_diff += time1

        data["call"] = call_hour_diff


        # -----end of the day
        temp = ''
        
        db_res2 = db.query(models.END_OF_DAY).filter(
            models.END_OF_DAY.Service_ID == row.Service_ID,
            models.END_OF_DAY.end_time_start>=picked_date,
            models.END_OF_DAY.end_time_start<=to_date
        ).all()

        count = db.query(models.END_OF_DAY).filter(
            models.END_OF_DAY.Service_ID == row.Service_ID,
            models.END_OF_DAY.end_time_start>=picked_date
        ).count()

        time_diff = timedelta(hours=0)
        if count >= 1 :
            for rom in db_res2:
                if rom.end_time_end == "":
                    temp = rom.end_time_start
                    parsed_date = datetime.strptime(str(temp), '%Y-%m-%d %H:%M:%S')
                    date_time22 = date_time1
                    time_diff += date_time22 - parsed_date
                else:
                    temp = rom.end_time_start
                    parsed_date = datetime.strptime(str(temp), '%Y-%m-%d %H:%M:%S')
                    date_time11 = datetime.strptime(rom.end_time_end, date_time_formate_string)
                    time_diff += date_time11 - parsed_date
        data["end_of_day"] = time_diff
        
        if row.work_status == "Completed":
            e_o_d = data["end_of_day"]
            data["in_progress"] = timedelta(hours=0)
            data["completed"] = (datetime.strptime(row.completed_time, date_time_formate_string) - datetime.strptime(row.working_time, date_time_formate_string)) - (call_hour_diff + break_hour_diff + meet_hour_diff + hold_hour_diff + e_o_d)
            # data["completed"] = (a + b) - (call_hour_diff + break_hour_diff + meet_hour_diff + hold_hour_diff + e_o_d)
        else:
            e_o_d = data["end_of_day"]
            data["completed"] = timedelta(hours=0)
            if row.work_status != "End Of Day":
                data["in_progress"] = (a + b) - (call_hour_diff + break_hour_diff + meet_hour_diff + hold_hour_diff + e_o_d)
            else:
                data["in_progress"] = (a + b) - (call_hour_diff + break_hour_diff + meet_hour_diff + hold_hour_diff + e_o_d)
            print("in progress - ",data["in_progress"])

        # data["total_time_taken"] = call_hour_diff + break_hour_diff + meet_hour_diff + hold_hour_diff + data["completed"] + data["in_progress"]

        data["total_time_taken"] =  (data["in_progress"] + data["completed"] )
        # data["second_report_data"] = call_hour_diff + hold_hour_diff + data["completed"] + data["in_progress"]
        data["second_report_data"] =  data["completed"] + data["in_progress"]

        
#--------------------------------------------------------------------------------------------------------------------------------------
        # ----- HOLD Hour ------
        holdchargable = db.query(models.HOLD).join(
            models.TL, models.HOLD.Service_ID == models.TL.Service_ID
        ).filter(
            models.HOLD.Service_ID == row.Service_ID,
            models.HOLD.hold_time_start >= picked_date,
            models.HOLD.hold_time_end <= to_date,
            models.TL.type_of_activity == 'CHARGABLE'
        ).all()

        holdchargable_hour_diff = timedelta(hours=0)

        for row2 in holdchargable:
            if row2.hold_time_end and row2.hold_time_start:
                date_time11 = datetime.strptime(row2.hold_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.hold_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                holdchargable_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.hold_time_start, date_time_formate_string)
                   
                    holdchargable_hour_diff += time1


        
        
        # ----- Meeting Hour ------
        Meetingchargable = db.query(models.MEETING).join(
            models.TL, models.MEETING.Service_ID == models.TL.Service_ID
        ).filter(
            models.MEETING.Service_ID == row.Service_ID,
            models.MEETING.meeting_time_start >= picked_date,
            models.MEETING.meeting_time_end <= to_date,
            models.TL.type_of_activity == 'CHARGABLE'
        ).all()

        meetch_hour_diff = timedelta(hours=0)

        for row2 in Meetingchargable:
            if row2.meeting_time_end and row2.meeting_time_start:
                date_time11 = datetime.strptime(row2.meeting_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                meetch_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                    
                    meetch_hour_diff += time1


        
        
        # ----- Break Hour ------
        Breakchargable = db.query(models.BREAK).join(
            models.TL, models.BREAK.Service_ID == models.TL.Service_ID
        ).filter(
            models.BREAK.Service_ID == row.Service_ID,
            models.BREAK.break_time_start >= picked_date,
            models.BREAK.break_time_end <= to_date,
            models.TL.type_of_activity == 'CHARGABLE'
        ).all()

        breakch_hour_diff = timedelta(hours=0)

        for row2 in Breakchargable:
            if row2.break_time_end and row2.break_time_start:
                date_time11 = datetime.strptime(row2.break_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.break_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                breakch_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.break_time_start, date_time_formate_string)
                  
                    breakch_hour_diff += time1


        
        
        # ----- Call Hour ------
        Callchargable = db.query(models.CALL).join(
            models.TL, models.CALL.Service_ID == models.TL.Service_ID
        ).filter(
            models.CALL.Service_ID == row.Service_ID,
            models.CALL.call_time_start >= picked_date,
            models.CALL.call_time_end <= to_date,
            models.TL.type_of_activity == 'CHARGABLE'
        ).all()

        callch_hour_diff = timedelta(hours=0)

        for row2 in Callchargable:
            if row2.call_time_end and row2.call_time_start:
                date_time11 = datetime.strptime(row2.call_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.call_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                callch_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.call_time_start, date_time_formate_string)
                 
                    callch_hour_diff += time1

        # -----end of the day
        endch = db.query(models.END_OF_DAY).join(
            models.TL, models.END_OF_DAY.Service_ID == models.TL.Service_ID
        ).filter(
            models.END_OF_DAY.Service_ID == row.Service_ID,
            models.END_OF_DAY.end_time_start >= picked_date,
            models.END_OF_DAY.end_time_end <= to_date,
            models.TL.type_of_activity == 'CHARGABLE'
        ).all()

        endch_hour_diff = timedelta(hours=0)

        for row2 in endch:
            if row2.end_time_end and row2.end_time_start:
                date_time11 = datetime.strptime(row2.end_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.end_time_start, date_time_formate_string)
                time_diff = date_time22 - date_time11
                endch_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.end_time_start, date_time_formate_string)
                   
                    endch_hour_diff += time1

        data["endch_hour_diff"] = endch_hour_diff
        if row.type_of_activity == "CHARGABLE":
            data["chargable_time"] = data["in_progress"] + data["completed"]
        else:
            data["chargable_time"] = timedelta(hours=0)

        parsed_time = datetime.strptime(data["estimated_time"], '%H:%M')
        time_delta = timedelta(hours=parsed_time.hour, minutes=parsed_time.minute)

        data["difference_a_b"] = time_delta - data["chargable_time"]
#--------------------------------------------------------------------------------------------------------------------------------------	



#--------------------------------------------------------------------------------------------------------------------------------------
        # ----- HOLD Hour ------
        holdchargable = db.query(models.HOLD).join(
            models.TL, models.HOLD.Service_ID == models.TL.Service_ID
        ).filter(
            models.HOLD.Service_ID == row.Service_ID,
            models.HOLD.hold_time_start >= picked_date,
            models.HOLD.hold_time_end <= to_date,
            models.TL.type_of_activity == 'Non-Charchable'
        ).all()

        holdchargable_hour_diff = timedelta(hours=0)

        for row2 in holdchargable:
            if row2.hold_time_end and row2.hold_time_start:
                date_time11 = datetime.strptime(row2.hold_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.hold_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                holdchargable_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.hold_time_start, date_time_formate_string)
                   
                    holdchargable_hour_diff += time1

        
        
        # ----- Meeting Hour ------
        Meetingchargable = db.query(models.MEETING).join(
            models.TL, models.MEETING.Service_ID == models.TL.Service_ID
        ).filter(
            models.MEETING.Service_ID == row.Service_ID,
            models.MEETING.meeting_time_start >= picked_date,
            models.MEETING.meeting_time_end <= to_date,
            models.TL.type_of_activity == 'Non-Charchable'
        ).all()

        meetch_hour_diff = timedelta(hours=0)

        for row2 in Meetingchargable:
            if row2.meeting_time_end and row2.meeting_time_start:
                date_time11 = datetime.strptime(row2.meeting_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                meetch_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                   
                    meetch_hour_diff += time1

        
        
        # ----- Break Hour ------
        Breakchargable = db.query(models.BREAK).join(
            models.TL, models.BREAK.Service_ID == models.TL.Service_ID
        ).filter(
            models.BREAK.Service_ID == row.Service_ID,
            models.BREAK.break_time_start >= picked_date,
            models.BREAK.break_time_end <= to_date,
            models.TL.type_of_activity == 'Non-Charchable'
        ).all()

        breakch_hour_diff = timedelta(hours=0)

        for row2 in Breakchargable:
            if row2.break_time_end and row2.break_time_start:
                date_time11 = datetime.strptime(row2.break_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.break_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                breakch_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.break_time_start, date_time_formate_string)
                    
                    breakch_hour_diff += time1


        
        
        # ----- Call Hour ------
        Callchargable = db.query(models.CALL).join(
            models.TL, models.CALL.Service_ID == models.TL.Service_ID
        ).filter(
            models.CALL.Service_ID == row.Service_ID,
            models.CALL.call_time_start >= picked_date,
            models.CALL.call_time_end <= to_date,
            models.TL.type_of_activity == 'Non-Charchable'
        ).all()

        callch_hour_diff = timedelta(hours=0)

        for row2 in Callchargable:
            if row2.call_time_end and row2.call_time_start:
                date_time11 = datetime.strptime(row2.call_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.call_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                callch_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.call_time_start, date_time_formate_string)
                  
                    callch_hour_diff += time1

        # -----end of the day
        endch = db.query(models.END_OF_DAY).join(
            models.TL, models.END_OF_DAY.Service_ID == models.TL.Service_ID
        ).filter(
            models.END_OF_DAY.Service_ID == row.Service_ID,
            models.END_OF_DAY.end_time_start >= picked_date,
            models.END_OF_DAY.end_time_end <= to_date,
            models.TL.type_of_activity == 'Non-Charchable'
        ).all()

        endch_hour_diff = timedelta(hours=0)

        for row2 in endch:
            if row2.end_time_end and row2.end_time_start:
                date_time11 = datetime.strptime(row2.end_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.end_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                endch_hour_diff += time_diff
            else :
                if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                    time1 =  datetime.now() - datetime.strptime(row2.end_time_start, date_time_formate_string)
                    endch_hour_diff += time1
	    

        data["endch_hour_diff"] = endch_hour_diff
        if row.type_of_activity == "Non-Charchable":
            data["Non_Charchable_time"] = endch_hour_diff 
        else:
            data["Non_Charchable_time"] = timedelta(hours=0)
        data["chargable_and_non_chargable"] = data["Non_Charchable_time"] + data["chargable_time"]
#--------------------------------------------------------------------------------------------------------------------------------------	



        str_temp = ""
        str_temper = ""

        if row.work_status == "Work in Progress":

            data["third_report_data"] = ""

        elif row.work_status == "Hold":

            db_res3 = db.query(models.HOLD).filter(
                models.HOLD.Service_ID == row.Service_ID,
            ).all()
            for hold_obj in db_res3:
                data["third_report_data"] = hold_obj.remarks
                str_temper = hold_obj.remarks

        elif row.work_status == "Meeting":

            db_res3 = db.query(models.MEETING).filter(
                models.MEETING.Service_ID == row.Service_ID,
            ).all()
            for meet_obj in db_res3:
                data["third_report_data"] = meet_obj.remarks


        elif row.work_status == "Break":
            db_res3 = db.query(models.BREAK).filter(
                models.BREAK.Service_ID == row.Service_ID,
            ).all()
            for break_obj in db_res3:
                
                data["third_report_data"] = break_obj.remarks
                
        elif row.work_status == "Clarification Call":
            db_res3 = db.query(models.CALL).filter(
                models.CALL.Service_ID == row.Service_ID,
            ).all()
            for call_obj in db_res3:
                
                data["third_report_data"] = call_obj.remarks

        elif row.work_status == "Completed":
            data["third_report_data"] = row.remarks

        if row.work_status == "Completed":
            try:
                db_res3 = db.query(models.HOLD).filter(
                    models.HOLD.Service_ID == row.Service_ID,
                ).all()
                for hold_obj in db_res3:
                    str_temp = str_temp + hold_obj.remarks + ","
            except:
                str_temp = ""
            try:
                db_res3 = db.query(models.MEETING).filter(
                    models.MEETING.Service_ID == row.Service_ID,
                ).all()
                for meet_obj in db_res3:

                    str_temp = str_temp + meet_obj.remarks + ","

            except:
                str_temp = ""
            try:
                db_res3 = db.query(models.BREAK).filter(
                    models.BREAK.Service_ID == row.Service_ID,
                ).all()
                for break_obj in db_res3:
                    str_temp = str_temp + break_obj.remarks + ","
            except:
                str_temp = ""
            try:
                db_res3 = db.query(models.CALL).filter(
                    models.CALL.Service_ID == row.Service_ID,
                ).all()
                for call_obj in db_res3:
                    str_temp = str_temp + call_obj.remarks + ","
                str_temp = str_temp + row.remarks + ","
            except:
                str_temp = ""

        data["fourth_report"] = row.no_of_items
        data["fourth_report2"] = str_temp
        data["fifth_report"] = str_temper        
        list_data.append(data)
    def convert_values(d):
        return dict(map(lambda item: (item[0], str(item[1]).split('.')[0] if not isinstance(item[1], (dict, list)) else item[1]), d.items()))

    converted_list_of_dicts = [convert_values(d) for d in list_data]
    return converted_list_of_dicts

#-------------------------------------------------------------------------------------------

def insert_tds(db:Session,tds_str:str):
   db_tds = models.tds(tds = tds_str)
   db.add(db_tds)
   try:
        db.commit()
        return "Success"
   except :
       db.rollback()
       return "Failure"

def get_tds(db:Session):
    return db.query(models.tds).filter(models.tds.tds_status==1).all()

def delete_tds(db:Session,tds_id:int):
    db_res = db.query(models.tds).filter(models.tds.tds_id==tds_id).first()
    db_res.tds_status = 0
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"

def update_tds(db:Session,tds_name:str,tds_id:int):
    db_res = db.query(models.tds).filter(models.tds.tds_id==tds_id).first()
    db_res.tds = tds_name
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"
    
#-------------------------------------------------------------------------------------------

def insert_gst(db:Session,gst_str:str):
   db_gst = models.gst(gst = gst_str)
   db.add(db_gst)
   try:
        db.commit()
        return "Success"
   except :
       db.rollback()
       return "Failure"

def get_gst(db:Session):
    return db.query(models.gst).filter(models.gst.gst_status==1).all()

def delete_gst(db:Session,gst_id:int):
    db_res = db.query(models.gst).filter(models.gst.gst_id==gst_id).first()
    db_res.gst_status = 0
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"

def update_gst(db:Session,gst:str,gst_id:int):
    db_res = db.query(models.gst).filter(models.gst.gst_id==gst_id).first()
    db_res.gst = gst
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"
    
#-------------------------------------------------------------------------------------------


def delete_entity(db:Session,record_service_id:int):
    db_res = db.query(models.TL).filter(models.TL.Service_ID==record_service_id).first()
    db_res.status = 0
    try:
        db.commit()
        return "Success"
    except:
        return "Failure"
    
#-------------------------------------------------------------------------------------------

def lastfivereports(db: Session, picked_date: str, to_date: str, reportoptions: str ):
    date_time_formate_string = '%Y-%m-%d %H:%M:%S'
    list_data = []

    # fetch_hold_data(db)

    d1 = picked_date
    d2 = to_date

    # Convert strings to datetime objects
    start_date = datetime.strptime(d1, '%Y-%m-%d')
    end_date = datetime.strptime(d2, '%Y-%m-%d')

    # Generate all dates in between and store as strings
    dates_list = []
    current_date = start_date

    while current_date <= end_date:
        
        dates_list.append(current_date.strftime('%Y-%m-%d'))
        current_date += timedelta(days=1)

#     # dates_list contains all dates as strings
    # print(dates_list)

    for item in dates_list:
        # print(item)
        list_data.append(report.user_wise_report(db,item,reportoptions))
        
    list_data = [item for item in list_data if item]
    return list_data

#----------------------------------------------------------------------------
def Hold_Wise_Day_Wise_Part(db: Session, picked_date: str, to_date: str):
    date_time_formate_string = '%Y-%m-%d %H:%M:%S'
    list_data = []

    # fetch_hold_data(db)

    date_time1 = datetime.now()
    # todatedd = datetime.strptime(to_date, "%Y-%m-%d")

    # db_res = db.query(models.TL).filter(models.TL.status == 1,
    #     or_(
    #         models.TL.working_time.between(picked_date, to_date),
    #         models.TL.reallocated_time.between(picked_date, to_date),
            
    #     )
    # ).all()

    list_data = []
    list_ddata1 = set()


    db_res2 = db.query(models.TL).filter(
        models.TL.status == 1,
        models.TL.working_time.between(picked_date, to_date)    
    )

    for row2 in db_res2:
        list_ddata1.add(row2.Service_ID)

    db_res2 = db.query(models.TL).filter(
        models.TL.status == 1,
        models.TL.Service_ID == models.HOLD.Service_ID,
        or_(
            models.HOLD.hold_time_end.between(picked_date, to_date),
            models.TL.working_time.between(picked_date, to_date)
        )
        
    )

    for row2 in db_res2:
        list_ddata1.add(row2.Service_ID)
    
    db_res2 = db.query(models.TL).filter(
        models.TL.status == 1,
        models.TL.Service_ID == models.END_OF_DAY.Service_ID,
        or_(
            models.END_OF_DAY.end_time_end.between(picked_date, to_date),
            models.TL.working_time.between(picked_date, to_date)
        )
    )

    for row2 in db_res2:
        list_ddata1.add(row2.Service_ID)
        

# final query
    db_res =  db.query(models.TL).filter(
        models.TL.status == 1,
        models.TL.Service_ID.in_(list_ddata1)
    ).all()


    for row in db_res:
        data = {}
        data["date"] = datetime.strptime(row.working_time, date_time_formate_string).date()
        data["user"] = row._user_table1.username
        data["Service_ID"] = row.Service_ID
        data["scope"] = row.Scope
        data["subscopes"] = row.From
        data["entity"] = row.name_of_entity
        data["status"] = row.work_status
        data["type_of_activity"] = row.type_of_activity
        data["Nature_of_Work"] = row._nature_of_work.work_name
        data["gst_tan"] = row.gst_tan
        data["estimated_d_o_d"] =  row.estimated_d_o_d
        data["estimated_time"] =  row.estimated_time
        # username = db.query(User_table).filter(User.user_id == row.Assigned_To).first()
        data["member_name"] = row._user_table1.firstname +' '+ row._user_table1.lastname
        
        date_time2 = datetime.strptime(row.working_time, date_time_formate_string)
        time_diff = date_time1 - date_time2
        work_hour_hours_diff = time_diff


        # -----end of the day
        # db_res2 = db.query(models.END_OF_DAY).filter(
        #     models.END_OF_DAY.Service_ID == row.Service_ID,
        #     cast(models.END_OF_DAY.end_time_start, Date) >= todatedd
        # ).all()

        
        
        
        # end_hour_diff = timedelta(hours=0)
        # date_time_format_string = '%Y-%m-%d %H:%M:%S'
        # for row2 in db_res2:
        #     if row2.end_time_end and row2.end_time_start:

        #         print(row.working_time,row2.end_time_end,row2.end_time_start)
                

        #         datetime_obj1 = datetime.strptime(row2.end_time_start, "%Y-%m-%d %H:%M:%S")
        #         datetime_obj2 = datetime.strptime(row2.end_time_end, "%Y-%m-%d %H:%M:%S")

        #         # Calculate the difference
        #         time_difference = datetime_obj2 - datetime_obj1

        #         print(time_difference,'tttttttttttttttttttttttttttttttttttttt')
        #         current_datetime = datetime.now()
        #         current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")


        #         date_time11 = datetime.strptime(row2.end_time_end, date_time_format_string)
        #         date_time22 = datetime.strptime(row2.end_time_start, date_time_format_string)
        #         time_diff = date_time11 - date_time22
        #         end_hour_diff += time_diff
        #         print(time_diff,'tttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttttt')
        #     else:
        #         if not (row.work_status == "Completed" or (row.work_status == "in_progress" or row.work_status == "End Of Day")):
        #             print(row.working_time,row2.end_time_end,row2.end_time_start)
                    

        #             datetime_obj1 = datetime.strptime(row2.end_time_start, "%Y-%m-%d %H:%M:%S")
        #             datetime_obj2 = datetime.strptime(row2.end_time_end, "%Y-%m-%d %H:%M:%S")

        #             # Calculate the difference
        #             time_difference = datetime_obj2 - datetime_obj1

        #             print(time_difference,'tttttttttttttttttttttttttttttttttttttt')
        #             current_datetime = datetime.now()
        #             current_datetime_str = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

        #             print(current_datetime_str,'####################################################')

        #             print(row.working_time)

        #             datetime_obj1 = datetime.strptime(row2.end_time_start, "%Y-%m-%d %H:%M:%S")
        #             minus = datetime.now()
        #             minus_datetime_str = minus.strftime("%Y-%m-%d %H:%M:%S")

        #             time_difference =  datetime_obj1 - minus_datetime_str


        #             end_hour_diff += time_difference


       
        a = timedelta(hours=0)
        b = timedelta(hours=0)
        if row.work_status == "Reallocated":
            db_res2 = db.query(models.REALLOCATED).filter(
                models.REALLOCATED.Service_ID == row.Service_ID,
                models.REALLOCATED.re_time_start >= picked_date,
                models.REALLOCATED.re_time_end <= to_date
            ).all()

            re_hour_diff = timedelta(hours=0)

            for row2 in db_res2:
                if row2.re_time_start and row2.re_time_end and (datetime.strptime(row2.re_time_start, date_time_formate_string).date()==datetime.strptime(row2.re_time_end, date_time_formate_string).date()):
                    date_time2r = datetime.strptime(row2.re_time_start, date_time_formate_string)
                    re_time_diff = date_time1 - date_time2r
                    re_hour_diff += re_time_diff
                    data["reallocated"] = re_hour_diff
            a = work_hour_hours_diff
        if row.work_status == "Completed":
            a = work_hour_hours_diff
        else:
            b = work_hour_hours_diff

        # ----- Hold Hour ------
        db_res2 = db.query(models.HOLD).filter(
            models.HOLD.Service_ID == row.Service_ID,
            models.HOLD.hold_time_start >= picked_date,
            models.HOLD.hold_time_end <= to_date
        ).all()

        hold_hour_diff = timedelta(hours=0)

        for row2 in db_res2:
            if (row2.hold_time_end and row2.hold_time_start) and (datetime.strptime(row2.hold_time_end, date_time_formate_string).date()==datetime.strptime(row2.hold_time_start, date_time_formate_string).date()):
                
                date_time11 = datetime.strptime(row2.hold_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.hold_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                # print(row.Service_ID,time_diff  ,'dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd')
                hold_hour_diff += time_diff
            # else :
            #     if not(row.work_status == "Completed" or row.work_status == "in_progress") :
            #         time1 =  datetime.now() - datetime.strptime(row2.hold_time_start, date_time_formate_string)
            #         hold_hour_diff +=  time1

        data["hold"] = hold_hour_diff


        # print(row.Service_ID,data["hold"],'lllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll')

        # ----- Meeting Hour ------
        db_res2 = db.query(models.MEETING).filter(
            models.MEETING.Service_ID == row.Service_ID,
            models.MEETING.meeting_time_start >= picked_date,
            models.MEETING.meeting_time_end <= to_date
        ).all()

        meet_hour_diff = timedelta(hours=0)

        for row2 in db_res2:
            if row2.meeting_time_end and row2.meeting_time_start  and (datetime.strptime(row2.meeting_time_end, date_time_formate_string).date()==datetime.strptime(row2.meeting_time_start, date_time_formate_string).date()):
                date_time11 = datetime.strptime(row2.meeting_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                meet_hour_diff += time_diff
            # else :
            #     if not(row.work_status == "Completed" or row.work_status == "in_progress"):
            #         time1 =  datetime.now() - datetime.strptime(row2.meeting_time_start, date_time_formate_string)
            #         meet_hour_diff +=   time1



        data["meeting"] = meet_hour_diff

        # ----- Break Hour ------
        db_res2 = db.query(models.BREAK).filter(
            models.BREAK.Service_ID == row.Service_ID,
            models.BREAK.break_time_start >= picked_date,
            models.BREAK.break_time_end <= to_date
        ).all()

        break_hour_diff = timedelta(hours=0)

        for row2 in db_res2:
            if row2.break_time_end and row2.break_time_start   and (datetime.strptime(row2.break_time_end, date_time_formate_string).date()==datetime.strptime(row2.break_time_start , date_time_formate_string).date()):
                date_time11 = datetime.strptime(row2.break_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.break_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                break_hour_diff += time_diff
            # else :
            #     if not(row.work_status == "Completed" or row.work_status == "in_progress"):
            #         time1 =  datetime.now() - datetime.strptime(row2.break_time_start, date_time_formate_string)
                 
            #         break_hour_diff += time1

        data["break"] = break_hour_diff

        # ----- Call Hour ------
        db_res2 = db.query(models.CALL).filter(
            models.CALL.Service_ID == row.Service_ID,
            models.CALL.call_time_start >= picked_date,
            models.CALL.call_time_end <= to_date
        ).all()

        call_hour_diff = timedelta(hours=0)

        for row2 in db_res2:
            if row2.call_time_end and row2.call_time_start    and (datetime.strptime(row2.call_time_end, date_time_formate_string).date()==datetime.strptime(row2.call_time_start  , date_time_formate_string).date()):
                date_time11 = datetime.strptime(row2.call_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.call_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                call_hour_diff += time_diff
            # else :
            #     if not(row.work_status == "Completed" or row.work_status == "in_progress"):
            #         time1 =  datetime.now() - datetime.strptime(row2.call_time_start, date_time_formate_string)
                   
            #         call_hour_diff += time1

        data["call"] = call_hour_diff


        # -----end of the day
        temp = ''
        
        db_res2 = db.query(models.END_OF_DAY).filter(
            models.END_OF_DAY.Service_ID == row.Service_ID,
            models.END_OF_DAY.end_time_start>=picked_date,
            models.END_OF_DAY.end_time_start<=to_date
        ).all()

        count = db.query(models.END_OF_DAY).filter(
            models.END_OF_DAY.Service_ID == row.Service_ID,
            models.END_OF_DAY.end_time_start>=picked_date
        ).count()

        time_diff = timedelta(hours=0)
        if count >= 1 :
            for rom in db_res2:
                if rom.end_time_end == "":
                    temp = rom.end_time_start
                    parsed_date = datetime.strptime(str(temp), '%Y-%m-%d %H:%M:%S')
                    date_time22 = date_time1
                    time_diff += date_time22 - parsed_date
                else:
                    temp = rom.end_time_start
                    parsed_date = datetime.strptime(str(temp), '%Y-%m-%d %H:%M:%S')
                    date_time11 = datetime.strptime(rom.end_time_end, date_time_formate_string)
                    time_diff += date_time11 - parsed_date
        data["end_of_day"] = time_diff
        
        if row.work_status == "Completed":
            e_o_d = data["end_of_day"]
            data["in_progress"] = timedelta(hours=0)
            data["completed"] = (datetime.strptime(row.completed_time, date_time_formate_string) - datetime.strptime(row.working_time, date_time_formate_string)) - (call_hour_diff + break_hour_diff + meet_hour_diff + hold_hour_diff + e_o_d)
            # data["completed"] = (a + b) - (call_hour_diff + break_hour_diff + meet_hour_diff + hold_hour_diff + e_o_d)
        else:
            e_o_d = data["end_of_day"]
            data["completed"] = timedelta(hours=0)
            if row.work_status != "End Of Day":
                data["in_progress"] = (a + b) - (call_hour_diff + break_hour_diff + meet_hour_diff + hold_hour_diff + e_o_d)
            else:
                data["in_progress"] = (a + b) - (call_hour_diff + break_hour_diff + meet_hour_diff + hold_hour_diff + e_o_d)
            print("in progress - ",data["in_progress"])

        # data["total_time_taken"] = call_hour_diff + break_hour_diff + meet_hour_diff + hold_hour_diff + data["completed"] + data["in_progress"]

        data["total_time_taken"] =  (data["in_progress"] + data["completed"] )
        # data["second_report_data"] = call_hour_diff + hold_hour_diff + data["completed"] + data["in_progress"]
        data["second_report_data"] =  data["completed"] + data["in_progress"]

        
#--------------------------------------------------------------------------------------------------------------------------------------
        # ----- HOLD Hour ------
        holdchargable = db.query(models.HOLD).join(
            models.TL, models.HOLD.Service_ID == models.TL.Service_ID
        ).filter(
            models.HOLD.Service_ID == row.Service_ID,
            models.HOLD.hold_time_start >= picked_date,
            models.HOLD.hold_time_end <= to_date,
            models.TL.type_of_activity == 'CHARGABLE'
        ).all()

        holdchargable_hour_diff = timedelta(hours=0)

        for row2 in holdchargable:
            if row2.hold_time_end and row2.hold_time_start   and (datetime.strptime(row2.hold_time_end, date_time_formate_string).date()==datetime.strptime(row2.hold_time_start  , date_time_formate_string).date()):
                date_time11 = datetime.strptime(row2.hold_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.hold_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                holdchargable_hour_diff += time_diff
            # else :
            #     if not(row.work_status == "Completed" or row.work_status == "in_progress"):
            #         time1 =  datetime.now() - datetime.strptime(row2.hold_time_start, date_time_formate_string)
                   
            #         holdchargable_hour_diff += time1


        
        
        # ----- Meeting Hour ------
        Meetingchargable = db.query(models.MEETING).join(
            models.TL, models.MEETING.Service_ID == models.TL.Service_ID
        ).filter(
            models.MEETING.Service_ID == row.Service_ID,
            models.MEETING.meeting_time_start >= picked_date,
            models.MEETING.meeting_time_end <= to_date,
            models.TL.type_of_activity == 'CHARGABLE'
        ).all()

        meetch_hour_diff = timedelta(hours=0)

        for row2 in Meetingchargable:
            if row2.meeting_time_end and row2.meeting_time_start   and (datetime.strptime(row2.meeting_time_end, date_time_formate_string).date()==datetime.strptime(row2.meeting_time_start  , date_time_formate_string).date()):
                date_time11 = datetime.strptime(row2.meeting_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                meetch_hour_diff += time_diff
            # else :
            #     if not(row.work_status == "Completed" or row.work_status == "in_progress"):
            #         time1 =  datetime.now() - datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                    
            #         meetch_hour_diff += time1


        
        
        # ----- Break Hour ------
        Breakchargable = db.query(models.BREAK).join(
            models.TL, models.BREAK.Service_ID == models.TL.Service_ID
        ).filter(
            models.BREAK.Service_ID == row.Service_ID,
            models.BREAK.break_time_start >= picked_date,
            models.BREAK.break_time_end <= to_date,
            models.TL.type_of_activity == 'CHARGABLE'
        ).all()

        breakch_hour_diff = timedelta(hours=0)

        for row2 in Breakchargable:
            if row2.break_time_end and row2.break_time_start   and (datetime.strptime( row2.break_time_end, date_time_formate_string).date()==datetime.strptime(row2.break_time_start , date_time_formate_string).date()):
                date_time11 = datetime.strptime(row2.break_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.break_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                breakch_hour_diff += time_diff
            # else :
            #     if not(row.work_status == "Completed" or row.work_status == "in_progress"):
            #         time1 =  datetime.now() - datetime.strptime(row2.break_time_start, date_time_formate_string)
                  
            #         breakch_hour_diff += time1


        
        
        # ----- Call Hour ------
        Callchargable = db.query(models.CALL).join(
            models.TL, models.CALL.Service_ID == models.TL.Service_ID
        ).filter(
            models.CALL.Service_ID == row.Service_ID,
            models.CALL.call_time_start >= picked_date,
            models.CALL.call_time_end <= to_date,
            models.TL.type_of_activity == 'CHARGABLE'
        ).all()

        callch_hour_diff = timedelta(hours=0)

        for row2 in Callchargable:
            if row2.call_time_end and row2.call_time_start   and (datetime.strptime( row2.call_time_end, date_time_formate_string).date()==datetime.strptime(row2.call_time_start  , date_time_formate_string).date()):
                date_time11 = datetime.strptime(row2.call_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.call_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                callch_hour_diff += time_diff
            # else :
            #     if not(row.work_status == "Completed" or row.work_status == "in_progress"):
            #         time1 =  datetime.now() - datetime.strptime(row2.call_time_start, date_time_formate_string)
                 
            #         callch_hour_diff += time1

        # -----end of the day
        endch = db.query(models.END_OF_DAY).join(
            models.TL, models.END_OF_DAY.Service_ID == models.TL.Service_ID
        ).filter(
            models.END_OF_DAY.Service_ID == row.Service_ID,
            models.END_OF_DAY.end_time_start >= picked_date,
            models.END_OF_DAY.end_time_end <= to_date,
            models.TL.type_of_activity == 'CHARGABLE'
        ).all()

        endch_hour_diff = timedelta(hours=0)

        for row2 in endch:
            if row2.end_time_end and row2.end_time_start and (datetime.strptime( row2.end_time_end , date_time_formate_string).date()==datetime.strptime(row2.end_time_start  , date_time_formate_string).date()):
                date_time11 = datetime.strptime(row2.end_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.end_time_start, date_time_formate_string)
                time_diff = date_time22 - date_time11
                endch_hour_diff += time_diff
            # else :
            #     if not(row.work_status == "Completed" or row.work_status == "in_progress"):
            #         time1 =  datetime.now() - datetime.strptime(row2.end_time_start, date_time_formate_string)
                   
            #         endch_hour_diff += time1

        data["endch_hour_diff"] = endch_hour_diff
        if row.type_of_activity == "CHARGABLE":
            data["chargable_time"] = data["in_progress"] + data["completed"]
        else:
            data["chargable_time"] = timedelta(hours=0)

        parsed_time = datetime.strptime(data["estimated_time"], '%H:%M')
        time_delta = timedelta(hours=parsed_time.hour, minutes=parsed_time.minute)

        data["difference_a_b"] = time_delta - data["chargable_time"]
#--------------------------------------------------------------------------------------------------------------------------------------	



#--------------------------------------------------------------------------------------------------------------------------------------
        # ----- HOLD Hour ------
        holdchargable = db.query(models.HOLD).join(
            models.TL, models.HOLD.Service_ID == models.TL.Service_ID
        ).filter(
            models.HOLD.Service_ID == row.Service_ID,
            models.HOLD.hold_time_start >= picked_date,
            models.HOLD.hold_time_end <= to_date,
            models.TL.type_of_activity == 'Non-Charchable'
        ).all()

        holdchargable_hour_diff = timedelta(hours=0)

        for row2 in holdchargable:
            if row2.hold_time_end and row2.hold_time_start    and (datetime.strptime(row2.hold_time_end, date_time_formate_string).date()==datetime.strptime(row2.hold_time_start  , date_time_formate_string).date()):
                date_time11 = datetime.strptime(row2.hold_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.hold_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                holdchargable_hour_diff += time_diff
            # else :
            #     if not(row.work_status == "Completed" or row.work_status == "in_progress"):
            #         time1 =  datetime.now() - datetime.strptime(row2.hold_time_start, date_time_formate_string)
                   
            #         holdchargable_hour_diff += time1

        
        
        # ----- Meeting Hour ------
        Meetingchargable = db.query(models.MEETING).join(
            models.TL, models.MEETING.Service_ID == models.TL.Service_ID
        ).filter(
            models.MEETING.Service_ID == row.Service_ID,
            models.MEETING.meeting_time_start >= picked_date,
            models.MEETING.meeting_time_end <= to_date,
            models.TL.type_of_activity == 'Non-Charchable'
        ).all()

        meetch_hour_diff = timedelta(hours=0)

        for row2 in Meetingchargable:
            if row2.meeting_time_end and row2.meeting_time_start    and (datetime.strptime(row2.meeting_time_end, date_time_formate_string).date()==datetime.strptime(row2.meeting_time_start  , date_time_formate_string).date()):
                date_time11 = datetime.strptime(row2.meeting_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                meetch_hour_diff += time_diff
            # else :
            #     if not(row.work_status == "Completed" or row.work_status == "in_progress"):
            #         time1 =  datetime.now() - datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                   
            #         meetch_hour_diff += time1

        
        
        # ----- Break Hour ------
        Breakchargable = db.query(models.BREAK).join(
            models.TL, models.BREAK.Service_ID == models.TL.Service_ID
        ).filter(
            models.BREAK.Service_ID == row.Service_ID,
            models.BREAK.break_time_start >= picked_date,
            models.BREAK.break_time_end <= to_date,
            models.TL.type_of_activity == 'Non-Charchable'
        ).all()

        breakch_hour_diff = timedelta(hours=0)

        for row2 in Breakchargable:
            if row2.break_time_end and row2.break_time_start    and (datetime.strptime(row2.break_time_end, date_time_formate_string).date()==datetime.strptime(row2.break_time_start , date_time_formate_string).date()):
                date_time11 = datetime.strptime(row2.break_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.break_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                breakch_hour_diff += time_diff
            # else :
            #     if not(row.work_status == "Completed" or row.work_status == "in_progress"):
            #         time1 =  datetime.now() - datetime.strptime(row2.break_time_start, date_time_formate_string)
                    
            #         breakch_hour_diff += time1


        
        
        # ----- Call Hour ------
        Callchargable = db.query(models.CALL).join(
            models.TL, models.CALL.Service_ID == models.TL.Service_ID
        ).filter(
            models.CALL.Service_ID == row.Service_ID,
            models.CALL.call_time_start >= picked_date,
            models.CALL.call_time_end <= to_date,
            models.TL.type_of_activity == 'Non-Charchable'
        ).all()

        callch_hour_diff = timedelta(hours=0)

        for row2 in Callchargable:
            if row2.call_time_end and row2.call_time_start    and (datetime.strptime( row2.call_time_end, date_time_formate_string).date()==datetime.strptime(row2.call_time_start  , date_time_formate_string).date()):
                date_time11 = datetime.strptime(row2.call_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.call_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                callch_hour_diff += time_diff
            # else :
            #     if not(row.work_status == "Completed" or row.work_status == "in_progress"):
            #         time1 =  datetime.now() - datetime.strptime(row2.call_time_start, date_time_formate_string)
                  
            #         callch_hour_diff += time1

        # -----end of the day
        endch = db.query(models.END_OF_DAY).join(
            models.TL, models.END_OF_DAY.Service_ID == models.TL.Service_ID
        ).filter(
            models.END_OF_DAY.Service_ID == row.Service_ID,
            models.END_OF_DAY.end_time_start >= picked_date,
            models.END_OF_DAY.end_time_end <= to_date,
            models.TL.type_of_activity == 'Non-Charchable'
        ).all()

        endch_hour_diff = timedelta(hours=0)

        for row2 in endch:
            if row2.end_time_end and row2.end_time_start  and (datetime.strptime( row2.end_time_end , date_time_formate_string).date()==datetime.strptime(row2.end_time_start  , date_time_formate_string).date()):
                date_time11 = datetime.strptime(row2.end_time_end, date_time_formate_string)
                date_time22 = datetime.strptime(row2.end_time_start, date_time_formate_string)
                time_diff = date_time11 - date_time22
                endch_hour_diff += time_diff
            # else :
            #     if not(row.work_status == "Completed" or row.work_status == "in_progress"):
            #         time1 =  datetime.now() - datetime.strptime(row2.end_time_start, date_time_formate_string)
            #         endch_hour_diff += time1
	    

        data["endch_hour_diff"] = endch_hour_diff
        if row.type_of_activity == "Non-Charchable":
            data["Non_Charchable_time"] = endch_hour_diff 
        else:
            data["Non_Charchable_time"] = timedelta(hours=0)
        data["chargable_and_non_chargable"] = data["Non_Charchable_time"] + data["chargable_time"]
#--------------------------------------------------------------------------------------------------------------------------------------	



        str_temp = ""
        str_temper = ""

        if row.work_status == "Work in Progress":

            data["third_report_data"] = ""

        elif row.work_status == "Hold":

            db_res3 = db.query(models.HOLD).filter(
                models.HOLD.Service_ID == row.Service_ID,
            ).all()
            for hold_obj in db_res3:
                data["third_report_data"] = hold_obj.remarks
                str_temper = hold_obj.remarks

        elif row.work_status == "Meeting":

            db_res3 = db.query(models.MEETING).filter(
                models.MEETING.Service_ID == row.Service_ID,
            ).all()
            for meet_obj in db_res3:
                data["third_report_data"] = meet_obj.remarks


        elif row.work_status == "Break":
            db_res3 = db.query(models.BREAK).filter(
                models.BREAK.Service_ID == row.Service_ID,
            ).all()
            for break_obj in db_res3:
                
                data["third_report_data"] = break_obj.remarks
                
        elif row.work_status == "Clarification Call":
            db_res3 = db.query(models.CALL).filter(
                models.CALL.Service_ID == row.Service_ID,
            ).all()
            for call_obj in db_res3:
                
                data["third_report_data"] = call_obj.remarks

        elif row.work_status == "Completed":
            data["third_report_data"] = row.remarks

        if row.work_status == "Completed":
            try:
                db_res3 = db.query(models.HOLD).filter(
                    models.HOLD.Service_ID == row.Service_ID,
                ).all()
                for hold_obj in db_res3:
                    str_temp = str_temp + hold_obj.remarks + ","
            except:
                str_temp = ""
            try:
                db_res3 = db.query(models.MEETING).filter(
                    models.MEETING.Service_ID == row.Service_ID,
                ).all()
                for meet_obj in db_res3:

                    str_temp = str_temp + meet_obj.remarks + ","

            except:
                str_temp = ""
            try:
                db_res3 = db.query(models.BREAK).filter(
                    models.BREAK.Service_ID == row.Service_ID,
                ).all()
                for break_obj in db_res3:
                    str_temp = str_temp + break_obj.remarks + ","
            except:
                str_temp = ""
            try:
                db_res3 = db.query(models.CALL).filter(
                    models.CALL.Service_ID == row.Service_ID,
                ).all()
                for call_obj in db_res3:
                    str_temp = str_temp + call_obj.remarks + ","
                str_temp = str_temp + row.remarks + ","
            except:
                str_temp = ""

        data["fourth_report"] = row.no_of_items
        data["fourth_report2"] = str_temp
        data["fifth_report"] = str_temper        
        list_data.append(data)
    def convert_values(d):
        return dict(map(lambda item: (item[0], str(item[1]).split('.')[0] if not isinstance(item[1], (dict, list)) else item[1]), d.items()))

    converted_list_of_dicts = [convert_values(d) for d in list_data]
    return converted_list_of_dicts




def convert_to_duration(value):
        total_seconds = int(value.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_duration = f"{hours}:{minutes}:{seconds}"
        
        return formatted_duration


def totalfivereports(db: Session, picked_date: str, to_date: str, reportoptions: str ):
    print(reportoptions,'klklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklklkl')
    
    # fetch_hold_data(db)
    
    if reportoptions == "userlist":
        

            finalre = {
                'estimated_time_with_add' : pendulum.duration(),
                'date': set(),
                'user': set(),
                'Service_ID': set(),
                'created_at' : set(),
                'Completed_date' : set(),
                'scope': set(),
                'subscopes': set(),
                'entity': set(),
                'status': set(),
                'type_of_activity': set(),
                'Nature_of_Work': set(),
                'gst_tan': set(),
                'estimated_d_o_d': set(),
                'estimated_time': set(),
                'member_name': set(),
                'end_time': pendulum.duration(),
                'hold': pendulum.duration(),
                'break': pendulum.duration(),
                'time_diff_work': pendulum.duration(),
                'call': pendulum.duration(),
                'meeting': pendulum.duration(),
                'in_progress': pendulum.duration(),
                'completed': pendulum.duration(),
                'third_report_data' : set(),
                'fourth_report' :  set(),
                'fourth_report2' : set(),
                'fifth_report' : set(),
                'no_of_items' : set(),
                'chargable' : set(),
                'non-chargable' : set(),
                'total-time' : set(),
                'idealname' : pendulum.duration()
            }

            date_time_formate_string = '%Y-%m-%d %H:%M:%S'
            list_data = []
            result_data = []
            


            d1 = picked_date
            d2 = to_date

            # Convert strings to datetime objects
            start_date = datetime.strptime(d1, '%Y-%m-%d')
            end_date = datetime.strptime(d2, '%Y-%m-%d')

            # Generate all dates in between and store as strings
            dates_list = []
            current_date = start_date

            while current_date <= end_date:
                
                dates_list.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)

        #     # dates_list contains all dates as strings
            # print(dates_list)

            for item in dates_list:
                # print(item)
                list_data.append(totaltime.user_wise_report(db,item,reportoptions))
                
            list_data = [item for item in list_data if item]

            common =  set()

            for report_list in list_data:
                for entry in report_list:
                        my_set = {str(x) for x in entry['user']} 
                        common.add(my_set.pop())
            
            for finalitems in common:
                for report_list in list_data:
                    
                    for entry in report_list:
                        
                        if entry['user']=={finalitems}:
                            # print(entry['Service_ID'],'ggggggggggggggggggggggggggggggggggggggggggggg')

                            
                            for key in finalre.keys():
                                                                             
                                        if key == 'end_time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'estimated_time_with_add':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'hold':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'break':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'time_diff_work':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'call':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'meeting':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'in_progress':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'idealname':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'completed':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'no_of_items':
                                        
                                            try:
                                                
                                                if len(finalre[key]) == 0:
                                                    finalre[key] = [finalre[key].pop()]+int(entry[key].pop())
                                                else:
                                                    finalre[key] = entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'non-chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'total-time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        else:
                                            finalre[key] = entry[key].union(finalre[key])


                result = {
                    'estimated_time_with_add' : set(),
                    'work_started_date' : set(),
                    'work_ended_date' : set(),
                    'number_of_days_taken' : set(),
                    'number_of_days_delayed' : set(),
                    'actual_date_of_delivery' : set(),
                    'estimated_date_of_delivery' : set(),
                    'number_of_entity' : set(),
                    'estimated_time_minus_chargable_time' : set(),
                    'date': set(),
                    'user': set(),
                    'Service_ID': set(),
                    'created_at' : set(),
                    'Completed_date' : set(),
                    'scope': set(),
                    'subscopes': set(),
                    'entity': set(),
                    'status': set(),
                    'type_of_activity': set(),
                    'Nature_of_Work': set(),
                    'gst_tan': set(),
                    'estimated_d_o_d': set(),
                    'estimated_time': set(),
                    'member_name': set(),
                    'end_time': set(),
                    'hold': set(),
                    'break': set(),
                    'time_diff_work': set(),
                    'call': set(),
                    'meeting': set(),
                    'in_progress': set(),
                    'completed': set(),
                    'third_report_data' : set(),
                    'fourth_report' :  set(),
                    'fourth_report2' : set(),
                    'fifth_report' : set(),
                    'no_of_items' : set(),
                    'chargable' : set(),
                    'non-chargable' : set(),
                    'total-time' : set(),
                    'idealname' : set()
                }
                
                for key in finalre:
                    if isinstance(finalre[key], set):

                            cpof = finalre[key]
                            result[key]= cpof
                           
                            finalre[key] = set()

                    else:
                    
                        result[key].add(convert_to_duration(finalre[key]))
                        finalre[key] = pendulum.duration()
                print(result)


#--------------------------- last calculation


                
                print(len(result['date']),'length ......................................................')
                print(len(result['entity']),'length ......................................................')
                # Define the set of date strings
                date_strings = result['date']

                # Convert the date strings to datetime objects
                dateslast = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                # Find the maximum date
                max_date = max(dateslast)

                min_date = min(dateslast)

                print(min_date,'work start date................................................................')
                print(max_date,'date delivery date ....................................................................')


                print(len(result['estimated_d_o_d']),'estimate date length ......................................................')
                # Define the set of date strings
                date_strings_date = result['estimated_d_o_d']

                # Convert the date strings to datetime objects
                dateslast_date = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings_date}

                # Find the maximum date
                max_date_in_dates = max(dateslast_date)

                print(max_date_in_dates,'estimate date ....................................................................')


#--------------------------- last calculation


                dateesti =  max_date_in_dates.strftime("%Y-%m-%d")

                # Define the set of date strings
                date_strings = result['date']

                # Convert dateesti to a datetime object
                dateesti_dt = datetime.strptime(dateesti, "%Y-%m-%d").date()

                # Convert the set of date strings to a set of datetime objects
                dates = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                # Find and count the dates that are greater than dateesti_dt
                greater_dates = {date for date in dates if date > dateesti_dt}
                count_greater_dates = len(greater_dates)

                # Print the count
                print(count_greater_dates,'number of days delayed  -----------------------------------------------')


#-----------------------------getting estimate time
                

                estichar = result['estimated_time_with_add'].pop()
                hourses, minuteses, secondses = map(int, estichar.split(':'))

                # Create a pendulum Duration object
                durationes = pendulum.duration(hours=hourses, minutes=minuteses, seconds=secondses)

#----------------------------------------- chargable time


                nchar = result['chargable'].pop()

                hours, minutes, seconds = map(int, nchar.split(':'))

                # Create a pendulum Duration object
                duration = pendulum.duration(hours=hours, minutes=minutes, seconds=seconds)
                print(durationes-duration,'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
#------------------------ late of date estimated
                result['chargable'] = nchar
                result['estimated_time_with_add'] = estichar
                result['work_started_date'] =  min_date
                result['work_ended_date'] = max_date
                result['number_of_days_taken'] = len(result['date'])
                result['number_of_days_delayed'] = count_greater_dates
                result['actual_date_of_delivery'] = max_date_in_dates 
                result['estimated_date_of_delivery'] = max_date_in_dates
                result['number_of_entity'] = len(result['entity'])
                result['estimated_time_minus_chargable_time'] = convert_to_duration(durationes-duration)

#------------------------------ code end

                result_data.append(result)
                result = {}


            return result_data

        

    elif reportoptions == "entitylist":

            finalre = {
                'estimated_time_with_add' : pendulum.duration(),
                'date': set(),
                'user': set(),
                'Service_ID': set(),
                'created_at' : set(),
                'Completed_date' : set(),
                'scope': set(),
                'subscopes': set(),
                'entity': set(),
                'status': set(),
                'type_of_activity': set(),
                'Nature_of_Work': set(),
                'gst_tan': set(),
                'estimated_d_o_d': set(),
                'estimated_time': set(),
                'member_name': set(),
                'end_time': pendulum.duration(),
                'hold': pendulum.duration(),
                'break': pendulum.duration(),
                'time_diff_work': pendulum.duration(),
                'call': pendulum.duration(),
                'meeting': pendulum.duration(),
                'in_progress': pendulum.duration(),
                'completed': pendulum.duration(),
                'third_report_data' : set(),
                'fourth_report' :  set(),
                'fourth_report2' : set(),
                'fifth_report' : set(),
                'no_of_items' : set(),
                'chargable' : set(),
                'non-chargable' : set(),
                'total-time' : set(),
                'idealname' : pendulum.duration()
            }

            date_time_formate_string = '%Y-%m-%d %H:%M:%S'
            list_data = []
            result_data = []
            


            d1 = picked_date
            d2 = to_date

            # Convert strings to datetime objects
            start_date = datetime.strptime(d1, '%Y-%m-%d')
            end_date = datetime.strptime(d2, '%Y-%m-%d')

            # Generate all dates in between and store as strings
            dates_list = []
            current_date = start_date

            while current_date <= end_date:
                
                dates_list.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)

        #     # dates_list contains all dates as strings
            # print(dates_list)

            for item in dates_list:
                # print(item)
                list_data.append(totaltime.user_wise_report(db,item,reportoptions))
                
            list_data = [item for item in list_data if item]

            common =  set()

            for report_list in list_data:
                for entry in report_list:
                        my_set = {str(x) for x in entry['entity']} 
                        common.add(my_set.pop())
            
            for finalitems in common:
                for report_list in list_data:
                    
                    for entry in report_list:
                        
                        if entry['entity']=={finalitems}:
                            # print(entry['Service_ID'],'ggggggggggggggggggggggggggggggggggggggggggggg')

                            
                            for key in finalre.keys():

                                        if key == 'end_time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'estimated_time_with_add':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'hold':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'break':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'time_diff_work':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'call':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'meeting':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'in_progress':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'completed':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'idealname':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'no_of_items':
                                            try:
                                                
                                                if len(finalre[key]) == 0:
                                                    finalre[key] = [finalre[key].pop()]+int(entry[key].pop())
                                                else:
                                                    finalre[key] = entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'non-chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'total-time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        else:
                                            finalre[key] = entry[key].union(finalre[key])

                result = {
                    'estimated_time_with_add' : set(),
                    'work_started_date' : set(),
                    'work_ended_date' : set(),
                    'number_of_days_taken' : set(),
                    'number_of_days_delayed' : set(),
                    'actual_date_of_delivery' : set(),
                    'estimated_date_of_delivery' : set(),
                    'number_of_entity' : set(),
                    'estimated_time_minus_chargable_time' : set(),
                    'date': set(),
                    'user': set(),
                    'Service_ID': set(),
                    'created_at' : set(),
                    'Completed_date' : set(),
                    'scope': set(),
                    'subscopes': set(),
                    'entity': set(),
                    'status': set(),
                    'type_of_activity': set(),
                    'Nature_of_Work': set(),
                    'gst_tan': set(),
                    'estimated_d_o_d': set(),
                    'estimated_time': set(),
                    'member_name': set(),
                    'end_time': set(),
                    'hold': set(),
                    'break': set(),
                    'time_diff_work': set(),
                    'call': set(),
                    'meeting': set(),
                    'in_progress': set(),
                    'completed': set(),
                    'third_report_data' : set(),
                    'fourth_report' :  set(),
                    'fourth_report2' : set(),
                    'fifth_report' : set(),
                    'no_of_items' : set(),
                    'chargable' : set(),
                    'non-chargable' : set(),
                    'total-time' : set(),
                    'idealname' : set()
                }
                for key in finalre:
                    if isinstance(finalre[key], set):

                            cpof = finalre[key]
                            result[key]= cpof
                           
                            finalre[key] = set()

                    elif isinstance(finalre[key], int):
                          result[key] = finalre[key]
                        #   print(finalre[key],'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
                    else:
                    
                        result[key].add(convert_to_duration(finalre[key]))
                        finalre[key] = pendulum.duration()
                print(result)


#--------------------------- last calculation


                
                print(len(result['date']),'length ......................................................')
                print(len(result['entity']),'length ......................................................')
                # Define the set of date strings
                date_strings = result['date']

                # Convert the date strings to datetime objects
                dateslast = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                # Find the maximum date
                max_date = max(dateslast)

                min_date = min(dateslast)

                print(min_date,'work start date................................................................')
                print(max_date,'date delivery date ....................................................................')


                print(len(result['estimated_d_o_d']),'estimate date length ......................................................')
                # Define the set of date strings
                date_strings_date = result['estimated_d_o_d']

                # Convert the date strings to datetime objects
                dateslast_date = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings_date}

                # Find the maximum date
                max_date_in_dates = max(dateslast_date)

                print(max_date_in_dates,'estimate date ....................................................................')


#--------------------------- last calculation


                dateesti =  max_date_in_dates.strftime("%Y-%m-%d")

                # Define the set of date strings
                date_strings = result['date']

                # Convert dateesti to a datetime object
                dateesti_dt = datetime.strptime(dateesti, "%Y-%m-%d").date()

                # Convert the set of date strings to a set of datetime objects
                dates = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                # Find and count the dates that are greater than dateesti_dt
                greater_dates = {date for date in dates if date > dateesti_dt}
                count_greater_dates = len(greater_dates)

                # Print the count
                print(count_greater_dates,'number of days delayed  -----------------------------------------------')


#-----------------------------getting estimate time
                

                estichar = result['estimated_time_with_add'].pop()
                hourses, minuteses, secondses = map(int, estichar.split(':'))

                # Create a pendulum Duration object
                durationes = pendulum.duration(hours=hourses, minutes=minuteses, seconds=secondses)

#----------------------------------------- chargable time


                nchar = result['chargable'].pop()

                hours, minutes, seconds = map(int, nchar.split(':'))

                # Create a pendulum Duration object
                duration = pendulum.duration(hours=hours, minutes=minutes, seconds=seconds)
                print(durationes-duration,'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
#------------------------ late of date estimated
                result['chargable'] = nchar
                result['estimated_time_with_add'] = estichar
                result['work_started_date'] =  min_date
                result['work_ended_date'] = max_date
                result['number_of_days_taken'] = len(result['date'])
                result['number_of_days_delayed'] = count_greater_dates
                result['actual_date_of_delivery'] = max_date_in_dates 
                result['estimated_date_of_delivery'] = max_date_in_dates
                result['number_of_entity'] = len(result['entity'])
                result['estimated_time_minus_chargable_time'] = convert_to_duration(durationes-duration)

#------------------------------ code end
                result_data.append(result)
                result = {}


            return result_data

    elif reportoptions == "scopelist":
        
        

            finalre = {
                'estimated_time_with_add' : pendulum.duration(),
                'date': set(),
                'user': set(),
                'Service_ID': set(),
                'created_at' : set(),
                'Completed_date' : set(),
                'scope': set(),
                'subscopes': set(),
                'entity': set(),
                'status': set(),
                'type_of_activity': set(),
                'Nature_of_Work': set(),
                'gst_tan': set(),
                'estimated_d_o_d': set(),
                'estimated_time': set(),
                'member_name': set(),
                'end_time': pendulum.duration(),
                'hold': pendulum.duration(),
                'break': pendulum.duration(),
                'time_diff_work': pendulum.duration(),
                'call': pendulum.duration(),
                'meeting': pendulum.duration(),
                'in_progress': pendulum.duration(),
                'completed': pendulum.duration(),
                'third_report_data' : set(),
                'fourth_report' :  set(),
                'fourth_report2' : set(),
                'fifth_report' : set(),
                'no_of_items' : set(),
                'chargable' : set(),
                'non-chargable' : set(),
                'total-time' : set(),
                'idealname' : pendulum.duration()
            }

            date_time_formate_string = '%Y-%m-%d %H:%M:%S'
            list_data = []
            result_data = []
            


            d1 = picked_date
            d2 = to_date

            # Convert strings to datetime objects
            start_date = datetime.strptime(d1, '%Y-%m-%d')
            end_date = datetime.strptime(d2, '%Y-%m-%d')

            # Generate all dates in between and store as strings
            dates_list = []
            current_date = start_date

            while current_date <= end_date:
                
                dates_list.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)

        #     # dates_list contains all dates as strings
            # print(dates_list)

            for item in dates_list:
                # print(item)
                list_data.append(totaltime.user_wise_report(db,item,reportoptions))
                
            list_data = [item for item in list_data if item]

            common =  set()

            for report_list in list_data:
                for entry in report_list:
                        my_set = {str(x) for x in entry['scope']} 
                        common.add(my_set.pop())
            
            
            for finalitems in common:
                for report_list in list_data:
                    
                    for entry in report_list:
                        
                        if entry['scope']=={finalitems}:
                            # print(entry['Service_ID'],'ggggggggggggggggggggggggggggggggggggggggggggg')

                            
                            for key in finalre.keys():

                                        if key == 'end_time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'estimated_time_with_add':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'hold':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'break':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'time_diff_work':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'call':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'meeting':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'in_progress':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'completed':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'idealname':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'no_of_items':
                                        
                                            try:
                                                
                                                if len(finalre[key]) == 0:
                                                    finalre[key] = [finalre[key].pop()]+int(entry[key].pop())
                                                else:
                                                    finalre[key] = entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'non-chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'total-time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        else:
                                            finalre[key] = entry[key].union(finalre[key])

                result = {
                    'estimated_time_with_add' : set(),
                    'date': set(),
                    'user': set(),
                    'Service_ID': set(),
                    'created_at' : set(),
                    'Completed_date' : set(),
                    'scope': set(),
                    'subscopes': set(),
                    'entity': set(),
                    'status': set(),
                    'type_of_activity': set(),
                    'Nature_of_Work': set(),
                    'gst_tan': set(),
                    'estimated_d_o_d': set(),
                    'estimated_time': set(),
                    'member_name': set(),
                    'end_time': set(),
                    'hold': set(),
                    'break': set(),
                    'time_diff_work': set(),
                    'call': set(),
                    'meeting': set(),
                    'in_progress': set(),
                    'completed': set(),
                    'third_report_data' : set(),
                    'fourth_report' :  set(),
                    'fourth_report2' : set(),
                    'fifth_report' : set(),
                    'no_of_items' : set(),
                    'chargable' : set(),
                    'non-chargable' : set(),
                    'total-time' : set(),
                    'idealname' : set()
                }
                for key in finalre:
                    if isinstance(finalre[key], set):

                            cpof = finalre[key]
                            result[key]= cpof
                           
                            finalre[key] = set()

                    else:
                    
                        result[key].add(convert_to_duration(finalre[key]))
                        finalre[key] = pendulum.duration()
                print(result)
                result_data.append(result)
                result = {}


            return result_data

    elif reportoptions == "subscope":
        
            print('hjhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
        

            finalre = {
                'estimated_time_with_add' : pendulum.duration(),
                'date': set(),
                'user': set(),
                'Service_ID': set(),
                'created_at' : set(),
                'Completed_date' : set(),
                'scope': set(),
                'subscopes': set(),
                'entity': set(),
                'status': set(),
                'type_of_activity': set(),
                'Nature_of_Work': set(),
                'gst_tan': set(),
                'estimated_d_o_d': set(),
                'estimated_time': set(),
                'member_name': set(),
                'end_time': pendulum.duration(),
                'hold': pendulum.duration(),
                'break': pendulum.duration(),
                'time_diff_work': pendulum.duration(),
                'call': pendulum.duration(),
                'meeting': pendulum.duration(),
                'in_progress': pendulum.duration(),
                'completed': pendulum.duration(),
                'third_report_data' : set(),
                'fourth_report' :  set(),
                'fourth_report2' : set(),
                'fifth_report' : set(),
                'no_of_items' : set(),
                'chargable' : set(),
                'non-chargable' : set(),
                'total-time' : set(),
                'idealname' : pendulum.duration()
            }

            date_time_formate_string = '%Y-%m-%d %H:%M:%S'
            list_data = []
            result_data = []
            


            d1 = picked_date
            d2 = to_date

            # Convert strings to datetime objects
            start_date = datetime.strptime(d1, '%Y-%m-%d')
            end_date = datetime.strptime(d2, '%Y-%m-%d')

            # Generate all dates in between and store as strings
            dates_list = []
            current_date = start_date

            while current_date <= end_date:
                
                dates_list.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)

        #     # dates_list contains all dates as strings
            # print(dates_list)

            for item in dates_list:
                # print(item)
                list_data.append(totaltime.user_wise_report(db,item,reportoptions))
                
            list_data = [item for item in list_data if item]

            common =  set()

            for report_list in list_data:
                for entry in report_list:
                        my_set = {str(x) for x in entry['subscopes']} 
                        common.add(my_set.pop())
            
            
            for finalitems in common:
                for report_list in list_data:
                    
                    for entry in report_list:
                        
                        if entry['subscopes']=={finalitems}:
                            # print(entry['Service_ID'],'ggggggggggggggggggggggggggggggggggggggggggggg')

                            
                            for key in finalre.keys():

                                        if key == 'end_time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'estimated_time_with_add':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'hold':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'break':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'time_diff_work':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'call':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'meeting':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'in_progress':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'completed':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'no_of_items':
                                        
                                            try:
                                                
                                                if len(finalre[key]) == 0:
                                                    finalre[key] = [finalre[key].pop()]+int(entry[key].pop())
                                                else:
                                                    finalre[key] = entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'idealname':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'non-chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'total-time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        else:
                                            finalre[key] = entry[key].union(finalre[key])

                result = {
                    'estimated_time_with_add' : set(),
                    'date': set(),
                    'user': set(),
                    'Service_ID': set(),
                    'created_at' : set(),
                    'Completed_date' : set(),
                    'scope': set(),
                    'subscopes': set(),
                    'entity': set(),
                    'status': set(),
                    'type_of_activity': set(),
                    'Nature_of_Work': set(),
                    'gst_tan': set(),
                    'estimated_d_o_d': set(),
                    'estimated_time': set(),
                    'member_name': set(),
                    'end_time': set(),
                    'hold': set(),
                    'break': set(),
                    'time_diff_work': set(),
                    'call': set(),
                    'meeting': set(),
                    'in_progress': set(),
                    'completed': set(),
                    'third_report_data' : set(),
                    'fourth_report' :  set(),
                    'fourth_report2' : set(),
                    'fifth_report' : set(),
                    'no_of_items' : set(),
                    'chargable' : set(),
                    'non-chargable' : set(),
                    'total-time' : set(),
                    'idealname' : set()
                }
                for key in finalre:
                    if isinstance(finalre[key], set):

                            cpof = finalre[key]
                            result[key]= cpof
                           
                            finalre[key] = set()

                    else:
                    
                        result[key].add(convert_to_duration(finalre[key]))
                        finalre[key] = pendulum.duration()
                print(result)
                result_data.append(result)
                result = {}


            return result_data
    
    elif reportoptions == "nature":
        

        

            finalre = {
                'estimated_time_with_add' : pendulum.duration(),
                'date': set(),
                'user': set(),
                'Service_ID': set(),
                'created_at' : set(),
                'Completed_date' : set(),
                'scope': set(),
                'subscopes': set(),
                'entity': set(),
                'status': set(),
                'type_of_activity': set(),
                'Nature_of_Work': set(),
                'gst_tan': set(),
                'estimated_d_o_d': set(),
                'estimated_time': set(),
                'member_name': set(),
                'end_time': pendulum.duration(),
                'hold': pendulum.duration(),
                'break': pendulum.duration(),
                'time_diff_work': pendulum.duration(),
                'call': pendulum.duration(),
                'meeting': pendulum.duration(),
                'in_progress': pendulum.duration(),
                'completed': pendulum.duration(),
                'third_report_data' : set(),
                'fourth_report' :  set(),
                'fourth_report2' : set(),
                'fifth_report' : set(),
                'no_of_items' : set(),
                'chargable' : set(),
                'non-chargable' : set(),
                'total-time' : set(),
                'idealname' : pendulum.duration()
            }

            date_time_formate_string = '%Y-%m-%d %H:%M:%S'
            list_data = []
            result_data = []
            


            d1 = picked_date
            d2 = to_date

            # Convert strings to datetime objects
            start_date = datetime.strptime(d1, '%Y-%m-%d')
            end_date = datetime.strptime(d2, '%Y-%m-%d')

            # Generate all dates in between and store as strings
            dates_list = []
            current_date = start_date

            while current_date <= end_date:
                
                dates_list.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)

        #     # dates_list contains all dates as strings
            # print(dates_list)

            for item in dates_list:
                # print(item)
                list_data.append(totaltime.user_wise_report(db,item,reportoptions))
                
            list_data = [item for item in list_data if item]

            common =  set()

            for report_list in list_data:
                for entry in report_list:
                        my_set = {str(x) for x in entry['Nature_of_Work']} 
                        common.add(my_set.pop())
            
            
            for finalitems in common:
                for report_list in list_data:
                    
                    for entry in report_list:
                        print('gggggggsdohfuisdhfuerhvijsdohveruiv dbojhhbvfjvneribv h ')
                        if entry['Nature_of_Work']=={finalitems}:
                            print(entry['Service_ID'],'ggggggggggggggggggggggggggggggggggggggggggggg')

                            
                            for key in finalre.keys():

                                        if key == 'end_time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'estimated_time_with_add':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'hold':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'break':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'time_diff_work':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'call':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'meeting':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'in_progress':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'completed':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'idealname':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'no_of_items':
                                        
                                            try:
                                                
                                                if len(finalre[key]) == 0:
                                                    finalre[key] = [finalre[key].pop()]+int(entry[key].pop())
                                                else:
                                                    finalre[key] = entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'non-chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'total-time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        else:
                                            finalre[key] = entry[key].union(finalre[key])

                result = {
                    'estimated_time_with_add' : set(),
                    'date': set(),
                    'user': set(),
                    'Service_ID': set(),
                    'created_at' : set(),
                    'Completed_date' : set(),
                    'scope': set(),
                    'subscopes': set(),
                    'entity': set(),
                    'status': set(),
                    'type_of_activity': set(),
                    'Nature_of_Work': set(),
                    'gst_tan': set(),
                    'estimated_d_o_d': set(),
                    'estimated_time': set(),
                    'member_name': set(),
                    'end_time': set(),
                    'hold': set(),
                    'break': set(),
                    'time_diff_work': set(),
                    'call': set(),
                    'meeting': set(),
                    'in_progress': set(),
                    'completed': set(),
                    'third_report_data' : set(),
                    'fourth_report' :  set(),
                    'fourth_report2' : set(),
                    'fifth_report' : set(),
                    'no_of_items' : set(),
                    'chargable' : set(),
                    'non-chargable' : set(),
                    'total-time' : set(),
                    'idealname' : set()
                }
                for key in finalre:
                    if isinstance(finalre[key], set):

                            cpof = finalre[key]
                            result[key]= cpof
                           
                            finalre[key] = set()

                    else:
                    
                        result[key].add(convert_to_duration(finalre[key]))
                        finalre[key] = pendulum.duration()
                print(result)
                result_data.append(result)
                result = {}


            return result_data


    elif reportoptions == "twenty":

            finalre = {
                'estimated_time_with_add' : pendulum.duration(),
                'date': set(),
                'user': set(),
                'Service_ID': set(),
                'scope': set(),
                'created_at' : set(),
                'Completed_date' : set(),
                'subscopes': set(),
                'entity': set(),
                'status': set(),
                'type_of_activity': set(),
                'Nature_of_Work': set(),
                'gst_tan': set(),
                'estimated_d_o_d': set(),
                'estimated_time': set(),
                'member_name': set(),
                'end_time': pendulum.duration(),
                'hold': pendulum.duration(),
                'break': pendulum.duration(),
                'time_diff_work': pendulum.duration(),
                'call': pendulum.duration(),
                'meeting': pendulum.duration(),
                'in_progress': pendulum.duration(),
                'completed': pendulum.duration(),
                'third_report_data' : set(),
                'fourth_report' :  set(),
                'fourth_report2' : set(),
                'fifth_report' : set(),
                'no_of_items' : set(),
                'chargable' : set(),
                'non-chargable' : set(),
                'total-time' : set(),
                'idealname' : pendulum.duration()
            }

            date_time_formate_string = '%Y-%m-%d %H:%M:%S'
            list_data = []
            result_data = []
            


            d1 = picked_date
            d2 = to_date

            # Convert strings to datetime objects
            start_date = datetime.strptime(d1, '%Y-%m-%d')
            end_date = datetime.strptime(d2, '%Y-%m-%d')

            # Generate all dates in between and store as strings
            dates_list = []
            current_date = start_date

            while current_date <= end_date:
                
                dates_list.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)

        #     # dates_list contains all dates as strings
            # print(dates_list)

            for item in dates_list:
                # print(item)
                list_data.append(totaltime.user_wise_report(db,item,reportoptions))
                
            list_data = [item for item in list_data if item]

            common =  set()

            for report_list in list_data:
                for entry in report_list:
                        my_set = {str(x) for x in entry['Service_ID']} 
                        
                        common.add(my_set.pop())

            
            
            for finalitems in common:
                for report_list in list_data:
                    
                    for entry in report_list:

                        if int(finalitems) in entry['Service_ID']:
                            
                            
                            for key in finalre.keys():

                                        if key == 'end_time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'estimated_time_with_add':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'hold':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'break':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'time_diff_work':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'call':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'meeting':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'in_progress':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'completed':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'idealname':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'no_of_items':
                                            
                                            try:
                                                
                                                if len(finalre[key]) == 0:
                                                    finalre[key] = [finalre[key].pop()]+int(entry[key].pop())
                                                else:
                                                    finalre[key] = entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'non-chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'total-time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        else:
                                            finalre[key] = entry[key].union(finalre[key])

                result = {
                    'estimated_time_with_add' : set(),
                    'work_started_date' : set(),
                    'work_ended_date' : set(),
                    'number_of_days_taken' : set(),
                    'number_of_days_delayed' : set(),
                    'actual_date_of_delivery' : set(),
                    'estimated_date_of_delivery' : set(),
                    'number_of_entity' : set(),
                    'estimated_time_minus_chargable_time' : set(),
                    'date': set(),
                    'user': set(),
                    'Service_ID': set(),
                    'created_at' : set(),
                    'Completed_date' : set(),
                    'scope': set(),
                    'subscopes': set(),
                    'entity': set(),
                    'status': set(),
                    'type_of_activity': set(),
                    'Nature_of_Work': set(),
                    'gst_tan': set(),
                    'estimated_d_o_d': set(),
                    'estimated_time': set(),
                    'member_name': set(),
                    'end_time': set(),
                    'hold': set(),
                    'break': set(),
                    'time_diff_work': set(),
                    'call': set(),
                    'meeting': set(),
                    'in_progress': set(),
                    'completed': set(),
                    'third_report_data' : set(),
                    'fourth_report' :  set(),
                    'fourth_report2' : set(),
                    'fifth_report' : set(),
                    'no_of_items' : set(),
                    'chargable' : set(),
                    'non-chargable' : set(),
                    'total-time' : set(),
                    'idealname' : set()
                }
                for key in finalre:
                    if isinstance(finalre[key], set):

                            cpof = finalre[key]
                            result[key]= cpof
                           
                            finalre[key] = set()

                    elif isinstance(finalre[key], int):
                          result[key] = finalre[key]
                        #   print(finalre[key],'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
                    else:
                    
                        result[key].add(convert_to_duration(finalre[key]))
                        finalre[key] = pendulum.duration()
                


#--------------------------- last calculation


                

                # Define the set of date strings
                date_strings = result['date']
               
                # Convert the date strings to datetime objects
                dateslast = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                # Find the maximum date
                max_date = max(dateslast)

                min_date = min(dateslast)




                # Define the set of date strings
                date_strings_date = result['estimated_d_o_d']

                # Convert the date strings to datetime objects
                dateslast_date = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings_date}

                # Find the maximum date
                max_date_in_dates = max(dateslast_date)

                


#--------------------------- last calculation


                dateesti =  max_date_in_dates.strftime("%Y-%m-%d")

                # Define the set of date strings
                date_strings = result['date']

                # Convert dateesti to a datetime object
                dateesti_dt = datetime.strptime(dateesti, "%Y-%m-%d").date()

                # Convert the set of date strings to a set of datetime objects
                dates = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                # Find and count the dates that are greater than dateesti_dt
                greater_dates = {date for date in dates if date > dateesti_dt}
                count_greater_dates = len(greater_dates)

               

#-----------------------------getting estimate time
                

                estichar = result['estimated_time_with_add'].pop()
                hourses, minuteses, secondses = map(int, estichar.split(':'))

                # Create a pendulum Duration object
                durationes = pendulum.duration(hours=hourses, minutes=minuteses, seconds=secondses)

#----------------------------------------- chargable time


                nchar = result['chargable'].pop()

                hours, minutes, seconds = map(int, nchar.split(':'))

                # Create a pendulum Duration object
                duration = pendulum.duration(hours=hours, minutes=minutes, seconds=seconds)
                # print(durationes-duration,'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
#------------------------ late of date estimated
                result['chargable'] = nchar
                result['estimated_time_with_add'] = estichar
                result['work_started_date'] =  min_date
                result['work_ended_date'] = max_date
                result['number_of_days_taken'] = len(result['date'])
                result['number_of_days_delayed'] = count_greater_dates
                result['actual_date_of_delivery'] = max_date_in_dates 
                result['estimated_date_of_delivery'] = max_date_in_dates
                result['number_of_entity'] = len(result['entity'])
                result['estimated_time_minus_chargable_time'] = convert_to_duration(durationes-duration)

#------------------------------ code end
                result_data.append(result)
                result = {}


            return result_data
    

#------------------------------------------------------------------------------------ Pasupathi



    elif reportoptions == "scope_subscope_natureofwork":

                    finalre = {
                        'estimated_time_with_add' : pendulum.duration(),
                        'date': set(),
                        'user': set(),
                        'Service_ID': set(),
                        'scope': set(),
                        'created_at' : set(),
                        'Completed_date' : set(),
                        'subscopes': set(),
                        'entity': set(),
                        # 'no_of_entity' : set(),
                        'status': set(),
                        'type_of_activity': set(),
                        'Nature_of_Work': set(),
                        'gst_tan': set(),
                        'estimated_d_o_d': set(),
                        'estimated_time': set(),
                        'member_name': set(),
                        'end_time': pendulum.duration(),
                        'hold': pendulum.duration(),
                        'break': pendulum.duration(),
                        'time_diff_work': pendulum.duration(),
                        'call': pendulum.duration(),
                        'meeting': pendulum.duration(),
                        'in_progress': pendulum.duration(),
                        'completed': pendulum.duration(),
                        'third_report_data' : set(),
                        'fourth_report' :  set(),
                        'fourth_report2' : set(),
                        'fifth_report' : set(),
                        'no_of_items' : set(),
                        'chargable' : set(),
                        'non-chargable' : set(),
                        'total-time' : set(),
                        'idealname' : pendulum.duration()
                    }

                    date_time_formate_string = '%Y-%m-%d %H:%M:%S'
                    list_data = []
                    result_data = []
                    


                    d1 = picked_date
                    d2 = to_date

                    # Convert strings to datetime objects
                    start_date = datetime.strptime(d1, '%Y-%m-%d')
                    end_date = datetime.strptime(d2, '%Y-%m-%d')

                    # Generate all dates in between and store as strings
                    dates_list = []
                    current_date = start_date

                    while current_date <= end_date:
                        
                        dates_list.append(current_date.strftime('%Y-%m-%d'))
                        current_date += timedelta(days=1)
                        

                #     # dates_list contains all dates as strings
                    # print(dates_list)
                    for item in dates_list:
                        # print(item)
                        print('db')
                        print(db)
                        print('item')
                        print(item)
                        print('reportoptions')
                        print(reportoptions)
                        reportoptions="twenty"
                        list_data.append(totaltime.user_wise_report(db,item,reportoptions))

                                    
                    list_data = [item for item in list_data if item]

                    common =  set()
                    print("list_data")
                    print(list_data)  
                    for report_list in list_data:
                        for entry in report_list:
                                my_set = {str(x) for x in entry['Service_ID']} 
                                
                                common.add(my_set.pop())

                                
                    for finalitems in common:
                        for report_list in list_data:
                            for entry in report_list:
                                if int(finalitems) in entry['Service_ID']:
                                    for key in finalre.keys():
                                                if key == 'end_time':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'estimated_time_with_add':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'hold':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'break':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'time_diff_work':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'call':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'meeting':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'in_progress':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'completed':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'idealname':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'no_of_items':
                                                    try:
                                                        
                                                    
                                                        finalre[key] = [finalre[key].pop()]+int(entry[key].pop())
                                                        
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'chargable':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'non-chargable':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'total-time':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                else:
                                                    finalre[key] = entry[key].union(finalre[key])

                        result = {
                            'estimated_time_with_add' : set(),
                            'work_started_date' : set(),
                            'work_ended_date' : set(),
                            'number_of_days_taken' : set(),
                            'number_of_days_delayed' : set(),
                            'actual_date_of_delivery' : set(),
                            'estimated_date_of_delivery' : set(),
                            'number_of_entity' : set(),
                            'estimated_time_minus_chargable_time' : set(),
                            'date': set(),
                            'user': set(),
                            'Service_ID': set(),
                            'created_at' : set(),
                            'Completed_date' : set(),
                            'scope': set(),
                            'subscopes': set(),
                            'entity': set(),
                            # 'no_of_entity' : set(),
                            'status': set(),
                            'type_of_activity': set(),
                            'Nature_of_Work': set(),
                            'gst_tan': set(),
                            'estimated_d_o_d': set(),
                            'estimated_time': set(),
                            'member_name': set(),
                            'end_time': set(),
                            'hold': set(),
                            'break': set(),
                            'time_diff_work': set(),
                            'call': set(),
                            'meeting': set(),
                            'in_progress': set(),
                            'completed': set(),
                            'third_report_data' : set(),
                            'fourth_report' :  set(),
                            'fourth_report2' : set(),
                            'fifth_report' : set(),
                            'no_of_items' : set(),
                            'chargable' : set(),
                            'non-chargable' : set(),
                            'total-time' : set(),
                            'idealname' : set()
                        }
                        for key in finalre:
                            if isinstance(finalre[key], set):

                                    cpof = finalre[key]
                                    result[key]= cpof
                                
                                    finalre[key] = set()

                            elif isinstance(finalre[key], int):
                                result[key] = finalre[key]
                                #   print(finalre[key],'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
                            else:
                            
                                result[key].add(convert_to_duration(finalre[key]))
                                finalre[key] = pendulum.duration()
                        


        #--------------------------- last calculation


                        

                        # Define the set of date strings
                        date_strings = result['date']
                    
                        # Convert the date strings to datetime objects
                        dateslast = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                        # Find the maximum date
                        max_date = max(dateslast)

                        min_date = min(dateslast)




                        # Define the set of date strings
                        date_strings_date = result['estimated_d_o_d']

                        # Convert the date strings to datetime objects
                        dateslast_date = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings_date}

                        # Find the maximum date
                        max_date_in_dates = max(dateslast_date)

                        


        #--------------------------- last calculation


                        dateesti =  max_date_in_dates.strftime("%Y-%m-%d")

                        # Define the set of date strings
                        date_strings = result['date']

                        # Convert dateesti to a datetime object
                        dateesti_dt = datetime.strptime(dateesti, "%Y-%m-%d").date()

                        # Convert the set of date strings to a set of datetime objects
                        dates = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                        # Find and count the dates that are greater than dateesti_dt
                        greater_dates = {date for date in dates if date > dateesti_dt}
                        count_greater_dates = len(greater_dates)

                    

        #-----------------------------getting estimate time
                        

                        estichar = result['estimated_time_with_add'].pop()
                        hourses, minuteses, secondses = map(int, estichar.split(':'))

                        # Create a pendulum Duration object
                        durationes = pendulum.duration(hours=hourses, minutes=minuteses, seconds=secondses)

        #----------------------------------------- chargable time


                        nchar = result['chargable'].pop()

                        hours, minutes, seconds = map(int, nchar.split(':'))

                        # Create a pendulum Duration object
                        duration = pendulum.duration(hours=hours, minutes=minutes, seconds=seconds)
                        # print(durationes-duration,'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
        #------------------------ late of date estimated
                        result['chargable'] = nchar
                        result['estimated_time_with_add'] = estichar
                        result['work_started_date'] =  min_date
                        result['work_ended_date'] = max_date
                        result['number_of_days_taken'] = len(result['date'])
                        result['number_of_days_delayed'] = count_greater_dates
                        result['actual_date_of_delivery'] = max_date_in_dates 
                        result['estimated_date_of_delivery'] = max_date_in_dates
                        result['number_of_entity'] = len(result['entity'])
                        result['estimated_time_minus_chargable_time'] = convert_to_duration(durationes-duration)

        #------------------------------ code end
                        result_data.append(result)
                        result = {}
                        # print("result starts here =>")
                        # print(result_data)
                        # print("result end here =>")
                    # CODE FOR COMBINING TOTAL-TIME STARTS HERE
                    newObj1 = {}

                    # print("hai")
                    # print(result_data)
                    
                    for item in result_data: 
                        #print(item)    

                        # print("single item starts ")    

                        # print(item)

                        # print("single item ends ")    
                        tempGroup = ''
                        
                        for scope in item['scope']:
                            tempGroup+=scope

                        for subscopes in item['subscopes']:
                            tempGroup+=subscopes

                        for Nature_of_Work in item['Nature_of_Work']:
                            tempGroup+=Nature_of_Work

                        key_to_check = tempGroup

                        if key_to_check in newObj1:
                            if isinstance(item['user'], set):   
                                newObj1[tempGroup]['user'].update(item['user'])  # Update with a set of users
                            else:
                                newObj1[tempGroup]['user'].add(item['user'])  # Add a single user

                            oldETWA = newObj1[tempGroup]['estimated_time_with_add']
                            currentETWA = item['estimated_time_with_add']

                            oldendtime = newObj1[tempGroup]['end_time']
                            currentendtime = item['end_time']

                            oldhold = newObj1[tempGroup]['hold']
                            currenthold = item['hold']

                            oldbreak = newObj1[tempGroup]['break']
                            currentbreak = item['break']

                            oldTDW = newObj1[tempGroup]['time_diff_work']
                            currentTDW = item['time_diff_work']

                            oldcall = newObj1[tempGroup]['call']
                            currentcall = item['call']

                            oldmeeting = newObj1[tempGroup]['meeting']
                            currentmeeting = item['meeting']

                            oldInProgress = newObj1[tempGroup]['in_progress']
                            currentInProgress = item['in_progress']

                            oldcompleted = newObj1[tempGroup]['completed']
                            currentcompleted = item['completed']

                            oldTime = newObj1[tempGroup]['total-time']
                            curentTime = item['total-time']
        #--------------------------------------------------------------------------------------
        #--------------------------Total-estimated_time_with_add-------------------------------
                            ETWAToAdd = {
                                'oldETWA': oldETWA,
                                'currentETWA' : currentETWA
                            }
                            print(oldETWA)
                            print(currentETWA)

                            total_ETWA = timedelta()

                            for times in ETWAToAdd:
                                time_value = ETWAToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_ETWA += time_str_to_timedelta(time_value)

                            total_ETWA_str1 = str(total_ETWA)

                            newObj1[tempGroup]['estimated_time_with_add'] = total_ETWA_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-end_time---------------------------------------------------
                            endtimeToAdd = {
                                'oldendtime': oldendtime,
                                'currentendtime' : currentendtime
                            }

                            print(oldendtime)
                            print(currentendtime)

                            total_endtime = timedelta()

                            for times in endtimeToAdd:
                                time_value = endtimeToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_endtime += time_str_to_timedelta(time_value)

                            total_endtime_str1 = str(total_endtime)

                            newObj1[tempGroup]['end_time'] = total_endtime_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-hold---------------------------------------------------
                            holdToAdd = {
                                'oldhold': oldhold,
                                'currenthold' : currenthold
                            }

                            print(oldhold)
                            print(currenthold)

                            total_hold = timedelta()

                            for times in holdToAdd:
                                time_value = holdToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_hold += time_str_to_timedelta(time_value)

                            total_hold_str1 = str(total_hold)

                            newObj1[tempGroup]['hold'] = total_hold_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-break------------------------------------------------------

                            breakToAdd = {
                                'oldbreak': oldbreak,
                                
                                'currentbreak' : currentbreak
                            }

                            print(oldbreak)
                            print(currentbreak)

                            total_break = timedelta()

                            for times in breakToAdd:
                                time_value = breakToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_break += time_str_to_timedelta(time_value)

                            total_break_str1 = str(total_break)

                            newObj1[tempGroup]['break'] = total_break_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-time_diff_work------------------------------------------------------

                            TDWToAdd = {
                                'oldTDW': oldTDW,
                                'currentTDW' : currentTDW
                            }

                            print(oldTDW)
                            print(currentTDW)

                            total_TDW = timedelta()

                            for times in TDWToAdd:
                                time_value = TDWToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_TDW += time_str_to_timedelta(time_value)

                            total_TDW_str1 = str(total_TDW)

                            newObj1[tempGroup]['time_diff_work'] = total_TDW_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-call------------------------------------------------------

                            callToAdd = {
                                'oldcall': oldcall,
                                'currentcall' : currentcall
                            }

                            print(oldcall)
                            print(currentcall)

                            total_call = timedelta()

                            for times in callToAdd:
                                time_value = callToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_call += time_str_to_timedelta(time_value)

                            total_call_str1 = str(total_call)

                            newObj1[tempGroup]['call'] = total_call_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-meeting------------------------------------------------------
                            meetingToAdd = {
                                'oldmeeting': oldmeeting,
                                'currentmeeting' : currentmeeting
                            }

                            print(oldmeeting)
                            print(currentmeeting)

                            total_meeting = timedelta()

                            for times in meetingToAdd:
                                time_value = meetingToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_meeting += time_str_to_timedelta(time_value)

                            total_meeting_str1 = str(total_meeting)

                            newObj1[tempGroup]['meeting'] =  total_meeting_str1
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-in_progress------------------------------------------------------

                            Inprogresstoadd = {
                                'oldInProgress': oldInProgress,
                                'currentInProgress' : currentInProgress
                            }

                            print(oldInProgress)
                            print(currentInProgress)

                            total_Inprogresstime = timedelta()

                            for times in Inprogresstoadd:
                                time_value = Inprogresstoadd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_Inprogresstime += time_str_to_timedelta(time_value)

                            total_time_str1 = str(total_Inprogresstime)

                            newObj1[tempGroup]['in_progress'] = total_time_str1 
                            #---------------------------------------------------------------------------------------
                            #-------------------------Total-completed------------------------------------------------------
                            completedToAdd = {
                                'oldcompleted': oldcompleted,
                                'currentcompleted' : currentcompleted

                            }

                            print(oldcompleted)
                            print(currentcompleted)

                            total_completed = timedelta()

                            for times in completedToAdd:
                                time_value = completedToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time1 in time_value:
                                        time_value = ""
                                        time_value += time1
                                else:
                                    time_values = time_value
                                
                                total_completed += time_str_to_timedelta(time_value)

                            total_completed_str1 = str(total_completed)

                            newObj1[tempGroup]['estimated_time_with_add'] = total_completed_str1 
                            #---------------------------------------------------------------------------------------
                            #-------------------------Total-total_time------------------------------------------------------

                            timesToAdd = {
                                'oldTime': oldTime,
                                'curentTime': curentTime
                            }
                            print(oldTime)
                            print(curentTime)
                            # Initialize a timedelta object to store the total time
                            total_time = timedelta()

                            # Iterate through the keys to add the time
                            for times in timesToAdd:                        
                                #time_value = next(iter(timesToAdd[times]))  # Extract the single item from the set                        
                                time_value = timesToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_values += time
                                else:
                                    time_values = time_value
                                
                                total_time += time_str_to_timedelta(time_values)

                            # Convert total_time back to a string in HH:MM:SS format
                            total_time_str = str(total_time)  

                            # newObj[tempGroup] = item     #-----(THIS LINE UPDATE THE RECENT RECORD TO THE RESPONSE)

                            newObj1[tempGroup]['total-time'] = total_time_str                    
                        else:
                            if not isinstance(item['user'], set):
                                    item['user'] = {item['user']}  # Convert the user to a set
                                    newObj1[tempGroup] = item  
                            newObj1[tempGroup] = item               
                        
                    combinedArr = []

                    for key, value in newObj1.items():
                        combinedArr.append(value)

                    result_data = combinedArr
                    # CODE FOR COMBINING TOTAL-TIME ENDS HERE
                    print("newObj1")
                    print(newObj1)

                    print("result data => sdfdfdfdfdfdfdfdfdf ")
                    print(result_data)


                    return result_data
        
    elif reportoptions == "scope_subscope":

                    finalre = {
                        'estimated_time_with_add' : pendulum.duration(),
                        'date': set(),
                        'user': set(),
                        'Service_ID': set(),
                        'scope': set(),
                        'created_at' : set(),
                        'Completed_date' : set(),
                        'subscopes': set(),
                        'entity': set(),
                        # 'no_of_entity' : set(),
                        'status': set(),
                        'type_of_activity': set(),
                        'Nature_of_Work': set(),
                        'gst_tan': set(),
                        'estimated_d_o_d': set(),
                        'estimated_time': set(),
                        'member_name': set(),
                        'end_time': pendulum.duration(),
                        'hold': pendulum.duration(),
                        'break': pendulum.duration(),
                        'time_diff_work': pendulum.duration(),
                        'call': pendulum.duration(),
                        'meeting': pendulum.duration(),
                        'in_progress': pendulum.duration(),
                        'completed': pendulum.duration(),
                        'third_report_data' : set(),
                        'fourth_report' :  set(),
                        'fourth_report2' : set(),
                        'fifth_report' : set(),
                        'no_of_items' : set(),
                        'chargable' : set(),
                        'non-chargable' : set(),
                        'total-time' : set(),
                        'idealname' : pendulum.duration()
                    }

                    date_time_formate_string = '%Y-%m-%d %H:%M:%S'
                    list_data = []
                    result_data = []
                    


                    d1 = picked_date
                    d2 = to_date

                    # Convert strings to datetime objects
                    start_date = datetime.strptime(d1, '%Y-%m-%d')
                    end_date = datetime.strptime(d2, '%Y-%m-%d')

                    # Generate all dates in between and store as strings
                    dates_list = []
                    current_date = start_date

                    while current_date <= end_date:
                        
                        dates_list.append(current_date.strftime('%Y-%m-%d'))
                        current_date += timedelta(days=1)
                        

                #     # dates_list contains all dates as strings
                    # print(dates_list)
                    for item in dates_list:
                        reportoptions="twenty"
                        list_data.append(totaltime.user_wise_report(db,item,reportoptions))

                        
                    list_data = [item for item in list_data if item]

                    common =  set()
                    # print("list_data")
                    # print(list_data)  
                    for report_list in list_data:
                        for entry in report_list:
                                my_set = {str(x) for x in entry['Service_ID']} 
                                
                                common.add(my_set.pop())

                                
                    for finalitems in common:
                        for report_list in list_data:
                            for entry in report_list:
                                if int(finalitems) in entry['Service_ID']:
                                    for key in finalre.keys():
                                                if key == 'end_time':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'estimated_time_with_add':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'hold':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'break':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'time_diff_work':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'call':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'meeting':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'in_progress':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'completed':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'idealname':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'no_of_items':
                                                    try:
                                                
                                            
                                                        finalre[key] = [finalre[key].pop()]+int(entry[key].pop())
                                                        
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'chargable':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'non-chargable':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'total-time':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                else:
                                                    finalre[key] = entry[key].union(finalre[key])

                        result = {
                            'estimated_time_with_add' : set(),
                            'work_started_date' : set(),
                            'work_ended_date' : set(),
                            'number_of_days_taken' : set(),
                            'number_of_days_delayed' : set(),
                            'actual_date_of_delivery' : set(),
                            'estimated_date_of_delivery' : set(),
                            'number_of_entity' : set(),
                            'estimated_time_minus_chargable_time' : set(),
                            'date': set(),
                            'user': set(),
                            'Service_ID': set(),
                            'created_at' : set(),
                            'Completed_date' : set(),
                            'scope': set(),
                            'subscopes': set(),
                            'entity': set(),
                            # 'no_of_entity' : set(),
                            'status': set(),
                            'type_of_activity': set(),
                            'Nature_of_Work': set(),
                            'gst_tan': set(),
                            'estimated_d_o_d': set(),
                            'estimated_time': set(),
                            'member_name': set(),
                            'end_time': set(),
                            'hold': set(),
                            'break': set(),
                            'time_diff_work': set(),
                            'call': set(),
                            'meeting': set(),
                            'in_progress': set(),
                            'completed': set(),
                            'third_report_data' : set(),
                            'fourth_report' :  set(),
                            'fourth_report2' : set(),
                            'fifth_report' : set(),
                            'no_of_items' : set(),
                            'chargable' : set(),
                            'non-chargable' : set(),
                            'total-time' : set(),
                            'idealname' : set()
                        }
                        for key in finalre:
                            if isinstance(finalre[key], set):

                                    cpof = finalre[key]
                                    result[key]= cpof
                                
                                    finalre[key] = set()

                            elif isinstance(finalre[key], int):
                                result[key] = finalre[key]
                                #   print(finalre[key],'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
                            else:
                            
                                result[key].add(convert_to_duration(finalre[key]))
                                finalre[key] = pendulum.duration()
                        


        #--------------------------- last calculation


                        

                        # Define the set of date strings
                        date_strings = result['date']
                    
                        # Convert the date strings to datetime objects
                        dateslast = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                        # Find the maximum date
                        max_date = max(dateslast)

                        min_date = min(dateslast)




                        # Define the set of date strings
                        date_strings_date = result['estimated_d_o_d']

                        # Convert the date strings to datetime objects
                        dateslast_date = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings_date}

                        # Find the maximum date
                        max_date_in_dates = max(dateslast_date)

                        


        #--------------------------- last calculation


                        dateesti =  max_date_in_dates.strftime("%Y-%m-%d")

                        # Define the set of date strings
                        date_strings = result['date']

                        # Convert dateesti to a datetime object
                        dateesti_dt = datetime.strptime(dateesti, "%Y-%m-%d").date()

                        # Convert the set of date strings to a set of datetime objects
                        dates = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                        # Find and count the dates that are greater than dateesti_dt
                        greater_dates = {date for date in dates if date > dateesti_dt}
                        count_greater_dates = len(greater_dates)

                    

        #-----------------------------getting estimate time
                        

                        estichar = result['estimated_time_with_add'].pop()
                        hourses, minuteses, secondses = map(int, estichar.split(':'))

                        # Create a pendulum Duration object
                        durationes = pendulum.duration(hours=hourses, minutes=minuteses, seconds=secondses)

        #----------------------------------------- chargable time


                        nchar = result['chargable'].pop()

                        hours, minutes, seconds = map(int, nchar.split(':'))

                        # Create a pendulum Duration object
                        duration = pendulum.duration(hours=hours, minutes=minutes, seconds=seconds)
                        # print(durationes-duration,'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
        #------------------------ late of date estimated
                        result['chargable'] = nchar
                        result['estimated_time_with_add'] = estichar
                        result['work_started_date'] =  min_date
                        result['work_ended_date'] = max_date
                        result['number_of_days_taken'] = len(result['date'])
                        result['number_of_days_delayed'] = count_greater_dates
                        result['actual_date_of_delivery'] = max_date_in_dates 
                        result['estimated_date_of_delivery'] = max_date_in_dates
                        result['number_of_entity'] = len(result['entity'])
                        result['estimated_time_minus_chargable_time'] = convert_to_duration(durationes-duration)

        #------------------------------ code end
                        result_data.append(result)
                        result = {}
                        # print("result starts here =>")
                        # print(result_data)
                        # print("result end here =>")
                    # CODE FOR COMBINING TOTAL-TIME STARTS HERE
                    newObj1 = {}
                    
                    for item in result_data: 
                        #print(item)    

                        # print("single item starts ")    

                        # print(item)

                        # print("single item ends ")    
                        tempGroup = ''
                        
                        for scope in item['scope']:
                            tempGroup+=scope

                        for subscopes in item['subscopes']:
                            tempGroup+=subscopes

                        key_to_check = tempGroup

                        if key_to_check in newObj1:
                            if isinstance(item['user'], set):   
                                newObj1[tempGroup]['user'].update(item['user'])  # Update with a set of users
                            else:
                                newObj1[tempGroup]['user'].add(item['user'])  # Add a single user

                            oldETWA = newObj1[tempGroup]['estimated_time_with_add']
                            currentETWA = item['estimated_time_with_add']

                            oldendtime = newObj1[tempGroup]['end_time']
                            currentendtime = item['end_time']

                            oldhold = newObj1[tempGroup]['hold']
                            currenthold = item['hold']

                            oldbreak = newObj1[tempGroup]['break']
                            currentbreak = item['break']

                            oldTDW = newObj1[tempGroup]['time_diff_work']
                            currentTDW = item['time_diff_work']

                            oldcall = newObj1[tempGroup]['call']
                            currentcall = item['call']

                            oldmeeting = newObj1[tempGroup]['meeting']
                            currentmeeting = item['meeting']

                            oldInProgress = newObj1[tempGroup]['in_progress']
                            currentInProgress = item['in_progress']

                            oldcompleted = newObj1[tempGroup]['completed']
                            currentcompleted = item['completed']

                            oldTime = newObj1[tempGroup]['total-time']
                            curentTime = item['total-time']
        #--------------------------------------------------------------------------------------
        #--------------------------Total-estimated_time_with_add-------------------------------
                            ETWAToAdd = {
                                'oldETWA': oldETWA,
                                'currentETWA' : currentETWA
                            }
                            print(oldETWA)
                            print(currentETWA)

                            total_ETWA = timedelta()

                            for times in ETWAToAdd:
                                time_value = ETWAToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_ETWA += time_str_to_timedelta(time_value)

                            total_ETWA_str1 = str(total_ETWA)

                            newObj1[tempGroup]['estimated_time_with_add'] = total_ETWA_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-end_time---------------------------------------------------
                            endtimeToAdd = {
                                'oldendtime': oldendtime,
                                'currentendtime' : currentendtime
                            }

                            print(oldendtime)
                            print(currentendtime)

                            total_endtime = timedelta()

                            for times in endtimeToAdd:
                                time_value = endtimeToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_endtime += time_str_to_timedelta(time_value)

                            total_endtime_str1 = str(total_endtime)

                            newObj1[tempGroup]['end_time'] = total_endtime_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-hold---------------------------------------------------
                            holdToAdd = {
                                'oldhold': oldhold,
                                'currenthold' : currenthold
                            }

                            print(oldhold)
                            print(currenthold)

                            total_hold = timedelta()

                            for times in holdToAdd:
                                time_value = holdToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_hold += time_str_to_timedelta(time_value)

                            total_hold_str1 = str(total_hold)

                            newObj1[tempGroup]['hold'] = total_hold_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-break------------------------------------------------------

                            breakToAdd = {
                                'oldbreak': oldbreak,
                                
                                'currentbreak' : currentbreak
                            }

                            print(oldbreak)
                            print(currentbreak)

                            total_break = timedelta()

                            for times in breakToAdd:
                                time_value = breakToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_break += time_str_to_timedelta(time_value)

                            total_break_str1 = str(total_break)

                            newObj1[tempGroup]['break'] = total_break_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-time_diff_work------------------------------------------------------

                            TDWToAdd = {
                                'oldTDW': oldTDW,
                                'currentTDW' : currentTDW
                            }

                            print(oldTDW)
                            print(currentTDW)

                            total_TDW = timedelta()

                            for times in TDWToAdd:
                                time_value = TDWToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_TDW += time_str_to_timedelta(time_value)

                            total_TDW_str1 = str(total_TDW)

                            newObj1[tempGroup]['time_diff_work'] = total_TDW_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-call------------------------------------------------------

                            callToAdd = {
                                'oldcall': oldcall,
                                'currentcall' : currentcall
                            }

                            print(oldcall)
                            print(currentcall)

                            total_call = timedelta()

                            for times in callToAdd:
                                time_value = callToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_call += time_str_to_timedelta(time_value)

                            total_call_str1 = str(total_call)

                            newObj1[tempGroup]['call'] = total_call_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-meeting------------------------------------------------------
                            meetingToAdd = {
                                'oldmeeting': oldmeeting,
                                'currentmeeting' : currentmeeting
                            }

                            print(oldmeeting)
                            print(currentmeeting)

                            total_meeting = timedelta()

                            for times in meetingToAdd:
                                time_value = meetingToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_meeting += time_str_to_timedelta(time_value)

                            total_meeting_str1 = str(total_meeting)

                            newObj1[tempGroup]['meeting'] =  total_meeting_str1
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-in_progress------------------------------------------------------

                            Inprogresstoadd = {
                                'oldInProgress': oldInProgress,
                                'currentInProgress' : currentInProgress
                            }

                            print(oldInProgress)
                            print(currentInProgress)

                            total_Inprogresstime = timedelta()

                            for times in Inprogresstoadd:
                                time_value = Inprogresstoadd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_Inprogresstime += time_str_to_timedelta(time_value)

                            total_time_str1 = str(total_Inprogresstime)

                            newObj1[tempGroup]['in_progress'] = total_time_str1 
                            #---------------------------------------------------------------------------------------
                            #-------------------------Total-completed------------------------------------------------------
                            completedToAdd = {
                                'oldcompleted': oldcompleted,
                                'currentcompleted' : currentcompleted

                            }

                            print(oldcompleted)
                            print(currentcompleted)

                            total_completed = timedelta()

                            for times in completedToAdd:
                                time_value = completedToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time1 in time_value:
                                        time_value = ""
                                        time_value += time1
                                else:
                                    time_values = time_value
                                
                                total_completed += time_str_to_timedelta(time_value)

                            total_completed_str1 = str(total_completed)

                            newObj1[tempGroup]['estimated_time_with_add'] = total_completed_str1 
                            #---------------------------------------------------------------------------------------
                            #-------------------------Total-total_time------------------------------------------------------

                            timesToAdd = {
                                'oldTime': oldTime,
                                'curentTime': curentTime
                            }
                            print(oldTime)
                            print(curentTime)
                            # Initialize a timedelta object to store the total time
                            total_time = timedelta()

                            # Iterate through the keys to add the time
                            for times in timesToAdd:                        
                                #time_value = next(iter(timesToAdd[times]))  # Extract the single item from the set                        
                                time_value = timesToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_values += time
                                else:
                                    time_values = time_value
                                
                                total_time += time_str_to_timedelta(time_values)

                            # Convert total_time back to a string in HH:MM:SS format
                            total_time_str = str(total_time)  

                            # newObj[tempGroup] = item     #-----(THIS LINE UPDATE THE RECENT RECORD TO THE RESPONSE)

                            newObj1[tempGroup]['total-time'] = total_time_str                    
                        else:
                            if not isinstance(item['user'], set):
                                    item['user'] = {item['user']}  # Convert the user to a set
                                    newObj1[tempGroup] = item  
                            newObj1[tempGroup] = item               
                        
                    combinedArr = []

                    for key, value in newObj1.items():
                        combinedArr.append(value)

                    result_data = combinedArr
                    # CODE FOR COMBINING TOTAL-TIME ENDS HERE

                    print("newObj1")
                    print(newObj1)

                    print("result data => sdfdfdfdfdfdfdfdfdf ")
                    print(result_data)


                    return result_data
        
    elif reportoptions == "natureofwork_membername":

                    finalre = {
                        'estimated_time_with_add' : pendulum.duration(),
                        'date': set(),
                        'user': set(),
                        'Service_ID': set(),
                        'scope': set(),
                        'created_at' : set(),
                        'Completed_date' : set(),
                        'subscopes': set(),
                        'entity': set(),
                        # 'no_of_entity' : set(),
                        'status': set(),
                        'type_of_activity': set(),
                        'Nature_of_Work': set(),
                        'gst_tan': set(),
                        'estimated_d_o_d': set(),
                        'estimated_time': set(),
                        'member_name': set(),
                        'end_time': pendulum.duration(),
                        'hold': pendulum.duration(),
                        'break': pendulum.duration(),
                        'time_diff_work': pendulum.duration(),
                        'call': pendulum.duration(),
                        'meeting': pendulum.duration(),
                        'in_progress': pendulum.duration(),
                        'completed': pendulum.duration(),
                        'third_report_data' : set(),
                        'fourth_report' :  set(),
                        'fourth_report2' : set(),
                        'fifth_report' : set(),
                        'no_of_items' : set(),
                        'chargable' : set(),
                        'non-chargable' : set(),
                        'total-time' : set(),
                        'idealname' : pendulum.duration()
                    }

                    date_time_formate_string = '%Y-%m-%d %H:%M:%S'
                    list_data = []
                    result_data = []
                    


                    d1 = picked_date
                    d2 = to_date

                    # Convert strings to datetime objects
                    start_date = datetime.strptime(d1, '%Y-%m-%d')
                    end_date = datetime.strptime(d2, '%Y-%m-%d')

                    # Generate all dates in between and store as strings
                    dates_list = []
                    current_date = start_date

                    while current_date <= end_date:
                        
                        dates_list.append(current_date.strftime('%Y-%m-%d'))
                        current_date += timedelta(days=1)
                        

                #     # dates_list contains all dates as strings
                    # print(dates_list)
                    for item in dates_list:
                        reportoptions="twenty"
                        list_data.append(totaltime.user_wise_report(db,item,reportoptions))

                        
                    list_data = [item for item in list_data if item]

                    common =  set()
                    # print("list_data")
                    # print(list_data)  
                    for report_list in list_data:
                        for entry in report_list:
                                my_set = {str(x) for x in entry['Service_ID']} 
                                
                                common.add(my_set.pop())

                                
                    for finalitems in common:
                        for report_list in list_data:
                            for entry in report_list:
                                if int(finalitems) in entry['Service_ID']:
                                    for key in finalre.keys():
                                                if key == 'end_time':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'estimated_time_with_add':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'hold':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'break':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'time_diff_work':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'call':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'meeting':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'in_progress':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'completed':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'idealname':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'no_of_items':
                                                
                                                    try:
                                                        
                                                    
                                                        finalre[key] = [finalre[key].pop()]+int(entry[key].pop())
                                                        
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'chargable':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'non-chargable':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                elif key == 'total-time':
                                                    try:

                                                        finalre[key] = finalre[key]+entry[key]
                                                    except:
                                                        finalre[key] = entry[key]
                                                else:
                                                    finalre[key] = entry[key].union(finalre[key])

                        result = {
                            'estimated_time_with_add' : set(),
                            'work_started_date' : set(),
                            'work_ended_date' : set(),
                            'number_of_days_taken' : set(),
                            'number_of_days_delayed' : set(),
                            'actual_date_of_delivery' : set(),
                            'estimated_date_of_delivery' : set(),
                            'number_of_entity' : set(),
                            'estimated_time_minus_chargable_time' : set(),
                            'date': set(),
                            'user': set(),
                            'Service_ID': set(),
                            'created_at' : set(),
                            'Completed_date' : set(),
                            'scope': set(),
                            'subscopes': set(),
                            'entity': set(),
                            # 'no_of_entity' : set(),
                            'status': set(),
                            'type_of_activity': set(),
                            'Nature_of_Work': set(),
                            'gst_tan': set(),
                            'estimated_d_o_d': set(),
                            'estimated_time': set(),
                            'member_name': set(),
                            'end_time': set(),
                            'hold': set(),
                            'break': set(),
                            'time_diff_work': set(),
                            'call': set(),
                            'meeting': set(),
                            'in_progress': set(),
                            'completed': set(),
                            'third_report_data' : set(),
                            'fourth_report' :  set(),
                            'fourth_report2' : set(),
                            'fifth_report' : set(),
                            'no_of_items' : set(),
                            'chargable' : set(),
                            'non-chargable' : set(),
                            'total-time' : set(),
                            'idealname' : set()
                        }
                        for key in finalre:
                            if isinstance(finalre[key], set):

                                    cpof = finalre[key]
                                    result[key]= cpof
                                
                                    finalre[key] = set()

                            elif isinstance(finalre[key], int):
                                result[key] = finalre[key]
                                #   print(finalre[key],'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
                            else:
                            
                                result[key].add(convert_to_duration(finalre[key]))
                                finalre[key] = pendulum.duration()
                        


        #--------------------------- last calculation


                        

                        # Define the set of date strings
                        date_strings = result['date']
                    
                        # Convert the date strings to datetime objects
                        dateslast = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                        # Find the maximum date
                        max_date = max(dateslast)

                        min_date = min(dateslast)




                        # Define the set of date strings
                        date_strings_date = result['estimated_d_o_d']

                        # Convert the date strings to datetime objects
                        dateslast_date = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings_date}

                        # Find the maximum date
                        max_date_in_dates = max(dateslast_date)

                        


        #--------------------------- last calculation


                        dateesti =  max_date_in_dates.strftime("%Y-%m-%d")

                        # Define the set of date strings
                        date_strings = result['date']

                        # Convert dateesti to a datetime object
                        dateesti_dt = datetime.strptime(dateesti, "%Y-%m-%d").date()

                        # Convert the set of date strings to a set of datetime objects
                        dates = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                        # Find and count the dates that are greater than dateesti_dt
                        greater_dates = {date for date in dates if date > dateesti_dt}
                        count_greater_dates = len(greater_dates)

                    

        #-----------------------------getting estimate time
                        

                        estichar = result['estimated_time_with_add'].pop()
                        hourses, minuteses, secondses = map(int, estichar.split(':'))

                        # Create a pendulum Duration object
                        durationes = pendulum.duration(hours=hourses, minutes=minuteses, seconds=secondses)

        #----------------------------------------- chargable time


                        nchar = result['chargable'].pop()

                        hours, minutes, seconds = map(int, nchar.split(':'))

                        # Create a pendulum Duration object
                        duration = pendulum.duration(hours=hours, minutes=minutes, seconds=seconds)
                        # print(durationes-duration,'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
        #------------------------ late of date estimated
                        result['chargable'] = nchar
                        result['estimated_time_with_add'] = estichar
                        result['work_started_date'] =  min_date
                        result['work_ended_date'] = max_date
                        result['number_of_days_taken'] = len(result['date'])
                        result['number_of_days_delayed'] = count_greater_dates
                        result['actual_date_of_delivery'] = max_date_in_dates 
                        result['estimated_date_of_delivery'] = max_date_in_dates
                        result['number_of_entity'] = len(result['entity'])
                        result['estimated_time_minus_chargable_time'] = convert_to_duration(durationes-duration)

        #------------------------------ code end
                        result_data.append(result)
                        result = {}
                        # print("result starts here =>")
                        # print(result_data)
                        # print("result end here =>")
                    # CODE FOR COMBINING TOTAL-TIME STARTS HERE
                    newObj1 = {}
                    
                    for item in result_data: 
                        #print(item)    

                        # print("single item starts ")    

                        # print(item)

                        # print("single item ends ")    
                        tempGroup = ''
                        
                        for Nature_of_Work in item['Nature_of_Work']:
                            tempGroup+=Nature_of_Work

                        for member_name in item['member_name']:
                            tempGroup+=member_name

                        key_to_check = tempGroup

                    
                        if key_to_check in newObj1:
                            if isinstance(item['user'], set):   
                                newObj1[tempGroup]['user'].update(item['user'])  # Update with a set of users
                            else:
                                newObj1[tempGroup]['user'].add(item['user'])  # Add a single user

                            oldETWA = newObj1[tempGroup]['estimated_time_with_add']
                            currentETWA = item['estimated_time_with_add']

                            oldendtime = newObj1[tempGroup]['end_time']
                            currentendtime = item['end_time']

                            oldhold = newObj1[tempGroup]['hold']
                            currenthold = item['hold']

                            oldbreak = newObj1[tempGroup]['break']
                            currentbreak = item['break']

                            oldTDW = newObj1[tempGroup]['time_diff_work']
                            currentTDW = item['time_diff_work']

                            oldcall = newObj1[tempGroup]['call']
                            currentcall = item['call']

                            oldmeeting = newObj1[tempGroup]['meeting']
                            currentmeeting = item['meeting']

                            oldInProgress = newObj1[tempGroup]['in_progress']
                            currentInProgress = item['in_progress']

                            oldcompleted = newObj1[tempGroup]['completed']
                            currentcompleted = item['completed']

                            oldTime = newObj1[tempGroup]['total-time']
                            curentTime = item['total-time']
        #--------------------------------------------------------------------------------------
        #--------------------------Total-estimated_time_with_add-------------------------------
                            ETWAToAdd = {
                                'oldETWA': oldETWA,
                                'currentETWA' : currentETWA
                            }
                            print(oldETWA)
                            print(currentETWA)

                            total_ETWA = timedelta()

                            for times in ETWAToAdd:
                                time_value = ETWAToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_ETWA += time_str_to_timedelta(time_value)

                            total_ETWA_str1 = str(total_ETWA)

                            newObj1[tempGroup]['estimated_time_with_add'] = total_ETWA_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-end_time---------------------------------------------------
                            endtimeToAdd = {
                                'oldendtime': oldendtime,
                                'currentendtime' : currentendtime
                            }

                            print(oldendtime)
                            print(currentendtime)

                            total_endtime = timedelta()

                            for times in endtimeToAdd:
                                time_value = endtimeToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_endtime += time_str_to_timedelta(time_value)

                            total_endtime_str1 = str(total_endtime)

                            newObj1[tempGroup]['end_time'] = total_endtime_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-hold---------------------------------------------------
                            holdToAdd = {
                                'oldhold': oldhold,
                                'currenthold' : currenthold
                            }

                            print(oldhold)
                            print(currenthold)

                            total_hold = timedelta()

                            for times in holdToAdd:
                                time_value = holdToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_hold += time_str_to_timedelta(time_value)

                            total_hold_str1 = str(total_hold)

                            newObj1[tempGroup]['hold'] = total_hold_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-break------------------------------------------------------

                            breakToAdd = {
                                'oldbreak': oldbreak,
                                
                                'currentbreak' : currentbreak
                            }

                            print(oldbreak)
                            print(currentbreak)

                            total_break = timedelta()

                            for times in breakToAdd:
                                time_value = breakToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_break += time_str_to_timedelta(time_value)

                            total_break_str1 = str(total_break)

                            newObj1[tempGroup]['break'] = total_break_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-time_diff_work------------------------------------------------------

                            TDWToAdd = {
                                'oldTDW': oldTDW,
                                'currentTDW' : currentTDW
                            }

                            print(oldTDW)
                            print(currentTDW)

                            total_TDW = timedelta()

                            for times in TDWToAdd:
                                time_value = TDWToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_TDW += time_str_to_timedelta(time_value)

                            total_TDW_str1 = str(total_TDW)

                            newObj1[tempGroup]['time_diff_work'] = total_TDW_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-call------------------------------------------------------

                            callToAdd = {
                                'oldcall': oldcall,
                                'currentcall' : currentcall
                            }

                            print(oldcall)
                            print(currentcall)

                            total_call = timedelta()

                            for times in callToAdd:
                                time_value = callToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_call += time_str_to_timedelta(time_value)

                            total_call_str1 = str(total_call)

                            newObj1[tempGroup]['call'] = total_call_str1 
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-meeting------------------------------------------------------
                            meetingToAdd = {
                                'oldmeeting': oldmeeting,
                                'currentmeeting' : currentmeeting
                            }

                            print(oldmeeting)
                            print(currentmeeting)

                            total_meeting = timedelta()

                            for times in meetingToAdd:
                                time_value = meetingToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_meeting += time_str_to_timedelta(time_value)

                            total_meeting_str1 = str(total_meeting)

                            newObj1[tempGroup]['meeting'] =  total_meeting_str1
                            #------------------------------------------------------------------------------------------
                            #-------------------------Total-in_progress------------------------------------------------------

                            # Inprogresstoadd = {
                            #     'oldInProgress': oldInProgress,
                            #     'currentInProgress' : currentInProgress
                            # }

                            # print(oldInProgress)
                            # print(currentInProgress)

                            # total_Inprogresstime = timedelta()

                            # for times in Inprogresstoadd:
                            #     time_value = Inprogresstoadd[times]
                            #     time_values = ''

                            #     if isinstance(time_value, set):
                            #         for time in time_value:
                            #             time_value = ""
                            #             time_value += time
                            #     else:
                            #         time_values = time_value
                                
                            #     total_Inprogresstime += time_str_to_timedelta(time_value)

                            # total_time_str1 = str(total_Inprogresstime)

                            # newObj1[tempGroup]['in_progress'] = total_time_str1 

                            Inprogresstoadd = {
                                'oldInProgress': oldInProgress,
                                'currentInProgress' : currentInProgress
                            }

                            print(oldInProgress)
                            print(currentInProgress)

                            total_Inprogresstime = timedelta()

                            for times in Inprogresstoadd:
                                time_value = Inprogresstoadd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_value = ""
                                        time_value += time
                                else:
                                    time_values = time_value
                                
                                total_Inprogresstime += time_str_to_timedelta(time_value)

                            total_time_str1 = str(total_Inprogresstime)

                            newObj1[tempGroup]['in_progress'] = total_time_str1 
                            #---------------------------------------------------------------------------------------
                            #-------------------------Total-completed------------------------------------------------------
                            completedToAdd = {
                                'oldcompleted': oldcompleted,
                                'currentcompleted' : currentcompleted

                            }

                            print(oldcompleted)
                            print(currentcompleted)

                            total_completed = timedelta()

                            for times in completedToAdd:
                                time_value = completedToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time1 in time_value:
                                        time_value = ""
                                        time_value += time1
                                else:
                                    time_values = time_value
                                
                                total_completed += time_str_to_timedelta(time_value)

                            total_completed_str1 = str(total_completed)

                            newObj1[tempGroup]['estimated_time_with_add'] = total_completed_str1 
                            #---------------------------------------------------------------------------------------
                            #-------------------------Total-total_time------------------------------------------------------

                            timesToAdd = {
                                'oldTime': oldTime,
                                'curentTime': curentTime
                            }
                            print(oldTime)
                            print(curentTime)
                            # Initialize a timedelta object to store the total time
                            total_time = timedelta()

                            # Iterate through the keys to add the time
                            for times in timesToAdd:                        
                                #time_value = next(iter(timesToAdd[times]))  # Extract the single item from the set                        
                                time_value = timesToAdd[times]
                                time_values = ''

                                if isinstance(time_value, set):
                                    for time in time_value:
                                        time_values += time
                                else:
                                    time_values = time_value
                                
                                total_time += time_str_to_timedelta(time_values)

                            # Convert total_time back to a string in HH:MM:SS format
                            total_time_str = str(total_time)  

                            # newObj[tempGroup] = item     #-----(THIS LINE UPDATE THE RECENT RECORD TO THE RESPONSE)

                            newObj1[tempGroup]['total-time'] = total_time_str                    
                        else:
                            if not isinstance(item['user'], set):
                                    item['user'] = {item['user']}  # Convert the user to a set
                                    newObj1[tempGroup] = item  
                            newObj1[tempGroup] = item               
                        
                    combinedArr = []

                    for key, value in newObj1.items():
                        combinedArr.append(value)

                    result_data = combinedArr
                    # CODE FOR COMBINING TOTAL-TIME ENDS HERE

                    print("newObj1")
                    print(newObj1)

                    print("result data => sdfdfdfdfdfdfdfdfdf ")
                    print(result_data)


                    return result_data


    elif reportoptions == "scope_subscope_natureofwork":

            finalre = {
                'estimated_time_with_add' : pendulum.duration(),
                'date': set(),
                'user': set(),
                'Service_ID': set(),
                'scope': set(),
                'created_at' : set(),
                'Completed_date' : set(),
                'subscopes': set(),
                'entity': set(),
                # 'no_of_entity' : set(),
                'status': set(),
                'type_of_activity': set(),
                'Nature_of_Work': set(),
                'gst_tan': set(),
                'estimated_d_o_d': set(),
                'estimated_time': set(),
                'member_name': set(),
                'end_time': pendulum.duration(),
                'hold': pendulum.duration(),
                'break': pendulum.duration(),
                'time_diff_work': pendulum.duration(),
                'call': pendulum.duration(),
                'meeting': pendulum.duration(),
                'in_progress': pendulum.duration(),
                'completed': pendulum.duration(),
                'third_report_data' : set(),
                'fourth_report' :  set(),
                'fourth_report2' : set(),
                'fifth_report' : set(),
                'no_of_items' : set(),
                'chargable' : set(),
                'non-chargable' : set(),
                'total-time' : set(),
                'idealname' : pendulum.duration()
            }

            date_time_formate_string = '%Y-%m-%d %H:%M:%S'
            list_data = []
            result_data = []
            


            d1 = picked_date
            d2 = to_date

            # Convert strings to datetime objects
            start_date = datetime.strptime(d1, '%Y-%m-%d')
            end_date = datetime.strptime(d2, '%Y-%m-%d')

            # Generate all dates in between and store as strings
            dates_list = []
            current_date = start_date

            while current_date <= end_date:
                
                dates_list.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)
                

            # dates_list contains all dates as strings
            # print(dates_list)
            for item in dates_list:
                # print(item)
                print('db')
                print(db)
                print('item')
                print(item)
                print('reportoptions')
                print(reportoptions)
                reportoptions="twenty"
                list_data.append(totaltime.user_wise_report(db,item,reportoptions))

                            
            list_data = [item for item in list_data if item]

            common =  set()
            print("list_data")
            print(list_data)  
            for report_list in list_data:
                for entry in report_list:
                        my_set = {str(x) for x in entry['Service_ID']} 
                        
                        common.add(my_set.pop())

                                
            for finalitems in common:
                for report_list in list_data:
                    for entry in report_list:
                        if int(finalitems) in entry['Service_ID']:
                            for key in finalre.keys():
                                        if key == 'end_time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'estimated_time_with_add':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'hold':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'break':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'time_diff_work':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'call':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'meeting':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'in_progress':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'completed':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'idealname':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'no_of_items':
                                            try:
                                                
                                                if len(finalre[key]) == 0:
                                                    finalre[key] = [finalre[key].pop()]+int(entry[key].pop())
                                                else:
                                                    finalre[key] = entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'non-chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'total-time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        else:
                                            finalre[key] = entry[key].union(finalre[key])

                result = {
                    'estimated_time_with_add' : set(),
                    'work_started_date' : set(),
                    'work_ended_date' : set(),
                    'number_of_days_taken' : set(),
                    'number_of_days_delayed' : set(),
                    'actual_date_of_delivery' : set(),
                    'estimated_date_of_delivery' : set(),
                    'number_of_entity' : set(),
                    'estimated_time_minus_chargable_time' : set(),
                    'date': set(),
                    'user': set(),
                    'Service_ID': set(),
                    'created_at' : set(),
                    'Completed_date' : set(),
                    'scope': set(),
                    'subscopes': set(),
                    'entity': set(),
                    # 'no_of_entity' : set(),
                    'status': set(),
                    'type_of_activity': set(),
                    'Nature_of_Work': set(),
                    'gst_tan': set(),
                    'estimated_d_o_d': set(),
                    'estimated_time': set(),
                    'member_name': set(),
                    'end_time': set(),
                    'hold': set(),
                    'break': set(),
                    'time_diff_work': set(),
                    'call': set(),
                    'meeting': set(),
                    'in_progress': set(),
                    'completed': set(),
                    'third_report_data' : set(),
                    'fourth_report' :  set(),
                    'fourth_report2' : set(),
                    'fifth_report' : set(),
                    'no_of_items' : set(),
                    'chargable' : set(),
                    'non-chargable' : set(),
                    'total-time' : set(),
                    'idealname' : set()
                }
                for key in finalre:
                    if isinstance(finalre[key], set):

                            cpof = finalre[key]
                            result[key]= cpof
                        
                            finalre[key] = set()

                    elif isinstance(finalre[key], int):
                        result[key] = finalre[key]
                        #   print(finalre[key],'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
                    else:
                    
                        result[key].add(convert_to_duration(finalre[key]))
                        finalre[key] = pendulum.duration()
                


        #--------------------------- last calculation


                        

                # Define the set of date strings
                date_strings = result['date']
            
                # Convert the date strings to datetime objects
                dateslast = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                # Find the maximum date
                max_date = max(dateslast)

                min_date = min(dateslast)




                # Define the set of date strings
                date_strings_date = result['estimated_d_o_d']

                # Convert the date strings to datetime objects
                dateslast_date = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings_date}

                # Find the maximum date
                max_date_in_dates = max(dateslast_date)

                        


        #--------------------------- last calculation


                dateesti =  max_date_in_dates.strftime("%Y-%m-%d")

                # Define the set of date strings
                date_strings = result['date']

                # Convert dateesti to a datetime object
                dateesti_dt = datetime.strptime(dateesti, "%Y-%m-%d").date()

                # Convert the set of date strings to a set of datetime objects
                dates = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                # Find and count the dates that are greater than dateesti_dt
                greater_dates = {date for date in dates if date > dateesti_dt}
                count_greater_dates = len(greater_dates)

                    

        #-----------------------------getting estimate time
                        

                estichar = result['estimated_time_with_add'].pop()
                hourses, minuteses, secondses = map(int, estichar.split(':'))

                # Create a pendulum Duration object
                durationes = pendulum.duration(hours=hourses, minutes=minuteses, seconds=secondses)

        #----------------------------------------- chargable time


                nchar = result['chargable'].pop()

                hours, minutes, seconds = map(int, nchar.split(':'))

                # Create a pendulum Duration object
                duration = pendulum.duration(hours=hours, minutes=minutes, seconds=seconds)
                # print(durationes-duration,'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
#------------------------ late of date estimated
                result['chargable'] = nchar
                result['estimated_time_with_add'] = estichar
                result['work_started_date'] =  min_date
                result['work_ended_date'] = max_date
                result['number_of_days_taken'] = len(result['date'])
                result['number_of_days_delayed'] = count_greater_dates
                result['actual_date_of_delivery'] = max_date_in_dates 
                result['estimated_date_of_delivery'] = max_date_in_dates
                result['number_of_entity'] = len(result['entity'])
                result['estimated_time_minus_chargable_time'] = convert_to_duration(durationes-duration)

        #------------------------------ code end
                result_data.append(result)
                result = {}
                # print("result starts here =>")
                # print(result_data)
                # print("result end here =>")
            # CODE FOR COMBINING TOTAL-TIME STARTS HERE
            newObj1 = {}

            # print("hai")
            # print(result_data)
            
            for item in result_data: 
                #print(item)    

                # print("single item starts ")    

                # print(item)

                # print("single item ends ")    
                tempGroup = ''
                
                for scope in item['scope']:
                    tempGroup+=scope

                for subscopes in item['subscopes']:
                    tempGroup+=subscopes

                for Nature_of_Work in item['Nature_of_Work']:
                    tempGroup+=Nature_of_Work

                key_to_check = tempGroup

                if key_to_check in newObj1:
                    if isinstance(item['user'], set):   
                        newObj1[tempGroup]['user'].update(item['user'])  # Update with a set of users
                    else:
                        newObj1[tempGroup]['user'].add(item['user'])  # Add a single user

                    oldETWA = newObj1[tempGroup]['estimated_time_with_add']
                    currentETWA = item['estimated_time_with_add']

                    oldendtime = newObj1[tempGroup]['end_time']
                    currentendtime = item['end_time']

                    oldhold = newObj1[tempGroup]['hold']
                    currenthold = item['hold']

                    oldbreak = newObj1[tempGroup]['break']
                    currentbreak = item['break']

                    oldTDW = newObj1[tempGroup]['time_diff_work']
                    currentTDW = item['time_diff_work']

                    oldcall = newObj1[tempGroup]['call']
                    currentcall = item['call']

                    oldmeeting = newObj1[tempGroup]['meeting']
                    currentmeeting = item['meeting']

                    oldInProgress = newObj1[tempGroup]['in_progress']
                    currentInProgress = item['in_progress']

                    oldcompleted = newObj1[tempGroup]['completed']
                    currentcompleted = item['completed']

                    oldnoofitems = newObj1[tempGroup]['no_of_items']
                    currentnoofitems = item['no_of_items']

                    oldTime = newObj1[tempGroup]['total-time']
                    curentTime = item['total-time']
                    #--------------------------------------------------------------------------------------
                    #--------------------------Total-estimated_time_with_add-------------------------------
                    ETWAToAdd = {
                        'oldETWA': oldETWA,
                        'currentETWA' : currentETWA
                    }
                    print(oldETWA)
                    print(currentETWA)

                    total_ETWA = timedelta()

                    for times in ETWAToAdd:
                        time_value = ETWAToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)  # Add time to the set

                                # time_value = ""
                                # time_value += time
                        else:
                            time_values = time_value
                        
                    total_ETWA += time_str_to_timedelta(time_values)

                    total_ETWA_str1 = str(total_ETWA)

                    newObj1[tempGroup]['estimated_time_with_add'] = total_ETWA_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-end_time---------------------------------------------------
                    endtimeToAdd = {
                        'oldendtime': oldendtime,
                        'currentendtime' : currentendtime
                    }

                    print(oldendtime)
                    print(currentendtime)

                    total_endtime = timedelta()

                    for times in endtimeToAdd:
                        time_value = endtimeToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)  # Add time to the set

                                # time_value = ""
                                # time_value += time
                        else:
                            time_values = time_value
                        
                    total_endtime += time_str_to_timedelta(time_values)

                    total_endtime_str1 = str(total_endtime)

                    newObj1[tempGroup]['end_time'] = total_endtime_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-hold---------------------------------------------------
                    holdToAdd = {
                        'oldhold': oldhold,
                        'currenthold' : currenthold
                    }

                    print(oldhold)
                    print(currenthold)

                    total_hold = timedelta()

                    for times in holdToAdd:
                        time_value = holdToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)  # Add time to the set

                                # time_value = ""
                                # time_value += time
                        else:
                            time_values = time_value
                        
                    total_hold += time_str_to_timedelta(time_values)

                    total_hold_str1 = str(total_hold)

                    newObj1[tempGroup]['hold'] = total_hold_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-break------------------------------------------------------

                    breakToAdd = {
                        'oldbreak': oldbreak,
                        
                        'currentbreak' : currentbreak
                    }

                    print(oldbreak)
                    print(currentbreak)

                    total_break = timedelta()

                    for times in breakToAdd:
                        time_value = breakToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)  # Add time to the set

                                # time_value = ""
                                # time_value += time
                        else:
                            time_values = time_value
                        
                    total_break += time_str_to_timedelta(time_values)

                    total_break_str1 = str(total_break)

                    newObj1[tempGroup]['break'] = total_break_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-time_diff_work------------------------------------------------------

                    TDWToAdd = {
                        'oldTDW': oldTDW,
                        'currentTDW' : currentTDW
                    }

                    print(oldTDW)
                    print(currentTDW)

                    total_TDW = timedelta()

                    for times in TDWToAdd:
                        time_value = TDWToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)  # Add time to the set

                                # time_value = ""
                                # time_value += time
                        else:
                            time_values = time_value
                        
                    total_TDW += time_str_to_timedelta(time_values)

                    total_TDW_str1 = str(total_TDW)

                    newObj1[tempGroup]['time_diff_work'] = total_TDW_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-call------------------------------------------------------

                    callToAdd = {
                        'oldcall': oldcall,
                        'currentcall' : currentcall
                    }

                    print(oldcall)
                    print(currentcall)

                    total_call = timedelta()

                    for times in callToAdd:
                        time_value = callToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)  # Add time to the set

                                # time_value = ""
                                # time_value += time
                        else:
                            time_values = time_value

                        
                    total_call += time_str_to_timedelta(time_values)

                    total_call_str1 = str(total_call)

                    newObj1[tempGroup]['call'] = total_call_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-meeting------------------------------------------------------
                    meetingToAdd = {
                        'oldmeeting': oldmeeting,
                        'currentmeeting' : currentmeeting
                    }

                    print(oldmeeting)
                    print(currentmeeting)

                    total_meeting = timedelta()

                    for times in meetingToAdd:
                        time_value = meetingToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)  # Add time to the set

                                # time_value = ""
                                # time_value += time
                        else:
                            time_values = time_value
                        
                    total_meeting += time_str_to_timedelta(time_values)

                    total_meeting_str1 = str(total_meeting)

                    newObj1[tempGroup]['meeting'] =  total_meeting_str1
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-in_progress------------------------------------------------------

                    Inprogresstoadd = {
                        'oldInProgress': oldInProgress,
                        'currentInProgress' : currentInProgress
                    }

                    print(oldInProgress)
                    print(currentInProgress)

                    total_Inprogresstime = timedelta()

                    for times in Inprogresstoadd:
                        time_value = Inprogresstoadd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)  # Add time to the set

                                # time_value = ""
                                # time_value += time
                        else:
                            time_values = time_value
                        
                    total_Inprogresstime += time_str_to_timedelta(time_values)

                    total_time_str1 = str(total_Inprogresstime)

                    newObj1[tempGroup]['in_progress'] = total_time_str1 
                    #---------------------------------------------------------------------------------------
                    #-------------------------Total-completed------------------------------------------------------
                    completedToAdd = {
                        'oldcompleted': oldcompleted,
                        'currentcompleted' : currentcompleted

                    }

                    print(oldcompleted)
                    print(currentcompleted)

                    total_completed = timedelta()

                    for times in completedToAdd:
                        time_value = completedToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)  # Add time to the set

                                # time_value = ""
                                # time_value += time1
                        else:
                            time_values = time_value
                        
                    total_completed += time_str_to_timedelta(time_values)

                    total_completed_str1 = str(total_completed)

                    newObj1[tempGroup]['completed'] = total_completed_str1 

                    #------------------------------------------------------------------------------------
                    #-------------------------Total-no_of_items------------------------------------------------------
                    noofitemsdToAdd = {
                        'oldnoofitems': oldnoofitems,
                        'currentnoofitems' : currentnoofitems
                    }
                 
                    print("Old number of items:", oldnoofitems)
                    print("Current number of items:", currentnoofitems)

                    total_noofitems = 0

                    for num in noofitemsdToAdd:
                        num_value = noofitemsdToAdd[num]

                        if isinstance(num_value, set):  # If the value is a set, extract the single element
                            total_noofitems += sum(num_value)
                        elif isinstance(num_value, int):  # If the value is an integer, add it directly
                            total_noofitems += num_value

                    total_noofitems_str1 = str(total_noofitems)

                    # Print the results
                    print("Total number of items:", total_noofitems)

                    #---------------------------------------------------------------------------------------
                    #-------------------------Total-total_time------------------------------------------------------

                    timesToAdd = {
                        'oldTime': oldTime,
                        'curentTime': curentTime
                    }
                    print(oldTime)
                    print(curentTime)
                    # Initialize a timedelta object to store the total time
                    total_time = timedelta()

                    # Iterate through the keys to add the time
                    for times in timesToAdd:                        
                        #time_value = next(iter(timesToAdd[times]))  # Extract the single item from the set                        
                        time_value = timesToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)  # Add time to the set

                                # time_value += time
                        else:
                            time_values = time_value
                        
                    total_time += time_str_to_timedelta(time_values)

                    # Convert total_time back to a string in HH:MM:SS format
                    total_time_str = str(total_time)  

                    # newObj[tempGroup] = item     #-----(THIS LINE UPDATE THE RECENT RECORD TO THE RESPONSE)

                    newObj1[tempGroup]['total-time'] = total_time_str                    
                else:
                    if not isinstance(item['user'], set):
                            item['user'] = {item['user']}  # Convert the user to a set
                            newObj1[tempGroup] = item  
                    newObj1[tempGroup] = item               
                
            combinedArr = []

            for key, value in newObj1.items():
                combinedArr.append(value)

            result_data = combinedArr
            # CODE FOR COMBINING TOTAL-TIME ENDS HERE
            print("newObj1")
            print(newObj1)

            print("result data => sdfdfdfdfdfdfdfdfdf ")
            print(result_data)


            return result_data
        
    elif reportoptions == "scope_subscope":

            finalre = {
                'estimated_time_with_add' : pendulum.duration(),
                'date': set(),
                'user': set(),
                'Service_ID': set(),
                'scope': set(),
                'created_at' : set(),
                'Completed_date' : set(),
                'subscopes': set(),
                'entity': set(),
                # 'no_of_entity' : set(),
                'status': set(),
                'type_of_activity': set(),
                'Nature_of_Work': set(),
                'gst_tan': set(),
                'estimated_d_o_d': set(),
                'estimated_time': set(),
                'member_name': set(),
                'end_time': pendulum.duration(),
                'hold': pendulum.duration(),
                'break': pendulum.duration(),
                'time_diff_work': pendulum.duration(),
                'call': pendulum.duration(),
                'meeting': pendulum.duration(),
                'in_progress': pendulum.duration(),
                'completed': pendulum.duration(),
                'third_report_data' : set(),
                'fourth_report' :  set(),
                'fourth_report2' : set(),
                'fifth_report' : set(),
                'no_of_items' : set(),
                'chargable' : set(),
                'non-chargable' : set(),
                'total-time' : set(),
                'idealname' : pendulum.duration()
            }

            date_time_formate_string = '%Y-%m-%d %H:%M:%S'
            list_data = []
            result_data = []
            


            d1 = picked_date
            d2 = to_date

            # Convert strings to datetime objects
            start_date = datetime.strptime(d1, '%Y-%m-%d')
            end_date = datetime.strptime(d2, '%Y-%m-%d')

            # Generate all dates in between and store as strings
            dates_list = []
            current_date = start_date

            while current_date <= end_date:
                
                dates_list.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)
                

        #     # dates_list contains all dates as strings
            # print(dates_list)
            for item in dates_list:
                reportoptions="twenty"
                list_data.append(totaltime.user_wise_report(db,item,reportoptions))

                
            list_data = [item for item in list_data if item]

            common =  set()
            # print("list_data")
            # print(list_data)  
            for report_list in list_data:
                for entry in report_list:
                        my_set = {str(x) for x in entry['Service_ID']} 
                        
                        common.add(my_set.pop())

                                
            for finalitems in common:
                for report_list in list_data:
                    for entry in report_list:
                        if int(finalitems) in entry['Service_ID']:
                            for key in finalre.keys():
                                        if key == 'end_time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'estimated_time_with_add':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'hold':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'break':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'time_diff_work':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'call':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'meeting':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'in_progress':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'completed':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'idealname':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'no_of_items':
                                            try:
                                                
                                                if len(finalre[key]) == 0:
                                                    finalre[key] = [finalre[key].pop()]+int(entry[key].pop())
                                                else:
                                                    finalre[key] = entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'non-chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'total-time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        else:
                                            finalre[key] = entry[key].union(finalre[key])

                result = {
                    'estimated_time_with_add' : set(),
                    'work_started_date' : set(),
                    'work_ended_date' : set(),
                    'number_of_days_taken' : set(),
                    'number_of_days_delayed' : set(),
                    'actual_date_of_delivery' : set(),
                    'estimated_date_of_delivery' : set(),
                    'number_of_entity' : set(),
                    'estimated_time_minus_chargable_time' : set(),
                    'date': set(),
                    'user': set(),
                    'Service_ID': set(),
                    'created_at' : set(),
                    'Completed_date' : set(),
                    'scope': set(),
                    'subscopes': set(),
                    'entity': set(),
                    # 'no_of_entity' : set(),
                    'status': set(),
                    'type_of_activity': set(),
                    'Nature_of_Work': set(),
                    'gst_tan': set(),
                    'estimated_d_o_d': set(),
                    'estimated_time': set(),
                    'member_name': set(),
                    'end_time': set(),
                    'hold': set(),
                    'break': set(),
                    'time_diff_work': set(),
                    'call': set(),
                    'meeting': set(),
                    'in_progress': set(),
                    'completed': set(),
                    'third_report_data' : set(),
                    'fourth_report' :  set(),
                    'fourth_report2' : set(),
                    'fifth_report' : set(),
                    'no_of_items' : set(),
                    'chargable' : set(),
                    'non-chargable' : set(),
                    'total-time' : set(),
                    'idealname' : set()
                }
                for key in finalre:
                    if isinstance(finalre[key], set):

                            cpof = finalre[key]
                            result[key]= cpof
                        
                            finalre[key] = set()

                    elif isinstance(finalre[key], int):
                        result[key] = finalre[key]
                        #   print(finalre[key],'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
                    else:
                    
                        result[key].add(convert_to_duration(finalre[key]))
                        finalre[key] = pendulum.duration()
                        


        #--------------------------- last calculation


                        

                # Define the set of date strings
                date_strings = result['date']
            
                # Convert the date strings to datetime objects
                dateslast = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                # Find the maximum date
                max_date = max(dateslast)

                min_date = min(dateslast)




                # Define the set of date strings
                date_strings_date = result['estimated_d_o_d']

                # Convert the date strings to datetime objects
                dateslast_date = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings_date}

                # Find the maximum date
                max_date_in_dates = max(dateslast_date)

                        


        #--------------------------- last calculation


                dateesti =  max_date_in_dates.strftime("%Y-%m-%d")

                # Define the set of date strings
                date_strings = result['date']

                # Convert dateesti to a datetime object
                dateesti_dt = datetime.strptime(dateesti, "%Y-%m-%d").date()

                # Convert the set of date strings to a set of datetime objects
                dates = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                # Find and count the dates that are greater than dateesti_dt
                greater_dates = {date for date in dates if date > dateesti_dt}
                count_greater_dates = len(greater_dates)

                    

        #-----------------------------getting estimate time
                        

                estichar = result['estimated_time_with_add'].pop()
                hourses, minuteses, secondses = map(int, estichar.split(':'))

                # Create a pendulum Duration object
                durationes = pendulum.duration(hours=hourses, minutes=minuteses, seconds=secondses)

        #----------------------------------------- chargable time


                nchar = result['chargable'].pop()

                hours, minutes, seconds = map(int, nchar.split(':'))

                # Create a pendulum Duration object
                duration = pendulum.duration(hours=hours, minutes=minutes, seconds=seconds)
                # print(durationes-duration,'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
#------------------------ late of date estimated
                result['chargable'] = nchar
                result['estimated_time_with_add'] = estichar
                result['work_started_date'] =  min_date
                result['work_ended_date'] = max_date
                result['number_of_days_taken'] = len(result['date'])
                result['number_of_days_delayed'] = count_greater_dates
                result['actual_date_of_delivery'] = max_date_in_dates 
                result['estimated_date_of_delivery'] = max_date_in_dates
                result['number_of_entity'] = len(result['entity'])
                result['estimated_time_minus_chargable_time'] = convert_to_duration(durationes-duration)

        #------------------------------ code end
                result_data.append(result)
                result = {}
                # print("result starts here =>")
                # print(result_data)
                # print("result end here =>")
            # CODE FOR COMBINING TOTAL-TIME STARTS HERE
            newObj1 = {}
            
            for item in result_data: 
                #print(item)    

                # print("single item starts ")    

                # print(item)

                # print("single item ends ")    
                tempGroup = ''
                
                for scope in item['scope']:
                    tempGroup+=scope

                for subscopes in item['subscopes']:
                    tempGroup+=subscopes

                key_to_check = tempGroup

                if key_to_check in newObj1:
                    if isinstance(item['user'], set):   
                        newObj1[tempGroup]['user'].update(item['user'])  # Update with a set of users
                    else:
                        newObj1[tempGroup]['user'].add(item['user'])  # Add a single user

                    oldETWA = newObj1[tempGroup]['estimated_time_with_add']
                    currentETWA = item['estimated_time_with_add']

                    oldendtime = newObj1[tempGroup]['end_time']
                    currentendtime = item['end_time']

                    oldhold = newObj1[tempGroup]['hold']
                    currenthold = item['hold']

                    oldbreak = newObj1[tempGroup]['break']
                    currentbreak = item['break']

                    oldTDW = newObj1[tempGroup]['time_diff_work']
                    currentTDW = item['time_diff_work']

                    oldcall = newObj1[tempGroup]['call']
                    currentcall = item['call']

                    oldmeeting = newObj1[tempGroup]['meeting']
                    currentmeeting = item['meeting']

                    oldInProgress = newObj1[tempGroup]['in_progress']
                    currentInProgress = item['in_progress']

                    oldcompleted = newObj1[tempGroup]['completed']
                    currentcompleted = item['completed']

                    oldnoofitems = newObj1[tempGroup]['no_of_items']
                    currentnoofitems = item['no_of_items']

                    oldTime = newObj1[tempGroup]['total-time']
                    curentTime = item['total-time']
#--------------------------------------------------------------------------------------
#--------------------------Total-estimated_time_with_add-------------------------------
                    ETWAToAdd = {
                        'oldETWA': oldETWA,
                        'currentETWA' : currentETWA
                    }
                    print(oldETWA)
                    print(currentETWA)

                    total_ETWA = timedelta()

                    for times in ETWAToAdd:
                        time_value = ETWAToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time) 
                        else:
                            time_values = time_value
                        
                    total_ETWA += time_str_to_timedelta(time_values)

                    total_ETWA_str1 = str(total_ETWA)

                    newObj1[tempGroup]['estimated_time_with_add'] = total_ETWA_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-end_time---------------------------------------------------
                    endtimeToAdd = {
                        'oldendtime': oldendtime,
                        'currentendtime' : currentendtime
                    }

                    print(oldendtime)
                    print(currentendtime)

                    total_endtime = timedelta()

                    for times in endtimeToAdd:
                        time_value = endtimeToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)
                        else:
                            time_values = time_value
                        
                    total_endtime += time_str_to_timedelta(time_values)

                    total_endtime_str1 = str(total_endtime)

                    newObj1[tempGroup]['end_time'] = total_endtime_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-hold---------------------------------------------------
                    holdToAdd = {
                        'oldhold': oldhold,
                        'currenthold' : currenthold
                    }

                    print(oldhold)
                    print(currenthold)

                    total_hold = timedelta()

                    for times in holdToAdd:
                        time_value = holdToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time) 
                        else:
                            time_values = time_value
                        
                    total_hold += time_str_to_timedelta(time_values)

                    total_hold_str1 = str(total_hold)

                    newObj1[tempGroup]['hold'] = total_hold_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-break------------------------------------------------------

                    breakToAdd = {
                        'oldbreak': oldbreak,
                        
                        'currentbreak' : currentbreak
                    }

                    print(oldbreak)
                    print(currentbreak)

                    total_break = timedelta()

                    for times in breakToAdd:
                        time_value = breakToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = ""
                                time_value += time
                        else:
                            time_values = time_value
                        
                    total_break += time_str_to_timedelta(time_values)

                    total_break_str1 = str(total_break)

                    newObj1[tempGroup]['break'] = total_break_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-time_diff_work------------------------------------------------------

                    TDWToAdd = {
                        'oldTDW': oldTDW,
                        'currentTDW' : currentTDW
                    }

                    print(oldTDW)
                    print(currentTDW)

                    total_TDW = timedelta()

                    for times in TDWToAdd:
                        time_value = TDWToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time) 
                        else:
                            time_values = time_value
                        
                    total_TDW += time_str_to_timedelta(time_values)

                    total_TDW_str1 = str(total_TDW)

                    newObj1[tempGroup]['time_diff_work'] = total_TDW_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-call------------------------------------------------------

                    callToAdd = {
                        'oldcall': oldcall,
                        'currentcall' : currentcall
                    }

                    print(oldcall)
                    print(currentcall)

                    total_call = timedelta()

                    for times in callToAdd:
                        time_value = callToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time) 
                        else:
                            time_values = time_value
                        
                    total_call += time_str_to_timedelta(time_values)

                    total_call_str1 = str(total_call)

                    newObj1[tempGroup]['call'] = total_call_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-meeting------------------------------------------------------
                    meetingToAdd = {
                        'oldmeeting': oldmeeting,
                        'currentmeeting' : currentmeeting
                    }

                    print(oldmeeting)
                    print(currentmeeting)

                    total_meeting = timedelta()

                    for times in meetingToAdd:
                        time_value = meetingToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time) 
                        else:
                            time_values = time_value
                        
                    total_meeting += time_str_to_timedelta(time_values)

                    total_meeting_str1 = str(total_meeting)

                    newObj1[tempGroup]['meeting'] =  total_meeting_str1
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-in_progress------------------------------------------------------

                    Inprogresstoadd = {
                        'oldInProgress': oldInProgress,
                        'currentInProgress' : currentInProgress
                    }

                    print(oldInProgress)
                    print(currentInProgress)

                    total_Inprogresstime = timedelta()

                    for times in Inprogresstoadd:
                        time_value = Inprogresstoadd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time) 
                        else:
                            time_values = time_value
                        
                    total_Inprogresstime += time_str_to_timedelta(time_values)

                    total_time_str1 = str(total_Inprogresstime)

                    newObj1[tempGroup]['in_progress'] = total_time_str1 
                    #---------------------------------------------------------------------------------------
                    #-------------------------Total-completed------------------------------------------------------
                    completedToAdd = {
                        'oldcompleted': oldcompleted,
                        'currentcompleted' : currentcompleted

                    }

                    print(oldcompleted)
                    print(currentcompleted)

                    total_completed = timedelta()

                    for times in completedToAdd:
                        time_value = completedToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time1 in time_value:
                                time_value = set()
                                time_value.add(time) 
                        else:
                            time_values = time_value
                        
                    total_completed += time_str_to_timedelta(time_values)

                    total_completed_str1 = str(total_completed)

                    newObj1[tempGroup]['completed'] = total_completed_str1 

                    #------------------------------------------------------------------------------------
                    #-------------------------Total-no_of_items------------------------------------------------------
                    noofitemsdToAdd = {
                        'oldnoofitems': oldnoofitems,
                        'currentnoofitems' : currentnoofitems
                    }
                    print(oldnoofitems)
                    print(oldnoofitems)

                    total_noofitems = 0

                    for num in noofitemsdToAdd:
                        num_value = noofitemsdToAdd[num]

                        if isinstance(num_value, set):  # If the value is a list, sum its elements
                            total_noofitems += sum(num_value)
                        elif isinstance(num_value, int):  # If the value is an integer, add it directly
                            total_noofitems += num_value

                    total_noofitems_str1 = str(total_noofitems)

                    newObj1[tempGroup]['no_of_items'] = total_noofitems_str1 

                    

                    #---------------------------------------------------------------------------------------
                    #-------------------------Total-total_time------------------------------------------------------

                    timesToAdd = {
                        'oldTime': oldTime,
                        'curentTime': curentTime
                    }
                    print(oldTime)
                    print(curentTime)
                    # Initialize a timedelta object to store the total time
                    total_time = timedelta()

                    # Iterate through the keys to add the time
                    for times in timesToAdd:                        
                        #time_value = next(iter(timesToAdd[times]))  # Extract the single item from the set                        
                        time_value = timesToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)
                        else:
                            time_values = time_value
                        
                    total_time += time_str_to_timedelta(time_values)

                    # Convert total_time back to a string in HH:MM:SS format
                    total_time_str = str(total_time)  

                    # newObj[tempGroup] = item     #-----(THIS LINE UPDATE THE RECENT RECORD TO THE RESPONSE)

                    newObj1[tempGroup]['total-time'] = total_time_str                    
                else:
                    if not isinstance(item['user'], set):
                            item['user'] = {item['user']}  # Convert the user to a set
                            newObj1[tempGroup] = item  
                    newObj1[tempGroup] = item               
                
            combinedArr = []

            for key, value in newObj1.items():
                combinedArr.append(value)

            result_data = combinedArr
            # CODE FOR COMBINING TOTAL-TIME ENDS HERE

            print("newObj1")
            print(newObj1)

            print("result data => sdfdfdfdfdfdfdfdfdf ")
            print(result_data)


            return result_data
        
    elif reportoptions == "natureofwork_membername":

            finalre = {
                'estimated_time_with_add' : pendulum.duration(),
                'date': set(),
                'user': set(),
                'Service_ID': set(),
                'scope': set(),
                'created_at' : set(),
                'Completed_date' : set(),
                'subscopes': set(),
                'entity': set(),
                # 'no_of_entity' : set(),
                'status': set(),
                'type_of_activity': set(),
                'Nature_of_Work': set(),
                'gst_tan': set(),
                'estimated_d_o_d': set(),
                'estimated_time': set(),
                'member_name': set(),
                'end_time': pendulum.duration(),
                'hold': pendulum.duration(),
                'break': pendulum.duration(),
                'time_diff_work': pendulum.duration(),
                'call': pendulum.duration(),
                'meeting': pendulum.duration(),
                'in_progress': pendulum.duration(),
                'completed': pendulum.duration(),
                'third_report_data' : set(),
                'fourth_report' :  set(),
                'fourth_report2' : set(),
                'fifth_report' : set(),
                'no_of_items' : set(),
                'chargable' : set(),
                'non-chargable' : set(),
                'total-time' : set(),
                'idealname' : pendulum.duration()
            }

            date_time_formate_string = '%Y-%m-%d %H:%M:%S'
            list_data = []
            result_data = []
            


            d1 = picked_date
            d2 = to_date

            # Convert strings to datetime objects
            start_date = datetime.strptime(d1, '%Y-%m-%d')
            end_date = datetime.strptime(d2, '%Y-%m-%d')

            # Generate all dates in between and store as strings
            dates_list = []
            current_date = start_date

            while current_date <= end_date:
                
                dates_list.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(days=1)
                

        #     # dates_list contains all dates as strings
            # print(dates_list)
            for item in dates_list:
                reportoptions="twenty"
                list_data.append(totaltime.user_wise_report(db,item,reportoptions))

                
            list_data = [item for item in list_data if item]

            common =  set()
            # print("list_data")
            # print(list_data)  
            for report_list in list_data:
                for entry in report_list:
                        my_set = {str(x) for x in entry['Service_ID']} 
                        
                        common.add(my_set.pop())

                                
            for finalitems in common:
                for report_list in list_data:
                    for entry in report_list:
                        if int(finalitems) in entry['Service_ID']:
                            for key in finalre.keys():
                                        if key == 'end_time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'estimated_time_with_add':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'hold':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'break':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'time_diff_work':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'call':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'meeting':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'in_progress':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'completed':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'idealname':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'no_of_items':
                                        
                                            try:
                                                
                                                if len(finalre[key]) == 0:
                                                    finalre[key] = [finalre[key].pop()]+int(entry[key].pop())
                                                else:
                                                    finalre[key] = entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'non-chargable':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        elif key == 'total-time':
                                            try:

                                                finalre[key] = finalre[key]+entry[key]
                                            except:
                                                finalre[key] = entry[key]
                                        else:
                                            finalre[key] = entry[key].union(finalre[key])

                result = {
                    'estimated_time_with_add' : set(),
                    'work_started_date' : set(),
                    'work_ended_date' : set(),
                    'number_of_days_taken' : set(),
                    'number_of_days_delayed' : set(),
                    'actual_date_of_delivery' : set(),
                    'estimated_date_of_delivery' : set(),
                    'number_of_entity' : set(),
                    'estimated_time_minus_chargable_time' : set(),
                    'date': set(),
                    'user': set(),
                    'Service_ID': set(),
                    'created_at' : set(),
                    'Completed_date' : set(),
                    'scope': set(),
                    'subscopes': set(),
                    'entity': set(),
                    # 'no_of_entity' : set(),
                    'status': set(),
                    'type_of_activity': set(),
                    'Nature_of_Work': set(),
                    'gst_tan': set(),
                    'estimated_d_o_d': set(),
                    'estimated_time': set(),
                    'member_name': set(),
                    'end_time': set(),
                    'hold': set(),
                    'break': set(),
                    'time_diff_work': set(),
                    'call': set(),
                    'meeting': set(),
                    'in_progress': set(),
                    'completed': set(),
                    'third_report_data' : set(),
                    'fourth_report' :  set(),
                    'fourth_report2' : set(),
                    'fifth_report' : set(),
                    'no_of_items' : set(),
                    'chargable' : set(),
                    'non-chargable' : set(),
                    'total-time' : set(),
                    'idealname' : set()
                }
                for key in finalre:
                    if isinstance(finalre[key], set):

                            cpof = finalre[key]
                            result[key]= cpof
                        
                            finalre[key] = set()

                    elif isinstance(finalre[key], int):
                        result[key] = finalre[key]
                        #   print(finalre[key],'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
                    else:
                    
                        result[key].add(convert_to_duration(finalre[key]))
                        finalre[key] = pendulum.duration()
                


        #--------------------------- last calculation


                        

                # Define the set of date strings
                date_strings = result['date']
            
                # Convert the date strings to datetime objects
                dateslast = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                # Find the maximum date
                max_date = max(dateslast)

                min_date = min(dateslast)




                # Define the set of date strings
                date_strings_date = result['estimated_d_o_d']

                # Convert the date strings to datetime objects
                dateslast_date = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings_date}

                # Find the maximum date
                max_date_in_dates = max(dateslast_date)

                        


        #--------------------------- last calculation


                dateesti =  max_date_in_dates.strftime("%Y-%m-%d")

                # Define the set of date strings
                date_strings = result['date']

                # Convert dateesti to a datetime object
                dateesti_dt = datetime.strptime(dateesti, "%Y-%m-%d").date()

                # Convert the set of date strings to a set of datetime objects
                dates = {datetime.strptime(date, "%Y-%m-%d").date() for date in date_strings}

                # Find and count the dates that are greater than dateesti_dt
                greater_dates = {date for date in dates if date > dateesti_dt}
                count_greater_dates = len(greater_dates)

                    

        #-----------------------------getting estimate time
                        

                estichar = result['estimated_time_with_add'].pop()
                hourses, minuteses, secondses = map(int, estichar.split(':'))

                # Create a pendulum Duration object
                durationes = pendulum.duration(hours=hourses, minutes=minuteses, seconds=secondses)

        #----------------------------------------- chargable time


                nchar = result['chargable'].pop()

                hours, minutes, seconds = map(int, nchar.split(':'))

                # Create a pendulum Duration object
                duration = pendulum.duration(hours=hours, minutes=minutes, seconds=seconds)
                # print(durationes-duration,'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
#------------------------ late of date estimated
                result['chargable'] = nchar
                result['estimated_time_with_add'] = estichar
                result['work_started_date'] =  min_date
                result['work_ended_date'] = max_date
                result['number_of_days_taken'] = len(result['date'])
                result['number_of_days_delayed'] = count_greater_dates
                result['actual_date_of_delivery'] = max_date_in_dates 
                result['estimated_date_of_delivery'] = max_date_in_dates
                result['number_of_entity'] = len(result['entity'])
                result['estimated_time_minus_chargable_time'] = convert_to_duration(durationes-duration)

        #------------------------------ code end
                result_data.append(result)
                result = {}
                # print("result starts here =>")
                # print(result_data)
                # print("result end here =>")
            # CODE FOR COMBINING TOTAL-TIME STARTS HERE
            newObj1 = {}
            
            for item in result_data: 
                #print(item)    

                # print("single item starts ")    

                # print(item)

                # print("single item ends ")    
                tempGroup = ''
                
                for Nature_of_Work in item['Nature_of_Work']:
                    tempGroup+=Nature_of_Work

                for member_name in item['member_name']:
                    tempGroup+=member_name

                key_to_check = tempGroup

            
                if key_to_check in newObj1:
                    if isinstance(item['user'], set):   
                        newObj1[tempGroup]['user'].update(item['user'])  # Update with a set of users
                    else:
                        newObj1[tempGroup]['user'].add(item['user'])  # Add a single user

                    oldETWA = newObj1[tempGroup]['estimated_time_with_add']
                    currentETWA = item['estimated_time_with_add']

                    oldendtime = newObj1[tempGroup]['end_time']
                    currentendtime = item['end_time']

                    oldhold = newObj1[tempGroup]['hold']
                    currenthold = item['hold']

                    oldbreak = newObj1[tempGroup]['break']
                    currentbreak = item['break']

                    oldTDW = newObj1[tempGroup]['time_diff_work']
                    currentTDW = item['time_diff_work']

                    oldcall = newObj1[tempGroup]['call']
                    currentcall = item['call']

                    oldmeeting = newObj1[tempGroup]['meeting']
                    currentmeeting = item['meeting']

                    oldInProgress = newObj1[tempGroup]['in_progress']
                    currentInProgress = item['in_progress']

                    oldcompleted = newObj1[tempGroup]['completed']
                    currentcompleted = item['completed']

                    oldnoofitems = newObj1[tempGroup]['no_of_items']
                    currentnoofitems = item['no_of_items']

                    oldTime = newObj1[tempGroup]['total-time']
                    curentTime = item['total-time']
#--------------------------------------------------------------------------------------
#--------------------------Total-estimated_time_with_add-------------------------------
                    ETWAToAdd = {
                        'oldETWA': oldETWA,
                        'currentETWA' : currentETWA
                    }
                    print(oldETWA)
                    print(currentETWA)

                    total_ETWA = timedelta()

                    for times in ETWAToAdd:
                        time_value = ETWAToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)
                        else:
                            time_values = time_value
                        
                    total_ETWA += time_str_to_timedelta(time_values)

                    total_ETWA_str1 = str(total_ETWA)

                    newObj1[tempGroup]['estimated_time_with_add'] = total_ETWA_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-end_time---------------------------------------------------
                    endtimeToAdd = {
                        'oldendtime': oldendtime,
                        'currentendtime' : currentendtime
                    }

                    print(oldendtime)
                    print(currentendtime)

                    total_endtime = timedelta()

                    for times in endtimeToAdd:
                        time_value = endtimeToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)
                        else:
                            time_values = time_value
                        
                    total_endtime += time_str_to_timedelta(time_values)

                    total_endtime_str1 = str(total_endtime)

                    newObj1[tempGroup]['end_time'] = total_endtime_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-hold---------------------------------------------------
                    holdToAdd = {
                        'oldhold': oldhold,
                        'currenthold' : currenthold
                    }

                    print(oldhold)
                    print(currenthold)

                    total_hold = timedelta()

                    for times in holdToAdd:
                        time_value = holdToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)
                        else:
                            time_values = time_value
                        
                    total_hold += time_str_to_timedelta(time_values)

                    total_hold_str1 = str(total_hold)

                    newObj1[tempGroup]['hold'] = total_hold_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-break------------------------------------------------------

                    breakToAdd = {
                        'oldbreak': oldbreak,
                        'currentbreak' : currentbreak
                    }

                    print(oldbreak)
                    print(currentbreak)

                    total_break = timedelta()

                    for times in breakToAdd:
                        time_value = breakToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)
                        else:
                            time_values = time_value
                        
                    total_break += time_str_to_timedelta(time_values)

                    total_break_str1 = str(total_break)

                    newObj1[tempGroup]['break'] = total_break_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-time_diff_work------------------------------------------------------

                    TDWToAdd = {
                        'oldTDW': oldTDW,
                        'currentTDW' : currentTDW
                    }

                    print(oldTDW)
                    print(currentTDW)

                    total_TDW = timedelta()

                    for times in TDWToAdd:
                        time_value = TDWToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)
                        else:
                            time_values = time_value
                        
                    total_TDW += time_str_to_timedelta(time_values)

                    total_TDW_str1 = str(total_TDW)

                    newObj1[tempGroup]['time_diff_work'] = total_TDW_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-call------------------------------------------------------

                    callToAdd = {
                        'oldcall': oldcall,
                        'currentcall' : currentcall
                    }

                    print(oldcall)
                    print(currentcall)

                    total_call = timedelta()

                    for times in callToAdd:
                        time_value = callToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)
                        else:
                            time_values = time_value
                        
                    total_call += time_str_to_timedelta(time_values)

                    total_call_str1 = str(total_call)

                    newObj1[tempGroup]['call'] = total_call_str1 
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-meeting------------------------------------------------------
                    meetingToAdd = {
                        'oldmeeting': oldmeeting,
                        'currentmeeting' : currentmeeting
                    }

                    print(oldmeeting)
                    print(currentmeeting)

                    total_meeting = timedelta()

                    for times in meetingToAdd:
                        time_value = meetingToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)
                        else:
                            time_values = time_value
                        
                    total_meeting += time_str_to_timedelta(time_values)

                    total_meeting_str1 = str(total_meeting)

                    newObj1[tempGroup]['meeting'] =  total_meeting_str1
                    #------------------------------------------------------------------------------------------
                    #-------------------------Total-in_progress------------------------------------------------------

                    # Inprogresstoadd = {
                    #     'oldInProgress': oldInProgress,
                    #     'currentInProgress' : currentInProgress
                    # }

                    # print(oldInProgress)
                    # print(currentInProgress)

                    # total_Inprogresstime = timedelta()

                    # for times in Inprogresstoadd:
                    #     time_value = Inprogresstoadd[times]
                    #     time_values = ''

                    #     if isinstance(time_value, set):
                    #         for time in time_value:
                    #             time_value = ""
                    #             time_value += time
                    #     else:
                    #         time_values = time_value
                        
                    #     total_Inprogresstime += time_str_to_timedelta(time_value)

                    # total_time_str1 = str(total_Inprogresstime)

                    # newObj1[tempGroup]['in_progress'] = total_time_str1 

                    Inprogresstoadd = {
                        'oldInProgress': oldInProgress,
                        'currentInProgress' : currentInProgress
                    }

                    print(oldInProgress)
                    print(currentInProgress)

                    total_Inprogresstime = timedelta()

                    for times in Inprogresstoadd:
                        time_value = Inprogresstoadd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)
                        else:
                            time_values = time_value
                        
                    total_Inprogresstime += time_str_to_timedelta(time_values)

                    total_time_str1 = str(total_Inprogresstime)

                    newObj1[tempGroup]['in_progress'] = total_time_str1 
                    #---------------------------------------------------------------------------------------
                    #-------------------------Total-completed------------------------------------------------------
                    completedToAdd = {
                        'oldcompleted': oldcompleted,
                        'currentcompleted' : currentcompleted

                    }

                    print(oldcompleted)
                    print(currentcompleted)

                    total_completed = timedelta()

                    for times in completedToAdd:
                        time_value = completedToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time)
                        else:
                            time_values = time_value
                        
                    total_completed += time_str_to_timedelta(time_values)

                    total_completed_str1 = str(total_completed)

                    newObj1[tempGroup]['completed'] = total_completed_str1 

                    #------------------------------------------------------------------------------------
                    #-------------------------Total-no_of_items------------------------------------------------------

                    noofitemsdToAdd = {
                        'oldnoofitems': oldnoofitems,
                        'currentnoofitems' : currentnoofitems
                    }
                    print(oldnoofitems)
                    print(oldnoofitems)

                    total_noofitems = 0

                    for num in noofitemsdToAdd:
                        num_value = noofitemsdToAdd[num]

                        if isinstance(num_value, set):  # If the value is a list, sum its elements
                            total_noofitems += sum(num_value)
                        elif isinstance(num_value, int):  # If the value is an integer, add it directly
                            total_noofitems += num_value

                    total_noofitems_str1 = str(total_noofitems)

                    newObj1[tempGroup]['no_of_items'] = total_noofitems_str1 


                    #---------------------------------------------------------------------------------------
                    #-------------------------Total-total_time------------------------------------------------------

                    timesToAdd = {
                        'oldTime': oldTime,
                        'curentTime': curentTime
                    }
                    print(oldTime)
                    print(curentTime)
                    # Initialize a timedelta object to store the total time
                    total_time = timedelta()

                    # Iterate through the keys to add the time
                    for times in timesToAdd:                        
                        #time_value = next(iter(timesToAdd[times]))  # Extract the single item from the set                        
                        time_value = timesToAdd[times]
                        time_values = ''

                        if isinstance(time_value, set):
                            for time in time_value:
                                time_value = set()
                                time_value.add(time) 
                        else:
                            time_values = time_value
                        
                    total_time += time_str_to_timedelta(time_values)

                    # Convert total_time back to a string in HH:MM:SS format
                    total_time_str = str(total_time)  

                    # newObj[tempGroup] = item     #-----(THIS LINE UPDATE THE RECENT RECORD TO THE RESPONSE)

                    newObj1[tempGroup]['total-time'] = total_time_str                    
                else:
                    if not isinstance(item['user'], set):
                            item['user'] = {item['user']}  # Convert the user to a set
                            newObj1[tempGroup] = item  
                    newObj1[tempGroup] = item               
                
            combinedArr = []

            for key, value in newObj1.items():
                combinedArr.append(value)

            result_data = combinedArr
            # CODE FOR COMBINING TOTAL-TIME ENDS HERE

            print("newObj1")
            print(newObj1)

            print("result data => sdfdfdfdfdfdfdfdfdf ")
            print(result_data)


            return result_data
#--------------------------------------------------------------------------- Paupathi


def scope_add(scope: str,db :Session):
   db_tds = models.scope(scope = scope)
   db.add(db_tds)
   try:
        db.commit()
        return "Success"
   except :
       db.rollback()
       return "Failure"

def get_scope(db:Session):
    return db.query(models.scope).all()

def scope_delete(scope_id: int, db: Session):
    
    db_scope = db.query(models.scope).filter(models.scope.scope_id == scope_id).first()
    
    
    if db_scope is None:
        return "Scope not found"

    
    db.delete(db_scope)
    
    try:
        db.commit()
        return "Success"
    except:
        db.rollback()
        return "Failure"
    
def scope_update(scope_id: int, new_scope: str, db: Session):
    
    db_scope = db.query(models.scope).filter(models.scope.scope_id == scope_id).first()
    
    
    if db_scope is None:
        return "Scope not found"

    
    db_scope.scope = new_scope
    
    try:
        db.commit()
        return "Success"
    except:
        db.rollback()
        return "Failure"


def sub_scope_add(scope_id: int, sub_scope: str, db: Session):
    # Create a new sub_scope instance
    db_sub_scope = models.sub_scope(scope_id=scope_id, sub_scope=sub_scope)
    db.add(db_sub_scope)
    
    try:
        db.commit()
        db.refresh(db_sub_scope)
        return "Success"
    except:
        db.rollback()
        return "Failure"

def sub_scope_delete(sub_scope_id: int, db: Session):
    # Fetch the sub_scope to delete
    db_sub_scope = db.query(models.sub_scope).filter(models.sub_scope.sub_scope_id == sub_scope_id).first()
    
    # If the sub_scope is not found, return an error message
    if db_sub_scope is None:
        return "Sub-scope not found"

    # Delete the sub_scope
    db.delete(db_sub_scope)
    
    try:
        db.commit()
        return "Success"
    except:
        db.rollback()
        return "Failure"

def sub_scope_update(sub_scope_id: int, new_scope_id: int, new_sub_scope: str, db: Session):
    
    db_sub_scope = db.query(models.sub_scope).filter(models.sub_scope.sub_scope_id == sub_scope_id).first()
    
    
    if db_sub_scope is None:
        return "Sub-scope not found"

    
    db_sub_scope.scope_id = new_scope_id
    db_sub_scope.sub_scope = new_sub_scope
    
    try:
        db.commit()
        db.refresh(db_sub_scope)
        return "Success"
    except:
        db.rollback()
        return None

def get_sub_scope(scope_id,db:Session):

    return db.query(models.sub_scope).filter(models.sub_scope.scope_id == scope_id).all()

def logintime_add(logtime: str,userid: int,db :Session):
   db_logintime = models.login_time(userid = userid, login_time = logtime)
   db.add(db_logintime)
   try:
        db.commit()
        return "Success"
   except :
       db.rollback()
       return "Failure"
   
# def logout_time_add(logouttime: str,userid: int,db :Session):

#     db_res2 = db.query(models.login_time).filter(models.login_time.userid == userid).order_by(models.login_time.login_id.desc()).first()
    
    
    
#     db_res2.logout_time = logouttime
#     db.commit()
#     return "Success"

def entityadd(entityname: str,tanorgst: str,tanvalue: str,db :Session):
    entity_name_upper = entityname.upper()
   
    db_logintime = models.entityadd(entityname = entity_name_upper, gstortan = tanorgst,tanvalue = tanvalue)
    db.add(db_logintime)
    try:
            db.commit()
            return "Success"
    except :
            db.rollback()
            return "Failure"
   
def get_entity_data(db:Session):

    return db.query(models.entityadd).all()

def get_filter_entitydata(id,db:Session):

    return db.query(models.entityadd).filter(models.entityadd.id == id).all()


# --------------------------------logout auto start

import pytz
def calculate_work_hours(userid: int, specific_date: str, db: Session):
    print(userid, specific_date, 'Calculating work hours...')

    timezone = pytz.timezone('Asia/Kolkata')

    # Parse the specific date
    date_object = datetime.strptime(specific_date, '%Y-%m-%d')

    # Start and end of the day
    start_of_day = timezone.localize(date_object.replace(hour=0, minute=0, second=0, microsecond=0))
    end_of_day = timezone.localize(date_object.replace(hour=23, minute=59, second=59, microsecond=999999))

    # Query the login/logout data for the specific user and date
    login_logout_data = db.query(models.login_time).filter(
        and_(
            models.login_time.userid == userid,
            models.login_time.login_time >= start_of_day.strftime('%Y-%m-%d %H:%M:%S'),
            models.login_time.login_time <= end_of_day.strftime('%Y-%m-%d %H:%M:%S')
        )
    ).all()

    total_seconds_worked = 0
    current_time = datetime.now(timezone)

    for record in login_logout_data:
        # Parse login time
        login_dt = timezone.localize(datetime.strptime(record.login_time, '%Y-%m-%d %H:%M:%S'))

        # Parse logout time, or use current time if logout time is None
        if record.logout_time:
            logout_dt = timezone.localize(datetime.strptime(record.logout_time, '%Y-%m-%d %H:%M:%S'))
        else:
            logout_dt = current_time

        # Ensure logout time is after login time
        if logout_dt < login_dt:
            print(f"Warning: Logout time {logout_dt} is before login time {login_dt}. Skipping record.")
            continue

        # Calculate seconds worked for this session
        seconds_worked = (logout_dt - login_dt).total_seconds()
        total_seconds_worked += seconds_worked

    # Convert total seconds to hours, minutes, and seconds
    total_hours = int(total_seconds_worked // 3600)
    remaining_minutes = int((total_seconds_worked % 3600) // 60)
    remaining_seconds = int(total_seconds_worked % 60)

    print(f"Total Hours Worked: {total_hours}, Remaining Minutes: {remaining_minutes}, Remaining Seconds: {remaining_seconds}")

    return f"{total_hours}:{remaining_minutes:02d}:{remaining_seconds:02d}"

# =======================================logout time auto update===================================

# def time_check_logout(db: Session):
#     ist = pytz.timezone('Asia/Kolkata')
#     try:
#         current_time = datetime.now(ist)
#         current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
#         print(f"Checking time: {current_time_str} IST")

#         # This runs at 14:15 daily
#         records_to_update = db.query(models.login_time).filter(
#             or_(models.login_time.logout_time == '', models.login_time.logout_time.is_(None))
#         ).all()

#         print(f"Records before update: {records_to_update}")

#         if records_to_update:
#             updated_count = db.query(models.login_time).filter(
#                 or_(models.login_time.logout_time == '', models.login_time.logout_time.is_(None))
#             ).update({models.login_time.logout_time: current_time_str}, synchronize_session=False)
            
#             db.commit()
#             print(f"Number of records updated: {updated_count}")

#             records_updated = db.query(models.login_time).filter(
#                 models.login_time.logout_time == current_time_str
#             ).all()

#             print(f"Records after update: {records_updated}")
#         else:
#             print("No records found to update.")
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")           

# import logging
# # Configure logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# ist = pytz.timezone('Asia/Kolkata')

# def time_check_logout(db: Session):

#     try:
#         current_time = datetime.now(ist)
#         current_timess = datetime.now()
#         current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
#         current_time_strss = current_timess.strftime('%Y-%m-%d %H:%M:%S')

#         logger.info(f"Checking time: {current_time_str} IST")

#         # Fetch records where logout_time is empty or None
#         records_to_update = db.query(models.login_time).filter(
#             or_(models.login_time.logout_time == '', models.login_time.logout_time.is_(None))
#         ).all()

#         logger.info(f"Records before update: {records_to_update}")

#         if records_to_update:
#             # Update logout_time for those records
#             updated_count = db.query(models.login_time).filter(
#                 or_(models.login_time.logout_time == '', models.login_time.logout_time.is_(None))
#             ).update({models.login_time.logout_time: current_time_str}, synchronize_session=False)
            
#             db.commit()
#             logger.info(f"Number of records updated: {updated_count}")

#             # Query the records that were updated
#             records_updated = db.query(models.login_time).filter(
#                 models.login_time.logout_time == current_time_str
#             ).all()

#             logger.info(f"Records after update: {records_updated}")

#             # Update WorkSession's end_time with the updated logout_time
#             for record in records_updated:
#                 work_session = db.query(models.WorkSession).filter(
#                     and_(
#                         models.WorkSession.user_id == models.TL.Assigned_To,
#                         models.WorkSession.end_time == ''  # Ensure end_time is empty
#                     )
#                 ).first()

#                 if work_session:
#                     # Calculate total time worked
#                     # Update WorkSession with end time and total time worked
#                     work_session.end_time = current_time_strss
#                     total_worked = calculate_total_times(work_session.start_time, work_session.end_time)
#                     work_session.total_time_worked = total_worked  # Assuming there's a field for total worked time
#                     db.add(work_session)

#             db.commit()
#             logger.info("Work sessions updated with end times and total worked times.")
        
#         else:
#             logger.info("No records found to update.")

#     except Exception as e:
#         logger.error(f"An error occurred: {str(e)}")

# ---------------new logout update 01/
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(_name_)

ist = pytz.timezone('Asia/Kolkata')


# def time_check_logout(db: Session):
#     try:
#         current_time = datetime.now(ist)
#         current_timess = datetime.now()
#         current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
#         current_time_strss = current_timess.strftime('%Y-%m-%d %H:%M:%S')

#         # logger.info(f"Checking time: {current_time_str} IST")

#         # Fetch records where logout_time is empty or None
#         records_to_update = db.query(models.login_time).filter(
#             or_(models.login_time.logout_time == '', models.login_time.logout_time.is_(None))
#         ).all()

#         # logger.info(f"Records before update: {records_to_update}")

#         if records_to_update:
#             # Update logout_time for those records
#             updated_count = db.query(models.login_time).filter(
#                 or_(models.login_time.logout_time == '', models.login_time.logout_time.is_(None))
#             ).update({models.login_time.logout_time: current_time_str}, synchronize_session=False)
            
#             db.commit()
#             # logger.info(f"Number of records updated: {updated_count}")

#             # Query the records that were updated
#             records_updated = db.query(models.login_time).filter(
#                 models.login_time.logout_time == current_time_str
#             ).all()

#             # logger.info(f"Records after update: {records_updated}")

#             # Update WorkSession's end_time with the updated logout_time
#             for record in records_updated:
#                 work_sessions = db.query(models.WorkSession).filter(
#                     and_(
#                         models.WorkSession.user_id == models.TL.Assigned_To,
#                         or_(models.WorkSession.end_time == '', models.WorkSession.end_time.is_(None))
#                     )
#                 ).all()

#                 for work_session in work_sessions:
#                     # Update WorkSession with end time and total time worked
#                     work_session.end_time = current_time_strss
#                     total_worked = calculate_total_times(work_session.start_time, work_session.end_time)
#                     work_session.total_time_worked = total_worked  # Assuming there's a field for total worked time
#                     db.add(work_session)

#             db.commit()
#             # logger.info("Work sessions updated with end times and total worked times.")
        
#         else:
#             pass
#             # logger.info("No records found to update.")

#     except Exception as e:
#         pass
#         # logger.error(f"An error occurred: {str(e)}")

def time_check_logout(db: Session):
    try:
        # Get current time in IST
        current_time = datetime.now(ist)
        current_time_utc = datetime.now()
        current_time_str = current_time.strftime('%Y-%m-%d %H:%M:%S')
        current_time_str_utc = current_time_utc.strftime('%Y-%m-%d %H:%M:%S')

        # Fetch records where logout_time is empty or None
        records_to_update = db.query(models.login_time).filter(
            or_(models.login_time.logout_time == '', models.login_time.logout_time.is_(None))
        ).all()

        if records_to_update:
            # Update logout_time for those records
            db.query(models.login_time).filter(
                or_(models.login_time.logout_time == '', models.login_time.logout_time.is_(None))
            ).update({models.login_time.logout_time: current_time_str}, synchronize_session=False)

            db.commit()

            # Query the records that were updated
            records_updated = db.query(models.login_time).filter(
                models.login_time.logout_time == current_time_str
            ).all()

            # Update WorkSession's end_time with the updated logout_time
            for record in records_updated:
                assigned_tasks = db.query(models.TL).filter(models.TL.Assigned_To == record.userid).all()

                for task in assigned_tasks:
                    work_sessions = db.query(models.WorkSession).filter(
                        and_(
                            models.WorkSession.user_id == task.Assigned_To,
                            or_(models.WorkSession.end_time == '', models.WorkSession.end_time.is_(None))
                        )
                    ).all()

                    for work_session in work_sessions:
                        # Update WorkSession with end time and total time worked
                        work_session.end_time = current_time_str_utc
                        total_worked = calculate_total_times(work_session.start_time, work_session.end_time)
                        work_session.total_time_worked = total_worked  # Assuming there's a field for total worked time
                        db.add(work_session)

            db.commit()

    except Exception as e:
        print(f"An error occurred: {str(e)}")


# --------------------------------logout auto end



            
#-------------------------------Change the Wrok statuses to Break, Call, Metting and Work in Progress--------------------------------------------


def check_and_update_work_status(db: Session):
    # Get the current time in IST
    # ist = pytz.timezone('Asia/Kolkata')
    current_datetime = datetime.now()

    # Query all relevant records
    all_records = db.query(models.TL).filter(models.TL.work_status.in_(
        ["Break", "Clarification Call", "Meeting", "Work in Progress"]
    )).all()

    print(f"Found {len(all_records)} records to process.")

    for db_res in all_records:
        # Get the current time for the record update
        current_time_str = current_datetime.strftime('%Y-%m-%d %H:%M:%S')

        # Update work status and corresponding records
        if db_res.work_status == "Break":
            db_res.work_status = "End Of Day"
            break_record = db.query(models.BREAK).filter(
                models.BREAK.Service_ID == db_res.Service_ID).first()
            if break_record:
                break_record.break_time_end = current_time_str
                db.add(break_record)

        elif db_res.work_status == "Clarification Call":
            db_res.work_status = "End Of Day"
            call_record = db.query(models.CALL).filter(
                models.CALL.Service_ID == db_res.Service_ID).first()
            if call_record:
                call_record.call_time_end = current_time_str
                db.add(call_record)

        elif db_res.work_status == "Meeting":
            db_res.work_status = "End Of Day"
            meeting_record = db.query(models.MEETING).filter(
                models.MEETING.Service_ID == db_res.Service_ID).first()
            if meeting_record:
                meeting_record.meeting_time_end = current_time_str
                db.add(meeting_record)

        elif db_res.work_status == "Work in Progress":
            db_res.work_status = "End Of Day"
            work_in_progress_record = db.query(models.TL).filter(
                models.TL.Service_ID == db_res.Service_ID).first()
            if work_in_progress_record:
                db_res.working_time = current_time_str
                db.add(work_in_progress_record)

        # Insert a new End Of Day (EOD) record
        end_of_day_record = models.END_OF_DAY(
            Service_ID=db_res.Service_ID,
            user_id=db_res.Assigned_To,
            end_time_start=current_time_str,
            remarks="Auto EOD"
        )
        db.add(end_of_day_record)

        # Insert a new Work Session record when automict
        work_session_record = models.WorkSession(
            user_id=db_res.Assigned_To,
            start_time=current_time_str  
        )
        db.add(work_session_record)

        

    # Commit all changes to the database
    try:
        db.commit()
        print("Work statuses updated successfully.")
    except Exception as e:
        print(f"Error committing changes: {e}")

# --------------------------------end     


# ------------------------------------------NEW IDEAL TIME and login satuts change CODE START

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

def idealtime(userid: int, check_status: str, db: Session):

    print("----------------------------->") 
    print(f"User ID: {userid}, Check Status: {check_status}")
    print("----------------------------->") 
 
    # ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now()
    current_time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")

    # Fetch the current work session for the user
    work_session = db.query(models.WorkSession).filter(
        models.WorkSession.user_id == userid
    ).order_by(models.WorkSession.id.desc()).first()

    # Check work status in TL table
    tl_records = db.query(models.TL).filter(models.TL.Assigned_To == userid).order_by(models.TL.Service_ID.desc()).all()
    
    new_session_created = False  # Track if a new session was created

    for tl_record in tl_records:
        if check_status == "Login":
            if tl_record.work_status == "Work in Progress":
                tl_record.work_status = "Hold"
                db.commit()
                print("Updated In Progress to Hold in TL table.")
                
                # new_session = models.WorkSession(user_id=userid, start_time=current_time_str)
                # db.add(new_session)
                # db.commit()
                # print("New session created due to working progress login.")

                # end_of_day_entry = models.END_OF_DAY(
                #     Service_ID=tl_record.Service_ID,
                #     user_id=userid,
                #     end_time_start=current_time_str,
                #     remarks="Work in Progress to EOD"
                # )
                # db.add(end_of_day_entry)
                hold_entry =models.HOLD(
                    Service_ID=tl_record.Service_ID,
                    user_id=userid,
                    hold_time_start=current_time_str,
                    remarks="Work in Progress to Hold"
                )
                db.add(hold_entry)

                try:
                    db.commit()
                    print("New Hold created.")
                except IntegrityError:
                    db.rollback()
                    print("Failed to create Hold due to IntegrityError.")
                
            elif tl_record.work_status == "Hold":
                if work_session and (work_session.end_time is None or work_session.end_time == ""):
                    work_session.end_time = current_time_str
                    db.commit()

                    start_time = datetime.strptime(work_session.start_time, "%Y-%m-%d %H:%M:%S")
                    end_time = datetime.strptime(work_session.end_time, "%Y-%m-%d %H:%M:%S")
                    total_time = end_time - start_time

                    work_session.total_time_worked = str(total_time)
                    db.commit()
                    print(f"Updated end_time of previous session to: {work_session.end_time}")

                if not new_session_created:
                    new_session = models.WorkSession(user_id=userid, start_time=current_time_str)
                    db.add(new_session)
                    db.commit()
                    print("New session created due to Login while work status is Hold.")
                    new_session_created = True  # Mark that a new session has been created

            elif check_status == "Login" and tl_record.work_status == "Break":
                tl_record.work_status = "Hold"
                db.commit()
                print("Updated Break in TL table to Hold.")

                # new_session = models.WorkSession(user_id=userid, start_time=current_time_str)
                # db.add(new_session)
                # db.commit()
                # print("New session created due to Break login.")

                break_record = db.query(models.BREAK).filter(
                    models.BREAK.user_id == userid,
                    models.BREAK.break_time_end == ""
                ).first()

                if break_record:
                    break_record.break_time_end = current_time_str
                    break_record.remarks = 'Break to Hold'
                    db.commit()
                    print(f"Updated break_time_end for Break record to: {break_record.break_time_end}")

                # end_of_day_record = models.END_OF_DAY(
                #     Service_ID=tl_record.Service_ID,
                #     user_id=userid,
                #     end_time_start=current_time_str,
                #     remarks="Break to EOD"
                # )
                # db.add(end_of_day_record)
                hold_entry =models.HOLD(
                    Service_ID=tl_record.Service_ID,
                    user_id=userid,
                    hold_time_start=current_time_str,
                    remarks="Break to Hold"
                )
                db.add(hold_entry)
                db.commit()
                print("New Hold record created.")


            elif check_status == "Login" and tl_record.work_status == "Meeting":  
                #  Change the TL status to End Of Day
                tl_record.work_status = "Hold"
                db.commit()
                print("Updated Break in TL table to Hold.")

                # new_session = models.WorkSession(user_id=userid, start_time=current_time_str)
                # db.add(new_session)
                # db.commit()
                # print("New session created due to Meeting login.")

                # Update the previous Meet record
                meet_record = db.query(models.MEETING).filter(
                    models.MEETING.user_id == userid,
                    models.MEETING.meeting_time_end == ""
                ).first()

                if meet_record:
                    meet_record.meeting_time_end = current_time_str
                    meet_record.remarks = 'Meeting to Hold'
                    db.commit()
                    print(f"Updated meeting_time_end for Meeting record to: {meet_record.meeting_time_end}")

                # # Create a new End Of Day record
                # end_of_day_record = models.END_OF_DAY(
                #     Service_ID=tl_record.Service_ID,
                #     user_id=userid,
                #     end_time_start=current_time_str,
                #     remarks="Meeting to EOD"
                # )
                # db.add(end_of_day_record)
                hold_entry =models.HOLD(
                    Service_ID=tl_record.Service_ID,
                    user_id=userid,
                    hold_time_start=current_time_str,
                    remarks="Meeting to Hold"
                )
                db.add(hold_entry)
                db.commit()
                print("New Hold record created.")  


            elif check_status == "Login" and tl_record.work_status == "Clarification Call":  
                #  Change the TL status to End Of Day
                tl_record.work_status = "Hold"
                db.commit()
                print("Updated Call in TL table to Hold.")

                # new_session = models.WorkSession(user_id=userid, start_time=current_time_str)
                # db.add(new_session)
                # db.commit()
                # print("New session created due to Clarification Call login.")

                # Update the previous Meet record
                call_record = db.query(models.CALL).filter(
                    models.CALL.user_id == userid,
                    models.CALL.call_time_end == ""
                ).first()

                if call_record:
                    call_record.call_time_end = current_time_str
                    call_record.remarks = 'Call to Hold'
                    db.commit()
                    print(f"Updated call_time_end for Call record to: {call_record.call_time_end}")

                # Create a new End Of Day record
                # end_of_day_record = models.END_OF_DAY(
                #     Service_ID=tl_record.Service_ID,
                #     user_id=userid,
                #     end_time_start=current_time_str,
                #     remarks="Call to EOD"
                # )
                hold_entry =models.HOLD(
                    Service_ID=tl_record.Service_ID,
                    user_id=userid,
                    hold_time_start=current_time_str,
                    remarks="Call to Hold"
                )
                db.add(hold_entry)
                db.commit()
                print("New Hold record created.")

            
            # elif tl_record.work_status == "End Of Day":  
            #     print("---------======EOD----------------------")
            #     new_session = models.WorkSession(user_id=userid, start_time=current_time_str)
            #     db.add(new_session)
            #     db.commit()
            #     print("New session created due to Login to End Of Day.")    
                
                


            
    if not new_session_created:
        # If all TL records are End Of Day, create a new session
        if tl_records and all(tl_record.work_status == "End Of Day" for tl_record in tl_records):
            if work_session and work_session.end_time == "":
                work_session.end_time = current_time_str
                db.commit()
                print(f"Updated end_time of previous session to: {work_session.end_time}")

                start_time = datetime.strptime(work_session.start_time, "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(work_session.end_time, "%Y-%m-%d %H:%M:%S")
                total_time = end_time - start_time

                work_session.total_time_worked = str(total_time)
                db.commit()
    
            # new_session = models.WorkSession(user_id=userid, start_time=current_time_str)
            # db.add(new_session)
            # db.commit()
            # print("New session created due to Login to End Of Day.")

        # Handle other statuses (if necessary)
        elif check_status in ["Login", "Hold", "Completed"]:
            if work_session and (work_session.end_time is None or work_session.end_time == ""):
                work_session.end_time = current_time_str
                db.commit()
                print("Active session exists, new session created.")

                # Calculate total_time_worked after updating end_time
                start_time = datetime.strptime(work_session.start_time, "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(work_session.end_time, "%Y-%m-%d %H:%M:%S")
                total_time = end_time - start_time

                work_session.total_time_worked = str(total_time)
                db.commit()

            new_session = models.WorkSession(user_id=userid, start_time=current_time_str)
            db.add(new_session)
            db.commit()
            print("New session created.")

            # Handle Work in Progress
        elif check_status == "Work in Progress":
            print("Handling Work in Progress")
            if work_session and (work_session.end_time is None or work_session.end_time == ""):
                # If the session has no end_time, set it to the current time
                work_session.end_time = current_time_str
                db.commit()

                # Calculate total_time_worked after updating end_time
                start_time = datetime.strptime(work_session.start_time, "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(work_session.end_time, "%Y-%m-%d %H:%M:%S")
                total_time = end_time - start_time

                # Store the total time worked
                work_session.total_time_worked = str(total_time)
                db.commit()
                print(f"Updated end_time to: {work_session.end_time}")
                print(f"Total time worked: {work_session.total_time_worked}")
            else:
                print("No active session found or session already closed.")
            # else:
            #     new_session = models.WorkSession(user_id=userid, start_time=current_time_str)
            #     db.add(new_session)
            #     db.commit()
            #     print(f"End time already populated. New session created for user ID: {userid}.")
            return userid

        # Handle Logout or Completed
        elif check_status == "Logout":
            print("Handling LOGOUT")
            if work_session and (work_session.end_time is None or work_session.end_time == ""):
                # If a session is active, finalize it by setting end_time
                work_session.end_time = current_time_str
                db.commit()

                # Calculate total_time_worked after updating end_time
                start_time = datetime.strptime(work_session.start_time, "%Y-%m-%d %H:%M:%S")
                end_time = datetime.strptime(work_session.end_time, "%Y-%m-%d %H:%M:%S")
                total_time = end_time - start_time

                # Store the total time worked
                work_session.total_time_worked = str(total_time)
                db.commit()
                print(f"Session completed, total time worked: {work_session.total_time_worked}")

            return userid

        
        # Handle End of Day
    if check_status == "End Of Day":
        print("Handling eOD")
        if work_session and (work_session.end_time is None or work_session.end_time == ""):
            work_session.end_time = current_time_str

            start_time = datetime.strptime(work_session.start_time, "%Y-%m-%d %H:%M:%S")
            end_time = datetime.strptime(work_session.end_time, "%Y-%m-%d %H:%M:%S")
            total_time = end_time - start_time

            work_session.total_time_worked = str(total_time)
            db.commit()
            print(f"EOD processed. Updated session ID: {work_session.id}, total time worked: {work_session.total_time_worked}")
        else:
            new_session = models.WorkSession(user_id=userid, start_time=current_time_str)
            db.add(new_session)
            db.commit()
            print(f"End time already populated. New session created for user ID: {userid}.")

        return userid



def add_ideal_time(data_list: List[Dict], dict2: Dict[str, str]) -> List[Dict]:
    # Iterate over each dictionary in the list
    for data in data_list:
        # Extract the user from the current dictionary
        user = next(iter(data['user']), None)
        if user and user in dict2:
            # Add 'idealtime' to the dictionary if the user exists in dict2
            data['idealtime'] = dict2[user]
    
    return data_list



def format_timedelta(td: timedelta) -> str:
    """Convert timedelta to a string in the format H:MM:SS."""
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes:02}:{seconds:02}"


ist = pytz.timezone('Asia/Kolkata')

def calculate_total_time_for_all_users(
    picked_date: str,
    to_date: str,
    db: Session
) -> dict:
    # Parse the dates from the form assuming the format 'YYYY-MM-DD'
    picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
    to_datett = datetime.strptime(to_date, "%Y-%m-%d")

    # If time is not provided, assume start time is 00:00:00 and end time is 23:59:59
    picked_date_start = picked_datett.replace(hour=0, minute=0, second=0)
    to_date_end = to_datett.replace(hour=23, minute=59, second=59)

    # Fetch all work sessions between the specified dates
    sessions = db.query(models.WorkSession).filter(
        models.WorkSession.start_time >= picked_date_start.strftime("%Y-%m-%d %H:%M:%S"),
        models.WorkSession.start_time <= to_date_end.strftime("%Y-%m-%d %H:%M:%S")  # Ensure we only consider sessions within the range
    ).all()

    # Dictionary to hold total time for each user
    user_total_time = defaultdict(timedelta)

    # Calculate the total time worked for each user
    for session in sessions:
        if session.start_time:
            start_time = datetime.strptime(session.start_time, "%Y-%m-%d %H:%M:%S")
            
            # Check if end_time is provided
            if session.end_time:
                end_time = datetime.strptime(session.end_time, "%Y-%m-%d %H:%M:%S")
                # Only calculate total time if both start and end times are present
                user_total_time[session._user_table1.username] += (end_time - start_time)

            else:
                # Handle ongoing sessions based on their start date
                if start_time.date() == datetime.now().date():
                    # Use current time as end time for today's ongoing sessions
                    end_time = datetime.now()
                    user_total_time[session._user_table1.username] += (end_time - start_time)
                elif start_time.date() < datetime.now().date():
                    # Skip past ongoing sessions as they should not be counted
                    continue

    # Format the output
    formatted_output = {}
    for user, total_time in user_total_time.items():
        # Format total_time using the custom function
        formatted_output[user] = format_timedelta(total_time)

    
    updated_data_list = add_ideal_time(totalfivereports(db, picked_date, to_date, 'userlist'), formatted_output)

    # Print the updated data list
    for item in updated_data_list:
        # print(item)
        break_time = parse_time(next(iter(item.get('break', ['0:0:0'])), '0:0:0'))
        in_progress_time = parse_time(next(iter(item.get('in_progress', ['0:0:0'])), '0:0:0'))
        call_time = parse_time(next(iter(item.get('call', ['0:0:0'])), '0:0:0'))
        meeting_time = parse_time(next(iter(item.get('meeting', ['0:0:0'])), '0:0:0'))
        completed_time = parse_time(next(iter(item.get('completed', ['0:0:0'])), '0:0:0'))

        # Handle ideal_time whether it's a list or set
        ideal_time_value = item.get('idealtime', '0:0:0')
        if isinstance(ideal_time_value, list):
            ideal_time_value = ideal_time_value[0] if ideal_time_value else '0:0:0'
        elif isinstance(ideal_time_value, set):
            ideal_time_value = next(iter(ideal_time_value), '0:0:0')

        ideal_time = parse_time(ideal_time_value)

        # Sum the times
        total_time_taken = break_time + in_progress_time + call_time + meeting_time + completed_time + ideal_time
        item['total_time_taken'] = str(total_time_taken)

    
    return updated_data_list

def parse_time(time_str: str) -> timedelta:
    """Helper function to parse time strings into timedelta objects."""
    hours, minutes, seconds = map(int, time_str.split(':'))
    return timedelta(hours=hours, minutes=minutes, seconds=seconds)

# --------------------------------------------------------------IDEAL TIME CODE END


# ---------------------------------logout status change to Hold- new function.............start
def get_current_time_str_login() -> str:
    """Get the current time as a string formatted for database storage with timezone."""
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now(ist)
    return current_time.strftime('%Y-%m-%d %H:%M:%S')

def get_current_time_str() -> str:
    """Get the current time as a string formatted for database storage without timezone."""
    ist = pytz.timezone('Asia/Kolkata')
    current_time = datetime.now()
    return current_time.strftime('%Y-%m-%d %H:%M:%S')

def get_current_time_str_with_offset(seconds: int) -> str:
    """Get the current time plus an offset in seconds as a string formatted for database storage."""
    current_time = datetime.now() + timedelta(seconds=seconds)
    return current_time.strftime('%Y-%m-%d %H:%M:%S')

def is_work_in_progress(db: Session, user_id: int) -> bool:
    """Check if work is in progress or on break for a given user with a valid Service_ID."""
    tl_entry = db.query(models.TL).filter(
        models.TL.Assigned_To == user_id,
        models.TL.work_status.in_(["Work in Progress", "Break","Clarification Call","Meeting","Hold","End Of Day","Not Picked"]),
    ).order_by(models.TL.Service_ID).all()
    return tl_entry is not None


def calculate_total_times(start_time_str: str, end_time_str: str) -> str:
    """Calculate the total time worked between start and end times."""
    try:
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")

        total_time_seconds = end_time - start_time
        hours, remainder = divmod(total_time_seconds.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_total_time = f"{int(hours)}:{int(minutes):02}:{int(seconds):02}"

        return formatted_total_time

    except Exception as e:
        logging.error(f"Error calculating total time: {e}")
        return '0:00:00'
    
# def logout_time_add(logouttime: str, userid: int, db: Session):
#     print("innnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnnn")
#     print(logouttime)
#     print(userid)
#     all_records = db.query(models.TL).filter(
#         models.TL.Assigned_To == userid,
#         models.TL.work_status.in_(["Break", "Work in Progress", "Clarification Call", "Meeting", "Hold", "End Of Day", "Not Picked"])
#     ).all()

#     print("Fetched records:", all_records)
    
#     # try:
#     if 1==1:
#         # Step 1: Check if there is a login entry with no logout_time
#         login_entry = db.query(models.login_time).filter(
#             models.login_time.userid == userid
#         ).order_by(models.login_time.login_id.desc()).first()
#         print((login_entry and not login_entry.logout_time))
#         if login_entry and not login_entry.logout_time:
#             logging.info(f"Login entry found for user {userid}, login_id: {login_entry.login_id}")
            
#             # Step 2: Check the TL table for the work status by Assigned_To (user_id)
#             tl_entry = db.query(models.TL).filter(
#                 models.TL.Assigned_To == userid
#             ).order_by(models.TL.Service_ID.desc()).first()
#             print(tl_entry,'bharath ku............................')
#             if tl_entry:
#                 print(f"TL entry found for user {userid}, Service_ID: {tl_entry.Service_ID}")
#                 logging.info(f"TL entry found for user {userid}, Service_ID: {tl_entry.Service_ID}")

#                 # Log current work status before updating
#                 logging.info(f"Current work status for TL entry: {tl_entry.work_status}")

#                 if tl_entry.work_status == "Work in Progress":
#                     logging.info(f"Work status is 'Work in Progress' for user {userid}")

#                     # Step 3: Change the work status from "Work in Progress" to "Hold"
#                     tl_entry.work_status = "Hold"
                    
#                     # Log the updated work status
#                     logging.info(f"Updated work status for TL entry: {tl_entry.work_status}")

#                     # Commit the change to the work status
#                     db.commit()
#                     logging.info(f"Work status changed to 'Hold' for Service_ID: {tl_entry.Service_ID}")
                    
                   
#                     hold_entry = models.HOLD(
#                         Service_ID=tl_entry.Service_ID,
#                         user_id=userid,
#                         hold_time_start=get_current_time_str(),
#                         remarks="Work put on Hold"
#                     )
#                     db.add(hold_entry)
#                     db.commit()
#                     logging.info(f"Hold entry created for Service_ID: {tl_entry.Service_ID}")

#                     # Step 5: Add a new record in the WorkSession table with the start time as the current time
#                     work_session = models.WorkSession(
#                         user_id=userid,
#                         start_time=get_current_time_str()
#                     )
#                     db.add(work_session)
#                     db.commit()
#                     logging.info(f"WorkSession created for user {userid}")

#                     # Step 6: Update logout_time in the login_time table with the current time
#                     login_entry.logout_time = logouttime
#                     db.commit()
#                     logging.info(f"Logout time updated for user {userid}")

#                     # Step 7: Update the end_time in the WorkSession table if the last record has an empty end_time
#                     last_work_session = db.query(models.WorkSession).filter(
#                         models.WorkSession.user_id == userid,
#                         models.WorkSession.end_time=='',
#                     ).order_by(models.WorkSession.id.desc()).first()

#                     if last_work_session:
#                         end_time_str = get_current_time_str_with_offset(2)
#                         last_work_session.end_time = end_time_str
#                         db.commit()
#                         logging.info(f"End time updated for WorkSession for user {userid}")

#                         # Step 8: Calculate the total working time (end_time - start_time)
#                         total_worked_time = calculate_total_times(last_work_session.start_time, last_work_session.end_time)
#                         last_work_session.total_time_worked = total_worked_time
#                         db.commit()
#                         logging.info(f"Total working time updated for WorkSession for user {userid}")
#                     else:
#                         logging.warning(f"No open WorkSession found for user {userid}")
                
#                 elif tl_entry.work_status == "Hold": 
#                     login_entry = db.query(models.login_time).filter(
#                     models.login_time.userid == userid,
#                     models.login_time.logout_time == ''
#                     ).order_by(models.login_time.login_id.desc()).first()

#                     if login_entry:
#                         login_entry.logout_time = logouttime
#                         db.commit()
#                         logging.info(f"Login end time updated for user {userid}")
#                     else:
#                         logging.error(f"No active login session found for user {userid}")

#                         last_work_session = db.query(models.WorkSession).filter(
#                         models.WorkSession.user_id == userid,
#                         models.WorkSession.end_time == ''
#                         ).order_by(models.WorkSession.id.desc()).first()
                
#                 elif tl_entry.work_status == "End Of Day": 
#                     login_entry = db.query(models.login_time).filter(
#                     models.login_time.userid == userid,
#                     models.login_time.logout_time == ''
#                     ).order_by(models.login_time.login_id.desc()).first()

#                     if login_entry:
#                         login_entry.logout_time = logouttime
#                         db.commit()
#                         logging.info(f"Login end time updated for user {userid}")
#                     else:
#                         logging.error(f"No active login session found for user {userid}")

#                         last_work_session = db.query(models.WorkSession).filter(
#                         models.WorkSession.user_id == userid,
#                         models.WorkSession.end_time == ''
#                         ).order_by(models.WorkSession.id.desc()).first()

#                 elif tl_entry.work_status == "Completed": 
#                     login_entry = db.query(models.login_time).filter(
#                     models.login_time.userid == userid,
#                     models.login_time.logout_time == ''
#                     ).order_by(models.login_time.login_id.desc()).first()

#                     if login_entry:
#                         login_entry.logout_time = logouttime
#                         db.commit()
#                         logging.info(f"Login end time updated for user {userid}")
#                     else:
#                         logging.error(f"No active login session found for user {userid}")

#                         last_work_session = db.query(models.WorkSession).filter(
#                         models.WorkSession.user_id == userid,
#                         models.WorkSession.end_time == ''
#                         ).order_by(models.WorkSession.id.desc()).first()
                        
#                 elif tl_entry.work_status == "Break":
#                     print(f"Work status is 'Break' for user {userid}")
#                     logging.info(f"Work status is 'Break' for user {userid}")

#                     # Step 2: Change the work status from "Work in Progress" to "Hold"
#                     tl_entry.work_status = "Hold"
#                     db.commit()
#                     logging.info(f"Work status changed to 'EOD' for Service_ID: {tl_entry.Service_ID}")
                    
                  
#                     hold_entry = models.HOLD(
#                         Service_ID=tl_entry.Service_ID,
#                         user_id=userid,
#                         hold_time_start=get_current_time_str(),
#                         remarks="Break put on Hold"
#                     )
#                     db.add(hold_entry)
#                     db.commit()
#                     logging.info(f"EOD entry created for Service_ID: {tl_entry.Service_ID}")

#                     # End the break with the current time
#                     last_break_entry = db.query(models.BREAK).filter(
#                         models.BREAK.user_id == userid
#                         ).order_by(models.BREAK.id.desc()).first()

#                     if last_break_entry and last_break_entry.break_time_end == '':
#                         last_break_entry.break_time_end = get_current_time_str()
#                         last_break_entry.remarks = "Break to Hold"
#                         db.commit()
#                         logging.info(f"Break end time updated to {last_break_entry.break_time_end} for user {userid}")

#                     # Step 4: Add a new record in the WorkSession table with the start time as the current time
#                     work_session = models.WorkSession(
#                         user_id=userid,
#                         start_time=get_current_time_str()
#                         )
#                     db.add(work_session)
#                     db.commit()
#                     logging.info(f"WorkSession created for user {userid}")

#                     # Step 5: Update logout_time in the login_time table with the current time
#                     login_entry.logout_time = logouttime
#                     db.commit()
#                     logging.info(f"Logout time updated for user {userid}")

#                     # Step 6: Update the end_time in the WorkSession table if the last record has an empty end_time
#                     last_work_session = db.query(models.WorkSession).filter(
#                         models.WorkSession.user_id == userid,
#                         models.WorkSession.end_time=='',  # Changed from empty string to None check
#                         ).order_by(models.WorkSession.id.desc()).first()

#                     if last_work_session:
#                         end_time_str = get_current_time_str_with_offset(2)
#                         last_work_session.end_time = end_time_str
#                         db.commit()
#                         logging.info(f"End time updated for WorkSession for user {userid}")

#                         # Step 7: Calculate the total working time (end_time - start_time)
#                         total_worked_time = calculate_total_times(last_work_session.start_time, last_work_session.end_time)
#                         last_work_session.total_time_worked = total_worked_time
#                         db.commit()
#                         logging.info(f"Total working time updated for WorkSession for user {userid}") 
                
#                 elif tl_entry.work_status == "Clarification Call":
#                     logging.info(f"Work status is 'Clarification Call' for user {userid}")

#                     # Step 2: Change the work status from "Work in Progress" to "Hold"
#                     tl_entry.work_status = "Hold"
#                     db.commit()
#                     logging.info(f"Work status changed to 'End Of Day' for Service_ID: {tl_entry.Service_ID}")
                    
                   
#                     hold_entry = models.HOLD(
#                         Service_ID=tl_entry.Service_ID,
#                         user_id=userid,
#                         hold_time_start=get_current_time_str(),
#                         remarks="Call put on Hold"
#                     )
#                     db.add(hold_entry)
#                     db.commit()
#                     logging.info(f"End Of Day entry created for Service_ID: {tl_entry.Service_ID}")

#                     # End the break with the current time
#                     last_call_entry = db.query(models.CALL).filter(
#                         models.CALL.user_id == userid
#                         ).order_by(models.CALL.id.desc()).first()

#                     if last_call_entry and last_call_entry.call_time_end == '':
#                         last_call_entry.call_time_end = get_current_time_str()
#                         last_call_entry.remarks = "Call to Hold"
#                         db.commit()
#                         logging.info(f"Call end time updated to {last_call_entry.call_time_end} for user {userid}")

#                     # Step 4: Add a new record in the WorkSession table with the start time as the current time
#                     work_session = models.WorkSession(
#                         user_id=userid,
#                         start_time=get_current_time_str()
#                         )
#                     db.add(work_session)
#                     db.commit()
#                     logging.info(f"WorkSession created for user {userid}")

#                     # Step 5: Update logout_time in the login_time table with the current time
#                     login_entry.logout_time = logouttime
#                     db.commit()
#                     logging.info(f"Logout time updated for user {userid}")

#                     # Step 6: Update the end_time in the WorkSession table if the last record has an empty end_time
#                     last_work_session = db.query(models.WorkSession).filter(
#                         models.WorkSession.user_id == userid,
#                         models.WorkSession.end_time.is_(None)  # Changed from empty string to None check
#                         ).order_by(models.WorkSession.id.desc()).first()

#                     if last_work_session:
#                         end_time_str = get_current_time_str_with_offset(2)
#                         last_work_session.end_time = end_time_str
#                         db.commit()
#                         logging.info(f"End time updated for WorkSession for user {userid}")

#                         # Step 7: Calculate the total working time (end_time - start_time)
#                         total_worked_time = calculate_total_times(last_work_session.start_time, last_work_session.end_time)
#                         last_work_session.total_time_worked = total_worked_time
#                         db.commit()
#                         logging.info(f"Total working time updated for WorkSession for user {userid}")

         
#                 elif tl_entry.work_status == "Meeting":
#                         logging.info(f"Work status is 'Meeting' for user {userid}")

#                         # Step 2: Change the work status from "Work in Progress" to "Hold"
#                         tl_entry.work_status = "Hold"
#                         db.commit()
#                         logging.info(f"Work status changed to 'Hold' for Service_ID: {tl_entry.Service_ID}")
                        
                       
#                         hold_entry = models.HOLD(
#                             Service_ID=tl_entry.Service_ID,
#                             user_id=userid,
#                             hold_time_start=get_current_time_str(),
#                             remarks="Meeting put on Hold"
#                         )
#                         db.add(hold_entry)
#                         db.commit()
#                         logging.info(f"Meeting entry created for Service_ID: {tl_entry.Service_ID}")

#                         # End the break with the current time
#                         last_meet_entry = db.query(models.MEETING).filter(
#                             models.MEETING.user_id == userid
#                             ).order_by(models.MEETING.id.desc()).first()

#                         if last_meet_entry and last_meet_entry.meeting_time_end == '':
#                             last_meet_entry.meeting_time_end = get_current_time_str()
#                             last_meet_entry.remarks = "Meeting to Hold"
#                             db.commit()
#                             logging.info(f"Meeting end time updated to {last_meet_entry.meeting_time_end} for user {userid}")

#                         # Step 4: Add a new record in the WorkSession table with the start time as the current time
#                         work_session = models.WorkSession(
#                             user_id=userid,
#                             start_time=get_current_time_str()
#                             )
#                         db.add(work_session)
#                         db.commit()
#                         logging.info(f"WorkSession created for user {userid}")

#                         # Step 5: Update logout_time in the login_time table with the current time
#                         login_entry.logout_time = logouttime
#                         db.commit()
#                         logging.info(f"Logout time updated for user {userid}")

#                         # Step 6: Update the end_time in the WorkSession table if the last record has an empty end_time
#                         last_work_session = db.query(models.WorkSession).filter(
#                             models.WorkSession.user_id == userid,
#                             models.WorkSession.end_time.is_(None)  # Changed from empty string to None check
#                             ).order_by(models.WorkSession.id.desc()).first()

#                         if last_work_session:
#                             end_time_str = get_current_time_str_with_offset(2)
#                             last_work_session.end_time = end_time_str
#                             db.commit()
#                             logging.info(f"End time updated for WorkSession for user {userid}")

#                             # Step 7: Calculate the total working time (end_time - start_time)
#                             total_worked_time = calculate_total_times(last_work_session.start_time, last_work_session.end_time)
#                             last_work_session.total_time_worked = total_worked_time
#                             db.commit()
#                             logging.info(f"Total working time updated for WorkSession for user {userid}")

#                 elif tl_entry.work_status == "Not Picked": 
#                     login_entry = db.query(models.login_time).filter(
#                     models.login_time.userid == userid,
#                     models.login_time.logout_time == ''
#                     ).order_by(models.login_time.login_id.desc()).first()

#                     if login_entry:
#                         login_entry.logout_time = logouttime
#                         db.commit()
#                         logging.info(f"Login end time updated for user {userid}")
#                     else:
#                         logging.error(f"No active login session found for user {userid}")

#                         last_work_session = db.query(models.WorkSession).filter(
#                         models.WorkSession.user_id == userid,
#                         models.WorkSession.end_time == ''
#                         ).order_by(models.WorkSession.id.desc()).first()

#                     if last_work_session:
#                         end_time_str = get_current_time_str_with_offset(2)
#                         last_work_session.end_time = end_time_str
#                         db.commit()
#                         logging.info(f"WorkSession end time updated to {end_time_str} for user {userid}")

#                         if last_work_session.start_time and last_work_session.end_time:
#                             formatted_total_time = calculate_total_times(last_work_session.start_time, last_work_session.end_time)
#                             last_work_session.total_time_worked = formatted_total_time
#                             db.commit()
#                             logging.info(f"Total working time calculated for user {userid}: {formatted_total_time}")
#                         else:
#                             logging.error(f"Cannot calculate total time for user {userid} due to missing start_time or end_time.")
#                     else:
#                         logging.error(f"No active WorkSession found with empty end_time for user {userid}.")
#         return "Success"

# ------------new logout function for Hold------------------
import logging
from sqlalchemy.orm import Session

def logout_time_add(logouttime: str, userid: int, db: Session):

    # Log the user ID being processed
    logging.info(f"Fetching records for user ID: {userid}")

    # Fetch all records with specified work statuses
    all_records = db.query(models.TL).filter(
        models.TL.Assigned_To == userid,
        models.TL.work_status.in_(["Break", "Work in Progress", "Clarification Call", "Meeting","End Of Day","Hold", "Not Picked"])
    ).order_by(models.TL.Service_ID).all()

    # Log the fetched records for debugging
    logging.info(f"Fetched records: {[record.work_status for record in all_records]}")

    try:
        # Get the latest login entry for the user
        login_entry = db.query(models.login_time).filter(models.login_time.userid == userid).order_by(models.login_time.login_id.desc()).first()
        
        if login_entry and not login_entry.logout_time:
            logging.info(f"Login entry found for user {userid}, login_id: {login_entry.login_id}")
            
            # Check if any work status is "Work in Progress"
            if any(record.work_status == "Work in Progress" for record in all_records):
                # Find the TL entry for the user
                tl_entry = next(record for record in all_records if record.work_status == "Work in Progress")

                logging.info(f"TL entry found for user {userid}, Service_ID: {tl_entry.Service_ID}")

                # Change the work status from "Work in Progress" to "Hold"
                tl_entry.work_status = "Hold"
                db.commit()
                logging.info(f"Work status changed to 'Hold' for Service_ID: {tl_entry.Service_ID}")
                
                # Step 3: Add a new record in the HOLD table with the start time as the current time
                hold_entry = models.HOLD(
                    Service_ID=tl_entry.Service_ID,
                    user_id=userid,
                    hold_time_start=get_current_time_str(),
                    remarks="Work put on hold"
                )
                db.add(hold_entry)
                db.commit()
                logging.info(f"Hold entry created for Service_ID: {tl_entry.Service_ID}")

                # Step 4: Add a new record in the WorkSession table with the start time as the current time
                work_session = models.WorkSession(
                    user_id=userid,
                    start_time=get_current_time_str()
                )
                db.add(work_session)
                db.commit()
                logging.info(f"WorkSession created for user {userid}")

                # Step 5: Update logout_time in the login_time table with the current time
                login_entry.logout_time = logouttime
                db.commit()
                logging.info(f"Logout time updated for user {userid}")

                # Step 6: Update the end_time in the WorkSession table if the last record has an empty end_time
                last_work_session = db.query(models.WorkSession).filter(
                    models.WorkSession.user_id == userid,
                    models.WorkSession.end_time.is_(None)  # Changed from empty string to None check
                ).order_by(models.WorkSession.id.desc()).first()

                if last_work_session:
                    end_time_str = get_current_time_str_with_offset(2)
                    last_work_session.end_time = end_time_str
                    db.commit()
                    logging.info(f"End time updated for WorkSession for user {userid}")

                    # Step 7: Calculate the total working time (end_time - start_time)
                    total_worked_time = calculate_total_times(last_work_session.start_time, last_work_session.end_time)
                    last_work_session.total_time_worked = total_worked_time
                    db.commit()
                    logging.info(f"Total working time updated for WorkSession for user {userid}")

            elif any(record.work_status == "Break" for record in all_records):
                # Find the TL entry for the user with a "Break" status
                tl_entry = next(record for record in all_records if record.work_status == "Break")

                logging.info(f"TL entry found for user {userid}, Service_ID: {tl_entry.Service_ID}")

                # Step 1: Change the work status from "Break" to "Hold"
                tl_entry.work_status = "Hold"
                db.commit()
                logging.info(f"Work status changed to 'Hold' for Service_ID: {tl_entry.Service_ID}")

                # Step 2: Add a new record in the HOLD table with the start time as the current time
                hold_entry = models.HOLD(
                    Service_ID=tl_entry.Service_ID,
                    user_id=userid,
                    hold_time_start=get_current_time_str(),
                    remarks="Break put on Hold"
                )
                db.add(hold_entry)
                db.commit()
                logging.info(f"Hold entry created for Service_ID: {tl_entry.Service_ID}")

                # Step 3: End the break with the current time
                last_break_entry = db.query(models.BREAK).filter(
                    models.BREAK.user_id == userid
                ).order_by(models.BREAK.id.desc()).first()

                if last_break_entry and last_break_entry.break_time_end == '':
                    last_break_entry.break_time_end = get_current_time_str()
                    last_break_entry.remarks = "Break to Hold"
                    db.commit()
                    logging.info(f"Break end time updated to {last_break_entry.break_time_end} for user {userid}")

                # Step 4: Add a new record in the WorkSession table with the start time as the current time
                work_session = models.WorkSession(
                    user_id=userid,
                    start_time=get_current_time_str()
                )
                db.add(work_session)
                db.commit()
                logging.info(f"WorkSession created for user {userid}")

                # Step 5: Update logout_time in the login_time table with the current time
                login_entry.logout_time = logouttime
                db.commit()
                logging.info(f"Logout time updated for user {userid}")

                # Step 6: Update the end_time in the WorkSession table if the last record has an empty end_time
                last_work_session = db.query(models.WorkSession).filter(
                    models.WorkSession.user_id == userid,
                    models.WorkSession.end_time.is_(None)  # Check for None instead of empty string
                ).order_by(models.WorkSession.id.desc()).first()

                if last_work_session:
                    end_time_str = get_current_time_str_with_offset(2)
                    last_work_session.end_time = end_time_str
                    db.commit()
                    logging.info(f"End time updated for WorkSession for user {userid}")

                    # Step 7: Calculate the total working time (end_time - start_time)
                    total_worked_time = calculate_total_times(last_work_session.start_time, last_work_session.end_time)
                    last_work_session.total_time_worked = total_worked_time
                    db.commit()
                    logging.info(f"Total working time updated for WorkSession for user {userid}")

            elif any(record.work_status == "Meeting" for record in all_records):
                # Find the TL entry for the user with a "Meeting" status
                tl_entry = next(record for record in all_records if record.work_status == "Meeting")

                logging.info(f"TL entry found for user {userid}, Service_ID: {tl_entry.Service_ID}")

                # Step 1: Change the work status from "Meeting" to "Hold"
                tl_entry.work_status = "Hold"
                db.commit()
                logging.info(f"Work status changed to 'Hold' for Service_ID: {tl_entry.Service_ID}")

                # Step 2: Add a new record in the HOLD table with the start time as the current time
                hold_entry = models.HOLD(
                    Service_ID=tl_entry.Service_ID,
                    user_id=userid,
                    hold_time_start=get_current_time_str(),
                    remarks="Meeting put on Hold"
                )
                db.add(hold_entry)
                db.commit()
                logging.info(f"Hold entry created for Service_ID: {tl_entry.Service_ID}")

                # Step 3: End the break with the current time
                last_meet_entry = db.query(models.MEETING).filter(
                    models.MEETING.user_id == userid
                ).order_by(models.MEETING.id.desc()).first()

                if last_meet_entry and last_meet_entry.meeting_time_end == '':
                    last_meet_entry.meeting_time_end = get_current_time_str()
                    last_meet_entry.remarks = "Meeting to Hold"
                    db.commit()
                    logging.info(f"Meet end time updated to {last_meet_entry.meeting_time_end} for user {userid}")

                # Step 4: Add a new record in the WorkSession table with the start time as the current time
                work_session = models.WorkSession(
                    user_id=userid,
                    start_time=get_current_time_str()
                )
                db.add(work_session)
                db.commit()
                logging.info(f"WorkSession created for user {userid}")

                # Step 5: Update logout_time in the login_time table with the current time
                login_entry.logout_time = logouttime
                db.commit()
                logging.info(f"Logout time updated for user {userid}")

                # Step 6: Update the end_time in the WorkSession table if the last record has an empty end_time
                last_work_session = db.query(models.WorkSession).filter(
                    models.WorkSession.user_id == userid,
                    models.WorkSession.end_time.is_(None)  # Check for None instead of empty string
                ).order_by(models.WorkSession.id.desc()).first()

                if last_work_session:
                    end_time_str = get_current_time_str_with_offset(2)
                    last_work_session.end_time = end_time_str
                    db.commit()
                    logging.info(f"End time updated for WorkSession for user {userid}")

                    # Step 7: Calculate the total working time (end_time - start_time)
                    total_worked_time = calculate_total_times(last_work_session.start_time, last_work_session.end_time)
                    last_work_session.total_time_worked = total_worked_time
                    db.commit()
                    logging.info(f"Total working time updated for WorkSession for user {userid}")

            elif any(record.work_status == "Clarification Call" for record in all_records):
                # Find the TL entry for the user with a "Meeting" status
                tl_entry = next(record for record in all_records if record.work_status == "Clarification Call")

                logging.info(f"TL entry found for user {userid}, Service_ID: {tl_entry.Service_ID}")

                # Step 1: Change the work status from "Clarification Call" to "Hold"
                tl_entry.work_status = "Hold"
                db.commit()
                logging.info(f"Work status changed to 'Hold' for Service_ID: {tl_entry.Service_ID}")

                # Step 2: Add a new record in the HOLD table with the start time as the current time
                hold_entry = models.HOLD(
                    Service_ID=tl_entry.Service_ID,
                    user_id=userid,
                    hold_time_start=get_current_time_str(),
                    remarks="Call put on Hold"
                )
                db.add(hold_entry)
                db.commit()
                logging.info(f"Hold entry created for Service_ID: {tl_entry.Service_ID}")

                # Step 3: End the break with the current time
                last_meet_entry = db.query(models.CALL).filter(
                    models.CALL.user_id == userid
                ).order_by(models.CALL.id.desc()).first()

                if last_meet_entry and last_meet_entry.call_time_end == '':
                    last_meet_entry.call_time_end = get_current_time_str()
                    last_meet_entry.remarks = "Call to Hold"
                    db.commit()
                    logging.info(f"Clarification Call end time updated to {last_meet_entry.call_time_end} for user {userid}")

                # Step 4: Add a new record in the WorkSession table with the start time as the current time
                work_session = models.WorkSession(
                    user_id=userid,
                    start_time=get_current_time_str()
                )
                db.add(work_session)
                db.commit()
                logging.info(f"WorkSession created for user {userid}")

                # Step 5: Update logout_time in the login_time table with the current time
                login_entry.logout_time = logouttime
                db.commit()
                logging.info(f"Logout time updated for user {userid}")

                # Step 6: Update the end_time in the WorkSession table if the last record has an empty end_time
                last_work_session = db.query(models.WorkSession).filter(
                    models.WorkSession.user_id == userid,
                    models.WorkSession.end_time.is_(None)  # Check for None instead of empty string
                ).order_by(models.WorkSession.id.desc()).first()

                if last_work_session:
                    end_time_str = get_current_time_str_with_offset(2)
                    last_work_session.end_time = end_time_str
                    db.commit()
                    logging.info(f"End time updated for WorkSession for user {userid}")

                    # Step 7: Calculate the total working time (end_time - start_time)
                    total_worked_time = calculate_total_times(last_work_session.start_time, last_work_session.end_time)
                    last_work_session.total_time_worked = total_worked_time
                    db.commit()
                    logging.info(f"Total working time updated for WorkSession for user {userid}")

            # elif any(record.work_status == "End Of Day" for record in all_records):
            #     # Find the TL entry for the user with an "End Of Day" status
            #     tl_entry = next(record for record in all_records if record.work_status == "End Of Day")

            #     logging.info(f"TL entry found for user {userid}, Service_ID: {tl_entry.Service_ID}")

                  
               
            #     # Handle the last work session if it has an empty end_time
            #     last_work_session = db.query(models.WorkSession).filter(
            #         models.WorkSession.user_id == userid,
            #         models.WorkSession.end_time.is_(None)  # Check for None instead of empty string
            #     ).order_by(models.WorkSession.id.desc()).first()

            #     if last_work_session:
            #         end_time_str = get_current_time_str_with_offset(2)  # Adjust end time if necessary
            #         last_work_session.end_time = end_time_str
            #         db.commit()
            #         logging.info(f"End time updated for WorkSession for user {userid}")

            #         # Calculate the total working time (end_time - start_time)
            #         total_worked_time = calculate_total_times(last_work_session.start_time, last_work_session.end_time)
            #         last_work_session.total_time_worked = total_worked_time
            #         db.commit()
            #         logging.info(f"Total working time updated for WorkSession for user {userid}")
                
            #     # Check for an active login session for the user
            #     login_entry = db.query(models.login_time).filter(
            #         models.login_time.userid == userid,
            #         models.WorkSession.end_time == ''  # Check for None instead of empty string
            #     ).order_by(models.login_time.login_id.desc()).first()

            #      # Update the logout_time for the active login session
            #     login_entry.logout_time = logouttime
            #     db.commit()
            #     logging.info(f"Login end time updated for user {userid}")

            
            elif any(record.work_status == "End Of Day" for record in all_records):
                # Find the TL entry for the user with an "End Of Day" status
                tl_entry = next(record for record in all_records if record.work_status == "End Of Day")

                logging.info(f"TL entry found for user {userid}, Service_ID: {tl_entry.Service_ID}")

                  
               
                # Handle the last work session if it has an empty end_time
                last_work_session = db.query(models.WorkSession).filter(
                    models.WorkSession.user_id == userid,
                    models.WorkSession.end_time.is_(None)  # Check for None instead of empty string
                ).order_by(models.WorkSession.id.desc()).first()

                if last_work_session:
                    end_time_str = get_current_time_str_with_offset(2)  # Adjust end time if necessary
                    last_work_session.end_time = end_time_str
                    db.commit()
                    logging.info(f"End time updated for WorkSession for user {userid}")

                    # Calculate the total working time (end_time - start_time)
                    total_worked_time = calculate_total_times(last_work_session.start_time, last_work_session.end_time)
                    last_work_session.total_time_worked = total_worked_time
                    db.commit()
                    logging.info(f"Total working time updated for WorkSession for user {userid}")
                
                # Check for an active login session for the user
                login_entry = db.query(models.login_time).filter(
                    models.login_time.userid == userid,
                    models.WorkSession.end_time == ''  # Check for None instead of empty string
                ).order_by(models.login_time.login_id.desc()).first()

                 # Update the logout_time for the active login session
                login_entry.logout_time = logouttime
                db.commit()
                logging.info(f"Login end time updated for user {userid}")

            elif any(record.work_status == "Hold" for record in all_records):
                # Find the TL entry for the user with an "End Of Day" status
                tl_entry = next(record for record in all_records if record.work_status == "Hold")

                logging.info(f"TL entry found for user {userid}, Service_ID: {tl_entry.Service_ID}")

                  
               
                # Handle the last work session if it has an empty end_time
                last_work_session = db.query(models.WorkSession).filter(
                    models.WorkSession.user_id == userid,
                    models.WorkSession.end_time.is_(None)  # Check for None instead of empty string
                ).order_by(models.WorkSession.id.desc()).first()

                if last_work_session:
                    end_time_str = get_current_time_str_with_offset(2)  # Adjust end time if necessary
                    last_work_session.end_time = end_time_str
                    db.commit()
                    logging.info(f"End time updated for WorkSession for user {userid}")

                    # Calculate the total working time (end_time - start_time)
                    total_worked_time = calculate_total_times(last_work_session.start_time, last_work_session.end_time)
                    last_work_session.total_time_worked = total_worked_time
                    db.commit()
                    logging.info(f"Total working time updated for WorkSession for user {userid}")
                
                # Check for an active login session for the user
                login_entry = db.query(models.login_time).filter(
                    models.login_time.userid == userid,
                    models.WorkSession.end_time == ''  # Check for None instead of empty string
                ).order_by(models.login_time.login_id.desc()).first()

                 # Update the logout_time for the active login session
                login_entry.logout_time = logouttime
                db.commit()
                logging.info(f"Login end time updated for user {userid}")

            elif any(record.work_status == "Not Picked" for record in all_records):
                # Find the TL entry for the user with an "End Of Day" status
                tl_entry = next(record for record in all_records if record.work_status == "Not Picked")

                logging.info(f"TL entry found for user {userid}, Service_ID: {tl_entry.Service_ID}")

                  
               
                # Handle the last work session if it has an empty end_time
                last_work_session = db.query(models.WorkSession).filter(
                    models.WorkSession.user_id == userid,
                    models.WorkSession.end_time.is_(None)  # Check for None instead of empty string
                ).order_by(models.WorkSession.id.desc()).first()

                if last_work_session:
                    end_time_str = get_current_time_str_with_offset(2)  # Adjust end time if necessary
                    last_work_session.end_time = end_time_str
                    db.commit()
                    logging.info(f"End time updated for WorkSession for user {userid}")

                    # Calculate the total working time (end_time - start_time)
                    total_worked_time = calculate_total_times(last_work_session.start_time, last_work_session.end_time)
                    last_work_session.total_time_worked = total_worked_time
                    db.commit()
                    logging.info(f"Total working time updated for WorkSession for user {userid}")
                
                # Check for an active login session for the user
                login_entry = db.query(models.login_time).filter(
                    models.login_time.userid == userid,
                    models.WorkSession.end_time == ''  # Check for None instead of empty string
                ).order_by(models.login_time.login_id.desc()).first()

                 # Update the logout_time for the active login session
                login_entry.logout_time = logouttime
                db.commit()
                logging.info(f"Login end time updated for user {userid}")

            else:
                    logging.info(f"No 'Work in Progress' records found for user {userid}")


    except Exception as e:
        logging.error(f"An error occurred: {e}")

    
# =-----------------------------------------

# ---------------------------------logout status change to Hold- new function.............end



# --------------------------------------loging Tracking code start with username with MAH001 

# from sqlalchemy import not_

# def get_user_status(picked_date: str, to_date: str, db: Session):
#     # users = db.query(models.User_table).all()
#     # users = db.query(models.User_table).filter(models.User_table.role != 'Admin').all()
#     users = db.query(models.User_table).filter(not_(models.User_table.role.in_(['Admin', 'TL']))).all()

#     result = []

#     # Convert picked_date and to_date to datetime objects
#     try:
#         picked_date = datetime.strptime(picked_date, "%Y-%m-%d")
#         to_date = datetime.strptime(to_date, "%Y-%m-%d")
#     except ValueError:
#         return {"error": "Invalid date format"}

#     for user in users:
#         # Fetch all login records within the specified date range
#         login_records = (
#             db.query(models.login_time)
#             .filter(models.login_time.userid == user.user_id)
#             .filter(models.login_time.login_time.between(
#                 picked_date.strftime("%Y-%m-%d 00:00:00"),
#                 to_date.strftime("%Y-%m-%d 23:59:59")
#             ))
#             .order_by(models.login_time.login_id.desc())
#             .all()  # Fetch all records in the date range
#         )

#         if login_records:
#             for record in login_records:
#                 # Extract date from login_time
#                 login_date = record.login_time.split()[0]

#                 # Parse login_time and logout_time into datetime objects
#                 try:
#                     login_datetime = datetime.strptime(record.login_time, "%Y-%m-%d %H:%M:%S")
#                     logout_datetime = datetime.strptime(record.logout_time, "%Y-%m-%d %H:%M:%S") if record.logout_time else None
#                 except ValueError:
#                     login_datetime = logout_datetime = None

#                 # Calculate duration
#                 if login_datetime and logout_datetime:
#                     duration = logout_datetime - login_datetime
#                     duration_str = str(duration)
#                 else:
#                     duration_str = "Not Completed"

#                 # Status logic based on logout_time
#                 status = "Active" if not record.logout_time else "Inactive"
#                 logout_time_display = record.logout_time if record.logout_time else "Still Active"

#                 result.append({
#                     "username": user.username,
#                     "login_time": record.login_time,
#                     "logout_time": logout_time_display,
#                     "login_date": login_date,
#                     "duration": duration_str,
#                     "status": status
#                 })
#         else:
#             result.append({
#                 "username": user.username,
#                 "login_time": "Not Picked",
#                 "logout_time": "Not Picked",
#                 "login_date": "Not Picked",
#                 "duration": "Not Picked",
#                 "status": "Inactive"
#             })

#     return result


# --------------------------------------loging Tracking code start with username with Fisrt name and last name 
from sqlalchemy import not_
from datetime import datetime
from sqlalchemy.orm import Session

def get_user_status(picked_date: str, to_date: str, db: Session):
    users = db.query(models.User_table).filter(not_(models.User_table.role.in_(['Admin', 'TL']))).all()

    result = []

    # Convert picked_date and to_date to datetime objects
    try:
        picked_date = datetime.strptime(picked_date, "%Y-%m-%d")
        to_date = datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format"}

    for user in users:
        # Fetch all login records within the specified date range
        login_records = (
            db.query(models.login_time)
            .filter(models.login_time.userid == user.user_id)
            .filter(models.login_time.login_time.between(
                picked_date.strftime("%Y-%m-%d 00:00:00"),
                to_date.strftime("%Y-%m-%d 23:59:59")
            ))
            .order_by(models.login_time.login_id.desc())
            .all()
        )

        full_name = f"{user.firstname} {user.lastname}"

        if login_records:
            found_active_record = False
            
            for index, record in enumerate(login_records):
                # Extract date from login_time
                login_date = record.login_time.split()[0]

                # Parse login_time and logout_time into datetime objects
                try:
                    login_datetime = datetime.strptime(record.login_time, "%Y-%m-%d %H:%M:%S")
                    logout_datetime = datetime.strptime(record.logout_time, "%Y-%m-%d %H:%M:%S") if record.logout_time else None
                except ValueError:
                    login_datetime = logout_datetime = None

                # Calculate duration
                if login_datetime and logout_datetime:
                    duration = logout_datetime - login_datetime
                    duration_str = str(duration)
                else:
                    duration_str = "Not Completed"

                # Determine status logic based on the current record's logout time
                if not found_active_record:
                    if record.logout_time:  # If there's a logout time, mark as Inactive
                        status = "Inactive"
                    else:  # If there's no logout time and it's the latest record, mark as Active
                        status = "Active"
                        found_active_record = True  # Mark that we found an active record
                else:
                    status = "Inactive"  # All previous records are inactive

                logout_time_display = record.logout_time if record.logout_time else "Still Active"

                result.append({
                    "username": full_name,
                    "login_time": record.login_time,
                    "logout_time": logout_time_display,
                    "login_date": login_date,
                    "duration": duration_str,
                    "status": status
                })
        else:
            # Uncomment this section if you want to show users with no records as inactive
            # result.append({
            #     "username": full_name,
            #     "login_time": "Not Picked",
            #     "logout_time": "Not Picked",
            #     "login_date": "Not Picked",
            #     "duration": "Not Picked",
            #     "status": "Inactive"
            # })
            pass

    return result
# --------------------------------------loging Tracking code end



# ----------------------------new hold missing date added on with corn job--------------------------
# from datetime import datetime, timedelta
# from sqlalchemy.orm import Session

# def fetch_hold_data(db: Session):
#     print("Fetch Hold Data running...")

#     # Fetch records from the TL table where work_status is 'Hold'
#     tl_records = db.query(models.TL).filter(models.TL.work_status == 'Hold').all()
#     print(f"TL records fetched: {len(tl_records)}")

#     if not tl_records:
#         print("No records found in TL table with work_status 'Hold'. Exiting function.")
#         return []

#     # Create a set of Service_IDs from the fetched TL records for quick lookup
#     hold_service_ids = {tl.Service_ID for tl in tl_records}
#     print(f"Hold Service IDs: {hold_service_ids}")

#     # Fetch all hold records for the users with 'Hold' status
#     hold_records = db.query(models.HOLD).filter(
#         models.HOLD.Service_ID.in_(hold_service_ids)
#     ).order_by(models.HOLD.id.desc()).all()

#     print(f"Hold records fetched: {len(hold_records)}")

#     # Current datetime and date string formatting
#     current_datetime = datetime.now()
#     current_date_str = current_datetime.strftime('%Y-%m-%d')
#     current_time_str = current_datetime.strftime('%H:%M:%S')

#     # Log the current date
#     print(f"Current Date: {current_date_str}")

#     # Determine the last hold record's start time
#     last_hold_record = hold_records[0] if hold_records else None
#     last_hold_start_time = last_hold_record.hold_time_start if last_hold_record else None

#     if last_hold_start_time:
#         # Convert last_hold_start_time to a datetime object
#         if isinstance(last_hold_start_time, str):
#             last_hold_start_time = datetime.strptime(last_hold_start_time, '%Y-%m-%d %H:%M:%S')
#         print(f"Last hold start time: {last_hold_start_time}")
#     else:
#         print("No last hold record found.")
#         return

#     # Logic to create/update records based on last hold date
#     # Check for all previous dates and update or create records
#     current_date = datetime.now().date()
    
#     # Update the end time for the last hold record
#     if last_hold_record:
#         last_hold_record.hold_time_end = datetime.strptime(f"{current_date_str} 01:00:00", "%Y-%m-%d %H:%M:%S")
#         print(f"Updated hold record {last_hold_record.id} end time to {last_hold_record.hold_time_end}")

#     for single_date in (last_hold_start_time.date() + timedelta(n) for n in range((current_date - last_hold_start_time.date()).days + 1)):
#         check_date_str = single_date.strftime('%Y-%m-%d')

#         # Check if a hold record exists for this date
#         hold_record = db.query(models.HOLD).filter(
#             models.HOLD.Service_ID.in_(hold_service_ids),
#             models.HOLD.hold_time_start >= f"{check_date_str} 00:00:00",
#             models.HOLD.hold_time_start <= f"{check_date_str} 23:59:59"
#         ).first()

#         if hold_record:
#             if single_date != current_date:
#                 print(f"Hold record found for {check_date_str}: {hold_record.id} with start time {hold_record.hold_time_start}")
#         else:
#             # Create a new record if none exists for that date
#             print(f"No hold record found for {check_date_str}. Creating new record.")
#             for service_id in hold_service_ids:
#                 new_hold = models.HOLD(
#                     Service_ID=service_id,
#                     user_id=tl_records[0].Assigned_To,  # Assuming user_id is the same for the hold
#                     hold_time_start=f"{check_date_str} 01:00:00",  # Set to 01:00:00 for the new record
#                     hold_time_end=None if single_date == current_date else f"{check_date_str} 23:59:59",
#                     remarks="New hold record for today" if single_date == current_date else "New hold record for previous date"
#                 )
#                 db.add(new_hold)

#             db.commit()  
#             print(f"Created new hold record for {check_date_str}")

#     # Prepare and return result
#     result = []
#     for hold in hold_records:
#         result.append({
#             "id": hold.id,
#             "Service_ID": hold.Service_ID,
#             "user_id": hold.user_id,
#             "hold_time_start": hold.hold_time_start,
#             "hold_time_end": hold.hold_time_end,
#             "remarks": hold.remarks
#         })

#     return result

# def update_end_time(hold_record):
#     """Update the end time for the hold record."""
#     if hold_record:
#         # Convert hold_time_start to a datetime object if it's a string
#         if isinstance(hold_record.hold_time_start, str):
#             hold_record.hold_time_start = datetime.strptime(hold_record.hold_time_start, "%Y-%m-%d %H:%M:%S")
        
#         # Now extract the date part of hold_time_start
#         hold_start_date = hold_record.hold_time_start.date()

#         # Set the end time to 23:59:59 on the same day as hold_time_start
#         hold_end_time = datetime.combine(hold_start_date, datetime.max.time()).replace(microsecond=0)
        
#         # Ensure the end time is exactly 23:59:59, but only for previous days
#         hold_record.hold_time_end = hold_end_time
#         print(f"Updated hold record {hold_record.id} end time to {hold_record.hold_time_end}")

# from datetime import datetime, timedelta
# from sqlalchemy.orm import Session

# def fetch_hold_data(db: Session):
#     print("Fetch Hold Data running...")

#     # Fetch records from the TL table where work_status is 'Hold'
#     tl_records = db.query(models.TL).filter(models.TL.work_status == 'Hold').all()
#     print(f"TL records fetched: {len(tl_records)}")

#     if not tl_records:
#         print("No records found in TL table with work_status 'Hold'. Exiting function.")
#         return []

#     # Create a set of Service_IDs from the fetched TL records for quick lookup
#     hold_service_ids = {tl.Service_ID for tl in tl_records}
#     print(f"Hold Service IDs: {hold_service_ids}")

#     # Fetch all hold records for the users with 'Hold' status
#     hold_records = db.query(models.HOLD).filter(
#         models.HOLD.Service_ID.in_(hold_service_ids)
#     ).order_by(models.HOLD.id.desc()).all()

#     print(f"Hold records fetched: {len(hold_records)}")

#     # Current datetime and date string formatting
#     current_datetime = datetime.now()
#     current_date_str = current_datetime.strftime('%Y-%m-%d')

#     # Log the current date
#     print(f"Current Date: {current_date_str}")

#     # Determine the last hold record's start time
#     last_hold_record = hold_records[0] if hold_records else None
#     last_hold_start_time = last_hold_record.hold_time_start if last_hold_record else None

#     if last_hold_start_time:
#         # Convert last_hold_start_time to a datetime object
#         if isinstance(last_hold_start_time, str):
#             last_hold_start_time = datetime.strptime(last_hold_start_time, '%Y-%m-%d %H:%M:%S')
#         print(f"Last hold start time: {last_hold_start_time}")
#     else:
#         print("No last hold record found.")
#         return

#     # Logic to create/update records based on last hold date
#     # Check for all previous dates and update or create records
#     current_date = datetime.now().date()
    
#     # Update the end time for all relevant hold records
#     for hold_record in hold_records:
#         # Convert hold_time_start to a datetime object if it's a string
#         if isinstance(hold_record.hold_time_start, str):
#             hold_record.hold_time_start = datetime.strptime(hold_record.hold_time_start, "%Y-%m-%d %H:%M:%S")

#         hold_start_date = hold_record.hold_time_start.date()

#         # Update the end time if the record is for a previous date
#         if hold_start_date < current_date:
#             hold_end_time = datetime.combine(hold_start_date, datetime.max.time()).replace(microsecond=0)
#             hold_record.hold_time_end = hold_end_time
#             print(f"Updated hold record {hold_record.id} end time to {hold_record.hold_time_end}")

#     # Commit all updated records
#     db.commit()

#     for single_date in (last_hold_start_time.date() + timedelta(n) for n in range((current_date - last_hold_start_time.date()).days + 1)):
#         check_date_str = single_date.strftime('%Y-%m-%d')

#         # Check if a hold record exists for this date
#         hold_record = db.query(models.HOLD).filter(
#             models.HOLD.Service_ID.in_(hold_service_ids),
#             models.HOLD.hold_time_start >= f"{check_date_str} 00:00:00",
#             models.HOLD.hold_time_start <= f"{check_date_str} 23:59:59"
#         ).first()

#         if hold_record:
#             if single_date != current_date:
#                 print(f"Hold record found for {check_date_str}: {hold_record.id} with start time {hold_record.hold_time_start}")
#         else:
#             # Create a new record if none exists for that date
#             print(f"No hold record found for {check_date_str}. Creating new record.")
#             for service_id in hold_service_ids:
#                 new_hold = models.HOLD(
#                     Service_ID=service_id,
#                     user_id=tl_records[0].Assigned_To,  # Assuming user_id is the same for the hold
#                     hold_time_start=f"{check_date_str} 01:00:00",  # Set to 01:00:00 for the new record
#                     hold_time_end=None if single_date == current_date else f"{check_date_str} 23:59:59",
#                     remarks="New hold record for today" if single_date == current_date else "New hold record for previous date"
#                 )
#                 db.add(new_hold)

#             db.commit()  
#             print(f"Created new hold record for {check_date_str}")

#     # Prepare and return result
#     result = []
#     for hold in hold_records:
#         result.append({
#             "id": hold.id,
#             "Service_ID": hold.Service_ID,
#             "user_id": hold.user_id,
#             "hold_time_start": hold.hold_time_start,
#             "hold_time_end": hold.hold_time_end,
#             "remarks": hold.remarks
#         })

#     return result


#----------------------------------new hold missing date code



from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# def fetch_hold_data(db: Session):
#     print("Fetch Hold Data running...")

#     # Fetch records from the TL table where work_status is 'Hold'
#     tl_records = db.query(models.TL).filter(models.TL.work_status == 'Hold').all()
#     print(f"TL records fetched: {len(tl_records)}")

#     if not tl_records:
#         print("No records found in TL table with work_status 'Hold'. Exiting function.")
#         return []

#     # Create a set of Service_IDs from the fetched TL records for quick lookup
#     hold_service_ids = {tl.Service_ID for tl in tl_records}
#     print(f"Hold Service IDs: {hold_service_ids}")

#     # Fetch all hold records for the users with 'Hold' status
#     hold_records = db.query(models.HOLD).filter(
#         models.HOLD.Service_ID.in_(hold_service_ids)
#     ).order_by(models.HOLD.id.desc()).all()

#     print(f"Hold records fetched: {len(hold_records)}")

#     # Current datetime and date string formatting
#     current_datetime = datetime.now()
#     current_date_str = current_datetime.strftime('%Y-%m-%d')

#     # Log the current date
#     print(f"Current Date: {current_date_str}")

#     # Determine the last hold record's start time
#     last_hold_record = hold_records[0] if hold_records else None
#     last_hold_start_time = last_hold_record.hold_time_start if last_hold_record else None

#     if last_hold_start_time:
#         # Convert last_hold_start_time to a datetime object
#         if isinstance(last_hold_start_time, str):
#             last_hold_start_time = datetime.strptime(last_hold_start_time, '%Y-%m-%d %H:%M:%S')
#         print(f"Last hold start time: {last_hold_start_time}")
#     else:
#         print("No last hold record found.")
#         return

#     # Logic to create/update records based on last hold date
#     # Check for all previous dates and update or create records
#     current_date = datetime.now().date()
    
#     # Update the end time for all relevant hold records
#     for hold_record in hold_records:
#         # Convert hold_time_start to a datetime object if it's a string
#         if isinstance(hold_record.hold_time_start, str):
#             hold_record.hold_time_start = datetime.strptime(hold_record.hold_time_start, "%Y-%m-%d %H:%M:%S")

#         hold_start_date = hold_record.hold_time_start.date()

#         # Update the end time if the record is for a previous date
#         if hold_start_date < current_date:
#             hold_end_time = datetime.combine(hold_start_date, datetime.max.time()).replace(microsecond=0)
#             hold_record.hold_time_end = hold_end_time
#             print(f"Updated hold record {hold_record.id} end time to {hold_record.hold_time_end}")

#     # Commit all updated records
#     db.commit()

#     for single_date in (last_hold_start_time.date() + timedelta(n) for n in range((current_date - last_hold_start_time.date()).days + 1)):
#         check_date_str = single_date.strftime('%Y-%m-%d')

#         # Check if a hold record exists for this date
#         hold_record = db.query(models.HOLD).filter(
#             models.HOLD.Service_ID.in_(hold_service_ids),
#             models.HOLD.hold_time_start >= f"{check_date_str} 00:00:00",
#             models.HOLD.hold_time_start <= f"{check_date_str} 23:59:59"
#         ).first()

#         if hold_record:
#             if single_date != current_date:
#                 print(f"Hold record found for {check_date_str}: {hold_record.id} with start time {hold_record.hold_time_start}")
#         else:
#             # Create a new record if none exists for that date
#             print(f"No hold record found for {check_date_str}. Creating new record.")
#             for service_id in hold_service_ids:
#                 new_hold = models.HOLD(
#                     Service_ID=service_id,
#                     user_id=tl_records[0].Assigned_To,  # Assuming user_id is the same for the hold
#                     hold_time_start=f"{check_date_str} 01:00:00",  # Set to 01:00:00 for the new record
#                     hold_time_end=None if single_date == current_date else f"{check_date_str} 23:59:59",
#                     remarks="New hold record for today" if single_date == current_date else "New hold record for previous date"
#                 )
#                 db.add(new_hold)

#             db.commit()  
#             print(f"Created new hold record for {check_date_str}")

#     # Prepare and return result
#     result = []
#     for hold in hold_records:
#         result.append({
#             "id": hold.id,
#             "Service_ID": hold.Service_ID,
#             "user_id": hold.user_id,
#             "hold_time_start": hold.hold_time_start,
#             "hold_time_end": hold.hold_time_end,
#             "remarks": hold.remarks
#         })

#     return result


# from datetime import datetime, timedelta
# from sqlalchemy.orm import Session

# def fetch_hold_data(db: Session):
#     print("Fetch Hold Data running...")

#     # Fetch records from the TL table where work_status is 'Hold'
#     tl_records = db.query(models.TL).filter(models.TL.work_status == 'Hold').all()
#     print(f"TL records fetched: {len(tl_records)}")

#     if not tl_records:
#         print("No records found in TL table with work_status 'Hold'. Exiting function.")
#         return []

#     # Create a set of Service_IDs from the fetched TL records for quick lookup
#     hold_service_ids = {tl.Service_ID for tl in tl_records}
#     print(f"Hold Service IDs: {hold_service_ids}")

#     # Fetch all hold records for the users with 'Hold' status
#     hold_records = db.query(models.HOLD).filter(
#         models.HOLD.Service_ID.in_(hold_service_ids)
#     ).order_by(models.HOLD.id.desc()).all()

#     print(f"Hold records fetched: {len(hold_records)}")

#     # Current datetime and date string formatting
#     current_datetime = datetime.now()
#     current_date_str = current_datetime.strftime('%Y-%m-%d')

#     # Log the current date
#     print(f"Current Date: {current_date_str}")

#     # Determine the last hold record's start time
#     last_hold_record = hold_records[0] if hold_records else None
#     last_hold_start_time = last_hold_record.hold_time_start if last_hold_record else None

#     if last_hold_start_time:
#         # Convert last_hold_start_time to a datetime object if it's a string
#         if isinstance(last_hold_start_time, str):
#             last_hold_start_time = datetime.strptime(last_hold_start_time, '%Y-%m-%d %H:%M:%S')
#         print(f"Last hold start time: {last_hold_start_time}")
#     else:
#         print("No last hold record found.")
#         return

#     # Logic to create/update records based on last hold date
#     current_date = datetime.now().date()  # Ensure this is a date object
    
#     # Update the end time for all relevant hold records
#     for hold_record in hold_records:
#         # Convert hold_time_start to a datetime object if it's a string
#         if isinstance(hold_record.hold_time_start, str):
#             hold_record.hold_time_start = datetime.strptime(hold_record.hold_time_start, "%Y-%m-%d %H:%M:%S")

#         # Ensure hold_time_start is a datetime object before calling .date()
#         if isinstance(hold_record.hold_time_start, datetime):
#             hold_start_date = hold_record.hold_time_start.date()

#             # Debugging information
#             print(f"Checking record {hold_record.id}: start date {hold_start_date}, current date {current_date}, end time {hold_record.hold_time_end}")

#             # Update the end time only if it is empty (None or '') and the record is for a previous date
#             if hold_start_date < current_date and (hold_record.hold_time_end is None or hold_record.hold_time_end == ''):
#                 hold_end_time = datetime.combine(hold_start_date, datetime.max.time()).replace(microsecond=0)
#                 hold_record.hold_time_end = hold_end_time
#                 print(f"Updated hold record {hold_record.id} end time to {hold_record.hold_time_end}")

#     # Commit all updated records
#     db.commit()

#     for single_date in (last_hold_start_time.date() + timedelta(n) for n in range((current_date - last_hold_start_time.date()).days + 1)):
#         check_date_str = single_date.strftime('%Y-%m-%d')

#         # Check if a hold record exists for this date
#         hold_record = db.query(models.HOLD).filter(
#             models.HOLD.Service_ID.in_(hold_service_ids),
#             models.HOLD.hold_time_start >= f"{check_date_str} 00:00:00",
#             models.HOLD.hold_time_start <= f"{check_date_str} 23:59:59"
#         ).first()

#         if hold_record:
#             if single_date != current_date:
#                 print(f"Hold record found for {check_date_str}: {hold_record.id} with start time {hold_record.hold_time_start}")
#         else:
#             # Create a new record if none exists for that date
#             print(f"No hold record found for {check_date_str}. Creating new record.")
#             for service_id in hold_service_ids:
#                 new_hold = models.HOLD(
#                     Service_ID=service_id,
#                     user_id=tl_records[0].Assigned_To,  # Assuming user_id is the same for the hold
#                     hold_time_start=f"{check_date_str} 01:00:00",  # Set to 01:00:00 for the new record
#                     hold_time_end=None if single_date == current_date else f"{check_date_str} 23:59:59",
#                     remarks="New hold record for today" if single_date == current_date else "New hold record for previous date"
#                 )
#                 db.add(new_hold)

#             db.commit()  
#             print(f"Created new hold record for {check_date_str}")

#     # Prepare and return result
#     result = []
#     for hold in hold_records:
#         result.append({
#             "id": hold.id,
#             "Service_ID": hold.Service_ID,
#             "user_id": hold.user_id,
#             "hold_time_start": hold.hold_time_start,
#             "hold_time_end": hold.hold_time_end,
#             "remarks": hold.remarks
#         })

#     return result

# --------new hold missing date updated code 07/10/2024-12:32-----


def fetch_hold_data(db: Session):
    print("Fetch Hold Data running...")

    # Fetch records from the TL table where work_status is 'Hold'
    tl_records = db.query(models.TL).filter(models.TL.work_status == 'Hold').all()
    print(f"TL records fetched: {len(tl_records)}")

    if not tl_records:
        print("No records found in TL table with work_status 'Hold'. Exiting function.")
        return []

    # Create a dictionary mapping Service_ID to Assigned_To (user_id) from the fetched TL records
    service_id_user_map = {tl.Service_ID: tl.Assigned_To for tl in tl_records}
    print(f"Service ID to User ID Map: {service_id_user_map}")

    # Fetch all hold records for the users with 'Hold' status
    hold_records = db.query(models.HOLD).filter(
        models.HOLD.Service_ID.in_(service_id_user_map.keys())
    ).order_by(models.HOLD.id.desc()).all()

    print(f"Hold records fetched: {len(hold_records)}")

    # Current datetime and date string formatting
    current_datetime = datetime.now()
    current_date_str = current_datetime.strftime('%Y-%m-%d')

    # Log the current date
    print(f"Current Date: {current_date_str}")

    # Determine the last hold record's start time
    last_hold_record = hold_records[0] if hold_records else None
    last_hold_start_time = last_hold_record.hold_time_start if last_hold_record else None

    if last_hold_start_time:
        # Convert last_hold_start_time to a datetime object if it's a string
        if isinstance(last_hold_start_time, str):
            last_hold_start_time = datetime.strptime(last_hold_start_time, '%Y-%m-%d %H:%M:%S')
        print(f"Last hold start time: {last_hold_start_time}")
    else:
        print("No last hold record found.")
        return

    # Logic to create/update records based on last hold date
    current_date = datetime.now().date()  # Ensure this is a date object

    # Update the end time for all relevant hold records
    for hold_record in hold_records:
        # Convert hold_time_start to a datetime object if it's a string
        if isinstance(hold_record.hold_time_start, str):
            hold_record.hold_time_start = datetime.strptime(hold_record.hold_time_start, "%Y-%m-%d %H:%M:%S")

        # Ensure hold_time_start is a datetime object before calling .date()
        if isinstance(hold_record.hold_time_start, datetime):
            hold_start_date = hold_record.hold_time_start.date()

            # Debugging information
            print(f"Checking record {hold_record.id}: start date {hold_start_date}, current date {current_date}, end time {hold_record.hold_time_end}")

            # Update the end time only if it is empty (None or '') and the record is for a previous date
            if hold_start_date < current_date and (hold_record.hold_time_end is None or hold_record.hold_time_end == ''):
                hold_end_time = datetime.combine(hold_start_date, datetime.max.time()).replace(microsecond=0)
                hold_record.hold_time_end = hold_end_time
                print(f"Updated hold record {hold_record.id} end time to {hold_record.hold_time_end}")

    # Commit all updated records
    db.commit()

    # Loop through each date between the last hold start time and the current date
    for single_date in (last_hold_start_time.date() + timedelta(n) for n in range((current_date - last_hold_start_time.date()).days + 1)):
        check_date_str = single_date.strftime('%Y-%m-%d')

        # Check if a hold record exists for this date
        hold_record = db.query(models.HOLD).filter(
            models.HOLD.Service_ID.in_(service_id_user_map.keys()),
            models.HOLD.hold_time_start >= f"{check_date_str} 00:00:00",
            models.HOLD.hold_time_start <= f"{check_date_str} 23:59:59"
        ).first()

        if hold_record:
            if single_date != current_date:
                print(f"Hold record found for {check_date_str}: {hold_record.id} with start time {hold_record.hold_time_start}")
        else:
            # Create a new record if none exists for that date for each service_id
            print(f"No hold record found for {check_date_str}. Creating new record.")
            for service_id, user_id in service_id_user_map.items():
                new_hold = models.HOLD(
                    Service_ID=service_id,
                    user_id=user_id,  # Use the correct user_id for each service_id
                    hold_time_start=f"{check_date_str} 01:00:00",  # Set to 01:00:00 for the new record
                    hold_time_end=None if single_date == current_date else f"{check_date_str} 23:59:59",
                    remarks="New hold record for today" if single_date == current_date else "New hold record for previous date"
                )
                db.add(new_hold)

            db.commit()
            print(f"Created new hold record for {check_date_str}")

    # Prepare and return result
    result = []
    for hold in hold_records:
        result.append({
            "id": hold.id,
            "Service_ID": hold.Service_ID,
            "user_id": hold.user_id,
            "hold_time_start": hold.hold_time_start,
            "hold_time_end": hold.hold_time_end,
            "remarks": hold.remarks
        })
    
    return result


"""-------
---------------
----------------
-----------------
------------------
---------------------
-----------------
------------------------
----------------------
-
-
-
-
-
-
-
-
-
-
-
-
-
-

-
------------------------
-----------------------
-----------------------
-----------------------
---------------------
-----------------------
----------------------"""

# ---------------------------------------------update version-------------------------------------------
# ----------------------start udpate version for hold
# def hold_action(db: Session, user_id: int, service_id: int):
     
#     current_time = datetime.now()

#     hold_record = db.query(models.HOLD).filter(
#         and_(models.HOLD.user_id == user_id, models.HOLD.Service_ID == service_id)
#     ).order_by(models.HOLD.hold_time_start.desc()).first()

#     if hold_record and hold_record.hold_time_end is None:
#         hold_record.hold_time_end = current_time
#         total_seconds = (hold_record.hold_time_end - hold_record.hold_time_start).total_seconds()
#         hold_record.hold_total_time = str(timedelta(seconds=int(total_seconds))).split('.')[0]

#         db.commit()
#         return "Hold record updated successfully."

#     else:
#         new_hold = models.HOLD(
#             user_id=user_id,
#             Service_ID=service_id,
#             hold_time_start=current_time
#         )
#         db.add(new_hold)
#         db.commit()
#         db.refresh(new_hold)

#         return "New hold record created successfully."
    


# def calculate_total_time_hold(db: Session, picked_date: str, to_date: str) -> dict:
#     picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
#     to_datett = datetime.strptime(to_date, "%Y-%m-%d")

#     picked_date_start = picked_datett.replace(hour=0, minute=0, second=0)
#     to_date_end = to_datett.replace(hour=23, minute=59, second=59)

#     hold_records = db.query(models.HOLD).filter(
#         models.HOLD.hold_time_start >= picked_date_start,
#         models.HOLD.hold_time_start <= to_date_end
#     ).all()

#     user_total_time = defaultdict(timedelta)

#     current_time = datetime.now()

#     for record in hold_records:
#         start_time = record.hold_time_start

#         if record.hold_time_end:
#             end_time = record.hold_time_end
#             user_total_time[record.user_id] += (end_time - start_time)
#         else:
#             if start_time.date() == current_time.date():
#                 end_time = current_time
#                 user_total_time[record.user_id] += (end_time - start_time)
#             elif start_time.date() < current_time.date():
#                 continue

#     formatted_total_time = {
#         user_id: str(hold_total_time).split('.')[0] for user_id,  hold_total_time in user_total_time.items()
#     }

#     return formatted_total_time
# # ----------------------end udpate version for hold


# # ----------------------start udpate version for break
# def break_action(db: Session, user_id: int, service_id: int):
     
#     current_time = datetime.now()

#     break_record = db.query(models.BREAK).filter(
#         and_(models.BREAK.user_id == user_id, models.BREAK.Service_ID == service_id)
#     ).order_by(models.BREAK.break_time_start.desc()).first()

#     if break_record and break_record.break_time_end is None:
#         break_record.break_time_end = current_time
#         total_seconds = (break_record.break_time_end - break_record.break_time_start).total_seconds()
#         break_record.break_total_time = str(timedelta(seconds=int(total_seconds))).split('.')[0]

#         db.commit()
#         return "BREAK record updated successfully."

#     else:
#         new_break = models.BREAK(
#             user_id=user_id,
#             Service_ID=service_id,
#             break_time_start=current_time
#         )
#         db.add(new_break)
#         db.commit()
#         db.refresh(new_break)

#         return "New Break record created successfully."
    


# def calculate_total_time_break(db: Session, picked_date: str, to_date: str) -> dict:
#     picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
#     to_datett = datetime.strptime(to_date, "%Y-%m-%d")

#     picked_date_start = picked_datett.replace(hour=0, minute=0, second=0)
#     to_date_end = to_datett.replace(hour=23, minute=59, second=59)

#     break_records = db.query(models.BREAK).filter(
#         models.BREAK.break_time_start >= picked_date_start,
#         models.BREAK.break_time_start <= to_date_end
#     ).all()

#     user_total_time = defaultdict(timedelta)

#     current_time = datetime.now()

#     for record in break_records:
#         start_time = record.break_time_start

#         if record.break_time_end:
#             end_time = record.break_time_end
#             user_total_time[record.user_id] += (end_time - start_time)
#         else:
#             if start_time.date() == current_time.date():
#                 end_time = current_time
#                 user_total_time[record.user_id] += (end_time - start_time)
#             elif start_time.date() < current_time.date():
#                 continue

#     formatted_total_time = {
#         user_id: str(break_total_time).split('.')[0] for user_id,  break_total_time in user_total_time.items()
#     }

#     return formatted_total_time
# # ----------------------end udpate version for break


# # ----------------------start udpate version for meeting
# def meeting_action(db: Session, user_id: int, service_id: int):
     
#     current_time = datetime.now()

#     meet_records = db.query(models.MEETING).filter(
#         and_(models.MEETING.user_id == user_id, models.MEETING.Service_ID == service_id)
#     ).order_by(models.MEETING.meeting_time_start.desc()).first()

#     if meet_records and meet_records.meeting_time_end is None:
#         meet_records.meeting_time_end = current_time
#         total_seconds = (meet_records.meeting_time_end - meet_records.meeting_time_start).total_seconds()
#         meet_records.meet_total_time = str(timedelta(seconds=int(total_seconds))).split('.')[0]

#         db.commit()
#         return "meeting record updated successfully."

#     else:
#         new_meet = models.MEETING(
#             user_id=user_id,
#             Service_ID=service_id,
#             meeting_time_start=current_time
#         )
#         db.add(new_meet)
#         db.commit()
#         db.refresh(new_meet)

#         return "New meeting record created successfully."
    


# def calculate_total_time_meeting(db: Session, picked_date: str, to_date: str) -> dict:
#     picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
#     to_datett = datetime.strptime(to_date, "%Y-%m-%d")

#     picked_date_start = picked_datett.replace(hour=0, minute=0, second=0)
#     to_date_end = to_datett.replace(hour=23, minute=59, second=59)

#     meet_records = db.query(models.MEETING).filter(
#         models.MEETING.meeting_time_start >= picked_date_start,
#         models.MEETING.meeting_time_start <= to_date_end
#     ).all()

#     user_total_time = defaultdict(timedelta)

#     current_time = datetime.now()

#     for record in meet_records:
#         start_time = record.meeting_time_start

#         if record.meeting_time_end:
#             end_time = record.meeting_time_end
#             user_total_time[record.user_id] += (end_time - start_time)
#         else:
#             if start_time.date() == current_time.date():
#                 end_time = current_time
#                 user_total_time[record.user_id] += (end_time - start_time)
#             elif start_time.date() < current_time.date():
#                 continue

#     formatted_total_time = {
#         user_id: str(meet_total_time).split('.')[0] for user_id,  meet_total_time in user_total_time.items()
#     }

#     return formatted_total_time
# # ----------------------end udpate version for meeting


# # ----------------------start udpate version for call
# def call_action(db: Session, user_id: int, service_id: int):
     
#     current_time = datetime.now()

#     call_records = db.query(models.CALL).filter(
#         and_(models.CALL.user_id == user_id, models.CALL.Service_ID == service_id)
#     ).order_by(models.CALL.call_time_start.desc()).first()

#     if call_records and call_records.call_time_end is None:
#         call_records.call_time_end = current_time
#         total_seconds = (call_records.call_time_end - call_records.call_time_start).total_seconds()
#         call_records.call_total_time = str(timedelta(seconds=int(total_seconds))).split('.')[0]

#         db.commit()
#         return "CALL record updated successfully."

#     else:
#         new_meet = models.CALL(
#             user_id=user_id,
#             Service_ID=service_id,
#             call_time_start=current_time
#         )
#         db.add(new_meet)
#         db.commit()
#         db.refresh(new_meet)

#         return "New CALL record created successfully."
    


# def calculate_total_time_call(db: Session, picked_date: str, to_date: str) -> dict:
#     picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
#     to_datett = datetime.strptime(to_date, "%Y-%m-%d")

#     picked_date_start = picked_datett.replace(hour=0, minute=0, second=0)
#     to_date_end = to_datett.replace(hour=23, minute=59, second=59)

#     call_records = db.query(models.CALL).filter(
#         models.CALL.call_time_start >= picked_date_start,
#         models.CALL.call_time_start <= to_date_end
#     ).all()

#     user_total_time = defaultdict(timedelta)

#     current_time = datetime.now()

#     for record in call_records:
#         start_time = record.call_time_start

#         if record.call_time_end:
#             end_time = record.call_time_end
#             user_total_time[record.user_id] += (end_time - start_time)
#         else:
#             if start_time.date() == current_time.date():
#                 end_time = current_time
#                 user_total_time[record.user_id] += (end_time - start_time)
#             elif start_time.date() < current_time.date():
#                 continue

#     formatted_total_time = {
#         user_id: str(call_total_time).split('.')[0] for user_id,  call_total_time in user_total_time.items()
#     }

#     return formatted_total_time
# # ----------------------end udpate version for call


# # ----------------------start udpate version for inprogress
# def inprogress_action(db: Session, user_id: int, service_id: int):
     
#     current_time = datetime.now()

#     inprogress_records = db.query(models.INPROGRESS).filter(
#         and_(models.INPROGRESS.user_id == user_id, models.INPROGRESS.Service_ID == service_id)
#     ).order_by(models.INPROGRESS.start_time.desc()).first()

#     if inprogress_records and inprogress_records.end_time is None:
#         inprogress_records.end_time = current_time
#         total_seconds = (inprogress_records.end_time - inprogress_records.start_time).total_seconds()
#         inprogress_records.total_time = str(timedelta(seconds=int(total_seconds))).split('.')[0]

#         db.commit()
#         return "INPROGRESS record updated successfully."

#     else:
#         new_meet = models.INPROGRESS(
#             user_id=user_id,
#             Service_ID=service_id,
#             start_time=current_time
#         )
#         db.add(new_meet)
#         db.commit()
#         db.refresh(new_meet)

#         return "New INPROGRESS record created successfully."
    


# def calculate_total_time_inprogress(db: Session, picked_date: str, to_date: str) -> dict:
#     picked_datett = datetime.strptime(picked_date, "%Y-%m-%d")
#     to_datett = datetime.strptime(to_date, "%Y-%m-%d")

#     picked_date_start = picked_datett.replace(hour=0, minute=0, second=0)
#     to_date_end = to_datett.replace(hour=23, minute=59, second=59)

#     inprogress_records = db.query(models.INPROGRESS).filter(
#         models.INPROGRESS.start_time >= picked_date_start,
#         models.INPROGRESS.start_time <= to_date_end
#     ).all()

#     user_total_time = defaultdict(timedelta)

#     current_time = datetime.now()

#     for record in inprogress_records:
#         start_time = record.start_time

#         if record.end_time:
#             end_time = record.end_time
#             user_total_time[record.user_id] += (end_time - start_time)
#         else:
#             if start_time.date() == current_time.date():
#                 end_time = current_time
#                 user_total_time[record.user_id] += (end_time - start_time)
#             elif start_time.date() < current_time.date():
#                 continue

#     formatted_total_time = {
#         user_id: str(total_time).split('.')[0] for user_id,  total_time in user_total_time.items()
#     }

#     return formatted_total_time
# # ----------------------end udpate version for inprogress

# def calculate_and_store_total_times(db: Session, user_id: int, service_id: int):
#     today = date.today()

#     # Fetch total time from INPROGRESS for today
#     inprogress_records = db.query(models.INPROGRESS).filter(
#         models.INPROGRESS.user_id == user_id, 
#         models.INPROGRESS.Service_ID == service_id,
#         models.INPROGRESS.start_time >= today,  # Only consider records from today
#     ).all()

#     # Fetching logic for HOLD, BREAK, MEETING, CALL, IDEAL
#     hold_records = db.query(models.HOLD).filter(
#         models.HOLD.user_id == user_id, 
#         models.HOLD.Service_ID == service_id,
#         models.HOLD.hold_time_start >= today,
#     ).all()

#     break_records = db.query(models.BREAK).filter(
#         models.BREAK.user_id == user_id, 
#         models.BREAK.Service_ID == service_id,
#         models.BREAK.break_time_start >= today,
#     ).all()

#     meeting_records = db.query(models.MEETING).filter(
#         models.MEETING.user_id == user_id, 
#         models.MEETING.Service_ID == service_id,
#         models.MEETING.meeting_time_start >= today,
#     ).all()

#     call_records = db.query(models.CALL).filter(
#         models.CALL.user_id == user_id, 
#         models.CALL.Service_ID == service_id,
#         models.CALL.call_time_start >= today,
#     ).all()

#     ideal_time_records = db.query(models.WorkSession).filter(
#         models.WorkSession.user_id == user_id
#     ).all()

#     # Prepare the values for TotalTimeTaken
#     total_inprogress_time = [record.total_time for record in inprogress_records]
#     total_hold_time = [record.hold_total_time for record in hold_records]
#     total_break_time = [record.break_total_time for record in break_records]
#     total_meeting_time = [record.meet_total_time for record in meeting_records]
#     total_call_time = [record.call_total_time for record in call_records]
#     total_ideal_time = [record.total_time_worked for record in ideal_time_records]

#     def get_first_or_default(record_list):
#         return record_list[0] if record_list else None  # Default to "0:00:00" if empty

#     # Initialize total_time_taken only if there are today's records
#     if inprogress_records or hold_records or break_records or meeting_records or call_records:
#         total_time_taken = models.TotalTimeTaken(
#             user_id=user_id,
#             service_id=service_id,
#             total_inprogress_time=get_first_or_default(total_inprogress_time),
#             total_hold_time=get_first_or_default(total_hold_time),
#             total_break_time=get_first_or_default(total_break_time),
#             total_meeting_time=get_first_or_default(total_meeting_time),
#             total_call_time=get_first_or_default(total_call_time),
#             total_ideal_time=get_first_or_default(total_ideal_time),
#             date=today,  # Set today's date
#         )

#         # Check if a record for this user and service exists
#         existing_record = db.query(models.TotalTimeTaken).filter(
#             models.TotalTimeTaken.user_id == user_id, 
#             models.TotalTimeTaken.service_id == service_id,
#             models.TotalTimeTaken.date == today  # Match the date
#         ).first()

#         if existing_record:
#             # Update existing record only if the new value is not None
#             if total_time_taken.total_inprogress_time:
#                 existing_record.total_inprogress_time = total_time_taken.total_inprogress_time
#             if total_time_taken.total_hold_time:
#                 existing_record.total_hold_time = total_time_taken.total_hold_time
#             if total_time_taken.total_break_time:
#                 existing_record.total_break_time = total_time_taken.total_break_time
#             if total_time_taken.total_meeting_time:
#                 existing_record.total_meeting_time = total_time_taken.total_meeting_time
#             if total_time_taken.total_call_time:
#                 existing_record.total_call_time = total_time_taken.total_call_time
#             if total_time_taken.total_ideal_time:
#                 existing_record.total_ideal_time = total_time_taken.total_ideal_time
#         else:
#             db.add(total_time_taken)

#         db.commit()


#         return total_time_taken
#     else:
#         return None