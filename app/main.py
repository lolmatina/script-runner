from fastapi import FastAPI, Request, Depends, HTTPException, Form, File, UploadFile, status, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, UTC
import subprocess
import sys
import os
import json
import importlib.util
import pytz
import pandas as pd
import psycopg2
from typing import Optional
from dotenv import load_dotenv
import logging
import asyncio

from .database import (
    get_db, create_tables, User, Script, Invitation, ScriptExecution, BetQuery, 
    get_bets_db_connection, execute_pg_query
)
from .auth import (
    verify_password, get_password_hash, create_access_token, 
    verify_token, generate_invitation_token, verify_admin_password,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from .email_service import email_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables from parent directory
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
logger.info(f"Looking for .env file at: {dotenv_path}")
load_dotenv(dotenv_path)

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
    
    # Update last login time
    user.last_login = datetime.now(UTC)
    db.commit()
    
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
    bet_queries = db.query(BetQuery).filter(BetQuery.user_id == user.id).order_by(BetQuery.created_at.desc()).limit(10).all()
    # Attach output_filename to each bet_query
    for query in bet_queries:
        query.output_filename = None
        if query.execution_id:
            execution = db.query(ScriptExecution).filter(ScriptExecution.id == query.execution_id).first()
            if execution and execution.output_files:
                try:
                    files = json.loads(execution.output_files)
                    if files and isinstance(files, list):
                        query.output_filename = files[0]
                except Exception:
                    pass
    return templates.TemplateResponse(
        "dashboard.html", 
        {
            "request": request, 
            "user": user, 
            "scripts": scripts, 
            "bet_queries": bet_queries,
            "now": datetime.now(UTC).replace(tzinfo=None)  # Make timezone-naive for template compatibility
        }
    )

async def process_bet_query(db: Session, query_id: int):
    query = db.query(BetQuery).filter(BetQuery.id == query_id).first()
    if not query:
        logger.error(f"Query {query_id} not found")
        return
    
    try:
        logger.info(f"Starting bet query processing for user_id: {query.target_user_id}")
        
        # Create execution record
        execution = ScriptExecution(
            user_id=query.user_id,
            script_id=None,  # No script for bet queries
            arguments=f"target_user_id={query.target_user_id}"
        )
        db.add(execution)
        db.commit()
        db.refresh(execution)
        
        # Store execution ID in query
        query.execution_id = execution.id
        
        # Update status to processing
        query.status = "processing"
        db.commit()
        logger.info("Updated status to processing")
        
        # Get user's creation date from PostgreSQL
        logger.info("Getting user creation date...")
        conn = get_bets_db_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("ROLLBACK")  # Reset any failed transaction
                cur.execute("SELECT created_at FROM users WHERE id = %s", (query.target_user_id,))
                result = cur.fetchone()
                if not result or not result[0]:
                    raise Exception(f"User {query.target_user_id} not found in PostgreSQL database")
                user_created_at = result[0]
            
            # Generate list of months from user creation until now
            tz = pytz.timezone('Europe/Istanbul')  # GMT+3
            current_date = datetime.now(tz)
            start_date = user_created_at.astimezone(tz)
            
            # Initialize empty DataFrame for results
            all_results = pd.DataFrame()
            
            # Query each month sequentially
            current_month = start_date.replace(day=1)
            while current_month <= current_date:
                table_name = f"bets_{current_month.strftime('%Y%m')}"
                logger.info(f"Querying table: {table_name}")
                
                sql_query = f"""
                select 
                    {table_name}.id as bet_id,
                    {table_name}.created_at,
                    {table_name}.updated_at,
                    {table_name}.payment_account_id,
                    {table_name}.game_id,
                    {table_name}.currency_id,
                    {table_name}.amount,
                    {table_name}.win,
                    {table_name}.amount_usd,
                    {table_name}.win_usd,
                    {table_name}.bonus,
                    {table_name}.external_id,
                    {table_name}.balance,
                    {table_name}.user_id,
                    {table_name}.mobile,
                    {table_name}.user_bonus_id,
                    {table_name}.frod_win,
                    {table_name}.bonus_balance,
                    games.id as game_id,
                    games.title as game_name,
                    games.game_type_id,
                    games.vendor_id,
                    vendors.name as vendor_name
                from {table_name}
                join games on {table_name}.game_id = games.id
                join vendors on vendors.id = games.vendor_id
                where {table_name}.user_id = %s
                and {table_name}.updated_at - {table_name}.created_at >= interval '10 min'
                """
                
                try:
                    with conn.cursor() as cur:
                        cur.execute(sql_query, (query.target_user_id,))
                        result = cur.fetchall()
                        if result:
                            # Get column names from cursor description
                            columns = [desc[0] for desc in cur.description]
                            month_df = pd.DataFrame(result, columns=columns)
                            if not month_df.empty:
                                logger.info(f"Found {len(month_df)} rows in {table_name}")
                                all_results = pd.concat([all_results, month_df], ignore_index=True)
                except Exception as e:
                    # Log error but continue with next month
                    logger.error(f"Error querying {table_name}: {str(e)}")
                    with conn.cursor() as cur:
                        cur.execute("ROLLBACK")  # Ensure transaction is rolled back on error
                
                # Move to next month
                if current_month.month == 12:
                    current_month = current_month.replace(year=current_month.year + 1, month=1)
                else:
                    current_month = current_month.replace(month=current_month.month + 1)
            
            logger.info(f"Query completed. Total rows found: {len(all_results)}")
            
            # Sort results by created_at if we have results
            if not all_results.empty:
                all_results = all_results.sort_values('created_at', ascending=False)
            
            # Save output file in permanent storage directory for this execution
            permanent_dir = os.path.join("script_outputs", "permanent", str(execution.id))
            os.makedirs(permanent_dir, exist_ok=True)
            
            # Update query status and save results
            query.status = "completed"
            query.completed_at = datetime.now(UTC)
            
            # Use completed_at for filename
            csv_filename = f"bet_query_{query.id}_{query.completed_at.strftime('%Y%m%d_%H%M%S')}.csv"
            csv_path = os.path.join(permanent_dir, csv_filename)
            
            try:
                all_results.to_csv(csv_path, index=False)
                logger.info(f"CSV file created successfully at {csv_path}")
            except Exception as csv_error:
                logger.error(f"CSV Creation Error: {str(csv_error)}")
                raise
            
            # Send email
            user = db.query(User).filter(User.id == query.user_id).first()
            if user:
                try:
                    logger.info(f"Sending email to {user.email}")
                    success, message = email_service.send_script_result_email(
                        to_email=user.email,
                        script_name=f"Bet Query for User {query.target_user_id}",
                        arguments="",
                        output={
                            'returncode': 0,
                            'stdout': f"Retrieved {len(all_results)} rows of data from {start_date.strftime('%Y-%m')} to {current_date.strftime('%Y-%m')}"
                        },
                        output_files=[{
                            'name': csv_filename,
                            'path': csv_path,
                            'category': 'data',
                            'size_human': f"{os.path.getsize(csv_path) / 1024:.1f} KB"
                        }],
                        execution_id=execution.id
                    )
                    if success:
                        query.email_sent = True
                        logger.info("Email sent successfully")
                    else:
                        logger.error(f"Failed to send email: {message}")
                        raise Exception(message)
                except Exception as email_error:
                    logger.error(f"Email Error: {str(email_error)}")
                    raise
            
            # Update execution record
            execution.output_text = f"Retrieved {len(all_results)} rows of data from {start_date.strftime('%Y-%m')} to {current_date.strftime('%Y-%m')}"
            execution.output_files = json.dumps([csv_filename])  # Store just the filename
            execution.return_code = 0
            
            db.commit()
            logger.info("Query processing completed successfully")
        
        except Exception as e:
            raise e
        finally:
            conn.close()
            logger.info("Database connection closed")
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Query processing failed: {error_msg}")
        query.status = "failed"
        query.error_message = error_msg
        query.completed_at = datetime.now(UTC)
        
        if 'execution' in locals():
            execution.error_message = error_msg
            execution.return_code = -1
        
        db.commit()
        logger.error(f"Updated query status to failed with error: {error_msg}")

@app.post("/run-bet-query")
async def run_bet_query(
    request: Request,
    background_tasks: BackgroundTasks,
    user_id: int = Form(...),
    user: User = Depends(require_auth),
    db: Session = Depends(get_db)
):
    try:
        # Create new query record
        query = BetQuery(
            user_id=user.id,
            target_user_id=user_id,
            status="pending"
        )
        db.add(query)
        db.commit()
        db.refresh(query)
        
        # Add task to background queue
        background_tasks.add_task(process_bet_query, db, query.id)
        
        # Redirect immediately with success message
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.headers["HX-Trigger"] = json.dumps({
            "showMessage": {
                "message": f"Query for user {user_id} has been submitted and is processing in the background. You can check its status in the history table.",
                "type": "success"
            }
        })
        return response
        
    except Exception as e:
        logger.error(f"Failed to submit bet query: {str(e)}")
        response = RedirectResponse(url="/dashboard", status_code=302)
        response.headers["HX-Trigger"] = json.dumps({
            "showMessage": {
                "message": f"Failed to submit query: {str(e)}",
                "type": "error"
            }
        })
        return response

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
            # Attempt to install missing packages with verification
            install_success, install_message = package_manager.install_packages(dependency_info['missing_packages'])
            package_install_output = install_message
            
            if not install_success:
                # Enhanced error handling for package installation failures
                output = {
                    "error": f"Package installation failed: {install_message}",
                    "missing_packages": dependency_info['missing_packages'],
                    "install_command": dependency_info['install_command'],
                    "suggestion": "Try enabling 'Auto-install missing packages' and run again, or install packages manually."
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
                # Installation succeeded - add success message to package warnings
                package_warnings.append(f"✅ Package installation: {install_message}")
        else:
            # Warn about missing packages but don't install
            package_warnings.append(f"⚠️ Missing packages: {', '.join(dependency_info['missing_packages'])}")
            package_warnings.append(f"📝 Install command: {dependency_info['install_command']}")
            package_warnings.append(f"💡 Enable 'Auto-install missing packages' to install automatically")
    
        # Final verification before script execution (if packages were required)
    if dependency_info['missing_packages'] and auto_install.lower() == "true":
        # Re-check that all packages are now available
        final_dependency_check = package_manager.analyze_script_dependencies(script_path, script.requirements)
        if final_dependency_check['missing_packages']:
            output = {
                "error": f"Script cannot run: Required packages are still missing after installation: {', '.join(final_dependency_check['missing_packages'])}",
                "missing_packages": final_dependency_check['missing_packages'],
                "install_command": final_dependency_check['install_command'],
                "suggestion": "Try running the script again, restart the application, or install packages manually."
            }
            
            # Update execution record
            execution.error_message = output["error"]
            execution.return_code = -1
            db.commit()
            
            # Send email with error
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
                    "dependency_info": final_dependency_check,
                    "execution_id": execution.id,
                    "output_files": []
                }
            )

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

