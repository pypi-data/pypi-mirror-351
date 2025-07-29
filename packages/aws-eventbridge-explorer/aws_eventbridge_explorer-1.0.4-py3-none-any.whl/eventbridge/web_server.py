"""
Flask web server for EventBridge Explorer.
This module provides a web server to serve the Cytoscape.js visualization.
"""

import os
import json
import threading
import webbrowser
import time
import networkx as nx
from typing import Dict, List, Any, Optional, Callable
import boto3
import datetime

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

from eventbridge.core import EventBridgeExplorer

class EventBridgeWebServer:
    """Web server for EventBridge Explorer."""
    
    def __init__(self, port=5000, explorer=None):
        """Initialize the web server."""
        self.port = port
        self.app = Flask(__name__, 
                         template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
                         static_folder=os.path.join(os.path.dirname(__file__), 'static'))
        CORS(self.app)  # Enable CORS for all routes
        
        # Initialize the explorer
        self.explorer = explorer if explorer else EventBridgeExplorer()
        
        # Register routes
        self.register_routes()
        
        # Store graph data
        self.graph_data = None
        self.server_thread = None
        self.is_running = False
        
    def register_routes(self):
        """Register routes for the web server."""
        @self.app.route('/')
        def index():
            """Render the index page."""
            return render_template('index.html')
        
        @self.app.route('/api/event-buses', methods=['GET'])
        def get_event_buses():
            """Get all event buses."""
            try:
                print("Fetching event buses...")
                event_buses = self.explorer.list_event_buses()
                print(f"Found {len(event_buses)} event buses")
                return jsonify({
                    'success': True,
                    'data': event_buses
                })
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"Error fetching event buses: {str(e)}\n{error_details}")
                return jsonify({
                    'success': False,
                    'message': str(e),
                    'error_type': type(e).__name__
                }), 500
        
        @self.app.route('/api/rules', methods=['GET'])
        def get_rules():
            """Get all rules for an event bus."""
            try:
                event_bus_name = request.args.get('event_bus')
                
                if not event_bus_name:
                    return jsonify({
                        'success': False,
                        'message': 'Event bus name is required'
                    }), 400
                
                # Clean up the event bus name if it has a prefix
                if "Event Bus:" in event_bus_name:
                    event_bus_name = event_bus_name.replace("Event Bus:", "").strip()
                
                try:
                    # Select the event bus
                    self.explorer.select_event_bus(event_bus_name)
                except ValueError as e:
                    # Handle the case where the event bus doesn't exist
                    return jsonify({
                        'success': False,
                        'message': str(e)
                    }), 404
                
                # Always fetch rules to ensure we have the latest
                print(f"Fetching rules for event bus: {event_bus_name}")
                rules = self.explorer.fetch_rules()
                print(f"Fetched {len(rules)} rules")
                
                return jsonify({
                    'success': True,
                    'data': self.explorer.rules
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/graph', methods=['POST'])
        def get_graph():
            """Get graph data for an event bus."""
            try:
                data = request.json
                event_bus_name = data.get('event_bus')
                rule_names = data.get('rules', [])
                
                if not event_bus_name:
                    return jsonify({
                        'success': False,
                        'message': 'Event bus name is required'
                    }), 400
                
                # Select the event bus
                self.explorer.select_event_bus(event_bus_name)
                
                # Fetch rules if not already fetched
                if not self.explorer.rules:
                    self.explorer.fetch_rules()
                
                # Build the graph
                graph = self.explorer.build_graph(event_bus_name, rule_names)
                
                # Convert to Cytoscape.js format
                elements = self.convert_graph_to_elements(graph)
                
                return jsonify({
                    'success': True,
                    'data': {
                        'elements': elements,
                        'eventBusName': event_bus_name
                    }
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
                
        @self.app.route('/api/logs', methods=['POST'])
        def get_logs():
            """Get logs for a rule."""
            try:
                data = request.json
                rule_name = data.get('rule')
                target_id = data.get('target_id')
                time_range = data.get('time_range', '1h')
                
                if not rule_name:
                    return jsonify({
                        'success': False,
                        'message': 'Rule name is required'
                    }), 400
                
                if not target_id:
                    return jsonify({
                        'success': False,
                        'message': 'Target ID is required'
                    }), 400
                
                # Get logs for the rule
                logs = self.explorer.get_logs(rule_name, target_id, time_range)
                
                return jsonify({
                    'success': True,
                    'data': logs
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
                
        @self.app.route('/api/logs/search', methods=['POST'])
        def search_logs():
            """Search logs across multiple rules."""
            try:
                data = request.json
                rules = data.get('rules', [])
                search_term = data.get('search_term')
                limit = data.get('limit', 100)
                
                if not rules:
                    return jsonify({
                        'success': False,
                        'message': 'At least one rule is required'
                    }), 400
                
                if not search_term:
                    return jsonify({
                        'success': False,
                        'message': 'Search term is required'
                    }), 400
                
                # Search logs across rules
                results = self.explorer.search_logs(rules, search_term, limit)
                
                return jsonify({
                    'success': True,
                    'data': results
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
                
        @self.app.route('/api/logs/stream', methods=['POST'])
        def get_stream_logs():
            """Get logs for a specific log stream."""
            try:
                data = request.json
                target_arn = data.get('target_arn')
                stream_name = data.get('stream_name')
                limit = data.get('limit', 50)
                search_term = data.get('search_term')
                
                if not target_arn or not stream_name:
                    return jsonify({
                        'success': False,
                        'message': 'Target ARN and stream name are required'
                    }), 400
                
                # Fetch logs for the specific stream
                result = self.explorer.fetch_stream_logs(
                    target_arn,
                    stream_name,
                    limit=limit,
                    search_term=search_term
                )
                
                return jsonify({
                    'success': True,
                    'data': result
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
                
        @self.app.route('/api/search_logs', methods=['POST'])
        def search_target_logs():
            """Search logs across a specific target for a search term."""
            try:
                data = request.json
                target_arn = data.get('targetArn')
                search_term = data.get('searchTerm')
                limit = data.get('limit', 100)
                
                if not target_arn:
                    return jsonify({
                        'success': False,
                        'message': 'Target ARN is required'
                    }), 400
                
                if not search_term:
                    return jsonify({
                        'success': False,
                        'message': 'Search term is required'
                    }), 400
                
                # Use the fetch_target_logs method with search_term parameter
                logs_data = self.explorer.fetch_target_logs(
                    target_arn=target_arn,
                    limit=limit,
                    search_term=search_term
                )
                
                if not logs_data.get('success', False):
                    return jsonify({
                        'success': False,
                        'message': logs_data.get('message', 'No logs found or error occurred'),
                        'metadata': logs_data.get('metadata', {})
                    }), 404
                
                # Return the logs data
                return jsonify({
                    'success': True,
                    'logs': logs_data.get('logs', []),
                    'metadata': logs_data.get('metadata', {})
                })
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"Error searching logs: {str(e)}\n{error_details}")
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
                
        @self.app.route('/api/target_log_streams', methods=['POST'])
        def get_target_log_streams():
            """Get target log streams for a specific target."""
            try:
                data = request.json
                target_arn = data.get('targetArn')
                
                if not target_arn:
                    return jsonify({
                        'success': False,
                        'message': 'Target ARN is required'
                    }), 400
                
                # Get target log streams
                streams = self.explorer.fetch_target_log_streams(target_arn, data.get("startTime"), data.get("endTime"))
                
                return jsonify({
                    'success': True,
                    'streams': streams
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
                
        @self.app.route('/api/graph/with-logs', methods=['POST'])
        def get_graph_with_logs():
            """Get graph data with log nodes included."""
            try:
                data = request.json
                event_bus_name = data.get('event_bus')
                rule_names = data.get('rules', [])
                
                if not event_bus_name:
                    return jsonify({
                        'success': False,
                        'message': 'Event bus name is required'
                    }), 400
                
                # Select the event bus
                self.explorer.select_event_bus(event_bus_name)
                
                # Fetch rules if not already fetched
                if not self.explorer.rules:
                    self.explorer.fetch_rules(event_bus_name)
                
                # Build the enhanced graph with log nodes
                graph = self.explorer.build_graph_with_logs(event_bus_name, rule_names)
                
                # Convert to Cytoscape.js format
                elements = self.convert_graph_to_elements(graph)
                
                return jsonify({
                    'success': True,
                    'data': {
                        'elements': elements,
                        'eventBusName': event_bus_name
                    }
                })
                
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
                
        @self.app.route('/api/stream_logs', methods=['POST'])
        def get_stream_logs_direct():
            """Get logs for a specific log stream using direct log group and stream names."""
            try:
                data = request.json
                log_group = data.get('logGroup')
                log_stream = data.get('logStream')
                start_time = data.get('startTime')  # Unix timestamp in seconds
                end_time = data.get('endTime')      # Unix timestamp in seconds
                limit = data.get('limit', 100)
                
                if not log_group or not log_stream:
                    return jsonify({
                        'success': False,
                        'message': 'Log group and stream name are required'
                    }), 400
                
                # Create CloudWatch Logs client
                logs_client = boto3.client('logs')
                
                # Prepare parameters for get_log_events
                params = {
                    'logGroupName': log_group,
                    'logStreamName': log_stream,
                    'limit': limit,
                    'startFromHead': True  # Start from the beginning of the stream
                }
                
                # Add time range parameters if provided
                if start_time:
                    params['startTime'] = int(start_time) * 1000  # Convert to milliseconds
                if end_time:
                    params['endTime'] = int(end_time) * 1000      # Convert to milliseconds
                
                try:
                    # Get log events
                    response = logs_client.get_log_events(**params)
                    
                    # Process events
                    log_entries = []
                    for event in response.get('events', []):
                        message = event.get('message', '')
                        timestamp = event.get('timestamp')
                        
                        if timestamp:
                            # Convert timestamp to readable format
                            dt = datetime.datetime.fromtimestamp(timestamp/1000)
                            formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                            log_entries.append(f"{formatted_time} {message}")
                        else:
                            log_entries.append(message)
                    
                    logs_content = "\n".join(log_entries)
                    
                    return jsonify({
                        'success': True,
                        'logs': logs_content
                    })
                    
                except Exception as e:
                    import traceback
                    error_details = traceback.format_exc()
                    print(f"Error fetching log events: {str(e)}\n{error_details}")
                    return jsonify({
                        'success': False,
                        'message': f"Error fetching log events: {str(e)}"
                    }), 500
                    
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"Error processing stream logs request: {str(e)}\n{error_details}")
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
        
        @self.app.route('/api/send_event', methods=['POST'])
        def send_event():
            """Send a test event to the EventBridge event bus."""
            try:
                data = request.json
                event_data = data.get('event_data')
                event_bus_name = data.get('event_bus_name', 'default')
                
                if not event_data:
                    return jsonify({
                        'success': False,
                        'message': 'Event data is required'
                    }), 400
                
                # Create EventBridge client
                events_client = boto3.client('events')
                
                # Send the event
                response = events_client.put_events(
                    Entries=[
                        {
                            'Source': event_data.get('source', 'test.event'),
                            'DetailType': event_data.get('detail-type', 'Test Event'),
                            'Detail': json.dumps(event_data.get('detail', {})),
                            'EventBusName': event_bus_name
                        }
                    ]
                )
                
                # Check the response
                if 'Entries' in response and len(response['Entries']) > 0:
                    entry = response['Entries'][0]
                    if 'EventId' in entry:
                        return jsonify({
                            'success': True,
                            'message': f'Event sent successfully with ID: {entry["EventId"]}',
                            'event_id': entry['EventId']
                        })
                    elif 'ErrorCode' in entry:
                        return jsonify({
                            'success': False,
                            'message': f'Error sending event: {entry["ErrorCode"]} - {entry.get("ErrorMessage", "No error message")}'
                        }), 400
                
                return jsonify({
                    'success': True,
                    'message': 'Event sent successfully',
                    'response': response
                })
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                print(f"Error sending event: {str(e)}\n{error_details}")
                return jsonify({
                    'success': False,
                    'message': str(e)
                }), 500
    
    def convert_graph_to_elements(self, graph: nx.DiGraph) -> Dict[str, List[Dict[str, Any]]]:
        """Convert a NetworkX graph to Cytoscape.js elements format."""
        elements = {
            'nodes': [],
            'edges': []
        }
        
        # Add nodes
        for node_id in graph.nodes():
            node_data = graph.nodes[node_id]
            elements['nodes'].append({
                'data': {
                    'id': node_id,
                    'type': node_data.get('type', 'unknown'),
                    'name': node_data.get('name', node_id),
                    **{k: v for k, v in node_data.items() if k not in ['type', 'name']}
                }
            })
        
        # Add edges
        for source, target in graph.edges():
            elements['edges'].append({
                'data': {
                    'id': f"{source}-{target}",
                    'source': source,
                    'target': target
                }
            })
        
        return elements
    
    def start(self, open_browser: bool = True):
        """Start the web server in a separate thread."""
        if self.is_running:
            print("Web server is already running.")
            return
        
        def run_server():
            self.app.run(host='127.0.0.1', port=self.port)
        
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Wait for the server to start
        time.sleep(1)
        
        self.is_running = True
        print(f"Web server running. Press Ctrl+C to stop.")
        
        # Only open the browser if requested and not already running
        if open_browser and not hasattr(self, '_browser_opened'):
            webbrowser.open(self.get_url())
            # Set a flag to indicate the browser has been opened
            self._browser_opened = True
    
    def stop(self):
        """Stop the web server."""
        if not self.is_running:
            print("Web server is not running.")
            return
        
        # There's no clean way to stop a Flask server in a thread
        # We'll rely on the daemon thread to be terminated when the main program exits
        self.is_running = False
        print("Web server stopped.")
        
    def get_url(self):
        """Get the URL of the web server."""
        return f"http://127.0.0.1:{self.port}"
