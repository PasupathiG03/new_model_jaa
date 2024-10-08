from sqlalchemy.orm import Session
from src import crud
from . import models, schemas
from fastapi import UploadFile,HTTPException
import pandas as pd
import json
from datetime import date,datetime,timedelta
import os
from zipfile import ZipFile
import tracemalloc
import shutil
from sqlalchemy import cast, or_,and_,func,Date
import csv
from datetime import datetime, timedelta
from io import BytesIO
import pendulum



def reset_to_midnight_and_get_timedelta(time_str):
    # Parse the given time
    current_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
    
    # Create a new datetime object with the same date but with time set to midnight
    midnight_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate the timedelta
    time_difference = current_time - midnight_time
    
    return  time_difference

from datetime import datetime

def calculate_end_of_day(current_time_str):
    # Parse the given current time
    current_time = datetime.strptime(current_time_str, '%Y-%m-%d %H:%M:%S')
    
    # Set time to end of the day (23:59:59)
    end_of_day = current_time.replace(hour=23, minute=59, second=59, microsecond=0)
    
    return end_of_day

def time_differencet(current_time_str):
    # Calculate the end of the day
    end_of_day = calculate_end_of_day(current_time_str)
    
    # Parse the given current time
    current_time = datetime.strptime(current_time_str, '%Y-%m-%d %H:%M:%S')
    
    # Calculate the time difference
    time_diff = end_of_day - current_time
    
    return end_of_day, time_diff






def time_difference(time1a , time2a):
    date_time_formate_string = '%Y-%m-%d %H:%M:%S'
    time1 = time1a
    time2 = time2a
    # print(type(time1) == str)
    if time1:
        if type(time1) == str:
             time1 = datetime.strptime(time1, date_time_formate_string)
    if time2:
        if type(time2) == str:
             time2 = datetime.strptime(time2, date_time_formate_string)
    if time1 and time2:
        try:
            # print(time1,time2,'two times')
            return time1 - time2
        except :
            return timedelta(hours=0)
    elif time1:
        time2 = datetime.now()
        try:
            # print(time1,datetime.now(),'time 2 absent')
            return time1 - datetime.now()
        except :
            return timedelta(hours=0)
    else :
        time1 = datetime.now()
        try:
            # print(time1,datetime.now(),'time 1 absent')
            return time1 - datetime.now()
        except :
            return timedelta(hours=0)

