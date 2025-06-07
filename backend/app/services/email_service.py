"""
Email service for UCC Event Manager.
Handles sending emails for password reset, notifications, etc.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


async def send_password_reset_email(
    email: str,
    name: str,
    token: str
) -> bool:
    """
    Send password reset email to user.
    
    Args:
        email: User's email address
        name: User's full name
        token: Password reset token
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Create reset URL
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
        
        # Email content
        subject = "Password Reset - UCC Event Manager"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Password Reset</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Password Reset Request</h2>
                
                <p>Hello {name},</p>
                
                <p>We received a request to reset your password for your UCC Event Manager account.</p>
                
                <p>Click the button below to reset your password:</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background-color: #3498db; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Reset Password
                    </a>
                </div>
                
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #3498db;">{reset_url}</p>
                
                <p><strong>This link will expire in 1 hour.</strong></p>
                
                <p>If you didn't request this password reset, please ignore this email. 
                   Your password will remain unchanged.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #666;">
                    This is an automated message from UCC Event Manager. 
                    Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request
        
        Hello {name},
        
        We received a request to reset your password for your UCC Event Manager account.
        
        Please visit the following link to reset your password:
        {reset_url}
        
        This link will expire in 1 hour.
        
        If you didn't request this password reset, please ignore this email. 
        Your password will remain unchanged.
        
        ---
        This is an automated message from UCC Event Manager.
        """
        
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.SMTP_FROM_EMAIL
        msg['To'] = email
        
        # Attach parts
        text_part = MIMEText(text_content, 'plain')
        html_part = MIMEText(html_content, 'html')
        
        msg.attach(text_part)
        msg.attach(html_part)
        
        # Send email
        if settings.SMTP_ENABLED:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                
                server.send_message(msg)
                
            logger.info("Password reset email sent", email=email)
            return True
        else:
            # In development, just log the reset URL
            logger.info("Password reset email (dev mode)", email=email, reset_url=reset_url)
            return True
            
    except Exception as e:
        logger.error("Failed to send password reset email", email=email, error=str(e))
        return False


async def send_welcome_email(
    email: str,
    name: str,
    temporary_password: Optional[str] = None
) -> bool:
    """
    Send welcome email to new user.
    
    Args:
        email: User's email address
        name: User's full name
        temporary_password: Temporary password if applicable
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        subject = "Welcome to UCC Event Manager"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Welcome to UCC Event Manager</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2c3e50;">Welcome to UCC Event Manager!</h2>
                
                <p>Hello {name},</p>
                
                <p>Welcome to UCC Event Manager! Your account has been successfully created.</p>
                
                {"<p><strong>Your temporary password is: " + temporary_password + "</strong></p>" if temporary_password else ""}
                {"<p>Please log in and change your password as soon as possible.</p>" if temporary_password else ""}
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/login" 
                       style="background-color: #27ae60; color: white; padding: 12px 30px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Login to Your Account
                    </a>
                </div>
                
                <p>If you have any questions, please don't hesitate to contact our support team.</p>
                
                <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p style="font-size: 12px; color: #666;">
                    This is an automated message from UCC Event Manager.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Create and send message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.SMTP_FROM_EMAIL
        msg['To'] = email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        if settings.SMTP_ENABLED:
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                if settings.SMTP_TLS:
                    server.starttls()
                if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                    server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
                
                server.send_message(msg)
                
            logger.info("Welcome email sent", email=email)
            return True
        else:
            logger.info("Welcome email (dev mode)", email=email)
            return True
            
    except Exception as e:
        logger.error("Failed to send welcome email", email=email, error=str(e))
        return False 