# src/tools/discovery.py
"""
Tool Discovery and Auto-Registration for QC Agent Template

Based on the Industrial Engineering Agent tool_discovery.py but enhanced
with better file scanning and module loading.
"""

import logging
import os
import importlib.util
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger("tools.discovery")


class ToolDiscovery:
    """Discovers and auto-registers tools from the filesystem."""
    
    def __init__(self, tool_registry=None):
        """
        Initialize the tool discovery system.
        
        Args:
            tool_registry: Tool registry instance
        """
        self.tool_registry = tool_registry
        self.discovered_tools: Dict[str, Dict[str, Any]] = {}
        logger.info("ToolDiscovery initialized")
    
    def discover_tools_in_directory(self, directory: str, category: str = "data_retrieval") -> int:
        """
        Discover and register tools in a directory with detailed logging.
        
        Args:
            directory: Directory path to scan
            category: Category to assign to discovered tools
            
        Returns:
            Number of tools discovered and registered
        """
        if not os.path.exists(directory):
            logger.warning(f"📁 Tools directory not found: {directory}")
            return 0
        
        logger.info(f"🔍 Starting tool discovery in: {directory}")
        logger.info(f"📋 Tool naming rules: Functions must end with '_tool' and have docstrings")
        
        discovered_tools = []
        scanned_files = []
        skipped_files = []
        skipped_functions = []
        
        try:
            python_files = list(Path(directory).glob("*.py"))
            logger.info(f"📄 Found {len(python_files)} Python files to scan")
            
            for file_path in python_files:
                if file_path.name.startswith("__"):
                    skipped_files.append(f"{file_path.name} (system file)")
                    continue
                
                logger.debug(f"📄 Scanning file: {file_path.name}")
                scanned_files.append(file_path.name)
                
                try:
                    tools_in_file = self._scan_file_for_tools(
                        str(file_path), category, discovered_tools, skipped_functions
                    )
                    
                    if tools_in_file == 0:
                        logger.debug(f"   No tools found in {file_path.name}")
                    else:
                        logger.debug(f"   Found {tools_in_file} tools in {file_path.name}")
                        
                except Exception as e:
                    error_msg = f"{file_path.name} (scan error: {e})"
                    skipped_files.append(error_msg)
                    logger.error(f"❌ Failed to scan {file_path.name}: {e}")
            
            # Detailed summary logging
            self._log_discovery_summary(directory, discovered_tools, scanned_files, 
                                      skipped_files, skipped_functions)
            
            return len(discovered_tools)
            
        except Exception as e:
            logger.error(f"❌ Tool discovery failed: {e}")
            return 0
    def _scan_file_for_tools(self, file_path: str, category: str, discovered_tools: list, skipped_functions: list) -> int:
        """
        Scan a Python file for tool functions with detailed tracking.
        
        Args:
            file_path: Path to Python file
            category: Category for discovered tools
            discovered_tools: List to track discovered tools
            skipped_functions: List to track skipped functions
            
        Returns:
            Number of tools found in file
        """
        try:
            # Load module from file path
            spec = importlib.util.spec_from_file_location("tool_module", file_path)
            if not spec or not spec.loader:
                return 0
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            tools_found = 0
            file_name = Path(file_path).name
            
            # Look for tool functions
            for name, obj in vars(module).items():
                if callable(obj):
                    if self._is_tool_function(name, obj):
                        self._register_discovered_tool(name, obj, category, file_path)
                        discovered_tools.append((name, file_name))
                        tools_found += 1
                        logger.debug(f"   ✅ Registered tool: {name}")
                    else:
                        # Track why functions were skipped
                        if not name.startswith("_") and name not in ["main", "test", "setup", "init"]:
                            reason = "does not end with '_tool'" if not name.endswith("_tool") else "missing docstring"
                            skipped_functions.append(f"{name} ({reason})")
            
            return tools_found
            
        except Exception as e:
            logger.warning(f"Could not scan {file_path}: {e}")
            return 0
    
    def _is_tool_function(self, name: str, func) -> bool:
        """
        Check if a function is a tool function using strict rules.
        
        STRICT TOOL DETECTION RULES:
        1. Must be callable
        2. Must NOT start with underscore (private)
        3. Must NOT be common non-tool names
        4. Must END with "_tool" (REQUIRED)
        5. Must have a docstring
        
        Args:
            name: Function name
            func: Function object
            
        Returns:
            True if function is a valid tool
        """
        # 1. Must be callable
        if not callable(func):
            return False
            
        # 2. Skip private functions
        if name.startswith("_"):
            return False
            
        # 3. Skip common non-tool functions
        if name in ["main", "test", "setup", "init", "run", "execute"]:
            return False
        
        # 4. STRICT RULE: Must end with "_tool"
        if not name.endswith("_tool"):
            return False
        
        # 5. Must have docstring
        if not (hasattr(func, '__doc__') and func.__doc__ and func.__doc__.strip()):
            logger.warning(f"⚠️  Tool {name} missing docstring - skipped")
            return False
        
        # 6. Should return dict (recommended but not enforced)
        if hasattr(func, '__annotations__') and 'return' in func.__annotations__:
            return_type = func.__annotations__['return']
            if return_type != dict and str(return_type) != 'dict':
                logger.info(f"💡 Tool {name} should return dict, found: {return_type}")
        
        return True
    
    def _register_discovered_tool(self, name: str, func, category: str, file_path: str):
        """
        Register a discovered tool with the tool registry.
        
        Args:
            name: Tool name
            func: Tool function
            category: Tool category
            file_path: Source file path
        """
        if not self.tool_registry:
            return
            
        try:
            # CHECK FOR DUPLICATES - Skip if already registered
            if name in self.tool_registry.get_tool_names():
                logger.info(f"⏭️  Tool {name} already registered - skipping duplicate from {file_path}")
                return
            
            # Create description from docstring or default
            description = func.__doc__ or f"Auto-discovered tool: {name}"
            # Allow longer descriptions for better context (removed 200 char limit)
            
            # Register the tool
            self.tool_registry.register_tool(
                name=name,
                function=func,
                description=description.strip(),
                category=category
            )
            
            self.discovered_tools[name] = {
                "function": func,
                "category": category,
                "file_path": file_path,
                "description": description
            }
            
            logger.info(f"✅ Auto-registered tool: {name} from {Path(file_path).name}")
            
        except Exception as e:
            logger.error(f"Failed to register tool {name}: {e}")
    
    def get_discovered_tools(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about all discovered tools.
        
        Returns:
            Dictionary of discovered tool information
        """
        result = {}
        for name, info in self.discovered_tools.items():
            # Copy without the function object
            tool_copy = info.copy()
            tool_copy.pop("function", None)
            result[name] = tool_copy
        return result    
    def _log_discovery_summary(self, directory: str, discovered_tools: list, 
                             scanned_files: list, skipped_files: list, skipped_functions: list):
        """Log detailed summary of tool discovery process."""
        logger.info("=" * 60)
        logger.info("🛠️  TOOL DISCOVERY SUMMARY")
        logger.info("=" * 60)
        logger.info(f"📁 Directory scanned: {directory}")
        logger.info(f"📄 Files scanned: {len(scanned_files)}")
        logger.info(f"🛠️  Tools discovered: {len(discovered_tools)}")
        
        if discovered_tools:
            logger.info("📋 REGISTERED TOOLS:")
            for tool_name, file_name in discovered_tools:
                logger.info(f"   ✅ {tool_name} (from {file_name})")
        else:
            logger.info("📋 No new tools found")
            logger.info("💡 Ensure functions end with '_tool' and have docstrings")
            
        if skipped_files:
            logger.debug("⏭️  SKIPPED FILES:")
            for file_info in skipped_files:
                logger.debug(f"   ⏭️  {file_info}")
                
        # Show a few skipped functions as examples (not all - too verbose)
        if skipped_functions:
            logger.debug("⏭️  SKIPPED FUNCTIONS (sample):")
            for func_info in skipped_functions[:5]:  # Only first 5
                logger.debug(f"   ⏭️  {func_info}")
            if len(skipped_functions) > 5:
                logger.debug(f"   ... and {len(skipped_functions) - 5} more")
                
        logger.info("💡 REMINDER: Functions must end with '_tool' and have docstrings")
        logger.info("=" * 60)
    
    def get_discovery_help(self) -> str:
        """Get help text for tool discovery rules."""
        return """
🛠️  TOOL DISCOVERY RULES

✅ REQUIRED:
   • Function name MUST end with '_tool'
   • Function MUST have a docstring
   • Function should return a dictionary

❌ SKIPPED:
   • Functions starting with '_' (private)
   • Functions named: main, test, setup, init, run, execute
   • Functions without docstrings
   • Non-callable objects

📝 EXAMPLE:
   def analyze_data_tool(input_data: str) -> dict:
       \"\"\"Analyze the provided input data.\"\"\"
       return {"result": "analysis complete"}

📁 RECOMMENDED FILE NAMING:
   • analysis_tools.py
   • database_tools.py  
   • reporting_tools.py
"""