def convert_to_duration(value):
        total_seconds = int(value.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_duration = f"{hours}:{minutes}:{seconds}"
        
        return formatted_duration


def commoncalculation(db: Session,db_res, date: str):
            h1_start = None
            h2_end = None
            list_data = []
            idealname = ''
            date_time1 = datetime.now()
            date_time_formate_string = '%Y-%m-%d %H:%M:%S'
            for row in db_res:
                
                data = {}
               
                data["date"] = date
                data["user"] = row._user_table1.username
                idealname = row.Assigned_To
                data["Service_ID"] = row.Service_ID
                data["scope"] = row.Scope
                data["subscopes"] = row.From
                data["entity"] = row.name_of_entity
                data["status"] = row.work_status
                data["created_at"] =  (row.created_on).date()
                data["Completed_date"] = (row.completed_time)
                data["type_of_activity"] = row.type_of_activity
                data["Nature_of_Work"] = row._nature_of_work.work_name
                data["gst_tan"] = row.gst_tan
                data["estimated_d_o_d"] =  row.estimated_d_o_d
                data["no_of_items"] = row.no_of_items
                data["estimated_time"] =  row.estimated_time
                data["member_name"] = row._user_table1.firstname +' '+ row._user_table1.lastname
                data['break'] = None
                data['call'] = None
                data['meeting'] = None
                data['hold'] = None
                data['in_progress'] = None
                data['completed'] = None
                working_time_report = datetime.strptime(row.working_time, date_time_formate_string)
                completed_time_report = None
                try:
                    completed_time_report = datetime.strptime(row.completed_time, date_time_formate_string)
                except Exception as e:
                    None
                
                    # print(f"An unexpected error occurred: {e}")
                hold_time_report = None
                break_time_report = None
                meeting_time_report = None
                call_time_report = None
                totalminus = None
                Totaltime = None
                

                current_time_report = datetime.now()
#---------------------------------------------------------------------------------------------------------------------- timing code for old start

                

                old_hold_start_time = None
                old_end_start_time = None
                old_hold_t1 = None
                old_end_t2 = None
                old_end = None
                old_hold_for_total = False
                try:
                    



                    query = db.query(models.HOLD).filter(
                        models.HOLD.Service_ID == row.Service_ID,
                        models.HOLD.hold_time_start < date,
                        
                    )
                    
                    if query:
                        nu = query.count()
                        re = query.all()
                        print(re[nu-1].hold_time_end,nu,'old_hold time iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
                        old_hold_start_time = re[nu-1].hold_time_start
                        old_hold_t1 = re[nu-1].hold_time_end
                    else:
                        print("No hold record found for Service_ID 14")
                except Exception as e:
                    None
                
                try:
                    query = db.query(models.END_OF_DAY).filter(
                        models.END_OF_DAY.Service_ID == row.Service_ID,
                        models.END_OF_DAY.end_time_start < date,
                        
                    )

                    if query:
                        nu = query.count()
                        re = query.all()
                        print(re[nu-1].end_time_end,nu,'old_end time iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii')
                        old_end_start_time = re[nu-1].end_time_start
                        old_end_t2 = re[nu-1].end_time_end
                    else:
                        print("No hold record found for Service_ID 14")
                except Exception as e:
                    None
                
                    # print(f"An unexpected error occurred: {e}")


                # print(old_hold_start_time , old_end_start_time,'fffffffffffffffffffffffffffffffffffffffffffffffffffffff')
                try:
                  old_hold_start_time = datetime.strptime(old_hold_start_time, date_time_formate_string)
                #   print(old_hold_start_time)
                except Exception as e:
                    None
                
                    # print(f"An unexpected error occurred: {e}")
                # print(old_hold_start_time , old_end_start_time,'ggggggggggggggggggggggggggggggggggggggggggggg')
                try:
                  old_end_start_time = datetime.strptime(old_end_start_time, date_time_formate_string)
                 
                except Exception as e:
                    None
                
                    # print(f"An unexpected error occurred: {e}")
                
                try:
                    if old_hold_start_time > old_end_start_time:
                            old_end = old_hold_t1
                            old_hold_for_total = True
                            print(old_end,'hold time ........................................................................................................................')

                except Exception as e:
                    None
                
                    # print(f"An unexpected error occurred: {e}")
                
                try:
                    if  old_hold_start_time < old_end_start_time:
                            old_end = old_end_t2

                except Exception as e:
                    None
                
                    # print(f"An unexpected error occurred: {e}")
                try:
                    if  (old_hold_start_time==None) and  (old_end_start_time!=None):
                            old_end = old_end_t2
                except Exception as e:
                    None
                
                    # print(f"An unexpected error occurred: {e}")
                try:
                    if  (old_end_start_time==None) and  (old_hold_start_time!=None):
                            old_hold_for_total = True
                            old_end = old_hold_t1
                            print(old_end,'hold time ........................................................................................................................')
                except Exception as e:
                    None
                
                    # print(f"An unexpected error occurred: {e}")

                # print(old_end,'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
#----------------------------------------------------------------------------------------------------   old start time end    




#---------------------------------------------------------------------------------------------------------------------- timing code for past today start
                date_obj = datetime.strptime(date, '%Y-%m-%d')

                # Add one day to the date
                new_date = date_obj + timedelta(days=1)

                # Format the new date back into a string
                added_date = new_date.strftime('%Y-%m-%d')

                past_today_greater_end_start = None
                past_today_greater_hold_start = None
                past_today_lower_hold_start = None
                past_today_greater_end_end = None
                past_today_greater_hold_end = None
                past_hold_t1 = None
                past_end_t2 = None
                past_today_greater = None
                days_hold_greater = None
                
                try:
                    query = db.query(models.HOLD).filter(
                        models.HOLD.Service_ID == row.Service_ID,
                        models.HOLD.hold_time_start.like(f"%{date}%"),
                    )

                    if query:
                        nu = query.count()
                        re = query.all()
                        print(re[nu-1].hold_time_start,'past_old_hold start ........................................................')
                        past_today_greater_end_end = re[nu-1].hold_time_start
                        past_today_greater_hold_start = re[nu-1].hold_time_start
                        past_hold_t1 = re[nu-1].hold_time_start
                    else:
                        None

                        # print("No hold record found for Service_ID 14")
                except Exception as e:
                    None
                
                    # print(f"An unexpected error occurred: {e}")

                
                query = db.query(models.END_OF_DAY).filter(
                    models.END_OF_DAY.Service_ID == row.Service_ID,
                    models.END_OF_DAY.end_time_start.like(f"%{date}%"),
                )
                print(query.count())
                try:
                    if query:
                        nu = query.count()
                        re = query.all()
                        print(re[nu-1].end_time_start ,'past_old_end start ........................................................')
                        past_today_greater_hold_end = re[nu-1].end_time_start
                        past_today_greater_end_start = re[nu-1].end_time_start
                        past_end_t2 = re[nu-1].end_time_start
                    else:
                        None

                        # print("No hold record found for Service_ID 14")
                except Exception as e:
                    None
                
                    # print(f"An unexpected error occurred: {e}")


                # print(past_today_greater_end_end , past_today_greater_hold_end,'fffffffffffffffffffffffffffffffffffffffffffffffffffffff')
                try:
                  past_today_greater_end_end = datetime.strptime(past_today_greater_end_end, date_time_formate_string)
                #   print(past_today_greater_end_end)
                except Exception as e:
                    None
                
                    # print(f"An unexpected error occurred: {e}")
                # print(past_today_greater_end_end , past_today_greater_hold_end,'ggggggggggggggggggggggggggggggggggggggggggggg')
                try:
                  past_today_greater_hold_end = datetime.strptime(past_today_greater_hold_end, date_time_formate_string)
                 
                except Exception as e:
                    None
                
                    # print(f"An unexpected error occurred: {e}")
                
                try:
                    if past_today_greater_end_end > past_today_greater_hold_end:
                            days_hold_greater = True
                            past_today_greater = past_hold_t1

                except Exception as e:
                    None
                
                    # print(f"An unexpected error occurred: {e}")
                
                try:
                    if  past_today_greater_end_end < past_today_greater_hold_end:
                            days_hold_greater = False
                            past_today_greater = past_end_t2

                except Exception as e:
                    None
                
                    # print(f"An unexpected error occurred: {e}")
                try:
                    if  (past_today_greater_end_end==None) and  (past_today_greater_hold_end!=None):
                            days_hold_greater = True
                            past_today_greater = past_end_t2
                except Exception as e:
                    None
                
                    # print(f"An unexpected error occurred: {e}")
                try:
                    if  (past_today_greater_hold_end==None) and  (past_today_greater_end_end!=None):
                            days_hold_greater = False
                            past_today_greater = past_hold_t1
                except Exception as e:
                
                    None
                    # print(f"An unexpected error occurred: {e}")
                # datetime.strptime(str(past_today_greater_end_end), date_time_formate_string)
                # datetime.strptime(str(past_today_greater_hold_end), date_time_formate_string)

                
                # print(past_end_t2,'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
#----------------------------------------------------------------------------------------------------   timing code for past today start
    

 
                if str(current_time_report.date()) == date:
                
                        print('current date.........................................................................................')


                        db_res2h = db.query(models.HOLD).filter(
                            models.HOLD.Service_ID == row.Service_ID,
                            models.HOLD.hold_time_start.like(f"%{date}%"),

                        )
                        # print(db_res2h.count(),'.....................................................................................')

                        for row2 in db_res2h.all():
                            if hold_time_report != None:
                                if row2.hold_time_end and row2.hold_time_start:
                                    date_time11 = datetime.strptime(row2.hold_time_end, date_time_formate_string)
                                    date_time22 = datetime.strptime(row2.hold_time_start, date_time_formate_string)
                                    time_diff = date_time11 - date_time22
                                    hold_time_report += time_diff
                                else :
                                    if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                                        time1 =  datetime.now() - datetime.strptime(row2.hold_time_start, date_time_formate_string)
                                        hold_time_report +=  time1
                            else:
                                if row2.hold_time_end and row2.hold_time_start:
                                    date_time11 = datetime.strptime(row2.hold_time_end, date_time_formate_string)
                                    date_time22 = datetime.strptime(row2.hold_time_start, date_time_formate_string)
                                    time_diff = date_time11 - date_time22
                                    hold_time_report = time_diff
                                else :
                                    if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                                        time1 =  datetime.now() - datetime.strptime(row2.hold_time_start, date_time_formate_string)
                                        hold_time_report =  time1

                        data["hold"] = hold_time_report
                        
        #----------------------- hold code completed



                        # ----- Break Hour ------
                        db_res2 = db.query(models.BREAK).filter(
                            models.BREAK.Service_ID == row.Service_ID,
                            models.BREAK.break_time_start.like(f"%{date}%"),

                        ).all()



                        for row2 in db_res2:
                            if break_time_report != None:
                                if row2.break_time_end and row2.break_time_start:
                                    date_time11 = datetime.strptime(row2.break_time_end, date_time_formate_string)
                                    date_time22 = datetime.strptime(row2.break_time_start, date_time_formate_string)
                                    time_diff = date_time11 - date_time22
                                    break_time_report += time_diff
                                else :
                                    if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                                        time1 =  datetime.now() - datetime.strptime(row2.break_time_start, date_time_formate_string)
                                    
                                        break_time_report += time1
                            else:
                                if row2.break_time_end and row2.break_time_start:
                                    date_time11 = datetime.strptime(row2.break_time_end, date_time_formate_string)
                                    date_time22 = datetime.strptime(row2.break_time_start, date_time_formate_string)
                                    time_diff = date_time11 - date_time22
                                    # print(type(time_diff),type(break_time_report),'ffffffffffffffffffffffffffffffffffffffffffffffffffffffffff')
                                    break_time_report = time_diff
                                else :
                                    if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                                        time1 =  datetime.now() - datetime.strptime(row2.break_time_start, date_time_formate_string)
                                    
                                        break_time_report = time1

                        data["break"] = break_time_report

        #------------------------- break code completed


                        # ----- Meeting Hour ------
                        db_res2 = db.query(models.MEETING).filter(
                            models.MEETING.Service_ID == row.Service_ID,
                            models.MEETING.meeting_time_start.like(f"%{date}%"),

                        ).all()

                        

                        for row2 in db_res2:
                            if meeting_time_report != None:
                                if row2.meeting_time_end and row2.meeting_time_start:
                                    date_time11 = datetime.strptime(row2.meeting_time_end, date_time_formate_string)
                                    date_time22 = datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                                    time_diff = date_time11 - date_time22
                                    meeting_time_report += time_diff
                                else :
                                    if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                                        time1 =  datetime.now() - datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                                        meeting_time_report +=   time1
                            else:
                                if row2.meeting_time_end and row2.meeting_time_start:
                                    date_time11 = datetime.strptime(row2.meeting_time_end, date_time_formate_string)
                                    date_time22 = datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                                    time_diff = date_time11 - date_time22
                                    meeting_time_report = time_diff
                                else :
                                    if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                                        time1 =  datetime.now() - datetime.strptime(row2.meeting_time_start, date_time_formate_string)
                                        meeting_time_report =   time1                        


                        data["meeting"] = meeting_time_report

        #--------------------- meeting code end

                        db_res2 = db.query(models.CALL).filter(
                            models.CALL.Service_ID == row.Service_ID,
                            models.CALL.call_time_start.like(f"%{date}%"),

                        ).all()

                        

                        for row2 in db_res2:
                            if call_time_report != None:
                                if row2.call_time_end and row2.call_time_start:
                                    date_time11 = datetime.strptime(row2.call_time_end, date_time_formate_string)
                                    date_time22 = datetime.strptime(row2.call_time_start, date_time_formate_string)
                                    time_diff = date_time11 - date_time22
                                    call_time_report += time_diff
                                else :
                                    if not(row.work_status == "Completed" or row.work_status == "in_progress"):

                                        time1 =  datetime.now() - datetime.strptime(row2.call_time_start, date_time_formate_string)
                                    
                                        call_time_report += time1
                            else:
                                if row2.call_time_end and row2.call_time_start:
                                    date_time11 = datetime.strptime(row2.call_time_end, date_time_formate_string)
                                    date_time22 = datetime.strptime(row2.call_time_start, date_time_formate_string)
                                    time_diff = date_time11 - date_time22
                                    call_time_report = time_diff
                                else :
                                    if not(row.work_status == "Completed" or row.work_status == "in_progress"):
                                        time1 =  datetime.now() - datetime.strptime(row2.call_time_start, date_time_formate_string)
                                    
                                        call_time_report = time1
                        data["call"] = call_time_report

        #------------------------------ call code end

                else:
                    

                    

                        query = db.query(models.HOLD).filter(
                            models.HOLD.Service_ID == row.Service_ID,
                            models.HOLD.hold_time_start.like(f"%{date}%"),
                            models.HOLD.hold_time_end.like(f"%{date}%")
                        )
                        for nq in query.all():
                                if hold_time_report != None:
                                    hold_time_report = hold_time_report+time_difference(datetime.strptime(nq.hold_time_end, date_time_formate_string),datetime.strptime(nq.hold_time_start, date_time_formate_string))
                                else:
                                    hold_time_report = time_difference(datetime.strptime(nq.hold_time_end, date_time_formate_string),datetime.strptime(nq.hold_time_start, date_time_formate_string))
                                
                                if 1==1:

                                    h1_start = nq.hold_time_start
                                    h2_end = nq.hold_time_end
                                    print((nq.hold_time_end),nq.hold_time_start,'bharath ...................................................................................................')
                                    # Convert the strings to datetime objects
                                    start_time = datetime.strptime(nq.hold_time_start, "%Y-%m-%d %H:%M:%S")
                                    end_time = datetime.strptime(nq.hold_time_end, "%Y-%m-%d %H:%M:%S")

                                    # Calculate the difference
                                    time_differenced = end_time - start_time

                                    # Get the total seconds from the time difference
                                    total_seconds = int(time_differenced.total_seconds())

                                    # Calculate hours, minutes, and seconds
                                    hours, remainder = divmod(total_seconds, 3600)
                                    minutes, seconds = divmod(remainder, 60)

                                    # Print the result
                                    print(f"Time Difference: {hours} hours, {minutes} minutes, and {seconds} seconds")
                        data['hold'] = hold_time_report

                        print(hold_time_report,'today-s hold time ...........................................................')


                    # try:                    
                        query = db.query(models.BREAK).filter(
                            models.BREAK.Service_ID == row.Service_ID,
                            models.BREAK.break_time_start.like(f"%{date}%"),
                            models.BREAK.break_time_end.like(f"%{date}%")
                        )

                        for nq in query.all():
                            if break_time_report != None:
                                break_time_report = break_time_report+time_difference(datetime.strptime(nq.break_time_end, date_time_formate_string),datetime.strptime(nq.break_time_start, date_time_formate_string))
                            else:
                                break_time_report = time_difference( datetime.strptime(nq.break_time_end, date_time_formate_string),datetime.strptime(nq.break_time_start, date_time_formate_string))

                        data['break'] = break_time_report

                        print(break_time_report,'today-s break time ...........................................................')

                    # except Exception as e:
                    
                    #     print(f"An unexpected error occurred: {e}")

                    # try:                    
                        query = db.query(models.MEETING).filter(
                            models.MEETING.Service_ID == row.Service_ID,
                            models.MEETING.meeting_time_start.like(f"%{date}%"),
                            models.MEETING.meeting_time_end.like(f"%{date}%")
                        )
                        for nq in query.all():
                            if meeting_time_report != None:
                                meeting_time_report = meeting_time_report+time_difference(datetime.strptime(nq.meeting_time_end, date_time_formate_string),datetime.strptime(nq.meeting_time_start, date_time_formate_string))
                            else:
                                meeting_time_report = time_difference(datetime.strptime(nq.meeting_time_end, date_time_formate_string),datetime.strptime(nq.meeting_time_start, date_time_formate_string))

                        data['meeting'] = meeting_time_report    


                        print(meeting_time_report,'today-s meeting time ...........................................................')

                    # except Exception as e:
                    
                    #     print(f"An unexpected error occurred: {e}")

                    # try:                    
                        query = db.query(models.CALL).filter(
                            models.CALL.Service_ID == row.Service_ID,
                            models.CALL.call_time_start.like(f"%{date}%"),
                            models.CALL.call_time_end.like(f"%{date}%")
                        )

                        for nq in query.all():
                            if call_time_report != None:
                                call_time_report = call_time_report+time_difference(datetime.strptime(nq.call_time_end, date_time_formate_string),datetime.strptime(nq.call_time_start, date_time_formate_string))
                            else:
                                call_time_report = time_difference(datetime.strptime(nq.call_time_end, date_time_formate_string),datetime.strptime(nq.call_time_start, date_time_formate_string))

                        data['call'] = call_time_report

                        print(call_time_report,'today-s call time ...........................................................')

                    # except Exception as e:
                    
                    #     print(f"An unexpected error occurred: {e}")

                
                if hold_time_report!=None :
                        if totalminus  == None:
                            totalminus = hold_time_report
                        else: 
                            totalminus = totalminus+hold_time_report
                
                if  break_time_report!=None:
                        if totalminus  == None:
                            totalminus = break_time_report
                        else: 
                            totalminus = totalminus+break_time_report

                if  meeting_time_report!=None:
                        if totalminus  == None:
                            totalminus = meeting_time_report
                        else: 
                            totalminus = totalminus+meeting_time_report

                if  call_time_report!=None:
                        if totalminus  == None:
                            totalminus = call_time_report
                        else: 
                            totalminus = totalminus+call_time_report
#----------------------------------------------------------------------------------------------------- timing code


#---------------------------------------------------------- calculation code
                livedayreportend = None
                try:

                    livedayreportend = datetime.strptime(old_end, date_time_formate_string).date()==current_time_report.date()
                except:
                    livedayreportend = False

                if completed_time_report:
                    
                    if completed_time_report.date() == working_time_report.date():
                        print('completed time == working time..........................................................')
                        timei1 = working_time_report
                        timei2 = completed_time_report
                        timediff_f2 = time_difference(timei2,timei1)

                        try:  
                            Totaltime = timediff_f2 - totalminus
                            data['completed'] = Totaltime
                            # print(type(timediff_f2),'ddddddddddddddddddddddddddddddddddddddddd')
                        except Exception as e:
                            # print(type(timediff_f2),'ddddddddddddddddddddddddddddddddddddddddd')
                            data['completed'] = timediff_f2
                            # print(f"An unexpected error occurred: {e}")

                        # print(Totaltime,'same day')
                    elif (str(working_time_report.date()) == date) and (completed_time_report.date() > working_time_report.date()):
                            print('completed time not equal to working time == date..........................................................................')
                            timei1 = working_time_report
                            timei2 = past_today_greater
                            # print(timei1,timei2,'fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff')
                            timediff_f2 = time_difference(datetime.strptime(timei2, date_time_formate_string),timei1)
                            
                            try:  
                                Totaltime = timediff_f2 - totalminus
                                data['completed'] = Totaltime
                            except Exception as e:
                                data['completed'] = timediff_f2
                                # print(f"An unexpected error occurred: {e}")

                    elif (str(completed_time_report.date()) == date):
                            print('completed time is today .........................................................')
                            timei1 = old_end
                            timei2 = completed_time_report
                            # print(type(timei1),type(timei2),'hellllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll')
                            timediff_f2 = time_difference(timei2,datetime.strptime(timei1, date_time_formate_string))
                            # print(timediff_f2,'ggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg')

                            try:  
                                Totaltime = timediff_f2 - totalminus
                                data['completed'] = Totaltime
                            except Exception as e:
                                data['completed'] = timediff_f2
                                print(f"An unexpected error occurred: {e}")

                    else:
                        print('in between day of completed time')
                        timei1 = old_end
                        timei2 = past_today_greater
                        # print(type(timei1),type(timei2),'kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
                        timediff_f2 = time_difference(datetime.strptime(timei2, date_time_formate_string),datetime.strptime(timei1, date_time_formate_string))

                        

                        try:  
                            Totaltime = timediff_f2 - totalminus
                            data['completed'] = Totaltime
                        except Exception as e:
                            data['completed'] = timediff_f2
                            # print(f"An unexpected error occurred: {e}")

                        
                elif  (old_end != None) and livedayreportend:
                        print('old_end == current day ....................................................................',current_time_report,old_end)
                        timei1 = current_time_report
                        timei2 = old_end
                        timei3 = past_today_greater
                        print(timei1,timei2,timei3,'.......................................................oooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo')


                        if timei3 and row.work_status == 'Work in Progress':
                            timediff_f2 = time_difference(timei1,timei2)

                            # print(timei1,timei2,timei3,timediff_f2,'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
                            try:  
                                Totaltime = timediff_f2 - totalminus
                                data['in_progress'] = Totaltime
                                
                            except Exception as e:
                                data['in_progress'] = timediff_f2
                        elif timei3 and row.work_status == 'Completed':
                            timediff_f2 = time_difference(timei3,timei2)

                            print(totalminus,'lllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll')
                            try:  
                                Totaltime = timediff_f2 #- totalminus
                                data['in_progress'] = Totaltime
                                
                            except Exception as e:
                                data['in_progress'] = timediff_f2
                        elif row.work_status == 'End Of Day':
                            timediff_f2 = time_difference(timei3,timei2)

                            print(timediff_f2,totalminus,'lllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllllll')
                            
                            try:  
                                Totaltime = timediff_f2 - totalminus
                                data['in_progress'] = Totaltime
                                
                            except Exception as e:
                                data['in_progress'] = timediff_f2
                        else:
                            timediff_f2 = time_difference(timei1,timei2)

                            
                            try:  
                                Totaltime = timediff_f2 - totalminus
                                data['in_progress'] = Totaltime
                                
                            except Exception as e:
                                data['in_progress'] = timediff_f2
                            

                elif (working_time_report.date()==current_time_report.date()) and past_end_t2!=None:
                        print('(working_time_report == current_time_report) and past_today_greater -not completed............................................')
                        timei1 = working_time_report
                        timei2 =  past_end_t2
                        timediff_f2 = time_difference(timei2,timei1)

                        # print(timei1,timei2,'uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu')
                        try:  
                            Totaltime = timediff_f2 - totalminus
                            data['in_progress'] = Totaltime
                            # print("1111111111111111111111111111111111111111111111111111")
                        except Exception as e:
                            data['in_progress'] = timediff_f2
                            # print("2222222222222222222222222222222222222222")
                            # print(f"An unexpected error occurred: {e}")
                        # print(Totaltime,'sameday not finished')

                elif working_time_report.date()==current_time_report.date():
                        print('working_time_report == current_time_report not completed............................................')
                        timei1 = working_time_report
                        timei2 = current_time_report
                        timediff_f2 = time_difference(timei2,timei1)

                        # print(timei1,timei2,'uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu')
                        try:  
                            Totaltime = timediff_f2 - totalminus
                            data['in_progress'] = Totaltime
                            # print("1111111111111111111111111111111111111111111111111111")
                        except Exception as e:
                            data['in_progress'] = timediff_f2
                            # print("2222222222222222222222222222222222222222")
                            # print(f"An unexpected error occurred: {e}")
                        # print(Totaltime,'sameday not finished')
                elif (working_time_report.date()!=current_time_report.date()) and (str(current_time_report.date()) == date):
                        print('working_time_report != current_time_report not completed............................................')
                        timei1 = working_time_report
                        timei2 = current_time_report
                        timediff_f2 = time_difference(timei2,timei1)

                        # print(timei1,timei2,'uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu')
                        try:  
                            Totaltime = timediff_f2 - totalminus
                            data['in_progress'] = Totaltime
                            # print("1111111111111111111111111111111111111111111111111111")
                        except Exception as e:
                            data['in_progress'] = timediff_f2
                            # print("2222222222222222222222222222222222222222")
                            # print(f"An unexpected error occurred: {e}")
                        # print(Totaltime,'sameday not finished')

                elif (str(working_time_report.date())== date) and completed_time_report==None:
                        print('working time ==date not completed..................................................................')
                        timei1 = working_time_report
                        timei2 = past_today_greater
                        print(timei1,timei2,time_difference(timei2,timei1),'lkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk')
                        timediff_f2 = time_difference(timei2,timei1)
                        print(totalminus,'today.......................................................................................................................eeeeeee')
                        if totalminus!=None:
                            if((timediff_f2 - totalminus) < timedelta(0)):
                                try:  
                                    Totaltime = timediff_f2 
                                    data['in_progress'] = timedelta(0)
                                    # print("1111111111111111111111111111111111111111111111111111")
                                except Exception as e:
                                    data['in_progress'] = timedelta(0)
                                    # print("2222222222222222222222222222222222222222")
                                    # print(f"An unexpected error occurred: {e}")
                                # print(Totaltime,'sameday not finished')
                            else:
                                try:  
                                    Totaltime = timediff_f2 - totalminus
                                    data['in_progress'] = Totaltime
                                    # print("1111111111111111111111111111111111111111111111111111")
                                except Exception as e:
                                    data['in_progress'] = timediff_f2
                                    # print("2222222222222222222222222222222222222222")
                                    # print(f"An unexpected error occurred: {e}")
                                # print(Totaltime,'sameday not finished')
                        else:     
                        # print(timei1,timei2,'uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu')
                            try:  
                                Totaltime = timediff_f2 - totalminus
                                data['in_progress'] = Totaltime
                                # print("1111111111111111111111111111111111111111111111111111")
                            except Exception as e:
                                data['in_progress'] = timediff_f2
                                # print("2222222222222222222222222222222222222222")
                                # print(f"An unexpected error occurred: {e}")
                            # print(Totaltime,'sameday not finished')

                elif (str(working_time_report.date())!= date and (old_end!=None and past_today_greater!= None)) and (completed_time_report==None and str(current_time_report.date())!=date):
                        print('working time != today, current time != date , not completed...........................')
                        timei1 = old_end
                        timei2 = past_today_greater
                        print(timei1,timei2,totalminus,'ggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggg')
                        timediff_f2 = time_difference(datetime.strptime(timei2, date_time_formate_string),datetime.strptime(timei1, date_time_formate_string))

                        # print(timei1,timei2,'uuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu')
                        try:  
                            Totaltime = timediff_f2 - totalminus
                            data['in_progress'] = Totaltime
                            # print("1111111111111111111111111111111111111111111111111111")
                        except Exception as e:
                            data['in_progress'] = timediff_f2
                            # print("2222222222222222222222222222222222222222")
                            # print(f"An unexpected error occurred: {e}")
                        # print(Totaltime,'sameday not finished')

                elif old_end :
                    try:
                        if old_hold_start_time and old_end_start_time:
                            
                            if (old_hold_start_time > old_end_start_time) and (old_end.date() == current_time_report.date()) :
                                print('old_hold_start_time > old_end_start_time , old_end == current date .................................')
                                timei1 = current_time_report
                                timei2 = old_end
                                timediff_f2 = time_difference(timei1,timei2)

                                print(timediff_f2,'ffffffffffffffffffffffffffffffffffffffffffffffffffffff')
                                try:  
                                    Totaltime = timediff_f2 - totalminus
                                    data['in_progress'] = Totaltime
                                    # print("333333333333333333333333333333333333333333333333")
                                except Exception as e:
                                    data['in_progress'] = timediff_f2
                                    # print("4444444444444444444444444444444444444444444")

                                    # print(f"An unexpected error occurred: {e}")
                                # print(Totaltime,'sameday not finished')
                                # print(Totaltime,'hold')
                            
                            elif (old_hold_start_time < old_end_start_time) and (old_end.date() == current_time_report.date()):
                                print('old_hold_start_time < old_end_start_time , old_end == current date .................................')
                                timei1 = current_time_report
                                timei2 = old_end
                            
                                timediff_f2 = time_difference(timei1,timei2)

                                
                                try:  
                                    Totaltime = timediff_f2 - totalminus
                                    data['in_progress'] = Totaltime
                                    # print("55555555555555555555555555555555555555555")

                                except Exception as e:
                                    data['in_progress'] = timediff_f2
                                    # print("666666666666666666666666666666666666666666666666666")

                                    # print(f"An unexpected error occurred: {e}")
                                # print(Totaltime,'sameday not finished')
                                
                        elif old_end_start_time and (old_end.date() == current_time_report.date()):
                            print('old_end_start_time!= none ,  old_end == current date .................................')
                            timei1 = current_time_report
                            timei2 = old_end
                        
                            timediff_f2 = time_difference(timei1,timei2)

                            
                            try:  
                                Totaltime = timediff_f2 - totalminus
                                data['in_progress'] = Totaltime
                                # print("777777777777777777777777777777777777777777777777")

                            except Exception as e:
                                data['in_progress'] = timediff_f2
                                # print("8888888888888888888888888888888888888888888888888888")

                                # print(f"An unexpected error occurred: {e}")
                            # print(Totaltime,'sameday not finished')
                        
                        elif old_hold_start_time and (datetime.strptime(old_end, date_time_formate_string).date() == current_time_report.date()):
                                print('old_hold_start_time!= none ,  old_end == current date .................................')
                                timei1 = current_time_report
                                timei2 = datetime.strptime(old_end, date_time_formate_string)
                                # print(timei1,timei2,'hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh')
                                timediff_f2 = time_difference(timei1,timei2)
            
                                
                                try:  
                                    Totaltime = timediff_f2 - totalminus
                                    data['in_progress'] = Totaltime
                                    # print("99999999999999999999999999999999")

                                except Exception as e:
                                    data['in_progress'] = timediff_f2
                                    # print("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")

                                    # print(f"An unexpected error occurred: {e}")
                                # print(Totaltime,'sameday not finished')
                    except:
                        None 

 
                try:

                    if completed_time_report!=None:

                        if (past_today_greater!=None) and (past_today_greater.date()!=current_time_report.date())   and (completed_time_report.date()!=past_today_greater.date()):

                                    print('past_today_greater!=None , past_today_greater not equal to current time report, completed_time_report != past_today_greater..................')
                                    timei1 = past_today_greater
                                    timei2 = old_end
                                    timediff_f2 = time_difference(timei1,timei2)


                                    try:  
                                        Totaltime = timediff_f2 - totalminus
                                        data['in_progress'] = Totaltime
                                        # print("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")

                                    except Exception as e:
                                        data['in_progress'] = timediff_f2
                                        # print("ccccccccccccccccccccccccccccccccccccccc")

                                        # print(f"An unexpected error occurred: {e}")
                                    # print(Totaltime,'sameday not finished')

                                

                    else:

                        if (past_today_greater!=None) and (past_today_greater.date()!=current_time_report.date()):

                                    print('past_today_greater!=None , past_today_greater!= current time .......................................................................')
                                    timei1 = past_today_greater
                                    timei2 = old_end
                                    timediff_f2 = time_difference(timei1,timei2)


                                    try:  
                                        Totaltime = timediff_f2 - totalminus
                                        data['in_progress'] = Totaltime
                                        # print("ddddddddddddddddddddddddddddddddddd")

                                    except Exception as e:
                                        data['in_progress'] = timediff_f2
                                        # print("eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee")

                                        # print(f"An unexpected error occurred: {e}")

                                

                except Exception as e:
                    None
                
                print('finisheddddddddddddddddddddddddddddddd........................................................................................................')


#---------------------------------calculation code

                str_temp = ""
                str_temper = ""
                
                data["third_report_data"] = None
                db_res3 = db.query(models.HOLD).filter(
                        models.HOLD.Service_ID == row.Service_ID,
                    ).all()
                for hold_obj in db_res3:
                        if data["third_report_data"] != None :
                            data["third_report_data"] = data["third_report_data"] + " , "+ hold_obj.remarks
                        else:
                            data["third_report_data"] = hold_obj.remarks
                        

                if row.work_status == "Work in Progress":

                    None

                # elif row.work_status == "Hold":

                #     db_res3 = db.query(models.HOLD).filter(
                #         models.HOLD.Service_ID == row.Service_ID,
                #     ).all()
                #     for hold_obj in db_res3:
                #         data["third_report_data"] = hold_obj.remarks
                #         str_temper = hold_obj.remarks

                elif row.work_status == "Meeting":

                    db_res3 = db.query(models.MEETING).filter(
                        models.MEETING.Service_ID == row.Service_ID,
                    ).all()
                    for meet_obj in db_res3:
                        
                        str_temper = meet_obj.remarks

                elif row.work_status == "Break":
                    db_res3 = db.query(models.BREAK).filter(
                        models.BREAK.Service_ID == row.Service_ID,
                    ).all()
                    for break_obj in db_res3:
                      
                        
                        str_temper = break_obj.remarks
                        
                elif row.work_status == "Clarification Call":
                    db_res3 = db.query(models.CALL).filter(
                        models.CALL.Service_ID == row.Service_ID,
                    ).all()
                    for call_obj in db_res3:
                      
                        
                        str_temper = call_obj.remarks

                elif row.work_status == "Completed":
                    
                    str_temper = row.remarks


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

                # hold_time_report = None
                # break_time_report = None
                # meeting_time_report = None
                # call_time_report = None
                # print(str(hold_time_report),break_time_report,call_time_report,meeting_time_report)
                # try:
                #     date['hold'] = str(hold_time_report)
                # except:
                #         None
                # try:
                #     date['break'] = str(break_time_report)
                # except:
                #         None
                # try:
                #     date['call'] = str(call_time_report)
                # except:
                #         None
                # try:
                #     date['meeting'] = str(meeting_time_report)
                # except:
                #         None
                # 'in_progress' 
                # data['completed'] = Totaltime
                # print(data['completed'],'9999999999999999999999999999999999999999999999999999999999')
                # print(old_hold_for_total,'tftftftftftftftftftftftftftftftftftftftftftftftftftftftftftftftftf')

#------------------------------------------------------ hold total calculation
                if 1==1:
                    total_hold_morning1 = None
                    total_hold_evening1 = None
                    if str(current_time_report.date()) == date:
                        
                        if old_hold_for_total:
                            date_obj = datetime.strptime(date, "%Y-%m-%d")

                            # Subtract one day using timedelta
                            one_day_back = date_obj - timedelta(days=1)

                            # Convert back to string if needed
                            new_date_str = one_day_back.strftime("%Y-%m-%d")

                            querygg = db.query(models.HOLD).filter(
                                models.HOLD.Service_ID == row.Service_ID,
                                models.HOLD.hold_time_start.like(f"%{new_date_str}%"),
                                models.HOLD.hold_time_end.like(f"%{date}%"),
                            )

                            if querygg:
                                nu = querygg.count()
                                re = querygg.all()
                                total_hold_morning1 = re[0].hold_time_end
                                print(re[0].hold_time_end, query.count(),str(date))
                            print(reset_to_midnight_and_get_timedelta(total_hold_morning1))
                            if data['hold'] == None:
                                    data['hold'] =  reset_to_midnight_and_get_timedelta(total_hold_morning1)
                            else :
                                    data['hold'] = data['hold'] + reset_to_midnight_and_get_timedelta(total_hold_morning1)
                    else :
                        if old_hold_for_total:
                            date_obj = datetime.strptime(date, "%Y-%m-%d")

                            # Subtract one day using timedelta
                            one_day_back = date_obj - timedelta(days=1)

                            # Convert back to string if needed
                            new_date_str = one_day_back.strftime("%Y-%m-%d")

                            querygg = db.query(models.HOLD).filter(
                                models.HOLD.Service_ID == row.Service_ID,
                                models.HOLD.hold_time_start.like(f"%{new_date_str}%"),
                                models.HOLD.hold_time_end.like(f"%{date}%"),
                            )

                            if querygg:
                                nu = querygg.count()
                                re = querygg.all()
                                total_hold_morning1 = re[0].hold_time_end
                                print(re[0].hold_time_end, query.count(),str(date))
                            print(reset_to_midnight_and_get_timedelta(total_hold_morning1))
                            
                            if data['hold'] == None:
                                    data['hold'] =  reset_to_midnight_and_get_timedelta(total_hold_morning1)
                            else :
                                    data['hold'] = data['hold'] + reset_to_midnight_and_get_timedelta(total_hold_morning1)
                        
                        if past_today_greater_end_start !=None and past_today_greater_hold_start !=None:
                            try:
                                print(str(completed_time_report.date()),date,'dateeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
                                if row.work_status == 'Completed' and (str(completed_time_report.date())!=date):
                                    if past_today_greater_end_start < past_today_greater_hold_start :
                                        future_time, time_differenceh = time_differencet(past_today_greater_hold_start)
                                        print(time_differenceh,'appppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp')


                                        if data['hold'] == None:
                                            data['hold'] = time_differenceh
                                        else :
                                            data['hold'] = data['hold'] + time_differenceh
                            except :
                                None
                            if row.work_status != 'Completed':
                                if past_today_greater_end_start < past_today_greater_hold_start :
                                        future_time, time_differenceh = time_differencet(past_today_greater_hold_start)
                                        print(time_differenceh,'bppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp')


                                        if data['hold'] == None:
                                            data['hold'] = time_differenceh
                                        else :
                                            data['hold'] = data['hold'] + time_differenceh
                        elif past_today_greater_end_start == None:
                                try:

                                    print(str(completed_time_report.date()),date,'dateeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee')
                                    
                                    if row.work_status == 'Completed' and (str(completed_time_report.date())!=date):
                                        future_time, time_differenceh = time_differencet(past_today_greater_hold_start)
                                        print(time_differenceh,'cppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp')

                                        if data['hold'] == None:
                                            data['hold'] = time_differenceh
                                        else :
                                            data['hold'] = data['hold'] + time_differenceh
                                except :
                                    None
                                
                                if row.work_status != 'Completed':
                                    
                                        future_time, time_differenceh = time_differencet(past_today_greater_hold_start)
                                        print(time_differenceh,'dppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp')

                                        if data['hold'] == None:
                                            data['hold'] = time_differenceh
                                        else :
                                            data['hold'] = data['hold'] + time_differenceh
                        print(past_today_greater_end_start,past_today_greater_hold_start,h1_start,h2_end,'jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj')
                    # print(old_hold_t1,h1_start,h2_end)
                    # if past_today_greater_end_start == None:
                    #     print((reset_to_midnight_and_get_timedelta(h1_start)),'ppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp')
                    
                    # if h1_start and h2_end:
                    #     future_time, time_differenceh = time_differencet(h2_end)
                    #     print((reset_to_midnight_and_get_timedelta(h1_start)),time_differenceh,'ppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp')

                    # print(past_today_greater_end_start,past_today_greater_hold_start,'jjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjjj')
                    
                    # print(old_hold_t1,old_hold_for_total,days_hold_greater)
                    # if old_hold_t1 or old_hold_for_total:
                    #     print('true..................................................................................................................')
                    # print(old_hold_for_total ,'pasupathi////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////')
                    # future_time, time_differenceh = time_differencet(h2_end)
                    # print((reset_to_midnight_and_get_timedelta(h1_start)),time_differenceh,'ppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppppp')

                    None
                
                total_hold_morning = None
                total_hold_evening = None
                if old_hold_for_total:
                        
                    try:
                        query = db.query(models.HOLD).filter(
                            models.HOLD.Service_ID == row.Service_ID,
                            models.HOLD.hold_time_end.like(f"%{date}%"),
                        )

                        if query:
                            nu = query.count()
                            re = query.all()
                            print(re[0].hold_time_end, query.count())
                           
                            dt_obj = datetime.strptime(re[0].hold_time_end, "%Y-%m-%d %H:%M:%S")

                            # Extract and format the time part
                            time_str = dt_obj.strftime("%H:%M:%S")

                            

                            time_format = "%H:%M:%S"
                            time1 = datetime.strptime(time_str, time_format)
                            

                            # Calculate the timedelta for each time
                            delta1 = timedelta(hours=time1.hour, minutes=time1.minute, seconds=time1.second)
                            

                            total_hold_morning = delta1 

                            
                            
                            
                        else:
                            None

                           
                    except Exception as e:
                        None
                    


                queryeod = db.query(models.END_OF_DAY).filter(
                    models.END_OF_DAY.Service_ID == row.Service_ID,
                    models.END_OF_DAY.end_time_start.like(f"%{date}%"),
                )

            
                if (date != str(datetime.today().date())) and (queryeod.count()==0):
                        
                        try:
                            
                            query = db.query(models.HOLD).filter(
                                models.HOLD.Service_ID == row.Service_ID,
                                func.date(models.HOLD.hold_time_start) == date,
                                
                            )

                            

                            if query:
                                nu = query.count()
                                re = query.all()
                                
                                datetime_str = re[nu-1].hold_time_start
                                given_datetime = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")

                                # End of the day (23:59:59 on the same date)
                                end_of_day = given_datetime.replace(hour=23, minute=59, second=59)

                                # Calculate the remaining time
                                remaining_time = end_of_day - given_datetime
                                total_hold_evening = remaining_time
                               
                                
                               
                                
                            else:
                                print("No hold record found for Service_ID 14")
                        except Exception as e:
                            None



                # print(total_hold_morning,total_hold_evening,'problem' )
                # for dt in [total_hold_morning, total_hold_evening]:
                #         if dt is not None:
                #             if data['hold'] == None:
                #                 data['hold'] = dt
                #             else :
                #                 data['hold'] = dt + data['hold']
#------------------------------------------------------ hold total calculation
                data["fourth_report"] = row.no_of_items
                data["fourth_report2"] = str_temp
                data["fifth_report"] = str_temper                    
                list_data.append(data)

                if idealname !='':

                    hoursidel, minutesidel , secondsidel= map(int, crud.calculate_work_hours(idealname, date, db).split(':'))

                    time_deltaidel = timedelta(hours=hoursidel, minutes=minutesidel, seconds=secondsidel)

                    for tmtime in [data['break'],data['call'],data['meeting'],data['hold'],data['in_progress'],data['completed']]:
                            if tmtime :
                                 time_deltaidel =  time_deltaidel - tmtime
                                 print(crud.calculate_work_hours(idealname, date, db),'first',time_deltaidel ,'sec', tmtime,'ideal ideal /////////////////////////////////////////////////////////////////////////////////////////////////////////')
                    data["idealname"] = time_deltaidel
                print(past_today_greater_hold_end,old_end_start_time,'llllllllllllllllllllllluuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuuu')
                print(old_hold_t1,'<old hold',old_end,old_hold_for_total,"=tgggggggggg>>>>>>>>>>>>>>>>>>>>>>>") 
                print(past_today_greater_end_end, past_today_greater_hold_end, past_hold_t1, past_end_t2, past_today_greater, "=>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                
            return list_data
#----------------------------------------------------------------------------


def common( db : Session , date : str , dataoptiopns   , option : str , statusdata : str):
            # dataoptiopns means entity , scope and sub scobe option means which report , statusdata means chargable or non-chargable
        # print(dataoptiopns,'000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000')
        
        if option == "userlist" and statusdata == 'CHARGABLE':
            
            list_ddata1 = set()


            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.Assigned_To == dataoptiopns,
                models.TL.status == 1,
                models.TL.working_time.like(f"%{date}%")    
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.Assigned_To == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.HOLD.Service_ID,
                or_(
                    models.HOLD.hold_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
            
            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.Assigned_To == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.END_OF_DAY.Service_ID,
                or_(
                    models.END_OF_DAY.end_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
                

        # final query
            newquery =  db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.Assigned_To == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID.in_(list_ddata1)
            ).all()

            
            
            
            return commoncalculation(db,newquery, date)
            
        elif option == "userlist" and statusdata == 'Non-Charchable':

            list_ddata1 = set()

           

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.Assigned_To == dataoptiopns,
                models.TL.status == 1,
                models.TL.working_time.like(f"%{date}%")    
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.Assigned_To == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.HOLD.Service_ID,
                or_(
                    models.HOLD.hold_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
            
            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.Assigned_To == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.END_OF_DAY.Service_ID,
                or_(
                    models.END_OF_DAY.end_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
                

        # final query
            newquery =  db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.Assigned_To == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID.in_(list_ddata1)
            ).all()

            
            
            return commoncalculation(db,newquery, date)
        
        elif option == "entitylist"  and statusdata == 'CHARGABLE':

            list_ddata1 = set()

           

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.name_of_entity == dataoptiopns,
                models.TL.status == 1,
                models.TL.working_time.like(f"%{date}%")    
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.name_of_entity == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.HOLD.Service_ID,
                or_(
                    models.HOLD.hold_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
            
            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.name_of_entity == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.END_OF_DAY.Service_ID,
                or_(
                    models.END_OF_DAY.end_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
                

        # final query
            newquery =  db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.name_of_entity == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID.in_(list_ddata1)
            ).all()

            
            
            return commoncalculation(db,newquery, date)
        elif option == "entitylist"  and statusdata == 'Non-Charchable':
            
            list_ddata1 = set()

           

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.name_of_entity == dataoptiopns,
                models.TL.status == 1,
                models.TL.working_time.like(f"%{date}%")    
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.name_of_entity == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.HOLD.Service_ID,
                or_(
                    models.HOLD.hold_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
            
            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.name_of_entity == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.END_OF_DAY.Service_ID,
                or_(
                    models.END_OF_DAY.end_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
                

        # final query
            newquery =  db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.name_of_entity == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID.in_(list_ddata1)
            ).all()

            
            
            return commoncalculation(db,newquery, date)


        elif option == "scopelist" and statusdata == 'CHARGABLE':
            

          
            list_ddata1 = set()

           

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.Scope == dataoptiopns,
                models.TL.status == 1,
                models.TL.working_time.like(f"%{date}%")    
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.Scope == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.HOLD.Service_ID,
                or_(
                    models.HOLD.hold_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
            
            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.Scope == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.END_OF_DAY.Service_ID,
                or_(
                    models.END_OF_DAY.end_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
                

        # final query
            newquery =  db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.Scope == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID.in_(list_ddata1)
            ).all()

            
            
            return commoncalculation(db,newquery, date)

        elif option == "scopelist" and statusdata == 'Non-Charchable':
            

            list_ddata1 = set()

           

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.Scope == dataoptiopns,
                models.TL.status == 1,
                models.TL.working_time.like(f"%{date}%")    
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.Scope == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.HOLD.Service_ID,
                or_(
                    models.HOLD.hold_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
            
            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.Scope == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.END_OF_DAY.Service_ID,
                or_(
                    models.END_OF_DAY.end_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
                

        # final query
            newquery =  db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.Scope == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID.in_(list_ddata1)
            ).all()

            
            
            return commoncalculation(db,newquery, date)

        elif option == "subscope"  and statusdata == 'CHARGABLE':
            

            list_ddata1 = set()

           

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.From == dataoptiopns,
                models.TL.status == 1,
                models.TL.working_time.like(f"%{date}%")    
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.From == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.HOLD.Service_ID,
                or_(
                    models.HOLD.hold_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
            
            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.From == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.END_OF_DAY.Service_ID,
                or_(
                    models.END_OF_DAY.end_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
                

        # final query
            newquery =  db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.From == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID.in_(list_ddata1)
            ).all()

            
            
            return commoncalculation(db,newquery, date)

        elif option == "subscope"  and statusdata == 'Non-Charchable':
            
            list_ddata1 = set()

           

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.From == dataoptiopns,
                models.TL.status == 1,
                models.TL.working_time.like(f"%{date}%")    
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.From == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.HOLD.Service_ID,
                or_(
                    models.HOLD.hold_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
            
            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.From == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID == models.END_OF_DAY.Service_ID,
                or_(
                    models.END_OF_DAY.end_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
                

        # final query
            newquery =  db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.From == dataoptiopns,
                models.TL.status == 1,
                models.TL.Service_ID.in_(list_ddata1)
            ).all()

            
            
            return commoncalculation(db,newquery, date)
        

        elif option == "twenty"  and statusdata == 'Non-Charchable':
            
            list_ddata1 = set()

           

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.Service_ID == dataoptiopns, 
                models.TL.status == 1,
                models.TL.working_time.like(f"%{date}%")    
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.Service_ID == dataoptiopns, 
                models.TL.status == 1,
                models.TL.Service_ID == models.HOLD.Service_ID,
                or_(
                    models.HOLD.hold_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
            
            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.Service_ID == dataoptiopns, 
                models.TL.status == 1,
                models.TL.Service_ID == models.END_OF_DAY.Service_ID,
                or_(
                    models.END_OF_DAY.end_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
                

        # final query
            newquery =  db.query(models.TL).filter(
                models.TL.type_of_activity == 'Non-Charchable',
                models.TL.Service_ID == dataoptiopns, 
                models.TL.status == 1,
                models.TL.Service_ID.in_(list_ddata1)
            ).all()

            
            
            return commoncalculation(db,newquery, date)
        
        elif option == "twenty"  and statusdata == 'CHARGABLE':
            
            list_ddata1 = set()

           

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.Service_ID == dataoptiopns, 
                models.TL.status == 1,
                models.TL.working_time.like(f"%{date}%")    
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)

            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.Service_ID == dataoptiopns, 
                models.TL.status == 1,
                models.TL.Service_ID == models.HOLD.Service_ID,
                or_(
                    models.HOLD.hold_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
            
            db_res2 = db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.Service_ID == dataoptiopns, 
                models.TL.status == 1,
                models.TL.Service_ID == models.END_OF_DAY.Service_ID,
                or_(
                    models.END_OF_DAY.end_time_end.like(f"%{date}%"),
                    models.TL.working_time.like(f"%{date}%")
                )
                
            )

            for row2 in db_res2:
                list_ddata1.add(row2.Service_ID)
                

        # final query
            newquery =  db.query(models.TL).filter(
                models.TL.type_of_activity == 'CHARGABLE',
                models.TL.Service_ID == dataoptiopns, 
                models.TL.status == 1,
                models.TL.Service_ID.in_(list_ddata1)
            ).all()

            
            
            return commoncalculation(db,newquery, date)
        
def user_wise_report(db: Session,date: str,option: str):
    list_data = []
    list_ddata1 = set()


    db_res2 = db.query(models.TL).filter(
        models.TL.status == 1,
        models.TL.working_time.like(f"%{date}%")    
    )

    for row2 in db_res2:
        list_ddata1.add(row2.Service_ID)

    db_res2 = db.query(models.TL).filter(
        models.TL.status == 1,
        models.TL.Service_ID == models.HOLD.Service_ID,
        or_(
            models.HOLD.hold_time_end.like(f"%{date}%"),
            models.TL.working_time.like(f"%{date}%")
        )
        
    )

    for row2 in db_res2:
        list_ddata1.add(row2.Service_ID)
    
    db_res2 = db.query(models.TL).filter(
        models.TL.status == 1,
        models.TL.Service_ID == models.END_OF_DAY.Service_ID,
        or_(
            models.END_OF_DAY.end_time_end.like(f"%{date}%"),
            models.TL.working_time.like(f"%{date}%")
        )
    )

    for row2 in db_res2:
        list_ddata1.add(row2.Service_ID)
        

# final query
    db_res =  db.query(models.TL).filter(
        models.TL.status == 1,
        models.TL.Service_ID.in_(list_ddata1)
    ).all()


    finalfilter = set()

    Scopelist = set() # scope
    subscopeslist = set() # form
    userlist = set() 
    entitylist = set() # name of entity
    twenty = set()

    for row in db_res:
        userlist.add(row._user_table1.user_id)
        entitylist.add(row.name_of_entity)
        Scopelist.add(row.Scope)
        subscopeslist.add(row.From)
        twenty.add(row.Service_ID)
 
    if option == "userlist":
        
        finalfilter = userlist
        

    elif option == "entitylist":
        # Assuming db_res contains the result of your query
        for tl_obj in db_res:
            service_id = tl_obj.Service_ID
        # print(service_id,'Or do whatever you need with service_id')  # Or do whatever you need with service_id

        finalfilter = entitylist
    elif option == "scopelist":
        
        finalfilter = Scopelist
    elif option == "subscope":
        
        finalfilter = subscopeslist
    elif option == "twenty":
        
        finalfilter = twenty

    # print(userlist,"userlist")
    # print(entitylist, "entitylist")
    # print(Scopelist,"scopelist")
    # print(subscopeslist,"subscope")
    # print(finalfilter,'fffffffffffffffffffffffffffffffffffffffffffffffffff')
    for usertof in finalfilter:

            

            combined_data = {
                'date': set(),
                'user': set(),
                'Service_ID': set(),
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
                'created_at' : set(),
                'Completed_date' : set(),
                'idealname' : pendulum.duration()
            }

            combined_datab = {
                'date': set(),
                'user': set(),
                'Service_ID': set(),
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
                'created_at' : set(),
                'Completed_date' : set(),
                'idealname' : pendulum.duration()
            }

            finalre = {
                'date': set(),
                'user': set(),
                'Service_ID': set(),
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
                'created_at' : set(),
                'Completed_date' : set(),
                'idealname' : set()
            }

            idealname = pendulum.duration()
            end_time = pendulum.duration()
            hold = pendulum.duration()
            breaks = pendulum.duration()
            time_diff_work = pendulum.duration()
            call = pendulum.duration()
            meeting = pendulum.duration()
            in_progress = pendulum.duration()
            completed = pendulum.duration() 
            no_itemsa = 0
            for entry in  common( db  , date  , usertof   , option  , 'Non-Charchable'):
                # print(entry,'newone non-chargable')
                for key in combined_datab.keys():
                    if key == 'date':
                            
                            combined_datab[key].add(entry[key])
                    elif key == 'end_time':
                        try : 
                            end_time = end_time + entry[key]
                            
                        except:
                            end_time = end_time + pendulum.duration(hours=0)
                    elif key == 'hold':
                        try : 
                            hold = hold + entry[key]
                           
                        except:
                            hold = hold +  pendulum.duration(hours=0)
                    elif key == 'break':
                        try : 
                            breaks = breaks + entry[key]
                            
                        except:
                            breaks = breaks + pendulum.duration(hours=0)
                    elif key == 'time_diff_work':
                        try : 
                            time_diff_work = time_diff_work + entry[key]

                        except:
                            time_diff_work = time_diff_work + pendulum.duration(hours=0)
                    elif key == 'call':
                        try : 
                            call = call + entry[key]
                           
                        except:
                            call = call + pendulum.duration(hours=0)
                    elif key == 'meeting':
                        try : 
                            meeting = meeting + entry[key]

                        except:
                            meeting = meeting + pendulum.duration(hours=0)
                    elif key == 'in_progress':
                        try : 

                            in_progress = in_progress + entry[key]
                            
                        except:
                            in_progress = in_progress + pendulum.duration(hours=0)
                    elif key == 'completed':
                        try : 
                            completed = completed + entry[key]
                          
                        except:
                            completed = completed +  pendulum.duration(hours=0)   
     
                    elif key == 'no_of_items':
                        
                        
                        try : 
                            no_itemsa = no_itemsa +  int(entry[key])
                         
                            
                            
                        except:
                            None   
                    elif key == 'idealname':
                        try : 
                            idealname =  entry[key]
                           
                        except:
                            idealname = idealname + pendulum.duration(hours=0)                                                                                                                                                        
                    else:
                        try:
                            combined_datab[key].add(entry[key])
                        except :
                            None


            idealnamea = pendulum.duration()
            end_timea = pendulum.duration()
            holda = pendulum.duration()
            breaksa = pendulum.duration()
            time_diff_worka = pendulum.duration()
            calla = pendulum.duration()
            meetinga = pendulum.duration()
            in_progressa = pendulum.duration()
            completeda = pendulum.duration()
            no_items = 0
            for entry in common( db  , date  , usertof   , option  , 'CHARGABLE'):
                
                for key in combined_data.keys():
                    if key == 'date':
                            
                            combined_data[key].add(entry[key])
                    elif key == 'end_time':
                        try : 
                            end_timea = end_timea + entry[key]
                            
                        except:
                            end_timea = end_timea + pendulum.duration(hours=0)
                    elif key == 'hold':
                        try : 
                            holda = holda + entry[key]
                           
                        except:
                            holda = holda +  pendulum.duration(hours=0)
                    elif key == 'break':
                        try : 
                            breaksa = breaksa + entry[key]
                            
                        except:
                            breaksa = breaksa + pendulum.duration(hours=0)
                    elif key == 'time_diff_work':
                        try : 
                            time_diff_worka = time_diff_worka + entry[key]

                        except:
                            time_diff_worka = time_diff_worka + pendulum.duration(hours=0)
                    elif key == 'call':
                        try : 
                            calla = calla + entry[key]
                           
                        except:
                            calla = calla + pendulum.duration(hours=0)
                    elif key == 'meeting':
                        try : 
                            meetinga = meetinga + entry[key]

                        except:
                            meetinga = meetinga + pendulum.duration(hours=0)
                    elif key == 'in_progress':
                        try : 

                            in_progressa = in_progressa + entry[key]
                            
                        except:
                            in_progressa = in_progressa + pendulum.duration(hours=0)
                    elif key == 'completed':
                        try : 
                            completeda = completeda + entry[key]
                          
                        except:
                            completeda = completeda +  pendulum.duration(hours=0)   
                    elif key == 'idealname':
                        try : 
                            idealnamea =  entry[key]
                           
                        except:
                            idealnamea = idealname + pendulum.duration(hours=0)  
                    elif key == 'no_of_items':
                        
                        try : 

                            no_items = no_items +  int(entry[key])
                         
                        except:
                            None                                                                                                                                                                                           
                    else:
                        try:
                            combined_datab[key].add(entry[key])
                        except :
                            None

#-------------------------------------------------------------------------------------------------------
            combined_data['idealname'] = idealnamea
            combined_data['end_time'] = end_timea
            combined_data['hold'] = holda
            combined_data['break'] = breaksa
            combined_data['time_diff_work'] = time_diff_worka
            combined_data['call'] = calla
            combined_data['meeting'] = meetinga
            combined_data['in_progress'] = in_progressa
            combined_data['completed'] =  completeda
            combined_data['no_of_items'].add(no_items)
            # print(no_itemsa ,no_items,'rrrrrrrrrrrrrrrrrr')

            # # Print the values of these variables
            # print("end_timea:", end_timea.in_words())
            # print("holda:", holda.in_words())
            # print("breaksa:", breaksa.in_words())
            # print("time_diff_worka:", time_diff_worka.in_words())
            # print("calla:", calla.in_words())
            # print("meetinga:", meetinga.in_words())
            # print("in_progressa:", in_progressa.in_words())
            # print("completeda:", completeda.in_words())

            combined_datab['idealname'] = idealname 
            combined_datab['end_time'] = end_time 
            combined_datab['hold'] = hold 
            combined_datab['break'] = breaks 
            combined_datab['time_diff_work'] = time_diff_work 
            combined_datab['call'] = call 
            combined_datab['meeting'] = meeting 
            combined_datab['in_progress'] = in_progress 
            combined_datab['completed'] =  completed 
            combined_datab['no_of_items'].add(no_itemsa)

            # print(common( db  , date  , usertof   , option  , 'CHARGABLE'),usertof,'result--------------------------')

            # Print the values of these variables
            # print("end_time:", end_time.in_words())
            # print("hold:", hold.in_words())
            # print("breaks:", breaks.in_words())
            # print("time_diff_work:", time_diff_work.in_words())
            # print("call:", call.in_words())
            # print("meeting:", meeting.in_words())
            # print("in_progress:", in_progress.in_words())
            # print("completed:", completed.in_words())

            for key in finalre.keys():

                        if key == 'end_time':
                            finalre[key].add(convert_to_duration(combined_datab[key]+combined_data[key]))
                        elif key == 'hold':
                            finalre[key].add(convert_to_duration(combined_datab[key]+combined_data[key]))
                        elif key == 'break':
                            finalre[key].add(convert_to_duration(combined_datab[key]+combined_data[key]))
                        elif key == 'time_diff_work':
                            finalre[key].add(convert_to_duration(combined_datab[key]+combined_data[key]))
                        elif key == 'call':
                            finalre[key].add(convert_to_duration(combined_datab[key]+combined_data[key]))
                        elif key == 'meeting':
                            finalre[key].add(convert_to_duration(combined_datab[key]+combined_data[key]))
                        elif key == 'in_progress':
                            finalre[key].add(convert_to_duration(combined_datab[key]+combined_data[key]))
                        elif key == 'completed':
                            finalre[key].add(convert_to_duration(combined_datab[key]+combined_data[key]))
                        elif key == 'idealname':
                            finalre[key].add(convert_to_duration(combined_datab[key]+combined_data[key]))
                        elif key == 'no_of_items':
                            finalre[key].add(no_items+no_itemsa)
                        elif key == 'chargable':
                            finalre[key].add(convert_to_duration(combined_data['in_progress']+combined_data['completed']))
                        elif key == 'non-chargable':
                            finalre[key].add(convert_to_duration(combined_datab['in_progress']+combined_datab['completed']))
                        elif key == 'total-time':
                            finalre[key].add(convert_to_duration(combined_data['in_progress']+combined_data['completed']+combined_datab['in_progress']+combined_datab['completed']))
                        else:
                            finalre[key] = combined_data[key].union(combined_datab[key])

# ------------------------------------------------------------------------------------            

            list_data.append(finalre)
           
    return list_data