"""
Tests for the EventBridgeExplorer core class.
"""

import unittest
from unittest.mock import patch, MagicMock

from eventbridge.core import EventBridgeExplorer


class TestEventBridgeExplorer(unittest.TestCase):
    """Test cases for the EventBridgeExplorer class."""

    @patch('boto3.client')
    def setUp(self, mock_boto3_client):
        """Set up the test case."""
        self.mock_eventbridge_client = MagicMock()
        self.mock_logs_client = MagicMock()
        
        # Configure boto3 client mock to return our mock clients
        mock_boto3_client.side_effect = lambda service: {
            'events': self.mock_eventbridge_client,
            'logs': self.mock_logs_client
        }[service]
        
        self.explorer = EventBridgeExplorer()
    
    def test_init(self):
        """Test the initialization of the EventBridgeExplorer class."""
        self.assertEqual(self.explorer.event_buses, [])
        self.assertIsNone(self.explorer.selected_bus)
        self.assertEqual(self.explorer.rules, [])
        
    @patch('boto3.client')
    def test_list_event_buses(self, mock_boto3_client):
        """Test listing event buses."""
        # Setup the mock to return a list of event buses
        self.mock_eventbridge_client.list_event_buses.return_value = {
            'EventBuses': [
                {'Name': 'default', 'Arn': 'arn:aws:events:us-east-1:123456789012:event-bus/default'},
                {'Name': 'custom-bus', 'Arn': 'arn:aws:events:us-east-1:123456789012:event-bus/custom-bus'}
            ]
        }
        
        event_buses = self.explorer.list_event_buses()
        
        # Check that the mock was called
        self.mock_eventbridge_client.list_event_buses.assert_called_once()
        
        # Check that we got the expected result
        self.assertEqual(len(event_buses), 2)
        self.assertEqual(event_buses[0]['Name'], 'default')
        self.assertEqual(event_buses[1]['Name'], 'custom-bus')


if __name__ == '__main__':
    unittest.main() 