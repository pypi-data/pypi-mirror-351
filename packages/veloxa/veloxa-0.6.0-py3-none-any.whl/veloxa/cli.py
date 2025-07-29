import shutil
import sys
from pathlib import Path
import questionary
import argparse
from rich import print as rprint

def get_structures():
    """Return available Flask project structures"""
    return [
        'Single File Structure (Hello World App)', 
        'Basic Modular Structure', 
        'Application Factory Pattern', 
        'Blueprint-Based Structure', 
        'Factory + Blueprints + Config Class', 
        'Flask with Celery (Task Queue Structure)', 
        'Flask with API (RESTful Structure)', 
        'Full-Scale Production Structure (Advanced)'
    ]

def get_slug_map():
    """Return mapping of structure names to template directory names"""
    return {
        'Single File Structure (Hello World App)': 'single_file', 
        'Basic Modular Structure': 'basic_modular', 
        'Application Factory Pattern': 'application_factory', 
        'Blueprint-Based Structure': 'blueprint_based', 
        'Factory + Blueprints + Config Class': 'factory_blueprints_config', 
        'Flask with Celery (Task Queue Structure)': 'flask_with_celery', 
        'Flask with API (RESTful Structure)': 'flask_with_api', 
        'Full-Scale Production Structure (Advanced)': 'full_scale_production'
    }

def create_project(project_name, selected_structure, dest_path):
    """Create project with given name and structure at destination path"""
    slug_map = get_slug_map()
    src_path = Path(__file__).parent / "templates" / slug_map[selected_structure]
    
    if not src_path.exists():
        print(f"❌ Template '{slug_map[selected_structure]}' not found.")
        return False

    try:
        if dest_path.exists():
            print(f"❌ Directory '{project_name}' already exists.")
            return False

        # Copy template to destination
        shutil.copytree(src_path, dest_path)
        
        print(f"✅ Flask project '{project_name}' created successfully!")
        print(f"📁 Structure: {selected_structure}")
        print(f"📍 Location: {dest_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error creating project: {e}")
        return False

def init_project_in_current_dir(selected_structure):
    """Initialize project in current directory"""
    current_dir = Path.cwd()
    project_name = current_dir.name
    slug_map = get_slug_map()
    src_path = Path(__file__).parent / "templates" / slug_map[selected_structure]
    
    if not src_path.exists():
        print(f"❌ Template '{slug_map[selected_structure]}' not found.")
        return False

    try:
        # Copy all files from template to current directory
        for item in src_path.iterdir():
            if item.is_file():
                shutil.copy2(item, current_dir / item.name)
            elif item.is_dir():
                shutil.copytree(item, current_dir / item.name, dirs_exist_ok=True)
        
        print(f"✅ Flask project '{project_name}' initialized successfully!")
        print(f"📁 Structure: {selected_structure}")
        print(f"📍 Location: {current_dir}")
        return True
        
    except Exception as e:
        print(f"❌ Error initializing project: {e}")
        return False

from pathlib import Path
import shutil
import questionary
from rich import print as rprint

def init_command(force=False):
    project_root = Path.cwd()
    template_base = Path(__file__).parent / "templates"

    if not template_base.exists():
        rprint("[red]❌ Templates folder not found.[/red]")
        return

    # Dynamically list all subdirectories in templates/
    structures = [
        folder.name for folder in template_base.iterdir()
        if folder.is_dir()
    ]

    if not structures:
        rprint("[red]❌ No project structures found in templates.[/red]")
        return

    selected_structure = questionary.select(
        "📁 Choose your project structure:",
        choices=structures
    ).ask()

    if selected_structure is None:
        rprint("[yellow]⚠️ No selection made. Exiting.[/yellow]")
        return

    src_path = template_base / selected_structure

    if not src_path.exists():
        rprint(f"[red]❌ Selected template '{selected_structure}' not found.[/red]")
        return

    # Copy logic
    def copy_all_files(src, dst):
        for item in src.iterdir():
            s_item = src / item.name
            d_item = dst / item.name
            if s_item.is_dir():
                shutil.copytree(s_item, d_item, dirs_exist_ok=True)
            else:
                shutil.copy2(s_item, d_item)

    if any(project_root.iterdir()) and not force:
        rprint("[red]❌ Directory not empty. Use -f to force overwrite.[/red]")
        return

    rprint(f"[yellow]⚠️ {'Overwriting' if force else 'Copying'} files to current directory.[/yellow]")

    if force:
        copy_all_files(src_path, project_root)
    else:
        shutil.copytree(src_path, project_root, dirs_exist_ok=True)

    rprint(f"[green]✅ Project initialized using '{selected_structure}' structure.[/green]")

def create_command():
    """Create a new Flask project with specified name"""
    project_name = questionary.text("Enter your project name:").ask()
    if not project_name:
        print("❌ Project name is required.")
        return

    structures = get_structures()
    selected = questionary.select(
        "Select a Flask project structure:",
        choices=structures
    ).ask()

    if not selected:
        print("❌ No structure selected. Project creation cancelled.")
        return

    dest_path = Path.cwd() / project_name
    create_project(project_name, selected, dest_path)

def main():
    """Main CLI entry point"""
    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "init":
            # Check for force flag
            force = False
            if len(sys.argv) > 2 and sys.argv[2] == "-f":
                force = True
            elif len(sys.argv) > 2 and sys.argv[2] not in ["-f"]:
                print("❌ Invalid argument. Use 'veloxa init -f' for force mode.")
                return
            
            init_command(force=force)
        else:
            # Show help for unknown commands
            print("Veloxa - Flask Project Scaffolding Tool")
            print("\nUsage:")
            print("  veloxa           Create a new Flask project (asks for project name)")
            print("  veloxa init      Initialize Flask project in current directory")
            print("  veloxa init -f   Force initialize (removes existing files)")
            print("\nExamples:")
            print("  # Create new project with custom name:")
            print("  veloxa")
            print()
            print("  # Initialize in existing directory:")
            print("  mkdir my-flask-app")
            print("  cd my-flask-app")
            print("  veloxa init")
            print()
            print("  # Force initialize (clears directory first):")
            print("  cd existing-project")
            print("  veloxa init -f")
    else:
        # Default behavior - ask for project name and create new directory
        create_command()
    """Create a new Flask project with specified name"""
    project_name = questionary.text("Enter your project name:").ask()
    if not project_name:
        print("❌ Project name is required.")
        return

    structures = get_structures()
    selected = questionary.select(
        "Select a Flask project structure:",
        choices=structures
    ).ask()

    if not selected:
        print("❌ No structure selected. Project creation cancelled.")
        return

    dest_path = Path.cwd() / project_name
    create_project(project_name, selected, dest_path)

def main():
    """Main CLI entry point"""
    if len(sys.argv) > 1 and sys.argv[1] == "init":
        init_command()
    elif len(sys.argv) == 1:
        create_command()
    else:
        print("Veloxa - Flask Project Scaffolding Tool")
        print("\nUsage:")
        print("  veloxa         Create a new Flask project (asks for project name)")
        print("  veloxa init    Initialize Flask project in current directory")
        print("\nExamples:")
        print("  # Create new project with custom name:")
        print("  veloxa")
        print()
        print("  # Initialize in existing directory:")
        print("  mkdir my-flask-app")
        print("  cd my-flask-app")
        print("  veloxa init")

if __name__ == "__main__":
    main()