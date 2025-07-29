"""
Progress reporting utilities.
"""

import sys
import time
import logging
from typing import Optional


class ProgressReporter:
    """Progress reporter that outputs to stderr or log file"""
    
    def __init__(self, logger: logging.Logger, enable_progress: bool = True):
        self.logger = logger
        self.enable_progress = enable_progress
        self.start_time = None
        self.current_step = None
        self.step_start_time = None
    
    def start(self, message: str) -> None:
        """
        Start progress reporting
        
        Args:
            message: Initial progress message
        """
        if not self.enable_progress:
            return
        
        self.start_time = time.time()
        self.step_start_time = self.start_time
        self.current_step = message
        self.logger.info(f"🚀 {message}")
    
    def update(self, message: str, step: Optional[int] = None, total: Optional[int] = None) -> None:
        """
        Update progress
        
        Args:
            message: Progress message
            step: Current step number (optional)
            total: Total steps (optional)
        """
        if not self.enable_progress:
            return
        
        current_time = time.time()
        elapsed = current_time - self.start_time if self.start_time else 0
        step_elapsed = current_time - self.step_start_time if self.step_start_time else 0
        
        if step is not None and total is not None:
            percentage = (step / total) * 100
            self.logger.info(
                f"⏳ {message} ({step}/{total}, {percentage:.1f}%) "
                f"- Step: {step_elapsed:.1f}s, Total: {elapsed:.1f}s"
            )
        else:
            self.logger.info(
                f"⏳ {message} - Step: {step_elapsed:.1f}s, Total: {elapsed:.1f}s"
            )
        
        self.current_step = message
        self.step_start_time = current_time
    
    def finish(self, message: str) -> None:
        """
        Finish progress reporting
        
        Args:
            message: Final message
        """
        if not self.enable_progress:
            return
        
        elapsed = time.time() - self.start_time if self.start_time else 0
        self.logger.info(f"✅ {message} - Total time: {elapsed:.1f}s")
    
    def log_error(self, message: str) -> None:
        """
        Log error message
        
        Args:
            message: Error message
        """
        self.logger.error(f"❌ {message}")
    
    def log_warning(self, message: str) -> None:
        """
        Log warning message
        
        Args:
            message: Warning message
        """
        self.logger.warning(f"⚠️  {message}")
