import os
import sys
import subprocess
import glob
import time
from datetime import datetime
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.style import Style
from rich import print as rprint
from rich.padding import Padding
from rich.box import Box, ROUNDED
from rich.tree import Tree
from rich.filesize import decimal as format_filesize

# Initialize Typer app
app = typer.Typer(
    help="FanFic Downloader CLI - Download fan fiction stories from various sites",
    add_completion=False,
)

# Initialize Rich console
console = Console()


# Configuration directory and file setup
def get_config_dir():
    """Get the appropriate config directory based on the operating system."""
    if sys.platform == 'win32':
        # Windows: Use AppData\Roaming
        config_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'FanFicDownloader')
    elif sys.platform == 'darwin':
        # macOS: Use ~/Library/Application Support
        config_dir = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'FanFicDownloader')
    else:
        # Linux/Unix: Use ~/.config
        config_dir = os.path.join(os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config')),
                                  'FanFicDownloader')

    # Create config directory if it doesn't exist
    os.makedirs(config_dir, exist_ok=True)
    return config_dir


# Configuration file to store settings
CONFIG_DIR = get_config_dir()
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.txt")
DEFAULT_DOWNLOAD_FOLDER = os.path.join(os.path.expanduser("~"), "FanFicDownloads")


def load_config():
    """Loads configuration settings from a file."""
    try:
        with open(CONFIG_FILE, "r") as file:
            config = file.readlines()
            download_folder = config[0].strip() if len(config) > 0 else DEFAULT_DOWNLOAD_FOLDER
            return download_folder
    except FileNotFoundError:
        return DEFAULT_DOWNLOAD_FOLDER


def save_config(download_folder):
    """Saves configuration settings to a file."""
    with open(CONFIG_FILE, "w") as file:
        file.write(f"{download_folder}\n")


# Initialize user folder
USER_FOLDER = load_config()
os.makedirs(USER_FOLDER, exist_ok=True)


def show_app_header():
    """Display a stylish app header."""
    header = Panel(
        "[bold blue]FanFic Downloader CLI[/bold blue]\n[italic]Powered by FanFicFare[/italic]",
        border_style="blue",
        expand=False
    )
    console.print(header)


def run_fanficfare(args: List[str], hide_console: bool = True, working_dir: str = None) -> subprocess.CompletedProcess:
    """
    Run the fanficfare command with the given arguments.

    Args:
        args: List of arguments to pass to fanficfare
        hide_console: Whether to hide the console window on Windows
        working_dir: Directory to run the command from (None = current directory)

    Returns:
        CompletedProcess object with the result
    """
    startupinfo = None
    if sys.platform == 'win32' and hide_console:
        # For Windows, use STARTUPINFO to hide the console
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = 0  # SW_HIDE

    try:
        result = subprocess.run(
            ["fanficfare"] + args,
            capture_output=True,
            text=True,
            check=False,
            startupinfo=startupinfo,
            cwd=working_dir  # This is the key parameter that sets the working directory
        )
        return result
    except FileNotFoundError:
        console.print("[bold red]Error:[/bold red] FanFicFare not found. Please install it with:")
        console.print("[yellow]pip install fanficfare[/yellow]")
        sys.exit(1)


def load_urls_from_file(file_path: str) -> List[str]:
    """Load URLs from a text file, one URL per line"""
    try:
        with open(file_path, "r") as file:
            urls = [url.strip() for url in file.readlines() if url.strip()]

        # Show success message with number of URLs loaded
        rprint(f"[green]✓[/green] Loaded [bold]{len(urls)}[/bold] URLs from {file_path}")
        return urls
    except Exception as e:
        rprint(f"[bold red]✗[/bold red] Error loading file {file_path}: {str(e)}")
        return []


def save_urls_to_file(urls: List[str], file_path: str) -> bool:
    """Save a list of URLs to a text file"""
    try:
        with open(file_path, "w") as file:
            for url in urls:
                file.write(f"{url}\n")
        rprint(f"[green]✓[/green] Saved [bold]{len(urls)}[/bold] URLs to {file_path}")
        return True
    except Exception as e:
        rprint(f"[bold red]✗[/bold red] Error saving to file {file_path}: {str(e)}")
        return False


