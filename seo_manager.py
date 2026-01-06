#!/usr/bin/env python3
"""
SEO Toolkit Manager
A unified command-line interface for managing and executing SEO research tools.
"""

import sys
import os
import json
from typing import Optional, Dict, Any

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")


# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


class ConfigManager:
    """Manages configuration for all tools."""
    
    def __init__(self):
        self.config_file = 'seo_config.json'
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        # Default configuration
        return {
            'api_key': os.environ.get('HASDATA_API_KEY', ''),
            'google_suggest_harvester': {
                'base_keyword': 'coffee',
                'max_depth': 2,
                'max_workers': 1
            },
            'trends_breakout_analyzer': {
                'seed_topic': 'Coffee',
                'geo': 'US',
                'date': 'now 7-d'
            },
            'paa_tree_builder': {
                'root_keyword': 'coffee',
                'max_depth': 2
            },
            'serp_intent_classifier': {
                'keyword': 'instant coffee',
                'device_type': 'desktop',
                'location': 'United States'
            },
            'serp_similarity_matrix': {
                'keywords': [
                    'health benefits of coffee',
                    'benefits of coffee for men',
                    'benefits of coffee for women'
                ]
            },
            'content_gap_analyzer': {
                'target_keyword': 'health benefits of decaf coffee',
                'my_url': 'https://www.telegraph.co.uk/health-fitness/diet/nutrition/is-decaf-coffee-good-or-bad-for-you/',
                'top_n_competitors': 10
            },
            'ai_overview_monitor': {
                'target_domain': 'webmd.com',
                'keywords': [
                    'health benefits of coffee',
                    'benefits of coffee for men',
                    'benefits of coffee for women'
                ]
            }
        }
    
    def save_config(self):
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            print(f"{Colors.GREEN}✓ Configuration saved successfully!{Colors.END}")
        except Exception as e:
            print(f"{Colors.FAIL}✗ Error saving configuration: {e}{Colors.END}")
    
    def get_api_key(self) -> str:
        """Get API key from config or environment."""
        return self.config.get('api_key') or os.environ.get('HASDATA_API_KEY', '')
    
    def set_api_key(self, api_key: str):
        """Set API key in configuration."""
        self.config['api_key'] = api_key
        self.save_config()
    
    def get_tool_config(self, tool_name: str) -> Dict[str, Any]:
        """Get configuration for specific tool."""
        return self.config.get(tool_name, {})
    
    def update_tool_config(self, tool_name: str, new_config: Dict[str, Any]):
        """Update configuration for specific tool."""
        self.config[tool_name] = new_config
        self.save_config()


def print_banner():
    """Display the toolkit banner."""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════╗
║           SEO Research Toolkit Manager v1.0               ║
║           Powered by HasData API                          ║
╚═══════════════════════════════════════════════════════════╝
{Colors.END}
    """
    print(banner)


def print_menu():
    """Display the main menu."""
    menu = f"""
{Colors.BOLD}Available Tools:{Colors.END}

{Colors.GREEN}[1]{Colors.END} Google Suggest Harvester
    └─ Extract long-tail keywords using Google's autocomplete
    
{Colors.GREEN}[2]{Colors.END} Trends Breakout Analyzer
    └─ Identify rising and top related queries from Google Trends
    
{Colors.GREEN}[3]{Colors.END} PAA Tree Builder
    └─ Build hierarchical "People Also Ask" question trees
    
{Colors.GREEN}[4]{Colors.END} SERP Intent Classifier
    └─ Classify search intent based on SERP composition
    
{Colors.GREEN}[5]{Colors.END} SERP Similarity Matrix
    └─ Analyze overlap between related keyword SERPs
    
{Colors.GREEN}[6]{Colors.END} Content Gap Analyzer
    └─ Find missing keywords/phrases vs competitors
    
{Colors.GREEN}[7]{Colors.END} AI Overview Monitor
    └─ Track domain visibility in Google's AI Overviews

