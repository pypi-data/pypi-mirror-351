"""
Firebase Admin Helper Functions

This module provides utility functions for managing Firebase Auth users and permissions.
These functions are designed for admin operations and testing purposes.
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
import firebase_admin
from firebase_admin import auth, credentials
from datetime import datetime, timezone, timedelta
from ipulse_shared_base_ftredge import log_info, log_warning, log_error, log_debug, LogLevel


def get_user_by_email(email: str, logger: Optional[logging.Logger] = None, print_out: bool = False) -> Optional[Dict[str, Any]]:
    """
    Get a user by email address from Firebase Auth.
    
    Args:
        email: User email address
        logger: Optional logger instance
        print_out: Whether to print output
        
    Returns:
        User dict or None if not found
    """
    try:
        user = auth.get_user_by_email(email)
        log_debug(f"Found user: {user.uid} ({user.email})", logger=logger, print_out=print_out)
        return user
    except auth.UserNotFoundError:
        log_debug(f"User not found: {email}", logger=logger, print_out=print_out)
        return None

def create_user_in_firebase(
    email: str, 
    password: str, 
    email_verified: bool = True,
    reset_password_if_exists: bool = False,
    logger: Optional[logging.Logger] = None, 
    print_out: bool = False
) -> Dict[str, Any]:
    """
    Create a user in Firebase Auth.
    
    Args:
        email: User email address
        password: User password
        email_verified: Whether the user's email is verified
        reset_password_if_exists: Whether to reset the password for existing users
        logger: Optional logger instance
        print_out: Whether to print output
        
    Returns:
        Created user dict
    """
    try:
        try:
            # Try to create the user first
            user = auth.create_user(
                email=email,
                password=password,
                email_verified=email_verified
            )
            log_info(f"Created user: {user.uid} ({user.email})", logger=logger, print_out=print_out)
            
            # Wait for Firebase Auth blocking function to complete
            log_info("Waiting for Firebase Auth blocking function to create profile and status...", logger=logger, print_out=print_out)
            time.sleep(5)
            
            return user
        except auth.EmailAlreadyExistsError:
            # User already exists
            user = auth.get_user_by_email(email)
            log_info(f"User already exists: {email} (UID: {user.uid})", logger=logger, print_out=print_out)
            
            # Reset password if enabled
            if reset_password_if_exists:
                auth.update_user(
                    user.uid,
                    password=password,
                    email_verified=email_verified
                )
                log_info(f"Reset password for existing user: {email}", logger=logger, print_out=print_out)
            
            return user
            
    except Exception as e:
        log_error(f"Error creating/updating user: {e}", logger=logger, print_out=print_out)
        raise
    
def update_user_custom_claims(
    user_uid: str, 
    primary_usertype: str, 
    secondary_usertypes: List[str], 
    approved: bool = True, 
    logger: Optional[logging.Logger] = None, 
    print_out: bool = False
) -> Dict[str, Any]:
    """
    Update a user's custom claims in Firebase Auth.
    
    Args:
        user_uid: User's UID
        primary_usertype: Primary user type
        secondary_usertypes: List of secondary user types
        approved: Whether the user is approved
        logger: Optional logger instance
        print_out: Whether to print output
        
    Returns:
        Updated custom claims dictionary
    """
    try:
        custom_claims = {
            "approved": approved,
            "primary_usertype": primary_usertype,
            "secondary_usertypes": secondary_usertypes
        }
        
        auth.set_custom_user_claims(user_uid, custom_claims)
        log_info(f"Updated custom claims for user {user_uid}: {custom_claims}", logger=logger, print_out=print_out)
        return custom_claims
    except Exception as e:
        log_error(f"Error updating custom claims: {e}", logger=logger, print_out=print_out)
        raise

def delete_user(user_uid: str, logger: Optional[logging.Logger] = None, print_out: bool = False) -> bool:
    """
    Delete a user from Firebase Auth.
    
    Args:
        user_uid: User's UID
        logger: Optional logger instance
        print_out: Whether to print output
        
    Returns:
        Success status
    """
    try:
        auth.delete_user(user_uid)
        log_info(f"Deleted user: {user_uid}", logger=logger, print_out=print_out)
        return True
    except auth.UserNotFoundError:
        log_warning(f"User not found for deletion: {user_uid}", logger=logger, print_out=print_out)
        return False
    except Exception as e:
        log_error(f"Error deleting user: {e}", logger=logger, print_out=print_out)
        return False

def get_user_auth_token(
    email: str, 
    password: str, 
    api_key: str, 
    logger: Optional[logging.Logger] = None, 
    print_out: bool = False,
    debug: bool = False
) -> Optional[str]:
    """
    Get a user authentication token using the Firebase REST API.
    
    Args:
        email: User email
        password: User password
        api_key: Firebase API key
        logger: Optional logger instance
        print_out: Whether to print output
        debug: Whether to print detailed debug info
        
    Returns:
        ID token or None if failed
    """
    import requests  # Import here to keep it optional
    
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }
    
    try:
        if debug:
            log_info(f"Sending authentication request to: {url}", logger=logger, print_out=print_out)
            log_info(f"Request payload: {payload}", logger=logger, print_out=print_out)
            
        response = requests.post(url, json=payload)
        
        # Add detailed error logging
        if not response.ok:
            error_details = response.text
            try:
                error_json = response.json()
                if "error" in error_json:
                    error_details = f"{error_json['error'].get('message', 'Unknown error')}"
            except Exception:
                pass
                
            log_error(f"Auth error ({response.status_code}): {error_details}", logger=logger, print_out=print_out)
            
            # Check for specific error conditions
            if "EMAIL_NOT_FOUND" in error_details or "INVALID_PASSWORD" in error_details:
                log_error(f"Authentication failed - invalid credentials for {email}", logger=logger, print_out=print_out)
            elif "USER_DISABLED" in error_details:
                log_error(f"User account is disabled: {email}", logger=logger, print_out=print_out)
            elif "INVALID_EMAIL" in error_details:
                log_error(f"Invalid email format: {email}", logger=logger, print_out=print_out)
            
            return None
        
        token = response.json().get("idToken")
        log_info(f"Successfully obtained auth token for {email}", logger=logger, print_out=print_out)
        return token
    except Exception as e:
        log_error(f"Error getting auth token: {e}", logger=logger, print_out=print_out)
        return None

def list_users(max_results: int = 1000, logger: Optional[logging.Logger] = None, print_out: bool = False) -> List[Dict[str, Any]]:
    """
    List users from Firebase Auth.
    
    Args:
        max_results: Maximum number of users to return
        logger: Optional logger instance
        print_out: Whether to print output
        
    Returns:
        List of user dicts
    """
    try:
        users = []
        page = auth.list_users()
        for user in page.users:
            users.append(user._data)
            if len(users) >= max_results:
                break
        
        log_info(f"Listed {len(users)} users from Firebase Auth", logger=logger, print_out=print_out)
        return users
    except Exception as e:
        log_error(f"Error listing users: {e}", logger=logger, print_out=print_out)
        return []

def create_custom_token(
    user_uid: str, 
    additional_claims: Dict[str, Any] = None, 
    logger: Optional[logging.Logger] = None, 
    print_out: bool = False
) -> str:
    """
    Create a custom token for a user.
    
    Args:
        user_uid: User's UID
        additional_claims: Additional claims to include in the token
        logger: Optional logger instance
        print_out: Whether to print output
        
    Returns:
        Custom token
    """
    try:
        token = auth.create_custom_token(user_uid, additional_claims)
        log_debug(f"Created custom token for user {user_uid}", logger=logger, print_out=print_out)
        return token
    except Exception as e:
        log_error(f"Error creating custom token: {e}", logger=logger, print_out=print_out)
        raise

def verify_id_token(
    token: str, 
    check_revoked: bool = False, 
    logger: Optional[logging.Logger] = None, 
    print_out: bool = False
) -> Dict[str, Any]:
    """
    Verify an ID token.
    
    Args:
        token: ID token to verify
        check_revoked: Whether to check if the token has been revoked
        logger: Optional logger instance
        print_out: Whether to print output
        
    Returns:
        Token claims
    """
    try:
        claims = auth.verify_id_token(token, check_revoked=check_revoked)
        log_debug(f"Verified ID token for user {claims.get('uid')}", logger=logger, print_out=print_out)
        return claims
    except Exception as e:
        log_error(f"Error verifying ID token: {e}", logger=logger, print_out=print_out)
        raise

def create_test_user_batch(
    user_configs: List[Dict[str, Any]], 
    logger: Optional[logging.Logger] = None, 
    print_out: bool = False
) -> Dict[str, str]:
    """
    Create a batch of test users based on configurations.
    
    Args:
        user_configs: List of user configurations with email, password, and other attributes
        logger: Optional logger instance
        print_out: Whether to print output
        
    Returns:
        Dict mapping user emails to UIDs
    """
    results = {}
    for config in user_configs:
        email = config.get("email")
        password = config.get("password", "Test123456")
        email_verified = config.get("email_verified", True)
        
        try:
            user = create_user_in_firebase(email, password, email_verified, logger=logger, print_out=print_out)
            results[email] = user.uid
            
            # Set custom claims if specified
            primary_usertype = config.get("primary_usertype")
            secondary_usertypes = config.get("secondary_usertypes", [])
            approved = config.get("approved", True)
            
            if primary_usertype:
                update_user_custom_claims(
                    user.uid, primary_usertype, secondary_usertypes, approved,
                    logger=logger, print_out=print_out
                )
                
        except Exception as e:
            log_error(f"Error creating test user {email}: {e}", logger=logger, print_out=print_out)
    
    return results