@app.post("/admin/edit-script")
async def edit_script(
    request: Request,
    script_id: int = Form(...),
    name: str = Form(...),
    description: str = Form(""),
    requirements: str = Form(""),
    output_types: str = Form("both"),
    db: Session = Depends(get_db)
):
    if not check_admin_auth(request):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get the script
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        return RedirectResponse(url="/admin?error=Script not found", status_code=302)
    
    # Update script metadata
    script.name = name
    script.description = description.strip() if description.strip() else None
    script.requirements = requirements.strip() if requirements.strip() else None
    script.output_types = output_types
    
    db.commit()
    
    return RedirectResponse(url=f"/admin?success=Script '{name}' updated successfully", status_code=302)

@app.post("/admin/delete-script")
async def delete_script(
    request: Request,
    script_id: int = Form(...),
    db: Session = Depends(get_db)
):
    if not check_admin_auth(request):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get the script
    script = db.query(Script).filter(Script.id == script_id).first()
    if not script:
        return RedirectResponse(url="/admin?error=Script not found", status_code=302)
    
    # Check if script has any executions
    execution_count = db.query(ScriptExecution).filter(ScriptExecution.script_id == script_id).count()
    
    script_name = script.name
    script_filename = script.filename
    
    # Delete the script from database
    db.delete(script)
    db.commit()
    
    # Try to delete the physical file
    try:
        import os
        file_path = f"app/scripts/{script_filename}"
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Warning: Could not delete script file {script_filename}: {e}")
    
    success_msg = f"Script '{script_name}' deleted successfully"
    if execution_count > 0:
        success_msg += f" (had {execution_count} previous executions)"
    
    return RedirectResponse(url=f"/admin?success={success_msg}", status_code=302)

