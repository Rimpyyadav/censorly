"""
Configuration Manager
Handles saving/loading user settings
"""

import json
import os
from typing import Dict, Any


class ConfigManager:
    """Manages application configuration"""
    
    DEFAULT_CONFIG = {
        "version": "1.0.0",
        "blur": {
            "mode": "regions",  # none, full, regions
            "strength": 7,      # 1-10
        },
        "detection": {
            "ocr_enabled": True,
            "confidence_threshold": 40,
            "ocr_interval": 2,  # frames
            "enabled_patterns": [
                "email",
                "phone",
                "credit_card",
                "ip_address",
                "account_number",
                "api_key"
            ]
        },
        "output": {
            "virtual_camera_enabled": False,
            "show_preview": False,
            "show_detection_boxes": False
        },
        "ui": {
            "start_minimized": False,
            "show_notifications": True
        },
        "performance": {
            "target_fps": 30
        }
    }
    
    def __init__(self, config_path="config/settings.json"):
        """
        Initialize config manager
        
        Args:
            config_path: Path to config file
        """
        self.config_path = config_path
        self.config = self.load_config()
        print(f"✅ Config Manager initialized")
        print(f"   Config file: {self.config_path}")
    
    def load_config(self) -> Dict[str, Any]:
        """
        Load configuration from file
        
        Returns:
            Configuration dictionary
        """
        # Create config directory if doesn't exist
        config_dir = os.path.dirname(self.config_path)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)
            print(f"📁 Created config directory: {config_dir}")
        
        # Try to load existing config
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                
                # Merge with defaults (in case new settings added)
                config = self._merge_configs(self.DEFAULT_CONFIG, loaded_config)
                
                print(f"✅ Loaded config from: {self.config_path}")
                return config
                
            except json.JSONDecodeError as e:
                print(f"⚠️ Config file corrupted: {e}")
                print(f"   Using default config")
                return self.DEFAULT_CONFIG.copy()
            except Exception as e:
                print(f"⚠️ Error loading config: {e}")
                return self.DEFAULT_CONFIG.copy()
        else:
            print(f"📄 No config file found, using defaults")
            # Save default config
            self.save_config(self.DEFAULT_CONFIG)
            return self.DEFAULT_CONFIG.copy()
    
    def save_config(self, config=None):
        """
        Save configuration to file
        
        Args:
            config: Config dict to save (uses self.config if None)
        """
        if config is None:
            config = self.config
        
        try:
            # Ensure directory exists
            config_dir = os.path.dirname(self.config_path)
            if config_dir and not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            # Save with pretty formatting
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            
            print(f"💾 Config saved to: {self.config_path}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save config: {e}")
            return False
    
    def _merge_configs(self, default: Dict, loaded: Dict) -> Dict:
        """
        Merge loaded config with defaults (adds missing keys)
        
        Args:
            default: Default configuration
            loaded: Loaded configuration
            
        Returns:
            Merged configuration
        """
        merged = default.copy()
        
        for key, value in loaded.items():
            if key in merged and isinstance(value, dict) and isinstance(merged[key], dict):
                # Recursively merge nested dicts
                merged[key] = self._merge_configs(merged[key], value)
            else:
                # Override with loaded value
                merged[key] = value
        
        return merged
    
    def get(self, key_path: str, default=None):
        """
        Get config value by dot-separated path
        
        Args:
            key_path: Dot-separated path (e.g., "blur.strength")
            default: Default value if not found
            
        Returns:
            Config value
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value: Any):
        """
        Set config value by dot-separated path
        
        Args:
            key_path: Dot-separated path (e.g., "blur.strength")
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to nested dict
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set value
        config[keys[-1]] = value
        
        # Auto-save
        self.save_config()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save_config()
        print("🔄 Config reset to defaults")


# Singleton instance
_config_manager = None

def get_config_manager() -> ConfigManager:
    """Get global config manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager