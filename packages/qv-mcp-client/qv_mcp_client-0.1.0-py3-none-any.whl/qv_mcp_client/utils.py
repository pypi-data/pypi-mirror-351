"""Utility functions for MCP client"""

import platform


def is_windows() -> bool:
    """Check if running on Windows"""
    return platform.system().lower() == "windows"


def needs_cmd_wrapper(command: str) -> bool:
    """Check if command needs cmd.exe wrapper on Windows"""
    # Common Node.js/npm commands that are .cmd files on Windows
    cmd_commands = {
        "npx", "npm", "yarn", "pnpm", "node", 
        "tsc", "webpack", "vite", "ng", "vue",
        "create-react-app", "next", "nuxt"
    }
    
    # Check if it's a known .cmd command
    if command.lower() in cmd_commands:
        return True
        
    # Check if it ends with .cmd or .bat
    if command.lower().endswith(('.cmd', '.bat')):
        return True
        
    return False 