def find_epub_files(folder_path: str) -> List[str]:
    """
    Recursively find all EPUB files in a folder and its subfolders.

    Args:
        folder_path: Path to the folder to search

    Returns:
        List of full paths to EPUB files
    """
    epub_files = []

    try:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.epub'):
                    epub_files.append(os.path.join(root, file))
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error searching folder {folder_path}: {str(e)}")

    return epub_files


def perform_download(urls_list, output_folder=None):
    """
    Core download functionality that can be called directly or from commands

    Args:
        urls_list: List of URLs to download
        output_folder: Optional custom output folder
    """
    # Set download folder
    target_folder = output_folder if output_folder else USER_FOLDER

    # Show download information
    console.print(f"[bold]Downloading [cyan]{len(urls_list)}[/cyan] stories to [blue]{target_folder}[/blue][/bold]")

    # Set up progress display
    with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}[/bold blue]"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            expand=True
    ) as progress:

        download_task = progress.add_task("[bold]Downloading stories...[/bold]", total=len(urls_list))
        success_count = 0
        error_count = 0

        # Process each URL
        for url in urls_list:
            filename = url.split('/')[-1] + ".epub"
            filepath = os.path.join(target_folder, filename)

            # Update progress description to show current URL
            progress.update(download_task, description=f"[bold]Downloading:[/bold] {url.split('/')[-1]}...")

            try:
                # Run FanFicFare to download the story
                result = run_fanficfare(["-o", "is_adult=true", "-u", url], working_dir=target_folder)

                if result.returncode == 0:
                    success_count += 1
                else:
                    error_count += 1
                    # Don't show error details in progress to avoid cluttering display

            except Exception as e:
                error_count += 1

            # Update progress
            progress.advance(download_task)

    # Show download summary
    if success_count > 0:
        console.print(f"[bold green]✓[/bold green] Successfully downloaded [bold]{success_count}[/bold] stories")

    if error_count > 0:
        console.print(f"[bold red]✗[/bold red] Failed to download [bold]{error_count}[/bold] stories")

    # Show open folder prompt if any successful downloads
    if success_count > 0 and Confirm.ask("Open download folder?"):
        open_download_folder()


@app.command("download")
def download_stories(
        urls: List[str] = typer.Option(None, "--url", "-u", help="One or more story URLs to download"),
        file: Optional[str] = typer.Option(None, "--file", "-f", help="File containing story URLs (one per line)"),
        interactive: bool = typer.Option(False, "--interactive", "-i", help="Enter URLs interactively"),
        output_folder: Optional[str] = typer.Option(None, "--output", "-o",
                                                    help="Override download folder for this session"),
):
    """
    Download fan fiction stories from provided URLs.

    Examples:
        fanfic download -u https://archiveofourown.org/works/12345678
        fanfic download -f urls.txt
        fanfic download -i
    """
    show_app_header()

    all_urls = []

    # Get URLs from command line arguments
    if urls:
        all_urls.extend(urls)

    # Get URLs from file
    if file:
        file_urls = load_urls_from_file(file)
        all_urls.extend(file_urls)

    if interactive or (not urls and not file):
        rprint("[bold]Enter story URLs, one per line[/bold] (Enter a blank line to finish):")
        try:
            while True:
                line = Prompt.ask("URL", default="")
                if not line.strip():
                    break  # Exit the loop when an empty line is entered
                all_urls.append(line.strip())
        except (EOFError, KeyboardInterrupt):
            console.print()  # Add a newline after EOF

    # Check if we have any URLs to download
    if not all_urls:
        console.print("[bold yellow]No URLs provided for download![/bold yellow]")
        console.print("Use -u/--url to specify URLs or -f/--file to load from a file.")
        return

    # Call the core download function
    perform_download(all_urls, output_folder)


