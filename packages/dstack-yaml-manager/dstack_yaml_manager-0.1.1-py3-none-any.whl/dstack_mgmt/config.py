#!/usr/bin/env python3
"""
Configuration management for dstack Management Tool
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigManager:
    """Manages configuration for dstack Management Tool"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".dstack-mgmt"
        self.config_file = self.config_dir / "config.yml"
        self.default_config = {
            "database": {
                "path": str(self.config_dir / "dstack_manager.db"),
                "auto_backup": True,
                "backup_count": 5
            },
            "ui": {
                "auto_save_notes": True,
                "auto_save_delay": 1.0,
                "restore_state": True
            },
            "paths": {
                "default_workspace": str(Path.home()),
                "scan_hidden_dirs": False
            }
        }
        self._ensure_config_exists()
    
    def _ensure_config_exists(self) -> None:
        """Ensure config directory and file exist with default values"""
        # Create config directory if it doesn't exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # Create config file with defaults if it doesn't exist
        if not self.config_file.exists():
            self._create_default_config()
        else:
            # Validate and update existing config with any missing keys
            self._update_config_if_needed()
    
    def _create_default_config(self) -> None:
        """Create config file with default values"""
        with open(self.config_file, 'w') as f:
            yaml.dump(self.default_config, f, default_flow_style=False, indent=2)
        
        print(f"✅ Created default configuration at: {self.config_file}")
    
    def _update_config_if_needed(self) -> None:
        """Update existing config with any missing default keys"""
        try:
            current_config = self.load_config()
            updated = False
            
            # Recursively merge default config into current config
            def merge_configs(default: Dict, current: Dict) -> Dict:
                nonlocal updated
                result = current.copy()
                
                for key, value in default.items():
                    if key not in result:
                        result[key] = value
                        updated = True
                    elif isinstance(value, dict) and isinstance(result[key], dict):
                        result[key] = merge_configs(value, result[key])
                
                return result
            
            merged_config = merge_configs(self.default_config, current_config)
            
            if updated:
                self.save_config(merged_config)
                print(f"🔄 Updated configuration with new default values")
                
        except Exception as e:
            print(f"⚠️ Error updating config, recreating: {e}")
            self._create_default_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        try:
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f) or {}
            return config
        except Exception as e:
            print(f"⚠️ Error loading config: {e}")
            return self.default_config.copy()
    
    def save_config(self, config: Dict[str, Any]) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
        except Exception as e:
            print(f"❌ Error saving config: {e}")
            raise
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """Get config value using dot notation (e.g., 'database.path')"""
        config = self.load_config()
        keys = key_path.split('.')
        
        current = config
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        
        return current
    
    def set(self, key_path: str, value: Any) -> None:
        """Set config value using dot notation"""
        config = self.load_config()
        keys = key_path.split('.')
        
        current = config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        current[keys[-1]] = value
        self.save_config(config)
    
    def get_database_path(self) -> Path:
        """Get the database file path from config"""
        db_path = self.get("database.path")
        if db_path:
            return Path(db_path)
        else:
            # Fallback to default
            return self.config_dir / "dstack_manager.db"
    
    def get_config_info(self) -> Dict[str, str]:
        """Get configuration information for display"""
        return {
            "Config Directory": str(self.config_dir),
            "Config File": str(self.config_file),
            "Database Path": str(self.get_database_path()),
            "Auto Save Notes": str(self.get("ui.auto_save_notes", True)),
            "Restore State": str(self.get("ui.restore_state", True))
        }