import asyncio
import os
import sys
from pathlib import Path
from typing import Tuple, Dict, Any, List, Optional

# These modules would need to be created as separate Python files
import os
import sys
from pathlib import Path

# Get the directory containing this script
current_dir = Path(__file__).parent

# Import local modules directly
sys.path.insert(0, str(current_dir))
from config import load_config, setup_config
from utils.logger import logger
from utils.mod_validator import ModValidator
from utils.file_operations import FileOperations
from utils.mod_report import ModReport


class ModProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.GAME_VERSION = "1.11.0"  # Current CK3 version
        self.config = config
        self.output_path = Path(os.getcwd()) / config["output_path"]
        self.mod_report = ModReport(self.output_path)

    def initialize(self) -> None:
        logger.init()
        # Create output directory for processed mods
        os.makedirs(self.output_path, exist_ok=True)
        # Create directory for local mods if it doesn't exist
        os.makedirs(self.config["local_mods_path"], exist_ok=True)
        logger.info('ModProcessor initialized successfully')
        logger.info(f"Using output directory: {self.output_path}")
        logger.info(f"Using local mods directory: {self.config['local_mods_path']}")

    def process_single_mod_file(self, mod_file_path: str, source_path: str, is_local: bool) -> bool:
        try:
            mod_folder_path = Path(source_path) / mod_file_path
            metadata = ModValidator.validate_mod(mod_file_path, str(mod_folder_path))

            if not metadata:
                logger.warn(f"Failed to validate mod: {mod_file_path}")
                return False

            # Check for missing version information
            mod_issue = {
                "mod_name": metadata["name"],
                "missing_version": "mod_version" not in metadata,
                "missing_game_version": "game_version" not in metadata,
                "missing_dependencies": []
            }

            # Validate game version compatibility
            is_game_version_compatible = ModValidator.check_game_version(metadata, self.GAME_VERSION)
            if not is_game_version_compatible:
                logger.warn(f"Mod {metadata['name']} may not be compatible with game version {self.GAME_VERSION}")

            # Check dependencies
            if metadata.get("dependencies"):
                for dep in metadata["dependencies"]:
                    if not ModValidator.validate_dependencies(metadata, dep):
                        mod_issue["missing_dependencies"].append(dep)

            # Add to report if there are any issues
            if mod_issue["missing_version"] or mod_issue["missing_game_version"] or mod_issue["missing_dependencies"]:
                self.mod_report.add_issue(mod_issue)

            version_string = ModValidator.get_version_string(metadata)
            dest_name = f"{metadata['name']} {version_string}{' [LOCAL]' if is_local else ''}"
            safe_name = "".join(c if c not in "\\/:*?\"<>|" else "_" for c in dest_name)
            dest_path = self.output_path / safe_name

            logger.info(f"Processing {'local' if is_local else 'workshop'} mod: {metadata['name']} ({version_string})")

            # Check if mod already exists
            if dest_path.exists():
                logger.info(f"Mod already exists: {safe_name}")
                return True

            # Create backup of existing files if they exist
            try:
                existing_files = [f for f in os.listdir(self.output_path) if f.startswith(safe_name)]
                for file in existing_files:
                    FileOperations.create_backup(self.output_path / file)
            except FileNotFoundError:
                pass

            # Copy mod files with verification
            success = FileOperations.copy_dir_concurrent(
                str(mod_folder_path),
                str(dest_path),
                True  # enable hash verification
            )

            if success:
                logger.info(f"Successfully processed mod: {safe_name}")
                return True
            else:
                logger.error(f"Failed to process mod: {safe_name}")
                return False
        except Exception as error:
            logger.error(f"Error processing mod: {mod_file_path}", error)
            return False

    def process_mods_in_directory(self, directory: str, is_local: bool) -> Tuple[int, int]:
        files = os.listdir(directory)
        mod_files = [file for file in files if file.endswith('.mod')]
        
        processed = 0
        successful = 0

        for file in mod_files:
            if self.process_single_mod_file(file, directory, is_local):
                successful += 1
            processed += 1
            sys.stdout.write(f"\rProcessing {'local' if is_local else 'workshop'} mods: {processed}/{len(mod_files)}")
            sys.stdout.flush()

        print()  # New line after progress display
        return processed, successful

    def process_all_mods(self) -> None:
        try:
            logger.info('Starting mod processing...')

            # Process Workshop mods
            workshop_processed, workshop_successful = self.process_mods_in_directory(
                self.config["workshop_path"],
                False
            )
            logger.info(f"Processed {workshop_successful}/{workshop_processed} workshop mods")

            # Process local mods
            local_processed, local_successful = self.process_mods_in_directory(
                self.config["local_mods_path"],
                True
            )
            logger.info(f"Processed {local_successful}/{local_processed} local mods")

            # Generate the mod issues report
            self.mod_report.generate_report()

            # Cleanup old backups and logs
            FileOperations.cleanup(str(self.output_path), 30)  # Keep backups for 30 days
            logger.cleanup(7)  # Keep logs for 7 days

            logger.info('Completed processing all mods')
        except Exception as error:
            logger.error('Error processing mods', error)
            sys.exit(1)


def main():
    try:
        config = load_config()
        
        if not config.get("workshop_path"):
            config = setup_config()

        processor = ModProcessor(config)
        processor.initialize()
        processor.process_all_mods()
    except Exception as error:
        print(f"Fatal error: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
