import click
import subprocess
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from ..core.models.manager import model_manager
from ..core.config.settings import settings

console = Console()

@click.command()
def verify_deps():
    """Verify and install missing dependencies"""
    console.print("\n🔍 [bold blue]Checking OllamaDiffuser Dependencies[/bold blue]")
    
    # Check critical dependencies
    deps_status = {}
    
    # OpenCV check
    try:
        import cv2
        deps_status['opencv-python'] = f"✅ Installed (v{cv2.__version__})"
    except ImportError:
        deps_status['opencv-python'] = "❌ Missing"
    
    # ControlNet Aux check
    try:
        import controlnet_aux
        deps_status['controlnet-aux'] = "✅ Installed"
    except ImportError:
        deps_status['controlnet-aux'] = "❌ Missing"
    
    # Torch check
    try:
        import torch
        deps_status['torch'] = f"✅ Installed (v{torch.__version__})"
    except ImportError:
        deps_status['torch'] = "❌ Missing"
    
    # Diffusers check
    try:
        import diffusers
        deps_status['diffusers'] = f"✅ Installed (v{diffusers.__version__})"
    except ImportError:
        deps_status['diffusers'] = "❌ Missing"
    
    # Create status table
    table = Table(title="Dependency Status")
    table.add_column("Package", style="cyan")
    table.add_column("Status", style="white")
    
    missing_deps = []
    for dep, status in deps_status.items():
        table.add_row(dep, status)
        if "❌ Missing" in status:
            missing_deps.append(dep)
    
    console.print(table)
    
    if missing_deps:
        console.print(f"\n⚠️  [bold yellow]{len(missing_deps)} dependencies are missing[/bold yellow]")
        
        if click.confirm("\nWould you like to install missing dependencies?"):
            for dep in missing_deps:
                console.print(f"\n📦 Installing {dep}...")
                
                # Determine package name
                if dep == 'opencv-python':
                    package = 'opencv-python>=4.8.0'
                elif dep == 'controlnet-aux':
                    package = 'controlnet-aux>=0.0.7'
                else:
                    package = dep
                
                try:
                    subprocess.check_call([
                        sys.executable, "-m", "pip", "install", package
                    ])
                    console.print(f"✅ {dep} installed successfully")
                except subprocess.CalledProcessError as e:
                    console.print(f"❌ Failed to install {dep}: {e}")
        
        console.print("\n🔄 Re-run 'ollamadiffuser verify-deps' to check status")
    else:
        console.print("\n🎉 [bold green]All dependencies are installed![/bold green]")
    
    # Check ControlNet preprocessors
    console.print("\n🔧 [bold blue]Testing ControlNet Preprocessors[/bold blue]")
    try:
        from ..core.utils.controlnet_preprocessors import controlnet_preprocessor
        if controlnet_preprocessor.is_available():
            available_types = controlnet_preprocessor.get_available_types()
            console.print(f"✅ Available types: {', '.join(available_types)}")
        else:
            console.print("⚠️  ControlNet preprocessors not fully available")
    except Exception as e:
        console.print(f"❌ Error testing preprocessors: {e}")

@click.command()
def doctor():
    """Run comprehensive system diagnostics"""
    console.print(Panel.fit("🩺 [bold blue]OllamaDiffuser Doctor[/bold blue]"))
    
    # System info
    import platform
    console.print(f"\n💻 System: {platform.system()} {platform.release()}")
    console.print(f"🐍 Python: {sys.version.split()[0]}")
    
    # GPU info
    try:
        import torch
        if torch.cuda.is_available():
            console.print(f"🎮 CUDA: Available ({torch.cuda.get_device_name()})")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            console.print("🍎 Apple Metal: Available")
        else:
            console.print("⚙️ GPU: CPU only")
    except ImportError:
        console.print("❌ PyTorch not installed")
    
    # Memory info
    try:
        import psutil
        memory = psutil.virtual_memory()
        console.print(f"🧠 RAM: {memory.total // (1024**3)} GB total, {memory.available // (1024**3)} GB available")
    except ImportError:
        console.print("⚠️ Cannot check memory (psutil missing)")
    
    # Run dependency check
    console.print("\n" + "="*50)
    ctx = click.Context(verify_deps)
    ctx.invoke(verify_deps) 