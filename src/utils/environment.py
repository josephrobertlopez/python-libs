import os
import sys
from typing import Dict

def get_resource_path(relative_path: str) -> str:
    """Get the absolute path to a resource, works for development and PyInstaller.

    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: The full path to the resource.

    Raises:
        FileNotFoundError: If the resource is not found.
    """
    if getattr(sys, 'frozen', False):  # Running in a PyInstaller bundle
        base_path = sys._MEIPASS  # PyInstaller's temp folder
    else:
        base_path = os.path.abspath(".")  # Current working directory
        
    full_path = os.path.join(base_path, relative_path)
    
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"Resource not found: {full_path}")
    
    return full_path

def get_running_in_pyinstaller() -> str:
    """Check if the script is running in a PyInstaller bundle.

    Returns:
        str: Path to the executable if running in PyInstaller.

    Raises:
        EnvironmentError: If not running in a PyInstaller bundle.
    """
    if getattr(sys, 'frozen', False):
        return sys.executable  # Return the path to the executable
    raise EnvironmentError("Not running in a PyInstaller bundle.")

def get_virtual_env() -> str:
    """Check if the script is running in a virtual environment.

    Returns:
        str: Path to the virtual environment.

    Raises:
        EnvironmentError: If not running in a virtual environment.
    """
    if hasattr(sys, 'real_prefix'):
        return sys.prefix  # Return the path to the virtual environment
    elif hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        return sys.prefix  # Return the path to the virtual environment
    raise EnvironmentError("Not running in a virtual environment.")

def get_env_var(var_name: str) -> str:
    """Get an environment variable.

    Args:
        var_name (str): The name of the environment variable to retrieve.

    Returns:
        str: Value of the environment variable.

    Raises:
        KeyError: If the environment variable is not found.
    """
    try:
        return os.environ[var_name]
    except KeyError:
        raise KeyError(f"Environment variable '{var_name}' not found.")

def get_docker_info() -> Dict[str, str]:
    """Check if the script is running inside a Docker container and return relevant info.

    Returns:
        Dict[str, str]: Information about the Docker environment, including:
            - 'running': True
            - 'container_id': ID of the Docker container
            - 'hostname': Hostname of the container

    Raises:
        EnvironmentError: If not running in Docker or an error occurred.
    """
    docker_info = {}

    try:
        with open('/proc/1/cgroup', 'rt') as f:
            cgroup_info = f.read()
            if 'docker' in cgroup_info:
                docker_info['running'] = True
                
                # Attempt to get container ID
                docker_info['container_id'] = cgroup_info.split('/')[-1].strip()
                
                # Get hostname
                with open('/etc/hostname', 'rt') as hostname_file:
                    docker_info['hostname'] = hostname_file.read().strip()
                
                return docker_info

    except FileNotFoundError:
        raise EnvironmentError("Not running in Docker.")
    except Exception as e:
        raise EnvironmentError(f"An error occurred while checking Docker: {e}")

    raise EnvironmentError("Not running in Docker.")
