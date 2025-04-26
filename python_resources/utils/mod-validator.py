import os
import re
import asyncio
import aiofiles
from typing import Dict, List, Optional, TypedDict, Any

# Assuming logger is imported from another module
from utils.logger import logger


class ModMetadata(TypedDict, total=False):
    name: str
    mod_version: Optional[str]  
    game_version: Optional[str]  
    dependencies: Optional[List[str]]
    workshop_id: str
    tags: Optional[List[str]]


class ModValidator:
    version_pattern = re.compile(r'version\s*=\s*"?([^"\s}]+)"?')
    game_version_pattern = re.compile(r'supported_version\s*=\s*"?([^"\s}]+)"?')
    dependency_pattern = re.compile(r'dependencies\s*=\s*\{([^}]+)\}')
    tag_pattern = re.compile(r'tags\s*=\s*\{([^}]+)\}')

    @staticmethod
    def format_mod_version(version: str) -> str:
        """Format the mod version with 'mv' prefix"""
        if not version:
            return 'mvUnknown'
        return f"mv{re.sub(r'^v', '', version, flags=re.IGNORECASE)}"

    @staticmethod
    def format_game_version(version: str) -> str:
        """Format the game version with 'gv' prefix"""
        if not version:
            return 'gvUnknown'
        return f"gv{re.sub(r'^v', '', version, flags=re.IGNORECASE)}"

    @classmethod
    async def validate_mod(cls, mod_file_path: str, mod_folder_path: str) -> Optional[ModMetadata]:
        """Validate a mod file and extract its metadata"""
        try:
            async with aiofiles.open(mod_file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                
            metadata = await cls.extract_metadata(content)
            
            if not metadata:
                await logger.warn(f"Failed to extract metadata from {mod_file_path}")
                return None

            # Validate mod folder exists
            if not os.path.exists(mod_folder_path):
                await logger.error(f"Mod folder not found: {mod_folder_path}")
                return None

            # Validate descriptor.mod exists in mod folder
            descriptor_path = os.path.join(mod_folder_path, 'descriptor.mod')
            if not os.path.exists(descriptor_path):
                await logger.warn(f"descriptor.mod not found in {mod_folder_path}")

            return metadata
        except Exception as error:
            await logger.error(f"Error validating mod: {mod_file_path}", error)
            return None

    @classmethod
    async def extract_metadata(cls, content: str) -> Optional[ModMetadata]:
        """Extract metadata from mod file content"""
        name_match = re.search(r'name="([^"]+)"|name=(\S+)', content)
        workshop_id_match = re.search(r'remote_file_id="([^"]+)"|remote_file_id=(\S+)', content)

        if not name_match or not workshop_id_match:
            return None

        metadata: ModMetadata = {
            "name": name_match.group(1) or name_match.group(2),
            "workshop_id": workshop_id_match.group(1) or workshop_id_match.group(2)
        }

        # Extract and format mod version
        version_match = cls.version_pattern.search(content)
        if version_match:
            raw_version = version_match.group(1)
            metadata["mod_version"] = cls.format_mod_version(raw_version)

        # Extract and format game version
        game_version_match = cls.game_version_pattern.search(content)
        if game_version_match:
            raw_game_version = game_version_match.group(1)
            metadata["game_version"] = cls.format_game_version(raw_game_version)

        # Log version information
        if "mod_version" in metadata:
            await logger.info(f"Mod version detected: {metadata['mod_version']}")
        if "game_version" in metadata:
            await logger.info(f"Game version detected: {metadata['game_version']}")

        # Extract dependencies
        dependency_match = cls.dependency_pattern.search(content)
        if dependency_match:
            dependencies = [
                line.strip() for line in dependency_match.group(1).split('\n')
                if line.strip()
            ]
            if dependencies:
                metadata["dependencies"] = dependencies

        # Extract tags
        tag_match = cls.tag_pattern.search(content)
        if tag_match:
            tags = [
                line.strip() for line in tag_match.group(1).split('\n')
                if line.strip()
            ]
            if tags:
                metadata["tags"] = tags

        return metadata

    @staticmethod
    async def validate_dependencies(metadata: ModMetadata, mod_base_path: str) -> bool:
        """Check if all dependencies exist"""
        if not metadata.get("dependencies") or len(metadata.get("dependencies", [])) == 0:
            return True

        for dependency in metadata["dependencies"]:
            dependency_path = os.path.join(mod_base_path, dependency)
            if not os.path.exists(dependency_path):
                await logger.warn(f"Missing dependency for {metadata['name']}: {dependency}")
                return False

        return True

    @classmethod
    async def check_game_version(cls, metadata: ModMetadata, required_version: str) -> bool:
        """Check if the mod supports the required game version"""
        if "game_version" not in metadata:
            await logger.warn(f"No game version specified for mod: {metadata['name']}")
            return False

        required_formatted = cls.format_game_version(required_version)
        return metadata["game_version"] == required_formatted

    @staticmethod
    def get_version_string(metadata: ModMetadata) -> str:
        """Get a formatted version string for the mod"""
        game_ver = metadata.get("game_version", "gvUnknown")
        mod_ver = metadata.get("mod_version", "mvUnknown")
        return f"[{game_ver}][{mod_ver}]"