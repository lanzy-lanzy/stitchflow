"""
SMS Service using Semaphore API
Send SMS notifications to customers and tailors

Official Semaphore API Documentation:
- Endpoint: POST https://api.semaphore.co/api/v4/messages
- Rate Limit: 120 requests per minute
- Character Limit: 160 characters per SMS (auto-split if longer)
- Sender Name: Customizable (defaults to SEMAPHORE if not set)

Reference: https://semaphore.co/docs
"""
import requests
import logging
from django.conf import settings
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class SemaphoreSMS:
    """Service to send SMS via Semaphore API
    
    API Endpoint: POST https://api.semaphore.co/api/v4/messages
    Rate Limit: 120 requests per minute
    
    Required Parameters:
    - apikey: Your Semaphore API key
    - number: Recipient phone number (09998887777 or +639998887777)
    - message: SMS message (auto-split if > 160 chars)
    
    Optional Parameters:
    - sendername: Sender name (defaults to SEMAPHORE)
    """
    
    # Get API key from settings, default to empty string if not set
    API_KEY = getattr(settings, 'SEMAPHORE_API_KEY', '')
    SENDER_NAME = getattr(settings, 'SEMAPHORE_SENDER_NAME', 'elsenior')
    API_URL = 'https://api.semaphore.co/api/v4/messages'  # Official Semaphore endpoint
    
    @classmethod
    def send_message(cls, message, number):
        """
        Send SMS message to a phone number via Semaphore API
        
        Args:
            message (str): The message content to send
                          - Max 160 characters per SMS
                          - Messages longer than 160 chars are auto-split
                          - Do NOT start with 'TEST' (silently ignored)
            number (str): Phone number to send to
                         - Philippine: 09998887777
                         - International: +639998887777
            
        Returns:
            tuple: (success: bool, response_data: dict or error_message: str)
            
        Response contains:
            - message_id: Unique identifier for the message
            - user_id: User who sent the message
            - status: pending/sent/failed/refunded
            - recipient: Phone number sent to
            - message: Message body
            - sender_name: Sender name used
        """
        # Validation
        if not cls.API_KEY:
            logger.error('Semaphore API key not configured')
            return False, 'Semaphore API key not configured'
        
        if not number:
            logger.error('Phone number not provided')
            return False, 'Phone number is required'
        
        if not message:
            logger.error('Message content is required')
            return False, 'Message content is required'
        
        # Warn if message starts with TEST (Semaphore silently ignores these)
        if message.strip().upper().startswith('TEST'):
            logger.warning(f'Message to {number} starts with TEST - may be silently ignored by Semaphore')
        
        try:
            # Prepare parameters according to Semaphore API docs
            params = {
                'apikey': cls.API_KEY,
                'sendername': cls.SENDER_NAME,
                'message': message,
                'number': number
            }
            
            # Build URL with query parameters
            url = f"{cls.API_URL}?{urlencode(params)}"
            
            logger.debug(f'Sending SMS to {number} via {cls.API_URL}')
            
            # Send POST request to Semaphore API
            # Rate limit: 120 requests per minute
            response = requests.post(url, timeout=10)
            
            # Log the request status
            logger.info(f'SMS API response: Status {response.status_code} for number {number}')
            
            # Check if successful (Semaphore returns 200 on success)
            if response.status_code == 200:
                response_data = response.json()
                
                # Semaphore returns array of messages (one per recipient)
                if isinstance(response_data, list) and len(response_data) > 0:
                    msg_data = response_data[0]
                    logger.info(
                        f'SMS sent successfully to {number}. '
                        f'Message ID: {msg_data.get("message_id", "N/A")}, '
                        f'Status: {msg_data.get("status", "unknown")}'
                    )
                    return True, response_data
                else:
                    logger.warning(f'Unexpected response format from Semaphore: {response_data}')
                    return True, response_data
            else:
                error_msg = f'SMS API returned status {response.status_code}'
                logger.error(f'{error_msg}: {response.text}')
                
                # Parse error details if available
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict) and 'error' in error_data:
                        error_msg = f"{error_msg} - {error_data['error']}"
                except:
                    pass
                
                return False, error_msg
                
        except requests.exceptions.Timeout:
            error_msg = 'SMS API request timeout (exceeded 10 seconds)'
            logger.error(error_msg)
            return False, error_msg
        except requests.exceptions.ConnectionError:
            error_msg = 'SMS API connection error - unable to reach Semaphore'
            logger.error(error_msg)
            return False, error_msg
        except requests.exceptions.RequestException as e:
            error_msg = f'SMS API request failed: {str(e)}'
            logger.error(error_msg)
            return False, error_msg
        except ValueError as e:
            error_msg = f'Invalid response from SMS API: {str(e)}'
            logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f'Unexpected error sending SMS: {str(e)}'
            logger.error(error_msg)
            return False, error_msg
    
    @classmethod
    def notify_customer_ready_for_pickup(cls, customer_name, customer_phone, order_id):
        """
        Send notification to customer that their garment is ready for pickup
        
        Args:
            customer_name (str): Customer's name
            customer_phone (str): Customer's phone number
            order_id (int): Order ID
            
        Returns:
            tuple: (success: bool, message: str)
        """
        message = f"Hi {customer_name}, your garment for Order #{order_id} is ready for pickup at El Senior Dumingag. Thank you!"
        
        logger.info(f'Sending ready-for-pickup notification to {customer_name} ({customer_phone})')
        success, response = cls.send_message(message, customer_phone)
        
        if success:
            logger.info(f'Successfully sent ready-for-pickup SMS to {customer_phone}')
            return True, 'Customer notified successfully'
        else:
            logger.error(f'Failed to send SMS to {customer_phone}: {response}')
            return False, f'Failed to notify customer: {response}'
    
    @classmethod
    def notify_tailor_commission_ready(cls, tailor_name, tailor_phone, commission_amount, order_id):
        """
        Send notification to tailor about commission payment
        
        Args:
            tailor_name (str): Tailor's name
            tailor_phone (str): Tailor's phone number
            commission_amount (Decimal): Commission amount
            order_id (int): Order ID
            
        Returns:
            tuple: (success: bool, message: str)
        """
        message = f"Hi {tailor_name}, commission of ₱{commission_amount} for Order #{order_id} has been approved. Please contact admin for payment."
        
        logger.info(f'Sending commission notification to {tailor_name} ({tailor_phone})')
        success, response = cls.send_message(message, tailor_phone)
        
        if success:
            logger.info(f'Successfully sent commission SMS to {tailor_phone}')
            return True, 'Tailor notified successfully'
        else:
            logger.error(f'Failed to send SMS to {tailor_phone}: {response}')
            return False, f'Failed to notify tailor: {response}'