@app.post("/admin/reset-password")
async def reset_user_password(
    request: Request,
    user_id: int = Form(...),
    new_password: str = Form(...),
    send_notification: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    if not check_admin_auth(request):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/admin?error=User not found", status_code=302)
    
    # Hash the new password
    from .auth import get_password_hash
    hashed_password = get_password_hash(new_password)
    
    # Update user password
    user.hashed_password = hashed_password
    db.commit()
    
    # Send email notification if requested
    notification_status = ""
    if send_notification:
        try:
            success, message = email_service.send_password_reset_notification(
                user.email, 
                new_password  # In production, don't send the actual password
            )
            if success:
                notification_status = " (user notified via email)"
            else:
                notification_status = f" (email notification failed: {message})"
        except Exception as e:
            notification_status = f" (email notification failed: {str(e)})"
    
    return RedirectResponse(
        url=f"/admin?success=Password reset for {user.email}{notification_status}", 
        status_code=302
    )

@app.post("/admin/toggle-user-status")
async def toggle_user_status(
    request: Request,
    user_id: int = Form(...),
    db: Session = Depends(get_db)
):
    if not check_admin_auth(request):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return RedirectResponse(url="/admin?error=User not found", status_code=302)
    
    # Toggle status
    user.is_active = not user.is_active
    status_text = "activated" if user.is_active else "deactivated"
    
    db.commit()
    
    return RedirectResponse(
        url=f"/admin?success=User {user.email} has been {status_text}", 
        status_code=302
    )

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