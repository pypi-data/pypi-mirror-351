import re
import subprocess
from typing import Tuple, Optional

class CommandProcessor:
    @staticmethod
    def extract_command(text: str) -> str:
        match = re.search(r"---command---\s*(.*?)\s*---end---", text, re.DOTALL)
        if match:
            command = match.group(1).strip()
        else:
            command = text.strip()
        
        command = re.sub(r'```.*?\n', '', command)
        command = re.sub(r'```', '', command)
        return command.strip()

    @staticmethod
    def validate_command(command: str) -> Tuple[bool, Optional[str]]:
        if len(command) > 200:
            return False, "Command exceeds maximum length of 200 characters"
        
        dangerous_commands = ['rm -rf', 'mkfs', 'dd', 'format']
        if any(dc in command.lower() for dc in dangerous_commands):
            return False, "Command contains potentially dangerous operations"
        
        return True, None

    @staticmethod
    def execute_command(command: str) -> Tuple[bool, str, str]:
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=True,
                capture_output=True,
                text=True
            )
            return True, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            return False, "", e.stderr
        except Exception as e:
            return False, "", str(e) 