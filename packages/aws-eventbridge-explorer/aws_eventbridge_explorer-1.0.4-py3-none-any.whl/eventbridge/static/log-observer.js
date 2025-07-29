/**
 * Log Observer for EventBridge Visualizer
 * This module provides enhanced log visualization and search capabilities
 */

class LogObserver {
    constructor(options = {}) {
        this.options = {
            searchInputSelector: '#log-search-input',
            searchButtonSelector: '#log-search-button',
            searchStatsSelector: '#search-stats',
            matchCountSelector: '#match-count',
            logCountSelector: '#log-count',
            ...options
        };
        
        // Wait for DOM to be fully loaded before initializing
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => {
                this.initializeElements();
                this.init();
            });
        } else {
            this.initializeElements();
            this.init();
        }
        
        this.searchTerm = '';
        this.matchBadges = [];
    }
    
    initializeElements() {
        this.searchInput = document.querySelector(this.options.searchInputSelector);
        this.searchButton = document.querySelector(this.options.searchButtonSelector);
        this.searchStats = document.querySelector(this.options.searchStatsSelector);
        this.matchCount = document.querySelector(this.options.matchCountSelector);
        this.logCount = document.querySelector(this.options.logCountSelector);
        
        // Log element availability for debugging
        console.log('Search input found:', !!this.searchInput);
        console.log('Search button found:', !!this.searchButton);
        console.log('Search stats found:', !!this.searchStats);
        console.log('Match count found:', !!this.matchCount);
        console.log('Log count found:', !!this.logCount);
    }
    
    init() {
        this.createLogContentModal();
        this.attachEventListeners();
        
        // Don't try to access window.cy immediately
        // Instead, set up a MutationObserver to wait for it
        this.setupCytoscapeEventHandlers();
    }
    
    setupCytoscapeEventHandlers() {
        // Function to set up Cytoscape event handlers when available
        const setupHandlers = () => {
            if (window.cy && typeof window.cy.on === 'function') {
                console.log('Cytoscape instance found, setting up event handlers');
                window.cy.on('tap', 'node[type="log_stream"]', (evt) => {
                    const node = evt.target;
                    this.showLogsForNode(node);
                });
                return true;
            }
            return false;
        };
        
        // Try immediately first
        if (setupHandlers()) {
            return;
        }
        
        // If not available, set up polling
        console.log('Cytoscape instance not available yet, will poll for it');
        let attempts = 0;
        const maxAttempts = 20;
        
        const checkInterval = setInterval(() => {
            attempts++;
            if (setupHandlers() || attempts >= maxAttempts) {
                clearInterval(checkInterval);
                if (attempts >= maxAttempts) {
                    console.warn('Could not find Cytoscape instance after', maxAttempts, 'attempts');
                }
            }
        }, 500);
    }
    
    createLogContentModal() {
        // Create modal container if it doesn't exist
        if (!document.getElementById('log-content-modal')) {
            const modal = document.createElement('div');
            modal.id = 'log-content-modal';
            modal.className = 'log-content-modal';
            
            modal.innerHTML = `
                <div class="log-modal-content">
                    <div class="log-modal-header">
                        <h2 class="text-xl font-bold">Log Stream: <span id="stream-name"></span></h2>
                        <button id="log-modal-close" class="log-modal-close">&times;</button>
                    </div>
                    <div class="log-modal-body">
                        <div id="log-content" class="font-mono text-sm whitespace-pre-wrap"></div>
                    </div>
                </div>
            `;
            
            document.body.appendChild(modal);
            
            // Add close button handler
            document.getElementById('log-modal-close').addEventListener('click', () => {
                this.hideLogContentModal();
            });
            
            // Close when clicking outside the modal content
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.hideLogContentModal();
                }
            });
        }
    }
    
    attachEventListeners() {
        // Search button click
        if (this.searchButton) {
            this.searchButton.addEventListener('click', () => {
                this.performSearch();
            });
        }
        
        // Search input enter key
        if (this.searchInput) {
            this.searchInput.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') {
                    this.performSearch();
                }
            });
        }
    }
    
    performSearch() {
        const searchTerm = this.searchInput.value.trim();
        if (!searchTerm) return;
        
        this.searchTerm = searchTerm;
        
        // Show loading indicator
        this.searchButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        
        // Get all rules from the graph
        let rules = [];
        
        // Method 1: Try to get rules from Cytoscape
        if (window.cy && typeof window.cy.nodes === 'function') {
            try {
                const ruleNodes = window.cy.nodes('[type="rule"]');
                ruleNodes.forEach(node => {
                    rules.push(node.id());
                });
                console.log('Rules found from Cytoscape:', rules);
            } catch (error) {
                console.error('Error getting rule nodes from Cytoscape:', error);
            }
        }
        
        // Method 2: Try to get rules from window.selectedRules
        if (rules.length === 0 && window.selectedRules && window.selectedRules.length > 0) {
            rules = window.selectedRules;
            console.log('Rules found from window.selectedRules:', rules);
        }
        
        // Method 3: Try to get the event bus name and fetch all rules
        if (rules.length === 0) {
            const eventBusElement = document.getElementById('event-bus-name');
            if (eventBusElement && eventBusElement.textContent && !eventBusElement.textContent.includes('No event bus')) {
                const eventBusName = eventBusElement.textContent.trim();
                console.log('Getting all rules for event bus:', eventBusName);
                
                // Extract just the event bus name without the "Event Bus:" prefix
                const cleanEventBusName = eventBusName.replace('Event Bus:', '').trim();
                
                // Make a synchronous request to get all rules for this event bus
                const xhr = new XMLHttpRequest();
                xhr.open('GET', `/api/rules?event_bus=${encodeURIComponent(cleanEventBusName)}`, false);
                xhr.send();
                
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.success && response.data && response.data.length > 0) {
                            rules = response.data.map(rule => rule.Name);
                            console.log('Rules fetched from API:', rules);
                        }
                    } catch (error) {
                        console.error('Error parsing rules response:', error);
                    }
                } else {
                    console.error('Failed to fetch rules:', xhr.status, xhr.statusText);
                }
            }
        }
        
        // Method 4: Last resort - check if there are any target nodes and extract rule names
        if (rules.length === 0 && window.cy && typeof window.cy.nodes === 'function') {
            try {
                const targetNodes = window.cy.nodes('[type="target"]');
                const ruleSet = new Set();
                
                targetNodes.forEach(node => {
                    const ruleData = node.data('rule');
                    if (ruleData) {
                        ruleSet.add(ruleData);
                    }
                });
                
                rules = Array.from(ruleSet);
                console.log('Rules extracted from target nodes:', rules);
            } catch (error) {
                console.error('Error extracting rules from target nodes:', error);
            }
        }
        
        // Method 5: Absolute last resort - hardcode some rules for testing
        if (rules.length === 0) {
            // Try to get the event bus select element
            const eventBusSelect = document.getElementById('event-bus-select');
            if (eventBusSelect && eventBusSelect.value) {
                console.log('Using event bus from select element:', eventBusSelect.value);
                
                // Make a synchronous request to get all rules for this event bus
                const xhr = new XMLHttpRequest();
                xhr.open('GET', `/api/rules?event_bus=${encodeURIComponent(eventBusSelect.value)}`, false);
                xhr.send();
                
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        if (response.success && response.data && response.data.length > 0) {
                            rules = response.data.map(rule => rule.Name);
                            console.log('Rules fetched from API using select element:', rules);
                        }
                    } catch (error) {
                        console.error('Error parsing rules response:', error);
                    }
                }
            }
        }
        
        if (rules.length === 0) {
            alert('No rules found. Please select an event bus first.');
            this.searchButton.innerHTML = '<i class="fas fa-search"></i> Search';
            return;
        }
        
        // Call the search API
        fetch('/api/logs/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                rules: rules,
                search_term: searchTerm,
                limit: 100
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.processSearchResults(data.data);
            } else {
                alert(`Search failed: ${data.message}`);
            }
            
            // Restore search button
            this.searchButton.innerHTML = '<i class="fas fa-search"></i> Search';
        })
        .catch(error => {
            console.error('Search error:', error);
            alert(`Search error: ${error.message}`);
            this.searchButton.innerHTML = '<i class="fas fa-search"></i> Search';
        });
    }
    
    processSearchResults(results) {
        // Reset all log nodes
        if (window.cy && typeof window.cy.nodes === 'function') {
            try {
                window.cy.nodes('[type="log_stream"]').forEach(node => {
                    node.data('has_matches', false);
                    node.data('match_count', 0);
                    node.removeData('matches');
                });
            } catch (error) {
                console.error('Error resetting log nodes:', error);
            }
        }
        
        // Remove existing match badges
        this.clearMatchBadges();
        
        // Process search results
        let totalMatches = 0;
        let matchingLogs = 0;
        
        // For each rule with results
        Object.keys(results.target_logs || {}).forEach(ruleName => {
            const targets = results.target_logs[ruleName];
            
            // For each target with results
            Object.keys(targets).forEach(targetId => {
                const targetData = targets[targetId];
                const targetArn = targetData.arn;
                const logs = targetData.logs;
                
                if (!logs || !logs.success) return;
                
                // Find matching logs
                const matchingLogEntries = logs.logs.filter(log => 
                    log.matches && log.matches.length > 0
                );
                
                if (matchingLogEntries.length === 0) return;
                
                // Count matches
                matchingLogs += matchingLogEntries.length;
                let targetMatches = 0;
                matchingLogEntries.forEach(log => {
                    totalMatches += log.matches.length;
                    targetMatches += log.matches.length;
                });
                
                // Find the target node
                if (window.cy && typeof window.cy.nodes === 'function') {
                    try {
                        const targetNodes = window.cy.nodes(`[target_arn="${targetArn}"]`);
                        if (targetNodes.length === 0) return;
                        
                        // Find log stream nodes for this target
                        const logNodes = window.cy.nodes(`[type="log_stream"][target_arn="${targetArn}"]`);
                        if (logNodes.length === 0) return;
                        
                        // Update log nodes with match data
                        logNodes.forEach(node => {
                            node.data('has_matches', true);
                            node.data('match_count', targetMatches);
                            node.data('matches', matchingLogEntries);
                            
                            // Add a badge with match count
                            this.addMatchBadge(node, targetMatches);
                        });
                    } catch (error) {
                        console.error('Error updating log nodes with match data:', error);
                    }
                }
            });
        });
        
        // Update search stats
        if (this.matchCount) this.matchCount.textContent = totalMatches;
        if (this.logCount) this.logCount.textContent = matchingLogs;
        if (this.searchStats) this.searchStats.classList.remove('hidden');
        
        // Flash matching nodes
        if (window.cy && typeof window.cy.nodes === 'function') {
            try {
                const matchingNodes = window.cy.nodes('[has_matches="true"]');
                if (matchingNodes.length > 0 && typeof matchingNodes.flashClass === 'function') {
                    matchingNodes.flashClass('highlight-match', 1500);
                }
            } catch (error) {
                console.error('Error flashing matching nodes:', error);
            }
        }
    }
    
    addMatchBadge(node, matchCount) {
        try {
            if (!node || typeof node.renderedPosition !== 'function') {
                console.error('Invalid node or node.renderedPosition is not a function');
                return;
            }
            
            const pos = node.renderedPosition();
            if (!pos || typeof pos.x !== 'number' || typeof pos.y !== 'number') {
                console.error('Invalid node position:', pos);
                return;
            }
            
            const nodeWidth = node.renderedWidth ? node.renderedWidth() : 0;
            const nodeHeight = node.renderedHeight ? node.renderedHeight() : 0;
            
            const badge = document.createElement('div');
            badge.className = 'match-badge';
            badge.textContent = matchCount;
            badge.style.left = `${pos.x + nodeWidth/2 - 10}px`;
            badge.style.top = `${pos.y - nodeHeight/2 - 10}px`;
            
            document.body.appendChild(badge);
            this.matchBadges.push({
                element: badge,
                node: node
            });
            
            // Add click handler to show logs
            badge.addEventListener('click', (e) => {
                e.stopPropagation();
                this.showLogsForNode(node);
            });
        } catch (error) {
            console.error('Error adding match badge:', error);
        }
    }
    
    clearMatchBadges() {
        this.matchBadges.forEach(badge => {
            if (badge.element && badge.element.parentNode) {
                badge.element.parentNode.removeChild(badge.element);
            }
        });
        this.matchBadges = [];
    }
    
    updateMatchBadgePositions() {
        try {
            this.matchBadges.forEach(badge => {
                const node = badge.node;
                const element = badge.element;
                
                if (node && element && typeof node.renderedPosition === 'function') {
                    const pos = node.renderedPosition();
                    if (pos && typeof pos.x === 'number' && typeof pos.y === 'number') {
                        const nodeWidth = node.renderedWidth ? node.renderedWidth() : 0;
                        const nodeHeight = node.renderedHeight ? node.renderedHeight() : 0;
                        
                        element.style.left = `${pos.x + nodeWidth/2 - 10}px`;
                        element.style.top = `${pos.y - nodeHeight/2 - 10}px`;
                    }
                }
            });
        } catch (error) {
            console.error('Error updating match badge positions:', error);
        }
    }
    
    showLogsForNode(node) {
        const streamName = node.data('name');
        const targetArn = node.data('target_arn');
        const hasMatches = node.data('has_matches');
        const matches = node.data('matches');
        
        // Show the log content modal
        this.showLogContentModal(streamName);
        
        const logContent = document.getElementById('log-content');
        if (!logContent) return;
        
        logContent.innerHTML = '<div class="p-4 text-center">Loading logs...</div>';
        
        // If we already have matches from search, display them
        if (hasMatches && matches) {
            this.displayLogEntries(logContent, matches, true);
            return;
        }
        
        // Otherwise fetch logs for this stream
        fetch('/api/logs/stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                target_arn: targetArn,
                stream_name: streamName,
                limit: 50,
                search_term: this.searchTerm || null
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.displayLogEntries(logContent, data.data.logs, !!this.searchTerm);
            } else {
                logContent.innerHTML = `<div class="p-4 text-red-500">Error: ${data.message}</div>`;
            }
        })
        .catch(error => {
            logContent.innerHTML = `<div class="p-4 text-red-500">Failed to load logs: ${error.message}</div>`;
        });
    }
    
    showLogContentModal(streamName) {
        const modal = document.getElementById('log-content-modal');
        if (modal) {
            document.getElementById('stream-name').textContent = streamName;
            modal.classList.add('active');
        }
    }
    
    hideLogContentModal() {
        const modal = document.getElementById('log-content-modal');
        if (modal) {
            modal.classList.remove('active');
        }
    }
    
    displayLogEntries(container, logs, highlight = false) {
        if (!logs || logs.length === 0) {
            container.innerHTML = '<div class="p-4 text-center">No logs found</div>';
            return;
        }
        
        const logHtml = logs.map(log => {
            let message = log.message;
            
            // Apply syntax highlighting for JSON
            if (message.trim().startsWith('{') && message.trim().endsWith('}')) {
                try {
                    const jsonObj = JSON.parse(message);
                    message = this.formatJson(jsonObj, highlight ? log.matches : null);
                } catch (e) {
                    // Not valid JSON, continue with normal formatting
                }
            }
            
            // Highlight search matches if needed
            if (highlight && log.matches && log.matches.length > 0) {
                // Only highlight if we're not already formatting as JSON
                if (!message.includes('<span class="json-')) {
                    log.matches.forEach(match => {
                        const before = message.substring(0, match.start);
                        const matched = message.substring(match.start, match.end);
                        const after = message.substring(match.end);
                        message = `${before}<span class="bg-yellow-300 dark:bg-yellow-700">${matched}</span>${after}`;
                    });
                }
            }
            
            return `
                <div class="log-entry mb-2 pb-2 border-b border-gray-200 dark:border-gray-700">
                    <div class="log-timestamp text-xs text-gray-500 dark:text-gray-400">${log.formatted_time}</div>
                    <div class="log-message">${message}</div>
                </div>
            `;
        }).join('');
        
        container.innerHTML = logHtml;
    }
    
    formatJson(json, matches = null) {
        const jsonString = JSON.stringify(json, null, 2);
        
        // Basic syntax highlighting
        let highlighted = jsonString
            .replace(/("(\\u[a-zA-Z0-9]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false|null)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?)/g, match => {
                let cls = 'json-number';
                if (/^"/.test(match)) {
                    if (/:$/.test(match)) {
                        cls = 'json-key';
                    } else {
                        cls = 'json-string';
                    }
                } else if (/true|false/.test(match)) {
                    cls = 'json-boolean';
                } else if (/null/.test(match)) {
                    cls = 'json-null';
                }
                return `<span class="${cls}">${match}</span>`;
            });
        
        // Highlight search matches if provided
        if (matches && matches.length > 0 && this.searchTerm) {
            // This is more complex for JSON as we've already modified the string
            // A more sophisticated approach would be needed for accurate highlighting in JSON
            // For now, we'll just add a note that there are matches
            highlighted = `<div class="text-xs bg-yellow-100 dark:bg-yellow-900 p-1 mb-1 rounded">
                Contains ${matches.length} match(es) for "${this.searchTerm}"
            </div>${highlighted}`;
        }
        
        return `<pre class="json-formatter">${highlighted}</pre>`;
    }
}

// Export the LogObserver class
window.LogObserver = LogObserver;
