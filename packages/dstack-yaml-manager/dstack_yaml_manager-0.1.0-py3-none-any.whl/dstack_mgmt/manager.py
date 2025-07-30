#!/usr/bin/env python3
"""
Main manager module for dstack Management Tool
"""

import os
import sys
import yaml
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

try:
    from .config import ConfigManager
except ImportError:
    # Fallback for standalone usage
    ConfigManager = None

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    DirectoryTree, Header, Footer, Static, Button, Input, 
    TextArea, Tree, Label, TabbedContent, TabPane, ListView, ListItem
)
from textual.binding import Binding
from textual.screen import ModalScreen, Screen
from textual.reactive import reactive
from textual.message import Message
from rich.syntax import Syntax
from rich.text import Text
from rich.console import Console
from rich.panel import Panel


class DStackConfigType(Enum):
    TASK = "task"
    SERVICE = "service"
    FLEET = "fleet"
    SERVER = "server"
    UNKNOWN = "unknown"


class DatabaseManager:
    """SQLite database manager for YAML file metadata"""
    
    def __init__(self, db_path: Path = None, config_manager=None):
        if db_path:
            self.db_path = db_path
        elif config_manager:
            self.db_path = config_manager.get_database_path()
        else:
            self.db_path = Path.cwd() / "dstack_manager.db"
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create yaml_files table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS yaml_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                path TEXT UNIQUE NOT NULL,
                config_type TEXT NOT NULL,
                content TEXT NOT NULL,
                parsed_yaml TEXT,
                is_valid BOOLEAN NOT NULL DEFAULT 1,
                validation_errors TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                file_size INTEGER,
                file_hash TEXT
            )
        """)
        
        # Create tags table for categorization
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                color TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create file_tags junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_tags (
                file_id INTEGER,
                tag_id INTEGER,
                PRIMARY KEY (file_id, tag_id),
                FOREIGN KEY (file_id) REFERENCES yaml_files (id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE
            )
        """)
        
        # Create templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                config_type TEXT NOT NULL,
                content TEXT NOT NULL,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create notes table for file-specific markdown notes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                note_content TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create application settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS app_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create project settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                root_path TEXT,
                is_active BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create file history table for version tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_id INTEGER,
                content TEXT NOT NULL,
                change_type TEXT NOT NULL,
                change_description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (file_id) REFERENCES yaml_files (id) ON DELETE CASCADE
            )
        """)
        
        # Create custom groups table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS custom_groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                color TEXT DEFAULT '#1e90ff',
                icon TEXT DEFAULT '📁',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create file_custom_groups junction table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS file_custom_groups (
                file_id INTEGER,
                group_id INTEGER,
                PRIMARY KEY (file_id, group_id),
                FOREIGN KEY (file_id) REFERENCES yaml_files (id) ON DELETE CASCADE,
                FOREIGN KEY (group_id) REFERENCES custom_groups (id) ON DELETE CASCADE
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_file(self, yaml_file: 'YAMLFile') -> int:
        """Add a YAML file to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Calculate file hash and size
        file_hash = self._calculate_hash(yaml_file.content)
        file_size = len(yaml_file.content.encode())
        
        cursor.execute("""
            INSERT OR REPLACE INTO yaml_files 
            (name, path, config_type, content, parsed_yaml, is_valid, validation_errors, 
             updated_at, file_size, file_hash)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            yaml_file.name,
            str(yaml_file.path),
            yaml_file.config_type.value,
            yaml_file.content,
            str(yaml_file.parsed_yaml) if yaml_file.parsed_yaml else None,
            yaml_file.is_valid,
            str(yaml_file.validation_errors) if yaml_file.validation_errors else None,
            datetime.now().isoformat(),
            file_size,
            file_hash
        ))
        
        file_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return file_id
    
    def get_all_files(self) -> List[Dict]:
        """Get all YAML files from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, path, config_type, content, parsed_yaml, 
                   is_valid, validation_errors, created_at, updated_at, 
                   file_size, file_hash
            FROM yaml_files 
            ORDER BY updated_at DESC
        """)
        
        columns = [description[0] for description in cursor.description]
        files = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return files
    
    def get_file_by_path(self, path: str) -> Optional[Dict]:
        """Get a specific file by path"""
        import datetime
        
        debug_log = "/Users/deep-diver/dstack-mgmt-tool/delete_debug.log"
        
        def log_debug(message):
            with open(debug_log, "a") as f:
                f.write(f"{datetime.datetime.now()}: {message}\n")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        log_debug(f"🔍 LOOKUP: Looking up file by path: '{path}'")
        
        # First, let's see what paths are in the database
        cursor.execute("SELECT id, name, path FROM yaml_files")
        all_files = cursor.fetchall()
        log_debug(f"🔍 DATABASE: All files in database ({len(all_files)} total):")
        for file_record in all_files:
            log_debug(f"  ID: {file_record[0]}, Name: {file_record[1]}, Path: '{file_record[2]}'")
        
        cursor.execute("""
            SELECT id, name, path, config_type, content, parsed_yaml, 
                   is_valid, validation_errors, created_at, updated_at, 
                   file_size, file_hash
            FROM yaml_files 
            WHERE path = ?
        """, (str(path),))
        
        row = cursor.fetchone()
        if row:
            log_debug(f"✅ FOUND: File with ID: {row[0]} and path: '{row[2]}'")
            columns = [description[0] for description in cursor.description]
            result = dict(zip(columns, row))
        else:
            log_debug(f"❌ NOT_FOUND: No file found with path: '{path}'")
            result = None
        
        conn.close()
        return result
    
    def update_file(self, path: str, content: str, parsed_yaml: Any = None, 
                   is_valid: bool = True, validation_errors: List[str] = None):
        """Update file content and metadata"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        file_hash = self._calculate_hash(content)
        file_size = len(content.encode())
        
        cursor.execute("""
            UPDATE yaml_files 
            SET content = ?, parsed_yaml = ?, is_valid = ?, validation_errors = ?,
                updated_at = ?, file_size = ?, file_hash = ?
            WHERE path = ?
        """, (
            content,
            str(parsed_yaml) if parsed_yaml else None,
            is_valid,
            str(validation_errors) if validation_errors else None,
            datetime.now().isoformat(),
            file_size,
            file_hash,
            str(path)
        ))
        
        conn.commit()
        conn.close()
    
    def delete_file(self, path: str):
        """Delete a file from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM yaml_files WHERE path = ?", (str(path),))
        
        conn.commit()
        conn.close()
    
    def get_files_by_type(self, config_type: str) -> List[Dict]:
        """Get files filtered by configuration type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, path, config_type, content, parsed_yaml, 
                   is_valid, validation_errors, created_at, updated_at, 
                   file_size, file_hash
            FROM yaml_files 
            WHERE config_type = ?
            ORDER BY updated_at DESC
        """, (config_type,))
        
        columns = [description[0] for description in cursor.description]
        files = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return files
    
    def _calculate_hash(self, content: str) -> str:
        """Calculate hash for content change detection"""
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()
    
    def add_template(self, name: str, config_type: str, content: str, description: str = ""):
        """Add a template to the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO templates (name, config_type, content, description)
            VALUES (?, ?, ?, ?)
        """, (name, config_type, content, description))
        
        conn.commit()
        conn.close()
    
    def get_templates(self) -> List[Dict]:
        """Get all templates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, config_type, content, description, created_at
            FROM templates 
            WHERE is_active = 1
            ORDER BY config_type, name
        """)
        
        columns = [description[0] for description in cursor.description]
        templates = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return templates
    
    def get_file_note(self, file_path: str) -> str:
        """Get note content for a file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT note_content FROM file_notes WHERE file_path = ?", (str(file_path),))
        row = cursor.fetchone()
        
        conn.close()
        return row[0] if row else ""
    
    def save_file_note(self, file_path: str, note_content: str):
        """Save note content for a file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO file_notes (file_path, note_content, updated_at)
            VALUES (?, ?, ?)
        """, (str(file_path), note_content, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_setting(self, key: str, default: str = "") -> str:
        """Get application setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT value FROM app_settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        
        conn.close()
        return row[0] if row else default
    
    def set_setting(self, key: str, value: str):
        """Set application setting"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO app_settings (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (key, value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def add_file_history(self, file_id: int, content: str, change_type: str, description: str = ""):
        """Add file history entry"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO file_history (file_id, content, change_type, change_description)
            VALUES (?, ?, ?, ?)
        """, (file_id, content, change_type, description))
        
        conn.commit()
        conn.close()
    
    def get_file_history(self, file_id: int) -> List[Dict]:
        """Get file history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, content, change_type, change_description, created_at
            FROM file_history 
            WHERE file_id = ?
            ORDER BY created_at DESC
        """, (file_id,))
        
        columns = [description[0] for description in cursor.description]
        history = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return history
    
    def export_file_to_filesystem(self, file_id: int, output_dir: Path = None) -> Path:
        """Export a file from database to filesystem"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, content FROM yaml_files WHERE id = ?", (file_id,))
        row = cursor.fetchone()
        
        if not row:
            raise ValueError(f"File with id {file_id} not found")
        
        name, content = row
        output_dir = output_dir or Path.cwd()
        file_path = output_dir / name
        
        with open(file_path, 'w') as f:
            f.write(content)
        
        conn.close()
        return file_path
    
    def export_all_files_to_filesystem(self, output_dir: Path = None) -> List[Path]:
        """Export all files from database to filesystem"""
        files = self.get_all_files()
        output_dir = output_dir or Path.cwd()
        exported_paths = []
        
        for file_data in files:
            file_path = output_dir / file_data['name']
            with open(file_path, 'w') as f:
                f.write(file_data['content'])
            exported_paths.append(file_path)
        
        return exported_paths
    
    def add_custom_group(self, name: str, description: str = "", color: str = "#1e90ff", icon: str = "📁") -> int:
        """Add a custom group"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO custom_groups (name, description, color, icon)
            VALUES (?, ?, ?, ?)
        """, (name, description, color, icon))
        
        group_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return group_id
    
    def get_custom_groups(self) -> List[Dict]:
        """Get all custom groups"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, name, description, color, icon, created_at
            FROM custom_groups 
            WHERE is_active = 1
            ORDER BY name
        """)
        
        columns = [description[0] for description in cursor.description]
        groups = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return groups
    
    def ensure_default_group(self) -> int:
        """Ensure Default custom group exists and return its ID"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if Default group already exists
        cursor.execute("SELECT id FROM custom_groups WHERE name = 'Default'")
        result = cursor.fetchone()
        
        if result:
            group_id = result[0]
        else:
            # Create Default group
            cursor.execute("""
                INSERT INTO custom_groups (name, icon)
                VALUES (?, ?)
            """, ("Default", "📁"))
            group_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        return group_id
    
    def delete_custom_group(self, group_id: int):
        """Delete a custom group"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("UPDATE custom_groups SET is_active = 0 WHERE id = ?", (group_id,))
        
        conn.commit()
        conn.close()
    
    def assign_file_to_custom_group(self, file_id: int, group_id: int):
        """Assign a file to a custom group"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO file_custom_groups (file_id, group_id)
            VALUES (?, ?)
        """, (file_id, group_id))
        
        conn.commit()
        conn.close()
    
    def get_files_in_custom_group(self, group_id: int) -> List[Dict]:
        """Get files in a custom group"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT yf.id, yf.name, yf.path, yf.config_type, yf.content, yf.parsed_yaml, 
                   yf.is_valid, yf.validation_errors, yf.created_at, yf.updated_at, 
                   yf.file_size, yf.file_hash
            FROM yaml_files yf
            JOIN file_custom_groups fcg ON yf.id = fcg.file_id
            WHERE fcg.group_id = ?
            ORDER BY yf.updated_at DESC
        """, (group_id,))
        
        columns = [description[0] for description in cursor.description]
        files = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        conn.close()
        return files
    
    def clear_all_data(self) -> bool:
        """Clear all data from the database - files, groups, templates, history, everything"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Clear all tables in the correct order (respecting foreign keys)
            cursor.execute("DELETE FROM file_custom_groups")
            cursor.execute("DELETE FROM file_history") 
            cursor.execute("DELETE FROM file_notes")
            cursor.execute("DELETE FROM custom_groups")
            cursor.execute("DELETE FROM templates")
            cursor.execute("DELETE FROM yaml_files")
            cursor.execute("DELETE FROM app_settings")
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error clearing database: {e}")
            return False
        finally:
            conn.close()
    
    def delete_file(self, file_id: int) -> bool:
        """Delete a file from database (removes from all groups and history)"""
        import datetime
        
        debug_log = "/Users/deep-diver/dstack-mgmt-tool/delete_debug.log"
        
        def log_debug(message):
            with open(debug_log, "a") as f:
                f.write(f"{datetime.datetime.now()}: {message}\n")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            log_debug(f"🔍 DELETE: Attempting to delete file with ID: {file_id}")
            
            # Check if file exists first
            cursor.execute("SELECT id, name FROM yaml_files WHERE id = ?", (file_id,))
            file_exists = cursor.fetchone()
            if not file_exists:
                log_debug(f"❌ DELETE: File with ID {file_id} not found")
                return False
            
            log_debug(f"🔍 DELETE: Found file: {file_exists[1]} (ID: {file_exists[0]})")
            
            # Delete from related tables first (foreign key constraints)
            cursor.execute("DELETE FROM file_custom_groups WHERE file_id = ?", (file_id,))
            deleted_groups = cursor.rowcount
            log_debug(f"🔍 DELETE: Deleted {deleted_groups} custom group assignments")
            
            cursor.execute("DELETE FROM file_history WHERE file_id = ?", (file_id,))
            deleted_history = cursor.rowcount
            log_debug(f"🔍 DELETE: Deleted {deleted_history} history entries")
            
            # Get the file path first to delete notes (file_notes uses file_path, not file_id)
            cursor.execute("SELECT path FROM yaml_files WHERE id = ?", (file_id,))
            file_path_result = cursor.fetchone()
            if file_path_result:
                file_path = file_path_result[0]
                cursor.execute("DELETE FROM file_notes WHERE file_path = ?", (file_path,))
                deleted_notes = cursor.rowcount
                log_debug(f"🔍 DELETE: Deleted {deleted_notes} note entries for path: {file_path}")
            else:
                log_debug(f"🔍 DELETE: No file path found for ID {file_id}, skipping notes deletion")
            
            # Finally delete the file itself
            cursor.execute("DELETE FROM yaml_files WHERE id = ?", (file_id,))
            deleted_files = cursor.rowcount
            log_debug(f"🔍 DELETE: Deleted {deleted_files} file record")
            
            if deleted_files == 0:
                log_debug(f"❌ DELETE: No file was deleted for ID {file_id}")
                return False
            
            conn.commit()
            log_debug(f"✅ DELETE: Successfully deleted file ID {file_id}")
            return True
        except Exception as e:
            log_debug(f"❌ DELETE_ERROR: {str(e)}")
            return False
        finally:
            conn.close()
    
    def delete_custom_group(self, group_id: int) -> bool:
        """Delete a custom group and all files in it"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Get all files in this group
            cursor.execute("SELECT file_id FROM file_custom_groups WHERE group_id = ?", (group_id,))
            file_ids = [row[0] for row in cursor.fetchall()]
            
            # Delete all files in the group
            for file_id in file_ids:
                cursor.execute("DELETE FROM file_custom_groups WHERE file_id = ?", (file_id,))
                cursor.execute("DELETE FROM file_history WHERE file_id = ?", (file_id,))
                
                # Get the file path to delete notes (file_notes uses file_path, not file_id)
                cursor.execute("SELECT path FROM yaml_files WHERE id = ?", (file_id,))
                file_path_result = cursor.fetchone()
                if file_path_result:
                    file_path = file_path_result[0]
                    cursor.execute("DELETE FROM file_notes WHERE file_path = ?", (file_path,))
                
                cursor.execute("DELETE FROM yaml_files WHERE id = ?", (file_id,))
            
            # Delete the group itself
            cursor.execute("DELETE FROM custom_groups WHERE id = ?", (group_id,))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting custom group: {e}")
            return False
        finally:
            conn.close()


@dataclass
class YAMLFile:
    path: Path
    name: str
    config_type: DStackConfigType
    content: str
    parsed_yaml: Optional[Dict[str, Any]] = None
    is_valid: bool = True
    validation_errors: List[str] = None


class YAMLManager:
    def __init__(self, root_path: Path = None, config_manager=None):
        self.root_path = root_path or Path.cwd()
        self.yaml_files: List[YAMLFile] = []
        self.config_manager = config_manager
        self.db = DatabaseManager(config_manager=config_manager)
        self.scan_files()
    
    def scan_files(self):
        """Load all files from database (SQLite is now primary storage)"""
        print("📊 SCANNING FILES FROM DATABASE")
        self.yaml_files.clear()
        
        # Load all files from database
        db_files = self.db.get_all_files()
        print(f"   Found {len(db_files)} files in database")
        
        for i, db_file in enumerate(db_files):
            print(f"   Loading file {i+1}: {db_file.get('name', 'UNNAMED')}")
            yaml_file = self._create_yaml_file_from_db(db_file)
            if yaml_file:
                self.yaml_files.append(yaml_file)
                print(f"     ✅ Loaded: {yaml_file.name}")
            else:
                print(f"     ❌ Failed to create YAMLFile from db_file")
        
        print(f"   Total loaded yaml_files: {len(self.yaml_files)}")
    
    def create_new_file(self, path: str, content: str, config_type: DStackConfigType) -> Optional[YAMLFile]:
        """Create a new YAML file in database (primary storage)"""
        try:
            # Parse YAML content
            parsed_yaml = None
            validation_errors = []
            is_valid = True
            
            try:
                parsed_yaml = yaml.safe_load(content)
            except yaml.YAMLError as e:
                is_valid = False
                validation_errors.append(f"YAML parsing error: {str(e)}")
            
            # Use the full path as entered by the user
            file_path = Path(path)
            
            yaml_file = YAMLFile(
                path=file_path,
                name=file_path.name,  # Extract filename from the full path
                config_type=config_type,
                content=content,
                parsed_yaml=parsed_yaml,
                is_valid=is_valid,
                validation_errors=validation_errors
            )
            
            # Add to database
            file_id = self.db.add_file(yaml_file)
            
            # Add to current list
            self.yaml_files.append(yaml_file)
            
            # Add creation history
            self.db.add_file_history(file_id, content, "created", "File created")
            
            return yaml_file
            
        except Exception as e:
            return None
    
    def update_file_content(self, yaml_file: YAMLFile, new_content: str) -> bool:
        """Update file content in database"""
        try:
            # Parse new content
            parsed_yaml = None
            validation_errors = []
            is_valid = True
            
            try:
                parsed_yaml = yaml.safe_load(new_content)
            except yaml.YAMLError as e:
                is_valid = False
                validation_errors.append(f"YAML parsing error: {str(e)}")
            
            # Update database
            self.db.update_file(
                str(yaml_file.path),
                new_content,
                parsed_yaml,
                is_valid,
                validation_errors
            )
            
            # Update object
            yaml_file.content = new_content
            yaml_file.parsed_yaml = parsed_yaml
            yaml_file.is_valid = is_valid
            yaml_file.validation_errors = validation_errors
            
            # Add to history
            file_data = self.db.get_file_by_path(str(yaml_file.path))
            if file_data:
                self.db.add_file_history(file_data['id'], new_content, "updated", "Content updated")
            
            return True
            
        except Exception as e:
            return False
    
    def delete_file(self, yaml_file: YAMLFile) -> bool:
        """Delete file from database"""
        try:
            self.db.delete_file(str(yaml_file.path))
            if yaml_file in self.yaml_files:
                self.yaml_files.remove(yaml_file)
            return True
        except:
            return False
    
    def _is_dstack_yaml(self, path: Path) -> bool:
        """Check if file is a dstack YAML configuration"""
        name = path.name.lower()
        return (
            name.endswith('.dstack.yml') or
            name.endswith('.dstack.yaml') or
            name in ['config.yml', 'config.yaml'] and 'dstack' in str(path.parent) or
            self._contains_dstack_config(path)
        )
    
    def _contains_dstack_config(self, path: Path) -> bool:
        """Check if YAML contains dstack configuration"""
        try:
            with open(path, 'r') as f:
                content = f.read()
                if 'type:' in content and any(t in content for t in ['task', 'service', 'fleet']):
                    return True
        except:
            pass
        return False
    
    def _create_yaml_file(self, path: Path) -> Optional[YAMLFile]:
        """Create YAMLFile object from path"""
        try:
            with open(path, 'r') as f:
                content = f.read()
            
            # Parse YAML
            parsed_yaml = None
            validation_errors = []
            is_valid = True
            
            try:
                parsed_yaml = yaml.safe_load(content)
            except yaml.YAMLError as e:
                is_valid = False
                validation_errors.append(f"YAML parsing error: {str(e)}")
            
            # Determine config type
            config_type = self._determine_config_type(path, parsed_yaml)
            
            return YAMLFile(
                path=path,
                name=path.name,
                config_type=config_type,
                content=content,
                parsed_yaml=parsed_yaml,
                is_valid=is_valid,
                validation_errors=validation_errors
            )
        except Exception as e:
            return None
    
    def _create_yaml_file_from_db(self, db_file: Dict) -> Optional[YAMLFile]:
        """Create YAMLFile object from database record"""
        try:
            config_type = DStackConfigType(db_file['config_type'])
            parsed_yaml = None
            validation_errors = None
            
            if db_file['parsed_yaml']:
                try:
                    parsed_yaml = eval(db_file['parsed_yaml'])
                except:
                    pass
            
            if db_file['validation_errors']:
                try:
                    validation_errors = eval(db_file['validation_errors'])
                except:
                    validation_errors = [db_file['validation_errors']]
            
            return YAMLFile(
                path=Path(db_file['path']),
                name=db_file['name'],
                config_type=config_type,
                content=db_file['content'],
                parsed_yaml=parsed_yaml,
                is_valid=bool(db_file['is_valid']),
                validation_errors=validation_errors
            )
        except Exception as e:
            return None
    
    def _determine_config_type(self, path: Path, parsed_yaml: Optional[Dict]) -> DStackConfigType:
        """Determine the type of dstack configuration"""
        if parsed_yaml and isinstance(parsed_yaml, dict):
            yaml_type = parsed_yaml.get('type', '').lower()
            if yaml_type in ['task', 'service', 'fleet']:
                return DStackConfigType(yaml_type)
        
        # Fallback to filename patterns
        name = path.name.lower()
        if 'service' in name:
            return DStackConfigType.SERVICE
        elif 'fleet' in name:
            return DStackConfigType.FLEET
        elif 'config' in name:
            return DStackConfigType.SERVER
        else:
            return DStackConfigType.TASK
    
    def get_files_by_type(self, config_type: DStackConfigType) -> List[YAMLFile]:
        """Get files filtered by configuration type"""
        return [f for f in self.yaml_files if f.config_type == config_type]
    
    def get_files_by_directory(self) -> Dict[str, List[YAMLFile]]:
        """Group files by directory"""
        groups = {}
        for yaml_file in self.yaml_files:
            dir_name = str(yaml_file.path.parent.relative_to(self.root_path))
            if dir_name not in groups:
                groups[dir_name] = []
            groups[dir_name].append(yaml_file)
        return groups


class FileTreeWidget(Tree):
    def __init__(self, yaml_manager: YAMLManager, **kwargs):
        super().__init__("dstack YAML Files", **kwargs)
        self.yaml_manager = yaml_manager
        self.current_file = reactive(None)
        self.build_tree()
    
    def build_tree(self):
        """Build the file tree with grouping"""
        print("🌳 BUILDING TREE")
        self.clear()
        
        # Add dstack global config as first node
        print("   Adding global config node...")
        global_config_node = self.root.add("🌐 dstack Global Config")
        global_config_file = self._load_global_config()
        global_config_node.data = global_config_file
        print(f"   Global config: {global_config_file.name}")
        
        # Get all files that are in custom groups so we can exclude them from default type groups
        files_in_custom_groups = set()
        custom_groups = self.yaml_manager.db.get_custom_groups()
        for group in custom_groups:
            files_in_group = self.yaml_manager.db.get_files_in_custom_group(group['id'])
            for file_data in files_in_group:
                files_in_custom_groups.add(file_data['path'])
        
        # Group by type (excluding files that are in custom groups)
        print("   Adding type groups...")
        type_nodes = {}
        for config_type in DStackConfigType:
            files = self.yaml_manager.get_files_by_type(config_type)
            # Filter out files that are in custom groups
            files_not_in_custom_groups = [f for f in files if str(f.path) not in files_in_custom_groups]
            print(f"   {config_type.value}: {len(files_not_in_custom_groups)} files (total: {len(files)}, in custom: {len(files) - len(files_not_in_custom_groups)})")
            if files_not_in_custom_groups:
                type_node = self.root.add(f"📁 {config_type.value.title()} ({len(files_not_in_custom_groups)})")
                type_nodes[config_type] = type_node
                
                for yaml_file in files_not_in_custom_groups:
                    print(f"     Adding file: {yaml_file.name}")
                    file_node = type_node.add(yaml_file.name)
                    file_node.data = yaml_file
        
        # Add custom groups
        custom_groups = self.yaml_manager.db.get_custom_groups()
        
        # Find the Default group among custom groups, or create a virtual one
        default_group = None
        other_custom_groups = []
        
        for group in custom_groups or []:
            if group['name'] == 'Default':
                default_group = group
            else:
                other_custom_groups.append(group)
        
        # Add default "Default" group (always visible, shows files from Default custom group)
        print("   Adding Default group...")
        if default_group:
            files_in_default = self.yaml_manager.db.get_files_in_custom_group(default_group['id'])
            group_files = [self.yaml_manager._create_yaml_file_from_db(f) for f in files_in_default if f]
            group_files = [f for f in group_files if f]  # Filter out None
            count = len(group_files)
            
            default_group_node = self.root.add(f"📁 Default ({count})")
            default_group_node.data = {'type': 'custom_group', 'group_data': default_group}
            
            for yaml_file in group_files:
                file_node = default_group_node.add(yaml_file.name)
                file_node.data = yaml_file
        else:
            # No Default group exists yet, show empty
            default_group_node = self.root.add("📁 Default (0)")
            default_group_node.data = {'type': 'default_group', 'name': 'Default'}
        # Add other custom groups (excluding Default which we handled above)
        if other_custom_groups:
            for group in other_custom_groups:
                files_in_group = self.yaml_manager.db.get_files_in_custom_group(group['id'])
                group_files = [self.yaml_manager._create_yaml_file_from_db(f) for f in files_in_group if f]
                group_files = [f for f in group_files if f]  # Filter out None
                
                group_node = self.root.add(f"{group['icon']} {group['name']} ({len(group_files)})")
                group_node.data = {'type': 'custom_group', 'group_data': group}
                
                for yaml_file in group_files:
                    file_node = group_node.add(yaml_file.name)
                    file_node.data = yaml_file
        
        # Expand all nodes
        for node in self.root.children:
            if hasattr(node, 'allow_expand') and not node.allow_expand:
                continue
            node.expand()
    
    def _load_global_config(self) -> YAMLFile:
        """Load dstack global config from ~/.dstack/config.yml"""
        try:
            global_config_path = Path.home() / ".dstack" / "config.yml"
            
            if global_config_path.exists():
                with open(global_config_path, 'r') as f:
                    content = f.read()
            else:
                # Create default content if file doesn't exist
                content = """# dstack global configuration
