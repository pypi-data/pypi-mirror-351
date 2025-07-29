# backend/auth/auth.py (Updated)
import os
import hashlib
import hmac
import time
import logging
from typing import Optional, Dict, Any, List
import json
import requests

# Firebase Admin SDK for server-side verification
try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    HAS_FIREBASE = True
except ImportError:
    HAS_FIREBASE = False
    logging.warning("Firebase Admin SDK not found. Remote API key validation disabled.")

# Initialize Firebase if credentials exist
if HAS_FIREBASE:
    try:
        # Path to the Firebase credentials file
        cred_path = os.path.join(os.path.dirname(__file__), '../firebase-credentials.json')
        if os.path.exists(cred_path):
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            logging.info("Firebase initialized successfully")
        else:
            logging.warning("Firebase credentials file not found")
            HAS_FIREBASE = False
    except Exception as e:
        logging.error(f"Error initializing Firebase: {e}")
        HAS_FIREBASE = False

# Path to the file storing valid keys (fallback)
KEYS_FILE = os.path.join(os.path.dirname(__file__), 'valid_keys.json')

# In-memory cache of valid API keys
_API_KEY_CACHE: Dict[str, Dict[str, Any]] = {}

# Master key for admin/development use
_MASTER_KEY = os.environ.get("CINDER_MASTER_KEY", "cinder_master_key_change_me")

