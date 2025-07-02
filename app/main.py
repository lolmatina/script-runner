from fastapi import FastAPI, Request, Depends, HTTPException, Form, File, UploadFile, status
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import timedelta
import subprocess
import sys
import os
import json
import importlib.util
from typing import Optional

from .database import get_db, create_tables, User, Script, Invitation, ScriptExecution
from .auth import (
    verify_password, get_password_hash, create_access_token, 
    verify_token, generate_invitation_token, verify_admin_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from .email_service import email_service

app = FastAPI(title="Script Runner App")

templates = Jinja2Templates(directory="app/templates")

# Create database tables
create_tables()

# Helper functions
def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    
    email = verify_token(token)
    if not email:
        return None
    
    user = db.query(User).filter(User.email == email).first()
    return user

def require_auth(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    return user

def check_admin_auth(request: Request):
    admin_token = request.cookies.get("admin_token")
    return admin_token == "admin_authenticated"

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    user = get_current_user(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=302)
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse(
            "login.html", 
            {"request": request, "error": "Invalid email or password"}
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=access_token, httponly=True)
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, token: Optional[str] = None):
    # Require invitation token for registration
    if not token:
        return templates.TemplateResponse(
            "register_error.html", 
            {"request": request, "error": "Registration requires an invitation from an administrator"}
        )
    
    # Verify token exists and is valid
    db = next(get_db())
    invitation = db.query(Invitation).filter(
        Invitation.token == token, 
        Invitation.is_used == False
    ).first()
    
    if not invitation:
        return templates.TemplateResponse(
            "register_error.html", 
            {"request": request, "error": "Invalid or expired invitation token"}
        )
    
    return templates.TemplateResponse(
        "register.html", 
        {"request": request, "token": token, "invited_email": invitation.email}
    )

@app.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    token: str = Form(...),  # Token is now required
    db: Session = Depends(get_db)
):
    # Require invitation token
    if not token:
        return templates.TemplateResponse(
            "register_error.html", 
            {"request": request, "error": "Registration requires an invitation from an administrator"}
        )
    
    # Check if invitation token is valid
    invitation = db.query(Invitation).filter(
        Invitation.token == token, 
        Invitation.is_used == False
    ).first()
    
    if not invitation or invitation.email != email:
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "error": "Invalid invitation token or email mismatch", "token": token}
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return templates.TemplateResponse(
            "register.html", 
            {"request": request, "error": "User already exists", "token": token, "invited_email": invitation.email}
        )
    
    # Create new user
    hashed_password = get_password_hash(password)
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    
    # Mark invitation as used
    invitation.is_used = True
    
    db.commit()
    
    return templates.TemplateResponse(
        "login.html", 
        {"request": request, "success": "Registration successful! Please login."}
    )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, user: User = Depends(require_auth), db: Session = Depends(get_db)):
    scripts = db.query(Script).all()
    return templates.TemplateResponse(
        "dashboard.html", 
        {"request": request, "user": user, "scripts": scripts}
    )

