import os
import aiofiles
from datetime import datetime
from typing import Dict, List, Optional, Any

# Assuming logger is imported from another module
from utils.logger import logger


class ModReport:
    def __init__(self, output_dir: str):
        self.issues: List[Dict[str, Any]] = []
        self.report_path = os.path.join(output_dir, 'mod-issues.log')

    def add_issue(self, issue: Dict[str, Any]) -> None:
        """Add a mod issue to the report.
        
        Issue format:
        {
            "mod_name": str,
            "missing_dependencies": Optional[List[str]],
            "missing_version": Optional[bool],
            "missing_game_version": Optional[bool]
        }
        """
        self.issues.append(issue)

    async def generate_report(self) -> None:
        """Generate a report of all mod issues."""
        if len(self.issues) == 0:
            async with aiofiles.open(self.report_path, 'w') as file:
                await file.write('No issues found with mods.\n')
            return

        report_lines = ['Mod Issues Report', '==================', '']
        timestamp = datetime.now().isoformat()
        report_lines.append(f'Generated: {timestamp}\n')

        # Group issues by type
        missing_versions = [i for i in self.issues if i.get('missing_version')]
        missing_game_versions = [i for i in self.issues if i.get('missing_game_version')]
        missing_deps = [i for i in self.issues if i.get('missing_dependencies') and len(i.get('missing_dependencies', []))]

        if missing_versions:
            report_lines.append('Mods Missing Version Information:')
            report_lines.append('--------------------------------')
            for issue in missing_versions:
                report_lines.append(f"- {issue['mod_name']}")
            report_lines.append('')

        if missing_game_versions:
            report_lines.append('Mods Missing Game Version Information:')
            report_lines.append('-------------------------------------')
            for issue in missing_game_versions:
                report_lines.append(f"- {issue['mod_name']}")
            report_lines.append('')

        if missing_deps:
            report_lines.append('Mods With Missing Dependencies:')
            report_lines.append('-----------------------------')
            for issue in missing_deps:
                report_lines.append(f"\n{issue['mod_name']}:")
                for dep in issue.get('missing_dependencies', []):
                    report_lines.append(f"  - Missing: {dep}")
            report_lines.append('')

        # Write the report to file
        async with aiofiles.open(self.report_path, 'w') as file:
            await file.write('\n'.join(report_lines))
        
        await logger.info(f"Generated mod issues report at {self.report_path}")