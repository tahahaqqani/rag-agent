import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_SETTINGS = {
    "title": "AI Assistant",
    "subtitle": "Ask me anything about our services and process.",
    "logo": "",  # Empty by default
    "accent": "#026CBD",
    "footer": "© 2024 AI Assistant",
    "suggested": [
        "What services do you offer?",
        "How does your process work?",
        "How much do you charge?",
        "What's your usual timeline?"
    ],
    "theme": {
        "primary_color": "#026CBD",
        "secondary_color": "#6c757d",
        "background_color": "#ffffff",
        "text_color": "#333333",
        "border_color": "#e9ecef"
    },
    "chat_settings": {
        "max_context_length": 3000,
        "temperature": 0.2,  # Lower for more focused responses
        "max_tokens": 140,    # Reduced for conciseness (60-100 words)
        "enable_streaming": False
    },
    "chat_icon": "",  # URL to custom chat icon image
    "chat_icon_text": "💬",  # Default emoji or text for chat icon
    "last_updated": datetime.now().isoformat()
}

# Configuration file path
CONFIG_PATH = Path("./config.json")
BACKUP_PATH = Path("./config.backup.json")


def load_settings() -> Dict[str, Any]:
    """
    Load settings from config file or return defaults.
    
    Returns:
        Dictionary containing current settings
    """
    try:
        if CONFIG_PATH.exists():
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                logger.info("Settings loaded from config file")
                
                # Merge with defaults to ensure all keys exist
                merged_settings = DEFAULT_SETTINGS.copy()
                merged_settings.update(settings)
                
                # Update timestamp
                merged_settings["last_updated"] = datetime.now().isoformat()
                
                return merged_settings
        else:
            logger.info("No config file found, using default settings")
            return DEFAULT_SETTINGS.copy()
            
    except Exception as e:
        logger.error(f"Error loading settings: {str(e)}")
        logger.info("Falling back to default settings")
        return DEFAULT_SETTINGS.copy()


def save_settings(data: Dict[str, Any]) -> bool:
    """
    Save settings to config file with backup.
    
    Args:
        data: Settings dictionary to save
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create backup of existing config
        if CONFIG_PATH.exists():
            import shutil
            shutil.copy2(CONFIG_PATH, BACKUP_PATH)
            logger.info("Backup created")
        
        # Validate required fields
        required_fields = ["title", "subtitle", "accent", "footer", "suggested"]
        for field in required_fields:
            if field not in data:
                logger.warning(f"Missing required field: {field}")
                data[field] = DEFAULT_SETTINGS[field]
        
        # Ensure suggested questions are limited to 4
        if "suggested" in data and isinstance(data["suggested"], list):
            data["suggested"] = data["suggested"][:4]
        
        # Update timestamp
        data["last_updated"] = datetime.now().isoformat()
        
        # Save to file
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info("Settings saved successfully")
        return True
        
    except Exception as e:
        logger.error(f"Error saving settings: {str(e)}")
        return False


def update_settings(updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update specific settings while preserving others.
    
    Args:
        updates: Dictionary containing settings to update
        
    Returns:
        Updated settings dictionary
    """
    try:
        current_settings = load_settings()
        
        # Update only the provided fields
        for key, value in updates.items():
            if key in current_settings:
                current_settings[key] = value
                logger.info(f"Updated setting: {key}")

            elif key == "secondaryColor" and "theme" in current_settings:
                current_settings["theme"]["secondary_color"] = value
                logger.info(f"Updated theme secondary_color: {value}")
            elif key == "backgroundColor" and "theme" in current_settings:
                current_settings["theme"]["background_color"] = value
                logger.info(f"Updated theme background_color: {value}")
            elif key == "textColor" and "theme" in current_settings:
                current_settings["theme"]["text_color"] = value
                logger.info(f"Updated theme text_color: {value}")
            # Handle chat settings
            elif key in ["temperature", "max_tokens", "max_context_length"] and "chat_settings" in current_settings:
                current_settings["chat_settings"][key] = value
                logger.info(f"Updated chat setting {key}: {value}")
            # Handle chat icon settings
            elif key == "chatIcon":
                current_settings["chat_icon"] = value
                logger.info(f"Updated chat icon: {value}")
            elif key == "chatIconText":
                current_settings["chat_icon_text"] = value
                logger.info(f"Updated chat icon text: {value}")
            else:
                logger.warning(f"Unknown setting key: {key}")
        
        # Save updated settings
        if save_settings(current_settings):
            return current_settings
        else:
            return {"error": "Failed to save settings"}
            
    except Exception as e:
        logger.error(f"Error updating settings: {str(e)}")
        return {"error": str(e)}


