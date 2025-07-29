"""
Command-line interface for AI Voice Generator.
"""

import argparse
import sys
import time
import webbrowser
from threading import Timer

from .app import create_app


def open_browser():
    """Open the web browser to the application URL after a short delay."""
    time.sleep(1.5)  # Give the server time to start
    webbrowser.open("http://127.0.0.1:5000")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="AI Voice Generator - Multi-provider Text-to-Speech web application"
    )
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
    parser.add_argument("--version", action="version", version="aivoicegen 1.0.0")

    args = parser.parse_args()

    # Create the Flask app
    app = create_app()

    print(f"🎙️  AI Voice Generator starting...")
    print(f"📍 Server will be available at: http://{args.host}:{args.port}")
    print(f"🛑 Press Ctrl+C to stop the server")

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
