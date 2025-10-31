from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse


def send_email(subject, template_name, context, recipient_email, plain_text_fallback=None):
    """
    Generic email sender function for any type of email
    
    Args:
        subject: Email subject line
        template_name: Path to HTML email template
        context: Dictionary of template context variables
        recipient_email: Recipient's email address
        plain_text_fallback: Optional plain text template path, if None strips HTML
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Render HTML message
        html_message = render_to_string(template_name, context)
        
        # Generate plain text message
        if plain_text_fallback:
            plain_message = render_to_string(plain_text_fallback, context)
        else:
            plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def send_verification_email(user, request):
    """
    Send email verification email to user
    """
    # Generate verification URL
    verification_url = request.build_absolute_uri(
        reverse('accounts:verify_email', args=[user.verification_token])
    )
    
    # Email context
    context = {
        'user': user,
        'verification_url': verification_url,
        'site_name': 'Restaurant Reservation',
    }
    
    # Email subject
    subject = 'Verify your email address - Restaurant Reservation'
    
    # Use the generic send_email function
    return send_email(
        subject=subject,
        template_name='emails/verification_email.html',
        context=context,
        recipient_email=user.email
    )

def send_password_reset_code_email(user, reset_code):
    """
    Send password reset code email to user
    """
    # Email context
    context = {
        'user': user,
        'reset_code': reset_code,
        'site_name': 'Restaurant Reservation',
    }
    
    # Email subject
    subject = 'Password Reset Code - Restaurant Reservation'
    
    # Use the generic send_email function
    return send_email(
        subject=subject,
        template_name='emails/password_reset_code_email.html',
        context=context,
        recipient_email=user.email
    )