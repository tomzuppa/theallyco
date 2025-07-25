# users/views/register.py - Simplified Token-based Registration

import logging
import string
import secrets
from datetime import datetime
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse

# Internal imports
from ..forms import RegisterForm
from ..utils.emails import send_activation_email_from_token
from project_root import messages as sysmsg
from core.utils import get_signup_branding, validate_recaptcha

User = get_user_model()
logger = logging.getLogger(__name__)

# Configuration from settings
# Reference: settings/base.py - Security and rate limiting settings
MAX_ATTEMPTS = settings.MAX_ATTEMPTS                      # 3
MAX_RESEND_COUNT = settings.MAX_RESEND_COUNT              # 3  
MAX_ABANDON_COUNT = settings.MAX_ABANDON_COUNT            # 3
TOKEN_SUFFIX_LENGTH = settings.TOKEN_SUFFIX_LENGTH        # 15
TOKEN_EXPIRY = settings.ACTIVATION_TOKEN_EXPIRY           # 20 seconds (testing)

# Session keys for registration process
SESSION_KEYS = {
    'USER_DATA': 'reg_user_data',
    'VERIFICATION_CODE': 'reg_verification_code', 
    'CREATED_AT': 'reg_created_at',
    'ATTEMPTS': 'reg_attempts',
    'RESEND_COUNT': 'reg_resend_count',
    'ABANDON_COUNT': 'reg_abandon_count'  # Persistent across sessions
}