def reset_settings() -> bool:
    """
    Reset settings to defaults.
    
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create backup of current config
        if CONFIG_PATH.exists():
            import shutil
            shutil.copy2(CONFIG_PATH, BACKUP_PATH)
            logger.info("Backup created before reset")
        
        # Remove config file to trigger default loading
        if CONFIG_PATH.exists():
            CONFIG_PATH.unlink()
            logger.info("Config file removed")
        
        logger.info("Settings reset to defaults")
        return True
        
    except Exception as e:
        logger.error(f"Error resetting settings: {str(e)}")
        return False


def get_setting(key: str, default: Any = None) -> Any:
    """
    Get a specific setting value.
    
    Args:
        key: Setting key to retrieve
        default: Default value if key not found
        
    Returns:
        Setting value or default
    """
    try:
        settings = load_settings()
        return settings.get(key, default)
    except Exception as e:
        logger.error(f"Error getting setting {key}: {str(e)}")
        return default


def validate_settings(settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean settings data.
    
    Args:
        settings: Settings dictionary to validate
        
    Returns:
        Validated settings dictionary
    """
    errors = []
    validated = {}
    
    # Validate title
    if "title" in settings:
        title = str(settings["title"]).strip()
        if len(title) > 100:
            errors.append("Title too long (max 100 characters)")
        elif len(title) < 1:
            errors.append("Title cannot be empty")
        else:
            validated["title"] = title
    
    # Validate subtitle
    if "subtitle" in settings:
        subtitle = str(settings["subtitle"]).strip()
        if len(subtitle) > 200:
            errors.append("Subtitle too long (max 200 characters)")
        else:
            validated["subtitle"] = subtitle
    
    # Validate accent color
    if "accent" in settings:
        accent = str(settings["accent"]).strip()
        if not accent.startswith("#") or len(accent) != 7:
            errors.append("Invalid accent color format (use #RRGGBB)")
        else:
            validated["accent"] = accent
    
    # Validate suggested questions
    if "suggested" in settings:
        suggested = settings["suggested"]
        if isinstance(suggested, list) and len(suggested) <= 4:
            # Clean and validate each question
            cleaned_questions = []
            for i, question in enumerate(suggested):
                if isinstance(question, str) and question.strip():
                    cleaned_questions.append(question.strip())
                else:
                    errors.append(f"Invalid question at index {i}")
            
            if len(cleaned_questions) > 0:
                validated["suggested"] = cleaned_questions[:4]
            else:
                errors.append("At least one suggested question is required")
        else:
            errors.append("Suggested questions must be a list with 1-4 items")
    
    # Validate logo URL
    if "logo" in settings:
        logo = str(settings["logo"]).strip()
        if logo and not (logo.startswith("http://") or logo.startswith("https://")):
            errors.append("Logo must be a valid HTTP/HTTPS URL")
        else:
            validated["logo"] = logo
    
    # Validate footer
    if "footer" in settings:
        footer = str(settings["footer"]).strip()
        if len(footer) > 100:
            errors.append("Footer too long (max 100 characters)")
        else:
            validated["footer"] = footer
    
    # Validate chat settings
    if "temperature" in settings:
        try:
            temp = float(settings["temperature"])
            if temp < 0.0 or temp > 2.0:
                errors.append("Temperature must be between 0.0 and 2.0")
            else:
                validated["temperature"] = temp
        except (ValueError, TypeError):
            errors.append("Temperature must be a valid number")
    
    if "max_tokens" in settings:
        try:
            tokens = int(settings["max_tokens"])
            if tokens < 50 or tokens > 1000:
                errors.append("Max tokens must be between 50 and 1000")
            else:
                validated["max_tokens"] = tokens
        except (ValueError, TypeError):
            errors.append("Max tokens must be a valid integer")
    
    if "max_context_length" in settings:
        try:
            ctx_len = int(settings["max_context_length"])
            if ctx_len < 1000 or ctx_len > 10000:
                errors.append("Max context length must be between 1000 and 10000")
            else:
                validated["max_context_length"] = ctx_len
        except (ValueError, TypeError):
            errors.append("Max context length must be a valid integer")
    
    if errors:
        logger.warning(f"Validation errors: {errors}")
        validated["validation_errors"] = errors
    
    return validated


def export_settings() -> str:
    """
    Export current settings as JSON string.
    
    Returns:
        JSON string of current settings
    """
    try:
        settings = load_settings()
        return json.dumps(settings, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error exporting settings: {str(e)}")
        return json.dumps({"error": str(e)})


def import_settings(json_string: str) -> Dict[str, Any]:
    """
    Import settings from JSON string.
    
    Args:
        json_string: JSON string containing settings
        
    Returns:
        Import result dictionary
    """
    try:
        # Parse JSON
        imported_settings = json.loads(json_string)
        
        # Validate imported settings
        validated = validate_settings(imported_settings)
        
        if "validation_errors" in validated:
            return {
                "success": False,
                "errors": validated["validation_errors"],
                "message": "Import failed due to validation errors"
            }
        
        # Save validated settings
        if save_settings(validated):
            return {
                "success": True,
                "message": "Settings imported successfully",
                "settings": validated
            }
        else:
            return {
                "success": False,
                "message": "Failed to save imported settings"
            }
            
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "message": f"Invalid JSON format: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Import error: {str(e)}"
        }
