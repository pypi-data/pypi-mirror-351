"""
Standalone setup script for fastchessenv that doesn't rely on external build scripts.
This script is used by the library loader to build the required libraries from source
when they are not found during import. It is designed to work in constrained environments
like Docker containers with minimal dependencies.
"""
import os
import platform
import subprocess
import sys
import tempfile
import logging
import shutil
from pathlib import Path

# Set up logging
logger = logging.getLogger("fastchessenv.setup_standalone")
handler = logging.StreamHandler()
formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Set log level based on environment variable
log_level = os.environ.get("FASTCHESSENV_LOG_LEVEL", "INFO").upper()
logger.setLevel(getattr(logging, log_level, logging.INFO))


def check_command_exists(command):
    """Check if a command exists in the system PATH."""
    try:
        subprocess.check_call(
            ["which", command],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def install_dependencies():
    """
    Try to install required dependencies using apt-get.
    This will only work if running with sufficient privileges.
    
    Returns:
        bool: True if dependencies were installed, False otherwise
    """
    try:
        # Check if we have sudo or root access
        is_root = os.geteuid() == 0 if hasattr(os, "geteuid") else False
        has_sudo = check_command_exists("sudo")
        
        if not is_root and not has_sudo:
            logger.warning("Not running as root and sudo not available. Cannot install dependencies.")
            return False
        
        # Check if apt-get is available (for Debian-based systems)
        if check_command_exists("apt-get"):
            logger.info("Installing required dependencies with apt-get...")
            
            cmd_prefix = ["sudo"] if not is_root and has_sudo else []
            
            # Update package list
            update_cmd = cmd_prefix + ["apt-get", "update", "-y"]
            subprocess.check_call(update_cmd)
            
            # Install dependencies
            install_cmd = cmd_prefix + [
                "apt-get", "install", "-y",
                "build-essential", "git", "gcc", "g++", "libomp-dev"
            ]
            subprocess.check_call(install_cmd)
            return True
        else:
            logger.warning("apt-get not found. Cannot install dependencies automatically.")
            return False
    except Exception as e:
        logger.warning(f"Failed to install dependencies: {e}")
        return False


def clone_misterqueen(target_dir):
    """
    Clone the MisterQueen repository to the target directory.
    If git is not available, try downloading a zip file instead.
    
    Args:
        target_dir: Directory to clone MisterQueen into
        
    Returns:
        str: Path to the MisterQueen directory, or None if failed
    """
    try:
        # First, try using git (the preferred method)
        if check_command_exists("git"):
            mq_dir = os.path.join(target_dir, "MisterQueen")
            logger.info(f"Cloning MisterQueen repository to {mq_dir}...")
            subprocess.check_call(
                ["git", "clone", "https://github.com/fogleman/MisterQueen.git", mq_dir]
            )
            return mq_dir
        
        # If git is not available, try downloading a zip file
        logger.warning("Git not found. Trying to download MisterQueen as a zip file...")
        
        # Check if we have curl or wget
        download_cmd = None
        if check_command_exists("curl"):
            download_cmd = ["curl", "-L", "-o"]
        elif check_command_exists("wget"):
            download_cmd = ["wget", "-O"]
        
        if download_cmd:
            # Download the zip file
            zip_path = os.path.join(target_dir, "misterqueen.zip")
            subprocess.check_call(
                download_cmd + [
                    zip_path,
                    "https://github.com/fogleman/MisterQueen/archive/refs/heads/master.zip"
                ]
            )
            
            # Extract the zip file
            import zipfile
            mq_dir = os.path.join(target_dir, "MisterQueen")
            os.makedirs(mq_dir, exist_ok=True)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(target_dir)
            
            # Move the contents to the correct location
            extracted_dir = os.path.join(target_dir, "MisterQueen-master")
            if os.path.exists(extracted_dir):
                # Copy all files from extracted_dir to mq_dir
                for item in os.listdir(extracted_dir):
                    src = os.path.join(extracted_dir, item)
                    dst = os.path.join(mq_dir, item)
                    if os.path.isdir(src):
                        shutil.copytree(src, dst, dirs_exist_ok=True)
                    else:
                        shutil.copy2(src, dst)
                
                # Remove the extracted directory
                shutil.rmtree(extracted_dir)
            
            # Remove the zip file
            os.remove(zip_path)
            
            return mq_dir
        
        logger.error("Neither git, curl, nor wget is available. Cannot download MisterQueen.")
        return None
    except Exception as e:
        logger.error(f"Failed to clone MisterQueen: {e}")
        return None


def build_misterqueen(mq_dir):
    """
    Build MisterQueen from source.
    
    Args:
        mq_dir: Path to the MisterQueen directory
        
    Returns:
        tuple: (build_dir, object_files, tc_obj_path) or (None, None, None) if failed
    """
    try:
        # Check if make is available
        if check_command_exists("make"):
            logger.info("Building MisterQueen with make...")
            subprocess.check_call(["make"], cwd=mq_dir)
            
            # Get output files
            build_dir = os.path.join(mq_dir, "build", "release")
            object_files = [
                os.path.join(build_dir, f) 
                for f in os.listdir(build_dir) 
                if f.endswith(".o") and not f.startswith("deps/")
            ]
            tc_obj_path = os.path.join(build_dir, "deps", "tinycthread", "tinycthread.o")
            
            return build_dir, object_files, tc_obj_path
        
        # If make is not available, try compiling manually
        logger.warning("Make not found. Trying to compile manually...")
        
        # Create build directory
        build_dir = os.path.join(mq_dir, "build", "manual")
        os.makedirs(build_dir, exist_ok=True)
        os.makedirs(os.path.join(build_dir, "deps", "tinycthread"), exist_ok=True)
        
        # Compile tinycthread
        tc_src = os.path.join(mq_dir, "deps", "tinycthread", "tinycthread.c")
        tc_obj_path = os.path.join(build_dir, "deps", "tinycthread", "tinycthread.o")
        subprocess.check_call(
            ["gcc", "-c", "-o", tc_obj_path, tc_src, "-pthread", "-I", os.path.join(mq_dir, "deps")]
        )
        
        # Get all source files
        src_files = []
        for root, _, files in os.walk(os.path.join(mq_dir, "src")):
            for file in files:
                if file.endswith(".c"):
                    src_files.append(os.path.join(root, file))
        
        # Compile all source files
        object_files = []
        for src_file in src_files:
            obj_file = os.path.join(build_dir, os.path.basename(src_file).replace(".c", ".o"))
            subprocess.check_call(
                ["gcc", "-c", "-o", obj_file, src_file, "-I", os.path.join(mq_dir, "src"), "-I", os.path.join(mq_dir, "deps")]
            )
            object_files.append(obj_file)
        
        return build_dir, object_files, tc_obj_path
    except Exception as e:
        logger.error(f"Failed to build MisterQueen: {e}")
        return None, None, None


def create_shared_libraries(lib_dir, object_files, tc_obj_path):
    """
    Create shared libraries from object files.
    
    Args:
        lib_dir: Directory to store the libraries
        object_files: List of object files for MisterQueen
        tc_obj_path: Path to the tinycthread object file
        
    Returns:
        bool: True if libraries were created successfully, False otherwise
    """
    try:
        # Ensure the library directory exists
        os.makedirs(lib_dir, exist_ok=True)
        
        # Determine compiler flags based on platform
        system = platform.system()
        machine = platform.machine().lower()
        
        # Default flags
        compile_flags = []
        link_flags = ["-lpthread"]
        
        # Platform-specific flags
        if system == "Darwin":  # macOS
            if machine == "arm64":
                compile_flags.extend(["-arch", "arm64"])
            else:
                compile_flags.extend(["-arch", "x86_64"])
            
            # Get platform-specific extension
            ext = ".dylib"
        elif system == "Linux":
            # Check if OpenMP is available
            has_openmp = False
            try:
                # Try to check if OpenMP is available by compiling a test program
                test_file = os.path.join(tempfile.mkdtemp(), "openmp_test.c")
                with open(test_file, "w") as f:
                    f.write("#include <omp.h>\nint main() { return 0; }")
                
                subprocess.check_call(
                    ["gcc", "-fopenmp", "-o", test_file + ".out", test_file],
                    stderr=subprocess.DEVNULL
                )
                has_openmp = True
            except Exception:
                pass
            
            if has_openmp:
                link_flags.append("-fopenmp")
                logger.info("OpenMP support detected and enabled")
            else:
                logger.warning("OpenMP not available, building without OpenMP support")
            
            # Get platform-specific extension
            ext = ".so"
        else:  # Windows or other
            ext = ".dll" if system == "Windows" else ".so"
        
        # Get architecture suffix
        arch_suffix = ""
        if system == "Darwin":
            arch_suffix = "_arm64" if machine == "arm64" else "_x86_64"
        elif system == "Linux":
            arch_suffix = "_aarch64" if "arm" in machine or "aarch64" in machine else "_x86_64"
        
        # Create shared libraries
        # Create libmisterqueen.so/dylib/dll
        mq_lib_path = os.path.join(lib_dir, f"libmisterqueen{arch_suffix}{ext}")
        logger.info(f"Creating MisterQueen library: {mq_lib_path}")
        subprocess.check_call(
            ["gcc"] + compile_flags + ["-shared", "-o", mq_lib_path] + object_files + link_flags
        )
        
        # Create libtinycthread.so/dylib/dll
        tc_lib_path = os.path.join(lib_dir, f"libtinycthread{arch_suffix}{ext}")
        logger.info(f"Creating tinycthread library: {tc_lib_path}")
        subprocess.check_call(
            ["gcc"] + compile_flags + ["-shared", "-o", tc_lib_path, tc_obj_path, "-lpthread"]
        )
        
        # Create plain .so versions for compatibility
        if ext != ".so":
            shutil.copy2(mq_lib_path, os.path.join(lib_dir, "libmisterqueen.so"))
            shutil.copy2(tc_lib_path, os.path.join(lib_dir, "libtinycthread.so"))
        
        return True
    except Exception as e:
        logger.error(f"Failed to create shared libraries: {e}")
        return False


def setup_libraries(target_dir=None):
    """
    Set up the required libraries for fastchessenv.
    
    Args:
        target_dir: Directory to install libraries to. If None, uses a temporary directory.
        
    Returns:
        Tuple of (success, lib_dir, error_message)
    """
    try:
        # Log system information
        logger.info(f"Platform: {platform.platform()}")
        logger.info(f"Architecture: {platform.machine()}")
        logger.info(f"Python version: {sys.version}")
        
        # Create a temporary directory if no target directory is specified
        if target_dir is None:
            temp_dir = tempfile.mkdtemp(prefix="fastchessenv_")
            lib_dir = os.path.join(temp_dir, "lib")
        else:
            lib_dir = os.path.join(target_dir, "lib")
        
        # Create the lib directory
        os.makedirs(lib_dir, exist_ok=True)
        
        # Check for required tools and dependencies
        logger.info("Checking for required tools and dependencies...")
        missing_tools = []
        for tool in ["gcc", "make", "git"]:
            if not check_command_exists(tool):
                missing_tools.append(tool)
        
        if missing_tools:
            logger.warning(f"Missing required tools: {', '.join(missing_tools)}")
            # Try to install dependencies
            if install_dependencies():
                logger.info("Dependencies installed successfully")
            else:
                logger.warning("Could not install dependencies automatically")
        
        # Clone MisterQueen repository
        work_dir = tempfile.mkdtemp(prefix="fastchessenv_build_")
        mq_dir = clone_misterqueen(work_dir)
        if not mq_dir:
            return False, None, "Failed to clone MisterQueen repository"
        
        # Build MisterQueen
        build_dir, object_files, tc_obj_path = build_misterqueen(mq_dir)
        if not build_dir:
            return False, None, "Failed to build MisterQueen"
        
        # Create shared libraries
        if not create_shared_libraries(lib_dir, object_files, tc_obj_path):
            return False, None, "Failed to create shared libraries"
        
        # Clean up temporary directories
        try:
            shutil.rmtree(work_dir)
        except Exception as e:
            logger.warning(f"Failed to clean up temporary directory: {e}")
        
        return True, lib_dir, None
    except Exception as e:
        import traceback
        error_message = f"Error building libraries: {e}\n{traceback.format_exc()}"
        logger.error(error_message)
        return False, None, error_message


if __name__ == "__main__":
    # When run directly, set up libraries in the current directory
    success, lib_dir, error = setup_libraries(".")
    if success:
        print(f"Libraries successfully built in {lib_dir}")
    else:
        print(f"Failed to build libraries: {error}")
        sys.exit(1)