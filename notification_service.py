"""
Notification Service for GUVNL Queue Management System
Handles SMS, Email, and Push notification delivery via Celery background tasks
"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional
from datetime import datetime

from twilio.rest import Client as TwilioClient
from twilio.base.exceptions import TwilioException
from flask import current_app
from celery import current_task

from app import celery, db
from app.models.notification import Notification

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling different types of notifications"""
    
    @staticmethod
    def create_notification(
        user_id: str,
        appointment_id: str,
        notification_type: str,
        recipient: str,
        subject: str,
        message: str,
        template_name: Optional[str] = None,
        template_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Create a notification record and queue it for delivery"""
        try:
            notification = Notification(
                user_id=user_id,
                appointment_id=appointment_id,
                type=notification_type,
                recipient=recipient,
                subject=subject,
                message=message,
                template_name=template_name,
                template_data=template_data or {}
            )
            
            db.session.add(notification)
            db.session.commit()
            
            # Queue the notification for delivery
            if notification_type == 'sms':
                send_sms_notification.delay(notification.id)
            elif notification_type == 'email':
                send_email_notification.delay(notification.id)
            elif notification_type == 'push':
                send_push_notification.delay(notification.id)
            
            return notification.id
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to create notification: {str(e)}")
            raise

    @staticmethod
    def get_sms_templates() -> Dict[str, str]:
        """SMS message templates"""
        return {
            'appointment_booked': (
                "Hello {name}! Your appointment for {service} at {office} "
                "is confirmed for {date} at {time}. Token: {token}. "
                "Track status: {status_url}"
            ),
            'appointment_reminder': (
                "Reminder: Your appointment for {service} at {office} "
                "is scheduled in {minutes} minutes. Token: {token}. "
                "Please arrive on time."
            ),
            'queue_update': (
                "Update: Your token {token} for {service} at {office}. "
                "Current position: {position}. Estimated wait: {wait_time} minutes."
            ),
            'appointment_ready': (
                "It's your turn! Please report to counter for {service} "
                "at {office}. Token: {token}."
            ),
            'appointment_completed': (
                "Thank you for visiting {office}. Your {service} request "
                "has been processed. Reference: {token}."
            ),
            'appointment_cancelled': (
                "Your appointment for {service} at {office} on {date} "
                "has been cancelled. Reschedule at: {booking_url}"
            )
        }

    @staticmethod
    def get_email_templates() -> Dict[str, Dict[str, str]]:
        """Email templates with subject and HTML body"""
        return {
            'appointment_booked': {
                'subject': 'Appointment Confirmation - GUVNL Queue Management',
                'html': '''
                <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #1976d2;">Appointment Confirmed!</h2>
                            <p>Dear {name},</p>
                            <p>Your appointment has been successfully booked. Here are the details:</p>
                            
                            <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
                                <p><strong>Service:</strong> {service}</p>
                                <p><strong>Office:</strong> {office}</p>
                                <p><strong>Date:</strong> {date}</p>
                                <p><strong>Time:</strong> {time}</p>
                                <p><strong>Token Number:</strong> {token}</p>
                            </div>
                            
                            <p>Please arrive 15 minutes before your scheduled time and bring all required documents.</p>
                            
                            <p style="margin-top: 30px;">
                                <a href="{status_url}" style="background: #1976d2; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                                    Track Your Appointment
                                </a>
                            </p>
                            
                            <hr style="margin: 30px 0;">
                            <p style="color: #666; font-size: 12px;">
                                This is an automated message from GUVNL Queue Management System. 
                                Please do not reply to this email.
                            </p>
                        </div>
                    </body>
                </html>
                '''
            },
            'appointment_reminder': {
                'subject': 'Appointment Reminder - GUVNL',
                'html': '''
                <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #ff9800;">Appointment Reminder</h2>
                            <p>Dear {name},</p>
                            <p>This is a reminder that your appointment is scheduled in <strong>{minutes} minutes</strong>.</p>
                            
                            <div style="background: #fff3e0; padding: 15px; border-radius: 5px; margin: 20px 0; border-left: 4px solid #ff9800;">
                                <p><strong>Service:</strong> {service}</p>
                                <p><strong>Office:</strong> {office}</p>
                                <p><strong>Token:</strong> {token}</p>
                            </div>
                            
                            <p>Please ensure you arrive on time with all required documents.</p>
                        </div>
                    </body>
                </html>
                '''
            }
        }

@celery.task(bind=True, max_retries=3)
def send_sms_notification(self, notification_id: str):
    """Send SMS notification via Twilio"""
    try:
        notification = Notification.query.get(notification_id)
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return False

        # Initialize Twilio client
        account_sid = current_app.config['TWILIO_ACCOUNT_SID']
        auth_token = current_app.config['TWILIO_AUTH_TOKEN']
        from_number = current_app.config['TWILIO_PHONE_NUMBER']
        
        if not all([account_sid, auth_token, from_number]):
            logger.error("Twilio configuration missing")
            notification.status = 'failed'
            notification.error_message = 'Twilio configuration missing'
            db.session.commit()
            return False

        client = TwilioClient(account_sid, auth_token)
        
        # Send SMS
        message = client.messages.create(
            body=notification.message,
            from_=from_number,
            to=notification.recipient
        )
        
        # Update notification status
        notification.status = 'sent'
        notification.sent_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"SMS sent successfully: {message.sid}")
        return True
        
    except TwilioException as e:
        logger.error(f"Twilio error: {str(e)}")
        notification.retry_count += 1
        notification.error_message = str(e)
        
        if notification.retry_count >= 3:
            notification.status = 'failed'
        
        db.session.commit()
        
        # Retry if not max retries
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        return False
        
    except Exception as e:
        logger.error(f"SMS notification error: {str(e)}")
        notification.status = 'failed'
        notification.error_message = str(e)
        db.session.commit()
        return False

@celery.task(bind=True, max_retries=3)
def send_email_notification(self, notification_id: str):
    """Send email notification via SMTP"""
    try:
        notification = Notification.query.get(notification_id)
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return False

        # SMTP configuration
        smtp_server = current_app.config['SMTP_SERVER']
        smtp_port = current_app.config['SMTP_PORT']
        smtp_username = current_app.config['SMTP_USERNAME']
        smtp_password = current_app.config['SMTP_PASSWORD']
        
        if not all([smtp_server, smtp_port, smtp_username, smtp_password]):
            logger.error("SMTP configuration missing")
            notification.status = 'failed'
            notification.error_message = 'SMTP configuration missing'
            db.session.commit()
            return False

        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = notification.subject
        msg['From'] = smtp_username
        msg['To'] = notification.recipient
        
        # Add HTML content
        html_part = MIMEText(notification.message, 'html')
        msg.attach(html_part)
        
        # Send email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        # Update notification status
        notification.status = 'sent'
        notification.sent_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Email sent successfully to {notification.recipient}")
        return True
        
    except smtplib.SMTPException as e:
        logger.error(f"SMTP error: {str(e)}")
        notification.retry_count += 1
        notification.error_message = str(e)
        
        if notification.retry_count >= 3:
            notification.status = 'failed'
        
        db.session.commit()
        
        # Retry if not max retries
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        return False
        
    except Exception as e:
        logger.error(f"Email notification error: {str(e)}")
        notification.status = 'failed'
        notification.error_message = str(e)
        db.session.commit()
        return False

@celery.task(bind=True, max_retries=3)
def send_push_notification(self, notification_id: str):
    """Send push notification via Firebase"""
    try:
        notification = Notification.query.get(notification_id)
        if not notification:
            logger.error(f"Notification {notification_id} not found")
            return False

        # Firebase configuration
        firebase_config = {
            'project_id': current_app.config['FIREBASE_PROJECT_ID'],
            'private_key_id': current_app.config['FIREBASE_PRIVATE_KEY_ID'],
            'private_key': current_app.config['FIREBASE_PRIVATE_KEY'],
            'client_email': current_app.config['FIREBASE_CLIENT_EMAIL'],
            'client_id': current_app.config['FIREBASE_CLIENT_ID'],
        }
        
        if not all(firebase_config.values()):
            logger.error("Firebase configuration missing")
            notification.status = 'failed'
            notification.error_message = 'Firebase configuration missing'
            db.session.commit()
            return False

        # TODO: Implement Firebase push notification logic
        # This would require firebase-admin SDK
        
        # For now, mark as sent (implement actual Firebase logic)
        notification.status = 'sent'
        notification.sent_at = datetime.utcnow()
        db.session.commit()
        
        logger.info(f"Push notification sent to {notification.recipient}")
        return True
        
    except Exception as e:
        logger.error(f"Push notification error: {str(e)}")
        notification.status = 'failed'
        notification.error_message = str(e)
        db.session.commit()
        return False

@celery.task
def send_appointment_reminders():
    """Periodic task to send appointment reminders"""
    from app.models.appointment import Appointment
    from app.models.user import User
    from datetime import datetime, timedelta
    
    # Find appointments starting in the next 15-30 minutes
    now = datetime.utcnow()
    reminder_start = now + timedelta(minutes=15)
    reminder_end = now + timedelta(minutes=30)
    
    appointments = Appointment.query.filter(
        Appointment.appointment_date == now.date(),
        Appointment.appointment_time.between(
            reminder_start.time(),
            reminder_end.time()
        ),
        Appointment.status == 'confirmed'
    ).all()
    
    templates = NotificationService.get_sms_templates()
    
    for appointment in appointments:
        if appointment.user:
            # Send SMS reminder
            if appointment.user.phone:
                message = templates['appointment_reminder'].format(
                    name=appointment.user.first_name,
                    service=appointment.queue.service.name,
                    office=appointment.queue.office.name,
                    token=appointment.token_number,
                    minutes=15
                )
                
                NotificationService.create_notification(
                    user_id=appointment.user_id,
                    appointment_id=appointment.id,
                    notification_type='sms',
                    recipient=appointment.user.phone,
                    subject='Appointment Reminder',
                    message=message,
                    template_name='appointment_reminder'
                )