@app.post("/run-script")
async def run_script(
    request: Request,
    script_id: int = Form(...),
    arguments: str = Form(""),
    auto_install: str = Form("false"),  # Option to auto-install packages
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        raise HTTPException(status_code=404, detail="Script not found")
    
    # Import file manager
    from .file_manager import file_manager
    from .package_manager import package_manager
    
    # Create execution record
    execution = ScriptExecution(
        script_id=script.id,
        user_id=user.id,
        arguments=arguments
    )
    db.add(execution)
    db.commit()
    db.refresh(execution)
    
    # Create workspace for this execution
    workspace_dir = file_manager.create_execution_workspace(execution.id, user.id)
    
    # Use absolute path for script to avoid path issues when changing working directory
    script_path = os.path.abspath(f"app/scripts/{script.filename}")
    
    # Verify script file exists
    if not os.path.exists(script_path):
        error_msg = f"Script file not found: {script.filename}"
        execution.error_message = error_msg
        execution.return_code = -1
        db.commit()
        
        scripts = db.query(Script).all()
        return templates.TemplateResponse(
            "dashboard.html",
            {
                "request": request, 
                "user": user, 
                "scripts": scripts, 
                "output": {"error": error_msg, "returncode": -1},
                "executed_script": script.name,
                "execution_id": execution.id
            }
        )
    
    # Check for missing packages
    dependency_info = package_manager.analyze_script_dependencies(script_path, script.requirements)
    
    package_warnings = []
    package_install_output = ""
    
    # Handle missing packages
    if dependency_info['missing_packages']:
        if auto_install.lower() == "true":
            # Attempt to install missing packages
            install_success, install_message = package_manager.install_packages(dependency_info['missing_packages'])
            package_install_output = install_message
            
            if not install_success:
                output = {
                    "error": f"Missing packages could not be installed: {install_message}",
                    "missing_packages": dependency_info['missing_packages'],
                    "install_command": dependency_info['install_command']
                }
                
                # Update execution record
                execution.error_message = output["error"]
                execution.return_code = -1
                db.commit()
                
                # Still send email with error
                email_success, email_message = email_service.send_script_result_email(
                    to_email=user.email,
                    script_name=script.name,
                    arguments=arguments,
                    output=output,
                    output_files=[],
                    execution_id=execution.id
                )
                
                email_status = f"📧 Error report sent to {user.email}" if email_success else f"⚠️ Email failed: {email_message}"
                
                scripts = db.query(Script).all()
                return templates.TemplateResponse(
                    "dashboard.html",
                    {
                        "request": request, 
                        "user": user, 
                        "scripts": scripts, 
                        "output": output,
                        "executed_script": script.name,
                        "email_status": email_status,
                        "dependency_info": dependency_info,
                        "execution_id": execution.id,
                        "output_files": []
                    }
                )
        else:
            # Warn about missing packages but don't install
            package_warnings.append(f"⚠️ Missing packages: {', '.join(dependency_info['missing_packages'])}")
            package_warnings.append(f"📝 Install command: {dependency_info['install_command']}")
    
    # Scan for files before execution
    before_files = set()
    for file_path in workspace_dir.rglob("*"):
        if file_path.is_file():
            before_files.add(file_path)
    
    try:
        # Parse arguments
        args = []
        if arguments.strip():
            try:
                args = json.loads(arguments) if arguments.startswith('[') else [arguments]
            except:
                args = [arguments]
        
        # Execute script in the workspace directory
        result = subprocess.run(
            [sys.executable, script_path] + [str(arg) for arg in args],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(workspace_dir)  # Run script in workspace directory
        )
        
        # Scan for output files after execution
        output_files = file_manager.scan_for_output_files(workspace_dir, before_files)
        
        # Move files to permanent storage
        if output_files:
            permanent_dir = file_manager.move_files_to_permanent_storage(workspace_dir, execution.id)
        
        output = {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
            "package_warnings": package_warnings,
            "package_install_output": package_install_output if package_install_output else None,
            "output_files": output_files,
            "file_summary": file_manager.create_file_summary(output_files)
        }
        
        # Update execution record
        execution.output_text = f"STDOUT:\n{result.stdout}\n\nSTDERR:\n{result.stderr}"
        execution.output_files = json.dumps([f["path"] for f in output_files])
        execution.return_code = result.returncode
        
    except subprocess.TimeoutExpired:
        output = {
            "error": "Script execution timed out", 
            "package_warnings": package_warnings,
            "output_files": [],
            "file_summary": {"total": 0}
        }
        execution.error_message = "Script execution timed out"
        execution.return_code = -1
        
    except Exception as e:
        output = {
            "error": str(e), 
            "package_warnings": package_warnings,
            "output_files": [],
            "file_summary": {"total": 0}
        }
        execution.error_message = str(e)
        execution.return_code = -1
    
    # Save execution record
    db.commit()
    
    # Clean up workspace
    file_manager.cleanup_workspace(workspace_dir)
    
    # Send email results to user (if email is configured)
    email_success, email_message = email_service.send_script_result_email(
        to_email=user.email,
        script_name=script.name,
        arguments=arguments,
        output=output,
        output_files=output.get("output_files", []),
        execution_id=execution.id
    )
    
    # Clean up files after successful email sending (if enabled)
    cleanup_status = ""
    if email_success and output.get("output_files"):
        if file_manager.cleanup_after_email:
            cleanup_success = file_manager.cleanup_execution_files(execution.id)
            if cleanup_success:
                cleanup_status = " (files cleaned up to save space)"
            else:
                cleanup_status = " (cleanup failed - files retained)"
        else:
            cleanup_status = " (files preserved for download)"
    
    # Add email status to output for display
    if email_success:
        email_status = f"📧 Results also sent to {user.email}{cleanup_status}"
    else:
        email_status = f"⚠️ Email failed: {email_message}"
    
    scripts = db.query(Script).all()
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request, 
            "user": user, 
            "scripts": scripts, 
            "output": output,
            "executed_script": script.name,
            "email_status": email_status,
            "execution_id": execution.id,
            "output_files": output.get("output_files", [])
        }
    )

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    if not check_admin_auth(request):
        return templates.TemplateResponse("admin_login.html", {"request": request})
    
    # Get data for admin panel
    db = next(get_db())
    users = db.query(User).all()
    scripts = db.query(Script).all()
    invitations = db.query(Invitation).filter(Invitation.is_used == False).all()
    
    return templates.TemplateResponse(
        "admin.html", 
        {
            "request": request, 
            "users": users, 
            "scripts": scripts, 
            "invitations": invitations
        }
    )

