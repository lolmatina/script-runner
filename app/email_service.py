import yagmail
import os
import base64
import io
from typing import Optional
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class EmailService:
    def __init__(self):
        self.gmail_email = os.getenv("GMAIL_EMAIL")
        self.gmail_password = os.getenv("GMAIL_APP_PASSWORD") 
        self.smtp_host = os.getenv("GMAIL_SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("GMAIL_SMTP_PORT", "587"))
        self.from_email = os.getenv("FROM_EMAIL", self.gmail_email)
        self.from_name = os.getenv("FROM_NAME", "Script Runner App")
        self.base_url = os.getenv("BASE_URL", "http://localhost:8000")
        
        # Check if email is configured
        self.is_configured = bool(self.gmail_email and self.gmail_password)
        
        if self.is_configured:
            try:
                self.yag = yagmail.SMTP(
                    user=self.gmail_email,
                    password=self.gmail_password,
                    host=self.smtp_host,
                    port=self.smtp_port,
                    smtp_starttls=True,
                    smtp_ssl=False
                )
            except Exception as e:
                print(f"❌ Gmail SMTP configuration error: {e}")
                self.is_configured = False
                self.yag = None
        else:
            self.yag = None
            print("⚠️  Gmail SMTP not configured. Update .env file with Gmail credentials.")
    
    def send_invitation_email(self, to_email: str, invitation_token: str) -> tuple[bool, str]:
        """
        Send invitation email to user
        Returns: (success: bool, message: str)
        """
        if not self.is_configured:
            return False, "Email service not configured. Please update .env file with Gmail SMTP settings."
        
        try:
            # Create registration URL
            registration_url = f"{self.base_url}/register?token={invitation_token}"
            
            # Email subject
            subject = f"🎉 You're Invited to Join {self.from_name}!"
            
            # Email body (HTML)
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .button {{ display: inline-block; background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 15px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                    .warning {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ffc107; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚀 Welcome to Script Runner App!</h1>
                        <p>You've been invited to join our platform</p>
                    </div>
                    
                    <div class="content">
                        <h2>Hello!</h2>
                        <p>Your administrator has invited you to join <strong>{self.from_name}</strong> - a secure platform for running Python scripts through a web interface.</p>
                        
                        <h3>📧 Your Invitation Details:</h3>
                        <ul>
                            <li><strong>Email:</strong> {to_email}</li>
                            <li><strong>Invited by:</strong> System Administrator</li>
                        </ul>
                        
                        <div class="warning">
                            <strong>⏰ Important:</strong> This invitation is unique to your email address and can only be used once. Please complete your registration soon.
                        </div>
                        
                        <p style="text-align: center; margin: 30px 0;">
                            <a href="{registration_url}" class="button">🔐 Complete Registration</a>
                        </p>
                        
                        <h3>🔒 What happens next:</h3>
                        <ol>
                            <li>Click the registration button above</li>
                            <li>Create your secure password</li>
                            <li>Start using the platform immediately</li>
                        </ol>
                        
                        <h3>✨ Platform Features:</h3>
                        <ul>
                            <li>🖥️ Run Python scripts through web interface</li>
                            <li>📊 View real-time script output and results</li>
                            <li>🔐 Secure authentication and session management</li>
                            <li>📱 Modern, responsive design</li>
                        </ul>
                        
                        <p><strong>Need help?</strong> Contact your system administrator if you have any questions.</p>
                    </div>
                    
                    <div class="footer">
                        <p>If the button doesn't work, copy and paste this URL into your browser:</p>
                        <p><code>{registration_url}</code></p>
                        <hr>
                        <p>This invitation was sent by {self.from_name} | Secure • Reliable • Easy to Use</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Send email
            self.yag.send(
                to=to_email,
                subject=subject,
                contents=html_body
            )
            
            return True, f"✅ Invitation email sent successfully to {to_email}"
            
        except Exception as e:
            error_msg = f"❌ Failed to send email to {to_email}: {str(e)}"
            print(error_msg)
            return False, error_msg
    
    def send_script_result_email(self, to_email: str, script_name: str, arguments: str, output: dict, output_files: list = None, execution_id: int = None) -> tuple[bool, str]:
        """
        Send script execution results to user via email with file attachments
        Returns: (success: bool, message: str)
        """
        if not self.is_configured:
            return False, "Email service not configured"
        
        try:
            # Email subject
            if output.get('error'):
                subject = f"❌ Script Execution Failed: {script_name}"
                status_icon = "❌"
                status_text = "Failed"
                status_color = "#dc3545"
            elif output.get('returncode', 0) == 0:
                subject = f"✅ Script Execution Successful: {script_name}"
                status_icon = "✅"
                status_text = "Success"
                status_color = "#28a745"
            else:
                subject = f"⚠️ Script Execution Completed with Errors: {script_name}"
                status_icon = "⚠️"
                status_text = "Warning"
                status_color = "#ffc107"
            
            # Format arguments for display
            args_display = arguments if arguments.strip() else "None"
            
            # Format output for display
            stdout_display = output.get('stdout', '').strip() or "No output"
            stderr_display = output.get('stderr', '').strip() or "No errors"
            
            # Process output files
            file_summary = output.get('file_summary', {})
            output_files = output_files or []
            
            # File attachments and information
            file_attachments = []
            file_section = ""
            
            if output_files:
                from .file_manager import file_manager
                
                file_section = f"""
                <h3>📁 Generated Files ({file_summary.get('total', 0)} files, {file_summary.get('total_size_human', '0 B')}):</h3>
                <div style="background: white; padding: 15px; border-radius: 5px; border: 1px solid #e9ecef;">
                """
                
                for file_info in output_files:
                    category_icons = {
                        'images': '🖼️',
                        'documents': '📄',
                        'data': '📊',
                        'charts': '📈',
                        'reports': '📋',
                        'other': '📎'
                    }
                    
                    icon = category_icons.get(file_info.get('category', 'other'), '📎')
                    
                    file_section += f"""
                    <div style="margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 3px;">
                        <strong>{icon} {file_info['name']}</strong><br>
                        <small style="color: #666;">
                            Size: {file_info.get('size_human', 'Unknown')} | 
                            Type: {file_info.get('category', 'Unknown').title()} |
                            <a href="{self.base_url}/download/{execution_id}/{file_info['path']}" style="color: #007bff;">Download</a>
                        </small>
                    </div>
                    """
                    
                    # Try to attach small files to email
                    if execution_id:
                        permanent_dir = file_manager.base_output_dir / "permanent" / str(execution_id)
                        file_path = permanent_dir / file_info['path']
                        
                        if file_path.exists():
                            file_content = file_manager.get_file_content_for_email(file_path, max_size_mb=5)
                            if file_content:
                                file_attachments.append(file_content)
                
                file_section += """
                </div>
                <div style="margin-top: 10px; padding: 15px; background: #e8f4fd; border-radius: 5px;">
                    <h4>📥 Download All Files</h4>
                    <p>Access your files from the dashboard: 
                    <a href="{}/dashboard?execution={}" style="color: #007bff; font-weight: bold;">View Results & Download Files</a></p>
                </div>
                """.format(self.base_url, execution_id or '')
            
            # Email body (HTML)
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .status {{ background: {status_color}; color: white; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0; }}
                    .code-block {{ background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 5px; padding: 15px; margin: 10px 0; font-family: 'Courier New', monospace; white-space: pre-wrap; max-height: 300px; overflow-y: auto; }}
                    .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }}
                    .info-box {{ background: white; padding: 15px; border-radius: 5px; border-left: 4px solid #667eea; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                    @media (max-width: 600px) {{ .info-grid {{ grid-template-columns: 1fr; }} }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>{status_icon} Script Execution Report</h1>
                        <p>Results from {self.from_name}</p>
                    </div>
                    
                    <div class="content">
                        <div class="status">
                            <h2>{status_icon} Status: {status_text}</h2>
                        </div>
                        
                        <div class="info-grid">
                            <div class="info-box">
                                <h3>📄 Script Details</h3>
                                <p><strong>Name:</strong> {script_name}</p>
                                <p><strong>User:</strong> {to_email}</p>
                                <p><strong>Executed:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                                {f'<p><strong>Execution ID:</strong> {execution_id}</p>' if execution_id else ''}
                            </div>
                            
                            <div class="info-box">
                                <h3>⚙️ Execution Info</h3>
                                <p><strong>Arguments:</strong> {args_display}</p>
                                <p><strong>Return Code:</strong> {output.get('returncode', 'N/A')}</p>
                                {f'<p><strong>Files Generated:</strong> {file_summary.get("total", 0)}</p>' if file_summary.get('total', 0) > 0 else ''}
                            </div>
                        </div>
                        
                        {file_section}
                        
                        <h3>📤 Standard Output:</h3>
                        <div class="code-block">{stdout_display}</div>
                        
                        <h3>🚨 Error Output:</h3>
                        <div class="code-block">{stderr_display}</div>
                        
                        {f'<h3>❌ Execution Error:</h3><div class="code-block" style="background: #fff5f5; border-color: #fed7d7;">{output["error"]}</div>' if output.get('error') else ''}
                        
                        <div style="margin-top: 30px; padding: 20px; background: #e3f2fd; border-radius: 5px;">
                            <h4>🔄 Next Steps</h4>
                            <p>• Visit your dashboard: <a href="{self.base_url}/dashboard">Dashboard</a></p>
                            {f'<p>• View this execution: <a href="{self.base_url}/dashboard?execution={execution_id}">Execution #{execution_id}</a></p>' if execution_id else ''}
                            <p>• Run scripts again with different parameters</p>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <hr>
                        <p>This report was sent by {self.from_name} | Automated Script Execution System</p>
                        {f'<p style="font-size: 12px; color: #999;">Execution ID: {execution_id} | Files attached if ≤5MB</p>' if execution_id else ''}
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Prepare email with attachments
            email_data = {
                'to': to_email,
                'subject': subject,
                'contents': html_body
            }
            
            # Add file attachments
            if file_attachments:
                email_data['attachments'] = []
                for attachment in file_attachments:
                    # Create a file-like object from binary data
                    binary_data = base64.b64decode(attachment['content'])
                    file_obj = io.BytesIO(binary_data)
                    file_obj.name = attachment['filename']  # Set filename for yagmail
                    email_data['attachments'].append(file_obj)
            
            # Send email
            self.yag.send(**email_data)
            
            attachment_info = f" with {len(file_attachments)} attachments" if file_attachments else ""
            return True, f"✅ Script results emailed to {to_email}{attachment_info}"
            
        except Exception as e:
            error_msg = f"❌ Failed to email results to {to_email}: {str(e)}"
            print(error_msg)
            return False, error_msg

    def test_connection(self) -> tuple[bool, str]:
        """Test Gmail SMTP connection"""
        if not self.is_configured:
            return False, "Email service not configured"
        
        try:
            # Try to send a test (but don't actually send)
            self.yag.smtp.noop()
            return True, "✅ Gmail SMTP connection successful"
        except Exception as e:
            return False, f"❌ Gmail SMTP connection failed: {str(e)}"

# Global email service instance
email_service = EmailService() 