# See: https://dstack.ai/docs/reference/server/config.yml

projects: []

backends: []
"""
            
            # Parse YAML
            parsed_yaml = None
            validation_errors = []
            is_valid = True
            
            try:
                parsed_yaml = yaml.safe_load(content)
            except yaml.YAMLError as e:
                is_valid = False
                validation_errors.append(f"YAML parsing error: {str(e)}")
            
            return YAMLFile(
                path=global_config_path,
                name="config.yml",
                config_type=DStackConfigType.SERVER,
                content=content,
                parsed_yaml=parsed_yaml,
                is_valid=is_valid,
                validation_errors=validation_errors
            )
            
        except Exception as e:
            # Return error placeholder if we can't load
            return YAMLFile(
                path=Path.home() / ".dstack" / "config.yml",
                name="config.yml",
                config_type=DStackConfigType.SERVER,
                content=f"# Error loading global config: {str(e)}",
                parsed_yaml=None,
                is_valid=False,
                validation_errors=[str(e)]
            )
    
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle file selection"""
        if hasattr(event.node, 'data') and event.node.data:
            # Only handle actual YAML files (not groups or other nodes)
            if hasattr(event.node.data, 'name') and hasattr(event.node.data, 'path'):
                self.current_file = event.node.data
                self.post_message(FileSelected(event.node.data))
                # Also notify for debugging
                self.app.notify(f"Tree: {event.node.data.name}", timeout=2)