@app.post("/admin/login")
async def admin_login(
    request: Request,
    password: str = Form(...)
):
    if verify_admin_password(password):
        response = RedirectResponse(url="/admin", status_code=302)
        response.set_cookie(key="admin_token", value="admin_authenticated", httponly=True)
        return response
    
    return templates.TemplateResponse(
        "admin_login.html", 
        {"request": request, "error": "Invalid admin password"}
    )

@app.post("/admin/upload-script")
async def upload_script(
    request: Request,
    name: str = Form(...),
    description: str = Form(""),
    requirements: str = Form(""),
    output_types: str = Form("both"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not check_admin_auth(request):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not file.filename.endswith('.py'):
        return RedirectResponse(url="/admin?error=Only Python files allowed", status_code=302)
    
    # Save file
    file_location = f"app/scripts/{file.filename}"
    with open(file_location, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Analyze dependencies
    from .package_manager import package_manager
    dependency_info = package_manager.analyze_script_dependencies(file_location, requirements)
    
    # Save to database with requirements and output types
    script = Script(
        name=name, 
        filename=file.filename, 
        description=description,
        requirements=requirements.strip() if requirements.strip() else None,
        output_types=output_types
    )
    db.add(script)
    db.commit()
    
    # Create success message with dependency info
    success_msg = f"Script '{name}' uploaded successfully"
    if dependency_info['missing_packages']:
        success_msg += f". ⚠️ Missing packages: {', '.join(dependency_info['missing_packages'])}"
    if dependency_info['detected_imports']:
        success_msg += f". 📦 Detected imports: {', '.join(dependency_info['detected_imports'])}"
    
    return RedirectResponse(url=f"/admin?success={success_msg}", status_code=302)

@app.post("/admin/invite-user")
async def invite_user(
    request: Request,
    email: str = Form(...),
    db: Session = Depends(get_db)
):
    if not check_admin_auth(request):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        return RedirectResponse(
            url=f"/admin?error=User with email {email} already exists!", 
            status_code=302
        )
    
    # Check if there's already a pending invitation for this email
    existing_invitation = db.query(Invitation).filter(
        Invitation.email == email, 
        Invitation.is_used == False
    ).first()
    if existing_invitation:
        return RedirectResponse(
            url=f"/admin?error=Pending invitation already exists for {email}!", 
            status_code=302
        )
    
    # Generate invitation token
    token = generate_invitation_token()
    invitation = Invitation(email=email, token=token)
    db.add(invitation)
    db.commit()
    
    # Send invitation email
    success, message = email_service.send_invitation_email(email, token)
    
    if success:
        return RedirectResponse(
            url=f"/admin?success={message}", 
            status_code=302
        )
    else:
        # If email failed, still provide the manual link as fallback
        invite_link = f"http://localhost:8000/register?token={token}"
        return RedirectResponse(
            url=f"/admin?error={message} | Manual link: {invite_link}", 
            status_code=302
        )

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="access_token")
    return response

@app.get("/admin/logout")
async def admin_logout():
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie(key="admin_token")
    return response

@app.get("/download/{execution_id}/{file_path:path}")
async def download_file(
    execution_id: int,
    file_path: str,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Download output file from script execution"""
    from .file_manager import file_manager
    
    # Verify user has access to this execution
    execution = db.query(ScriptExecution).filter(
        ScriptExecution.id == execution_id,
        ScriptExecution.user_id == user.id
    ).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found or access denied")
    
    # Get file info
    file_info = file_manager.get_file_download_info(execution_id, file_path)
    if not file_info:
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(file_info['path']),
        filename=file_info['name'],
        media_type=file_info['mime_type']
    )

@app.get("/api/execution/{execution_id}/files")
async def get_execution_files(
    execution_id: int,
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    """Get list of files for an execution (API endpoint)"""
    from .file_manager import file_manager
    
    # Verify user has access to this execution
    execution = db.query(ScriptExecution).filter(
        ScriptExecution.id == execution_id,
        ScriptExecution.user_id == user.id
    ).first()
    
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found or access denied")
    
    # Get files from permanent storage
    permanent_dir = file_manager.base_output_dir / "permanent" / str(execution_id)
    
    if not permanent_dir.exists():
        return JSONResponse({"files": [], "summary": {"total": 0}})
    
    # Scan files in permanent storage
    output_files = file_manager.scan_for_output_files(permanent_dir)
    file_summary = file_manager.create_file_summary(output_files)
    
    return JSONResponse({
        "execution_id": execution_id,
        "files": output_files,
        "summary": file_summary
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 