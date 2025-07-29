import os
from pathlib import Path
from labdb.api import ExperimentLogger, ExperimentQuery

__all__ = ["ExperimentLogger", "ExperimentQuery", "get_package_root"]

def get_package_root():
    """
    Returns the path to the labdb package directory.
    
    This is useful for finding the MATLAB interface files.
    
    Returns:
        str: The path to the labdb package directory
    """
    return os.path.dirname(os.path.abspath(__file__))