@app.command("extract")
def extract_story_urls(
        urls: List[str] = typer.Option(None, "--url", "-u", help="One or more URLs to extract from"),
        file: Optional[str] = typer.Option(None, "--file", "-f", help="File containing URLs to extract from"),
        output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file to save extracted URLs"),
        download: bool = typer.Option(False, "--download", "-d", help="Download extracted stories immediately"),
        interactive: bool = typer.Option(False, "--interactive", "-i", help="Enter URLs interactively"),
):
    """
    Extract story URLs from listing pages (author profiles, series pages, etc).

    Examples:
        fanfic extract -u https://archiveofourown.org/users/username/works
        fanfic extract -f sites.txt -o extracted_urls.txt
        fanfic extract -u https://archiveofourown.org/series/12345 -d
    """
    show_app_header()

    all_urls = []

    # Get URLs from command line arguments
    if urls:
        all_urls.extend(urls)

    # Get URLs from file
    if file:
        file_urls = load_urls_from_file(file)
        all_urls.extend(file_urls)

    # If interactive or no URLs provided, prompt for input
    if interactive or (not urls and not file):
        rprint("[bold]Enter URLs to extract from, one per line[/bold] (Enter a blank line to finish):")
        try:
            while True:
                line = Prompt.ask("URL", default="")
                if not line.strip():
                    break  # Exit the loop when an empty line is entered
                all_urls.append(line.strip())
        except (EOFError, KeyboardInterrupt):
            console.print()  # Add a newline after EOF

    # Check if we have any URLs to extract from
    if not all_urls:
        console.print("[bold yellow]No URLs provided for extraction![/bold yellow]")
        console.print("Use -u/--url to specify URLs or -f/--file to load from a file.")
        return

    all_extracted_urls = []

    # Show extraction information
    console.print(f"[bold]Extracting story links from [cyan]{len(all_urls)}[/cyan] sources[/bold]")

    # Set up progress display
    with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}[/bold blue]"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            expand=True
    ) as progress:

        extract_task = progress.add_task("[bold]Extracting URLs...[/bold]", total=len(all_urls))

        # Process each URL
        for source_url in all_urls:
            # Update progress description to show current URL
            progress.update(extract_task, description=f"[bold]Extracting from:[/bold] {source_url.split('/')[-2]}/...")

            try:
                # Run FanFicFare to extract story URLs
                result = run_fanficfare(["-o", "is_adult=true", "-l", source_url])

                if result.returncode == 0:
                    # Process extracted URLs
                    extracted_urls = [url.strip() for url in result.stdout.split("\n") if url.strip()]
                    all_extracted_urls.extend(extracted_urls)

            except Exception as e:
                pass  # Errors will be reflected in the final count

            # Update progress
            progress.advance(extract_task)

    # Show extraction summary
    if all_extracted_urls:
        console.print(
            f"[bold green]✓[/bold green] Extracted [bold]{len(all_extracted_urls)}[/bold] stories from {len(all_urls)} sources")

        # Display sample of extracted URLs
        if len(all_extracted_urls) > 0:
            sample_count = min(5, len(all_extracted_urls))
            sample_table = Table(title="Sample of Extracted URLs", box=ROUNDED)
            sample_table.add_column("URL", style="cyan")

            for i in range(sample_count):
                sample_table.add_row(all_extracted_urls[i])

            if len(all_extracted_urls) > sample_count:
                sample_table.add_row(f"... and {len(all_extracted_urls) - sample_count} more")

            console.print(sample_table)
    else:
        console.print("[bold red]✗[/bold red] No story URLs extracted")

    # Save to file if output specified
    if output and all_extracted_urls:
        save_urls_to_file(all_extracted_urls, output)

    # Download extracted stories if requested
    if download and all_extracted_urls:
        if Confirm.ask(f"Do you want to download all {len(all_extracted_urls)} extracted stories?"):
            console.print()  # Add newline for readability
            # Call the shared download function directly instead of the command
            perform_download(all_extracted_urls)


