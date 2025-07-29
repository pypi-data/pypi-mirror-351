/**
 * Enhanced Log Viewer for EventBridge Visualizer
 * This module provides advanced log visualization and search capabilities
 */

class LogViewer {
    constructor(options = {}) {
        this.options = {
            containerSelector: '#log-viewer',
            searchInputSelector: '#log-search-input',
            searchButtonSelector: '#log-search-button',
            timeRangeSelector: '#log-time-range',
            refreshButtonSelector: '#log-refresh-button',
            ...options
        };
        
        // Don't try to access DOM elements immediately
        // Wait until DOM is fully loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.initialize());
        } else {
            // Small delay to ensure all elements are created
            setTimeout(() => this.initialize(), 100);
        }
        
        this.targetLogs = {};
        this.selectedTarget = null;
        this.searchTerm = '';
        this.timeRangeValue = '1h'; // Default to 1 hour
    }
    
    initialize() {
        // Find container
        this.container = document.querySelector(this.options.containerSelector);
        
        // Check if container exists before proceeding
        if (!this.container) {
            console.warn('Log viewer container not found. Creating container element.');
            // Create the container if it doesn't exist
            this.container = document.createElement('div');
            this.container.id = this.options.containerSelector.substring(1); // Remove the # from the selector
            document.body.appendChild(this.container);
        }
        
        // Initialize other elements
        this.searchInput = document.querySelector(this.options.searchInputSelector);
        this.searchButton = document.querySelector(this.options.searchButtonSelector);
        this.timeRange = document.querySelector(this.options.timeRangeSelector);
        this.refreshButton = document.querySelector(this.options.refreshButtonSelector);
        
        this.init();
    }
    
    init() {
        // Initialize UI components
        this.initUI();
        
        // Attach event listeners
        this.attachEventListeners();
    }
    
    initUI() {
        if (!this.container) {
            console.error('Log viewer container not found');
            return;
        }
        
        // Create the log viewer UI structure
        this.container.innerHTML = `
            <div class="log-viewer-header flex justify-between items-center mb-4">
                <div class="log-viewer-title text-lg font-bold">Log Viewer</div>
                <div class="log-viewer-controls flex gap-2">
                    <select id="log-time-range" class="p-2 rounded border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700">
                        <option value="15m">Last 15 minutes</option>
                        <option value="1h" selected>Last 1 hour</option>
                        <option value="3h">Last 3 hours</option>
                        <option value="6h">Last 6 hours</option>
                        <option value="12h">Last 12 hours</option>
                        <option value="24h">Last 24 hours</option>
                        <option value="3d">Last 3 days</option>
                        <option value="7d">Last 7 days</option>
                        <option value="14d">Last 14 days</option>
                        <option value="30d">Last 30 days</option>
                    </select>
                    <button id="log-refresh-button" class="bg-aws-orange hover:bg-amber-600 text-white py-2 px-3 rounded font-medium">
                        <i class="fas fa-sync-alt"></i> Refresh
                    </button>
                </div>
            </div>
            
            <div class="log-viewer-search mb-4">
                <div class="flex">
                    <input type="text" id="log-search-input" placeholder="Search logs..." 
                           class="p-2 rounded-l border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 flex-grow">
                    <button id="log-search-button" class="bg-aws-darkblue hover:bg-blue-800 text-white py-2 px-4 rounded-r font-medium">
                        <i class="fas fa-search"></i> Search
                    </button>
                </div>
                <div id="log-search-info" class="text-sm mt-1 text-gray-500 dark:text-gray-400 hidden">
                    Showing results for "<span id="search-term-display"></span>" 
                    (<span id="search-results-count">0</span> matches in <span id="search-logs-count">0</span> logs)
                </div>
            </div>
            
            <div class="log-viewer-tabs mb-4">
                <div class="flex border-b border-gray-300 dark:border-gray-600">
                    <button id="tab-all-logs" class="tab-button py-2 px-4 font-medium border-b-2 border-aws-orange">All Logs</button>
                    <button id="tab-search-results" class="tab-button py-2 px-4 font-medium border-b-2 border-transparent">Search Results</button>
                    <button id="tab-log-streams" class="tab-button py-2 px-4 font-medium border-b-2 border-transparent">Log Streams</button>
                </div>
            </div>
            
            <div class="log-viewer-content">
                <div id="tab-content-all-logs" class="tab-content">
                    <div id="log-entries" class="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded p-2 h-96 overflow-y-auto font-mono text-sm"></div>
                </div>
                <div id="tab-content-search-results" class="tab-content hidden">
                    <div id="search-entries" class="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded p-2 h-96 overflow-y-auto font-mono text-sm"></div>
                </div>
                <div id="tab-content-log-streams" class="tab-content hidden">
                    <div id="log-streams" class="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded p-2 h-96 overflow-y-auto"></div>
                </div>
            </div>
            
            <div id="log-status" class="mt-2 text-sm text-gray-500 dark:text-gray-400">
                No logs loaded
            </div>
        `;
        
        // Update references to newly created elements
        this.searchInput = document.querySelector(this.options.searchInputSelector);
        this.searchButton = document.querySelector(this.options.searchButtonSelector);
        this.timeRange = document.querySelector(this.options.timeRangeSelector);
        this.refreshButton = document.querySelector(this.options.refreshButtonSelector);
        
        // Tab elements
        this.tabButtons = this.container.querySelectorAll('.tab-button');
        this.tabContents = this.container.querySelectorAll('.tab-content');
        
        // Log content elements
        this.logEntries = this.container.querySelector('#log-entries');
        this.searchEntries = this.container.querySelector('#search-entries');
        this.logStreams = this.container.querySelector('#log-streams');
        this.logStatus = this.container.querySelector('#log-status');
        
        // Search info elements
        this.searchInfo = this.container.querySelector('#log-search-info');
        this.searchTermDisplay = this.container.querySelector('#search-term-display');
        this.searchResultsCount = this.container.querySelector('#search-results-count');
        this.searchLogsCount = this.container.querySelector('#search-logs-count');
    }
    
    attachEventListeners() {
        // Check if elements exist before attaching listeners
        if (!this.container) {
            console.error('Cannot attach event listeners: container not found');
            return;
        }
        
        // Search button click
        if (this.searchButton) {
            this.searchButton.addEventListener('click', () => this.searchLogs());
        }
        
        // Search input enter key
        if (this.searchInput) {
            this.searchInput.addEventListener('keyup', (e) => {
                if (e.key === 'Enter') {
                    this.searchLogs();
                }
            });
        }
        
        // Time range change
        if (this.timeRange) {
            this.timeRange.addEventListener('change', () => {
                this.timeRangeValue = this.timeRange.value;
                if (this.selectedTarget) {
                    this.loadTargetLogs(this.selectedTarget);
                }
            });
        }
        
        // Refresh button click
        if (this.refreshButton) {
            this.refreshButton.addEventListener('click', () => {
                if (this.selectedTarget) {
                    this.loadTargetLogs(this.selectedTarget);
                }
            });
        }
        
        // Tab switching
        const tabButtons = this.container.querySelectorAll('.tab-button');
        const tabContents = this.container.querySelectorAll('.tab-content');
        
        if (tabButtons && tabButtons.length > 0) {
            tabButtons.forEach(button => {
                button.addEventListener('click', () => {
                    const tabId = button.id.replace('tab-', 'tab-content-');
                    
                    // Update active tab button
                    tabButtons.forEach(btn => {
                        btn.classList.remove('border-aws-orange');
                        btn.classList.add('border-transparent');
                    });
                    button.classList.remove('border-transparent');
                    button.classList.add('border-aws-orange');
                    
                    // Show selected tab content
                    tabContents.forEach(content => {
                        content.classList.add('hidden');
                    });
                    const tabContent = document.getElementById(tabId);
                    if (tabContent) {
                        tabContent.classList.remove('hidden');
                    }
                });
            });
        }
    }
    
    // Set the target to display logs for
    setTarget(targetArn, targetId, ruleName) {
        this.selectedTarget = {
            arn: targetArn,
            id: targetId,
            rule: ruleName
        };
        
        // Load logs for the selected target
        this.loadTargetLogs(this.selectedTarget);
    }
    
    // Load logs for a target
    loadTargetLogs(target) {
        // Show loading state
        this.logStatus.textContent = `Loading logs for ${target.id}...`;
        this.logEntries.innerHTML = '<div class="p-4 text-center">Loading...</div>';
        
        // Calculate time range
        const endTime = Math.floor(Date.now() / 1000);
        let startTime = endTime;
        
        switch (this.timeRangeValue) {
            case '15m': startTime = endTime - (15 * 60); break;
            case '1h': startTime = endTime - (60 * 60); break;
            case '3h': startTime = endTime - (3 * 60 * 60); break;
            case '6h': startTime = endTime - (6 * 60 * 60); break;
            case '12h': startTime = endTime - (12 * 60 * 60); break;
            case '24h': startTime = endTime - (24 * 60 * 60); break;
            case '3d': startTime = endTime - (3 * 24 * 60 * 60); break;
            case '7d': startTime = endTime - (7 * 24 * 60 * 60); break;
            case '14d': startTime = endTime - (14 * 24 * 60 * 60); break;
            case '30d': startTime = endTime - (30 * 24 * 60 * 60); break;
            default: startTime = endTime - (60 * 60); // Default to 1 hour
        }
        
        // Make API request to get logs
        fetch('/api/logs/target', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                target_arn: target.arn,
                limit: 100,
                start_time: startTime,
                end_time: endTime,
                search_term: this.searchTerm || null
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.targetLogs[target.arn] = data.data;
                this.renderLogs(data.data);
            } else {
                this.logStatus.textContent = `Error: ${data.message}`;
                this.logEntries.innerHTML = `<div class="p-4 text-red-500">${data.message}</div>`;
            }
        })
        .catch(error => {
            this.logStatus.textContent = `Error: ${error.message}`;
            this.logEntries.innerHTML = `<div class="p-4 text-red-500">Failed to load logs: ${error.message}</div>`;
        });
    }
    
    // Render logs in the UI
    renderLogs(logData) {
        // Clear existing logs
        this.logEntries.innerHTML = '';
        this.searchEntries.innerHTML = '';
        this.logStreams.innerHTML = '';
        
        if (!logData.success) {
            this.logStatus.textContent = logData.message;
            this.logEntries.innerHTML = `<div class="p-4 text-red-500">${logData.message}</div>`;
            return;
        }
        
        const logs = logData.logs;
        const metadata = logData.metadata;
        
        // Update status
        this.logStatus.textContent = `${logs.length} log entries from ${metadata.log_group} (${metadata.start_time} to ${metadata.end_time})`;
        
        if (logs.length === 0) {
            this.logEntries.innerHTML = '<div class="p-4 text-center">No logs found in the selected time range</div>';
            return;
        }
        
        // Render all logs
        const allLogsHtml = logs.map(log => this.formatLogEntry(log)).join('');
        this.logEntries.innerHTML = allLogsHtml;
        
        // Render search results if search term is provided
        if (this.searchTerm) {
            const searchResults = logs.filter(log => log.matches && log.matches.length > 0);
            
            if (searchResults.length > 0) {
                const searchHtml = searchResults.map(log => this.formatLogEntry(log, true)).join('');
                this.searchEntries.innerHTML = searchHtml;
                
                // Update search info
                this.searchInfo.classList.remove('hidden');
                this.searchTermDisplay.textContent = this.searchTerm;
                
                // Count total matches
                const totalMatches = searchResults.reduce((sum, log) => sum + log.matches.length, 0);
                this.searchResultsCount.textContent = totalMatches;
                this.searchLogsCount.textContent = searchResults.length;
                
                // Switch to search results tab
                document.getElementById('tab-search-results').click();
            } else {
                this.searchEntries.innerHTML = `<div class="p-4 text-center">No matches found for "${this.searchTerm}"</div>`;
                this.searchInfo.classList.remove('hidden');
                this.searchTermDisplay.textContent = this.searchTerm;
                this.searchResultsCount.textContent = '0';
                this.searchLogsCount.textContent = '0';
            }
        } else {
            this.searchInfo.classList.add('hidden');
        }
        
        // Render log streams info
        if (metadata.streams) {
            const streamsHtml = metadata.streams.map(stream => {
                const firstTime = new Date(stream.firstEventTimestamp).toLocaleString();
                const lastTime = new Date(stream.lastEventTimestamp).toLocaleString();
                
                return `
                    <div class="log-stream mb-4 p-3 border border-gray-200 dark:border-gray-700 rounded">
                        <div class="font-bold">${stream.name}</div>
                        <div class="text-sm">
                            <div>First event: ${firstTime}</div>
                            <div>Last event: ${lastTime}</div>
                            <div>Events: ${stream.logEvents.length}</div>
                        </div>
                        <button class="view-stream-btn mt-2 bg-aws-darkblue hover:bg-blue-800 text-white py-1 px-2 rounded text-sm"
                                data-stream="${stream.name}">
                            View Events
                        </button>
                    </div>
                `;
            }).join('');
            
            this.logStreams.innerHTML = streamsHtml;
            
            // Add event listeners to stream buttons
            const streamButtons = this.logStreams.querySelectorAll('.view-stream-btn');
            streamButtons.forEach(button => {
                button.addEventListener('click', () => {
                    const streamName = button.getAttribute('data-stream');
                    this.filterLogsByStream(streamName);
                });
            });
        }
    }
    
    // Format a log entry for display
    formatLogEntry(log, highlight = false) {
        const timestamp = log.formatted_time;
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
                <div class="log-timestamp text-xs text-gray-500 dark:text-gray-400">${timestamp}</div>
                <div class="log-message whitespace-pre-wrap">${message}</div>
            </div>
        `;
    }
    
    // Format JSON with syntax highlighting
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
        if (matches && matches.length > 0) {
            // This is more complex for JSON as we've already modified the string
            // A more sophisticated approach would be needed for accurate highlighting in JSON
            // For now, we'll just add a note that there are matches
            highlighted = `<div class="text-xs bg-yellow-100 dark:bg-yellow-900 p-1 mb-1 rounded">
                Contains ${matches.length} match(es) for "${this.searchTerm}"
            </div>${highlighted}`;
        }
        
        return `<pre class="json-formatter">${highlighted}</pre>`;
    }
    
    // Filter logs by stream
    filterLogsByStream(streamName) {
        if (!this.selectedTarget || !this.targetLogs[this.selectedTarget.arn]) {
            return;
        }
        
        const logData = this.targetLogs[this.selectedTarget.arn];
        const logs = logData.logs.filter(log => log.stream === streamName);
        
        // Update the log entries view
        this.logEntries.innerHTML = '';
        
        if (logs.length === 0) {
            this.logEntries.innerHTML = `<div class="p-4 text-center">No logs found in stream "${streamName}"</div>`;
            return;
        }
        
        const logsHtml = logs.map(log => this.formatLogEntry(log)).join('');
        this.logEntries.innerHTML = logsHtml;
        
        // Update status
        this.logStatus.textContent = `Showing ${logs.length} logs from stream "${streamName}"`;
        
        // Switch to all logs tab
        document.getElementById('tab-all-logs').click();
    }
    
    // Search logs
    searchLogs() {
        if (!this.searchInput || !this.selectedTarget) {
            return;
        }
        
        const searchTerm = this.searchInput.value.trim();
        
        if (searchTerm === '') {
            // Clear search
            this.searchTerm = '';
            this.searchInfo.classList.add('hidden');
            
            // Reload logs without search term
            this.loadTargetLogs(this.selectedTarget);
            return;
        }
        
        this.searchTerm = searchTerm;
        
        // Reload logs with search term
        this.loadTargetLogs(this.selectedTarget);
    }
    
    // Global search across all targets
    globalSearch(rules, searchTerm) {
        if (!searchTerm || searchTerm.trim() === '') {
            return;
        }
        
        // Show loading state
        this.logStatus.textContent = `Searching across all targets...`;
        this.searchEntries.innerHTML = '<div class="p-4 text-center">Searching...</div>';
        
        // Make API request to search logs
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
                this.renderGlobalSearchResults(data.data, searchTerm);
            } else {
                this.logStatus.textContent = `Error: ${data.message}`;
                this.searchEntries.innerHTML = `<div class="p-4 text-red-500">${data.message}</div>`;
            }
        })
        .catch(error => {
            this.logStatus.textContent = `Error: ${error.message}`;
            this.searchEntries.innerHTML = `<div class="p-4 text-red-500">Search failed: ${error.message}</div>`;
        });
    }
    
    // Render global search results
    renderGlobalSearchResults(searchData, searchTerm) {
        // Update search term
        this.searchTerm = searchTerm;
        
        // Clear existing search results
        this.searchEntries.innerHTML = '';
        
        // Update search info
        this.searchInfo.classList.remove('hidden');
        this.searchTermDisplay.textContent = searchTerm;
        
        // Count total matches
        let totalMatches = 0;
        let totalLogs = 0;
        
        // Process target logs
        const targetLogs = searchData.target_logs || {};
        const ruleNames = Object.keys(targetLogs);
        
        if (ruleNames.length === 0) {
            this.searchEntries.innerHTML = `<div class="p-4 text-center">No matches found for "${searchTerm}"</div>`;
            this.searchResultsCount.textContent = '0';
            this.searchLogsCount.textContent = '0';
            return;
        }
        
        let resultsHtml = '';
        
        // Process each rule
        ruleNames.forEach(ruleName => {
            const targets = targetLogs[ruleName];
            const targetIds = Object.keys(targets);
            
            // Process each target
            targetIds.forEach(targetId => {
                const targetData = targets[targetId];
                const logs = targetData.logs;
                
                if (!logs || !logs.success) {
                    return;
                }
                
                // Filter logs with matches
                const matchingLogs = logs.logs.filter(log => log.matches && log.matches.length > 0);
                
                if (matchingLogs.length === 0) {
                    return;
                }
                
                // Count matches
                totalLogs += matchingLogs.length;
                matchingLogs.forEach(log => {
                    totalMatches += log.matches.length;
                });
                
                // Add rule and target header
                resultsHtml += `
                    <div class="search-result-group mb-4">
                        <div class="search-result-header bg-aws-darkblue text-white p-2 rounded-t">
                            <div class="font-bold">${ruleName}</div>
                            <div class="text-sm">Target: ${targetId} (${targetData.arn})</div>
                        </div>
                        <div class="search-result-logs border border-t-0 border-gray-300 dark:border-gray-600 rounded-b p-2">
                `;
                
                // Add matching logs
                matchingLogs.forEach(log => {
                    resultsHtml += this.formatLogEntry(log, true);
                });
                
                resultsHtml += `
                        </div>
                    </div>
                `;
            });
        });
        
        // Update search counts
        this.searchResultsCount.textContent = totalMatches;
        this.searchLogsCount.textContent = totalLogs;
        
        // Display results
        if (resultsHtml) {
            this.searchEntries.innerHTML = resultsHtml;
        } else {
            this.searchEntries.innerHTML = `<div class="p-4 text-center">No matches found for "${searchTerm}"</div>`;
        }
        
        // Update status
        this.logStatus.textContent = `Found ${totalMatches} matches in ${totalLogs} logs across ${ruleNames.length} rules`;
        
        // Switch to search results tab
        document.getElementById('tab-search-results').click();
    }
}

// Export the LogViewer class
window.LogViewer = LogViewer;
