#!/usr/bin/env python3
import argparse
import requests
import json
import re
import time
import os
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.panel import Panel
from rich import print as rprint

class VirtueRedCLI:
    def __init__(self, server_url=None):
        """
        Initialize CLI with server URL priority:
        1. Command line argument (server_url parameter)
        2. Config file
        3. Default value
        """
        config_file = Path.home() / '.virtuered' / 'config.json'
        config_url = None
    
        # Try to read from config file
        if config_file.exists():
            try:
                config = self.load_json_with_comments(config_file)
                config_url = config.get('server_url')
            except Exception as e:
                pass
        
        # Priority: command line > config file > default
        self.server_url = server_url or config_url or "http://localhost:4401"
        self.console = Console()
        # Initialize scan_config_path with default value
        self.scan_config_path = Path('scan_config.json')

    def _get_server_url(self):
        """Get current server URL"""
        return self.server_url

    def configure(self, server_url):
        """Save server configuration"""
        config_dir = Path.home() / '.virtuered'
        config_file = config_dir / 'config.json'
        
        # Create config directory if it doesn't exist
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Save configuration
        config = {'server_url': server_url}
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)
        
        # Update current instance's server_url
        self.server_url = server_url
        
        self.console.print(f"[green]Server URL configured: {server_url}[/green]")
        self.console.print("[yellow]You can override this setting with:[/yellow]")
        self.console.print(f"  - Command line: virtuered --server <url> <command>")

    def load_json_with_comments(self, file_path):
        """
        Load a JSON file that contains comments starting with '//'
        
        Args:
            file_path (str): Path to the JSON file
            
        Returns:
            dict: Parsed JSON data
        """
        
        # Read the file content
        with open(file_path, 'r') as file:
            content = file.read()
        
        # Remove single-line comments (// ...)
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # Remove empty lines
        content = '\n'.join(line for line in content.splitlines() if line.strip())
        
        # Parse and return the JSON
        return json.loads(content)

    def print_config(self):
        """Print current configuration"""
        self.console.print("\n[bold]Current Configuration:[/bold]")
        self.console.print(f"Server URL: {self.server_url}")
        
        config_file = Path.home() / '.virtuered' / 'config.json'
        if config_file.exists():
            try:
                config = self.load_json_with_comments(config_file)
                stored_url = config.get('server_url')
                if stored_url:
                    self.console.print(f"[green]Configured URL in config file: {stored_url}[/green]")
            except Exception:
                self.console.print("[red]Error reading config file[/red]")

        self.console.print("\n[bold]Override Options:[/bold]")
        self.console.print("1. Command line: virtuered --server URL <command>")
        self.console.print("2. Set default: virtuered config URL")

        
    def check_server(self):
        """Check if both the main server and client server are running and accessible"""
        try:
            # First check if main server is running
            response = requests.get(f"{self.server_url}/scan/list")
            response.raise_for_status()
            
            # Get client address from main server
            try:
                response = requests.get(f"{self.server_url}/scan/getclientaddress")
                if response.status_code == 200:
                    client_address = response.json()['client_address']
                    
                    # Now check if client server is running at that address
                    health_response = requests.get(f"{client_address}/health")
                    if health_response.status_code == 200:
                        # self.console.print(f"[green]VirtueRed system is fully operational:[/green]")
                        # # self.console.print(f"- Main server: {self.server_url}")
                        # self.console.print(f"- Client server: {client_address}")
                        return True
                return False
                    
            except requests.exceptions.RequestException:
                self.console.print("[red]Error: Client server is not accessible[/red]")
                self.console.print(f"[yellow]Client server should be running at: {client_address}[/yellow]")
                self.console.print("[yellow]Please start the client server[/yellow]")
                return False
            
        except requests.exceptions.RequestException as e:
            if "Connection refused" in str(e):
                self.console.print(f"[red]Main server is not accessible [/red]")
            else:
                self.console.print(f"[red]Server error: {str(e)}[/red]")
            return False


    def list_models(self):
        """List all available models with input/output modalities"""
        try:
            response = requests.get(f"{self.server_url}/scan/models")
            response.raise_for_status()
            models_data = response.json()
            
            if not models_data:
                self.console.print("[yellow]No models found[/yellow]")
                return

            # Create and display the table
            table = Table(title="Available Models")
            table.add_column("Index", style="blue")
            table.add_column("Model Name", style="cyan")
            table.add_column("Input Modalities", style="magenta")
            table.add_column("Output Modalities", style="green")
            table.add_column("Creation Time", style="yellow")

            for idx, model in enumerate(models_data, 1):
                input_modalities = ", ".join(model.get('input_modalities', []))
                output_modalities = ", ".join(model.get('output_modalities', []))
                table.add_row(
                    str(idx),
                    model['model_name'],
                    input_modalities,
                    output_modalities,
                    model['time']
                )

            self.console.print(table)

        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Failed to get models: {str(e)}[/red]")
            
    def read_scan_config(self):
        """Read and validate scan configuration from the config file"""
        try:
            if not self.scan_config_path.exists():
                self.console.print(f"[red]Error: Scan config file not found: {self.scan_config_path}[/red]")
                self.show_config_template()
                return None
                
            config = self.load_json_with_comments(self.scan_config_path)
            
            # Required fields
            required_fields = ['name', 'model', 'datasets']
            missing_fields = [field for field in required_fields if field not in config]
            
            if missing_fields:
                self.console.print(f"[red]Error: Missing required fields in config file: {', '.join(missing_fields)}[/red]")
                self.show_config_template()
                return None
            
            # Validate datasets format
            if not isinstance(config['datasets'], list):
                self.console.print("[red]Error: 'datasets' must be a list of objects[/red]")
                self.show_config_template()
                return None
                
            for dataset in config['datasets']:
                if not isinstance(dataset, dict) or 'name' not in dataset:
                    self.console.print("[red]Error: Each dataset must be an object with a 'name' field[/red]")
                    self.show_config_template()
                    return None
            
            return config
            
        except json.JSONDecodeError:
            self.console.print("[red]Error: Invalid JSON format in config file[/red]")
            self.show_config_template()
            return None
        except Exception as e:
            self.console.print(f"[red]Error reading config file: {str(e)}[/red]")
            self.show_config_template()
            return None

    def show_config_template(self):
        """Show the template for scan configuration"""
        self.console.print("\n[yellow]Please create a scan config file named 'scan_config.json' in the current directory with the following format:[/yellow]")
        template = '''{
    "name": "test_scan",              // Name of your scan
    "model": "together_template",      // Model to use for scanning
    "datasets": [                      // List of datasets to scan
        {
            "name": "Dataset Name",     // Name of the dataset
            "subcategories": [          // Optional: name of the subcategories
                "Subcategory Name 1",
                "Subcategory Name 2"
        ]
        }
    ],
    "extra_args": {                    // Optional additional arguments
        "modelname": "model name",
        "apikey": "your-api-key"
    }
}'''
        self.console.print(template)
        self.console.print("\n[yellow]Note: Comments (// ...) should be removed in the actual JSON file[/yellow]")
        
        # Add example command to create config file
        example_config = {
            "name": "test_scan",
            "model": "together_template",
            "datasets": [
                {"name": "EU Artificial Intelligence Act",    
                "subcategories": [          
                    "Criminal justice/Predictive policing",
                    "Persons (including murder)"
        ]}
            ],
            "extra_args": {
                "modelname": "model name",
                "apikey": "your-api-key"
            }
        }
        self.console.print("\n[yellow]You can create a template config file with:[/yellow]")
        self.console.print(f"echo '{json.dumps(example_config, indent=4)}' > scan_config.json")
        
    def init_scan(self, scan_name, model_name, datasets, extra_args=None):
        """Initialize a new scan"""
        payload = {
            "scan_name": scan_name,
            "model_name": model_name,
            "datasets": datasets,
        }
        if extra_args:
            payload["extra_args"] = extra_args

        try:
            response = requests.post(f"{self.server_url}/scan/start", json=payload)
            response.raise_for_status()
            self.console.print("[green]Scan initialized successfully[/green]")
            return True
        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Failed to initialize scan: {str(e)}[/red]")
            return False
        
    def monitor_progress(self, interval=5):
        """Monitor scan progress"""
        try:
            while True:
                response = requests.get(f"{self.server_url}/scan/progress")
                response.raise_for_status()
                scans = response.json()
                
                if not scans:  # No active scans
                    self.console.print("[green]No active scans found[/green]")
                    break

                # Check if all scans are completed
                all_completed = all(
                    scan.get('scan_percentage', 0) >= 100 or 
                    scan.get('scanning_status') == 'Finished' 
                    for scan in scans
                )
                
                if all_completed:
                    self.console.print("\n[green]All scans completed![/green]")
                    break

                table = Table(show_header=True, header_style="bold")
                table.add_column("Scan Name")
                table.add_column("Model")
                table.add_column("Status")
                table.add_column("Progress")
                table.add_column("Time Remaining")

                for scan in scans:
                    # Create progress bar
                    progress = min(100, scan.get('scan_percentage', 0))
                    progress_bar = "█" * int(progress / 2) + "-" * (50 - int(progress / 2))
                    
                    status_color = {
                        'Scanning': 'green',
                        'Paused': 'yellow',
                        'Initializing': 'blue'
                    }.get(scan['scanning_status'], 'white')

                    table.add_row(
                        scan['scan_name'],
                        scan['model_name'],
                        f"[{status_color}]{scan['scanning_status']}[/{status_color}]",
                        f"[{status_color}]{progress_bar} {progress:.1f}%[/{status_color}]",
                        scan.get('remaining_time', 'N/A')
                    )

                self.console.clear()
                self.console.print(table)
                self.console.print("\n[yellow]Press Ctrl+C to exit monitoring[/yellow]")
                time.sleep(interval)

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Monitoring stopped by user[/yellow]")
        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Error monitoring progress: {str(e)}[/red]")

    def get_runs(self):
        """Get list of all runs"""
        try:
            response = requests.get(f"{self.server_url}/scan/list")
            response.raise_for_status()
            # Parse the full JSON response which is a dictionary
            response_data = response.json()
            runs = response_data.get("items", []) 
            
            if not runs:
                self.console.print("[yellow]No runs found[/yellow]")
                return []

            # Create and display the table
            table = Table(title="All Runs")
            table.add_column("Index", style="blue")
            table.add_column("Scan Name", style="cyan")
            table.add_column("Model", style="magenta")
            table.add_column("Status", style="green")
            table.add_column("Time", style="yellow")
            # table.add_column("Run ID", style="white", no_wrap=False)

            for idx, run in enumerate(runs, 1):
                status_style = {
                    'Finished': 'green',
                    'Scanning': 'blue',
                    'Failed': 'red',
                    'Paused': 'yellow',
                    'Initializing': 'yellow'
                }.get(run['scanning_status'], 'white')
                
                table.add_row(
                    str(idx),
                    run['scan_name'],
                    run['model_name'],
                    f"[{status_style}]{run['scanning_status']}[/{status_style}]",
                    run['scan_time'],
                    # run['filename']
                )

            self.console.print(table)
            return runs

        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Failed to get runs: {str(e)}[/red]")
            return []

    def find_run_by_name_or_id(self, identifier):
        """Helper function to find a run by scan name or full run ID"""
        runs = self.get_runs()  # This will also display the table
        
        # Try to find by index first
        try:
            idx = int(identifier)
            if 1 <= idx <= len(runs):
                return runs[idx-1]['scan_id']
        except ValueError:
            pass

        # Try to find by scan name or full run ID
        matching_runs = [run for run in runs if 
                        run['scan_name'] == identifier or 
                        run['scan_id'] == identifier]
        
        if not matching_runs:
            self.console.print(f"[red]No run found with identifier: {identifier}[/red]")
            return None
        elif len(matching_runs) > 1:
            self.console.print(f"[yellow]Multiple runs found with name: {identifier}[/yellow]")
            self.console.print("Please use the index number from the list above.")
            return None
        else:
            return matching_runs[0]['scan_id']

    def pause_scan(self, identifier):
        """Pause a running scan"""
        run_id = self.find_run_by_name_or_id(identifier)
        if not run_id:
            return False
            
        try:
            
            response = requests.post(f"{self.server_url}/scan/pause/{run_id}")
            response.raise_for_status()
            
            self.console.print(f"[green]Successfully paused scan: {run_id}[/green]")
            return True
            
        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Failed to pause scan: {str(e)}[/red]")
            return False

    def resume_scan(self, identifier):
        """Resume a paused scan"""
        run_id = self.find_run_by_name_or_id(identifier)
        if not run_id:
            return False
            
        try:
            
            response = requests.post(f"{self.server_url}/scan/resume/{run_id}")
            response.raise_for_status()
            
            self.console.print(f"[green]Successfully resumed scan: {run_id}[/green]")
            return True
            
        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Failed to resume scan: {str(e)}[/red]")
            return False

    def get_run_summary(self, identifier):
        """Get summary for a specific run"""
        # Name mapping dictionary
        name_mapping = {
            "EU AI Act": "EU Artificial Intelligence Act",
            "White House Executive Order": "White House AI Executive Order",
            "Bias": "Bias",
            "Over Cautiousness": "Over-cautiousness",
            "hallucination": "Hallucination",
            "Regulational Harmfulness": "Societal Harmfulness",
            "Privacy": "Privacy",
            "OOD Robustness": "Robustness",
            "Finance Brand Risk": "Finance Brand Risk",
            "Medical Brand Risk": "Health Care Brand Risk",
            "Education Brand Risk": "Education Brand Risk"
        }

        def get_score_color(value):
            """Return color based on score value"""
            if value < 50:
                return "red"
            elif value < 80:
                return "yellow"
            else:
                return "green"

        run_id = self.find_run_by_name_or_id(identifier)
        if not run_id:
            return
            
        try:
            response = requests.get(f"{self.server_url}/scan/summary/{run_id}")
            response.raise_for_status()
            data = response.json()
            
            # Print model name
            self.console.print(f"\n[bold cyan]Model:[/bold cyan] {data['model_name']}\n")
            
            # Print averages with mapped names and color-coded scores
            self.console.print("[bold]Dataset Averages:[/bold]")
            for dataset, score in data['averages'].items():
                # Use the mapped name if available, otherwise use original name
                mapped_name = name_mapping.get(dataset, dataset)
                color = get_score_color(score)
                self.console.print(
                    f"{mapped_name}: [{color}]{score:.2f}%[/{color}]"
                )

            # Print subcategory averages with mapped names and color-coded scores
            self.console.print("\n[bold]Subcategory Averages:[/bold]")
            for dataset, subcats in data['averages_sub'].items():
                mapped_name = name_mapping.get(dataset, dataset)
                self.console.print(f"\n{mapped_name}:")
                for subcat, score in subcats.items():
                    color = get_score_color(score)
                    self.console.print(
                        f"  {subcat}: [{color}]{score:.2f}%[/{color}]"
                    )

            # Print risk scores
            self.console.print("\n[bold]Risk Distribution:[/bold]")
            scores = data['scores']
            total = sum(scores.values())
            for risk, count in scores.items():
                percentage = (count / total * 100) if total > 0 else 0
                color = {
                    'High Risk': 'red',
                    'Low Risk': 'yellow',
                    'No Risk': 'green',
                    'No Response': 'blue'
                }.get(risk, 'white')
                self.console.print(f"[{color}]{risk}: {count} ({percentage:.1f}%)[/{color}]")

        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Failed to get run summary: {str(e)}[/red]")

    def generate_report(self, identifier):
        """Generate and download PDF report"""
        run_id = self.find_run_by_name_or_id(identifier)
        if not run_id:
            self.console.print(f"[red]No run found with identifier: {identifier}[/red]")
            return
            
        try:
            self.console.print("[green]Start generating report ... ")
            response = requests.get(f"{self.server_url}/scan/generate_pdf/{run_id}")
            response.raise_for_status()
            # Get the current working directory
            cwd = os.getcwd()
            filename = f"report_{run_id}.pdf"
            filepath = os.path.join(cwd, filename)
            
            with open(filepath, 'wb') as f:
                f.write(response.content)
            self.console.print(f"[green]Report saved at: {filepath}[/green]")
        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Failed to generate report: {str(e)}[/red]")
            
    def delete_run(self, identifier):
        """Delete a run and its associated files"""
        run_id = self.find_run_by_name_or_id(identifier)
        if not run_id:
            return False
            
        try:
            # Ask for confirmation before deleting
            self.console.print(f"\n[yellow]Are you sure you want to delete run: {run_id}?[/yellow]")
            self.console.print("[yellow]This action cannot be undone.[/yellow]")
            confirmation = input("Type 'yes' to confirm: ")
            
            if confirmation.lower() != 'yes':
                self.console.print("[yellow]Deletion cancelled[/yellow]")
                return False
            
            response = requests.delete(f"{self.server_url}/scan/delete/{run_id}")
            response.raise_for_status()
            
            self.console.print(f"[green]Successfully deleted run: {run_id}[/green]")
            return True
            
        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Failed to delete run: {str(e)}[/red]")
            return False
        
    def refresh_custom_tests(self):
        """
        Call the refresh_sdk endpoint to refresh and display current Customized Tests.
        Extracts the 'name' field from each subcategory dictionary.
        """
        try:
            response = requests.get(f"{self.server_url}/datasets/refresh_sdk")
            response.raise_for_status()
            data = response.json()
            self.console.print("[green]Customized tests refreshed![/green]\n")

            tests = data.get("Customized Tests", [])
            if not tests:
                self.console.print("[yellow]No customized tests found.[/yellow]")
                return

            table = Table(title="Current Customized Tests")
            table.add_column("Test Name", style="cyan", justify="left")
            table.add_column("Subcategories (max 3 shown)", style="magenta", justify="left")

            for test_info in tests:
                test_name = test_info.get("name", "")
                subcats = test_info.get("subcategories", [])

                # Convert each subcategory to a string, preferring the "name" field if it's a dict.
                subcats_str_list = []
                for sc in subcats:
                    if isinstance(sc, dict) and "name" in sc:
                        subcats_str_list.append(sc["name"])
                    else:
                        subcats_str_list.append(str(sc))

                # Truncate subcategories to at most 3
                displayed_subcats = subcats_str_list[:3]
                if len(subcats_str_list) > 3:
                    displayed_subcats.append("...")

                subcategories_str = "\n".join(displayed_subcats)
                table.add_row(test_name, subcategories_str)

            self.console.print(table)

        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Failed to refresh customized tests: {str(e)}[/red]")


            