class FileSelected(Message):
    def __init__(self, yaml_file: YAMLFile):
        super().__init__()
        self.yaml_file = yaml_file


class YAMLPreviewWidget(Container):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_file = None
    
    def compose(self) -> ComposeResult:
        with TabbedContent(initial="preview"):
            with TabPane("Preview", id="preview"):
                with ScrollableContainer(id="preview-container"):
                    yield Static("Select a YAML file to preview", id="preview-content")
            with TabPane("Note", id="note"):
                with Container(id="note-container"):
                    yield TextArea("Select a YAML file to add notes", id="note-content")
            with TabPane("Metadata", id="metadata"):
                with ScrollableContainer(id="metadata-container"):
                    yield Static("Select a YAML file to view metadata", id="metadata-content")
    
    def update_preview(self, yaml_file: YAMLFile):
        """Update all tabs with selected YAML file"""
        self.current_file = yaml_file
        self._update_preview_tab(yaml_file)
        self._update_note_tab(yaml_file)
        self._update_metadata_tab(yaml_file)
    
    def _update_preview_tab(self, yaml_file: YAMLFile):
        """Update the preview tab with syntax highlighted content"""
        try:
            syntax = Syntax(
                yaml_file.content,
                "yaml",
                theme="monokai",
                line_numbers=True,
                word_wrap=False
            )
            
            content_widget = self.query_one("#preview-content", Static)
            content_widget.update(Panel(syntax, title=yaml_file.name))
            
        except Exception as e:
            content_widget = self.query_one("#preview-content", Static)
            content_widget.update(f"Error displaying file: {str(e)}")
    
    def _update_note_tab(self, yaml_file: YAMLFile):
        """Update the note tab with markdown content for the selected file"""
        try:
            # Get note for this file from database (editable)
            note_content = self._get_file_note(yaml_file.path)
            note_widget = self.query_one("#note-content", TextArea)
            if note_content:
                # Load note content into editable text area
                note_widget.text = note_content
            else:
                note_widget.text = "# Notes for this file\n\nAdd your notes here..."
            
            # Store current file path for saving in the main app
            self.app.current_note_file_path = yaml_file.path
        except Exception as e:
            note_widget = self.query_one("#note-content", TextArea)
            note_widget.text = f"Error loading note: {str(e)}"
    
    def _get_file_note(self, file_path: Path) -> str:
        """Get note content for a file from database"""
        # Access database through the app's yaml_manager
        if hasattr(self.app, 'yaml_manager'):
            return self.app.yaml_manager.db.get_file_note(str(file_path))
        return ""
    
    def _update_metadata_tab(self, yaml_file: YAMLFile):
        """Update the metadata tab with file information"""
        try:
            metadata_lines = []
            
            # Basic file information
            metadata_lines.append("📄 **File Information**")
            metadata_lines.append(f"Name: {yaml_file.name}")
            metadata_lines.append(f"Path: {yaml_file.path}")
            metadata_lines.append(f"Type: {yaml_file.config_type.value}")
            
            # Check if it's a global config by examining the path
            is_global = "/.dstack/" in str(yaml_file.path) and yaml_file.name == "config.yml"
            metadata_lines.append(f"Global Config: {'Yes' if is_global else 'No'}")
            metadata_lines.append("")
            
            # File size and content info
            content_size = len(yaml_file.content.encode('utf-8'))
            line_count = yaml_file.content.count('\n') + 1
            metadata_lines.append("📊 **Content Statistics**")
            metadata_lines.append(f"File Size: {content_size:,} bytes")
            metadata_lines.append(f"Lines: {line_count:,}")
            metadata_lines.append(f"Characters: {len(yaml_file.content):,}")
            metadata_lines.append("")
            
            # Validation status
            metadata_lines.append("✅ **Validation Status**")
            metadata_lines.append(f"Valid YAML: {'Yes' if yaml_file.is_valid else 'No'}")
            if yaml_file.validation_errors and len(yaml_file.validation_errors) > 0:
                metadata_lines.append("Errors:")
                for error in yaml_file.validation_errors:
                    metadata_lines.append(f"  • {error}")
            else:
                metadata_lines.append("No validation errors")
            metadata_lines.append("")
            
            # Database information
            if hasattr(self.app, 'yaml_manager'):
                db_info = self.app.yaml_manager.db.get_file_by_path(str(yaml_file.path))
                if db_info:
                    metadata_lines.append("💾 **Database Information**")
                    metadata_lines.append(f"Created: {db_info.get('created_at', 'Unknown')}")
                    metadata_lines.append(f"Modified: {db_info.get('updated_at', 'Unknown')}")
                    metadata_lines.append(f"History Entries: {db_info.get('history_count', 0)}")
                    metadata_lines.append("")
            
            # YAML structure info
            if yaml_file.parsed_yaml:
                metadata_lines.append("🏗️ **YAML Structure**")
                try:
                    import yaml
                    if isinstance(yaml_file.parsed_yaml, dict):
                        key_count = len(yaml_file.parsed_yaml.keys())
                        metadata_lines.append(f"Top-level keys: {key_count}")
                        metadata_lines.append("Keys:")
                        for key in sorted(yaml_file.parsed_yaml.keys()):
                            value = yaml_file.parsed_yaml[key]
                            value_type = type(value).__name__
                            metadata_lines.append(f"  • {key}: {value_type}")
                    elif isinstance(yaml_file.parsed_yaml, list):
                        metadata_lines.append(f"Array with {len(yaml_file.parsed_yaml)} items")
                    else:
                        metadata_lines.append(f"Single value: {type(yaml_file.parsed_yaml).__name__}")
                except Exception as e:
                    metadata_lines.append(f"Error analyzing structure: {e}")
                metadata_lines.append("")
            
            # Join all metadata into a single string
            metadata_content = "\n".join(metadata_lines)
            
            metadata_widget = self.query_one("#metadata-content", Static)
            metadata_widget.update(metadata_content)
            
        except Exception as e:
            metadata_widget = self.query_one("#metadata-content", Static)
            metadata_widget.update(f"Error loading metadata: {str(e)}")
    