{Colors.BLUE}[8]{Colors.END} Configure Tool Settings
    └─ Customize parameters for each tool

{Colors.BLUE}[9]{Colors.END} Configure API Key
    └─ Set or update your HasData API key

{Colors.WARNING}[0]{Colors.END} Exit

{Colors.BOLD}═══════════════════════════════════════════════════════════{Colors.END}
    """
    print(menu)


def configure_api_key(config_manager: ConfigManager):
    """Interactive API key configuration."""
    print(f"\n{Colors.BOLD}API Key Configuration{Colors.END}")
    print("─" * 50)
    
    current_key = config_manager.get_api_key()
    if current_key:
        masked = current_key[:8] + "..." + current_key[-4:] if len(current_key) > 12 else "***"
        print(f"Current API key: {masked}")
        print("\nEnter new key (or press Enter to keep current):")
    else:
        print("No API key found. Please enter your HasData API key:")
    
    new_key = input("> ").strip()
    
    if new_key:
        config_manager.set_api_key(new_key)
        os.environ['HASDATA_API_KEY'] = new_key
    elif not current_key:
        print(f"{Colors.WARNING}⚠ No API key configured. Tools will not work.{Colors.END}")


def configure_tool_settings(config_manager: ConfigManager):
    """Interactive tool settings configuration."""
    tools_menu = f"""
{Colors.BOLD}Configure Tool Settings:{Colors.END}