@app.command("update")
def update_epub_files(
        folder: Optional[str] = typer.Option(None, "--folder", "-f", help="Folder path to update EPUB files from"),
        recursive: bool = typer.Option(True, "--recursive", "-r", help="Search subfolders recursively"),
        force: bool = typer.Option(False, "--force", help="Skip confirmation prompt"),
):
    """
    Update existing EPUB files using FanFicFare's --update-epub feature.

    This command will find all EPUB files in the specified folder (or default download folder)
    and attempt to update them with the latest versions from their original sources.

    Examples:
        fanfic update
        fanfic update -f /path/to/epub/folder
        fanfic update -f /path/to/folder --force
        fanfic update --no-recursive  # Only check the main folder, not subfolders
    """
    show_app_header()

    # Use provided folder or default to USER_FOLDER
    target_folder = folder if folder else USER_FOLDER

    # Validate folder exists
    if not os.path.exists(target_folder):
        console.print(f"[bold red]✗[/bold red] Folder does not exist: [blue]{target_folder}[/blue]")
        return

    if not os.path.isdir(target_folder):
        console.print(f"[bold red]✗[/bold red] Path is not a directory: [blue]{target_folder}[/blue]")
        return

    console.print(f"[bold]Searching for EPUB files in:[/bold] [blue]{target_folder}[/blue]")

    # Find all EPUB files
    if recursive:
        epub_files = find_epub_files(target_folder)
        console.print(f"[bold]Found [cyan]{len(epub_files)}[/cyan] EPUB files (including subfolders)[/bold]")
    else:
        epub_files = glob.glob(os.path.join(target_folder, "*.epub"))
        console.print(f"[bold]Found [cyan]{len(epub_files)}[/cyan] EPUB files in main folder[/bold]")

    if not epub_files:
        console.print("[bold yellow]No EPUB files found to update![/bold yellow]")
        return

    # Show sample of files to be updated
    if len(epub_files) > 0:
        sample_count = min(5, len(epub_files))
        sample_table = Table(title="EPUB Files to Update", box=ROUNDED)
        sample_table.add_column("Filename", style="green")
        sample_table.add_column("Location", style="blue")

        for i in range(sample_count):
            file_path = epub_files[i]
            filename = os.path.basename(file_path)
            location = os.path.dirname(file_path)
            sample_table.add_row(filename, location)

        if len(epub_files) > sample_count:
            sample_table.add_row(f"... and {len(epub_files) - sample_count} more files", "...")

        console.print(sample_table)

    # Confirmation prompt unless force flag is used
    if not force:
        if not Confirm.ask(f"Do you want to update all {len(epub_files)} EPUB files?"):
            console.print("[yellow]Update cancelled.[/yellow]")
            return

    console.print(f"[bold]Updating [cyan]{len(epub_files)}[/cyan] EPUB files...[/bold]")

    # Set up progress display
    with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}[/bold blue]"),
            BarColumn(bar_width=40),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            expand=True
    ) as progress:

        update_task = progress.add_task("[bold]Updating EPUB files...[/bold]", total=len(epub_files))
        success_count = 0
        error_count = 0
        skipped_count = 0
        errors_detail = []

        # Process each EPUB file
        for epub_file in epub_files:
            filename = os.path.basename(epub_file)
            file_dir = os.path.dirname(epub_file)

            # Update progress description to show current file
            progress.update(update_task, description=f"[bold]Updating:[/bold] {filename[:50]}...")

            try:
                # Run FanFicFare with --update-epub
                result = run_fanficfare(["-o", "is_adult=true", "--update-epub", epub_file], working_dir=file_dir)

                if result.returncode == 0:
                    # Check if the output indicates success, skip, or update
                    output_lower = result.stdout.lower()
                    if "already up to date" in output_lower or "no update needed" in output_lower:
                        skipped_count += 1
                    else:
                        success_count += 1
                else:
                    error_count += 1
                    # Store error details for later display
                    error_msg = result.stderr.strip() if result.stderr else "Unknown error"
                    errors_detail.append((filename, error_msg))

            except Exception as e:
                error_count += 1
                errors_detail.append((filename, str(e)))

            # Update progress
            progress.advance(update_task)

    # Show update summary
    console.print(f"\n[bold]Update Summary:[/bold]")

    if success_count > 0:
        console.print(f"[bold green]✓[/bold green] Successfully updated [bold]{success_count}[/bold] files")

    if skipped_count > 0:
        console.print(f"[bold yellow]⏭[/bold yellow] Skipped [bold]{skipped_count}[/bold] files (already up to date)")

    if error_count > 0:
        console.print(f"[bold red]✗[/bold red] Failed to update [bold]{error_count}[/bold] files")

        # Show error details if there are errors and not too many
        if len(errors_detail) > 0 and len(errors_detail) <= 10:
            console.print("\n[bold red]Error Details:[/bold red]")
            error_table = Table(box=ROUNDED)
            error_table.add_column("File", style="red")
            error_table.add_column("Error", style="yellow")

            for filename, error_msg in errors_detail:
                # Truncate long error messages
                if len(error_msg) > 100:
                    error_msg = error_msg[:97] + "..."
                error_table.add_row(filename, error_msg)

            console.print(error_table)
        elif len(errors_detail) > 10:
            console.print(f"[dim]Too many errors to display ({len(errors_detail)} total)[/dim]")

    # Ask if user wants to open the folder
    if success_count > 0 and Confirm.ask("Open download folder?"):
        if folder:
            open_folder(target_folder)
        else:
            open_download_folder()