class YAMLPropertiesWidget(ScrollableContainer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_file = None
    
    def compose(self) -> ComposeResult:
        yield Static("Select a YAML file to view properties", id="properties-content", markup=True)
    
    def update_properties(self, yaml_file: YAMLFile):
        """Update properties panel with file details"""
        self.current_file = yaml_file
        
        # Build properties with rich text instead of markup to avoid parsing issues
        from rich.text import Text
        
        text = Text()
        text.append("File: ", style="bold")
        text.append(f"{yaml_file.name}\n")
        text.append("Type: ", style="bold")
        text.append(f"{yaml_file.config_type.value}\n")
        text.append("Path: ", style="bold")
        text.append(f"{yaml_file.path}\n")
        
        if yaml_file.parsed_yaml:
            # Extract key properties from parsed YAML
            if isinstance(yaml_file.parsed_yaml, dict):
                for key in ['type', 'name', 'python', 'image', 'port', 'resources']:
                    if key in yaml_file.parsed_yaml:
                        value = yaml_file.parsed_yaml[key]
                        text.append(f"{key.title()}: ", style="bold")
                        text.append(f"{value}\n")
        
        if not yaml_file.is_valid and yaml_file.validation_errors:
            text.append("Errors:\n", style="bold red")
            for error in yaml_file.validation_errors:
                text.append("  • ", style="red")
                # Truncate very long error messages
                error_text = str(error)[:200] + "..." if len(str(error)) > 200 else str(error)
                text.append(f"{error_text}\n")
        
        properties_widget = self.query_one("#properties-content", Static)
        properties_widget.update(text)


class AddFileScreen(Screen):
    """Screen for adding existing YAML files to selected groups"""
    
    CSS = """
    AddFileScreen {
        layout: vertical;
        align: center middle;
    }
    
    #add-file-container {
        width: 80;
        height: auto;
        border: solid $primary;
        background: $surface;
        padding: 2;
    }
    
    #group-list {
        height: 10;
        border: solid $accent;
        margin: 1 0;
    }
    
    #filepath-input {
        margin: 1 0;
    }
    
    #completion-hint {
        height: 2;
        margin: 1 0;
        color: $text-muted;
    }
    
    #completion-dropdown {
        height: 8;
        margin: 1 0;
        border: solid $accent;
        display: none;
    }
    
    #completion-dropdown.visible {
        display: block;
    }
    
    #button-row {
        layout: horizontal;
        height: 3;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "handle_enter", "Add File"),
        Binding("tab", "show_completions", "Complete"),
        Binding("up", "completion_up", "Up", show=False),
        Binding("down", "completion_down", "Down", show=False),
    ]
    
    def __init__(self):
        super().__init__()
        self.groups = ["Task", "Service", "Fleet", "Server"]
        self.custom_groups = []
        self.current_completions = []
        self.completion_index = 0
        self.dropdown_visible = False
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("Add Existing YAML File", id="title"),
            Static("Select Group:", id="group-label"),
            Tree("Groups", id="group-list"),
            Static("Enter file path:", id="filepath-label"),
            Input(placeholder="Enter path to .dstack.yml file (Tab to complete)", id="filepath-input"),
            Static("Press Tab to show completions", id="completion-hint"),
            Tree("Completions", id="completion-dropdown"),
            Horizontal(
                Button("Add File", variant="primary", id="add-btn"),
                Button("Cancel", variant="default", id="cancel-btn"),
                id="button-row"
            ),
            id="add-file-container"
        )
    
    def on_mount(self) -> None:
        """Setup the group tree and file input"""
        # Setup group list to exactly match the main tree view
        group_tree = self.query_one("#group-list", Tree)
        
        if hasattr(self.app, 'yaml_manager'):
            # Use the same logic as the main tree view to ensure perfect synchronization
            
            # Get all files that are in custom groups so we can exclude them from default type groups
            files_in_custom_groups = set()
            custom_groups = self.app.yaml_manager.db.get_custom_groups()
            for group in custom_groups or []:
                files_in_group = self.app.yaml_manager.db.get_files_in_custom_group(group['id'])
                for file_data in files_in_group:
                    files_in_custom_groups.add(file_data['path'])
            
            # Group by type (excluding files that are in custom groups) - same logic as main tree
            from collections import defaultdict
            type_counts = defaultdict(int)
            
            for config_type in DStackConfigType:
                files = self.app.yaml_manager.get_files_by_type(config_type)
                # Filter out files that are in custom groups
                files_not_in_custom_groups = [f for f in files if str(f.path) not in files_in_custom_groups]
                if files_not_in_custom_groups:
                    type_counts[config_type] = len(files_not_in_custom_groups)
            
            # Find Default group among custom groups
            default_group = None
            other_custom_groups = []
            
            for group in custom_groups or []:
                if group['name'] == 'Default':
                    default_group = group
                else:
                    other_custom_groups.append(group)
            
            # Add Default group first (always visible)
            if default_group:
                files_in_default = self.app.yaml_manager.db.get_files_in_custom_group(default_group['id'])
                count = len(files_in_default)
                default_node = group_tree.root.add(f"📁 Default ({count})")
                default_node.data = {'type': 'custom', 'value': default_group['id'], 'name': 'Default'}
            else:
                default_node = group_tree.root.add("📁 Default (0)")
                default_node.data = {'type': 'default_group', 'value': 'default', 'name': 'Default'}
            
            # Add dstack configuration groups that actually have files (excluding those in custom groups)
            for config_type, count in type_counts.items():
                display_name = f"📁 {config_type.value.title()} ({count})"
                node = group_tree.root.add(display_name)
                node.data = {'type': 'default', 'value': config_type.value}
            
            # Add other custom groups (excluding Default which we handled above)
            if other_custom_groups:
                for group in other_custom_groups:
                    files_in_group = self.app.yaml_manager.db.get_files_in_custom_group(group['id'])
                    group_files = [self.app.yaml_manager._create_yaml_file_from_db(f) for f in files_in_group if f]
                    group_files = [f for f in group_files if f]  # Filter out None
                    
                    display_name = f"{group['icon']} {group['name']} ({len(group_files)})"
                    node = group_tree.root.add(display_name)
                    node.data = {'type': 'custom', 'value': group['id'], 'name': group['name']}
        
        group_tree.root.expand()
        
        # Focus filepath input
        self.query_one("#filepath-input", Input).focus()
    
    def action_show_completions(self) -> None:
        """Show completion dropdown when Tab is pressed, or auto-complete if only one option"""
        filepath_input = self.query_one("#filepath-input", Input)
        current_path = filepath_input.value
        
        if not current_path:
            current_path = str(Path.cwd()) + "/"
            filepath_input.value = current_path
            filepath_input.cursor_position = len(current_path)
        
        completions = self.get_completions(current_path)
        if completions:
            if len(completions) == 1:
                # Auto-complete when there's only one option
                completion = completions[0]
                filepath_input.value = completion['path']
                filepath_input.cursor_position = len(completion['path'])
                self.hide_completion_dropdown()
            else:
                # Show dropdown when there are multiple options
                self.show_completion_dropdown(completions)
        else:
            self.hide_completion_dropdown()
    
    def action_completion_up(self) -> None:
        """Move up in completion dropdown"""
        if self.dropdown_visible and self.current_completions:
            self.completion_index = (self.completion_index - 1) % len(self.current_completions)
            self.update_completion_selection()
    
    def action_completion_down(self) -> None:
        """Move down in completion dropdown"""
        if self.dropdown_visible and self.current_completions:
            self.completion_index = (self.completion_index + 1) % len(self.current_completions)
            self.update_completion_selection()
    
    def get_completions(self, current_path: str) -> list:
        """Get list of possible completions for current path"""
        completions = []
        try:
            input_path = Path(current_path)
            
            # Expand home directory shortcut
            if current_path.startswith("~"):
                current_path = str(Path(current_path).expanduser())
                input_path = Path(current_path)
            
            if current_path.endswith('/') or input_path.is_dir():
                # Show directory contents
                search_dir = input_path if input_path.is_dir() else input_path.parent
                try:
                    for item in search_dir.iterdir():
                        if item.is_dir():
                            completions.append({
                                'path': str(item) + "/",
                                'display': f"📂 {item.name}/",
                                'type': 'directory'
                            })
                        elif item.name.endswith(('.yml', '.yaml')):
                            icon = "📄" if 'dstack' in item.name else "📋"
                            completions.append({
                                'path': str(item),
                                'display': f"{icon} {item.name}",
                                'type': 'yaml'
                            })
                except PermissionError:
                    pass
            else:
                # Show matching files in parent directory
                parent_dir = input_path.parent
                filename_start = input_path.name
                try:
                    for item in parent_dir.iterdir():
                        if item.name.startswith(filename_start):
                            if item.is_dir():
                                completions.append({
                                    'path': str(item) + "/",
                                    'display': f"📂 {item.name}/",
                                    'type': 'directory'
                                })
                            elif item.name.endswith(('.yml', '.yaml')):
                                icon = "📄" if 'dstack' in item.name else "📋"
                                completions.append({
                                    'path': str(item),
                                    'display': f"{icon} {item.name}",
                                    'type': 'yaml'
                                })
                except (FileNotFoundError, PermissionError):
                    pass
            
            # Sort: directories first, then YAML files, then others
            completions.sort(key=lambda x: (x['type'] != 'directory', x['type'] != 'yaml', x['display'].lower()))
            
        except Exception:
            pass
        
        return completions
    
    def show_completion_dropdown(self, completions: list):
        """Show the completion dropdown with options"""
        self.current_completions = completions
        self.completion_index = 0
        self.dropdown_visible = True
        
        dropdown = self.query_one("#completion-dropdown", Tree)
        dropdown.clear()
        
        for i, completion in enumerate(completions):
            node = dropdown.root.add(completion['display'])
            node.data = completion['path']
        
        dropdown.root.expand()
        dropdown.display = True
        
        # Select first item
        if completions:
            self.update_completion_selection()
    
    def hide_completion_dropdown(self):
        """Hide the completion dropdown"""
        self.dropdown_visible = False
        dropdown = self.query_one("#completion-dropdown", Tree)
        dropdown.display = False
        dropdown.clear()
    
    def update_completion_selection(self):
        """Update the selected item in dropdown"""
        dropdown = self.query_one("#completion-dropdown", Tree)
        if self.current_completions and 0 <= self.completion_index < len(self.current_completions):
            # Rebuild dropdown with selected item highlighted
            dropdown.clear()
            
            for i, completion in enumerate(self.current_completions):
                if i == self.completion_index:
                    # Highlight selected item
                    display_text = f"→ {completion['display']}"
                else:
                    display_text = f"  {completion['display']}"
                
                node = dropdown.root.add(display_text)
                node.data = completion['path']
            
            dropdown.root.expand()
    
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle completion selection from dropdown"""
        # Check if this is from the completion dropdown
        if hasattr(event.node, 'data') and event.node.data:
            # Get the tree that triggered this event
            tree = event.control
            if tree.id == "completion-dropdown":
                # Find which completion was selected and update completion_index
                for i, completion in enumerate(self.current_completions):
                    if completion['path'] == event.node.data:
                        self.completion_index = i
                        break
                
                filepath_input = self.query_one("#filepath-input", Input)
                filepath_input.value = event.node.data
                filepath_input.cursor_position = len(event.node.data)
                self.hide_completion_dropdown()
                filepath_input.focus()
        
    def on_input_changed(self, event: Input.Changed) -> None:
        """Hide dropdown when user types"""
        if event.input.id == "filepath-input" and self.dropdown_visible:
            self.hide_completion_dropdown()
    
    def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key pressed in input field"""
        if event.input.id == "filepath-input":
            if self.dropdown_visible and self.current_completions:
                # Enter selects current completion
                if 0 <= self.completion_index < len(self.current_completions):
                    completion = self.current_completions[self.completion_index]
                    event.input.value = completion['path']
                    event.input.cursor_position = len(completion['path'])
                    self.hide_completion_dropdown()
                    return
            
            # Regular add file functionality if no dropdown
            self.add_file()
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "add-btn":
            self.add_file()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()
    
    def action_cancel(self) -> None:
        """Cancel and return to main screen"""
        self.app.pop_screen()
    
    def action_handle_enter(self) -> None:
        """Handle Enter key - either select completion or add file"""
        if self.dropdown_visible and self.current_completions:
            # Enter selects current completion
            if 0 <= self.completion_index < len(self.current_completions):
                completion = self.current_completions[self.completion_index]
                filepath_input = self.query_one("#filepath-input", Input)
                filepath_input.value = completion['path']
                filepath_input.cursor_position = len(completion['path'])
                self.hide_completion_dropdown()
                # Focus the input field after selection
                filepath_input.focus()
                return
        
        # Regular add file functionality
        self.add_file()
    
    def add_file(self) -> None:
        """Add existing YAML file to selected group"""
        group_tree = self.query_one("#group-list", Tree)
        filepath_input = self.query_one("#filepath-input", Input)
        
        # Get selected group
        selected_group_data = None
        if group_tree.cursor_node and hasattr(group_tree.cursor_node, 'data') and group_tree.cursor_node.data:
            selected_group_data = group_tree.cursor_node.data
        
        if not selected_group_data:
            self.notify("Please select a group", severity="warning", markup=False)
            return
        
        filepath = filepath_input.value.strip()
        if not filepath:
            self.notify("Please enter a file path", severity="warning", markup=False)
            return
        
        file_path = Path(filepath)
        
        # Check if file exists
        if not file_path.exists():
            self.notify("File does not exist", severity="error", markup=False)
            return
        
        # Check if it's a YAML file
        if not file_path.name.endswith(('.yml', '.yaml')):
            self.notify("File must be a .yml or .yaml file", severity="error", markup=False)
            return
        
        # Check if file already exists in database
        if hasattr(self.app, 'yaml_manager'):
            existing_file = self.app.yaml_manager.db.get_file_by_path(str(file_path))
            if existing_file:
                self.notify("File already added to database", severity="error", markup=False)
                return
        
        try:
            # Read and add file to database
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Determine config type and handling
            if selected_group_data['type'] == 'default':
                config_type = DStackConfigType(selected_group_data['value'])
                group_name = selected_group_data['value'].title()
                
                if hasattr(self.app, 'yaml_manager'):
                    yaml_file = self.app.yaml_manager.create_new_file(str(file_path), content, config_type)
                    if not yaml_file:
                        raise Exception("Failed to add file to database")
            elif selected_group_data['type'] == 'default_group':
                # For default group, create a special "default" custom group to keep files separate
                group_name = selected_group_data['name']
                
                # First, ensure we have a "Default" custom group in the database
                default_group_id = self.app.yaml_manager.db.ensure_default_group()
                
                # Use TASK as config type but assign to Default custom group
                config_type = DStackConfigType.TASK
                
                if hasattr(self.app, 'yaml_manager'):
                    yaml_file = self.app.yaml_manager.create_new_file(str(file_path), content, config_type)
                    if not yaml_file:
                        raise Exception("Failed to add file to database")
                    
                    # Assign the file to the Default custom group
                    file_data = self.app.yaml_manager.db.get_file_by_path(str(file_path))
                    if file_data:
                        self.app.yaml_manager.db.assign_file_to_custom_group(
                            file_data['id'], 
                            default_group_id
                        )
            else:
                # For custom groups, use task as default config type to avoid creating "Unknown" group
                config_type = DStackConfigType.TASK
                group_name = selected_group_data['name']
                
                if hasattr(self.app, 'yaml_manager'):
                    yaml_file = self.app.yaml_manager.create_new_file(str(file_path), content, config_type)
                    if not yaml_file:
                        raise Exception("Failed to add file to database")
                    
                    # Assign the file to the custom group
                    file_data = self.app.yaml_manager.db.get_file_by_path(str(file_path))
                    if file_data:
                        self.app.yaml_manager.db.assign_file_to_custom_group(
                            file_data['id'], 
                            selected_group_data['value']
                        )
            
            self.notify(f"Added {file_path.name} to {group_name} group", 
                       severity="information", markup=False)
            self.app.pop_screen()
            
            # Refresh the main screen
            if hasattr(self.app, 'action_refresh'):
                self.app.action_refresh()
                
        except Exception as e:
            self.notify(f"Failed to add file: {str(e)}", severity="error", markup=False)


class NewGroupScreen(Screen):
    """Screen for creating new custom groups"""
    
    CSS = """
    NewGroupScreen {
        layout: vertical;
        align: center middle;
    }
    
    #new-group-container {
        width: 60;
        height: auto;
        border: solid $primary;
        background: $surface;
        padding: 2;
    }
    
    #group-name-input {
        margin: 1 0;
    }
    
    #group-description-input {
        margin: 1 0;
    }
    
    #icon-selector {
        height: 8;
        border: solid $accent;
        margin: 1 0;
    }
    
    #button-row {
        layout: horizontal;
        height: 3;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "create_group", "Create Group"),
    ]
    
    def __init__(self):
        super().__init__()
        self.icons = ["📁", "🗂️", "📂", "🎯", "⭐", "🏷️", "🔖", "📝", "💼", "🎨"]
        self.selected_icon = "📁"
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static("Create New Group", id="title"),
            Static("Group Name:", id="name-label"),
            Input(placeholder="Enter group name", id="group-name-input"),
            Static("Description (optional):", id="description-label"),
            Input(placeholder="Enter description", id="group-description-input"),
            Static("Select Icon:", id="icon-label"),
            Tree("Icons", id="icon-selector"),
            Horizontal(
                Button("Create Group", variant="primary", id="create-btn"),
                Button("Cancel", variant="default", id="cancel-btn"),
                id="button-row"
            ),
            id="new-group-container"
        )
    
    def on_mount(self) -> None:
        """Setup the icon selector and focus name input"""
        # Setup icon tree
        icon_tree = self.query_one("#icon-selector", Tree)
        for icon in self.icons:
            node = icon_tree.root.add(f"{icon}")
            node.data = icon
        icon_tree.root.expand()
        
        # Focus name input
        self.query_one("#group-name-input", Input).focus()
    
    def on_tree_node_selected(self, event: Tree.NodeSelected) -> None:
        """Handle icon selection"""
        if hasattr(event.node, 'data') and event.node.data:
            tree = event.control
            if tree.id == "icon-selector":
                self.selected_icon = event.node.data
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button clicks"""
        if event.button.id == "create-btn":
            self.create_group()
        elif event.button.id == "cancel-btn":
            self.app.pop_screen()
    
    def action_cancel(self) -> None:
        """Cancel and return to main screen"""
        self.app.pop_screen()
    
    def action_create_group(self) -> None:
        """Create group on Enter key"""
        self.create_group()
    
    def create_group(self) -> None:
        """Create the new custom group"""
        name_input = self.query_one("#group-name-input", Input)
        description_input = self.query_one("#group-description-input", Input)
        
        group_name = name_input.value.strip()
        group_description = description_input.value.strip()
        
        if not group_name:
            self.notify("Please enter a group name", severity="warning", markup=False)
            return
        
        try:
            if hasattr(self.app, 'yaml_manager'):
                group_id = self.app.yaml_manager.db.add_custom_group(
                    group_name, 
                    group_description, 
                    "#1e90ff",  # Default color
                    self.selected_icon
                )
                
                self.notify(f"Created group '{group_name}' successfully!", 
                           severity="information", markup=False)
                self.app.pop_screen()
                
                # Refresh the main screen
                if hasattr(self.app, 'action_refresh'):
                    self.app.action_refresh()
                    
        except Exception as e:
            error_msg = "Group name already exists" if "UNIQUE constraint failed" in str(e) else "Failed to create group"
            self.notify(error_msg, severity="error", markup=False)


class YAMLEditorScreen(Screen):
    """Full-screen YAML editor"""
    
    CSS = """
    YAMLEditorScreen {
        layout: vertical;
    }
    
    #editor-header {
        height: 3;
        background: $primary;
        color: $text;
        margin-bottom: 1;
    }
    
    #editor-textarea {
        height: 1fr;
        margin: 0 1;
        border: solid $primary;
    }
    
    #editor-footer {
        height: 3;
        background: $surface;
        margin-top: 1;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+s", "save_file", "Save"),
        Binding("escape", "save_and_exit", "Save & Exit"),
    ]
    
    def __init__(self, yaml_file: YAMLFile):
        super().__init__()
        self.yaml_file = yaml_file
        self.original_content = yaml_file.content
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static(f"Editing: {self.yaml_file.name} | Ctrl+S: Save | Esc: Save & Exit", 
                   id="editor-header"),
            TextArea(
                self.yaml_file.content,
                language="yaml",
                theme="monokai",
                id="editor-textarea"
            ),
            Static("", id="editor-footer"),
            id="editor-container"
        )
    
    def on_mount(self) -> None:
        """Focus the text area when screen opens"""
        text_area = self.query_one("#editor-textarea", TextArea)
        text_area.focus()
    
    def action_save_file(self) -> None:
        """Save the file"""
        text_area = self.query_one("#editor-textarea", TextArea)
        new_content = text_area.text
        
        try:
            # Validate YAML before saving
            yaml.safe_load(new_content)
            
            # Check if this is the global config file
            if str(self.yaml_file.path).endswith("/.dstack/config.yml"):
                # Save global config to filesystem
                self.yaml_file.path.parent.mkdir(parents=True, exist_ok=True)
                with open(self.yaml_file.path, 'w') as f:
                    f.write(new_content)
                
                # Update the object
                self.yaml_file.content = new_content
                self.yaml_file.parsed_yaml = yaml.safe_load(new_content)
                self.yaml_file.is_valid = True
                self.yaml_file.validation_errors = []
                
                self.notify("Global config saved successfully!", severity="information", markup=False)
            else:
                # Update in database for regular files
                if hasattr(self.app, 'yaml_manager'):
                    success = self.app.yaml_manager.update_file_content(self.yaml_file, new_content)
                    if not success:
                        raise Exception("Failed to update file in database")
                
                self.notify("File saved successfully!", severity="information", markup=False)
            
        except yaml.YAMLError as e:
            # Simple error message without special characters
            self.notify("YAML syntax error - please check your formatting", severity="error", markup=False)
        except Exception as e:
            self.notify("Save error - could not write file", severity="error", markup=False)
    
    
    def action_save_and_exit(self) -> None:
        """Save file and return to main screen"""
        try:
            self.action_save_file()
        except:
            # If save fails, still exit but don't update the file object
            pass
        # Always exit regardless of save success/failure
        self.app.pop_screen()


