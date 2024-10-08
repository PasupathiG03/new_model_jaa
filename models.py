from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, Date, DateTime,JSON, UniqueConstraint
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import func
from .database import Base

class Nature_Of_Work(Base):
    __tablename__ = "nature_of_work"
    work_id = Column(Integer,primary_key=True,autoincrement=True)
    work_name = Column(String)
    work_status = Column(Integer,default=1)

class User_table(Base):
    __tablename__ = "user_table"
    user_id = Column(Integer,primary_key=True,autoincrement=True)
    username = Column(String)
    # username = Column(String, unique=True, nullable=False)
    password = Column(String,default='jaa')
    role = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    location = Column(String)
    user_status = Column(Integer,default=1)

    # __table_args__ = (UniqueConstraint('username', name='_username_uc'),)

class gst(Base):
    __tablename__ = "gst"
    gst_id = Column(Integer,primary_key=True,autoincrement=True)
    gst = Column(String)
    gst_status = Column(Integer,default=1)

class tds(Base):
    __tablename__ = "tds"
    tds_id = Column(Integer,primary_key=True,autoincrement=True)
    tds = Column(String)
    tds_status = Column(Integer,default=1)

class TL(Base):
    __tablename__ = "tl"
    Service_ID = Column(Integer,primary_key=True,autoincrement=True)
    name_of_entity = Column(String)
    gst_or_tan = Column(String)
    gst_tan = Column(String)
    client_grade = Column(String)
    Priority = Column(String)
    Assigned_By = Column(Integer)
    Assigned_Date = Column(DateTime, default=func.now())
    estimated_d_o_d = Column(String)
    estimated_time = Column(String)
    Assigned_To = Column(Integer,ForeignKey(User_table.user_id))
    Scope = Column(String)
    nature_of_work = Column(Integer,ForeignKey(Nature_Of_Work.work_id))
    From = Column(String)
    Actual_d_o_d = Column(String)
    status = Column(Integer,default=1)
    created_on = Column(DateTime,default=func.now())
    type_of_activity = Column(String,default='')   
    work_status = Column(String,default='Not Picked')
    no_of_items = Column(String,default='')
    remarks = Column(String,default='')
    working_time = Column(String,default='')
    completed_time = Column(String,default='')
    reallocated_time = Column(String,default='')
    _user_table1 = relationship("User_table")
    _nature_of_work = relationship("Nature_Of_Work")

class HOLD(Base):
    __tablename__ = "hold"
    id = Column(Integer,primary_key=True,autoincrement=True)
    Service_ID = Column(Integer,ForeignKey(TL.Service_ID))
    user_id = Column(Integer,ForeignKey(User_table.user_id))
    hold_time_start = Column(String,default='')
    hold_time_end = Column(String,default='')
    remarks = Column(String)
    _hold_table1 = relationship("TL")

class BREAK(Base):
    __tablename__ = "break"
    id = Column(Integer,primary_key=True,autoincrement=True)
    Service_ID = Column(Integer,ForeignKey(TL.Service_ID))
    user_id = Column(Integer,ForeignKey(User_table.user_id))
    break_time_start = Column(String,default='')
    break_time_end = Column(String,default='')
    remarks = Column(String)
    _break_table1 = relationship("TL")

class MEETING(Base):
    __tablename__ = "meeting"
    id = Column(Integer,primary_key=True,autoincrement=True)
    Service_ID = Column(Integer,ForeignKey(TL.Service_ID))
    user_id = Column(Integer,ForeignKey(User_table.user_id))
    meeting_time_start = Column(String,default='')
    meeting_time_end = Column(String,default='')
    remarks = Column(String)
    _meeting_table1 = relationship("TL")

class CALL(Base):
    __tablename__ = "call"
    id = Column(Integer,primary_key=True,autoincrement=True)
    Service_ID = Column(Integer,ForeignKey(TL.Service_ID))
    user_id = Column(Integer,ForeignKey(User_table.user_id))
    call_time_start = Column(String,default='')
    call_time_end = Column(String,default='')
    remarks = Column(String)
    _call_table1 = relationship("TL")

class END_OF_DAY(Base):
    __tablename__ = "end_of_day"
    id = Column(Integer,primary_key=True,autoincrement=True)
    Service_ID = Column(Integer,ForeignKey(TL.Service_ID))
    user_id = Column(Integer,ForeignKey(User_table.user_id))
    end_time_start = Column(String,default='')
    end_time_end = Column(String,default='')
    remarks = Column(String)
    _end_table1 = relationship("TL")

class REALLOCATED(Base):
    __tablename__ = "Reallocated"
    id = Column(Integer,primary_key=True,autoincrement=True)
    Service_ID = Column(Integer,ForeignKey(TL.Service_ID))
    user_id = Column(Integer,ForeignKey(User_table.user_id))
    re_time_start = Column(String,default='')
    re_time_end = Column(String,default='')
    remarks = Column(String)
    _reallocated_table1 = relationship("TL")


class scope(Base):
    __tablename__ = "scope"
    scope_id = Column(Integer,primary_key=True,autoincrement=True)
    scope = Column(String, unique=True)

class sub_scope(Base):
    __tablename__ = "sub_scope"
    sub_scope_id = Column(Integer,primary_key=True,autoincrement=True)
    scope_id = Column(Integer,ForeignKey(scope.scope_id))
    sub_scope = Column(String, unique=True)

class login_time(Base):
    __tablename__ = "logintime"
    login_id = Column(Integer,primary_key=True,autoincrement=True)
    userid = Column(Integer,ForeignKey(User_table.user_id))
    login_time = Column(String,default='')
    logout_time = Column(String,default='')
    _user_table1 = relationship("User_table")
    
class entityadd(Base):
    __tablename__ = "entityadd"
    id = Column(Integer,primary_key=True,autoincrement=True)
    entityname = Column(String,default='')
    gstortan = Column(String,default='')
    tanvalue = Column(String,default='')


class WorkSession(Base):
    __tablename__ = "work_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('user_table.user_id'))  
    start_time = Column(String,default='')
    end_time = Column(String,default='')
    total_time_worked = Column(String,default='')
    _user_table1 = relationship("User_table")