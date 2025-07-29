"""
Command-line interface for AI Voice Generator.
"""

import argparse
import getpass
import sys
import time
import webbrowser
from pathlib import Path
from threading import Timer

from .app import create_app
from .config import config
from .database import reset_database, add_sample_data


def open_browser():
    """Open the web browser to the application URL after a short delay."""
    time.sleep(1.5)  # Give the server time to start
    webbrowser.open("http://127.0.0.1:5000")


def config_command(args):
    """Handle config-related commands."""
    if args.config_action == "set":
        if not args.key:
            print("❌ Please specify a key to set (e.g., --key OPENAI_API_KEY)")
            return
        
        if args.value:
            value = args.value
        else:
            # Prompt securely for API keys
            if "API_KEY" in args.key.upper():
                value = getpass.getpass(f"Enter value for {args.key}: ")
            else:
                value = input(f"Enter value for {args.key}: ")
        
        config.set(args.key, value)
        print(f"✅ Set {args.key}")
        
    elif args.config_action == "get":
        if not args.key:
            print("❌ Please specify a key to get (e.g., --key OPENAI_API_KEY)")
            return
            
        value = config.get(args.key)
        if value:
            # Mask API keys for security
            if "API_KEY" in args.key.upper():
                masked = value[:8] + "..." if len(value) > 8 else "***"
                print(f"{args.key}: {masked}")
            else:
                print(f"{args.key}: {value}")
        else:
            print(f"{args.key}: (not set)")
            
    elif args.config_action == "list":
        print("🔧 Current Configuration:")
        print(f"📁 Config file: {config.config_file}")
        print(f"📥 Output directory: {config.get_output_dir()}")
        print()
        
        # List common API keys
        api_keys = ["OPENAI_API_KEY", "ELEVENLABS_API_KEY", "GEMINI_API_KEY", "GOOGLE_APPLICATION_CREDENTIALS"]
        for key in api_keys:
            value = config.get(key)
            if value:
                if "API_KEY" in key:
                    masked = value[:8] + "..." if len(value) > 8 else "***"
                    print(f"  {key}: {masked}")
                else:
                    print(f"  {key}: {value}")
            else:
                print(f"  {key}: (not set)")
                
    elif args.config_action == "init":
        print("🔧 Setting up AI Voice Generator configuration...")
        print(f"📁 Config will be saved to: {config.config_file}")
        print()
        
        # Guide user through setting up API keys
        api_keys = {
            "OPENAI_API_KEY": "OpenAI API key for TTS",
            "ELEVENLABS_API_KEY": "ElevenLabs API key",
            "GEMINI_API_KEY": "Google Gemini API key",
        }
        
        for key, description in api_keys.items():
            current = config.get(key)
            if current:
                print(f"✅ {key} is already set")
                continue
                
            print(f"\n📝 {description}")
            value = getpass.getpass(f"Enter {key} (or press Enter to skip): ")
            if value.strip():
                config.set(key, value)
                print(f"✅ Set {key}")
        
        print(f"\n🎉 Configuration complete!")
        print(f"📁 Files will be saved to: {config.get_output_dir()}")
        print("🚀 Run 'aivoicegen' to start the application")


def database_command(args):
    """Handle database-related commands."""
    if args.db_action == "reset":
        print("🗑️  Resetting database to clean state...")
        reset_database()
        print("✅ Database reset successfully")
        
    elif args.db_action == "sample":
        print("📝 Adding sample data to database...")
        add_sample_data()
        print("✅ Sample data added successfully")
        
    elif args.db_action == "clear":
        print("🗑️  Clearing all generation history...")
        reset_database()
        print("✅ History cleared successfully")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Voice Generator - Multi-provider Text-to-Speech web application"
    )
    
    # Create subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Default command (run server)
    run_parser = subparsers.add_parser("run", help="Run the web server (default)")
    run_parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to run the server on (default: 5000)",
    )
    run_parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)",
    )
    run_parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    run_parser.add_argument(
        "--no-browser", action="store_true", help="Don't automatically open browser"
    )
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Manage configuration")
    config_parser.add_argument(
        "config_action", 
        choices=["init", "set", "get", "list"],
        help="Configuration action"
    )
    config_parser.add_argument("--key", help="Configuration key")
    config_parser.add_argument("--value", help="Configuration value")
    
    # Database command
    db_parser = subparsers.add_parser("db", help="Manage database")
    db_parser.add_argument(
        "db_action",
        choices=["reset", "clear", "sample"],
        help="Database action: reset (clean start), clear (remove history), sample (add demo data)"
    )
    
    # Add version to main parser
    parser.add_argument("--version", action="version", version="aivoicegen 1.5.2")
    
    # For backward compatibility - add run parser args to main parser
    parser.add_argument(
        "--port",
        type=int,
        default=5000,
        help="Port to run the server on (default: 5000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)",
    )
    parser.add_argument("--debug", action="store_true", help="Run in debug mode")
    parser.add_argument(
        "--no-browser", action="store_true", help="Don't automatically open browser"
    )

    args = parser.parse_args()
    
    # Handle config command
    if args.command == "config":
        config_command(args)
        return
    
    # Handle database command  
    if args.command == "db":
        database_command(args)
        return
    
    # If no command specified or run command, start the server
    if args.command is None or args.command == "run":
        # Create the Flask app
        app = create_app()

        print(f"🎙️  AI Voice Generator starting...")
        print(f"📍 Server will be available at: http://{args.host}:{args.port}")
        print(f"📁 Audio files will be saved to: {config.get_output_dir()}")
        print(f"🛑 Press Ctrl+C to stop the server")
        print(f"💡 Run 'aivoicegen config init' to set up API keys")

        # Open browser automatically unless disabled
        if not args.no_browser:
            Timer(1.5, open_browser).start()

        try:
            app.run(
                host=args.host,
                port=args.port,
                debug=args.debug,
                use_reloader=False,  # Disable reloader to prevent double startup
            )
        except KeyboardInterrupt:
            print("\n🛑 Shutting down AI Voice Generator...")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Error starting server: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
