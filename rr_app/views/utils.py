import re
    
def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def validate_password(password):
    min_length = 8
    max_length = 20
    if not password:
        return False, "Password cannot be empty"
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters"
    if len(password) > max_length:
        return False, f"Password cannot exceed {max_length} characters"
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"
    return True, "Password is valid"