class ConfirmDeleteScreen(Screen):
    """Confirmation modal for delete operations"""
    
    CSS = """
    ConfirmDeleteScreen {
        align: center middle;
        background: $surface-darken-2 80%;
    }
    
    #delete-dialog {
        width: 60;
        height: 15;
        border: thick $warning 80%;
        background: $surface;
        content-align: center middle;
        layout: vertical;
    }
    
    #delete-title {
        width: 100%;
        height: 3;
        content-align: center middle;
        text-style: bold;
        color: $warning;
    }
    
    #delete-message {
        width: 100%;
        height: 5;
        content-align: center middle;
        text-align: center;
    }
    
    #button-container {
        layout: horizontal;
        width: 100%;
        height: 3;
        align: center middle;
    }
    
    Button {
        margin: 0 1;
        width: 12;
    }
    """
    
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("enter", "confirm_delete", "Delete"),
        Binding("y", "confirm_delete", "Yes"),
        Binding("n", "cancel", "No"),
    ]
    
    def __init__(self, item_name: str, item_type: str, callback):
        super().__init__()
        self.item_name = item_name
        self.item_type = item_type
        self.callback = callback
    
    def compose(self) -> ComposeResult:
        with Container(id="delete-dialog"):
            yield Static("⚠️ Confirm Delete", id="delete-title")
            yield Static(f"Are you sure you want to delete the {self.item_type}:\n\n'{self.item_name}'?\n\nThis action cannot be undone.", id="delete-message")
            with Container(id="button-container"):
                yield Button("Cancel", variant="default", id="cancel-btn")
                yield Button("Delete", variant="error", id="delete-btn")
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "delete-btn":
            self.action_confirm_delete()
        else:
            self.action_cancel()
    
    def action_confirm_delete(self) -> None:
        """Confirm the deletion"""
        self.app.pop_screen()
        if self.callback:
            self.callback()
    
    def action_cancel(self) -> None:
        """Cancel the deletion"""
        self.app.pop_screen()


