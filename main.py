from fastapi import FastAPI,Request,Form,Depends,HTTPException
from database import engine,get_db
from models import Base,Users
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Annotated
from sqlalchemy.orm import Session
from pwdlib import PasswordHash
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from dotenv import load_dotenv
import os
from csrf import get_csrf_token,valid_csrf_token

app = FastAPI()
Base.metadata.create_all(bind=engine)
templates = Jinja2Templates(directory="templates")
app.mount("/static",StaticFiles(directory="static"))
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

class UserRegister(BaseModel):
    name :str
    email :str
    password :str
class UserLogin(BaseModel):
    email:str
    password : str

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
    session_cookie="myapp_session",
    max_age=60*60*24*7,
    same_site="lax",
    https_only=False
)



@app.get("/")
def home(request: Request):
    
    return templates.TemplateResponse(request=request,name="home.html")

@app.get("/register")
def register(request:Request):
    csrf_token = get_csrf_token(request)
    return templates.TemplateResponse(request=request,
                                      name="register.html",
                                      context={"csrf_token": csrf_token})

@app.post("/register")
def register_user(request:Request, form_data : Annotated[UserRegister,Form()],
                  db:Session = Depends(get_db),csrf_token: str = Form(...)):
    if not valid_csrf_token(request, csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF Token")
    existing_user = db.query(Users).filter(Users.email==form_data.email).first()
    if existing_user:
        return templates.TemplateResponse(
            request=request,
            name="register.html",
            context={"error":"Email already registerd",
                     "csrf_token": get_csrf_token(request)}
        )
    password_hasher = PasswordHash.recommended()
    hashed_password = password_hasher.hash(form_data.password)
    new_user = Users(
        name = form_data.name,
        email = form_data.email,
        password_hash = hashed_password
    )
    db.add(new_user)
    db.commit()
    return RedirectResponse(url ="/login",status_code=303)

@app.get("/login")
def login(request:Request):
    csrf_token = get_csrf_token(request)
    return templates.TemplateResponse(request=request,
                                      name="login.html",
                                     context={"csrf_token": csrf_token})

@app.post("/login")
def login_user(request:Request,form_data:Annotated[UserLogin,Form()],
               db:Session=Depends(get_db),csrf_token: str = Form(...)):
    if not valid_csrf_token(request, csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF Token")
    user = db.query(Users).filter(Users.email==form_data.email).first()
    password_hasher = PasswordHash.recommended()
    if user and password_hasher.verify(form_data.password,user.password_hash):
        request.session['user_id']=user.id
        return RedirectResponse(url="/dashboard",status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": "Invalid email or password",
                 "csrf_token": get_csrf_token(request)}
    )

@app.get("/dashboard")
def dashboard(request:Request,db:Session=Depends(get_db)):
    csrf_token = get_csrf_token(request)
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login",status_code=303)
    user = db.query(Users).filter(Users.id==user_id).first()
    if not user:
        request.session.clear()
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"user":user,"csrf_token":csrf_token})

@app.get("/admin")
def admin_page(request:Request,db:Session=Depends(get_db)):
    csrf_token = get_csrf_token(request)
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login",status_code=303)
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        request.session.clear()
        return RedirectResponse(url="/login",status_code=303)
    if user.role != "admin":
        raise HTTPException(status_code=403,detail="Access Denied") 
    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={"user":user,"csrf_token":csrf_token}
    )

@app.get("/admin/students")
def students_management(request:Request,db:Session=Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login",status_code=303)
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        request.session.clear()
        return RedirectResponse(url="/login", status_code=303)
    if user.role != "admin":
        raise HTTPException(status_code=403,detail="Access Denied")
    students = db.query(Users).filter(Users.role == "student").all()
    csrf_token = get_csrf_token(request)

    return templates.TemplateResponse(
        request=request,
        name="students.html",
        context={"students":students,
                 "csrf_token": csrf_token}
    )

@app.post("/admin/students/delete/{student_id}")
def delete_student(student_id : int,request:Request,
                   db:Session=Depends(get_db),csrf_token: str = Form(...)):
    if not valid_csrf_token(request, csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF Token")
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login",status_code=303)
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        request.session.clear()
        return RedirectResponse(url="/login", status_code=303)
    if user.role != "admin":
        raise HTTPException(status_code=403,detail="Access Denied")
    student = db.query(Users).filter(Users.id == student_id,Users.role=="student").first()
    db.delete(student)
    db.commit()
    return RedirectResponse(url="/admin/students", status_code=303)

@app.post("/logout")
def logout(request: Request,csrf_token: str = Form(...)):
    if not valid_csrf_token(request, csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF Token")

    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
    