class RegisterTokenView(View):
    """
    Simplified registration with email verification.
    
    Flow: Form → Verification → Complete Registration
    Limits: 3 attempts, 3 resends, 3 abandons → Block
    Token: 15 characters, expires in 20 seconds (testing)
    
    Business Rules:
    - Exit and return ALWAYS counts as abandon and requires restart
    - Token is sent complete (not split into parts)
    - reCAPTCHA validation required
    - All counters reset on successful registration
    
    Reference: URLs mapped in users/urls.py
    Reference: Templates in templates/users/register_token.html
    """
    
    def dispatch(self, request, *args, **kwargs):
        """
        Pre-request security check for abandon count blocking.
        
        Executes before GET/POST methods to validate user access.
        Blocks if abandon count exceeded.
        
        Args:
            request: Django request object
            
        Returns:
            HttpResponse: Redirect to blocked page if limits exceeded
            
        Reference: users/views/blocked.py - BlockedView for rate-limited users
        """
        abandon_count = request.session.get(SESSION_KEYS['ABANDON_COUNT'], 0)
        
        if abandon_count >= MAX_ABANDON_COUNT:
            messages.error(request, sysmsg.MESSAGES["MAX_ATTEMPTS_EXCEEDED_BLOCKED"])
            return redirect('users:blocked')
            
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        """
        Handle GET requests for registration page.
        
        Manages:
        - Active session detection
        - Expired session handling with abandon counting
        - Session cleanup and form initialization
        
        Returns:
            HttpResponse: Rendered registration form or verification step
        """
        # If valid session exists, show verification step
        if self._has_valid_session(request):
            return self._render_verification_step(request)
        
        # If expired session exists, count as abandon
        if self._has_expired_session(request):
            self._handle_abandon(request, reason="token_expired")
            
        # Clean any previous session and show form
        self._clear_registration_session(request)
        form = RegisterForm()
        return render(request, 'users/register_token.html', {
            'form': form,
            'step': 'form',
            'branding': get_signup_branding(),
            'show_token_field': False,
            'disable_fields': False,
            'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY
        })
    
    def post(self, request):
        """
        Route POST requests to appropriate handlers based on action.
        
        Checks for specific button names in POST data:
        - 'resend_code': Handle resend verification code
        - 'verify_code': Handle verification code submission
        - Otherwise: Handle initial registration form
        
        Args:
            request: Django request object
            
        Returns:
            HttpResponse: Response from appropriate handler
        """
        # Check which button was clicked based on name attribute
        if 'resend_code' in request.POST:
            return self._handle_resend(request)
        elif 'verify_code' in request.POST:
            return self._handle_verification(request)
        else:
            return self._handle_registration_form(request)
    
    def _handle_registration_form(self, request):
        """
        Process initial registration form and send verification code.
        
        Process:
        1. Check for existing session (counts as abandon)
        2. Validate reCAPTCHA
        3. Validate form data
        4. Check for existing user
        5. Generate verification code
        6. Send email
        7. Transition to verification step
        
        Args:
            request: Django request object
            
        Returns:
            HttpResponse: Rendered form or verification view
            
        Reference: users/forms.py - RegisterForm validation rules
        """
        # If active session exists, it's an abandon
        if self._has_any_session(request):
            self._handle_abandon(request, reason="new_registration_attempt")
        
        form = RegisterForm(request.POST)
        
        # Validate reCAPTCHA first using core utility
        if not validate_recaptcha(request):
            return render(request, 'users/register_token.html', {
                'form': form,
                'step': 'form',
                'branding': get_signup_branding(),
                'show_token_field': False,
                'disable_fields': False,
                'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY
            })
        
        if not form.is_valid():
            return render(request, 'users/register_token.html', {
                'form': form,
                'step': 'form',
                'branding': get_signup_branding(),
                'show_token_field': False,
                'disable_fields': False,
                'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY
            })
        
        # Check if email already exists
        if User.objects.filter(email=form.cleaned_data['email']).exists():
            messages.error(request, sysmsg.MESSAGES["USER_ALREADY_EXISTS"])
            return render(request, 'users/register_token.html', {
                'form': form,
                'step': 'form',
                'branding': get_signup_branding(),
                'show_token_field': False,
                'disable_fields': False,
                'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY
            })
        
        # Save data and generate code
        user_data = form.cleaned_data
        verification_code = self._generate_verification_code()
        
        # Create new session
        request.session.update({
            SESSION_KEYS['USER_DATA']: user_data,
            SESSION_KEYS['VERIFICATION_CODE']: verification_code,
            SESSION_KEYS['CREATED_AT']: timezone.now().isoformat(),
            SESSION_KEYS['ATTEMPTS']: 0,
            SESSION_KEYS['RESEND_COUNT']: 0
        })
        
        # Send verification email
        try:
            send_activation_email_from_token(
                user_data['email'], 
                request, 
                verification_code
            )
            # Email sent successfully
            messages.success(
                request, 
                sysmsg.MESSAGES["ACTIVATION_INSTRUCTIONS"].format(
                    email=user_data["email"]
                )
            )
            logger.info(f"Verification code sent to {user_data['email']}")
            
            # Force save session before rendering
            request.session.save()
            
            # Render verification step
            return self._render_verification_step(request)
            
        except Exception as e:
            # Log the full exception for debugging
            logger.error(f"Error sending verification email to {user_data['email']}: {e}", exc_info=True)
            
            # Clear session on error
            self._clear_registration_session(request)
            
            # Show error message
            messages.error(request, sysmsg.MESSAGES["ERROR_SENDING_EMAIL"])
            
            # Return to registration form
            return render(request, 'users/register_token.html', {
                'form': form,
                'step': 'form',
                'branding': get_signup_branding(),
                'show_token_field': False,
                'disable_fields': False,
                'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY
            })
    
    def _handle_verification(self, request):
        """
        Handle verification code submission and user account creation.
        
        Process:
        1. Validate session exists and is not expired
        2. Check verification attempt limits
        3. Validate submitted code
        4. Compare with stored code
        5. Create user account atomically
        6. Handle all error scenarios
        
        Args:
            request: Django request object
            
        Returns:
            HttpResponse: Success redirect or error form
            
        Reference: users/models.py - User model creation
        """
        if not self._has_valid_session(request):
            messages.error(request, sysmsg.MESSAGES["SESSION_EMAIL_MISSING"])
            self._handle_abandon(request, reason="session_expired_on_verify")
            return redirect('users:register')
        
        # Check verification attempt limits
        attempts = request.session.get(SESSION_KEYS['ATTEMPTS'], 0)
        if attempts >= MAX_ATTEMPTS:
            messages.error(request, sysmsg.MESSAGES["MAX_ATTEMPTS_EXCEEDED_BLOCKED"])
            self._clear_registration_session(request)
            return redirect('users:blocked')
        
        # Get submitted code from textarea
        submitted_code = request.POST.get('verification_code', '').strip()
        stored_code = request.session.get(SESSION_KEYS['VERIFICATION_CODE'])
        
        if not submitted_code:
            messages.error(request, sysmsg.MESSAGES["ACTIVATION_TOKEN_REQUIRED"])
            return self._render_verification_step(request)
        
        # Verify code matches
        if submitted_code != stored_code:
            # Increment attempt counter
            new_attempts = attempts + 1
            request.session[SESSION_KEYS['ATTEMPTS']] = new_attempts
            
            remaining = MAX_ATTEMPTS - new_attempts
            if remaining > 0:
                messages.error(
                    request, 
                    sysmsg.MESSAGES["INVALID_TOKEN_ATTEMPTS"].format(
                        attempts_left=remaining
                    )
                )
                return self._render_verification_step(request)
            else:
                messages.error(
                    request, 
                    sysmsg.MESSAGES["MAX_ATTEMPTS_EXCEEDED_BLOCKED"]
                )
                self._clear_registration_session(request)
                return redirect('users:blocked')
        
        # Code is correct - create user account
        try:
            user_data = request.session[SESSION_KEYS['USER_DATA']]
            
            with transaction.atomic():
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password1'],
                    is_verified=True,
                    terms_accepted=user_data.get('terms', False)
                )
            
            # Clear session completely (including abandon count)
            self._clear_registration_session(request, clear_abandon=True)
            
            messages.success(request, sysmsg.MESSAGES["ACTIVATION_SUCCESS"])
            logger.info(f"User successfully registered: {user.username}")
            
            return redirect('users:login')
            
        except Exception as e:
            logger.error(f"Error creating user account: {e}")
            messages.error(request, sysmsg.MESSAGES["GENERIC_ERROR"])
            self._clear_registration_session(request)
            return redirect('users:register')
    
    def _handle_resend(self, request):
        """
        Handle verification code resend with proper rate limiting.
        
        Process:
        1. Validate session exists and is valid
        2. Check resend count limits
        3. Increment resend counter
        4. Generate new verification code
        5. Send new email
        6. Reset attempt counter
        
        Args:
            request: Django request object
            
        Returns:
            HttpResponse: Rendered verification form or redirect
        """
        if not self._has_any_session(request):
            messages.error(request, sysmsg.MESSAGES["SESSION_EMAIL_MISSING"])
            return redirect('users:register')
        
        # Check resend limits
        resend_count = request.session.get(SESSION_KEYS['RESEND_COUNT'], 0)
        if resend_count >= MAX_RESEND_COUNT:
            messages.error(request, sysmsg.MESSAGES["RESEND_LIMIT_EXCEEDED"])
            self._clear_registration_session(request)
            return redirect('users:blocked')
        
        # Increment resend counter
        new_resend_count = resend_count + 1
        request.session[SESSION_KEYS['RESEND_COUNT']] = new_resend_count
        
        # Generate new verification code
        new_code = self._generate_verification_code()
        request.session[SESSION_KEYS['VERIFICATION_CODE']] = new_code
        request.session[SESSION_KEYS['CREATED_AT']] = timezone.now().isoformat()
        request.session[SESSION_KEYS['ATTEMPTS']] = 0  # Reset verification attempts
        
        # Send new verification email
        try:
            user_data = request.session[SESSION_KEYS['USER_DATA']]
            send_activation_email_from_token(
                user_data['email'], 
                request, 
                new_code
            )
            
            messages.success(
                request, 
                sysmsg.MESSAGES["ACTIVATION_RESENT"].format(
                    email=user_data['email']
                )
            )
            logger.info(
                f"Verification code resent to {user_data['email']} "
                f"({new_resend_count}/{MAX_RESEND_COUNT})"
            )
            
            return self._render_verification_step(request)
            
        except Exception as e:
            logger.error(f"Error resending verification code: {e}")
            messages.error(request, sysmsg.MESSAGES["ERROR_RESENDING_TOKEN"])
            self._clear_registration_session(request)
            return redirect('users:register')
    
    def _render_verification_step(self, request):
        """
        Render verification step template with current state.
        
        Provides all necessary context variables for the template to show:
        - Verification code textarea
        - Countdown timer
        - Verify and resend buttons with proper states
        
        Args:
            request: Django request object
            
        Returns:
            HttpResponse: Rendered verification template
            
        Reference: templates/users/register_token.html - Registration template
        """
        user_data = request.session.get(SESSION_KEYS['USER_DATA'], {})
        attempts = request.session.get(SESSION_KEYS['ATTEMPTS'], 0)
        resend_count = request.session.get(SESSION_KEYS['RESEND_COUNT'], 0)
        time_remaining = self._get_time_remaining(request)
        
        # Log for debugging
        logger.info(
            f"Rendering verification step for {user_data.get('email', 'unknown')}: "
            f"time_remaining={time_remaining}, attempts={attempts}, "
            f"resend_count={resend_count}"
        )
        
        # Create form with user data for display (read-only)
        form = RegisterForm(initial=user_data)
        
        context = {
            # Form object (required by _form_fields_register.html)
            'form': form,
            
            # Step indicator
            'step': 'verify',
            
            # User information
            'email': user_data.get('email', ''),
            
            # Attempt counters
            'attempts_remaining': MAX_ATTEMPTS - attempts,
            'resends_remaining': MAX_RESEND_COUNT - resend_count,
            
            # Time tracking
            'time_remaining': time_remaining,
            'countdown': time_remaining,  # For JavaScript timer
            
            # State flags
            'show_token_field': True,  # Shows textarea
            'disable_fields': True,    # Disables form fields
            'token_expired': time_remaining <= 0,
            'can_verify': time_remaining > 0 and attempts < MAX_ATTEMPTS,
            'can_resend': resend_count  < MAX_RESEND_COUNT and time_remaining <= 0,
            
            # Counter information
            'resend_count': resend_count,
            'max_resend_count': MAX_RESEND_COUNT,
            
            # Other required context
            'branding': get_signup_branding(),
            'RECAPTCHA_SITE_KEY': settings.RECAPTCHA_SITE_KEY
        }
        
        # Debug log the context
        logger.debug(f"Verification context: show_token_field={context['show_token_field']}, "
                    f"step={context['step']}, can_verify={context['can_verify']}")
        
        return render(request, 'users/register_token.html', context)
    
    def _has_valid_session(self, request):
        """
        Check if valid session exists and token has not expired.
        
        Args:
            request: Django request object
            
        Returns:
            bool: True if session is valid and not expired
        """
        return (
            self._has_any_session(request) and 
            not self._is_session_expired(request)
        )
    
    def _has_expired_session(self, request):
        """
        Check if session exists but token has expired.
        
        Args:
            request: Django request object
            
        Returns:
            bool: True if session exists but is expired
        """
        return (
            self._has_any_session(request) and 
            self._is_session_expired(request)
        )
    
    def _has_any_session(self, request):
        """
        Check if any registration session data exists.
        
        Args:
            request: Django request object
            
        Returns:
            bool: True if registration data exists in session
        """
        return bool(request.session.get(SESSION_KEYS['USER_DATA']))
    
    def _is_session_expired(self, request):
        """
        Check if current session has expired based on creation timestamp.
        
        Args:
            request: Django request object
            
        Returns:
            bool: True if session has expired or timestamp invalid
        """
        created_at_str = request.session.get(SESSION_KEYS['CREATED_AT'])
        if not created_at_str:
            return True
        
        try:
            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            elapsed = (timezone.now() - created_at).total_seconds()
            return elapsed > TOKEN_EXPIRY
        except (ValueError, TypeError):
            return True
    
    def _get_time_remaining(self, request):
        """
        Calculate remaining time before token expires.
        
        Args:
            request: Django request object
            
        Returns:
            int: Seconds remaining, 0 if expired or no timestamp
        """
        created_at_str = request.session.get(SESSION_KEYS['CREATED_AT'])
        if not created_at_str:
            return 0
        
        try:
            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
            elapsed = (timezone.now() - created_at).total_seconds()
            remaining = TOKEN_EXPIRY - elapsed
            return max(0, int(remaining))
        except (ValueError, TypeError):
            return 0
    
    def _generate_verification_code(self):
        """
        Generate random verification code avoiding confusing characters.
        
        Uses uppercase letters and digits, excluding confusing characters:
        - 0 (zero) vs O (letter O)
        - 1 (one) vs I (letter I)
        
        Returns:
            str: Random verification code of TOKEN_SUFFIX_LENGTH characters
        """
        # Use only uppercase letters and digits for clarity
        chars = string.ascii_uppercase + string.digits
        # Remove confusing characters
        chars = chars.replace('0', '').replace('O', '').replace('1', '').replace('I', '')
        return ''.join(secrets.choice(chars) for _ in range(TOKEN_SUFFIX_LENGTH))
    
    def _handle_abandon(self, request, reason="unknown"):
        """
        Handle registration abandonment and increment counter.
        
        Args:
            request: Django request object
            reason: String describing abandonment reason for logging
            
        Note: Abandon counter persists across sessions to track patterns
        """
        abandon_count = request.session.get(SESSION_KEYS['ABANDON_COUNT'], 0) + 1
        request.session[SESSION_KEYS['ABANDON_COUNT']] = abandon_count
        
        logger.info(
            f"Registration abandoned - Reason: {reason} - "
            f"Count: {abandon_count}/{MAX_ABANDON_COUNT}"
        )
        
        if abandon_count >= MAX_ABANDON_COUNT:
            messages.warning(
                request, 
                sysmsg.MESSAGES["MAX_ATTEMPTS_EXCEEDED_BLOCKED"]
            )
    
    def _clear_registration_session(self, request, clear_abandon=False):
        """
        Clear registration-specific session variables.
        
        Args:
            request: Django request object
            clear_abandon: bool - Whether to clear abandon_count (default: False)
            
        Note: Preserves abandon_count by default to track patterns across attempts
        """
        keys_to_clear = [
            SESSION_KEYS['USER_DATA'],
            SESSION_KEYS['VERIFICATION_CODE'],
            SESSION_KEYS['CREATED_AT'],
            SESSION_KEYS['ATTEMPTS'],
            SESSION_KEYS['RESEND_COUNT']
        ]
        
        if clear_abandon:
            keys_to_clear.append(SESSION_KEYS['ABANDON_COUNT'])
        
        for key in keys_to_clear:
            request.session.pop(key, None)


def check_token_status(request):
    """
    AJAX endpoint to check token validity status in real-time.
    
    Used by frontend JavaScript to update countdown timer and button states.
    
    Args:
        request: Django request object
        
    Returns:
        JsonResponse: {
            'valid': bool - Whether token is still valid
            'time_remaining': int - Seconds until expiration
            'expired': bool - Whether token has expired
        }
        
    Reference: Used by JavaScript in register_token.html template
    """
    view = RegisterTokenView()
    
    if not view._has_valid_session(request):
        return JsonResponse({
            'valid': False,
            'time_remaining': 0,
            'expired': True
        })
    
    time_remaining = view._get_time_remaining(request)
    
    return JsonResponse({
        'valid': time_remaining > 0,
        'time_remaining': time_remaining,
        'expired': time_remaining <= 0
    })