@app.command("list")
def list_downloaded_files(
        detailed: bool = typer.Option(False, "--detailed", "-d", help="Show detailed file information"),
        sort_by: str = typer.Option("name", "--sort", "-s", help="Sort by: name, date, size"),
):
    """
    List downloaded stories in the download folder.

    Examples:
        fanfic list
        fanfic list -d
        fanfic list -s size
    """
    show_app_header()

    # Find all .epub files in the download folder
    epub_files = glob.glob(os.path.join(USER_FOLDER, "*.epub"))

    if not epub_files:
        console.print(f"[bold yellow]No EPUB files found in:[/bold yellow] {USER_FOLDER}")
        return

    # Sort files based on sorting option
    if sort_by.lower() == "name":
        epub_files.sort(key=lambda path: os.path.basename(path).lower())
    elif sort_by.lower() == "date":
        epub_files.sort(key=lambda path: os.path.getmtime(path), reverse=True)
    elif sort_by.lower() == "size":
        epub_files.sort(key=lambda path: os.path.getsize(path), reverse=True)

    # Create a table to display the files
    table = Table(title=f"Downloaded Stories in {USER_FOLDER}", box=ROUNDED)

    # Add columns based on detail level
    table.add_column("#", style="cyan", no_wrap=True)
    table.add_column("Filename", style="green")
    table.add_column("Size", style="magenta")
    table.add_column("Date", style="yellow")

    if detailed:
        table.add_column("Path", style="blue")

    # Add rows for each file
    for i, file_path in enumerate(epub_files):
        file_info = os.stat(file_path)
        file_name = os.path.basename(file_path)
        file_size = format_filesize(file_info.st_size)

        # Format creation date based on platform
        if sys.platform == 'win32':
            creation_date = datetime.fromtimestamp(int(file_info.st_ctime)).strftime("%Y-%m-%d %H:%M")
        else:
            creation_date = datetime.fromtimestamp(int(file_info.st_mtime)).strftime("%Y-%m-%d %H:%M")

        # Add row to table
        if detailed:
            table.add_row(str(i + 1), file_name, file_size, creation_date, file_path)
        else:
            table.add_row(str(i + 1), file_name, file_size, creation_date)

    # Print the table
    console.print(table)

    # Show total count and size
    total_size = sum(os.path.getsize(file) for file in epub_files)
    console.print(f"[bold]Total:[/bold] {len(epub_files)} files, {format_filesize(total_size)}")

    # Ask if user wants to open the folder
    if Confirm.ask("Open download folder?"):
        open_download_folder()


