#!/usr/bin/env python3
"""
Concilium - Automated Setup Script
Handles cross-platform installation and configuration
"""

import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path


class ConciliumSetup:
    def __init__(self):
        self.system = platform.system()
        self.project_root = Path(__file__).parent
        self.backend_dir = self.project_root / "backend"
        self.venv_dir = self.backend_dir / "venv"
        
    def print_header(self, text):
        """Print formatted header"""
        print("\n" + "=" * 60)
        print(f"  {text}")
        print("=" * 60 + "\n")
    
    def print_step(self, text):
        """Print step message"""
        print(f"→ {text}")
    
    def print_success(self, text):
        """Print success message"""
        print(f"✓ {text}")
    
    def print_error(self, text):
        """Print error message"""
        print(f"✗ ERROR: {text}")
    
    def check_python_version(self):
        """Check Python version"""
        self.print_step("Checking Python version...")
        version = sys.version_info
        
        if version.major == 3 and version.minor >= 9:
            self.print_success(f"Python {version.major}.{version.minor}.{version.micro}")
            return True
        else:
            self.print_error(f"Python 3.9+ required, found {version.major}.{version.minor}")
            return False
    
    def check_ffmpeg(self):
        """Check if ffmpeg is installed"""
        self.print_step("Checking ffmpeg installation...")
        
        if shutil.which("ffmpeg"):
            self.print_success("ffmpeg is installed")
            return True
        else:
            self.print_error("ffmpeg not found")
            self.print_install_instructions()
            return False
    
    def print_install_instructions(self):
        """Print platform-specific installation instructions"""
        print("\nPlease install ffmpeg:")
        
        if self.system == "Windows":
            print("  Option 1: Download from https://ffmpeg.org/download.html")
            print("  Option 2: choco install ffmpeg")
        elif self.system == "Darwin":  # macOS
            print("  brew install ffmpeg")
        elif self.system == "Linux":
            print("  sudo apt install ffmpeg  # Ubuntu/Debian")
            print("  sudo yum install ffmpeg  # RHEL/CentOS")
        
        print()
    
    def create_virtualenv(self):
        """Create Python virtual environment"""
        self.print_step("Creating virtual environment...")
        
        if self.venv_dir.exists():
            self.print_success("Virtual environment already exists")
            return True
        
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(self.venv_dir)],
                check=True
            )
            self.print_success("Virtual environment created")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to create virtual environment: {e}")
            return False
    
    def get_pip_command(self):
        """Get the correct pip command for the platform"""
        if self.system == "Windows":
            return str(self.venv_dir / "Scripts" / "pip.exe")
        else:
            return str(self.venv_dir / "bin" / "pip")
    
    def get_python_command(self):
        """Get the correct python command for the platform"""
        if self.system == "Windows":
            return str(self.venv_dir / "Scripts" / "python.exe")
        else:
            return str(self.venv_dir / "bin" / "python")
    
    def upgrade_pip(self):
        """Upgrade pip to latest version"""
        self.print_step("Upgrading pip...")
        
        try:
            subprocess.run(
                [self.get_python_command(), "-m", "pip", "install", "--upgrade", "pip"],
                check=True,
                cwd=str(self.backend_dir)
            )
            self.print_success("pip upgraded")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to upgrade pip: {e}")
            return False
    
    def install_requirements(self):
        """Install Python requirements"""
        self.print_step("Installing Python packages...")
        
        requirements_file = self.backend_dir / "requirements.txt"
        
        if not requirements_file.exists():
            self.print_error(f"requirements.txt not found at {requirements_file}")
            return False
        
        try:
            subprocess.run(
                [self.get_pip_command(), "install", "-r", "requirements.txt"],
                check=True,
                cwd=str(self.backend_dir)
            )
            self.print_success("Python packages installed")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to install requirements: {e}")
            return False
    
    def install_pytorch(self):
        """Install PyTorch based on platform"""
        self.print_step("Installing PyTorch...")
        
        print("\nSelect PyTorch installation:")
        print("1. CPU only (recommended for most systems)")
        print("2. CUDA 11.8 (NVIDIA GPU)")
        print("3. CUDA 12.1 (NVIDIA GPU)")
        print("4. macOS (includes MPS support)")
        
        choice = input("\nEnter choice (1-4) [1]: ").strip() or "1"
        
        commands = {
            "1": [self.get_pip_command(), "install", "torch", "torchvision", "torchaudio", 
                  "--index-url", "https://download.pytorch.org/whl/cpu"],
            "2": [self.get_pip_command(), "install", "torch", "torchvision", "torchaudio",
                  "--index-url", "https://download.pytorch.org/whl/cu118"],
            "3": [self.get_pip_command(), "install", "torch", "torchvision", "torchaudio",
                  "--index-url", "https://download.pytorch.org/whl/cu121"],
            "4": [self.get_pip_command(), "install", "torch", "torchvision", "torchaudio"]
        }
        
        command = commands.get(choice, commands["1"])
        
        try:
            subprocess.run(command, check=True, cwd=str(self.backend_dir))
            self.print_success("PyTorch installed")
            return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Failed to install PyTorch: {e}")
            return False
    
    def create_env_file(self):
        """Create .env configuration file"""
        self.print_step("Creating configuration file...")
        
        env_file = self.backend_dir / ".env"
        env_example = self.backend_dir / ".env.example"
        
        if env_file.exists():
            self.print_success(".env file already exists")
            return True
        
        if env_example.exists():
            shutil.copy(env_example, env_file)
            self.print_success(".env file created from template")
            print("\n⚠ IMPORTANT: Edit .env file and set your HF_TOKEN")
            print("  Get token from: https://huggingface.co/settings/tokens\n")
            return True
        else:
            # Create basic .env
            env_content = """# Concilium Configuration
APP_NAME=Concilium AI Assistant
ENVIRONMENT=development
DEBUG=true

HOST=0.0.0.0
PORT=8000
RELOAD=true

# AI Models - Set based on your system
LLM_MODEL_NAME=meta-llama/Llama-2-7b-chat-hf
WHISPER_MODEL_SIZE=base
LLM_DEVICE=cpu
WHISPER_DEVICE=cpu

# ⚠ REQUIRED: Get token from https://huggingface.co/settings/tokens
HF_TOKEN=your_token_here

MAX_UPLOAD_SIZE_MB=100
DATABASE_URL=sqlite+aiosqlite:///./concilium.db
LOG_LEVEL=INFO
"""
            env_file.write_text(env_content)
            self.print_success(".env file created")
            print("\n⚠ IMPORTANT: Edit .env file and set your HF_TOKEN")
            print("  Get token from: https://huggingface.co/settings/tokens\n")
            return True
    
    def create_directories(self):
        """Create necessary directories"""
        self.print_step("Creating directories...")
        
        directories = [
            self.backend_dir / "uploads",
            self.backend_dir / "outputs" / "workflows",
            self.backend_dir / "outputs" / "documents",
            self.backend_dir / "templates",
            self.backend_dir / "logs"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
        
        self.print_success("Directories created")
        return True
    
    def print_next_steps(self):
        """Print next steps for the user"""
        self.print_header("Setup Complete!")
        
        print("Next steps:\n")
        print("1. Edit .env file and add your Hugging Face token:")
        print(f"   {self.backend_dir / '.env'}\n")
        
        print("2. Activate virtual environment:")
        if self.system == "Windows":
            print(f"   {self.venv_dir}\\Scripts\\activate\n")
        else:
            print(f"   source {self.venv_dir}/bin/activate\n")
        
        print("3. Start the application:")
        print("   cd backend")
        print("   python -m app.main\n")
        
        print("4. Access the API:")
        print("   http://localhost:8000\n")
        print("   http://localhost:8000/docs (API documentation)\n")
        
        print("For desktop app:")
        print("   cd frontend/desktop")
        print("   npm install")
        print("   npm start\n")
    
    def run(self):
        """Run the complete setup process"""
        self.print_header(f"Concilium Setup - {self.system}")
        
        steps = [
            ("Checking Python version", self.check_python_version),
            ("Checking ffmpeg", self.check_ffmpeg),
            ("Creating virtual environment", self.create_virtualenv),
            ("Upgrading pip", self.upgrade_pip),
            ("Installing requirements", self.install_requirements),
            ("Installing PyTorch", self.install_pytorch),
            ("Creating configuration", self.create_env_file),
            ("Creating directories", self.create_directories),
        ]
        
        for step_name, step_func in steps:
            if not step_func():
                self.print_error(f"Setup failed at step: {step_name}")
                return False
        
        self.print_next_steps()
        return True


if __name__ == "__main__":
    setup = ConciliumSetup()
    success = setup.run()
    sys.exit(0 if success else 1)
