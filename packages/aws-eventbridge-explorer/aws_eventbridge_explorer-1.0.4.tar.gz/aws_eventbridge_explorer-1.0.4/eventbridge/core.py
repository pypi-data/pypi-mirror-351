#!/usr/bin/env python3
"""
Core functionality for AWS EventBridge Explorer.
This module contains the core logic for fetching and processing EventBridge data.
"""

import boto3
import networkx as nx
import json
import datetime
import time
from typing import Dict, List, Any, Tuple, Optional

class EventBridgeExplorer:
    """Core class for AWS EventBridge exploration logic."""
    
    def __init__(self):
        """Initialize the EventBridge explorer."""
        self.event_buses = []
        self.selected_bus = None
        self.rules = []
        self.eventbridge_client = boto3.client('events')
        self.logs_client = boto3.client('logs')
        
    def list_event_buses(self):
        """List all event buses in the account."""
        try:
            response = self.eventbridge_client.list_event_buses()
            # Store the event buses in the instance variable
            self.event_buses = response.get('EventBuses', [])
            print(f"Found and stored {len(self.event_buses)} event buses")
            return self.event_buses
        except Exception as e:
            print(f"Error listing event buses: {str(e)}")
            return []
    
    def fetch_event_buses(self) -> List[Dict[str, Any]]:
        """Fetch all event buses from AWS."""
        try:
            events_client = boto3.client('events')
            response = events_client.list_event_buses()
            self.event_buses = response.get('EventBuses', [])
            return self.event_buses
        except Exception as e:
            raise Exception(f"Failed to fetch event buses: {str(e)}")
    
    def select_event_bus(self, bus_name: str) -> Dict[str, Any]:
        """Select an event bus by name."""
        # Reset state when selecting a new event bus
        self.rules = []
        self.selected_rules = []
        self.rule_logs = {}
        self.rule_payloads = {}
        self.graph = None
        
        print(f"Selecting event bus '{bus_name}'...")
        print(f"Available event buses: {[bus['Name'] for bus in self.event_buses]}")
        for bus in self.event_buses:
            print(f"Checking event bus '{bus['Name']}'...")
            if bus['Name'] == bus_name:
                # Store just the name, not the entire object
                self.selected_bus = bus_name
                print(f"Selected event bus name: {self.selected_bus}")
                return bus
        raise ValueError(f"Event bus '{bus_name}' not found")
    
    def fetch_rules(self, event_bus_name=None):
        """Fetch rules for an event bus."""
        # Use the provided event_bus_name or fall back to the selected_bus
        bus_name = event_bus_name or self.selected_bus
        
        if not bus_name:
            raise ValueError("No event bus selected or provided")
        
        try:
            print(f"Fetching rules for event bus: {bus_name}")
            
            # Check if bus_name is a string or a dictionary
            if isinstance(bus_name, dict) and 'Name' in bus_name:
                actual_bus_name = bus_name['Name']
            else:
                actual_bus_name = bus_name
                
            print(f"Using event bus name: {actual_bus_name}")
            
            # Use pagination to get all rules
            rules = []
            paginator = self.eventbridge_client.get_paginator('list_rules')
            page_iterator = paginator.paginate(EventBusName=actual_bus_name)
            
            for page in page_iterator:
                rules.extend(page.get('Rules', []))
            
            # Get targets for each rule
            for rule in rules:
                try:
                    targets_response = self.eventbridge_client.list_targets_by_rule(
                        Rule=rule['Name'],
                        EventBusName=actual_bus_name
                    )
                    rule['Targets'] = targets_response.get('Targets', [])
                except Exception as e:
                    print(f"Error fetching targets for rule {rule['Name']}: {e}")
                    rule['Targets'] = []
            
            self.rules = rules
            return self.rules
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Error fetching rules for event bus {bus_name}: {str(e)}\n{error_details}")
            return []
    
    def select_rules(self, rule_names: List[str]) -> List[Dict[str, Any]]:
        """Select rules by name."""
        self.selected_rules = []
        for rule in self.rules:
            if rule['Name'] in rule_names:
                self.selected_rules.append(rule)
        return self.selected_rules
    
    def create_graph(self, event_bus_name: str, rules: List[Dict[str, Any]]) -> Tuple[nx.DiGraph, Dict[str, str]]:
        """Create a graph visualization of the event bus and rules."""
        # Create graph
        G = nx.DiGraph()
        
        # Add event bus as the central node
        G.add_node(event_bus_name, type='event_bus')
        node_colors = {event_bus_name: 'lightblue'}
        
        # Process each rule
        for rule in rules:
            rule_name = rule['Name']
            G.add_node(rule_name, type='rule', data=rule)
            node_colors[rule_name] = 'lightgreen'
            
            # Connect event bus to rule
            G.add_edge(event_bus_name, rule_name)
            
            # Process targets for this rule
            for i, target in enumerate(rule.get('Targets', [])):
                target_id = target.get('Id', f'unknown_{i}')
                target_arn = target.get('Arn', 'unknown')
                
                # Extract service name from ARN
                service_name = 'unknown'
                if ':' in target_arn:
                    parts = target_arn.split(':')
                    if len(parts) >= 3:
                        service_name = parts[2]
                
                # Create a unique target label
                target_label = f"{service_name}:{target_id}_{rule_name}"
                
                G.add_node(target_label, type='target', arn=target_arn, data=target)
                node_colors[target_label] = 'salmon'
                
                # Connect rule to target
                G.add_edge(rule_name, target_label)
        
        self.graph = G
        return G, node_colors
    
    def fetch_rule_events_and_logs(self, rules: List[Dict[str, Any]], event_bus_name: str) -> Dict[str, Dict[str, str]]:
        """Fetch recent events and logs for the selected rules."""
        result = {'logs': {}, 'payloads': {}}
        
        try:
            # Create CloudWatch Logs client
            logs_client = boto3.client('logs')
            
            # Create CloudWatch Events client
            events_client = boto3.client('events')
            
            # Process each rule
            for rule in rules:
                rule_name = rule['Name']
                
                # Try to fetch recent events
                try:
                    # Check if the rule has a log group
                    log_group_name = f"/aws/events/{rule_name}"
                    
                    # Try to fetch logs
                    try:
                        # Check if log group exists
                        logs_client.describe_log_groups(logGroupNamePrefix=log_group_name)
                        
                        # Query recent logs
                        end_time = int(datetime.datetime.now().timestamp())
                        start_time = end_time - (24 * 60 * 60)  # Last 24 hours
                        
                        query = f"fields @timestamp, @message | sort @timestamp desc | limit 10"
                        start_query_response = logs_client.start_query(
                            logGroupName=log_group_name,
                            startTime=start_time,
                            endTime=end_time,
                            queryString=query
                        )
                        
                        query_id = start_query_response['queryId']
                        
                        # Wait for query to complete
                        response = None
                        while response is None or response['status'] == 'Running':
                            time.sleep(1)
                            response = logs_client.get_query_results(queryId=query_id)
                        
                        # Process results
                        log_entries = []
                        for result_item in response.get('results', []):
                            message = next((field['value'] for field in result_item if field['field'] == '@message'), None)
                            timestamp = next((field['value'] for field in result_item if field['field'] == '@timestamp'), None)
                            if message and timestamp:
                                log_entries.append(f"{timestamp}: {message}")
                        
                        if log_entries:
                            result['logs'][rule_name] = "\n".join(log_entries)
                        else:
                            result['logs'][rule_name] = "No logs found in the last 24 hours."
                    except Exception as e:
                        result['logs'][rule_name] = f"Could not fetch logs: {str(e)}"
                    
                    # Try to fetch recent events using CloudWatch Events TestEventPattern
                    try:
                        # Get the rule's event pattern
                        rule_details = events_client.describe_rule(
                            Name=rule_name,
                            EventBusName=event_bus_name
                        )
                        
                        event_pattern = rule_details.get('EventPattern')
                        
                        if event_pattern:
                            # For demonstration, we'll create a sample event based on the pattern
                            result['payloads'][rule_name] = f"Event Pattern:\n{event_pattern}\n\n" + \
                                                          "Note: AWS doesn't provide direct access to past events. " + \
                                                          "This is the event pattern the rule is looking for."
                        else:
                            result['payloads'][rule_name] = "No event pattern defined for this rule."
                    except Exception as e:
                        result['payloads'][rule_name] = f"Could not fetch event pattern: {str(e)}"
                
                except Exception as e:
                    result['logs'][rule_name] = f"Error fetching logs: {str(e)}"
                    result['payloads'][rule_name] = f"Error fetching events: {str(e)}"
            
            self.rule_logs = result['logs']
            self.rule_payloads = result['payloads']
            return result
            
        except Exception as e:
            raise Exception(f"Failed to fetch events and logs: {str(e)}")
            
    def fetch_target_logs(self, target_arn: str, limit: int = 10, start_time=None, end_time=None, search_term=None) -> Dict[str, Any]:
        """Fetch logs for a specific target with enhanced search capabilities.
        
        Args:
            target_arn: The ARN of the target
            limit: Maximum number of log entries to fetch
            start_time: Start time for log query (Unix timestamp in seconds)
            end_time: End time for log query (Unix timestamp in seconds)
            search_term: Optional search term to filter logs
            
        Returns:
            Dictionary containing log entries, metadata, and search results
        """
        try:
            # Create CloudWatch Logs client
            logs_client = boto3.client('logs')
            
            # Print the ARN for debugging
            print(f"Fetching logs for ARN: {target_arn}")
            print(f"Start time: {start_time}, End time: {end_time}")
            print(f"Search term: {search_term}")
            
            # Convert start_time and end_time to datetime objects if provided
            start_datetime = None
            end_datetime = None
            
            if start_time:
                start_datetime = datetime.datetime.fromtimestamp(float(start_time))
                
            if end_time:
                end_datetime = datetime.datetime.fromtimestamp(float(end_time))
            
            # Extract service and resource from ARN
            parts = target_arn.split(':')
            if len(parts) < 6:
                return {
                    "success": False,
                    "message": f"Invalid ARN format: {target_arn}",
                    "logs": [],
                    "metadata": {"target_arn": target_arn}
                }
            
            service = parts[2]
            resource_id = None
            
            # Extract the actual resource ID based on the service type
            if service == 'lambda':
                if len(parts) >= 7:
                    function_name = parts[6]
                    resource_id = function_name
                else:
                    return {
                        "success": False,
                        "message": f"Invalid Lambda ARN format: {target_arn}",
                        "logs": [],
                        "metadata": {"target_arn": target_arn}
                    }
            elif service == 'states':
                if len(parts) >= 7:
                    resource_id = parts[6]
                else:
                    return {
                        "success": False,
                        "message": f"Invalid Step Functions ARN format: {target_arn}",
                        "logs": [],
                        "metadata": {"target_arn": target_arn}
                    }
            else:
                resource_part = parts[5] if len(parts) > 5 else ""
                if '/' in resource_part:
                    resource_id = resource_part.split('/')[-1]
                else:
                    resource_id = resource_part
            
            if not resource_id:
                return {
                    "success": False,
                    "message": f"Could not extract resource ID from ARN: {target_arn}",
                    "logs": [],
                    "metadata": {"target_arn": target_arn}
                }
                
            # Determine log group name based on service
            log_group_name = None
            if service == 'lambda':
                log_group_name = f"/aws/lambda/{resource_id}"
            elif service == 'states':
                log_group_name = f"/aws/states/{resource_id}"
            elif service == 'sqs':
                return {
                    "success": False,
                    "message": "CloudWatch logs not directly available for SQS. Check CloudWatch metrics instead.",
                    "logs": [],
                    "metadata": {"target_arn": target_arn, "service": "sqs"}
                }
            elif service == 'sns':
                return {
                    "success": False,
                    "message": "CloudWatch logs not directly available for SNS. Check CloudWatch metrics instead.",
                    "logs": [],
                    "metadata": {"target_arn": target_arn, "service": "sns"}
                }
            else:
                return {
                    "success": False,
                    "message": f"Log fetching not implemented for service: {service}",
                    "logs": [],
                    "metadata": {"target_arn": target_arn, "service": service}
                }
            
            if not log_group_name:
                return {
                    "success": False,
                    "message": f"Could not determine log group for {target_arn}",
                    "logs": [],
                    "metadata": {"target_arn": target_arn}
                }
                
            # Check if log group exists
            try:
                log_groups = logs_client.describe_log_groups(logGroupNamePrefix=log_group_name)
                
                # Check if the exact log group exists
                exact_match = False
                for log_group in log_groups.get('logGroups', []):
                    if log_group.get('logGroupName') == log_group_name:
                        exact_match = True
                        break
                
                if not exact_match:
                    return {
                        "success": False,
                        "message": f"Log group {log_group_name} does not exist. This could mean:\n" + 
                                  "1. The resource has never been invoked\n" + 
                                  "2. Logs have been deleted\n" + 
                                  "3. The resource was recently created",
                        "logs": [],
                        "metadata": {"target_arn": target_arn, "log_group": log_group_name}
                    }
                
            except Exception as e:
                return {
                    "success": False,
                    "message": f"Log group {log_group_name} not found: {str(e)}\n\n" + 
                              "This could mean the resource has never been invoked or logs have been deleted.",
                    "logs": [],
                    "metadata": {"target_arn": target_arn, "log_group": log_group_name}
                }
            
            # Set up time range for query
            if not start_time:
                # Default to 30 days ago if no start time is provided
                start_time_ms = int((datetime.datetime.now() - datetime.timedelta(days=30)).timestamp()) * 1000
            else:
                start_time_ms = int(float(start_time) * 1000)  # Convert to milliseconds
                
            if not end_time:
                end_time_ms = int(datetime.datetime.now().timestamp() * 1000)  # Current time
            else:
                end_time_ms = int(float(end_time) * 1000)  # Convert to milliseconds
            
            print(f"Using time range: {start_time_ms} to {end_time_ms}")
            
            try:
                # Build CloudWatch Logs Insights query
                query = f"fields @timestamp, @message"
                
                # Add search filter if provided
                if search_term:
                    # Escape special characters in search term
                    escaped_term = search_term.replace("'", "\\'").replace('"', '\\"')
                    # Use CloudWatch Logs Insights patterns with wildcards for partial matching
                    query += f" | filter @message like '%{escaped_term}%'"
                    # Add a second filter for case-insensitive matching
                    query += f" | filter @message like '%{escaped_term.lower()}%' or @message like '%{escaped_term.upper()}%'"
                    # Log the query for debugging
                    print(f"Search query: {query}")
                
                query += f" | sort @timestamp desc | limit {limit}"
                
                # Start the query
                start_query_response = logs_client.start_query(
                    logGroupName=log_group_name,
                    startTime=int(start_time_ms / 1000),  # Convert back to seconds for API
                    endTime=int(end_time_ms / 1000),      # Convert back to seconds for API
                    queryString=query
                )
                
                query_id = start_query_response['queryId']
                
                # Wait for query to complete
                response = None
                max_attempts = 20
                attempts = 0
                
                while (response is None or response['status'] == 'Running') and attempts < max_attempts:
                    time.sleep(1)
                    response = logs_client.get_query_results(queryId=query_id)
                    attempts += 1
                
                if attempts >= max_attempts and (response is None or response['status'] == 'Running'):
                    return {
                        "success": False,
                        "message": f"Query timed out for {log_group_name}. Please try again later or with a narrower time range.",
                        "logs": [],
                        "metadata": {
                            "target_arn": target_arn,
                            "log_group": log_group_name,
                            "query": query
                        }
                    }
                
                # Process results
                log_entries = []
                for result_item in response.get('results', []):
                    message = next((field['value'] for field in result_item if field['field'] == '@message'), None)
                    timestamp_str = next((field['value'] for field in result_item if field['field'] == '@timestamp'), None)
                    
                    if message and timestamp_str:
                        # Parse timestamp
                        try:
                            timestamp_dt = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')
                            timestamp_ms = int(timestamp_dt.timestamp() * 1000)
                        except ValueError:
                            try:
                                timestamp_dt = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                                timestamp_ms = int(timestamp_dt.timestamp() * 1000)
                            except ValueError:
                                timestamp_ms = 0
                        
                        formatted_time = timestamp_str
                        
                        log_entry = {
                            "timestamp": timestamp_ms,
                            "formatted_time": formatted_time,
                            "message": message,
                            "stream": "unknown",  # CloudWatch Insights doesn't return stream info
                            "matches": []
                        }
                        
                        # If search term is provided, highlight matches
                        if search_term and search_term.lower() in message.lower():
                            # Find all occurrences of the search term (case insensitive)
                            message_lower = message.lower()
                            search_term_lower = search_term.lower()
                            start_idx = 0
                            while True:
                                idx = message_lower.find(search_term_lower, start_idx)
                                if idx == -1:
                                    break
                                log_entry["matches"].append({
                                    "start": idx,
                                    "end": idx + len(search_term)
                                })
                                start_idx = idx + len(search_term)
                        
                        log_entries.append(log_entry)
                
                # Sort logs by timestamp (newest first)
                log_entries.sort(key=lambda x: x["timestamp"], reverse=True)
                
                # Format the date range for the metadata
                start_str = datetime.datetime.fromtimestamp(int(start_time_ms / 1000)).strftime('%Y-%m-%d %H:%M:%S')
                end_str = datetime.datetime.fromtimestamp(int(end_time_ms / 1000)).strftime('%Y-%m-%d %H:%M:%S')
                
                if log_entries:
                    return {
                        "success": True,
                        "message": f"Found {len(log_entries)} log entries",
                        "logs": log_entries,
                        "metadata": {
                            "target_arn": target_arn,
                            "log_group": log_group_name,
                            "resource_id": resource_id,
                            "service": service,
                            "start_time": start_str,
                            "end_time": end_str,
                            "query": query,
                            "search_term": search_term,
                            "total_logs": len(log_entries)
                        }
                    }
                else:
                    return {
                        "success": True,
                        "message": f"No logs found for {resource_id} between {start_str} and {end_str}.",
                        "logs": [],
                        "metadata": {
                            "target_arn": target_arn,
                            "log_group": log_group_name,
                            "resource_id": resource_id,
                            "service": service,
                            "start_time": start_str,
                            "end_time": end_str,
                            "query": query,
                            "search_term": search_term
                        }
                    }
                    
            except Exception as query_error:
                return {
                    "success": False,
                    "message": f"Error querying logs: {str(query_error)}",
                    "logs": [],
                    "metadata": {
                        "target_arn": target_arn,
                        "log_group": log_group_name,
                        "error": str(query_error)
                    }
                }
                
        except Exception as e:
            error_message = str(e)
            return {
                "success": False,
                "message": f"Error fetching logs: {error_message}",
                "logs": [],
                "metadata": {"target_arn": target_arn, "error": error_message}
            }
    def fetch_target_log_streams(self, target_arn: str, start_time=None, end_time=None) -> List[Dict[str, Any]]:
        """Fetch log streams for a specific target.
        
        Args:
            target_arn: The ARN of the target
            start_time: Start time for log query (Unix timestamp in seconds)
            end_time: End time for log query (Unix timestamp in seconds)
            
        Returns:
            List of log stream information
        """
        try:
            # Create CloudWatch Logs client
            logs_client = boto3.client('logs')
            
            # Print the ARN for debugging
            print(f"Fetching log streams for ARN: {target_arn}")
            
            # Extract service and resource from ARN
            # ARN format: arn:partition:service:region:account-id:resource-type/resource-id
            parts = target_arn.split(':')
            if len(parts) < 6:
                return []
            
            service = parts[2]
            resource_id = None
            
            # Extract the actual resource ID based on the service type
            if service == 'lambda':
                # Lambda ARN format: arn:aws:lambda:region:account-id:function:function-name
                # or arn:aws:lambda:region:account-id:function:function-name:alias
                if len(parts) >= 7:
                    # The function name is the 7th part (index 6)
                    function_name = parts[6]
                    # Handle potential alias or version
                    if len(parts) > 7:
                        # If there are more parts, the function name might include an alias or version
                        # We just want the function name part
                        resource_id = function_name
                    else:
                        resource_id = function_name
                else:
                    return []
            elif service == 'states':
                # Step Functions ARN format: arn:aws:states:region:account-id:stateMachine:name
                if len(parts) >= 7:
                    resource_id = parts[6]
                else:
                    return []
            else:
                # For other services, use the last part of the ARN
                resource_part = parts[5] if len(parts) > 5 else ""
                if '/' in resource_part:
                    resource_id = resource_part.split('/')[-1]
                else:
                    resource_id = resource_part
            
            if not resource_id:
                return []
                
            print(f"Extracted resource ID: {resource_id} from ARN: {target_arn}")
                
            # Determine log group name based on service
            log_group_name = None
            if service == 'lambda':
                log_group_name = f"/aws/lambda/{resource_id}"
            elif service == 'states':
                log_group_name = f"/aws/states/{resource_id}"
            elif service == 'sqs':
                return []  # No logs for SQS
            elif service == 'sns':
                return []  # No logs for SNS
            else:
                return []  # Not implemented for other services
            
            if not log_group_name:
                return []
            
            print(f"Looking for log streams in group: {log_group_name}")
                
            # Check if log group exists
            try:
                log_groups = logs_client.describe_log_groups(logGroupNamePrefix=log_group_name)
                
                # Check if the exact log group exists
                exact_match = False
                for log_group in log_groups.get('logGroups', []):
                    if log_group.get('logGroupName') == log_group_name:
                        exact_match = True
                        break
                
                if not exact_match:
                    return []
                
            except Exception as e:
                print(f"Log group {log_group_name} not found: {str(e)}")
                return []
            
            # Fetch log streams
            streams = []
            next_token = None
            
            while True:
                if next_token:
                    response = logs_client.describe_log_streams(
                        logGroupName=log_group_name,
                        orderBy='LastEventTime',
                        descending=True,
                        limit=50,
                        nextToken=next_token
                    )
                else:
                    response = logs_client.describe_log_streams(
                        logGroupName=log_group_name,
                        orderBy='LastEventTime',
                        descending=True,
                        limit=50
                    )
                
                for stream in response.get('logStreams', []):
                    # Format the timestamps for display
                    if 'firstEventTimestamp' in stream:
                        first_time = datetime.datetime.fromtimestamp(stream['firstEventTimestamp'] / 1000)
                        stream['firstEventTime'] = first_time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    if 'lastEventTimestamp' in stream:
                        last_time = datetime.datetime.fromtimestamp(stream['lastEventTimestamp'] / 1000)
                        stream['lastEventTime'] = last_time.strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Add the log group name for reference
                    stream['logGroupName'] = log_group_name
                    
                    streams.append(stream)
                
                # Check if there are more streams to fetch
                next_token = response.get('nextToken')
                if not next_token or len(streams) >= 100:  # Limit to 100 streams max
                    break
            
            return streams
                
        except Exception as e:
            print(f"Error fetching log streams: {str(e)}")
            return []
            
    def fetch_stream_logs(self, log_group_name: str, log_stream_name: str, limit: int = 100) -> str:
        """Fetch logs from a specific log stream with improved handling.
        
        Args:
            log_group_name: The name of the log group
            log_stream_name: The name of the log stream
            limit: Maximum number of log entries to fetch
            
        Returns:
            String containing the log entries
        """
        try:
            # Create CloudWatch Logs client
            logs_client = boto3.client('logs')
            
            print(f"Fetching logs from stream: {log_stream_name} in group: {log_group_name}")
            
            # First, get information about the log stream to find its time range
            try:
                stream_info = logs_client.describe_log_streams(
                    logGroupName=log_group_name,
                    logStreamNamePrefix=log_stream_name,
                    limit=1
                )
                
                if not stream_info.get('logStreams'):
                    return f"<div class='log-container log-empty'>Log stream '{log_stream_name}' not found in log group '{log_group_name}'.</div>"
                    
                stream = stream_info['logStreams'][0]
                first_event_time = stream.get('firstEventTimestamp')
                last_event_time = stream.get('lastEventTimestamp')
                
                if not first_event_time or not last_event_time:
                    return f"<div class='log-container log-empty'>No events found in stream '{log_stream_name}'.</div>"
                    
                print(f"Stream time range: {first_event_time} to {last_event_time}")
                
            except Exception as e:
                print(f"Error getting stream info: {str(e)}")
                return f"<div class='log-container log-error'>Error getting stream info: {str(e)}</div>"
            
            # Get events from the stream using the stream's time range
            try:
                response = logs_client.get_log_events(
                    logGroupName=log_group_name,
                    logStreamName=log_stream_name,
                    startTime=first_event_time,
                    endTime=last_event_time,
                    limit=limit,
                    startFromHead=False  # Start from the end (most recent)
                )
                
                print(f"Log events response: {response}")
                
                # Process the events
                log_entries = []
                for event in response.get('events', []):
                    message = event.get('message')
                    timestamp = event.get('timestamp')
                    
                    if message and timestamp:
                        # Convert timestamp to readable format
                        dt = datetime.datetime.fromtimestamp(timestamp/1000)
                        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                        
                        # Create a preview (first 150 characters)
                        preview = message[:150] + ('...' if len(message) > 150 else '')
                        
                        # Display full log entries without collapsible feature
                        log_entries.append(f"""<div class='log-entry'>
                            <span class='log-timestamp'>{formatted_time}</span>
                            <span class='log-message'>{message}</span>
                        </div>""")
                
                if log_entries:
                    return "<div class='log-container'>" + "".join(log_entries) + "</div>"
                else:
                    # If no events in the first request, try using the token for pagination
                    next_token = response.get('nextForwardToken')
                    if next_token:
                        print(f"No events in first request, trying with token: {next_token}")
                        token_response = logs_client.get_log_events(
                            logGroupName=log_group_name,
                            logStreamName=log_stream_name,
                            nextToken=next_token,
                            limit=limit
                        )
                        
                        token_events = token_response.get('events', [])
                        if token_events:
                            token_entries = []
                            for event in token_events:
                                message = event.get('message')
                                timestamp = event.get('timestamp')
                                
                                if message and timestamp:
                                    dt = datetime.datetime.fromtimestamp(timestamp/1000)
                                    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                                    
                                    # Create a preview (first 150 characters)
                                    preview = message[:150] + ('...' if len(message) > 150 else '')
                                    
                                # Display full log entries without collapsible feature
                                token_entries.append(f"""<div class='log-entry'>
                                    <span class='log-timestamp'>{formatted_time}</span>
                                    <span class='log-message'>{message}</span>
                                </div>""")
                            
                            if token_entries:
                                return "<div class='log-container'>" + "".join(token_entries) + "</div>"
                    
                    # Try one more approach - get events without specifying time range
                    print("Trying to fetch logs without time range...")
                    fallback_response = logs_client.get_log_events(
                        logGroupName=log_group_name,
                        logStreamName=log_stream_name,
                        limit=limit
                    )
                    
                    fallback_events = fallback_response.get('events', [])
                    if fallback_events:
                        fallback_entries = []
                        for event in fallback_events:
                            message = event.get('message')
                            timestamp = event.get('timestamp')
                            
                            if message and timestamp:
                                dt = datetime.datetime.fromtimestamp(timestamp/1000)
                                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                                
                                # Create a preview (first 150 characters)
                                preview = message[:150] + ('...' if len(message) > 150 else '')
                                
                                # Display full log entries without collapsible feature
                                fallback_entries.append(f"""<div class='log-entry'>
                                    <span class='log-timestamp'>{formatted_time}</span>
                                    <span class='log-message'>{message}</span>
                                </div>""")
                        
                        if fallback_entries:
                            return "<div class='log-container'>" + "".join(fallback_entries) + "</div>"
                    
                    return f"<div class='log-container log-empty'>No log events found in stream '{log_stream_name}'.</div>"
                    
            except Exception as e:
                print(f"Error getting log events: {str(e)}")
                return f"<div class='log-container log-error'>Error getting log events: {str(e)}</div>"
                    
        except Exception as e:
            error_message = str(e)
            print(f"Error fetching stream logs: {error_message}")
            return f"<div class='log-container log-error'>Error fetching logs: {error_message}</div>"
    def build_graph_with_logs(self, event_bus_name: str, rule_names: List[str] = None) -> nx.DiGraph:
        """Build a graph representation of the event bus, rules, targets, and a summary of their log streams.
        
        Args:
            event_bus_name: Name of the event bus
            rule_names: Optional list of rule names to filter by
            
        Returns:
            NetworkX DiGraph object representing the event bus, rules, targets, and log stream summaries.
        """
        G = nx.DiGraph()
        
        # Add event bus node
        G.add_node(event_bus_name, type='event_bus', name=event_bus_name, label=event_bus_name)
        
        # Process each rule
        for rule_data in self.rules: # Assuming self.rules contains the rule objects
            rule_name = rule_data['Name']
            
            # Skip if we're filtering rules and this one isn't in the list
            if rule_names and rule_name not in rule_names:
                continue
                
            # Add rule node
            G.add_node(rule_name, type='rule', name=rule_name, label=rule_name)
            
            # Connect event bus to rule
            G.add_edge(event_bus_name, rule_name)
            
            # Get rule details (which should include targets after previous fixes)
            rule_details = self.get_rule_details(rule_name)
            
            if not rule_details:
                print(f"Warning: Could not get details for rule {rule_name}. Skipping targets for this rule.")
                continue

            # Include the event pattern in the rule node data
            event_pattern = rule_details.get('EventPattern')
            if event_pattern:
                G.nodes[rule_name]['eventPattern'] = event_pattern

            # Process targets
            for target in rule_details.get('Targets', []):
                target_id_from_aws = target.get('Id', 'unknown_target')
                target_arn = target.get('Arn', 'unknown_arn')
                # Create a unique node ID for the target, prefixed by its rule, as targets can be reused.
                target_node_id = f"target:{rule_name}:{target_id_from_aws}" 
                
                # Extract service name and function name from ARN if available
                display_name = target_id_from_aws  # Default to AWS target ID
                if ':lambda:' in target_arn and ':function:' in target_arn:
                    # Extract the function name from the ARN
                    display_name = target_arn.split(':function:')[-1]
                
                # Add target node
                G.add_node(target_node_id, 
                          type='target', 
                          name=target_id_from_aws, # Original ID in rule
                          label=display_name, # Cytoscape label - using function name for Lambda
                          arn=target_arn, 
                          rule_name=rule_name) # Store original rule name for context
                
                # Connect rule to target
                G.add_edge(rule_name, target_node_id)
                
                # Note: Log stream nodes are no longer added to the graph
                # Instead, log streams will be fetched and displayed in the target details panel
        
        return G
    def get_rule_details(self, rule_name):
        """Get details for a specific rule, attempting to augment with list_targets_by_rule if needed."""
        if not self.selected_bus:
            print(f"Error in get_rule_details: No event bus selected when trying to describe rule '{rule_name}'.")
            return None 
        
        print(f"Getting details for rule: {rule_name} on event bus: {self.selected_bus}")
        rule_details_response = None
        try:
            rule_details_response = self.eventbridge_client.describe_rule(
                Name=rule_name,
                EventBusName=self.selected_bus
            )
            print(f"Initial response from describe_rule for {rule_name}: {rule_details_response}")
            
            targets_from_describe = rule_details_response.get('Targets')
            if targets_from_describe:
                print(f"Found {len(targets_from_describe)} targets for rule {rule_name} via describe_rule: {targets_from_describe}")
            else:
                print(f"No 'Targets' field or targets list is empty in describe_rule response for {rule_name}. Attempting list_targets_by_rule.")
                try:
                    list_targets_response = self.eventbridge_client.list_targets_by_rule(
                        Rule=rule_name,
                        EventBusName=self.selected_bus
                    )
                    targets_from_list = list_targets_response.get('Targets')
                    if targets_from_list:
                        print(f"Found {len(targets_from_list)} targets for rule {rule_name} via list_targets_by_rule: {targets_from_list}")
                        # Ensure rule_details_response is not None before trying to update it
                        if rule_details_response is None:
                            rule_details_response = {} # Should not happen if describe_rule succeeded earlier
                        rule_details_response['Targets'] = targets_from_list # Augment/add Targets key
                    else:
                        print(f"list_targets_by_rule also found no targets for {rule_name}.")
                except Exception as e_list_targets:
                    print(f"Exception calling list_targets_by_rule for {rule_name}: {str(e_list_targets)}")
                    # If list_targets_by_rule fails, we proceed with whatever describe_rule gave (which might be no targets)

        except Exception as e_describe_rule:
            print(f"Exception in describe_rule for {rule_name} on bus {self.selected_bus}: {str(e_describe_rule)}")
            # If describe_rule fails, we might still try list_targets_by_rule if we want to be super robust,
            # but for now, if describe_rule fails, we assume we can't get core rule details.
            # However, if the goal is *just* targets, one could try list_targets_by_rule here too.
            # For now, let's ensure rule_details_response is initialized for safety if it was None and an exception occurred.
            if rule_details_response is None: rule_details_response = {} # Initialize if describe_rule failed before assignment

        if not rule_details_response: # If describe_rule failed badly and rule_details_response is still None
             print(f"describe_rule returned an empty or None response for {rule_name} and was not augmented.")

        return rule_details_response