@app.command("settings")
def manage_settings(
        folder: Optional[str] = typer.Option(None, "--folder", "-f", help="Change download folder location"),
        open_folder: bool = typer.Option(False, "--open", "-o", help="Open download folder in file explorer"),
):
    """
    View and manage application settings.

    Examples:
        fanfic settings
        fanfic settings -f /path/to/download/folder
        fanfic settings -o
    """
    show_app_header()

    # Create settings display
    settings_panel = Panel.fit(
        f"[bold]Current Settings[/bold]\n\n"
        f"[bold]Download Folder:[/bold] [blue]{USER_FOLDER}[/blue]\n"
        f"[bold]Config File:[/bold] [blue]{os.path.abspath(CONFIG_FILE)}[/blue]",
        title="Settings",
        border_style="green"
    )
    console.print(settings_panel)

    # If folder option is provided, change the download location
    if folder:
        change_download_location(folder)

    # If open option is provided, open the download folder
    if open_folder:
        open_download_folder()

    # If no options provided, show interactive settings menu
    if not folder and not open_folder:
        console.print("\n[bold]Available Actions:[/bold]")
        console.print("1. Change download folder")
        console.print("2. Open download folder")
        console.print("3. Exit")

        choice = Prompt.ask("Select an option", choices=["1", "2", "3"], default="3")

        if choice == "1":
            folder_path = Prompt.ask("Enter new download folder path")
            if folder_path:
                change_download_location(folder_path)
        elif choice == "2":
            open_download_folder()


def change_download_location(new_folder):
    """Change and save the download folder location"""
    global USER_FOLDER

    try:
        # Create folder if it doesn't exist
        os.makedirs(new_folder, exist_ok=True)

        # Update global variable and save to config
        USER_FOLDER = new_folder
        save_config(USER_FOLDER)

        console.print(f"[bold green]✓[/bold green] Download location changed to: [blue] {USER_FOLDER} [/blue] ")
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Error changing download location: {str(e)}")


def open_download_folder():
    """Open the download folder in the file explorer"""
    open_folder(USER_FOLDER)


def open_folder(folder_path):
    """Open a specific folder in the file explorer"""
    try:
        if sys.platform == 'win32':
            os.startfile(folder_path)
        elif sys.platform == 'darwin':  # macOS
            subprocess.run(['open', folder_path], check=True)
        else:  # Linux
            subprocess.run(['xdg-open', folder_path], check=True)

        console.print(f"[green]✓[/green] Opened folder: [blue]{folder_path}[/blue]")
    except Exception as e:
        console.print(f"[bold red]✗[/bold red] Could not open folder: {str(e)}")


@app.callback()
def main():
    """
    FanFic Downloader CLI - Download fan fiction stories from various sites

    This application uses FanFicFare to download stories from fan fiction sites.
    """
    pass  # This function will be called before any of the commands


@app.command()
def help():
    """
    Show detailed help and examples for all commands.
    """
    show_app_header()

    help_text = """
    # FanFic Downloader CLI

    A command-line tool to download fan fiction stories from various sites
    using FanFicFare as the backend.

    ## Commands

    ### Download Stories

    Download stories from specific URLs.

    ```
    fanfic download -u https://example.com/story1 https://example.com/story2
    fanfic download -f url_list.txt
    fanfic download -i  # Interactive mode
    ```

    ### Extract URLs

    Extract story URLs from listing pages, like author profiles or series pages.

    ```
    fanfic extract -u https://example.com/author_page
    fanfic extract -f sources.txt -o extracted_urls.txt
    fanfic extract -u https://example.com/series/123 -d  # Extract and download
    ```

    ### Update EPUB Files

    Update existing EPUB files with their latest versions.

    ```
    fanfic update  # Update all EPUBs in default folder
    fanfic update -f /path/to/epub/folder  # Update EPUBs in specific folder
    fanfic update --no-recursive  # Only check main folder, not subfolders
    fanfic update --force  # Skip confirmation prompt
    ```

    ### List Downloaded Files

    View stories that have been downloaded.

    ```
    fanfic list  # Simple list
    fanfic list -d  # Detailed view
    fanfic list -s size  # Sort by size
    ```

    ### Manage Settings

    View and modify application settings.

    ```
    fanfic settings  # View current settings
    fanfic settings -f /path/to/download/folder  # Change download folder
    fanfic settings -o  # Open download folder
    ```

    ## Getting Started

    1. Make sure you have FanFicFare installed:
       ```
       pip install fanficfare
       ```

    2. Download a story:
       ```
       fanfic download -u https://archiveofourown.org/works/12345678
       ```

    3. List your downloaded stories:
       ```
       fanfic list
       ```

    4. Update your existing stories:
       ```
       fanfic update
       ```
    """

    md = Markdown(help_text)
    console.print(md)


def run():
    """Entry point for the application."""
    app()


if __name__ == "__main__":
    run()