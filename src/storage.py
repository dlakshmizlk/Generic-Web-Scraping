"""
Storage module for persisting discovered URLs in JSON format.
"""
import json
import logging
from pathlib import Path
from typing import Set, List
from datetime import datetime


class URLStorage:
    """Manages persistent storage of discovered URLs."""
    
    def __init__(self, storage_file: Path, logger: logging.Logger):
        """
        Initialize URL storage.
        
        Args:
            storage_file: Path to JSON file for storing URLs
            logger: Logger instance
        """
        self.storage_file = storage_file
        self.logger = logger
        self.data = self._load()
    
    def _load(self) -> dict:
        """Load existing URLs from JSON file."""
        if not self.storage_file.exists():
            self.logger.info(f"Storage file not found. Creating new: {self.storage_file}")
            return {
                "urls": [],
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "total_urls": 0
                }
            }
        
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.logger.info(f"Loaded {len(data.get('urls', []))} existing URLs from storage")
                return data
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON file: {e}. Creating new storage.")
            return {
                "urls": [],
                "metadata": {
                    "created_at": datetime.now().isoformat(),
                    "last_updated": datetime.now().isoformat(),
                    "total_urls": 0
                }
            }
        except Exception as e:
            self.logger.error(f"Error loading storage file: {e}")
            raise
    
    def _save(self) -> None:
        """Save URLs to JSON file."""
        try:
            self.data["metadata"]["last_updated"] = datetime.now().isoformat()
            self.data["metadata"]["total_urls"] = len(self.data["urls"])
            
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved {len(self.data['urls'])} URLs to storage")
        except Exception as e:
            self.logger.error(f"Error saving storage file: {e}")
            raise
    
    def get_seen_urls(self) -> Set[str]:
        """
        Get set of all previously seen URLs.
        
        Returns:
            Set of URL strings
        """
        return set(self.data.get("urls", []))
    
    def add_urls(self, new_urls: List[str]) -> List[str]:
        """
        Add new URLs to storage and return only the newly added ones.
        
        Args:
            new_urls: List of URLs to add
            
        Returns:
            List of URLs that were actually new (not duplicates)
        """
        cleaned = []
        for u in new_urls:
            if not u:
                continue
            u = u.strip()
            if u.endswith('/'):
                u = u[:-1]
            cleaned.append(u)

        seen = self.get_seen_urls()
        truly_new = [url for url in new_urls if url not in seen]
        
        if truly_new:
            self.data["urls"].extend(truly_new)
            self._save()
            self.logger.info(f"Added {len(truly_new)} new URLs to storage")
        else:
            self.logger.info("No new URLs to add")
        
        return truly_new
    
    def get_stats(self) -> dict:
        """
        Get statistics about stored URLs.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_urls": len(self.data.get("urls", [])),
            "created_at": self.data.get("metadata", {}).get("created_at"),
            "last_updated": self.data.get("metadata", {}).get("last_updated")
        }