class NavigateInfoScreen(Screen):
    """Modal to show directory navigation and command options"""
    
    CSS = """
    NavigateInfoScreen {
        align: center middle;
        background: $surface-darken-2 80%;
    }
    
    #navigate-dialog {
        width: 80;
        height: 15;
        border: thick $primary 80%;
        background: $surface;
        layout: vertical;
        padding: 1;
    }
    
    #navigate-title {
        width: 100%;
        height: 2;
        content-align: center middle;
        text-style: bold;
        color: $primary;
    }
    
    #navigate-path {
        width: 100%;
        height: 2;
        content-align: center middle;
        text-align: center;
        text-style: italic;
        color: $text;
        margin-bottom: 1;
    }
    
    #commands-list {
        height: 6;
        border: solid $accent;
        background: $surface-lighten-1;
    }
    
    #button-container {
        layout: horizontal;
        width: 100%;
        height: 3;
        align: center middle;
        margin-top: 1;
    }
    
    Button {
        margin: 0 1;
        width: 12;
    }
    """
    
    BINDINGS = [
        Binding("escape", "close", "Close"),
        Binding("enter", "copy_selected", "Copy Selected"),
        Binding("up", "cursor_up", "Up", show=False),
        Binding("down", "cursor_down", "Down", show=False),
    ]
    
    def __init__(self, directory_path: str, filename: str):
        super().__init__()
        self.directory_path = directory_path
        self.filename = filename
        self.selected_index = 0
        self.commands = [
            {
                "label": "📋 Copy file path",
                "command": f'"{directory_path}/{filename}"'
            },
            {
                "label": "🚀 Copy file path and dstack apply",
                "command": f'cd "{directory_path}" && dstack apply -f {filename}'
            }
        ]
    
    def compose(self) -> ComposeResult:
        with Container(id="navigate-dialog"):
            yield Static("📁 File Actions", id="navigate-title")
            yield Static(f"{self.directory_path}/{self.filename}", id="navigate-path")
            yield ListView(
                *[ListItem(Label(cmd['label'])) for cmd in self.commands],
                id="commands-list"
            )
            with Container(id="button-container"):
                yield Button("Close (Esc)", variant="default", id="close-btn")
    
    def on_mount(self) -> None:
        """Set initial selection"""
        commands_list = self.query_one("#commands-list", ListView)
        commands_list.index = 0
    
    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.action_close()
    
    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle list item selection - copy and close"""
        self.action_copy_selected()
    
    def action_cursor_up(self) -> None:
        """Move selection up"""
        commands_list = self.query_one("#commands-list", ListView)
        if commands_list.index > 0:
            commands_list.index -= 1
    
    def action_cursor_down(self) -> None:
        """Move selection down"""
        commands_list = self.query_one("#commands-list", ListView)
        if commands_list.index < len(self.commands) - 1:
            commands_list.index += 1
    
    def action_copy_selected(self) -> None:
        """Copy the selected command to clipboard and close modal"""
        try:
            commands_list = self.query_one("#commands-list", ListView)
            selected_command = self.commands[commands_list.index]
            
            import subprocess
            # Copy to clipboard on macOS
            subprocess.run(['pbcopy'], input=selected_command['command'].encode(), check=True)
            self.notify(f"📋 Copied: {selected_command['label']}", timeout=2)
            
            # Close modal after copying
            self.app.pop_screen()
        except Exception:
            self.notify("❌ Could not copy to clipboard", severity="error")
    
    def action_close(self) -> None:
        """Close the modal"""
        self.app.pop_screen()


class DStackYAMLManager(App):
    """dstack YAML Management TUI"""
    
    CSS = """
    Screen {
        layout: grid;
        grid-size: 2 3;
        grid-columns: 1fr 2fr;
        grid-rows: auto 1fr auto;
        height: 100vh;
    }
    
    Header {
        column-span: 2;
        height: auto;
    }
    
    #file-tree {
        border: solid $primary;
        margin: 1;
        height: 1fr;
    }
    
    Tree > TreeNode {
        margin: 1 0;
        padding: 0 1;
    }
    
    #preview-pane {
        border: solid $primary;
        margin: 1;
        height: 1fr;
    }
    
    TabbedContent {
        height: 1fr;
    }
    
    TabPane {
        height: 1fr;
    }
    
    #preview-container, #note-container, #metadata-container {
        height: 1fr;
        width: 1fr;
    }
    
    #preview-content, #metadata-content {
        padding: 1;
        height: auto;
        width: 1fr;
    }
    
    #note-content {
        padding: 1;
        height: 1fr;
        width: 1fr;
        border: solid $accent;
        background: $surface-lighten-1;
    }
    
    Footer {
        column-span: 2;
        height: auto;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+x", "smart_quit", "Quit"),
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("ctrl+n", "add_file", "Add File"),
        Binding("ctrl+g", "new_group", "New Group"),
        Binding("delete", "delete_selected", "Delete"),
        Binding("ctrl+d", "delete_selected", "Delete"),
        Binding("ctrl+a", "navigate_to_file", "Navigate to File"),
        Binding("ctrl+s", "save_note", "Save Note"),
    ]
    
    def __init__(self, root_path: str = None, config_manager=None, restore_state_file: str = None):
        super().__init__()
        self.config_manager = config_manager
        self.yaml_manager = YAMLManager(
            Path(root_path) if root_path else None,
            config_manager=config_manager
        )
        self._terminal_script_path = None
        self._restore_state_file = restore_state_file
    
    def compose(self) -> ComposeResult:
        """Create child widgets for the app"""
        yield Header()
        yield FileTreeWidget(self.yaml_manager, id="file-tree")
        yield YAMLPreviewWidget(id="preview-pane")
        yield Footer()
    
    def on_mount(self) -> None:
        """Called when app starts"""
        print("🚀 APP MOUNTED")
        self.title = "dstack YAML Manager"
        self.sub_title = f"Managing YAML files in {self.yaml_manager.root_path} • Use ↑↓←→ keys or Page Up/Down to scroll preview"
        print(f"📁 Root path: {self.yaml_manager.root_path}")
        
        # Initialize note tracking
        self.current_note_file_path = None
        
        # Let's see if the tree is built properly
        try:
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            print(f"🌳 File tree found: {file_tree}")
            print(f"   Tree children count: {len(file_tree.root.children)}")
            
            # Force rebuild tree to see if it shows the logs
            print("🔄 Forcing tree rebuild...")
            file_tree.build_tree()
            print(f"   Tree children count after rebuild: {len(file_tree.root.children)}")
            
            # Show what's actually in the tree
            print("🔍 Tree contents:")
            for i, child in enumerate(file_tree.root.children):
                print(f"   Child {i}: {child.label if hasattr(child, 'label') else 'NO_LABEL'}")
                print(f"     Has data: {hasattr(child, 'data') and child.data is not None}")
                if hasattr(child, 'children'):
                    print(f"     Subchildren: {len(child.children)}")
                    for j, subchild in enumerate(child.children):
                        print(f"       Subchild {j}: {subchild.label if hasattr(subchild, 'label') else 'NO_LABEL'}")
                        print(f"         Has data: {hasattr(subchild, 'data') and subchild.data is not None}")
                        
        except Exception as e:
            print(f"❌ Could not find file tree: {e}")
            import traceback
            print(f"   Full error: {traceback.format_exc()}")
        
        # Check for restore state file passed via CLI or auto-restore hint file
        if self._restore_state_file:
            print(f"🔄 CLI restore mode: {self._restore_state_file}")
            if os.path.exists(self._restore_state_file):
                print("✅ State file exists, restoring...")
                self.call_later(lambda: self.restore_app_state(self._restore_state_file))
            else:
                print("❌ CLI state file no longer exists")
        else:
            # Check for auto-restore hint file
            restore_hint_file = os.path.join(self.yaml_manager.root_path, ".dstack_restore_state")
            if os.path.exists(restore_hint_file):
                print("🔄 Found restore hint file, attempting auto-restore...")
                try:
                    with open(restore_hint_file, 'r') as f:
                        state_file_path = f.read().strip()
                    
                    print(f"📄 State file path: {state_file_path}")
                    
                    if os.path.exists(state_file_path):
                        print("✅ State file exists, restoring...")
                        # Schedule restoration after the UI is fully loaded
                        self.call_later(lambda: self.restore_app_state(state_file_path))
                        
                        # Clean up hint file
                        os.remove(restore_hint_file)
                        print("🗑️ Removed restore hint file")
                    else:
                        print("❌ State file no longer exists")
                        os.remove(restore_hint_file)
                        
                except Exception as e:
                    print(f"❌ Error during auto-restore: {e}")
                    # Clean up hint file on error
                    try:
                        os.remove(restore_hint_file)
                    except:
                        pass
    
    def on_key(self, event) -> None:
        """Handle key events globally"""
        # Debug logging to file
        debug_log = "/Users/deep-diver/dstack-mgmt-tool/terminal_debug.log"
        
        def log_debug(msg):
            with open(debug_log, "a") as f:
                f.write(f"{datetime.now()}: {msg}\n")
                f.flush()
        
        log_debug(f"KEY PRESSED: {event.key}")
        
        # Handle escape key in note editing mode
        if event.key == "escape":
            try:
                # Check if note TextArea currently has focus
                note_widget = self.query_one("#note-content", TextArea)
                if note_widget.has_focus:
                    # Remove focus from TextArea to exit editing mode
                    self.set_focus(None)
                    self.notify("📝 Exited note editing mode", timeout=1)
                    return
            except Exception:
                pass
        
        # Use notify instead of print for TUI apps
        if "ctrl" in event.key.lower():
            self.notify(f"🔑 CTRL Key: {event.key}", timeout=2)
            log_debug(f"CTRL key detected: {event.key}")
        
    def on_text_area_changed(self, event) -> None:
        """Auto-save note content when TextArea changes"""
        try:
            # Only auto-save if it's the note content and we have a file selected
            if (hasattr(event.text_area, 'id') and 
                event.text_area.id == "note-content" and 
                self.current_note_file_path):
                
                # Debounce auto-save - only save after a brief delay
                self.set_timer(1.0, self._auto_save_note)
        except Exception:
            pass  # Silently handle any auto-save errors
    def _auto_save_note(self) -> None:
        """Internal method for auto-saving notes"""
        try:
            if self.current_note_file_path:
                note_widget = self.query_one("#note-content", TextArea)
                note_content = note_widget.text
                self.yaml_manager.db.save_file_note(str(self.current_note_file_path), note_content)
        except Exception:
            pass  # Silently handle auto-save errors
    
    def on_file_selected(self, event: FileSelected) -> None:
        """Handle file selection from tree"""
        # Use notifications in TUI apps instead of print
        self.notify(f"Selected: {event.yaml_file.name}", severity="information")
        
        # Make sure the tree widget stores the current file
        file_tree = self.query_one("#file-tree", FileTreeWidget)
        file_tree.current_file = event.yaml_file
        self.notify(f"Stored in tree: {event.yaml_file.name}", timeout=1)
        
        preview_widget = self.query_one("#preview-pane", YAMLPreviewWidget)
        preview_widget.update_preview(event.yaml_file)
    
    def action_refresh(self) -> None:
        """Refresh the file list"""
        self.yaml_manager.scan_files()
        file_tree = self.query_one("#file-tree", FileTreeWidget)
        file_tree.build_tree()
    
    
    def action_export_all(self) -> None:
        """Export all files to filesystem"""
        try:
            export_dir = Path.cwd() / "exported_dstack_configs"
            export_dir.mkdir(exist_ok=True)
            
            exported_paths = self.yaml_manager.db.export_all_files_to_filesystem(export_dir)
            
            self.notify(f"Exported {len(exported_paths)} files to {export_dir}", 
                       severity="information", markup=False)
        except Exception as e:
            self.notify("Export failed", severity="error", markup=False)
    
    def action_new_group(self) -> None:
        """Create a new group/category"""
        new_group_screen = NewGroupScreen()
        self.push_screen(new_group_screen)
    
    def action_add_file(self) -> None:
        """Add an existing file"""
        add_file_screen = AddFileScreen()
        self.push_screen(add_file_screen)
    
    def action_clear_all_data(self) -> None:
        """Clear all data from the database"""
        try:
            self.notify("🗑️ Clearing all data...", timeout=2)
            
            # Clear database
            if self.yaml_manager.db.clear_all_data():
                # Clear in-memory data
                self.yaml_manager.yaml_files = []
                
                # Refresh the UI
                self.action_refresh()
                
                self.notify("✅ All data cleared successfully!", timeout=3)
            else:
                self.notify("❌ Failed to clear data", severity="error")
                
        except Exception as e:
            self.notify(f"❌ Error clearing data: {str(e)}", severity="error")
    
    def action_delete_selected(self) -> None:
        """Delete the currently selected item (file or group)"""
        try:
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            if not file_tree.cursor_node or not file_tree.cursor_node.data:
                self.notify("❌ No item selected", severity="warning")
                return
            
            selected_data = file_tree.cursor_node.data
            
            # Handle different types of selected items
            if hasattr(selected_data, 'name'):
                # This is a file
                item_name = selected_data.name
                item_type = "file"
                
                def delete_file_callback():
                    import datetime
                    
                    debug_log = "/Users/deep-diver/dstack-mgmt-tool/delete_debug.log"
                    
                    def log_debug(message):
                        with open(debug_log, "a") as f:
                            f.write(f"{datetime.datetime.now()}: {message}\n")
                    
                    # Get file ID from database
                    file_path_str = str(selected_data.path)
                    log_debug(f"🎯 CALLBACK: Starting delete for file: {file_path_str}")
                    log_debug(f"🎯 CALLBACK: Selected data type: {type(selected_data)}")
                    log_debug(f"🎯 CALLBACK: Selected data attributes: {dir(selected_data)}")
                    
                    self.notify(f"🔍 Looking for file: {file_path_str}", timeout=2)
                    
                    file_data = self.yaml_manager.db.get_file_by_path(file_path_str)
                    if file_data:
                        log_debug(f"🎯 CALLBACK: Found file data: {file_data}")
                        self.notify(f"🔍 Found file ID: {file_data['id']}", timeout=2)
                        delete_result = self.yaml_manager.db.delete_file(file_data['id'])
                        log_debug(f"🎯 CALLBACK: Delete result: {delete_result}")
                        if delete_result:
                            self.notify(f"✅ Deleted file: {item_name}", timeout=3)
                            self.action_refresh()
                        else:
                            self.notify(f"❌ Failed to delete file: {item_name}", severity="error")
                    else:
                        log_debug(f"🎯 CALLBACK: File not found in database")
                        self.notify(f"❌ File not found in database: {file_path_str}", severity="error")
                
                # Show confirmation dialog
                confirm_screen = ConfirmDeleteScreen(item_name, item_type, delete_file_callback)
                self.push_screen(confirm_screen)
                
            elif isinstance(selected_data, dict) and selected_data.get('type') == 'custom_group':
                # This is a custom group
                group_data = selected_data['group_data']
                item_name = group_data['name']
                item_type = "group"
                
                def delete_group_callback():
                    if self.yaml_manager.db.delete_custom_group(group_data['id']):
                        self.notify(f"✅ Deleted group: {item_name}", timeout=3)
                        self.action_refresh()
                    else:
                        self.notify(f"❌ Failed to delete group: {item_name}", severity="error")
                
                # Show confirmation dialog
                confirm_screen = ConfirmDeleteScreen(item_name, item_type, delete_group_callback)
                self.push_screen(confirm_screen)
                
            else:
                self.notify("❌ Cannot delete this item type", severity="warning")
                
        except Exception as e:
            self.notify(f"❌ Error during delete: {str(e)}", severity="error")
    
    def action_navigate_to_file(self) -> None:
        """Navigate to selected file's directory and quit"""
        try:
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            if not file_tree.cursor_node or not file_tree.cursor_node.data:
                self.notify("❌ No file selected", severity="warning")
                return
            
            selected_data = file_tree.cursor_node.data
            
            # Only works for files, not groups
            if hasattr(selected_data, 'path'):
                file_path = Path(selected_data.path)
                target_directory = file_path.parent
                filename = file_path.name
                
                # Show modal with navigation and command options
                navigate_screen = NavigateInfoScreen(str(target_directory), filename)
                self.push_screen(navigate_screen)
            else:
                self.notify("❌ Please select a file (not a group)", severity="warning")
                
        except Exception as e:
            self.notify(f"❌ Error navigating to file: {str(e)}", severity="error")
    
    def action_save_note(self) -> None:
        """Save the current note content to database"""
        try:
            if not self.current_note_file_path:
                self.notify("❌ No file selected for note saving", severity="warning")
                return
            
            # Get the note content from the TextArea
            note_widget = self.query_one("#note-content", TextArea)
            note_content = note_widget.text
            
            # Save to database
            self.yaml_manager.db.save_file_note(str(self.current_note_file_path), note_content)
            self.notify("💾 Note saved!", timeout=2)
            
        except Exception as e:
            self.notify(f"❌ Error saving note: {str(e)}", severity="error")
    
    def save_app_state(self) -> str:
        """Save current app state to a temporary file"""
        import json
        import tempfile
        
        # Use notification for TUI debugging
        self.notify("Saving state...", timeout=2)
        
        try:
            # Get currently selected file and its details
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            
            selected_file_data = None
            
            if file_tree.current_file:
                # Ensure we save the absolute path
                file_path = file_tree.current_file.path
                if not file_path.is_absolute():
                    file_path = self.yaml_manager.root_path / file_path
                
                selected_file_data = {
                    "path": str(file_path),
                    "name": file_tree.current_file.name,
                    "config_type": file_tree.current_file.config_type.value,
                    "is_global_config": str(file_path).endswith("/.dstack/config.yml")
                }
                self.notify(f"State: {file_tree.current_file.name} at {file_path}", timeout=3)
            else:
                self.notify("No file selected to save!", severity="warning", timeout=3)
            
            # Get active tab in preview pane
            preview_widget = self.query_one("#preview-pane", YAMLPreviewWidget)
            active_tab = "preview"  # Default
            try:
                tabbed_content = preview_widget.query_one("TabbedContent")
                if tabbed_content.active_tab:
                    active_tab = tabbed_content.active_tab.id
            except:
                pass
            
            # Get expanded tree nodes for restoration
            expanded_nodes = []
            try:
                def collect_expanded_nodes(node, path=""):
                    if hasattr(node, 'expanded') and node.expanded:
                        node_id = node.label.plain if hasattr(node, 'label') else str(node)
                        expanded_nodes.append(f"{path}/{node_id}" if path else node_id)
                        for child in node.children:
                            collect_expanded_nodes(child, f"{path}/{node_id}" if path else node_id)
                
                collect_expanded_nodes(file_tree.root)
            except:
                pass
            
            state = {
                "selected_file": selected_file_data,
                "active_tab": active_tab,
                "expanded_nodes": expanded_nodes,
                "root_path": str(self.yaml_manager.root_path),
                "timestamp": str(datetime.now())
            }
            
            print(f"   Final state to save: {state}")
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(state, f, indent=2)
                temp_file = f.name
                
            print(f"   State saved to: {temp_file}")
            return temp_file
                
        except Exception as e:
            print(f"❌ Failed to save state: {e}")
            import traceback
            print(f"   Full error: {traceback.format_exc()}")
            return None
    
    def action_smart_quit(self) -> None:
        """Smart quit: save state, change to relevant directory, and exit"""
        import subprocess
        import os
        import sys
        import tempfile
        
        # Comprehensive logging
        debug_log = "/Users/deep-diver/dstack-mgmt-tool/terminal_debug.log"
        
        def log_debug(msg):
            with open(debug_log, "a") as f:
                f.write(f"{datetime.now()}: {msg}\n")
                f.flush()
        
        log_debug("=== ACTION_SMART_QUIT CALLED ===")
        
        # Show notification first to confirm it's called
        self.notify("👋 Smart quit triggered!", severity="information", timeout=3)
        self.notify("💾 Saving state and changing directory...", timeout=3)
        log_debug("Notifications sent")
        
        # Simple and elegant approach: save state, change directory, and exit
        try:
            log_debug("Starting simple directory change approach...")
            
            # Save current app state first
            log_debug("Starting state save...")
            self.notify("💾 Saving app state...", timeout=2)
            state_file = self.save_app_state()
            log_debug(f"State saved to: {state_file}")
            
            # Determine target directory based on selected file
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            target_dir = self.yaml_manager.root_path  # Default to project root
            
            if file_tree.current_file:
                # Special handling for global dstack config
                if (str(file_tree.current_file.path).endswith("/.dstack/config.yml") or 
                    (file_tree.current_file.name == "config.yml" and "/.dstack/" in str(file_tree.current_file.path))):
                    target_dir = str(Path.home() / ".dstack")
                    log_debug(f"Selected global config, changing to: {target_dir}")
                    self.notify(f"📁 Changing to global config directory", timeout=2)
                else:
                    # For virtual database files, use project root but show selected file info
                    log_debug(f"Selected virtual file: {file_tree.current_file.name}, staying in project root")
                    self.notify(f"📁 Changing to project directory", timeout=2)
            else:
                log_debug("No file selected, using project root")
                self.notify(f"📁 Changing to project directory", timeout=2)
            
            log_debug(f"Target directory: {target_dir}")
            
            # Create a restoration hint file for next startup
            restore_hint_file = os.path.join(self.yaml_manager.root_path, ".dstack_restore_state")
            try:
                with open(restore_hint_file, 'w') as f:
                    f.write(state_file)
                log_debug(f"Created restore hint file: {restore_hint_file}")
            except Exception as e:
                log_debug(f"Failed to create restore hint: {e}")
            
            # Change to target directory
            try:
                os.chdir(target_dir)
                log_debug(f"Changed directory to: {target_dir}")
                self.notify(f"🎯 Directory changed to: {target_dir}", timeout=3)
            except Exception as e:
                log_debug(f"Failed to change directory: {e}")
                self.notify(f"❌ Failed to change directory: {e}", severity="error")
            
            # Show final message and exit  
            self.notify("✅ State saved! Restart the app to restore your session.", timeout=4)
            log_debug("App smart quit complete")
            
            # Exit the app cleanly
            self.exit()
            
        except Exception as e:
            # Log the error and show notification
            log_debug(f"EXCEPTION in action_open_terminal: {e}")
            import traceback
            log_debug(f"Exception traceback: {traceback.format_exc()}")
            self.notify(f"Terminal error: {str(e)}", severity="error", markup=False)
    
    def restore_app_state(self, state_file_path: str):
        """Restore app state from saved file"""
        import json
        import os
        
        # Log to a separate file that won't be captured by TUI
        def log_restore(msg):
            with open("restore.log", "a") as f:
                f.write(f"{msg}\n")
                f.flush()
        
        log_restore(f"🚀 restore_app_state called with: {state_file_path}")
        
        try:
            log_restore(f"📁 Checking if state file exists: {state_file_path}")
            if not os.path.exists(state_file_path):
                log_restore("❌ No state file found - starting fresh")
                return
            
            log_restore("📖 Reading state file...")
            with open(state_file_path, 'r') as f:
                state = json.load(f)
            
            log_restore(f"✅ Loaded state: {state}")
            log_restore(f"🔄 Restoring app state from {state.get('timestamp', 'unknown time')}")
            
            # Refresh the file tree first to ensure all files are loaded
            log_restore("🔄 Refreshing file tree...")
            self.action_refresh()
            
            # Restore selected file after tree expansion completes
            if state.get("selected_file"):
                log_restore(f"⏰ Scheduling file selection in 0.3s for: {state['selected_file']}")
                self.set_timer(0.3, lambda: self._debug_and_restore_file_selection(state["selected_file"]))
            else:
                log_restore("⚠️ No selected_file in state")
            
            # Restore active tab after file selection
            if state.get("active_tab"):
                log_restore(f"⏰ Scheduling tab restoration in 0.5s for: {state['active_tab']}")
                self.set_timer(0.5, lambda: self._restore_active_tab(state["active_tab"]))
            else:
                log_restore("⚠️ No active_tab in state")
            
            # Clean up state file
            try:
                log_restore(f"🗑️ Cleaning up state file: {state_file_path}")
                os.unlink(state_file_path)
                log_restore("✅ State file cleaned up")
            except Exception as cleanup_error:
                log_restore(f"⚠️ Failed to cleanup state file: {cleanup_error}")
            
        except Exception as e:
            log_restore(f"❌ Failed to restore state: {e}")
            import traceback
            log_restore(f"Full traceback: {traceback.format_exc()}")
            # If restore fails, just continue normally
            pass
    
    def _debug_and_restore_file_selection(self, file_data: dict):
        """Debug version that shows tree structure and attempts restoration"""
        def log_restore(msg):
            with open("restore.log", "a") as f:
                f.write(f"{msg}\n")
                f.flush()
        
        try:
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            target_path = file_data.get("path")
            target_name = file_data.get("name")
            
            log_restore(f"🔍 DEBUG: Tree has {len(file_tree.root.children)} top-level nodes")
            log_restore(f"🎯 Looking for file: {target_name} at {target_path}")
            
            # First, let's see what's in the tree
            def debug_tree_structure(node, depth=0):
                indent = "  " * depth
                log_restore(f"{indent}📋 Node: {node.label if hasattr(node, 'label') else 'NO_LABEL'}")
                if hasattr(node, 'data') and node.data:
                    if hasattr(node.data, 'path'):
                        log_restore(f"{indent}   Path: {node.data.path}")
                    if hasattr(node.data, 'name'):
                        log_restore(f"{indent}   Name: {node.data.name}")
                log_restore(f"{indent}   Children: {len(node.children)}")
                
                if depth < 2:  # Limit depth to avoid too much logging
                    for child in node.children:
                        debug_tree_structure(child, depth + 1)
            
            log_restore("🌳 Tree structure:")
            debug_tree_structure(file_tree.root)
            
            # Now try to find and select the file
            log_restore("🔍 Starting file selection process...")
            self._restore_file_selection(file_data)
            
        except Exception as e:
            log_restore(f"❌ Debug error: {e}")
            import traceback
            log_restore(f"Full traceback: {traceback.format_exc()}")
    
    def _restore_file_selection(self, file_data: dict):
        """Helper to restore file selection using detailed file data"""
        def log_restore(msg):
            with open("restore.log", "a") as f:
                f.write(f"{msg}\n")
                f.flush()
        
        try:
            file_tree = self.query_one("#file-tree", FileTreeWidget)
            target_path = file_data.get("path")
            target_name = file_data.get("name")
            
            log_restore(f"🎯 Looking for file: {target_name} at {target_path}")
            
            # Find the file in the tree and expand path to it
            def find_and_expand_to_file(node, path_to_node=[], depth=0):
                indent = "  " * depth
                current_path = path_to_node + [node]
                
                if hasattr(node, 'data') and node.data:
                    # Check for path match (handle both absolute and relative paths)
                    if hasattr(node.data, 'path'):
                        node_path = str(node.data.path)
                        # Try exact match first
                        if node_path == target_path:
                            log_restore(f"{indent}✅ Found exact path match: {node_path}")
                            return self._select_found_file(node, current_path, target_path, log_restore)
                        # Try matching by filename (since tree has relative paths, target has absolute)
                        elif target_path.endswith(node_path) or node_path == target_name:
                            log_restore(f"{indent}✅ Found filename match: {node_path} for target {target_path}")
                            return self._select_found_file(node, current_path, node_path, log_restore)
                        
                        # Also check by name as fallback
                        if hasattr(node.data, 'name'):
                            node_name = str(node.data.name)
                            if node_name == target_name:
                                log_restore(f"{indent}✅ Found target by name: {node_name}")
                                return self._select_found_file(node, current_path, node_name, log_restore)
                
                # First expand this node if it's a group/folder
                if hasattr(node, 'expand') and hasattr(node, 'children') and len(node.children) > 0:
                    node.expand()
                
                # Recursively search children
                for child in node.children:
                    if find_and_expand_to_file(child, current_path, depth + 1):
                        return True
                return False
            
            if find_and_expand_to_file(file_tree.root):
                log_restore(f"✅ Successfully restored and expanded to: {target_name}")
            else:
                log_restore(f"❌ Could not find file: {target_name}")
                # As fallback, expand all nodes to make sure file is visible
                log_restore("🔄 Expanding all nodes as fallback...")
                self._expand_all_tree_nodes(file_tree.root)
                
        except Exception as e:
            log_restore(f"❌ Error restoring file selection: {e}")
            import traceback
            log_restore(f"Full traceback: {traceback.format_exc()}")

    def _select_found_file(self, node, current_path, node_path, log_restore):
        """Helper to select a found file node"""
        # Expand all nodes in the path to this file
        for path_node in current_path[:-1]:  # Don't expand the file itself
            if hasattr(path_node, 'expand'):
                path_node.expand()
                log_restore(f"📂 Expanded: {path_node.label}")
        
        # Wait a moment for expansion to complete, then select
        def delayed_selection():
            log_restore(f"🎯 Selecting file after expansion: {node_path}")
            
            try:
                file_tree = self.query_one("#file-tree", FileTreeWidget)
                
                # Method 1: Update internal file tracking
                file_tree.current_file = node.data
                log_restore(f"✅ Set current_file to: {node.data.name}")
                
                # Method 2: Try to set tree cursor (for visual highlighting)
                try:
                    # Use the proper Textual Tree API to select the node
                    if hasattr(file_tree, 'select_node'):
                        file_tree.select_node(node)
                        log_restore(f"✅ Selected node using select_node")
                    elif hasattr(node, 'action_select'):
                        node.action_select()
                        log_restore(f"✅ Selected node using action_select")
                    
                    # Try to scroll to the node and make it visible
                    if hasattr(file_tree, 'scroll_to_node'):
                        file_tree.scroll_to_node(node)
                        log_restore(f"✅ Scrolled to node")
                    
                    # Refresh the tree widget to update visual state
                    file_tree.refresh()
                    log_restore(f"✅ Refreshed tree widget")
                    
                except Exception as e:
                    log_restore(f"⚠️ Tree cursor/scroll failed: {e}")
                
                # Method 3: Post the FileSelected message
                file_tree.post_message(FileSelected(node.data))
                log_restore(f"✅ Posted FileSelected message")
                
                # Method 4: Direct preview update as backup
                try:
                    preview_widget = self.query_one("#preview-pane", YAMLPreviewWidget)
                    preview_widget.update_preview(node.data)
                    log_restore(f"✅ Updated preview for: {node.data.name}")
                except Exception as e:
                    log_restore(f"⚠️ Preview update failed: {e}")
                
                # Method 5: Focus the tree widget
                try:
                    file_tree.focus()
                    log_restore(f"✅ Focused tree widget")
                except Exception as e:
                    log_restore(f"⚠️ Tree focus failed: {e}")
                    
            except Exception as e:
                log_restore(f"❌ Delayed selection failed: {e}")
        
        # Schedule selection after expansion delay
        self.set_timer(0.2, delayed_selection)
        return True
    
    def _expand_all_tree_nodes(self, node):
        """Helper to expand all tree nodes"""
        try:
            if hasattr(node, 'expand'):
                node.expand()
            for child in node.children:
                self._expand_all_tree_nodes(child)
        except:
            pass
    
    def _restore_active_tab(self, tab_id: str):
        """Helper to restore active tab"""
        try:
            print(f"🔄 Restoring active tab: {tab_id}")
            preview_widget = self.query_one("#preview-pane", YAMLPreviewWidget)
            tabbed_content = preview_widget.query_one("TabbedContent")
            tabbed_content.active = tab_id
            print(f"✅ Successfully restored tab: {tab_id}")
        except Exception as e:
            print(f"❌ Error restoring tab: {e}")
            pass
    


# This module is now imported as part of the dstack-mgmt package
# The main entry point is in cli.py