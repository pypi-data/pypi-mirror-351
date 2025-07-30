import typer
from dbconvert.core.loggingsetup import LoggerManager
from dbconvert.converters.converter_factory import ConverterFactory
from dbconvert.writers.sqlite_writer import SQLiteWriter
from dbconvert.core.enums import DatabaseType
import os
from dbconvert.core.metadata import load_pyproject_metadata
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

app = typer.Typer(help="Convert SQL databases to SQLite. Supports both Command-Line and Graphical User Interfaces.")
logger = LoggerManager.get_logger()

def print_banner(version, author, author_url, repo):
    console = Console()
    banner_text = Text()
    banner_text.append("\n██████╗ ██████╗  ██████╗ ██████╗ ███╗   ██╗██╗   ██╗███████╗██████╗ ████████╗", style="bold blue")
    banner_text.append("\n██╔══██╗██╔══██╗██╔════╝██╔═══██╗████╗  ██║██║   ██║██╔════╝██╔══██╗╚══██╔══╝", style="bold blue")
    banner_text.append("\n██║  ██║██████╔╝██║     ██║   ██║██╔██╗ ██║██║   ██║█████╗  ██████╔╝   ██║   ", style="bold blue")
    banner_text.append("\n██║  ██║██╔══██╗██║     ██║   ██║██║╚██╗██║╚██╗ ██╔╝██╔══╝  ██╔══██╗   ██║   ", style="bold blue")
    banner_text.append("\n██████╔╝██████╔╝╚██████╗╚██████╔╝██║ ╚████║ ╚████╔╝ ███████╗██║  ██║   ██║   ", style="bold blue")
    banner_text.append("\n╚═════╝ ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═══╝  ╚═══╝  ╚══════╝╚═╝  ╚═╝   ╚═╝   \n", style="bold blue")
    banner_text.append(f"Version : {version}\n", style="bold blue")
    banner_text.append(f"Author  : {author} ({author_url})\n", style="magenta")
    banner_text.append(f"Repo    : {repo}\n", style="green")
    banner_text.append("\nDbConvert supports both a modern Command-Line Interface (CLI) and a user-friendly Graphical User Interface (GUI).", style="bold yellow")
    console.print(Panel(banner_text, expand=False, border_style="blue", title="Welcome", title_align="left"))

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    metadata = load_pyproject_metadata()
    version = metadata.get("version")
    repo = metadata.get("repository")
    internal_urls = metadata.get("internalurls", {})
    author = f"{internal_urls.get('author_name')}"
    author_url = f"{internal_urls.get('author_linkedin')}"
    print_banner(version, author, author_url, repo)
    if ctx.invoked_subcommand is None:
        logger.info("No command provided. Use --help for usage.")

@app.command(name="gui")
def launch_gui():
    """
    Launch the graphical user interface (GUI) for DbConvert.
    The GUI provides a simple, no-code way to convert your databases.
    """
    try:
        import PIL
        from dbconvert.gui.app import main
        main()
    except ImportError:
        logger.error("The GUI requires extra dependencies. Please install with: \npip install dbconvert[gui]")
        raise typer.Exit(1)
    except Exception as e:
        logger.error(f"Error launching GUI: {str(e)}")
        raise typer.Exit(1)

@app.command(name="supported-databases")
def supported_databases():
    """
    Show supported database types for conversion.
    """
    logger.info("Supported database types:")
    for db_type in DatabaseType.values():
        logger.info(f"  • {db_type}")

@app.command()
def convert(
    source: str = typer.Option(..., help=f"Source database type ({', '.join(DatabaseType.values())})"),
    conn: str = typer.Option(..., help="Source database connection string"),
    sqlite: str = typer.Option(..., help="Target SQLite database file path")
):
    """
    Convert a PostgreSQL or MySQL database to SQLite.
    """
    try:
        # Validate source database type
        if source not in DatabaseType.values():
            raise ValueError(f"Unsupported source database type: {source}")
        
        # Validate connection string
        if not conn:
            raise ValueError("Connection string cannot be empty")
        
        # Validate SQLite path
        sqlite_dir = os.path.dirname(sqlite)
        if sqlite_dir and not os.path.exists(sqlite_dir):
            os.makedirs(sqlite_dir)
        
        # Create converter using factory
        converter = ConverterFactory.create_converter(source, conn)
        
        # Read source database
        logger.info("Reading source database...")
        tables = converter.read_all_tables()
        
        # Write to SQLite
        logger.info("Writing to SQLite database...")
        writer = SQLiteWriter(sqlite)
        writer.write_all_tables(tables)
        
        logger.info("✅ Conversion completed successfully!")
        
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()