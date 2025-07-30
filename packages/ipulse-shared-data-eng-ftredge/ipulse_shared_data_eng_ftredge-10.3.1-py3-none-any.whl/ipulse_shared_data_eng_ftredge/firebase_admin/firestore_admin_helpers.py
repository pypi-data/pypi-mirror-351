"""
Firestore Admin Helper Functions

This module provides utility functions for managing Firestore documents,
particularly for user profiles and status documents.
"""

import os
import time
import logging
from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timezone, timedelta
from google.cloud import firestore
from ipulse_shared_base_ftredge import log_info, log_warning, log_error, log_debug, LogLevel

# Constants
USER_PROFILES_COLLECTION = "papp_core_user_userprofiles"
USER_STATUS_COLLECTION = "papp_core_user_userstatuss"
PROFILE_OBJ_REF = "userprofile"
STATUS_OBJ_REF = "userstatus"

def get_user_profile(
    db: firestore.Client, 
    user_uid: str,
    logger: Optional[logging.Logger] = None,
    print_out: bool = False,
    user_profiles_collection: str = USER_PROFILES_COLLECTION,
    profile_obj_ref: str = PROFILE_OBJ_REF
) -> Optional[Dict[str, Any]]:
    """
    Get a user profile from Firestore.
    
    Args:
        db: Firestore client
        user_uid: User's UID
        logger: Optional logger instance
        print_out: Whether to print output
        user_profiles_collection: Collection name for user profiles
        profile_obj_ref: Object reference prefix for user profiles
        
    Returns:
        User profile dict or None if not found
    """
    profile_id = f"{profile_obj_ref}_{user_uid}"
    doc = db.collection(user_profiles_collection).document(profile_id).get()
    
    if doc.exists:
        log_debug(f"Retrieved user profile for {user_uid}", logger=logger, print_out=print_out)
        return doc.to_dict()
    else:
        log_debug(f"User profile not found for {user_uid}", logger=logger, print_out=print_out)
        return None

def get_user_status(
    db: firestore.Client, 
    user_uid: str,
    logger: Optional[logging.Logger] = None,
    print_out: bool = False,
    user_status_collection: str = USER_STATUS_COLLECTION,
    status_obj_ref: str = STATUS_OBJ_REF
) -> Optional[Dict[str, Any]]:
    """
    Get a user status from Firestore.
    
    Args:
        db: Firestore client
        user_uid: User's UID
        logger: Optional logger instance
        print_out: Whether to print output
        user_status_collection: Collection name for user statuses
        status_obj_ref: Object reference prefix for user statuses
        
    Returns:
        User status dict or None if not found
    """
    status_id = f"{status_obj_ref}_{user_uid}"
    doc = db.collection(user_status_collection).document(status_id).get()
    
    if doc.exists:
        log_debug(f"Retrieved user status for {user_uid}", logger=logger, print_out=print_out)
        return doc.to_dict()
    else:
        log_debug(f"User status not found for {user_uid}", logger=logger, print_out=print_out)
        return None