{Colors.GREEN}[1]{Colors.END} Google Suggest Harvester (keyword, depth, workers)
{Colors.GREEN}[2]{Colors.END} Trends Breakout Analyzer (topic, geo, date range)
{Colors.GREEN}[3]{Colors.END} PAA Tree Builder (keyword, depth)
{Colors.GREEN}[4]{Colors.END} SERP Intent Classifier (keyword, device, location)
{Colors.GREEN}[5]{Colors.END} SERP Similarity Matrix (keyword list)
{Colors.GREEN}[6]{Colors.END} Content Gap Analyzer (keyword, URL, competitors)
{Colors.GREEN}[7]{Colors.END} AI Overview Monitor (domain, keyword list)
{Colors.BLUE}[0]{Colors.END} Back to main menu
    """
    
    while True:
        print("\n" + "─" * 60)
        print(tools_menu)
        choice = input(f"{Colors.BOLD}Select tool to configure [0-7]:{Colors.END} ").strip()
        
        if choice == '0':
            break
        elif choice == '1':
            configure_suggest_harvester(config_manager)
        elif choice == '2':
            configure_trends_analyzer(config_manager)
        elif choice == '3':
            configure_paa_builder(config_manager)
        elif choice == '4':
            configure_intent_classifier(config_manager)
        elif choice == '5':
            configure_similarity_matrix(config_manager)
        elif choice == '6':
            configure_gap_analyzer(config_manager)
        elif choice == '7':
            configure_overview_monitor(config_manager)
        else:
            print(f"{Colors.FAIL}✗ Invalid choice{Colors.END}")


def configure_suggest_harvester(config_manager: ConfigManager):
    """Configure Google Suggest Harvester settings."""
    print(f"\n{Colors.BOLD}Google Suggest Harvester Configuration{Colors.END}")
    config = config_manager.get_tool_config('google_suggest_harvester')
    
    print(f"\nCurrent settings:")
    print(f"  Base keyword: {config['base_keyword']}")
    print(f"  Max depth: {config['max_depth']}")
    print(f"  Max workers: {config['max_workers']}")
    
    keyword = input(f"\nBase keyword [{config['base_keyword']}]: ").strip()
    depth = input(f"Max depth (1-3) [{config['max_depth']}]: ").strip()
    workers = input(f"Max workers (1-1500) [{config['max_workers']}]: ").strip()
    
    if keyword:
        config['base_keyword'] = keyword
    if depth and depth.isdigit():
        config['max_depth'] = int(depth)
    if workers and workers.isdigit():
        config['max_workers'] = int(workers)
    
    config_manager.update_tool_config('google_suggest_harvester', config)


def configure_trends_analyzer(config_manager: ConfigManager):
    """Configure Trends Breakout Analyzer settings."""
    print(f"\n{Colors.BOLD}Trends Breakout Analyzer Configuration{Colors.END}")
    config = config_manager.get_tool_config('trends_breakout_analyzer')
    
    print(f"\nCurrent settings:")
    print(f"  Seed topic: {config['seed_topic']}")
    print(f"  Geo: {config['geo']}")
    print(f"  Date range: {config['date']}")
    
    topic = input(f"\nSeed topic [{config['seed_topic']}]: ").strip()
    geo = input(f"Geo (country code) [{config['geo']}]: ").strip()
    date = input(f"Date range (e.g., 'now 7-d', 'today 12-m') [{config['date']}]: ").strip()
    
    if topic:
        config['seed_topic'] = topic
    if geo:
        config['geo'] = geo.upper()
    if date:
        config['date'] = date
    
    config_manager.update_tool_config('trends_breakout_analyzer', config)


def configure_paa_builder(config_manager: ConfigManager):
    """Configure PAA Tree Builder settings."""
    print(f"\n{Colors.BOLD}PAA Tree Builder Configuration{Colors.END}")
    config = config_manager.get_tool_config('paa_tree_builder')
    
    print(f"\nCurrent settings:")
    print(f"  Root keyword: {config['root_keyword']}")
    print(f"  Max depth: {config['max_depth']}")
    
    keyword = input(f"\nRoot keyword [{config['root_keyword']}]: ").strip()
    depth = input(f"Max depth (1-3) [{config['max_depth']}]: ").strip()
    
    if keyword:
        config['root_keyword'] = keyword
    if depth and depth.isdigit():
        config['max_depth'] = int(depth)
    
    config_manager.update_tool_config('paa_tree_builder', config)


def configure_intent_classifier(config_manager: ConfigManager):
    """Configure SERP Intent Classifier settings."""
    print(f"\n{Colors.BOLD}SERP Intent Classifier Configuration{Colors.END}")
    config = config_manager.get_tool_config('serp_intent_classifier')
    
    print(f"\nCurrent settings:")
    print(f"  Keyword: {config['keyword']}")
    print(f"  Device type: {config['device_type']}")
    print(f"  Location: {config['location']}")
    
    keyword = input(f"\nKeyword [{config['keyword']}]: ").strip()
    device = input(f"Device type (desktop/mobile) [{config['device_type']}]: ").strip()
    location = input(f"Location [{config['location']}]: ").strip()
    
    if keyword:
        config['keyword'] = keyword
    if device:
        config['device_type'] = device.lower()
    if location:
        config['location'] = location
    
    config_manager.update_tool_config('serp_intent_classifier', config)


def configure_similarity_matrix(config_manager: ConfigManager):
    """Configure SERP Similarity Matrix settings."""
    print(f"\n{Colors.BOLD}SERP Similarity Matrix Configuration{Colors.END}")
    config = config_manager.get_tool_config('serp_similarity_matrix')
    
    print(f"\nCurrent keywords:")
    for i, kw in enumerate(config['keywords'], 1):
        print(f"  {i}. {kw}")
    
    print(f"\nEnter keywords (one per line, empty line to finish):")
    keywords = []
    while True:
        kw = input(f"Keyword {len(keywords) + 1}: ").strip()
        if not kw:
            break
        keywords.append(kw)
    
    if keywords:
        config['keywords'] = keywords
        config_manager.update_tool_config('serp_similarity_matrix', config)
    else:
        print(f"{Colors.WARNING}No changes made{Colors.END}")


def configure_gap_analyzer(config_manager: ConfigManager):
    """Configure Content Gap Analyzer settings."""
    print(f"\n{Colors.BOLD}Content Gap Analyzer Configuration{Colors.END}")
    config = config_manager.get_tool_config('content_gap_analyzer')
    
    print(f"\nCurrent settings:")
    print(f"  Target keyword: {config['target_keyword']}")
    print(f"  Your URL: {config['my_url']}")
    print(f"  Top N competitors: {config['top_n_competitors']}")
    
    keyword = input(f"\nTarget keyword [{config['target_keyword']}]: ").strip()
    url = input(f"Your URL [{config['my_url']}]: ").strip()
    top_n = input(f"Top N competitors (1-20) [{config['top_n_competitors']}]: ").strip()
    
    if keyword:
        config['target_keyword'] = keyword
    if url:
        config['my_url'] = url
    if top_n and top_n.isdigit():
        config['top_n_competitors'] = int(top_n)
    
    config_manager.update_tool_config('content_gap_analyzer', config)


def configure_overview_monitor(config_manager: ConfigManager):
    """Configure AI Overview Monitor settings."""
    print(f"\n{Colors.BOLD}AI Overview Monitor Configuration{Colors.END}")
    config = config_manager.get_tool_config('ai_overview_monitor')
    
    print(f"\nCurrent settings:")
    print(f"  Target domain: {config['target_domain']}")
    print(f"  Keywords: {len(config['keywords'])} keywords")
    
    domain = input(f"\nTarget domain [{config['target_domain']}]: ").strip()
    
    if domain:
        config['target_domain'] = domain
    
    print(f"\nEnter keywords (one per line, empty line to finish):")
    keywords = []
    while True:
        kw = input(f"Keyword {len(keywords) + 1}: ").strip()
        if not kw:
            break
        keywords.append(kw)
    
    if keywords:
        config['keywords'] = keywords
    
    if domain or keywords:
        config_manager.update_tool_config('ai_overview_monitor', config)
    else:
        print(f"{Colors.WARNING}No changes made{Colors.END}")


def run_tool(tool_number: int, config_manager: ConfigManager):
    """Execute the selected tool with configured parameters."""
    tool_map = {
        1: ("google_suggest_harvester.py", "Google Suggest Harvester", "google_suggest_harvester"),
        2: ("trends_breakout_analyzer.py", "Trends Breakout Analyzer", "trends_breakout_analyzer"),
        3: ("paa_tree_builder.py", "PAA Tree Builder", "paa_tree_builder"),
        4: ("serp_intent_classifier.py", "SERP Intent Classifier", "serp_intent_classifier"),
        5: ("serp_similarity_matrix.py", "SERP Similarity Matrix", "serp_similarity_matrix"),
        6: ("content_gap_analyzer.py", "Content Gap Analyzer", "content_gap_analyzer"),
        7: ("ai_overview_monitor.py", "AI Overview Monitor", "ai_overview_monitor"),
    }
    
    if tool_number not in tool_map:
        print(f"{Colors.FAIL}✗ Invalid tool number{Colors.END}")
        return
    
    script_name, tool_name, config_key = tool_map[tool_number]
    
    script_path = os.path.join(SCRIPTS_DIR, script_name)

    # Check if script exists
    if not os.path.exists(script_path):
        print(f"{Colors.FAIL}✗ Error: {script_path} not found in current directory{Colors.END}")
        return
    
    # Check API key
    api_key = config_manager.get_api_key()
    if not api_key:
        print(f"{Colors.WARNING}⚠ Warning: No API key configured!{Colors.END}")
        print("Configure API key now? (y/n): ", end="")
        if input().lower() == 'y':
            configure_api_key(config_manager)
            api_key = config_manager.get_api_key()
            if not api_key:
                print(f"{Colors.FAIL}✗ Cannot proceed without API key{Colors.END}")
                return
        else:
            return
    
    # Get tool configuration
    tool_config = config_manager.get_tool_config(config_key)
    
    print(f"\n{Colors.CYAN}► Launching {tool_name}...{Colors.END}")
    print(f"{Colors.BOLD}Configuration:{Colors.END}")
    for key, value in tool_config.items():
        if isinstance(value, list):
            print(f"  {key}: {len(value)} items")
        else:
            print(f"  {key}: {value}")
    print("─" * 50)
    
    # Execute the tool script with injected configuration
    try:
        # Read the script
        with open(script_path, 'r') as f:
            script_content = f.read()
        
        # Prepare execution environment
        exec_globals = {
            '__name__': '__main__',
            'API_KEY': api_key,
            **tool_config  # Inject all tool-specific config as global variables
        }
        
        # Execute
        exec(script_content, exec_globals)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠ Tool interrupted by user{Colors.END}")
    except Exception as e:
        print(f"{Colors.FAIL}✗ Error executing tool: {e}{Colors.END}")
        import traceback
        traceback.print_exc()
    
    print(f"\n{Colors.CYAN}► Tool execution completed{Colors.END}")
    input("\nPress Enter to return to main menu...")


def interactive_mode(config_manager: ConfigManager):
    """Run the toolkit in interactive mode."""
    while True:
        os.system('clear' if os.name == 'posix' else 'cls')
        print_banner()
        print_menu()
        
        try:
            choice = input(f"{Colors.BOLD}Select a tool [0-9]:{Colors.END} ").strip()
            
            if choice == '0':
                print(f"\n{Colors.CYAN}Thank you for using SEO Toolkit!{Colors.END}\n")
                sys.exit(0)
            elif choice == '9':
                configure_api_key(config_manager)
                input("\nPress Enter to continue...")
            elif choice == '8':
                configure_tool_settings(config_manager)
            elif choice.isdigit() and 1 <= int(choice) <= 7:
                run_tool(int(choice), config_manager)
            else:
                print(f"{Colors.FAIL}✗ Invalid choice. Please enter a number between 0-9.{Colors.END}")
                input("\nPress Enter to continue...")
        except KeyboardInterrupt:
            print(f"\n\n{Colors.CYAN}Thank you for using SEO Toolkit!{Colors.END}\n")
            sys.exit(0)
        except Exception as e:
            print(f"{Colors.FAIL}✗ Error: {e}{Colors.END}")
            input("\nPress Enter to continue...")


def main():
    """Main entry point."""
    config_manager = ConfigManager()
    
    # Check for command-line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            print_banner()
            print(f"""
{Colors.BOLD}Usage:{Colors.END}
  python seo_toolkit_manager.py          Run in interactive mode
  python seo_toolkit_manager.py [1-9]    Run specific tool or config
  python seo_toolkit_manager.py --help   Show this help message

{Colors.BOLD}Examples:{Colors.END}
  python seo_toolkit_manager.py          # Interactive menu
  python seo_toolkit_manager.py 1        # Run Google Suggest Harvester
  python seo_toolkit_manager.py 8        # Configure tool settings
  python seo_toolkit_manager.py 9        # Configure API key
            """)
            sys.exit(0)
        elif sys.argv[1].isdigit():
            tool_num = int(sys.argv[1])
            if tool_num == 9:
                configure_api_key(config_manager)
            elif tool_num == 8:
                configure_tool_settings(config_manager)
            elif 1 <= tool_num <= 7:
                print_banner()
                run_tool(tool_num, config_manager)
            else:
                print(f"{Colors.FAIL}✗ Invalid tool number. Use 1-9 or --help for usage.{Colors.END}")
                sys.exit(1)
        else:
            print(f"{Colors.FAIL}✗ Invalid argument. Use --help for usage information.{Colors.END}")
            sys.exit(1)
    else:
        # Run in interactive mode
        interactive_mode(config_manager)


if __name__ == "__main__":
    main()