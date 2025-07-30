import click
import uvicorn
import os
import webbrowser
import threading
import time
from pyfiglet import Figlet
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.box import ROUNDED

console = Console()

def print_branding():
    figlet = Figlet(font="slant")
    ascii_logo = figlet.renderText("VirtueRed")
    
    # Pre-process the ASCII logo to color it
    # Color the V and part of the logo in purple
    colored_logo = Text()
    for i, line in enumerate(ascii_logo.split('\n')):
        if i > 0:  # Skip first empty line if any
            colored_line = Text()
            for j, char in enumerate(line):
                if char != ' ':
                    # Apply magenta to the left half (approximately the "Virtue" part)
                    if j < len(line) * 0.58:  # Adjust this ratio as needed
                        colored_line.append(char, style="bold magenta")
                    else:
                        colored_line.append(char, style="bold red")
                else:
                    colored_line.append(char)
            colored_logo.append(colored_line)
            colored_logo.append("\n")
    
    # Create colored brand name for the text below
    brand = Text()
    brand.append("Virtue", style="bold magenta")
    brand.append("Red", style="bold red")
    
    # Create panel with the combined content
    tagline = Text("✨ Elevate your AI safety and security with ", style="bold")
    tagline.append(brand)
    
    # Combine colored_logo and tagline into a single Text object
    combined_text = Text("\n")
    combined_text.append(colored_logo)
    combined_text.append("\n")
    combined_text.append(tagline)
    
    panel = Panel(
        combined_text,
        box=ROUNDED,
        border_style="bright_blue",
        padding=(0, 2),
        width=60
    )
    
    console.print(panel)
    
def show_progress_bar():
    with Progress(
        TextColumn("🚀 [bold cyan]Initializing web service...[/]"),
        BarColumn(bar_width=30, complete_style="red"),
        TextColumn("[bold]{task.percentage:>3.0f}%"),
        console=console,
        expand=False
    ) as progress:
        task = progress.add_task("", total=100)
        for _ in range(100):
            time.sleep(0.02)
            progress.update(task, advance=1)

def display_service_info(port, backend_url):
    # Simple service information messages
    console.print("")
    console.print("✅ [bold green]Status:[/] Running")
    console.print(f"🌐 [bold green]Web UI:[/] [link=http://localhost:{port}]http://localhost:{port}[/link]")
    console.print(f"🔌 [bold cyan]Backend:[/] {backend_url}")
    console.print("💡 [bold yellow]Exit:[/] Press Ctrl+C to quit")
    console.print("")

def start_webui_server(backend_url: str, host: str, port: int, open_browser_flag: bool = True):
    """Starts the FastAPI server for the web UI."""
    os.environ["API_URL"] = backend_url

    print_branding()
    show_progress_bar()
    display_service_info(port, backend_url)

    if open_browser_flag:
        # Open browser in a separate thread
        def open_browser_task():
            time.sleep(1.0) # Give server a moment to start
            try:
                webbrowser.open(f"http://localhost:{port}") # Use localhost for browser opening
            except Exception as e:
                console.print(f"[yellow]Could not automatically open browser: {e}[/yellow]")

        threading.Thread(target=open_browser_task, daemon=True).start()

    # Run the server using uvicorn
    try:
        console.print(f"Starting server on {host}:{port}...")
        uvicorn.run(
            "virtuered.webui.server:app", # IMPORTANT: Updated path
            host=host,
            port=port,
            log_level="warning",
        )
    except OSError as e:
        if "Address already in use" in str(e):
            console.print(f"[bold red]Error: Port {port} is already in use.[/bold red]")
            console.print("[yellow]Try stopping the existing process or use a different port with --port option.[/yellow]")
        else:
            console.print(f"[bold red]Failed to start server: {e}[/bold red]")
    except KeyboardInterrupt:
        console.print("\n[bold magenta]Shutting down VirtueRed Web UI... Goodbye![/]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")
        
@click.group()
def webui_entry_point():
    """VirtueRed Web UI commands (primarily for internal use now)."""
    pass

@webui_entry_point.command(name="serve", help="Launch the VirtueRed Web UI (now typically launched via 'virtuered webui').")
@click.option('--backend-url', default="http://localhost:4401", help="The full URL of your VirtueRed backend")
@click.option('--host', default="0.0.0.0", help="Host for the web UI server")
@click.option('--port', default=3000, type=int, help="Port for the web UI server")
@click.option('--no-browser', is_flag=True, default=False, help="Don't automatically open the web browser")

def serve_command(backend_url, host, port, no_browser):
    """Click command wrapper for starting the server."""
    start_webui_server(backend_url, host, port, open_browser_flag=not no_browser)
