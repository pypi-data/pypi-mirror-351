#!/usr/bin/env python3
"""
CLI entry point for AWS EventBridge Explorer.
"""

import sys
import os
import argparse
import time

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(
        description='AWS EventBridge Explorer',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--port', '-p', type=int, default=5050,
                        help='Port for web server')
    
    args = parser.parse_args()
    
    from eventbridge.core import EventBridgeExplorer
    from eventbridge.web_server import EventBridgeWebServer
    
    # Initialize the core explorer
    explorer = EventBridgeExplorer()
    
    # Initialize the web server
    web_server = EventBridgeWebServer(port=args.port, explorer=explorer)
    
    # Start the web server
    web_server.start()
    
    # Keep the main thread running
    try:
        print("Web server running at http://localhost:{}".format(args.port))
        print("Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        web_server.stop()

if __name__ == "__main__":
    main() 