def update_usertypes_in_userprofile(
    db: firestore.Client, 
    user_uid: str, 
    primary_usertype: str, 
    secondary_usertypes: List[str],
    logger: Optional[logging.Logger] = None,
    print_out: bool = False,
    user_profiles_collection: str = USER_PROFILES_COLLECTION,
    profile_obj_ref: str = PROFILE_OBJ_REF
) -> bool:
    """
    Update a user's primary and secondary usertypes in Firestore user profile.
    
    Args:
        db: Firestore client
        user_uid: User's UID
        primary_usertype: Primary user type
        secondary_usertypes: List of secondary user types
        logger: Optional logger instance
        print_out: Whether to print output
        user_profiles_collection: Collection name for user profiles
        profile_obj_ref: Object reference prefix for user profiles
        
    Returns:
        Success status
    """
    profile_id = f"{profile_obj_ref}_{user_uid}"
    
    try:
        db.collection(user_profiles_collection).document(profile_id).update({
            "primary_usertype": primary_usertype,
            "secondary_usertypes": secondary_usertypes,
            "updated_by": "firestore_admin_helpers",
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        log_info(f"Updated user types in profile for {user_uid}", logger=logger, print_out=print_out)
        return True
    except Exception as e:
        log_error(f"Error updating user types in profile: {e}", logger=logger, print_out=print_out)
        return False

def update_usertypes_in_userstatus(
    db: firestore.Client, 
    user_uid: str, 
    primary_usertype: str, 
    secondary_usertypes: List[str],
    logger: Optional[logging.Logger] = None,
    print_out: bool = False,
    user_status_collection: str = USER_STATUS_COLLECTION,
    status_obj_ref: str = STATUS_OBJ_REF
) -> bool:
    """
    Update a user's primary and secondary usertypes in Firestore user status.
    
    Args:
        db: Firestore client
        user_uid: User's UID
        primary_usertype: Primary user type
        secondary_usertypes: List of secondary user types
        logger: Optional logger instance
        print_out: Whether to print output
        user_status_collection: Collection name for user statuses
        status_obj_ref: Object reference prefix for user statuses
        
    Returns:
        Success status
    """
    status_id = f"{status_obj_ref}_{user_uid}"
    
    try:
        db.collection(user_status_collection).document(status_id).update({
            "primary_usertype": primary_usertype,
            "secondary_usertypes": secondary_usertypes,
            "updated_by": "firestore_admin_helpers",
            "updated_at": firestore.SERVER_TIMESTAMP
        })
        log_info(f"Updated user types in status for {user_uid}", logger=logger, print_out=print_out)
        return True
    except Exception as e:
        log_error(f"Error updating user types in status: {e}", logger=logger, print_out=print_out)
        return False

def add_iam_permissions_for_user(
    db: firestore.Client,
    user_uid: str, 
    domain: str = "papp", 
    iam_unit_type: str = "groups", 
    iam_unit_ref: str = "domain_sensitive_admin_group", 
    permanent: bool = False,
    logger: Optional[logging.Logger] = None,
    print_out: bool = False,
    user_status_collection: str = USER_STATUS_COLLECTION,
    status_obj_ref: str = STATUS_OBJ_REF
) -> bool:
    """
    Add IAM permissions for a user by updating their status document.
    
    Args:
        db: Firestore client
        user_uid: User's UID
        domain: IAM domain (e.g., "papp")
        iam_unit_type: IAM unit type (e.g., "groups", "roles")
        iam_unit_ref: Reference name of the IAM unit (e.g., "domain_sensitive_admin_group")
        permanent: If True, no expiration date is set
        logger: Optional logger instance
        print_out: Whether to print output
        user_status_collection: Collection name for user statuses
        status_obj_ref: Object reference prefix for user statuses
        
    Returns:
        Success status
    """
    status_id = f"{status_obj_ref}_{user_uid}"
    
    try:
        # Current time
        now = datetime.now(timezone.utc)
        
        # Set expiration if not permanent
        if permanent:
            expiration = None
        else:
            expiration = now + timedelta(days=365 * 10)  # 10 years
        
        # Create the document field update path
        field_path = f"iam_domain_permissions.{domain}.{iam_unit_type}.{iam_unit_ref}"
        
        # Create IAM permission assignment
        iam_permission = {
            "iam_unit_ref": iam_unit_ref,
            "source": "firestore_admin_helpers",
            "expires_at": expiration
        }
        
        # Update the document
        db.collection(user_status_collection).document(status_id).update({
            field_path: iam_permission
        })
        
        log_info(f"Added {domain}.{iam_unit_type}.{iam_unit_ref} permissions for user {user_uid}", 
              logger=logger, print_out=print_out)
        return True
    except Exception as e:
        log_error(f"Error adding permissions: {e}", logger=logger, print_out=print_out)
        return False

def update_user_credit_balances(
    db: firestore.Client,
    user_uid: str, 
    subscription_credits: Optional[int] = None,
    extra_credits: Optional[int] = None,
    voting_credits: Optional[int] = None,
    logger: Optional[logging.Logger] = None,
    print_out: bool = False,
    user_status_collection: str = USER_STATUS_COLLECTION,
    status_obj_ref: str = STATUS_OBJ_REF
) -> bool:
    """
    Update a user's credit balances in their status document.
    
    Args:
        db: Firestore client
        user_uid: User's UID
        subscription_credits: New subscription-based insight credits
        extra_credits: New extra insight credits
        voting_credits: New voting credits
        logger: Optional logger instance
        print_out: Whether to print output
        user_status_collection: Collection name for user statuses
        status_obj_ref: Object reference prefix for user statuses
        
    Returns:
        Success status
    """
    status_id = f"{status_obj_ref}_{user_uid}"
    now = datetime.now(timezone.utc).isoformat()
    
    try:
        updates = {}
        
        if subscription_credits is not None:
            updates["sbscrptn_based_insight_credits"] = subscription_credits
            updates["sbscrptn_based_insight_credits_updtd_on"] = now
            
        if extra_credits is not None:
            updates["extra_insight_credits"] = extra_credits
            updates["extra_insight_credits_updtd_on"] = now
            
        if voting_credits is not None:
            updates["voting_credits"] = voting_credits
            updates["voting_credits_updtd_on"] = now
            
        if updates:
            updates["updated_by"] = "firestore_admin_helpers"
            updates["updated_at"] = firestore.SERVER_TIMESTAMP
            
            db.collection(user_status_collection).document(status_id).update(updates)
            log_info(f"Updated credit balances for user {user_uid}", logger=logger, print_out=print_out)
            return True
        
        return False
    except Exception as e:
        log_error(f"Error updating credit balances: {e}", logger=logger, print_out=print_out)
        return False

def get_subscription_plans(
    db: firestore.Client, 
    collection: str = "papp_core_configs_subscriptionplans",
    logger: Optional[logging.Logger] = None,
    print_out: bool = False
) -> Dict[str, Any]:
    """
    Get all subscription plans from Firestore.
    
    Args:
        db: Firestore client
        collection: Collection name
        logger: Optional logger instance
        print_out: Whether to print output
        
    Returns:
        Dict of subscription plans
    """
    try:
        doc = db.collection(collection).document("all_subscriptionplans_defaults").get()
        if doc.exists:
            log_info("Retrieved subscription plans", logger=logger, print_out=print_out)
            return doc.to_dict() or {}
        else:
            log_warning("Subscription plans document not found", logger=logger, print_out=print_out)
            return {}
    except Exception as e:
        log_error(f"Error getting subscription plans: {e}", logger=logger, print_out=print_out)
        return {}

def get_user_defaults(
    db: firestore.Client, 
    collection: str = "papp_core_configs_user",
    logger: Optional[logging.Logger] = None,
    print_out: bool = False
) -> Dict[str, Any]:
    """
    Get all user defaults from Firestore.
    
    Args:
        db: Firestore client
        collection: Collection name
        logger: Optional logger instance
        print_out: Whether to print output
        
    Returns:
        Dict of user defaults
    """
    try:
        doc = db.collection(collection).document("all_users_defaults").get()
        if doc.exists:
            log_info("Retrieved user defaults", logger=logger, print_out=print_out)
            return doc.to_dict() or {}
        else:
            log_warning("User defaults document not found", logger=logger, print_out=print_out)
            return {}
    except Exception as e:
        log_error(f"Error getting user defaults: {e}", logger=logger, print_out=print_out)
        return {}

def find_users_by_query(
    db: firestore.Client, 
    field_path: str, 
    op_string: str, 
    value: Any, 
    collection: str = USER_PROFILES_COLLECTION, 
    limit: int = 10,
    logger: Optional[logging.Logger] = None,
    print_out: bool = False
) -> List[Dict[str, Any]]:
    """
    Find users by a query.
    
    Args:
        db: Firestore client
        field_path: Field path to query
        op_string: Operation string ('==', '!=', '>', '<', '>=', '<=', 'array-contains', etc.)
        value: Value to compare
        collection: Collection name
        limit: Maximum number of results
        logger: Optional logger instance
        print_out: Whether to print output
        
    Returns:
        List of matching documents
    """
    try:
        query = db.collection(collection).where(field_path, op_string, value).limit(limit)
        results = [doc.to_dict() for doc in query.stream()]
        log_info(f"Found {len(results)} documents matching query {field_path} {op_string} {value}", 
              logger=logger, print_out=print_out)
        return results
    except Exception as e:
        log_error(f"Error querying Firestore: {e}", logger=logger, print_out=print_out)
        return []

def verify_user_setup(
    db: firestore.Client, 
    user_uid: str, 
    expected_primary_usertype: str, 
    expected_secondary_usertypes: List[str],
    logger: Optional[logging.Logger] = None,
    print_out: bool = False,
    user_profiles_collection: str = USER_PROFILES_COLLECTION,
    user_status_collection: str = USER_STATUS_COLLECTION,
    profile_obj_ref: str = PROFILE_OBJ_REF,
    status_obj_ref: str = STATUS_OBJ_REF
) -> bool:
    """
    Verify that a user is set up correctly with the expected user types.
    
    Args:
        db: Firestore client
        user_uid: User UID
        expected_primary_usertype: Expected primary user type
        expected_secondary_usertypes: Expected secondary user types
        logger: Optional logger instance
        print_out: Whether to print output
        user_profiles_collection: Collection name for user profiles
        user_status_collection: Collection name for user statuses
        profile_obj_ref: Object reference prefix for user profiles
        status_obj_ref: Object reference prefix for user statuses
        
    Returns:
        Whether the user is set up correctly
    """
    # Get user profile and status
    profile = get_user_profile(
        db, user_uid, logger=logger, print_out=print_out,
        user_profiles_collection=user_profiles_collection, profile_obj_ref=profile_obj_ref
    )
    status = get_user_status(
        db, user_uid, logger=logger, print_out=print_out,
        user_status_collection=user_status_collection, status_obj_ref=status_obj_ref
    )
    
    if not profile or not status:
        log_error(f"User {user_uid} is missing profile or status documents", logger=logger, print_out=print_out)
        return False
    
    # Check user types in profile
    profile_primary = profile.get("primary_usertype")
    profile_secondary = profile.get("secondary_usertypes", [])
    
    # Check user types in status
    status_primary = status.get("primary_usertype")
    status_secondary = status.get("secondary_usertypes", [])
    
    # Check if all match expectations
    profile_primary_match = profile_primary == expected_primary_usertype
    status_primary_match = status_primary == expected_primary_usertype
    
    # Check if secondary user types match (order doesn't matter)
    profile_secondary_match = sorted(profile_secondary) == sorted(expected_secondary_usertypes)
    status_secondary_match = sorted(status_secondary) == sorted(expected_secondary_usertypes)
    
    # Print summary
    log_info(f"\n--- Verification for user {user_uid} ---", logger=logger, print_out=print_out)
    log_info(f"Primary usertype matches:", logger=logger, print_out=print_out)
    log_info(f"  - Profile: {profile_primary_match} ({profile_primary})", logger=logger, print_out=print_out)
    log_info(f"  - Status: {status_primary_match} ({status_primary})", logger=logger, print_out=print_out)
    
    log_info(f"Secondary usertypes match:", logger=logger, print_out=print_out)
    log_info(f"  - Profile: {profile_secondary_match} ({profile_secondary})", logger=logger, print_out=print_out)
    log_info(f"  - Status: {status_secondary_match} ({status_secondary})", logger=logger, print_out=print_out)
    
    return all([
        profile_primary_match, status_primary_match,
        profile_secondary_match, status_secondary_match
    ])

def delete_user_documents(
    db: firestore.Client, 
    user_uid: str,
    logger: Optional[logging.Logger] = None,
    print_out: bool = False,
    user_profiles_collection: str = USER_PROFILES_COLLECTION,
    user_status_collection: str = USER_STATUS_COLLECTION,
    profile_obj_ref: str = PROFILE_OBJ_REF,
    status_obj_ref: str = STATUS_OBJ_REF
) -> bool:
    """
    Delete a user's profile and status documents.
    
    Args:
        db: Firestore client
        user_uid: User's UID
        logger: Optional logger instance
        print_out: Whether to print output
        user_profiles_collection: Collection name for user profiles
        user_status_collection: Collection name for user statuses
        profile_obj_ref: Object reference prefix for user profiles
        status_obj_ref: Object reference prefix for user statuses
        
    Returns:
        Success status
    """
    try:
        profile_id = f"{profile_obj_ref}_{user_uid}"
        status_id = f"{status_obj_ref}_{user_uid}"
        
        batch = db.batch()
        batch.delete(db.collection(user_profiles_collection).document(profile_id))
        batch.delete(db.collection(user_status_collection).document(status_id))
        batch.commit()
        
        log_info(f"Deleted profile and status documents for user {user_uid}", logger=logger, print_out=print_out)
        return True
    except Exception as e:
        log_error(f"Error deleting user documents: {e}", logger=logger, print_out=print_out)
        return False
