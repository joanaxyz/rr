from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ..models import User
from .utils import validate_password
from supabase import create_client
from django.conf import settings
from functools import wraps
import json
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

def login_render(request):
    return render(request, 'rr_app/login.html')

def register_render(request):
    return render(request, 'rr_app/register.html')

def forgot_pass_render(request):
    return render(request, 'rr_app/fpass.html')

def reset_password_render(request):
    return render(request, 'rr_app/reset_password.html')

def get_supabase_client():
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

# =========================
# REGISTER USER
# =========================
@csrf_exempt
@require_http_methods(["POST"])
def register_user(request):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")
        c_password = data.get("c_password")
        first_name = data.get("first_name")
        last_name = data.get("last_name")

        if not all([email, password, c_password, first_name, last_name]):
            return JsonResponse({"success": False, "error": "Please input all fields"}, status=400)

        # Email validation
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({"success": False, "error": "Invalid email format"}, status=400)

        # Password validation
        valid, message = validate_password(password)
        if not valid:
            return JsonResponse({"success": False, "error": message}, status=400)

        # Confirm password
        if password != c_password:
            return JsonResponse({"success": False, "error": "Passwords do not match"}, status=400)

        supabase = get_supabase_client()
        auth_response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {"first_name": first_name, "last_name": last_name}
            }
        })
        user = auth_response.user
        if not user:
            return JsonResponse({"success": False, "error": "Registration failed"}, status=400)

        # Create Django user
        django_user = User.objects.create(
            supabase_id=user.id,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=True
        )
        django_user.update_last_login()

        return JsonResponse({
            "success": True,
            "message": "Registration successful! Please check your email to verify your account.",
            "user": {"id": django_user.id, "email": django_user.email}
        })

    except Exception as e:
        error_message = str(e)
        if "User already registered" in error_message:
            return JsonResponse({"success": False, "error": "Email already exists"}, status=400)
        return JsonResponse({"success": False, "error": error_message}, status=400)

# =========================
# LOGIN USER
# =========================
@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return JsonResponse({"success": False, "error": "Please input all fields"}, status=400)

        supabase = get_supabase_client()
        auth_response = supabase.auth.sign_in_with_password({"email": email, "password": password})

        if auth_response.user and auth_response.session:
            access_token = auth_response.session.access_token
            user = supabase.auth.get_user(access_token).user
            django_user = User.objects.filter(supabase_id=user.id).first()
            django_user.update_last_login()
            return JsonResponse({
                "success": True,
                "message": "Login successful",
                "session": {
                    "access_token": access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "expires_at": auth_response.session.expires_at
                },
                "user": {
                    "id": django_user.id,
                    "supabase_id": django_user.supabase_id,
                    "email": django_user.email,
                    "first_name": django_user.first_name,
                    "last_name": django_user.last_name,
                    "role": django_user.role,
                    "is_admin": django_user.is_admin()
                }
            })
        else:
            return JsonResponse({"success": False, "error": "Invalid credentials"}, status=400)

    except Exception as e:
        error_message = str(e)
        if "Invalid login credentials" in error_message:
            return JsonResponse({"success": False, "error": "Email or password is incorrect"}, status=400)
        elif "Email not confirmed" in error_message:
            return JsonResponse({"success": False, "error": "Please verify your email first"}, status=400)
        return JsonResponse({"success": False, "error": error_message}, status=400)

# =========================
# FORGOT PASSWORD
# =========================
@csrf_exempt
@require_http_methods(["POST"])
def fpass_request(request):
    try:
        data = json.loads(request.body)
        email = data.get("email")
        if not email:
            return JsonResponse({"success": False, "error": "Please input email"}, status=400)

        supabase = get_supabase_client()
        supabase.auth.reset_password_email(email, {
            "redirect_to": f"{request.build_absolute_uri('/')[:-1]}/rr/reset-password/"
        })
        return JsonResponse({"success": True, "message": "Password reset email sent. Please check your inbox."})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

# =========================
# RESET PASSWORD
# =========================
@csrf_exempt
@require_http_methods(["POST"])
def reset_password_request(request):
    try:
        data = json.loads(request.body)
        access_token = data.get("access_token")
        password = data.get("password")
        c_password = data.get("c_password")

        if not all([access_token, password, c_password]):
            return JsonResponse({"success": False, "error": "Missing required fields"}, status=400)

        # Validate password
        valid, message = validate_password(password)
        if not valid:
            return JsonResponse({"success": False, "error": message}, status=400)

        # Confirm password
        if password != c_password:
            return JsonResponse({"success": False, "error": "Passwords do not match"}, status=400)

        supabase = get_supabase_client()
        supabase.auth.update_user({"password": password}, access_token)
        return JsonResponse({"success": True, "message": "Password updated successfully"})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

# =========================
# REFRESH TOKEN
# =========================
@csrf_exempt
@require_http_methods(["POST"])
def refresh_token(request):
    try:
        data = json.loads(request.body)
        refresh_token = data.get("refresh_token")
        if not refresh_token:
            return JsonResponse({"success": False, "error": "Refresh token required"}, status=400)

        supabase = get_supabase_client()
        auth_response = supabase.auth.refresh_session(refresh_token)
        if auth_response.session:
            return JsonResponse({
                "success": True,
                "session": {
                    "access_token": auth_response.session.access_token,
                    "refresh_token": auth_response.session.refresh_token,
                    "expires_at": auth_response.session.expires_at
                }
            })
        else:
            return JsonResponse({"success": False, "error": "Failed to refresh token"}, status=400)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)

# =========================
# SUPABASE AUTH DECORATOR
# =========================
def supabase_auth_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return JsonResponse({"success": False, "error": "Authentication required"}, status=401)
        token = auth_header.split('Bearer ')[1]
        supabase = get_supabase_client()
        try:
            user = supabase.auth.get_user(token).user
            if user:
                django_user = User.objects.filter(supabase_id=user.id).first()
                request.user = django_user
                request.supabase_user = user
                return view_func(request, *args, **kwargs)
        except Exception:
            pass
        return JsonResponse({"success": False, "error": "Invalid token"}, status=401)
    return wrapper

@supabase_auth_required
def get_current_user(request):
    return JsonResponse({
        "success": True,
        "user": {
            "id": request.user.id,
            "supabase_id": request.user.supabase_id,
            "email": request.user.email,
            "first_name": request.user.first_name,
            "last_name": request.user.last_name,
            "role": request.user.role,
            "is_admin": request.user.is_admin(),
        }
    })