def _load_valid_keys() -> Dict[str, Dict[str, Any]]:
    """Load valid keys from the keys file (fallback method)."""
    if os.path.exists(KEYS_FILE):
        try:
            with open(KEYS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error loading keys file: {e}")
    return {}

def _save_valid_keys(keys: Dict[str, Dict[str, Any]]) -> bool:
    """Save valid keys to the keys file (fallback method)."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(KEYS_FILE), exist_ok=True)
        
        with open(KEYS_FILE, 'w') as f:
            json.dump(keys, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving keys file: {e}")
        return False

def validate_api_key(api_key: Optional[str]) -> bool:
    """
    Validate if an API key is valid.
    
    Args:
        api_key: The API key to validate
        
    Returns:
        bool: True if the API key is valid, False otherwise
    """
    if not api_key:
        return False
    
    # Check cache first
    if api_key in _API_KEY_CACHE:
        # Check if the cached key is expired
        if _API_KEY_CACHE[api_key].get("expires_at", 0) > time.time():
            return True
        else:
            # Remove expired key
            del _API_KEY_CACHE[api_key]
    
    # For development: allow master key for testing
    if api_key == _MASTER_KEY:
        _API_KEY_CACHE[api_key] = {
            "valid": True,
            "expires_at": time.time() + (365 * 24 * 60 * 60),  # 1 year
            "permissions": ["all"],
            "tier": "pro"
        }
        return True
    
    # Try to validate with Firebase
    if HAS_FIREBASE:
        try:
            # Query Firestore for the API key
            api_keys_ref = db.collection('api_keys')
            query = api_keys_ref.where('key', '==', api_key).limit(1)
            results = query.get()
            
            for doc in results:
                key_data = doc.to_dict()
                
                # Check if key is active and not expired
                if key_data.get('active', False) and key_data.get('expiresAt', 0) > time.time():
                    # Add to cache
                    _API_KEY_CACHE[api_key] = {
                        "valid": True,
                        "expires_at": key_data.get('expiresAt', 0),
                        "permissions": key_data.get('permissions', ['basic']),
                        "tier": key_data.get('tier', 'free'),
                        "user_id": key_data.get('userId', '')
                    }
                    
                    # Update usage stats in Firebase
                    doc_ref = db.collection('api_keys').document(doc.id)
                    doc_ref.update({
                        'lastUsed': firestore.SERVER_TIMESTAMP,
                        'usageCount': firestore.Increment(1)
                    })
                    
                    return True
            
            return False
        except Exception as e:
            logging.error(f"Firebase validation error: {e}")
            # Fall back to local validation
    
    # Fallback: Check valid keys file
    valid_keys = _load_valid_keys()
    if api_key in valid_keys:
        # Check if key is expired
        if valid_keys[api_key].get("expires_at", 0) > time.time():
            # Add to cache
            _API_KEY_CACHE[api_key] = valid_keys[api_key]
            return True
        else:
            # Remove expired key
            del valid_keys[api_key]
            _save_valid_keys(valid_keys)
    
    # As a fallback, check environment variable
    env_valid_keys = os.environ.get("CINDER_VALID_KEYS", "").split(",")
    if api_key in env_valid_keys:
        _API_KEY_CACHE[api_key] = {
            "valid": True,
            "expires_at": time.time() + (30 * 24 * 60 * 60),  # 30 days
            "permissions": ["basic"],
            "tier": "free"
        }
        return True
    
    return False

def get_key_tier(api_key: Optional[str]) -> str:
    """
    Get the subscription tier associated with an API key.
    
    Args:
        api_key: The API key
        
    Returns:
        str: Subscription tier (free, basic, pro)
    """
    if not api_key:
        return "free"
    
    if api_key in _API_KEY_CACHE:
        return _API_KEY_CACHE[api_key].get("tier", "free")
    
    if validate_api_key(api_key):
        return _API_KEY_CACHE[api_key].get("tier", "free")
    
    return "free"

def generate_api_key(user_id: str, tier: str = "free") -> str:
    """
    Generate a new API key for a user and add it to the valid keys list.
    
    Args:
        user_id: Unique identifier for the user
        tier: Subscription tier (free, basic, pro)
        
    Returns:
        str: Generated API key
    """
    timestamp = str(int(time.time()))
    
    # Create a unique key based on user_id, timestamp and a secret
    secret = os.environ.get("CINDER_API_SECRET", "change_this_secret_key")
    message = f"{user_id}:{timestamp}"
    
    # Generate HMAC using SHA-256
    signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).hexdigest()
    
    # Create the formatted API key
    api_key = f"cinder_{timestamp}_{signature[:32]}"
    
    # Add the key to Firebase if available
    if HAS_FIREBASE:
        try:
            # Create key data
            key_data = {
                "key": api_key,
                "userId": user_id,
                "tier": tier,
                "createdAt": time.time(),
                "expiresAt": time.time() + (365 * 24 * 60 * 60),  # 1 year
                "lastUsed": None,
                "usageCount": 0,
                "active": True
            }
            
            # Add to Firestore
            db.collection('api_keys').add(key_data)
            logging.info(f"Added API key to Firebase for user {user_id}")
        except Exception as e:
            logging.error(f"Error adding key to Firebase: {e}")
            # Fall back to local storage
    
    # Fallback: Add the key to the local list of valid keys
    valid_keys = _load_valid_keys()
    valid_keys[api_key] = {
        "user_id": user_id,
        "created_at": time.time(),
        "expires_at": time.time() + (365 * 24 * 60 * 60),  # 1 year
        "permissions": ["basic"],
        "tier": tier
    }
    _save_valid_keys(valid_keys)
    
    return api_key

def get_key_permissions(api_key: Optional[str]) -> List[str]:
    """
    Get the permissions associated with an API key.
    
    Args:
        api_key: The API key
        
    Returns:
        list: List of permission strings
    """
    if not api_key:
        return []
    
    if api_key in _API_KEY_CACHE:
        return _API_KEY_CACHE[api_key].get("permissions", [])
    
    if validate_api_key(api_key):
        return _API_KEY_CACHE[api_key].get("permissions", [])
    
    return []

def revoke_api_key(api_key: str) -> bool:
    """
    Revoke an API key.
    
    Args:
        api_key: The API key to revoke
        
    Returns:
        bool: True if the key was revoked, False otherwise
    """
    # Remove from cache
    if api_key in _API_KEY_CACHE:
        del _API_KEY_CACHE[api_key]
    
    # Remove from Firebase
    if HAS_FIREBASE:
        try:
            # Find the key in Firestore
            api_keys_ref = db.collection('api_keys')
            query = api_keys_ref.where('key', '==', api_key).limit(1)
            results = query.get()
            
            for doc in results:
                # Instead of deleting, mark as inactive
                doc_ref = db.collection('api_keys').document(doc.id)
                doc_ref.update({"active": False})
                return True
                
            return False
        except Exception as e:
            logging.error(f"Error revoking key in Firebase: {e}")
            # Fall back to local storage
    
    # Fallback: Remove from valid keys file
    valid_keys = _load_valid_keys()
    if api_key in valid_keys:
        del valid_keys[api_key]
        return _save_valid_keys(valid_keys)
    
    return False

def list_valid_keys(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    List all valid API keys, optionally filtered by user_id.
    
    Args:
        user_id: Optional user ID to filter keys
        
    Returns:
        list: List of key information dictionaries
    """
    result = []
    
    # Try to get keys from Firebase
    if HAS_FIREBASE:
        try:
            api_keys_ref = db.collection('api_keys')
            
            if user_id:
                query = api_keys_ref.where('userId', '==', user_id).where('active', '==', True)
            else:
                query = api_keys_ref.where('active', '==', True)
                
            results = query.get()
            
            for doc in results:
                key_data = doc.to_dict()
                
                # Don't include the full key for security
                masked_key = f"{key_data['key'][:10]}...{key_data['key'][-5:]}"
                
                result.append({
                    "key": masked_key,
                    "full_key": key_data['key'],  # Only for internal use
                    "user_id": key_data.get('userId', 'unknown'),
                    "tier": key_data.get('tier', 'free'),
                    "created_at": key_data.get('createdAt', 0),
                    "expires_at": key_data.get('expiresAt', 0),
                    "last_used": key_data.get('lastUsed', None),
                    "usage_count": key_data.get('usageCount', 0)
                })
                
            return result
        except Exception as e:
            logging.error(f"Error listing keys from Firebase: {e}")
            # Fall back to local storage
    
    # Fallback: Load from local file
    valid_keys = _load_valid_keys()
    
    for key, info in valid_keys.items():
        if user_id and info.get("user_id") != user_id:
            continue
            
        # Don't include the full key for security
        masked_key = f"{key[:10]}...{key[-5:]}"
        result.append({
            "key": masked_key,
            "full_key": key,  # Only for internal use
            "user_id": info.get("user_id", "unknown"),
            "tier": info.get("tier", "free"),
            "created_at": info.get("created_at", 0),
            "expires_at": info.get("expires_at", 0)
        })
    
    return result