def main():
    parser = argparse.ArgumentParser(description="VirtueAI Redteaming CLI")
    parser.add_argument('--server', help='Server URL (default: http://localhost:4401)')
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Add configuration commands
    config_parser = subparsers.add_parser('config', help='Configure server settings')
    config_parser.add_argument('server_url', nargs='?', help='Server URL to configure')
    
    # Add show config command
    subparsers.add_parser('show-config', help='Show current configuration')
    
    # Add server status command
    subparsers.add_parser('status', help='Check server status')
    
    # Scan command
    # scan_parser = subparsers.add_parser('scan', help='Initialize a new scan')
    # scan_parser.add_argument('--name', required=True, help='Scan name')
    # scan_parser.add_argument('--model', required=True, help='Model name')
    # scan_parser.add_argument('--datasets', required=True, help='Datasets (JSON string)')
    # scan_parser.add_argument('--extra-args', help='Extra arguments (JSON string)')
    # scan_parser.add_argument('--monitor', action='store_true', help='Monitor progress after starting')
    scan_parser = subparsers.add_parser('scan', help='Initialize a new scan using configuration from scan_config.json in current directory')
    scan_parser.add_argument('config_file', nargs='?', default='scan_config.json',
                           help='Path to scan configuration file (default: scan_config.json)')
    # List runs command
    subparsers.add_parser('list', help='List all runs')
    
    # Add models command
    subparsers.add_parser('models', help='List all available models')
    
    # Get summary command
    summary_parser = subparsers.add_parser('summary', help='Get run summary')
    summary_parser.add_argument('identifier', 
                              help='Run identifier (can be index number, scan name, or full run ID)')
    
    # Generate report command
    report_parser = subparsers.add_parser('report', help='Generate PDF report')
    report_parser.add_argument('identifier', 
                             help='Run identifier (can be index number, scan name, or full run ID)')
    
    # Monitor command
    subparsers.add_parser('monitor', help='Monitor ongoing scans')
    
    # Pause command
    pause_parser = subparsers.add_parser('pause', help='Pause a running scan')
    pause_parser.add_argument('identifier', 
                            help='Run identifier (can be index number, scan name, or full run ID)')
    
    # Resume command
    resume_parser = subparsers.add_parser('resume', help='Resume a paused scan')
    resume_parser.add_argument('identifier', 
                             help='Run identifier (can be index number, scan name, or full run ID)')
    # delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a run and its associated files')
    delete_parser.add_argument('identifier', 
                             help='Run identifier (can be index number, scan name, or full run ID)')
    delete_parser.add_argument('--force', '-f', action='store_true',
                             help='Force deletion without confirmation')
    
    # Add a new subparser for refreshing custom tests
    subparsers.add_parser('customized-tests', help='Refresh and display customized tests')
    # --- Add the new webui subparser ---
    webui_parser = subparsers.add_parser('webui', help='Launch the VirtueRed Web UI')
    webui_parser.add_argument(
        '--host',
        default="0.0.0.0",
        help="Host address for the Web UI server (default: 0.0.0.0)"
    )
    webui_parser.add_argument(
        '--port',
        type=int,
        default=3000,
        help="Port for the Web UI server (default: 3000)"
    )
    webui_parser.add_argument(
        '--no-browser',
        action='store_true',
        default=False,
        help="Don't automatically open the web browser"
    )
    webui_parser.add_argument(
        '--backend-url',
        default=None, # Default to None, will use CLI/config value
        help="Override the backend URL specifically for the Web UI"
    )

    args = parser.parse_args()
    cli = VirtueRedCLI(args.server)

    if args.command == 'config':
        if args.server_url:
            cli.configure(args.server_url)
        else:
            cli.print_config()
    
    elif args.command == 'show-config':
        cli.print_config()
    
    elif args.command == 'status':
        cli.check_server()
    
    elif args.command == 'models':
        if cli.check_server():
            cli.list_models()
                
    elif args.command == 'scan':
        if cli.check_server():
            # Update scan_config_path based on provided argument
            cli.scan_config_path = Path(args.config_file)
            config = cli.read_scan_config()
            if config:
                cli.init_scan(
                    config['name'],
                    config['model'],
                    config['datasets'],
                    config.get('extra_args')
                )
                    
    elif args.command == 'list':
        if cli.check_server():
            cli.get_runs()
    
    elif args.command == 'summary':
        if cli.check_server():
            cli.get_run_summary(args.identifier)
    
    elif args.command == 'report':
        if cli.check_server():
            cli.generate_report(args.identifier)
    
    elif args.command == 'monitor':
        if cli.check_server():
            cli.monitor_progress()
        
    elif args.command == 'pause':
        if cli.check_server():
            cli.pause_scan(args.identifier)
        
    elif args.command == 'resume':
        if cli.check_server():
            cli.resume_scan(args.identifier)
        
    elif args.command == 'delete':
        if cli.check_server():
            cli.delete_run(args.identifier)
            
    elif args.command == 'customized-tests':
        if cli.check_server():
            cli.refresh_custom_tests()
    # --- Handle the new webui command ---
    elif args.command == 'webui':
        # --- Import the webui function HERE ---
        try:
            # Add console/sys imports if not already at the top
            from rich.console import Console 
            import sys 
            # Import the function needed only for this command
            from virtuered.webui.cli import start_webui_server
        except ImportError as e:
            # Handle cases where webui dependencies might be missing
            console = Console() # Create a console instance for error message
            console.print(f"[bold red]Error: Failed to import web UI components ({e}).[/bold red]")
            console.print("[yellow]The web UI requires additional packages.[/yellow]")
            console.print("You might need to install them:")
            # Suggest installation, possibly using extras (see step 3 below)
            console.print("  pip install virtuered[webui]") 
            # Or list explicitly:
            # console.print("  pip install fastapi 'uvicorn[standard]' click pyfiglet")
            sys.exit(1) # Exit if dependencies are missing

        # Determine the backend URL to use:
        backend_url_to_use = args.backend_url if args.backend_url else cli.server_url

        if not backend_url_to_use:
            # Use the existing cli.console if available, or create one
            error_console = getattr(cli, 'console', Console())
            error_console.print("[red]Error: Backend URL not configured or provided.[/red]")
            error_console.print("Use 'virtuered config <url>' or provide --server or --backend-url.")
            sys.exit(1)
        # Call the function to start the server
        start_webui_server(
            backend_url=backend_url_to_use,
            host=args.host,
            port=args.port,
            open_browser_flag=not args.no_browser
        )

    else:
        parser.print_help()
        
if __name__ == '__main__':
    main()