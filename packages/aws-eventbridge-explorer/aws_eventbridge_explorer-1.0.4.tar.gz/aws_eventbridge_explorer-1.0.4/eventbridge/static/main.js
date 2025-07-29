// Function to display log streams in the UI with Tailwind styling
function displayLogStreams(streams) {
  const streamsList = document.getElementById("log-streams-container");
  streamsList.innerHTML = "";

  if (streams.length === 0) {
    streamsList.innerHTML =
      '<div class="p-4 text-center text-gray-500 dark:text-gray-400">No log streams found</div>';
    return;
  }

  // Add a search/filter input
  const searchContainer = document.createElement("div");
  searchContainer.className =
    "p-3 bg-gray-200 dark:bg-gray-800 border-b border-gray-300 dark:border-gray-700";

  const searchInput = document.createElement("input");
  searchInput.type = "text";
  searchInput.placeholder = "Search streams...";
  searchInput.className =
    "w-full p-2 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200";
  searchInput.addEventListener("input", function () {
    const searchTerm = this.value.toLowerCase();
    document.querySelectorAll(".log-stream-item").forEach((item) => {
      const streamName = item
        .querySelector(".stream-name")
        .textContent.toLowerCase();
      if (streamName.includes(searchTerm)) {
        item.style.display = "flex";
      } else {
        item.style.display = "none";
      }
    });
  });

  searchContainer.appendChild(searchInput);
  streamsList.appendChild(searchContainer);

  // Create a container for the streams
  const streamsContainer = document.createElement("div");
  streamsContainer.className =
    "max-h-[300px] overflow-y-auto bg-gray-900 text-gray-200";

  // Sort streams by last event time (most recent first)
  streams.sort((a, b) => {
    const aTime = a.lastEventTimestamp || 0;
    const bTime = b.lastEventTimestamp || 0;
    return bTime - aTime;
  });

  console.log(`Displaying ${streams.length} log streams`);

  // Add streams to the container
  streams.forEach((stream) => {
    console.log(`Stream: ${stream.logStreamName}`);

    const streamItem = document.createElement("div");
    streamItem.className =
      "log-stream-item flex items-center justify-between p-3 border-b border-gray-700 cursor-pointer hover:bg-gray-800 transition-colors";
    streamItem.dataset.logGroup = stream.logGroupName;
    streamItem.dataset.logStream = stream.logStreamName;

    // Create a container for stream info
    const streamInfo = document.createElement("div");
    streamInfo.className = "flex-1";

    const streamName = document.createElement("div");
    streamName.className = "stream-name font-bold text-aws-lightblue";
    streamName.textContent = stream.logStreamName;

    const streamDate = document.createElement("div");
    streamDate.className = "text-gray-400 text-xs mt-1";

    // Format the date with the same color as log timestamps
    if (stream.lastEventTime) {
      const dateSpan = document.createElement("span");
      dateSpan.className = "text-aws-lightblue";
      dateSpan.textContent = stream.lastEventTime;
      streamDate.innerHTML = "Last event: ";
      streamDate.appendChild(dateSpan);
    } else {
      streamDate.textContent = "Last event: Unknown";
    }

    streamInfo.appendChild(streamName);
    streamInfo.appendChild(streamDate);

    // Create view button
    const viewButton = document.createElement("button");
    viewButton.className =
      "text-aws-lightblue hover:text-white p-2 rounded-full hover:bg-gray-700 transition-colors";
    viewButton.innerHTML = '<i class="fas fa-eye"></i>';
    viewButton.title = "View logs";

    streamItem.appendChild(streamInfo);
    streamItem.appendChild(viewButton);

    // Add click handler for the view button
    viewButton.addEventListener("click", function (e) {
      e.stopPropagation(); // Prevent triggering the parent click event

      // Fetch logs directly when clicking the view button
      fetchStreamLogs(
        this.parentElement.dataset.logGroup,
        this.parentElement.dataset.logStream,
      );

      // Remove selected class from all items
      document.querySelectorAll(".log-stream-item").forEach((item) => {
        item.classList.remove(
          "selected",
          "bg-gray-800",
          "border-l-4",
          "border-aws-lightblue",
        );
      });

      // Add selected class to this item's parent
      this.parentElement.classList.add(
        "selected",
        "bg-gray-800",
        "border-l-4",
        "border-aws-lightblue",
      );
    });

    // Add click handler to the stream item itself
    streamItem.addEventListener("click", function () {
      // Remove selected class from all items
      document.querySelectorAll(".log-stream-item").forEach((item) => {
        item.classList.remove(
          "selected",
          "bg-gray-800",
          "border-l-4",
          "border-aws-lightblue",
        );
      });

      // Add selected class to this item
      this.classList.add(
        "selected",
        "bg-gray-800",
        "border-l-4",
        "border-aws-lightblue",
      );

      // Show the fetch logs button
      const fetchLogsBtn = document.getElementById("fetch-logs-btn");
      fetchLogsBtn.classList.remove("hidden");

      // Update status message
      document.getElementById("logs-content-container").textContent =
        `Selected stream: ${this.dataset.logStream}\nClick "Fetch Logs" to view logs`;

      // Log the data attributes for debugging
      console.log(
        `Selected stream: ${this.dataset.logStream} in group: ${this.dataset.logGroup}`,
      );

      fetchLogsBtn.onclick = () =>
        fetchStreamLogs(this.dataset.logGroup, this.dataset.logStream);
    });

    streamsContainer.appendChild(streamItem);
  });

  streamsList.appendChild(streamsContainer);

  // Add a select all button and quick actions
  const actionsContainer = document.createElement("div");
  actionsContainer.className =
    "p-3 bg-gray-200 dark:bg-gray-800 border-t border-gray-300 dark:border-gray-700 flex justify-between";

  const selectRecentBtn = document.createElement("button");
  selectRecentBtn.textContent = "Select Most Recent";
  selectRecentBtn.className =
    "bg-blue-600 hover:bg-blue-700 text-white py-1 px-3 rounded text-sm";
  selectRecentBtn.addEventListener("click", function () {
    // Select the first (most recent) stream
    const firstStream = document.querySelector(".log-stream-item");
    if (firstStream) {
      firstStream.click();
    }
  });

  actionsContainer.appendChild(selectRecentBtn);
  streamsList.appendChild(actionsContainer);

  // Auto-select the most recent stream
  const firstStream = document.querySelector(".log-stream-item");
  if (firstStream) {
    firstStream.click();
  }
}

// Helper function to format logs with Tailwind classes
function formatLogsWithTailwind(logText) {
  if (!logText || logText.trim() === "") {
    return '<div class="p-4 text-center text-gray-500 dark:text-gray-400">No logs available</div>';
  }

  const lines = logText.split("\n");
  let formattedHtml = '<div class="text-sm font-mono whitespace-pre-wrap overflow-y-auto p-4 bg-gray-900 text-gray-200 rounded max-h-[70vh] h-[70vh]">';

  lines.forEach((line) => {
    // Try to extract timestamp at the beginning (format: YYYY-MM-DD HH:MM:SS)
    const timestampMatch = line.match(/^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})/);
    
    if (timestampMatch) {
      const timestamp = timestampMatch[1];
      const message = line.substring(timestamp.length).trim();
      formattedHtml += `<div class="mb-1">`;
      formattedHtml += `<span class="text-blue-400 mr-2">[${timestamp}]</span>`;
      formattedHtml += `<span>${escapeHtml(message)}</span>`;
      formattedHtml += `</div>`;
    } else {
      formattedHtml += `<div class="mb-1">${escapeHtml(line)}</div>`;
    }
  });

  formattedHtml += '</div>';
  return formattedHtml;
}

// Function to fetch log streams for a target
async function fetchLogStreams(targetArn) {
  if (!targetArn) {
    document.getElementById("logs-content-container").textContent =
      "Error: No target ARN available";
    return;
  }

  // Get date range values
  const startDateInput = document.getElementById("start-date").value;
  const endDateInput = document.getElementById("end-date").value;

  let startTime = null;
  let endTime = null;

  if (startDateInput) {
    startTime = new Date(startDateInput).getTime() / 1000; // Convert to seconds
  }

  if (endDateInput) {
    endTime = new Date(endDateInput).getTime() / 1000; // Convert to seconds
  } else {
    // If no end date is specified, use current time
    endTime = Math.floor(Date.now() / 1000);
  }

  document.getElementById("logs-content-container").textContent =
    "Fetching log streams...";
  document.getElementById("fetch-streams-btn").disabled = true;
  document.getElementById("fetch-streams-btn").textContent = "Fetching...";
  document.getElementById("fetch-logs-btn").classList.add("hidden");

  try {
    const response = await fetch("/api/target_log_streams", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        targetArn: targetArn,
        startTime: startTime,
        endTime: endTime,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch log streams");
    }

    const data = await response.json();

    if (data.streams && data.streams.length > 0) {
      // Display the log streams
      displayLogStreams(data.streams);
      document.getElementById("logs-content-container").textContent =
        "Select a log stream to view logs";
    } else {
      document.getElementById("logs-content-container").textContent =
        "No log streams available for this resource";
      document.getElementById("log-streams-container").innerHTML = "";
    }
  } catch (error) {
    console.error("Error fetching log streams:", error);
    document.getElementById("logs-content-container").textContent =
      `Error fetching log streams: ${error.message}`;
    document.getElementById("log-streams-container").innerHTML = "";
  } finally {
    document.getElementById("fetch-streams-btn").disabled = false;
    document.getElementById("fetch-streams-btn").textContent =
      "Fetch Log Streams";
  }
}

// Function to fetch logs from a specific stream
async function fetchStreamLogs(logGroup, logStream) {
  if (!logGroup || !logStream) {
    document.getElementById("logs-content-container").textContent =
      "Error: Log group or stream name missing";
    return;
  }

  console.log(`Fetching logs from stream: ${logStream} in group: ${logGroup}`);
  document.getElementById("logs-content-container").textContent =
    "Fetching logs from stream...";
  document.getElementById("fetch-logs-btn").disabled = true;
  document.getElementById("fetch-logs-btn").textContent = "Fetching...";

  try {
    const response = await fetch("/api/stream_logs", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        logGroup: logGroup,
        logStream: logStream,
        limit: 100,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to fetch logs");
    }

    const data = await response.json();
    console.log("Received log data:", data);

    if (data.logs) {
      // Format logs with Tailwind classes
      const formattedLogs = formatLogsWithTailwind(data.logs);
      document.getElementById("logs-content-container").innerHTML =
        formattedLogs;
    } else {
      document.getElementById("logs-content-container").innerHTML =
        '<div class="p-4 text-center text-gray-500 dark:text-gray-400">No logs available in this stream</div>';
    }
  } catch (error) {
    console.error("Error fetching stream logs:", error);
    document.getElementById("logs-content-container").textContent =
      `Error fetching logs: ${error.message}`;
  } finally {
    document.getElementById("fetch-logs-btn").disabled = false;
    document.getElementById("fetch-logs-btn").textContent = "Fetch Logs";
  }
}

// Function to fetch event buses
async function fetchEventBuses() {
  try {
    const eventBusSelect = document.getElementById("event-bus-select");
    console.log("Starting fetchEventBuses, current state:", {
      disabled: eventBusSelect.disabled,
      options: eventBusSelect.options.length,
      innerHTML: eventBusSelect.innerHTML
    });
    
    eventBusSelect.innerHTML = '<option value="">Loading event buses...</option>';
    // Commented out to prevent disabling
    // eventBusSelect.disabled = true;

    // Show loading message
    document.getElementById("event-bus-name").textContent = "Loading event buses...";
    document.getElementById("event-bus-name").classList.add("animate-pulse");

    const response = await fetch("/api/event-buses");
    console.log("API response status:", response.status);
    
    if (!response.ok) {
      console.error("API error response:", await response.clone().text());
      throw new Error("Failed to fetch event buses");
    }

    const data = await response.json();
    console.log("API response data:", data);
    
    // Use our force update function instead of manual updates
    forceUpdateEventBusDropdown(data.data || []);
    
    // If there's only one event bus, select it automatically
    const eventBuses = data.data || [];
    if (eventBuses.length === 1) {
      console.log("Auto-selecting the only event bus:", eventBuses[0].Name);
      setTimeout(() => {
        eventBusSelect.value = eventBuses[0].Name;
        // Trigger change event manually
        const event = new Event('change');
        eventBusSelect.dispatchEvent(event);
      }, 100);
    }
  } catch (error) {
    console.error("Error fetching event buses:", error);
    
    // Force update with empty array to show error state
    forceUpdateEventBusDropdown([]);
    
    // Show error in UI
    document.getElementById("error-message").textContent = error.toString();
    document.getElementById("error").classList.remove("hidden");
    document.getElementById("error").style.display = "block";
  } finally {
    // Always ensure the dropdown is enabled
    const eventBusSelect = document.getElementById("event-bus-select");
    if (eventBusSelect) {
      eventBusSelect.disabled = false;
      eventBusSelect.removeAttribute('disabled');
      console.log("Final dropdown state:", {
        disabled: eventBusSelect.disabled,
        options: eventBusSelect.options.length,
        innerHTML: eventBusSelect.innerHTML.substring(0, 50) + "..."
      });
    }
  }
}

// Function to handle event bus selection
async function handleEventBusSelection(busName) {
  if (!busName) return;

  try {
    console.log("Handling selection of event bus:", busName);
    document.getElementById("loading").style.display = "block";
    document.getElementById("event-bus-name").textContent =
      `Loading ${busName}...`;
    document.getElementById("event-bus-name").classList.add("animate-pulse");
    document.getElementById("rules-info").textContent = "Loading rules...";

    // Fetch rules for the selected event bus
    const response = await fetch(`/api/rules?event_bus=${encodeURIComponent(busName)}`);
    console.log("Rules API response status:", response.status);
    
    const data = await response.json();
    console.log("Rules API response:", data);
    
    if (!response.ok || !data.success) {
      throw new Error(data.message || "Failed to fetch rules");
    }

    // Update UI
    document.getElementById("event-bus-name").textContent =
      `Event Bus: ${busName}`;
    document.getElementById("event-bus-name").classList.remove("animate-pulse");
    document.getElementById("rules-info").textContent =
      `${data.rules.length} rules available`;

    // Store rules for later use
    window.availableRules = data.data;
    
    // Update rules count
    document.getElementById("rules-info").textContent = 
      `${data.data.length} rules available`;
    
    // Populate rules list
    const rulesList = document.getElementById("rules-list");
    rulesList.innerHTML = "";
    
    if (data.data.length === 0) {
      rulesList.innerHTML = '<div class="text-gray-500 dark:text-gray-400 text-sm">No rules found for this event bus</div>';
    } else {
      data.data.forEach(rule => {
        const ruleItem = document.createElement("div");
        ruleItem.className = "flex items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700";
        
        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.className = "rule-checkbox mr-2";
        checkbox.value = rule.Name;
        checkbox.id = `rule-${rule.Name}`;
        
        const label = document.createElement("label");
        label.htmlFor = `rule-${rule.Name}`;
        label.className = "flex-grow cursor-pointer";
        label.textContent = rule.Name;
        
        ruleItem.appendChild(checkbox);
        ruleItem.appendChild(label);
        rulesList.appendChild(ruleItem);
      });
    }

    document.getElementById("loading").style.display = "none";
    document.getElementById("event-bus-name").classList.remove("animate-pulse");
  } catch (error) {
    console.error("Error selecting event bus:", error);
    document.getElementById("event-bus-name").textContent =
      "Error selecting event bus";
    document.getElementById("event-bus-name").classList.remove("animate-pulse");
    document.getElementById("rules-info").textContent = "Error loading rules";
    document.getElementById("loading").style.display = "none";
    document.getElementById("error-message").textContent = error.toString();
    document.getElementById("error").classList.remove("hidden");
    document.getElementById("error").style.display = "block";
  }
}

// Function to apply rule selection
async function applyRuleSelection() {
  const selectedRules = [];
  document.querySelectorAll(".rule-checkbox:checked").forEach((checkbox) => {
    selectedRules.push(checkbox.value);
  });

  try {
    document.getElementById("loading").style.display = "block";
    document.getElementById("rules-info").textContent = "Updating graph...";

    const response = await fetch("/api/select_rules", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        rules: selectedRules,
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to update rules");
    }

    const data = await response.json();

    // Update UI
    if (selectedRules.length > 0) {
      const ruleCount = selectedRules.length;
      const rulesList = selectedRules.slice(0, 3).join(", ");
      const moreText = ruleCount > 3 ? ` and ${ruleCount - 3} more...` : "";
      document.getElementById("rules-info").textContent =
        `Rules: ${rulesList}${moreText}`;
    } else {
      document.getElementById("rules-info").textContent = "No rules selected";
    }

    // Reload graph data if rules were updated
    if (data.graphUpdated) {
      loadGraphData();
    }

    document.getElementById("loading").style.display = "none";
  } catch (error) {
    console.error("Error updating rules:", error);
    document.getElementById("rules-info").textContent = "Error updating rules";
    document.getElementById("loading").style.display = "none";
    document.getElementById("error-message").textContent = error.toString();
    document.getElementById("error").style.display = "block";
  }
}

// Function to show rules selection modal with Tailwind styling
function showRulesModal() {
  // Check if an event bus is selected
  if (!window.availableRules) {
    alert("Please select an event bus first");
    return;
  }

  // Create modal if it doesn't exist
  let rulesModal = document.getElementById("rules-modal");
  if (!rulesModal) {
    rulesModal = document.createElement("div");
    rulesModal.id = "rules-modal";
    rulesModal.className =
      "fixed inset-0 bg-black/40 z-20 flex items-center justify-center";

    const modalContent = document.createElement("div");
    modalContent.className =
      "bg-white dark:bg-gray-800 p-5 rounded-lg shadow-lg w-full max-w-lg mx-4";

    // Header
    const modalHeader = document.createElement("div");
    modalHeader.className =
      "flex justify-between items-center border-b border-gray-200 dark:border-gray-700 pb-3 mb-4";
    modalHeader.innerHTML = `
            <div class="text-lg font-bold">Select Rules</div>
            <span class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 text-2xl font-bold cursor-pointer">&times;</span>
        `;

    // Body
    const modalBody = document.createElement("div");
    modalBody.className = "max-h-[70vh] overflow-y-auto";

    // Rules list container
    const rulesContainer = document.createElement("div");
    rulesContainer.id = "rules-container";
    rulesContainer.className = "max-h-[400px] overflow-y-auto";

    // Search box
    const searchBox = document.createElement("input");
    searchBox.type = "text";
    searchBox.placeholder = "Search rules...";
    searchBox.className =
      "w-full p-2 mb-3 border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200";

    searchBox.addEventListener("input", function () {
      const searchTerm = this.value.toLowerCase();
      document.querySelectorAll(".rule-item").forEach((item) => {
        const ruleName = item.querySelector("label").textContent.toLowerCase();
        if (ruleName.includes(searchTerm)) {
          item.style.display = "flex";
        } else {
          item.style.display = "none";
        }
      });
    });

    // Action buttons
    const actionButtons = document.createElement("div");
    actionButtons.className = "flex justify-between mt-4";

    const selectAllBtn = document.createElement("button");
    selectAllBtn.textContent = "Select All";
    selectAllBtn.className =
      "bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 py-2 px-4 rounded";
    selectAllBtn.addEventListener("click", () => {
      document.querySelectorAll(".rule-checkbox").forEach((checkbox) => {
        checkbox.checked = true;
      });
    });

    const clearAllBtn = document.createElement("button");
    clearAllBtn.textContent = "Clear All";
    clearAllBtn.className =
      "bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 text-gray-800 dark:text-gray-200 py-2 px-4 rounded";
    clearAllBtn.addEventListener("click", () => {
      document.querySelectorAll(".rule-checkbox").forEach((checkbox) => {
        checkbox.checked = false;
      });
    });

    const applyBtn = document.createElement("button");
    applyBtn.textContent = "Apply Selection";
    applyBtn.className =
      "bg-aws-orange hover:bg-amber-600 text-white py-2 px-4 rounded";
    applyBtn.addEventListener("click", () => {
      applyRuleSelection();
      rulesModal.style.display = "none";
    });

    actionButtons.appendChild(selectAllBtn);
    actionButtons.appendChild(clearAllBtn);
    actionButtons.appendChild(applyBtn);

    // Assemble modal
    modalBody.appendChild(searchBox);
    modalBody.appendChild(rulesContainer);
    modalBody.appendChild(actionButtons);

    modalContent.appendChild(modalHeader);
    modalContent.appendChild(modalBody);
    rulesModal.appendChild(modalContent);

    document.body.appendChild(rulesModal);

    // Close button functionality
    const closeBtn = rulesModal.querySelector("span");
    closeBtn.onclick = function () {
      rulesModal.style.display = "none";
    };

    // Close when clicking outside
    window.onclick = function (event) {
      if (event.target === rulesModal) {
        rulesModal.style.display = "none";
      }
    };
  }

  // Populate rules list
  const rulesContainer = document.getElementById("rules-container");
  rulesContainer.innerHTML = "";

  window.availableRules.forEach((ruleName) => {
    const ruleItem = document.createElement("div");
    ruleItem.className =
      "rule-item flex items-center p-2 border-b border-gray-200 dark:border-gray-700";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "rule-checkbox mr-3 h-4 w-4";
    checkbox.value = ruleName;

    const label = document.createElement("label");
    label.textContent = ruleName;
    label.className = "flex-1 cursor-pointer";

    ruleItem.appendChild(checkbox);
    ruleItem.appendChild(label);
    rulesContainer.appendChild(ruleItem);

    // Make the label also toggle the checkbox
    label.addEventListener("click", (e) => {
      e.preventDefault();
      checkbox.checked = !checkbox.checked;
    });
  });

  // Show the modal
  rulesModal.style.display = "flex";
}
// Initialize Cytoscape with minimal configuration
// let cy = null; // This is already global
let selectedNode = null; // This is already global
let dagreRegistered = false; // Flag for Dagre registration

// Function to initialize Cytoscape instance or clear existing one
function initCytoscapeInstance() {
  if (!dagreRegistered) {
    if (typeof cytoscapeDagre !== 'undefined') {
      cytoscape.use(cytoscapeDagre);
      dagreRegistered = true;
    } else {
      console.error("cytoscapeDagre is not defined. Layouts requiring Dagre may fail.");
    }
  }

  const container = document.getElementById("cy");
  if (!container) {
    console.error("Cytoscape container #cy not found in the DOM. Graph cannot be initialized.");
    cy = null; // Ensure cy is null if container is missing
    return; // Exit early, subsequent calls might also fail until container exists.
  }

  if (!cy || typeof cy.elements !== 'function') { // Check if cy is not valid or not initialized
    console.log("Cytoscape instance is not valid or not initialized. Attempting to create new instance.");
    try {
  cy = cytoscape({
        container: container, // Use the already fetched container
    style: [
      {
        selector: "node",
        style: {
          label: "data(label)",
          "text-wrap": "wrap",
          "text-max-width": 120,
          "font-size": 12,
          "text-valign": "bottom",
          "text-margin-y": 10,
          "background-color": "#f8f9fa",
          "border-width": 1,
          "border-color": "#dee2e6",
          width: 60,
          height: 60,
          shape: "ellipse",
          "text-halign": "center",
          "background-fit": "contain",
          "background-clip": "none",
          "background-image-containment": "over",
          "background-position-x": "50%",
          "background-position-y": "50%",
          "background-width": "70%",
          "background-height": "70%",
        },
      },
      {
        selector: 'node[type="event_bus"]',
        style: {
          "background-image": "/static/icons/event-bus.svg",
          "background-color": "#495057",
          "border-color": "#6c757d",
          "border-width": 2,
          "color": "#212529",
          "text-outline-width": 1,
          "text-outline-color": "#ffffff",
        },
      },
      {
        selector: 'node[type="rule"]',
        style: {
          "background-image": "/static/icons/rule.svg",
          "background-color": "#8abbed",
          "border-color": "#4a7aaa",
          "border-width": 2,
          "color": "#212529",
          "text-outline-width": 1,
          "text-outline-color": "#ffffff",
        },
      },
      {
        selector: 'node[type="target"]',
        style: {
          "background-image": "/static/icons/lambda.svg",
          "background-color": "#ffd166",
          "border-color": "#e9c46a",
          "border-width": 2,
          "color": "#212529",
          "text-outline-width": 1,
          "text-outline-color": "#ffffff",
        },
      },
          { selector: 'node[icon="sqs"]', style: { 
            "background-image": "/static/icons/sqs.svg",
            "background-color": "#cbaacb",
            "border-color": "#9f8ba8",
            "border-width": 2
          }},
          { selector: 'node[icon="sns"]', style: { 
            "background-image": "/static/icons/sns.svg",
            "background-color": "#7dcfb6",
            "border-color": "#5aaa98",
            "border-width": 2
          }},
          {
            selector: 'node[type="log_stream"]',
            style: {
              "background-color": "rgba(142, 190, 216, 0.7)",
              "border-color": "#6a98ac",
              "border-width": 2,
              shape: "round-rectangle",
              width: "label",
              height: 30,
              padding: "5px",
              "text-valign": "center",
              "text-halign": "center",
              "text-wrap": "wrap",
              "text-max-width": 150,
              "font-size": "10px",
              color: "#212529",
              "text-outline-width": 1,
              "text-outline-color": "#ffffff",
            },
          },
          {
            selector: 'node[type="log_placeholder"]',
            style: {
              "background-color": "rgba(169, 169, 169, 0.5)",
              "border-color": "#808080",
              "border-width": 1,
              shape: "round-rectangle",
              width: "label",
              height: 25,
              padding: "5px",
              "text-valign": "center",
              "text-halign": "center",
              "text-wrap": "wrap",
              "text-max-width": 120,
              "font-size": "9px",
              color: "#333",
              "text-outline-width": 0,
        },
      },
      {
        selector: "edge",
            style: { 
              width: 2, 
              "line-color": "#adb5bd", 
              "target-arrow-color": "#adb5bd", 
              "target-arrow-shape": "triangle", 
              "curve-style": "bezier" 
            },
          },
          {
            selector: 'node[type="target_log_streams_summary"]',
        style: {
              'background-image': '/static/icons/logs.svg', // Placeholder icon for a list/summary of logs
              'background-fit': 'contain',
              'background-clip': 'none',
              'shape': 'round-rectangle',
              'width': 'label',
              'height': 35, // Slightly taller to accommodate text
              'padding': '5px',
              'label': 'data(label)',
              'font-size': '10px',
              'text-valign': 'center',
              'text-halign': 'center',
              'text-wrap': 'wrap',
              'text-max-width': 80,
              'color': '#ffffff',
              'text-outline-color': '#0056b3',
              'text-outline-width': 1,
              'background-color': '#007bff', // A distinct blue color
              'border-color': '#0056b3',
              'border-width': 1,
            }
          },
          {
            selector: 'node[type="log_placeholder"]',
            style: {
              "background-color": "rgba(169, 169, 169, 0.5)", 
              "border-color": "#808080",
              "border-width": 1,
              shape: "round-tag", // Changed shape for distinction
              width: "label",
              height: 25,
              padding: "8px",
              'label': 'data(label)', // Ensure label mapping
              "text-valign": "center",
              "text-halign": "center",
              "text-wrap": "wrap",
              "text-max-width": 100, // Max width for label
              "font-size": "9px",
              color: "#333333",
              "text-outline-width": 0,
            }
      },
    ],
        layout: { name: "preset" },
    wheelSensitivity: 0.2,
  });

      if (!cy || typeof cy.elements !== 'function') {
        console.error("Cytoscape initialization (cytoscape(...)) failed to return a valid instance.");
        cy = null; // Ensure cy is null if initialization failed
        return;
      }
      console.log("Cytoscape instance created successfully.");
      _applyPersistentCytoscapeEventHandlers();
    } catch (e) {
      console.error("Error during Cytoscape object creation:", e);
      cy = null; // Ensure cy is null on error
      return;
    }
  }

  // If we reach here, cy should ideally be a valid instance.
  // Clear existing elements before adding new ones.
  if (cy && typeof cy.elements === 'function') {
    cy.elements().remove();
  } else {
    console.error("Cannot clear elements: cy is not a valid Cytoscape instance. Graph rendering will be skipped.");
    // It might be that the container #cy appeared later; the next call to render might succeed.
  }
}

// Function to apply persistent Cytoscape event handlers
function _applyPersistentCytoscapeEventHandlers() {
  if (!window.cy) {
    console.error("Cannot apply Cytoscape event handlers: cy instance not found.");
    return;
  }

  // Node tap handler - using setupNodeClickHandler as it's set up on DOMContentLoaded
  if (typeof setupNodeClickHandler === 'function') {
    setupNodeClickHandler(); // This function should attach 'tap' listener to window.cy
  } else {
    console.error("setupNodeClickHandler function not found. Node click interactions may not work.");
  }

  // Tooltip handlers (adapted from original loadGraphData)
  cy.on("mouseover", "node", function (evt) {
    const node = evt.target;
    // const baseNodeStyle = cy.style().json().find(s => s.selector === 'node').style; // Not strictly needed if scratch is used
    node.scratch('_originalBorderWidth', node.style('border-width')); // Store original
    node.scratch('_originalBorderColor', node.style('border-color'));

    node.style("border-width", 3);
    node.style("border-color", "#333333"); // Darker color for hover

    const tooltip = document.getElementById("tooltip");
    if (tooltip) {
      let content = `<strong>${node.data("label") || node.id()}</strong>`; // Corrected template literal
      const type = node.data("type");
      const arn = node.data("arn");
      const name = node.data("name") || node.data("label") || node.id();

      if (type === "target" && arn) {
        content = `<strong>ARN:</strong> ${arn}`; // Corrected template literal
      } else if (type) {
        content = `<strong>${type.replace(/_/g, " ")}:</strong> ${name}`; // Corrected template literal
      }
       if (type === "log_stream") {
        content = `<strong>Log Stream: ${name}</strong><br><span class="text-xs">Target: ${node.data("target")}</span><br><span class="text-xs italic">Click to view logs in observer</span>`; // Corrected template literal
      }
      tooltip.innerHTML = content;
      tooltip.style.display = "block";
      tooltip.style.left = evt.renderedPosition.x + 15 + "px";
      tooltip.style.top = evt.renderedPosition.y + 15 + "px";
    }
  });

  cy.on("mouseout", "node", function (evt) {
    const node = evt.target;
    // Restore original border style or use defaults
    node.style("border-width", node.scratch('_originalBorderWidth') || 1);
    node.style("border-color", node.scratch('_originalBorderColor') || '#cccccc');

    const tooltip = document.getElementById("tooltip");
    if (tooltip) {
      tooltip.style.display = "none";
    }
  });

  cy.on("mousemove", "node", function (evt) {
    const tooltip = document.getElementById("tooltip");
    if (tooltip && tooltip.style.display === "block") {
      tooltip.style.left = evt.renderedPosition.x + 15 + "px";
      tooltip.style.top = evt.renderedPosition.y + 15 + "px";
    }
  });

  // Ensure other persistent listeners like pan/zoom for logObserver badges are also handled.
  // The existing DOMContentLoaded listener for this should be fine if cy is not destroyed.
}

// Function to initialize Cytoscape (original, to be replaced or removed)
// function initCytoscape() { ... } // This will be replaced by initCytoscapeInstance

// ... existing code ...
// Replace the old initCytoscape function definition (around line 700)
// Ensure this new code is placed before initCytoscape is called.
// We'll need to find the original initCytoscape and replace it.
// For now, assume this code block will be inserted at an appropriate place (e.g., near the old initCytoscape).
// The edit tool will need to handle placing this correctly.
// The old initCytoscape function should be removed or commented out.
// For the edit, I will provide line numbers to replace the old function.

// This is a placeholder for the edit tool to replace the old initCytoscape.
// The actual replacement will be handled by providing the correct content for the `edit_file` call.
// The content above defines the new functions.
// The call to `edit_file` should target the lines of the old `initCytoscape` and replace them.
// And ensure `dagreRegistered` and `selectedNode` are defined globally if not already.
// `cy` is already global.

// Function to apply dagre layout
function applyDagreLayout() {
  if (!cy) return;

  const layout = cy.layout({
    name: "dagre",
    rankDir: "TB", // Top to bottom
    rankSep: 160, // Distance between ranks (increased for larger nodes)
    nodeSep: 120, // Distance between nodes (increased for larger nodes)
    edgeSep: 50, // Distance between edges
    fit: true, // Fit to viewport
    padding: 50, // Padding around the graph
    animate: true, // Animate the layout
    animationDuration: 500, // Animation duration
  });

  layout.run();
}

// Function to load graph data
async function loadGraphData() {
  try {
    document.getElementById("loading").style.display = "block";
    document.getElementById("error").style.display = "none";

    const response = await fetch("/api/graph"); // This is the old endpoint
    if (!response.ok) {
      throw new Error("Failed to load graph data from /api/graph");
    }

    const graphData = await response.json(); // graphData here is { elements: [...], etc. }
    console.log("Received graph data from /api/graph:", graphData);

    // Use the new internal rendering function
    // The graphData should be in the format expected by _internalRenderActualGraph
    // which is typically { elements: [...], eventBusName: "...", ... }
    // If /api/graph returns a different structure, it might need adaptation here.
    // For now, assume graphData is directly usable or _internalRenderActualGraph is robust enough.
    _internalRenderActualGraph(graphData);

    // Update UI elements like event bus name if this data contains it (optional, as fetchGraph does this)
    // if (graphData.eventBusName) {
    //   document.getElementById("event-bus-name").textContent = graphData.eventBusName;
    // }
    // if (graphData.rulesInfo) { // Or however rules info is structured
    //   document.getElementById("rules-info").textContent = graphData.rulesInfo;
    // }

    document.getElementById("loading").style.display = "none";
  } catch (error) {
    console.error("Error in loadGraphData:", error);
    document.getElementById("loading").style.display = "none";
    document.getElementById("error-message").textContent = error.toString();
    document.getElementById("error").style.display = "block";
    // Ensure graph is cleared or shows an error state
    if (window.cy) window.cy.elements().remove();
  }
}

// Function to show node details in the side drawer
function showNodeDetails(node) {
  let nodeDataToUse = node; 
  if (typeof node.data === 'function') {
      nodeDataToUse = node.data();
  }

  const drawer = document.getElementById("details-drawer");
  const drawerTitle = document.getElementById("drawer-title");
  const detailsContent = document.getElementById("details-tab-content");
  const logsContentContainer = document.getElementById("logs-content-container"); 
  const fetchStreamsBtn = document.getElementById("fetch-streams-btn");
  const fetchLogsBtn = document.getElementById("fetch-logs-btn");

  if (!drawer || !drawerTitle || !detailsContent || !logsContentContainer || !fetchStreamsBtn || !fetchLogsBtn) {
    console.error("Drawer elements not found. Cannot show node details.");
    return;
  }

  const nodeId = nodeDataToUse.id || nodeDataToUse.name;
  const nodeType = nodeDataToUse.type;
  let defaultTab = "details";

  fetchStreamsBtn.style.display = "none";
  fetchLogsBtn.classList.add("hidden");

  if (nodeType === "event_bus") {
    drawerTitle.textContent = `Event Bus: ${nodeDataToUse.label || nodeId}`;
    detailsContent.innerHTML = `
        <div class="details-section"><div class="details-title">Event Bus Information</div>
                <div class="details-value">
                <span class="details-label">Name:</span> ${nodeDataToUse.label || nodeId}<br>
                    <span class="details-label">Type:</span> EventBridge Event Bus
            </div></div>`;
    logsContentContainer.innerHTML = "<div class='p-4 text-gray-500 dark:text-gray-400'>Log information is typically viewed per target.</div>";
  } else if (nodeType === "rule") {
    drawerTitle.textContent = `Rule: ${nodeDataToUse.label || nodeId}`;
    detailsHtml = `
            <div class="details-section">
                <div class="details-title">Rule Information</div>
                <div class="details-value">
          <span class="details-label">Name:</span> ${nodeDataToUse.label || nodeId}<br>
          ${nodeDataToUse.description ? `<span class="details-label">Description:</span> ${nodeDataToUse.description}<br>` : ""}
                </div>
            </div>
        `;

    let eventPatternHtml = '';
    let patternForTemplate = {};
    
    if (nodeDataToUse.eventPattern) {
        try {
            const formattedPattern = typeof nodeDataToUse.eventPattern === 'string' ? 
                                    formatJsonString(nodeDataToUse.eventPattern) :
                                    formatJson(nodeDataToUse.eventPattern);
            ruleDetailsHtml += `
                <div class="details-section mt-4"><div class="details-title">Event Pattern</div>
                    <div class="json-content">${formattedPattern}</div></div>`;
        } catch (e) {
            ruleDetailsHtml += `
                <div class="details-section mt-4"><div class="details-title">Event Pattern (raw)</div>
                    <pre class="text-xs bg-gray-700 dark:bg-gray-900 p-2 rounded">${escapeHtml(JSON.stringify(nodeDataToUse.eventPattern, null, 2))}</pre></div>`;
        }
    }
    
    // Add section to send test events to the event bus
    ruleDetailsHtml += `
      <div class="details-section mt-4">
        <div class="details-title">Send Test Event</div>
        <div class="mt-2">
          <textarea id="test-event-json" 
            class="w-full h-32 p-2 text-xs font-mono border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200"
            placeholder='{\n  "source": "test.event",\n  "detail-type": "Test Event",\n  "detail": {\n    "key": "value"\n  }\n}'></textarea>
          <div class="flex justify-between items-center mt-2">
            <div id="event-send-status" class="text-xs"></div>
            <button id="send-test-event-btn" 
              class="px-3 py-1 bg-aws-orange text-white rounded hover:bg-amber-600"
              data-rule-name="${nodeDataToUse.label || nodeId}">
              Send Event
            </button>
                    </div>
        </div>
                    </div>
                `;
    detailsContent.innerHTML = ruleDetailsHtml;
    logsContentContainer.innerHTML = "<div class='p-4 text-gray-500 dark:text-gray-400'>Log information is viewed per target. Select a target connected to this rule.</div>";
  } else if (nodeType === "target") {
    drawerTitle.textContent = `Target: ${nodeDataToUse.label || nodeDataToUse.name}`;
    const targetArn = nodeDataToUse.arn || "Unknown";
    const targetName = nodeDataToUse.label || nodeDataToUse.name || nodeId;
    const ruleName = nodeDataToUse.rule_name || 'N/A';
    
    detailsContent.innerHTML = `
        <div class="details-section"><div class="details-title">Target Information</div>
                <div class="details-value">
                <span class="details-label">Display Name:</span> ${targetName}<br>
                <span class="details-label">ID in Rule:</span> ${nodeDataToUse.name}<br>
                <span class="details-label">ARN:</span> <span class="break-all">${targetArn}</span><br>
                <span class="details-label">Parent Rule:</span> ${ruleName}<br>
            </div></div>

        <div class="details-section">
            <div class="details-title">Log Streams</div>
            <div id="log-streams-container" class="mt-3 p-2 bg-gray-50 dark:bg-gray-900 rounded">
                <div class="text-center p-4">
                    <div class="animate-spin inline-block w-6 h-6 border-2 border-aws-orange border-t-transparent rounded-full mb-2"></div>
                    <div>Loading log streams...</div>
                </div>
            </div>
        </div>`;

    // Fetch log streams for this target
    fetchLogStreams(targetArn).then(streams => {
        displayLogStreamsInDetails(streams);
    }).catch(error => {
        document.getElementById("log-streams-container").innerHTML = `
            <div class="text-red-500 p-2">Error loading log streams: ${error.message}</div>
        `;
    });
    
    logsContentContainer.innerHTML = "<div class='p-4 text-gray-500 dark:text-gray-400'>Select a log stream from the Details tab to view logs.</div>";
    defaultTab = "details";
  } else {
    drawerTitle.textContent = `Details: ${nodeDataToUse.label || nodeId}`;
    detailsContent.innerHTML = `<div class="p-4 text-gray-500 dark:text-gray-400">Details for node type '${nodeType}' not specifically handled. ID: ${escapeHtml(nodeId)}</div>`;
    logsContentContainer.innerHTML = "";
  }

  drawer.style.transition = "width 0.3s ease";
  drawer.style.width = "600px"; 

  if (typeof makeDrawerResizable === 'function') makeDrawerResizable();

  const defaultTabButton = document.querySelector(`.drawer-tab[data-tab="${defaultTab}"]`);
  if (defaultTabButton && typeof defaultTabButton.click === 'function') {
      defaultTabButton.click();
  } else {
      const fallbackDetailsTab = document.querySelector('.drawer-tab[data-tab="details"]');
      if(fallbackDetailsTab && typeof fallbackDetailsTab.click === 'function') fallbackDetailsTab.click();
  }
  
  // Set up event listeners for rule-specific functionality
  if (nodeType === "rule") {
    // Set up event listener for the "Use as Template" button
    const usePatternBtn = document.getElementById("use-pattern-as-template");
    const eventJsonTextarea = document.getElementById("test-event-json");
    const sendButton = document.getElementById("send-test-event-btn");
    const formatJsonBtn = document.getElementById("format-json-btn");
    const statusElement = document.getElementById("event-send-status");
    
    if (usePatternBtn && eventJsonTextarea) {
      usePatternBtn.addEventListener("click", function() {
        try {
          // Create a template event based on the rule pattern
          let templateEvent = {
            source: "test.event",
            "detail-type": "Test Event",
            detail: {}
          };
          
          // Get the pattern structure from the rule
          const pattern = typeof nodeData.eventPattern === 'string' 
            ? JSON.parse(nodeData.eventPattern) 
            : nodeData.eventPattern;
            
          // If the pattern has a source, use it
          if (pattern.source) {
            if (Array.isArray(pattern.source)) {
              templateEvent.source = pattern.source[0];
            } else {
              templateEvent.source = pattern.source;
    }
  }

          // If the pattern has a detail-type, use it
          if (pattern['detail-type']) {
            if (Array.isArray(pattern['detail-type'])) {
              templateEvent['detail-type'] = pattern['detail-type'][0];
            } else {
              templateEvent['detail-type'] = pattern['detail-type'];
            }
          }
          
          // If the pattern has detail fields, use them as a template
          if (pattern.detail) {
            templateEvent.detail = {};

            // For each detail field in the pattern, add a placeholder in the template
            for (const [key, value] of Object.entries(pattern.detail)) {
              if (Array.isArray(value)) {
                templateEvent.detail[key] = value[0];
              } else if (typeof value === 'object') {
                // For nested objects, create a template object
                templateEvent.detail[key] = {};
                for (const [nestedKey, nestedValue] of Object.entries(value)) {
                  if (Array.isArray(nestedValue)) {
                    templateEvent.detail[key][nestedKey] = nestedValue[0];
                  } else {
                    templateEvent.detail[key][nestedKey] = nestedValue;
                  }
                }
              } else {
                templateEvent.detail[key] = value;
              }
            }
          }
          
          // Set the textarea value to the formatted template
          eventJsonTextarea.value = JSON.stringify(templateEvent, null, 2);

          // Show success message
          statusElement.textContent = "Template applied";
          statusElement.className = "text-xs text-green-500";
          
          // Clear message after 3 seconds
          setTimeout(() => {
            statusElement.textContent = "";
          }, 3000);
        } catch (error) {
          console.error("Error creating template:", error);
          statusElement.textContent = `Error creating template: ${error.message}`;
          statusElement.className = "text-xs text-red-500";
        }
      });
  }

    // Add event listener for the Format JSON button
    if (formatJsonBtn && eventJsonTextarea && statusElement) {
      formatJsonBtn.addEventListener("click", function() {
        try {
          // Parse the current JSON in the textarea
          const jsonData = JSON.parse(eventJsonTextarea.value);

          // Format the JSON with indentation and write it back to the textarea
          eventJsonTextarea.value = JSON.stringify(jsonData, null, 2);
          
          // Show success message
          statusElement.textContent = "JSON formatted";
          statusElement.className = "text-xs text-green-500";

          // Clear message after 3 seconds
          setTimeout(() => {
            statusElement.textContent = "";
          }, 3000);
        } catch (error) {
          console.error("Error formatting JSON:", error);
          statusElement.textContent = `Error: ${error.message}`;
          statusElement.className = "text-xs text-red-500";
        }
      });
    }
    
    if (sendButton && eventJsonTextarea && statusElement) {
      sendButton.onclick = function() {
        // Get the rule name and event data
        const ruleName = this.getAttribute("data-rule-name");
        let eventData;
        
        try {
          eventData = JSON.parse(eventJsonTextarea.value);
          statusElement.textContent = "Sending event...";
          statusElement.className = "text-xs text-blue-500";
          
          // Send the event
          sendEventToEventBus(eventData, ruleName, statusElement);
        } catch (error) {
          statusElement.textContent = `Error: ${error.message}`;
          statusElement.className = "text-xs text-red-500";
        }
      };
    }
  }
}

// Display log streams in the details panel
function displayLogStreamsInDetails(streams) {
    const logStreamsContainer = document.getElementById("log-streams-container");
    if (!logStreamsContainer) return;
    
    if (!streams || streams.length === 0) {
        logStreamsContainer.innerHTML = `
            <div class="text-gray-500 dark:text-gray-400 p-2 text-center">
                No log streams found for this target
            </div>
        `;
        return;
    }
    
    let html = `
        <div class="text-xs text-gray-500 dark:text-gray-400 mb-2">
            ${streams.length} log stream(s) available
        </div>
        <div class="max-h-[400px] overflow-y-auto">
    `;

    // Sort streams by last event time (most recent first)
    streams.sort((a, b) => {
        const aTime = a.lastEventTimestamp || 0;
        const bTime = b.lastEventTimestamp || 0;
        return bTime - aTime;
      });

    streams.forEach(stream => {
        const streamName = stream.logStreamName || "Unnamed Stream";
        const lastEventTime = stream.lastEventTime || "No events";
        const logGroupName = stream.logGroupName || "";
        
        html += `
            <div class="stream-item cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 p-2 rounded mb-1 border-l-2 border-aws-lightblue"
                 onclick="showStreamLogsInModal('${logGroupName}', '${streamName}')">
                <div class="font-medium text-aws-lightblue">${streamName}</div>
                <div class="text-xs text-gray-500 dark:text-gray-400">
                    Last event: ${lastEventTime}
                </div>
            </div>
        `;
    });
    
    html += `</div>`;
    logStreamsContainer.innerHTML = html;
}

// Function to fetch log streams for a target, returns a Promise
async function fetchLogStreams(targetArn) {
    if (!targetArn) {
        throw new Error("No target ARN available");
    }
    
    // Start time from far in the past (30 years ago) to get all logs
    const startTime = new Date();
    startTime.setFullYear(startTime.getFullYear() - 30);

    // End time is now
    const endTime = new Date();
    
    // Convert to Unix timestamp in seconds
    const startTimeSeconds = Math.floor(startTime.getTime() / 1000);
    const endTimeSeconds = Math.floor(endTime.getTime() / 1000);
    
    const response = await fetch("/api/target_log_streams", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            targetArn: targetArn,
            startTime: startTimeSeconds,
            endTime: endTimeSeconds,
        }),
    });
    
    if (!response.ok) {
        throw new Error("Failed to fetch log streams");
    }
    
    const data = await response.json();
    return data.streams || [];
}

// Function to make the drawer resizable
function makeDrawerResizable() {
  const drawer = document.getElementById("details-drawer");
  if (!drawer) return;

  // Create and add resize handle if it doesn't exist
  let resizeHandle = document.getElementById("drawer-resize-handle");
  if (!resizeHandle) {
    resizeHandle = document.createElement("div");
    resizeHandle.id = "drawer-resize-handle";
    resizeHandle.className =
      "absolute left-0 top-0 h-full w-4 cursor-ew-resize";
    resizeHandle.style.cssText =
      "cursor: ew-resize; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background-color: transparent;";
    drawer.appendChild(resizeHandle);
  }

  let startX, startWidth;

  const startResize = function (e) {
    startX = e.clientX;
    startWidth = parseInt(
      document.defaultView.getComputedStyle(drawer).width,
      10,
    );
    document.addEventListener("mousemove", resize);
    document.addEventListener("mouseup", stopResize);
    document.body.style.cursor = "ew-resize";
    document.body.style.userSelect = "none";
  };

  const resize = function (e) {
    const width = startWidth - (e.clientX - startX);
    drawer.style.width = width + "px";
  };

  const stopResize = function () {
    document.removeEventListener("mousemove", resize);
    document.removeEventListener("mouseup", stopResize);
    document.body.style.cursor = "";
    document.body.style.userSelect = "";
  };

  resizeHandle.addEventListener("mousedown", startResize);
}

// Set up button handlers and initialize
document.addEventListener("DOMContentLoaded", function () {
  // Initialize Cytoscape
  initCytoscapeInstance();

  // Ensure the drawer is hidden initially
  const drawer = document.getElementById("details-drawer");
  if (drawer) {
    drawer.style.width = "0";
  }

  // Set up button handlers
  document.getElementById("fit-btn").addEventListener("click", () => {
    if (cy) cy.fit();
  });

  // Comment out the event listener for the non-existent layout button
  // document.getElementById("layout-btn").addEventListener("click", () => {
  //   applyDagreLayout();
  // });

  document.getElementById("refresh-buses-btn").addEventListener("click", () => {
    fetchEventBuses();
  });

  //document.getElementById("show-rules-btn").addEventListener("click", () => {
  //  showRulesModal();
  //});

  document.getElementById("dismiss-error").addEventListener("click", () => {
    document.getElementById("error").style.display = "none";
  });

  // Set up event bus select change handler
  document
    .getElementById("event-bus-select")
    .addEventListener("change", function () {
      const selectedBus = this.value;
      if (selectedBus) {
        handleEventBusSelection(selectedBus);
      }
    });

  // Set up tab switching in the drawer
  document.querySelectorAll(".drawer-tab").forEach((tab) => {
    tab.addEventListener("click", function () {
      // Remove active class from all tabs
      tabs.forEach((t) =>
        t.classList.remove(
          "active",
          "bg-gray-100",
          "dark:bg-gray-700",
          "border-gray-300",
          "dark:border-gray-600",
        ),
        );

      // Add active class to clicked tab
      this.classList.add(
        "active",
        "bg-gray-100",
        "dark:bg-gray-700",
        "border-gray-300",
        "dark:border-gray-600",
      );

      // Hide all tab contents
      document.querySelectorAll(".tab-content").forEach((content) => {
        content.classList.add("hidden");
        content.classList.remove("active");
      });

      // Show the corresponding tab content
      const tabName = this.getAttribute("data-tab");
      const tabContent = document.getElementById(`${tabName}-tab-content`);
      tabContent.classList.remove("hidden");
      tabContent.classList.add("active");
    });
  });

  //// Set up close drawer button
  //document
  //  .querySelector(".close-drawer")
  //  .addEventListener("click", function () {
  //    document.getElementById("details-drawer").style.width = "0";
  //  });

  // Load event buses on page load
  fetchEventBuses();
});
// Function to format JSON with syntax highlighting
function formatJsonString(jsonString) {
  if (!jsonString) return "";

  try {
    // Parse the JSON string
    const obj = JSON.parse(jsonString);

    // Format with indentation and syntax highlighting
    return formatJson(obj);
  } catch (e) {
    // If it's not valid JSON, return as is
    return jsonString;
  }
}

// Helper function to format JSON object with syntax highlighting
function formatJson(obj, indent = 0) {
  const indentStr = "  ".repeat(indent);

  if (obj === null) {
    return `<span class="json-null">null</span>`;
  }

  if (typeof obj === "boolean") {
    return `<span class="json-boolean">${obj}</span>`;
  }

  if (typeof obj === "number") {
    return `<span class="json-number">${obj}</span>`;
  }

  if (typeof obj === "string") {
    return `<span class="json-string">"${escapeHtml(obj)}"</span>`;
  }

  if (Array.isArray(obj)) {
    if (obj.length === 0) {
      return "[]";
    }

    let result = "[\n";

    obj.forEach((item, index) => {
      result += `${indentStr}  ${formatJson(item, indent + 1)}`;
      if (index < obj.length - 1) {
        result += ",";
      }
      result += "\n";
    });

    result += `${indentStr}]`;
    return result;
  }

  if (typeof obj === "object") {
    const keys = Object.keys(obj);

    if (keys.length === 0) {
      return "{}";
    }

    let result = "{\n";

    keys.forEach((key, index) => {
      result += `${indentStr}  <span class="json-key">"${escapeHtml(key)}"</span>: ${formatJson(obj[key], indent + 1)}`;
      if (index < keys.length - 1) {
        result += ",";
      }
      result += "\n";
    });

    result += `${indentStr}}`;
    return result;
  }

  return String(obj);
}

// Helper function to escape HTML special characters
function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
// Initialize the LogViewer when the document is ready
document.addEventListener("DOMContentLoaded", function () {
  // Create global log viewer instance
  window.globalLogViewer = new LogViewer({
    containerSelector: "#log-viewer-container",
  });

  // Add log viewer modal
  createLogViewerModal();
});

// Function to remove the setupGlobalSearch function since it's no longer needed
// Function to remove the rest of the setupGlobalSearch function

// Function to remove the performGlobalSearch function

// Function to remove the getSelectedRules function
function getSelectedRules() {
  // If specific rules are selected, use those
  if (window.selectedRules && window.selectedRules.length > 0) {
    return window.selectedRules;
  }

  // Otherwise, get all rules from the graph
  const rules = [];
  if (window.cy) {
    const ruleNodes = window.cy
      .nodes()
      .filter((node) => node.data("type") === "rule");
    ruleNodes.forEach((node) => {
      rules.push(node.data("id"));
    });
  }

  return rules;
}

// Create log viewer modal
function createLogViewerModal() {
  // Create modal container
  const modal = document.createElement("div");
  modal.id = "log-viewer-modal";
  modal.className = "log-modal";

  // Create modal content
  modal.innerHTML = `
        <div class="log-modal-content">
            <div class="log-modal-header">
                <h2 class="text-xl font-bold">Log Viewer</h2>
                <button id="log-modal-close" class="log-modal-close">&times;</button>
            </div>
            <div class="log-modal-body">
                <div id="log-viewer-container"></div>
            </div>
            <div class="log-modal-footer">
                <button id="log-modal-close-btn" class="bg-gray-300 hover:bg-gray-400 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-white py-2 px-4 rounded">
                    Close
                </button>
            </div>
        </div>
    `;

  // Add to document
  document.body.appendChild(modal);

  // Add event listeners
  const closeButton = document.getElementById("log-modal-close");
  const closeButtonFooter = document.getElementById("log-modal-close-btn");

  if (closeButton) {
    closeButton.addEventListener("click", hideLogViewerModal);
  }

  if (closeButtonFooter) {
    closeButtonFooter.addEventListener("click", hideLogViewerModal);
  }

  // Close when clicking outside the modal content
  modal.addEventListener("click", (e) => {
    if (e.target === modal) {
      hideLogViewerModal();
    }
  });
}

// Function to show log viewer modal
function showLogViewerModal() {
  const modal = document.getElementById("log-viewer-modal");
  if (modal) {
    modal.classList.add("active");
    modal.classList.remove("hidden");
    modal.style.display = "flex";
  }
}

// Hide log viewer modal
function hideLogViewerModal() {
  const modal = document.getElementById("log-viewer-modal");
  if (modal) {
    modal.classList.remove("active");
    modal.classList.add("hidden");
    modal.style.display = "none";
  }
}

// Enhance the node click handler to show logs for log stream nodes
window.handleNodeClick = function (event) {
  const node = event.target;
  const nodeData = node.data();

  // If this is a log stream node, show logs in modal
  if (nodeData.type === "log_stream") {
    const logGroupName = nodeData.log_group || "";
    const logStreamName = nodeData.name || "";
    
    if (logGroupName && logStreamName) {
      showStreamLogsInModal(logGroupName, logStreamName);
      return;
    } else if (window.logObserver) {
      // Fallback to logObserver if available
      window.logObserver.showLogsForNode(node);
    return;
    }
  }

  // If this is a target node, show logs
  if (nodeData.type === "target") {
    // Show the log viewer modal
    if (window.globalLogViewer) {
      window.globalLogViewer.setTarget(
        nodeData.arn,
        nodeData.id,
        nodeData.rule,
      );
      showLogViewerModal();
    }
    return;
  }

  // Default behavior for other node types
  showNodeDetails(nodeData);
};

// Add log badges to target nodes
function addLogBadgesToTargets() {
  // This function has been intentionally disabled to remove the orange badges
  console.log('Target node badges are disabled');
    return;
}

// Update log badge positions
function updateLogBadgePositions() {
  // This function has been intentionally disabled
  return;
}

// Add log badges after graph is rendered
const originalRenderGraph = window.renderGraph; // Captures whatever window.renderGraph was before this point
window.renderGraph = function (graphPayload) { // graphPayload is the { elements: ..., eventBusName: ... } object
  if (originalRenderGraph && typeof originalRenderGraph === 'function') {
    originalRenderGraph(graphPayload); // If it existed and was a function, call it.
    } else {
    // originalRenderGraph is not defined or not a function, so we render the graph.
    if (!originalRenderGraph) {
      console.warn("originalRenderGraph was not defined. Calling _internalRenderActualGraph.");
        } else {
      console.warn("originalRenderGraph was not a function. Calling _internalRenderActualGraph. Type was: " + typeof originalRenderGraph);
        }
    _internalRenderActualGraph(graphPayload); // Our new function to render the graph
    }
  
  // The badges functionality has been removed
  // No timeout or addLogBadgesToTargets calls
};

// Initialize the LogObserver when the document is ready
document.addEventListener("DOMContentLoaded", function () {
  // Create log viewer container if it doesn't exist
  if (!document.getElementById("log-viewer-container")) {
    const container = document.createElement("div");
    container.id = "log-viewer-container";
    container.style.display = "none"; // Hide it initially
    document.body.appendChild(container);
  }

  // Initialize components with a delay to ensure DOM is ready
  setTimeout(() => {
    // Create global log viewer instance
    window.globalLogViewer = new LogViewer({
      containerSelector: "#log-viewer-container",
    });
  }, 200);
});

// Add node styles for log nodes
const logNodeStyles = [
  {
    selector: 'node[type="log_stream"]',
    style: {
      "background-color": "rgba(100, 149, 237, 0.7)", // Cornflower blue
      "border-color": "#4682B4",
      "border-width": 2,
      shape: "round-rectangle",
      width: "label",
      height: 30,
      padding: "5px",
      "text-valign": "center",
      "text-halign": "center",
      "text-wrap": "wrap",
      "text-max-width": 150,
      "font-size": "10px",
      color: "#fff",
      "text-outline-width": 1,
      "text-outline-color": "#4682B4",
    },
  },
  {
    selector: 'node[type="log_placeholder"]',
    style: {
      "background-color": "rgba(169, 169, 169, 0.5)", // Light gray
      "border-color": "#808080",
      "border-width": 1,
      shape: "round-rectangle",
      width: "label",
      height: 25,
      padding: "5px",
      "text-valign": "center",
      "text-halign": "center",
      "text-wrap": "wrap",
      "text-max-width": 120,
      "font-size": "9px",
      color: "#333",
      "text-outline-width": 0,
    },
  },
];

// Extend the existing node styles with log node styles
if (typeof window.nodeStyles === "undefined") {
  window.nodeStyles = [];
}
window.nodeStyles = window.nodeStyles.concat(logNodeStyles);

// Override the fetchGraph function to use the enhanced graph with logs
window.fetchGraph = function (eventBusName, selectedRules = []) {
  // Show loading indicator
  document.getElementById("loading").classList.remove("hidden");

  // Use the enhanced API endpoint that includes log nodes
  fetch("/api/graph/with-logs", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      event_bus: eventBusName,
      rules: selectedRules,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        renderGraph(data.data);

        // Update selections info
        document.getElementById("event-bus-name").textContent =
          data.data.eventBusName;
        const rulesInfo =
          selectedRules.length > 0
            ? `${selectedRules.length} rules selected`
            : "All rules";
        document.getElementById("rules-info").textContent = rulesInfo;

        // Hide loading indicator
        document.getElementById("loading").classList.add("hidden");
      } else {
        // Show error
        document.getElementById("loading").classList.add("hidden");
        document.getElementById("error-message").textContent = data.message;
        document.getElementById("error").classList.remove("hidden");
      }
    })
    .catch((error) => {
      console.error("Error fetching graph:", error);
      document.getElementById("loading").classList.add("hidden");
      document.getElementById("error-message").textContent = error.message;
      document.getElementById("error").classList.remove("hidden");
    });
};

// Enhance the node click handler to show logs for log stream nodes
const originalNodeClickHandler = window.handleNodeClick;
window.handleNodeClick = function (event) {
  const node = event.target;
  const nodeData = node.data();

  // If this is a log stream node, show logs in modal
  if (nodeData.type === "log_stream") {
    const logGroupName = nodeData.log_group || "";
    const logStreamName = nodeData.name || "";
    
    if (logGroupName && logStreamName) {
      showStreamLogsInModal(logGroupName, logStreamName);
      return;
    } else if (window.logObserver) {
      // Fallback to logObserver if available
      window.logObserver.showLogsForNode(node);
    return;
    }
  }

  // Otherwise call the original handler
  if (originalNodeClickHandler) {
    originalNodeClickHandler(event);
  }
};

// Update match badge positions when the graph is panned or zoomed
document.addEventListener("DOMContentLoaded", function () {
  // Wait for Cytoscape to be initialized
  const checkCyInterval = setInterval(() => {
    if (window.cy && typeof window.cy.on === "function") {
      window.cy.on("pan zoom resize", function () {
        if (
          window.logObserver &&
          typeof window.logObserver.updateMatchBadgePositions === "function"
        ) {
          window.logObserver.updateMatchBadgePositions();
        }
      });
      clearInterval(checkCyInterval);
    }
  }, 100);
});
// Function to show node details (used by handleNodeClick)
function showNodeDetails(nodeData) {
  // Get the tooltip element
  const tooltip = document.getElementById("tooltip");
  if (!tooltip) return;

  // Format the details based on node type
  let details = "";

  switch (nodeData.type) {
    case "event_bus":
      details = `<div class="font-bold">Event Bus: ${nodeData.name}</div>`;
      break;
    case "rule":
      details = `<div class="font-bold">Rule: ${nodeData.name}</div>`;
      break;
    case "target":
      details = `
                <div class="font-bold">Target: ${nodeData.name}</div>
                <div class="text-xs mt-1">ARN: ${nodeData.arn}</div>
                <div class="text-xs">Rule: ${nodeData.rule}</div>
            `;
      break;
    case "log_stream":
      details = `
                <div class="font-bold">Log Stream: ${nodeData.name}</div>
                <div class="text-xs mt-1">Target: ${nodeData.target}</div>
                <div class="text-xs">Click to view logs</div>
            `;
      break;
    case "log_placeholder":
      details = `
                <div class="font-bold">No Logs Available</div>
                <div class="text-xs mt-1">${nodeData.error || "No log streams found"}</div>
            `;
      break;
    default:
      details = `<div class="font-bold">${nodeData.name || "Unknown"}</div>`;
  }

  // Update tooltip content
  tooltip.innerHTML = details;

  // Show the tooltip
  tooltip.classList.remove("hidden");

  // Position the tooltip near the node
  if (window.cy && nodeData.id) {
    const node = window.cy.getElementById(nodeData.id);
    if (node && node.renderedPosition) {
      const pos = node.renderedPosition();
      if (pos && typeof pos.x === "number" && typeof pos.y === "number") {
        tooltip.style.left = `${pos.x + 10}px`;
        tooltip.style.top = `${pos.y + 10}px`;
      }
    }
  }

  // Hide tooltip after a delay
  setTimeout(() => {
    tooltip.classList.add("hidden");
  }, 3000);
}
// Function to set up the node click handler
function setupNodeClickHandler() {
  if (!window.cy || typeof window.cy.on !== "function") {
    console.error("Cytoscape instance not available or missing on method");
    return;
  }

  window.cy.on("tap", "node", function (evt) {
    try {
      const node = evt.target;
      const nodeData = node.data();

      // Update details sidebar with node information
      updateDetailsSidebar(nodeData);
    } catch (error) {
      console.error("Error in node click handler:", error);
    }
  });
}
// Store selected rules globally for access by other components
window.selectedRules = [];

// Override the original rule selection handler to store selected rules globally
document.addEventListener("DOMContentLoaded", function () {
  const originalSelectRules = window.selectRules;
  if (typeof originalSelectRules === "function") {
    window.selectRules = function (ruleNames) {
      // Store selected rules globally
      window.selectedRules = ruleNames;

      // Call original function if it exists
      if (originalSelectRules) {
        originalSelectRules(ruleNames);
      }
    };
  }

  // Also capture rules when fetching the graph
  const originalFetchGraph = window.fetchGraph;
  if (typeof originalFetchGraph === "function") {
    window.fetchGraph = function (eventBusName, selectedRules = []) {
      // Store selected rules globally
      window.selectedRules = selectedRules;

      // Use the enhanced API endpoint that includes log nodes
      fetch("/api/graph/with-logs", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          event_bus: eventBusName,
          rules: selectedRules,
        }),
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.success) {
            renderGraph(data.data);

            // Update selections info
            document.getElementById("event-bus-name").textContent =
              data.data.eventBusName;
            const rulesInfo =
              selectedRules.length > 0
                ? `${selectedRules.length} rules selected`
                : "All rules";
            document.getElementById("rules-info").textContent = rulesInfo;

            // Store all rules if none are specifically selected
            if (
              selectedRules.length === 0 &&
              data.data.elements &&
              data.data.elements.nodes
            ) {
              const allRules = data.data.elements.nodes
                .filter((node) => node.data && node.data.type === "rule")
                .map((node) => node.data.id);
              window.selectedRules = allRules;
              console.log("Stored all rules:", window.selectedRules);
            }

            // Hide loading indicator
            document.getElementById("loading").classList.add("hidden");
          } else {
            // Show error
            document.getElementById("loading").classList.add("hidden");
            document.getElementById("error-message").textContent = data.message;
            document.getElementById("error").classList.remove("hidden");
          }
        })
        .catch((error) => {
          console.error("Error fetching graph:", error);
          document.getElementById("loading").classList.add("hidden");
          document.getElementById("error-message").textContent = error.message;
          document.getElementById("error").classList.remove("hidden");
        });
    };
  }
});
// Set up the node click handler with a delay to ensure Cytoscape is initialized
setTimeout(() => {
  if (window.cy && typeof window.cy.on === "function") {
    setupNodeClickHandler();
  } else {
    // Wait for cy to be initialized
    const checkCy = setInterval(() => {
      if (window.cy && typeof window.cy.on === "function") {
        setupNodeClickHandler();
        clearInterval(checkCy);
      }
    }, 100);
  }
}, 500);
// Override the original event bus selection handler to use our new flow
document.addEventListener("DOMContentLoaded", function () {
  // Find the original event handler for the event bus select
  const eventBusSelect = document.getElementById("event-bus-select");
  if (eventBusSelect) {
    // Remove any existing event listeners by cloning the element
    const newEventBusSelect = eventBusSelect.cloneNode(true);
    eventBusSelect.parentNode.replaceChild(newEventBusSelect, eventBusSelect);

    // Add our new event listener
    newEventBusSelect.addEventListener("change", function () {
      const selectedBus = this.value;
      if (selectedBus) {
        // Fetch rules for this event bus and show the selection modal
        fetchRulesAndShowModal(selectedBus);
      }
    });
  }
});

// Function to fetch rules and show the selection modal
function fetchRulesAndShowModal(eventBusName) {
  // Show loading indicator
  document.getElementById("loading").classList.remove("hidden");

  // Fetch rules for the selected event bus
  fetch(`/api/rules?event_bus=${encodeURIComponent(eventBusName)}`)
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        // Hide loading indicator
        document.getElementById("loading").classList.add("hidden");

        window.availableRules = data.data; // Store fetched rules globally

        // Show rules selection modal
        showRulesSelectionModal(eventBusName, data.data);
      } else {
        // Show error
        document.getElementById("loading").classList.add("hidden");
        document.getElementById("error-message").textContent = data.message;
        document.getElementById("error").classList.remove("hidden");
        window.availableRules = []; // Clear or set to empty on error
      }
    })
    .catch((error) => {
      console.error("Error fetching rules:", error);
      document.getElementById("loading").classList.add("hidden");
      document.getElementById("error-message").textContent = error.message;
      document.getElementById("error").classList.remove("hidden");
      window.availableRules = []; // Clear or set to empty on error
    });
}

// Function to show the rules selection modal
function showRulesSelectionModal(eventBusName, rules) {
  // Create modal if it doesn't exist
  let modal = document.getElementById("rules-selection-modal");
  if (!modal) {
    modal = document.createElement("div");
    modal.id = "rules-selection-modal";
    modal.className =
      "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50";
    document.body.appendChild(modal);
  }

  // Sort rules alphabetically for better usability
  rules.sort((a, b) => a.Name.localeCompare(b.Name));

  // Create rules list with checkboxes
  const rulesList = rules
    .map(
      (rule) => `
        <div class="flex items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700">
            <input type="checkbox" id="rule-${rule.Name}" value="${rule.Name}" class="rule-checkbox mr-2" checked>
            <label for="rule-${rule.Name}" class="flex-grow cursor-pointer">${rule.Name}</label>
        </div>
    `,
    )
    .join("");

  // Populate modal content
  modal.innerHTML = `
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] flex flex-col">
            <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
                <h2 class="text-lg font-semibold">Select Rules for ${eventBusName}</h2>
                <button id="close-rules-modal" class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="p-4 overflow-y-auto flex-grow">
                <div class="mb-4">
                    <div class="flex justify-between items-center mb-2">
                        <span class="text-sm text-gray-600 dark:text-gray-300">${rules.length} rules available</span>
                        <div>
                            <button id="select-all-rules" class="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 mr-3">Select All</button>
                            <button id="deselect-all-rules" class="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400">Deselect All</button>
                        </div>
                    </div>
                    <input type="text" id="rules-filter" placeholder="Filter rules..." class="w-full p-2 border border-gray-300 dark:border-gray-600 rounded">
                </div>
                <div id="rules-list" class="border border-gray-200 dark:border-gray-700 rounded max-h-[40vh] overflow-y-auto">
                    ${rulesList}
                </div>
            </div>
            <div class="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-end">
                <button id="cancel-rules-selection" class="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded mr-2">Cancel</button>
                <button id="confirm-rules-selection" class="px-4 py-2 bg-aws-orange text-white rounded hover:bg-amber-600">Visualize Selected Rules</button>
            </div>
        </div>
    `;

  // Show the modal
  modal.classList.remove("hidden");

  // Add keyboard shortcuts for better accessibility
  modal.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      // Close modal on Escape key
      modal.classList.add("hidden");
    } else if (e.key === "Enter" && e.ctrlKey) {
      // Submit on Ctrl+Enter
      document.getElementById("confirm-rules-selection").click();
    }
  });

  // Focus the filter input for immediate typing
  setTimeout(() => {
    document.getElementById("rules-filter").focus();
  }, 100);

  // Add event listeners for modal actions
  document.getElementById("close-rules-modal").addEventListener("click", () => {
    modal.classList.add("hidden");
  });

  document
    .getElementById("cancel-rules-selection")
    .addEventListener("click", () => {
      modal.classList.add("hidden");
    });

  document.getElementById("select-all-rules").addEventListener("click", () => {
    document.querySelectorAll(".rule-checkbox").forEach((checkbox) => {
      // Only select visible rules (respecting the filter)
      if (checkbox.closest("div").style.display !== "none") {
        checkbox.checked = true;
      }
    });
  });

  document
    .getElementById("deselect-all-rules")
    .addEventListener("click", () => {
      document.querySelectorAll(".rule-checkbox").forEach((checkbox) => {
        // Only deselect visible rules (respecting the filter)
        if (checkbox.closest("div").style.display !== "none") {
          checkbox.checked = false;
        }
      });
    });

  // Filter functionality with improved UX
  const rulesFilter = document.getElementById("rules-filter");
  rulesFilter.addEventListener("input", function () {
    const filterText = this.value.toLowerCase();
    let visibleCount = 0;

    document.querySelectorAll("#rules-list > div").forEach((item) => {
      const label = item.querySelector("label");
      if (label) {
        const ruleName = label.textContent.toLowerCase();
        if (ruleName.includes(filterText)) {
          item.style.display = "flex";
          visibleCount++;
        } else {
          item.style.display = "none";
        }
      } else {
        // Handle case where label is null
        item.style.display = "none";
      }
    });

    // Update the rules count to show filtered count
    const rulesCountElement = document.querySelector(".text-sm.text-gray-600");
    if (rulesCountElement) {
      if (filterText) {
        rulesCountElement.textContent = `${visibleCount} of ${rules.length} rules shown`;
      } else {
        rulesCountElement.textContent = `${rules.length} rules available`;
      }
    }
  });

  // Clear filter when clicking X button
  const clearFilterButton = document.createElement("button");
  clearFilterButton.innerHTML = "&times;";
  clearFilterButton.className =
    "absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600";
  clearFilterButton.style.display = "none";
  clearFilterButton.addEventListener("click", () => {
    rulesFilter.value = "";
    rulesFilter.dispatchEvent(new Event("input"));
    rulesFilter.focus();
    clearFilterButton.style.display = "none";
  });

  // Add the clear button to the filter input container
  const filterContainer = rulesFilter.parentNode;
  filterContainer.style.position = "relative";
  filterContainer.appendChild(clearFilterButton);

  // Show/hide clear button based on filter content
  rulesFilter.addEventListener("input", () => {
    clearFilterButton.style.display = rulesFilter.value ? "block" : "none";
  });

  // Handle rule selection confirmation
  document
    .getElementById("confirm-rules-selection")
    .addEventListener("click", () => {
      // Get selected rules
      const selectedRules = Array.from(
        document.querySelectorAll(".rule-checkbox:checked"),
      ).map((checkbox) => checkbox.value);

      // Hide modal
      modal.classList.add("hidden");

      // Show loading indicator
      document.getElementById("loading").classList.remove("hidden");

      // Fetch graph with selected rules
      fetchGraph(eventBusName, selectedRules);

      // Update UI to show selected rules
      document.getElementById("event-bus-name").textContent =
        `Event Bus: ${eventBusName}`;
      const rulesInfo =
        selectedRules.length > 0
          ? `${selectedRules.length} rules selected`
          : "All rules";
      document.getElementById("rules-info").textContent = rulesInfo;

      // Store selected rules globally
      window.selectedRules = selectedRules;
      console.log("Selected rules:", selectedRules);
    });
}
// Function to force update the event bus dropdown
function forceUpdateEventBusDropdown(buses = []) {
  console.log("Force updating event bus dropdown with", buses.length, "buses");
  
  // Get the dropdown element
  const eventBusSelect = document.getElementById("event-bus-select");
  if (!eventBusSelect) {
    console.error("Event bus select element not found");
    return;
  }
  
  // Clear existing options and disabled state
  eventBusSelect.innerHTML = '';
  eventBusSelect.disabled = false;
  eventBusSelect.removeAttribute('disabled');
  
  // Add default option
  const defaultOption = document.createElement('option');
  defaultOption.value = "";
  defaultOption.textContent = buses.length > 0 ? "Select Event Bus" : "No event buses found";
  eventBusSelect.appendChild(defaultOption);
  
  // Add options for each bus
  if (buses.length > 0) {
    buses.forEach(bus => {
      const option = document.createElement('option');
      option.value = typeof bus === 'string' ? bus : bus.Name;
      option.textContent = typeof bus === 'string' ? bus : bus.Name;
      eventBusSelect.appendChild(option);
    });
  }
  
  // Reset the event bus name display
  const eventBusName = document.getElementById("event-bus-name");
  if (eventBusName) {
    eventBusName.textContent = "No event bus selected";
    eventBusName.classList.remove("animate-pulse");
  }
  
  // Force a DOM refresh
  eventBusSelect.style.display = 'none';
  void eventBusSelect.offsetHeight; // Force reflow
  eventBusSelect.style.display = '';
  
  console.log("Dropdown enabled state:", !eventBusSelect.disabled);
  console.log("Dropdown options count:", eventBusSelect.options.length);
}
// Add this to ensure the function is called when the page loads and retry if needed
document.addEventListener('DOMContentLoaded', function() {
  console.log("DOM fully loaded, fetching event buses...");
  fetchEventBuses();
  
  // Also add a retry mechanism
  setTimeout(() => {
    const eventBusSelect = document.getElementById("event-bus-select");
    if (eventBusSelect && (eventBusSelect.disabled || eventBusSelect.options.length <= 1)) {
      console.log("Dropdown still disabled or empty after initial load, retrying...");
      fetchEventBuses();
    }
  }, 2000);
});
// Function to show the rules modal
function showRulesModal() {
  const rulesModal = document.getElementById("rules-modal");
  const rulesModalList = document.getElementById("rules-modal-list");
  
  // Clear previous content
  rulesModalList.innerHTML = "";
  
  // Check if we have rules to display
  if (!window.availableRules || window.availableRules.length === 0) {
    rulesModalList.innerHTML = '<div class="text-gray-500 dark:text-gray-400 text-sm">No rules available</div>';
    rulesModal.classList.remove("hidden");
    return;
  }
  
  // Populate with available rules
  window.availableRules.forEach(rule => {
    const ruleItem = document.createElement("div");
    ruleItem.className = "flex items-center p-2 hover:bg-gray-100 dark:hover:bg-gray-700";
    
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "modal-rule-checkbox mr-2";
    checkbox.value = rule.Name;
    checkbox.id = `modal-rule-${rule.Name}`;
    
    // Check if this rule is already selected in the sidebar
    const sidebarCheckbox = document.querySelector(`.rule-checkbox[value="${rule.Name}"]`);
    if (sidebarCheckbox && sidebarCheckbox.checked) {
      checkbox.checked = true;
    }
    
    const label = document.createElement("label");
    label.htmlFor = `modal-rule-${rule.Name}`;
    label.className = "flex-grow cursor-pointer";
    label.textContent = rule.Name;
    
    ruleItem.appendChild(checkbox);
    ruleItem.appendChild(label);
    rulesModalList.appendChild(ruleItem);
  });
  
  // Show the modal
  rulesModal.classList.remove("hidden");
}

// Function to handle modal filter
function handleModalFilter() {
  const filterText = document.getElementById("rules-modal-filter").value.toLowerCase();
  const ruleItems = document.querySelectorAll("#rules-modal-list > div");
  
  ruleItems.forEach(item => {
    const label = item.querySelector("label");
    if (label) {
      const ruleName = label.textContent.toLowerCase();
      if (ruleName.includes(filterText)) {
        item.style.display = "flex";
      } else {
        item.style.display = "none";
      }
    }
  });
}

// Function to apply rule selection from modal
function applyModalRuleSelection() {
  const modalCheckboxes = document.querySelectorAll(".modal-rule-checkbox");
  const sidebarRulesList = document.getElementById("rules-list");
  
  // Update the sidebar checkboxes based on modal selection
  modalCheckboxes.forEach(modalCheckbox => {
    const ruleName = modalCheckbox.value;
    const sidebarCheckbox = document.querySelector(`.rule-checkbox[value="${ruleName}"]`);
    
    if (sidebarCheckbox) {
      sidebarCheckbox.checked = modalCheckbox.checked;
    }
  });
  
  // Close the modal
  document.getElementById("rules-modal").classList.add("hidden");
  
  // Apply the rule selection
  applyRuleSelection();
}

// Add event listeners for the rules modal
document.addEventListener("DOMContentLoaded", function() {
  // Show rules modal button
  const showRulesBtn = document.getElementById("show-rules-btn");
  if (showRulesBtn) {
    showRulesBtn.addEventListener("click", function() {
      const selectedBusName = document.getElementById("event-bus-select").value;
      if (!selectedBusName) {
        alert("Please select an event bus first.");
        return;
      }
      if (window.availableRules && window.availableRules.length > 0) {
        // Ensure availableRules are for the currently selected bus.
        // This assumption is stronger now that fetchRulesAndShowModal also updates it.
        showRulesSelectionModal(selectedBusName, window.availableRules);
      } else {
        // Rules are not immediately available, so fetch them and then show the modal.
        fetchRulesAndShowModal(selectedBusName); 
      }
    });
  }
  
  // Close modal button
  const closeModalBtn = document.getElementById("rules-modal-close");
  if (closeModalBtn) {
    closeModalBtn.addEventListener("click", () => {
      document.getElementById("rules-modal").classList.add("hidden");
    });
  }
  
  // Apply button
  const applyBtn = document.getElementById("rules-modal-apply");
  if (applyBtn) {
    applyBtn.addEventListener("click", applyModalRuleSelection);
  }
  
  // Filter input
  const filterInput = document.getElementById("rules-modal-filter");
  if (filterInput) {
    filterInput.addEventListener("input", handleModalFilter);
  }
});

// ... existing code ...
// (This function should be placed after _applyPersistentCytoscapeEventHandlers and before it's first used)

// Function to render the graph using Cytoscape with the provided data
function _internalRenderActualGraph(graphPayload) {
  try {
    initCytoscapeInstance(); // Ensures cy exists, is empty, and persistent handlers are attached if first time

    if (!cy || typeof cy.add !== 'function') {
        console.error("_internalRenderActualGraph: Cytoscape instance (cy) is not valid. Skipping graph rendering.");
        // Display error to user
        const errMessageContainer = document.getElementById("error-message");
        if (errMessageContainer) errMessageContainer.textContent = "Graph engine failed to initialize.";
        const errContainer = document.getElementById("error");
        if (errContainer) errContainer.style.display = "block";
        return;
    }

    let cytoscapeElements = [];
    if (graphPayload && graphPayload.elements && 
        typeof graphPayload.elements === 'object' && 
        Array.isArray(graphPayload.elements.nodes) && 
        Array.isArray(graphPayload.elements.edges)) {

      // Node type and icon inference (operates on graphPayload.elements.nodes)
      graphPayload.elements.nodes.forEach(node => {
        // Ensure node.data exists
        if (!node.data) node.data = { id: node.id }; // Basic fallback if data is missing
        if (!node.data.id && node.id) node.data.id = node.id; // Ensure data.id if only node.id exists

        if (!node.data.type) { // Only infer if type is not already provided
          const id = String(node.data.id || "").toLowerCase();
          const arn = String(node.data.arn || "").toLowerCase();
          if (id.includes("rule")) {
            node.data.type = "rule";
          } else if (id.includes("bus")) {
            node.data.type = "event_bus";
          } else if (id.includes("target") || arn.includes(":lambda:") || arn.includes(":sqs:") || arn.includes(":sns:") || arn.includes(":states:") || arn.includes(":apigateway:")) {
            node.data.type = "target";
            if (!node.data.icon) {
                if (arn.includes(":lambda:")) node.data.icon = "lambda";
                else if (arn.includes(":sqs:")) node.data.icon = "sqs";
                else if (arn.includes(":sns:")) node.data.icon = "sns";
            }
          } else if (id.includes("log_stream")) {
            node.data.type = "log_stream";
          } else if (id.includes("log_placeholder")) {
            node.data.type = "log_placeholder";
          }
        }

        // Ensure data.label is set for Cytoscape's style mapping
        if (typeof node.data.label === 'undefined') { // Check if label is not set at all
          node.data.label = node.data.name || node.data.id || ""; // Use name, fallback to id, then empty string
        }
      });
      
      // Build a set of connected node IDs based on the edges
      const connectedNodes = new Set();
      const selectedBusNodes = new Set();
      
      // First find the event bus node(s)
      graphPayload.elements.nodes.forEach(node => {
        if (node.data && node.data.type === "event_bus") {
          selectedBusNodes.add(node.data.id);
          connectedNodes.add(node.data.id);
        }
      });
      
      // Add all nodes connected by edges (directly or indirectly) to the event bus
      let newNodesAdded = true;
      while (newNodesAdded) {
        newNodesAdded = false;
        graphPayload.elements.edges.forEach(edge => {
          if (edge.data) {
            if (connectedNodes.has(edge.data.source) && !connectedNodes.has(edge.data.target)) {
              connectedNodes.add(edge.data.target);
              newNodesAdded = true;
            }
            else if (connectedNodes.has(edge.data.target) && !connectedNodes.has(edge.data.source)) {
              connectedNodes.add(edge.data.source);
              newNodesAdded = true;
            }
          }
        });
      }
      
      // Filter to keep only connected nodes and their edges
      const filteredNodes = graphPayload.elements.nodes.filter(node => 
        node.data && connectedNodes.has(node.data.id)
      );
      
      const filteredEdges = graphPayload.elements.edges.filter(edge => 
        edge.data && connectedNodes.has(edge.data.source) && connectedNodes.has(edge.data.target)
      );
      
      cytoscapeElements = filteredNodes.concat(filteredEdges);
      console.log(`Filtered graph from ${graphPayload.elements.nodes.length} nodes to ${filteredNodes.length} connected nodes`);
    } else {
      console.warn("Graph data is not in the expected format (elements object with nodes/edges arrays) or is empty.", graphPayload);
    }

    if (cytoscapeElements.length > 0) {
      cy.add(cytoscapeElements); 
      
      if (typeof applyDagreLayout === 'function') {
        applyDagreLayout();
      } else {
        console.error("applyDagreLayout function not found. Graph layout may not be applied.");
      }
    } else {
      // Handle empty graph data: clear graph and show message
      if (cy) cy.elements().remove(); 
      const errMessageContainer = document.getElementById("error-message");
      if (errMessageContainer) errMessageContainer.textContent = "No graph data to display (or data was empty/invalid).";
      const errContainer = document.getElementById("error");
      if (errContainer) errContainer.style.display = "block";
      console.warn("No valid elements found in graphPayload to render after processing.");
    }
  } catch (error) {
    console.error("Error in _internalRenderActualGraph:", error);
    const errMessageContainer = document.getElementById("error-message");
    if (errMessageContainer) errMessageContainer.textContent = "Error rendering graph: " + error.toString();
    const errContainer = document.getElementById("error");
    if (errContainer) errContainer.style.display = "block";
  }
}

// ... existing code ...
// This function should be placed before the window.renderGraph override and loadGraphData modifications.

function handleStreamListItemClick(logGroupName, logStreamName) {
    console.log(`Clicked on log stream ${logStreamName} in group ${logGroupName}`);
    
    // Get current search term if available
    let searchTerm = '';
    if (window.logSearchManager && window.logSearchManager.searchTerm) {
      searchTerm = window.logSearchManager.searchTerm;
    }
    
    // Show the logs in a modal
    showStreamLogsInModal(logGroupName, logStreamName, searchTerm);
}

// Function to update the details sidebar with node information
function updateDetailsSidebar(nodeData) {
  const detailsContent = document.getElementById("details-content");
  const sidebar = document.getElementById("sidebar");
  const detailsTitle = document.querySelector("#details-container > h2");
  const logsContentContainer = document.getElementById("logs-content-container");
  let defaultTab = "details";
  
  if (!detailsContent) {
    console.error("Details content element not found");
    return;
  }
  
  if (!sidebar) {
    console.error("Sidebar element not found");
    return;
  }

  const nodeId = nodeData.id || nodeData.name || 'Unknown';
  const nodeType = nodeData.type || 'Unknown';

  // Generate details HTML based on node type
  let detailsHtml = '';

  if (nodeType === "event_bus") {
    if (detailsTitle) detailsTitle.textContent = `Event Bus: ${nodeData.label || nodeId}`;
    detailsHtml = `
      <div class="details-section">
        <div class="details-title">Event Bus Information</div>
        <div class="details-value">
          <span class="details-label">Name:</span> ${nodeData.label || nodeId}<br>
          <span class="details-label">Type:</span> EventBridge Event Bus
        </div>
      </div>
    `;
  } else if (nodeType === "rule") {
    if (detailsTitle) detailsTitle.textContent = `Rule: ${nodeData.label || nodeId}`;
    detailsHtml = `
      <div class="details-section">
        <div class="details-title">Rule Information</div>
        <div class="details-value">
          <span class="details-label">Name:</span> ${nodeData.label || nodeId}<br>
          ${nodeData.description ? `<span class="details-label">Description:</span> ${nodeData.description}<br>` : ""}
        </div>
      </div>
    `;

    let eventPatternHtml = '';
    let patternForTemplate = {};
    
    if (nodeData.eventPattern) {
      try {
        // Parse the event pattern for template use
        patternForTemplate = typeof nodeData.eventPattern === 'string' 
          ? JSON.parse(nodeData.eventPattern) 
          : nodeData.eventPattern;
          
        // Format for display
        const formattedPattern = typeof nodeData.eventPattern === 'string' ? 
                              formatJsonString(nodeData.eventPattern) :
                              formatJson(nodeData.eventPattern);
        
        eventPatternHtml = `
          <div class="details-section mt-4">
            <div class="details-title flex justify-between items-center">
              <span>Event Pattern</span>
              <button id="use-pattern-as-template" class="text-xs bg-aws-orange hover:bg-amber-600 text-white px-2 py-1 rounded">
                Use as Template
              </button>
            </div>
            <div class="json-content mt-2 border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 p-2 rounded overflow-auto max-h-60">
              ${formattedPattern}
            </div>
          </div>
        `;
      } catch (e) {
        eventPatternHtml = `
          <div class="details-section mt-4">
            <div class="details-title">Event Pattern (raw)</div>
            <pre class="text-xs bg-gray-700 dark:bg-gray-900 p-2 rounded">${escapeHtml(JSON.stringify(nodeData.eventPattern, null, 2))}</pre>
          </div>
        `;
      }
    }
    
    // Add pattern section first, then test event section
    detailsHtml += eventPatternHtml;
    
    // Add section to send test events to the event bus
    detailsHtml += `
      <div class="details-section mt-4">
        <div class="details-title">Send Test Event</div>
        <div class="text-xs text-gray-600 dark:text-gray-300 mb-2">
          Create a test event that matches the pattern above. Click "Use as Template" to start with the rule's pattern.
        </div>
        <div class="mt-2">
          <textarea id="test-event-json" 
            class="w-full h-32 p-2 text-xs font-mono border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200"
            placeholder='{\n  "source": "test.event",\n  "detail-type": "Test Event",\n  "detail": {\n    "key": "value"\n  }\n}'></textarea>
          <div class="flex justify-between items-center mt-2">
            <div id="event-send-status" class="text-xs"></div>
            <div class="flex space-x-2">
              <button id="format-json-btn" 
                class="px-3 py-1 bg-gray-200 hover:bg-gray-300 text-gray-800 dark:bg-gray-700 dark:hover:bg-gray-600 dark:text-white rounded"
                title="Format JSON in the text area">
                Format JSON
              </button>
              <button id="send-test-event-btn" 
                class="px-3 py-1 bg-aws-orange text-white rounded hover:bg-amber-600"
                data-rule-name="${nodeData.label || nodeId}">
                Send Event
              </button>
            </div>
          </div>
        </div>
      </div>
    `;
  } else if (nodeType === "target") {
    const targetArn = nodeData.arn || "Unknown";
    const targetId = nodeData.name || 'Unknown';
    const ruleName = nodeData.rule_name || 'N/A';
    
    // Debug the node data to see what's available
    console.log("Target node data:", nodeData);
    console.log("Target ARN:", targetArn);
    console.log("Target ID:", targetId);
    console.log("Node label:", nodeData.label);
    
    // Extract function name from Lambda ARN if available
    let functionName = targetId;
    if (targetArn && targetArn.includes(':function:')) {
      const arnParts = targetArn.split(':function:');
      if (arnParts.length > 1) {
        functionName = arnParts[1];
      }
    }
    
    // Use nodeData.label if available, otherwise use the extracted function name
    const displayName = nodeData.label || functionName;
    
    if (detailsTitle) detailsTitle.textContent = `Target: ${displayName}`;
    
    detailsHtml = `
      <div class="details-section">
        <div class="details-title">Target Information</div>
        <div class="details-value">
          <span class="details-label">Display Name:</span> ${displayName}<br>
          <span class="details-label">ID in Rule:</span> ${targetId}<br>
          <span class="details-label">ARN:</span> <span class="break-all">${targetArn}</span><br>
          <span class="details-label">Parent Rule:</span> ${ruleName}<br>
        </div>
      </div>
      
      <div class="details-section">
        <div class="details-title">Log Streams</div>
        <div id="log-streams-container" class="mt-3 p-2 bg-gray-50 dark:bg-gray-900 rounded">
          <div class="text-center p-4">
            <div class="animate-spin inline-block w-6 h-6 border-2 border-aws-orange border-t-transparent rounded-full mb-2"></div>
            <div>Loading log streams...</div>
          </div>
        </div>
      </div>`;
    
    // Fetch log streams for this target
    fetchLogStreams(targetArn).then(streams => {
      displayLogStreamsInDetails(streams);
    }).catch(error => {
      const container = document.getElementById("log-streams-container");
      if (container) {
        container.innerHTML = `
          <div class="text-red-500 p-2">Error loading log streams: ${error.message}</div>
        `;
      }
    });
  } else if (nodeType === 'target_log_streams_summary') {
    const parentTargetId = nodeData.parent_target_id || 'Unknown Target';
    const streams = nodeData.streams || []; 
    
    if (detailsTitle) detailsTitle.textContent = `Log Streams for Target: ${parentTargetId.substring(parentTargetId.indexOf(':')+1)}`;
    
    detailsHtml = `
      <div class="details-section">
        <div class="details-title">Log Streams</div>
        <div class="details-value">
          <span class="details-label">Target:</span> ${parentTargetId.substring(parentTargetId.indexOf(':')+1)}<br>
          <span class="details-label">Stream Count:</span> ${streams.length}<br>
        </div>
      </div>
      
      <div class="details-section mt-4">
        <div class="details-title">Available Log Streams</div>
        <div class="details-value">
          ${streams.length > 0 
            ? streams.map(stream => 
              `<div class="stream-item cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 p-2 rounded" 
                   onclick="showStreamLogsInModal('${stream.logGroupName || ''}', '${stream.logStreamName || ''}')">
                 <div class="text-aws-blue dark:text-aws-sky font-semibold">${stream.logStreamName || 'Unnamed'}</div>
                 <div class="text-xs text-gray-500">Last event: ${stream.lastEventTime || 'N/A'}</div>
               </div>`
            ).join('')
            : '<div class="text-gray-500">No streams available</div>'
          }
        </div>
      </div>
    `;
  } else if (nodeType === 'log_placeholder') {
    if (detailsTitle) detailsTitle.textContent = `Log Information: ${nodeData.label || nodeId}`;
    detailsHtml = `
      <div class="p-4">
        <p class="text-gray-600 dark:text-gray-300">${nodeData.label || 'Information about logs.'}</p>
        ${nodeData.error ? `<p class="text-red-500 text-xs mt-2">Details: ${escapeHtml(nodeData.error)}</p>` : ''}
      </div>
    `;
    if (logsContentContainer) {
      logsContentContainer.innerHTML = '<div class="p-4 text-gray-500 dark:text-gray-400">No specific logs to display for this placeholder.</div>';
    }
    defaultTab = "details";
  } else {
    if (detailsTitle) detailsTitle.textContent = `Details: ${nodeData.label || nodeId}`;
    detailsHtml = `<div class="p-4 text-gray-500 dark:text-gray-400">Details for node type '${nodeType}' not specifically handled. ID: ${escapeHtml(nodeId)}</div>`;
    if (logsContentContainer) {
      logsContentContainer.innerHTML = "";
    }
  }

  // Update the details content with the generated HTML
  detailsContent.innerHTML = detailsHtml;

  // Ensure the sidebar is visible (for mobile responsiveness)
  if (sidebar.classList.contains('hidden')) {
    sidebar.classList.remove('hidden');
  }
  
  // Make sure the drawer is properly sized
  sidebar.style.transition = "width 0.3s ease";
  sidebar.style.width = "600px"; 
  
  // Enable drawer resizing if the function exists
  if (typeof makeDrawerResizable === 'function') {
    makeDrawerResizable();
  }

  // Set the active tab if using tabs
  if (document.querySelector('.drawer-tab')) {
    const defaultTabButton = document.querySelector(`.drawer-tab[data-tab="${defaultTab}"]`);
    if (defaultTabButton && typeof defaultTabButton.click === 'function') {
      defaultTabButton.click();
    } else {
      const fallbackDetailsTab = document.querySelector('.drawer-tab[data-tab="details"]');
      if(fallbackDetailsTab && typeof fallbackDetailsTab.click === 'function') fallbackDetailsTab.click();
    }
  }
  
  // Set up event listeners for rule-specific functionality
  if (nodeType === "rule") {
    // Set up event listener for the "Use as Template" button
    const usePatternBtn = document.getElementById("use-pattern-as-template");
    const eventJsonTextarea = document.getElementById("test-event-json");
    const sendButton = document.getElementById("send-test-event-btn");
    const formatJsonBtn = document.getElementById("format-json-btn");
    const statusElement = document.getElementById("event-send-status");
    
    if (usePatternBtn && eventJsonTextarea) {
      usePatternBtn.addEventListener("click", function() {
        try {
          // Create a template event based on the rule pattern
          let templateEvent = {
            source: "test.event",
            "detail-type": "Test Event",
            detail: {}
          };
          
          // Get the pattern structure from the rule
          const pattern = typeof nodeData.eventPattern === 'string' 
            ? JSON.parse(nodeData.eventPattern) 
            : nodeData.eventPattern;
            
          // If the pattern has a source, use it
          if (pattern.source) {
            if (Array.isArray(pattern.source)) {
              templateEvent.source = pattern.source[0];
            } else {
              templateEvent.source = pattern.source;
            }
          }
          
          // If the pattern has a detail-type, use it
          if (pattern['detail-type']) {
            if (Array.isArray(pattern['detail-type'])) {
              templateEvent['detail-type'] = pattern['detail-type'][0];
            } else {
              templateEvent['detail-type'] = pattern['detail-type'];
            }
          }
          
          // If the pattern has detail fields, use them as a template
          if (pattern.detail) {
            templateEvent.detail = {};
            
            // For each detail field in the pattern, add a placeholder in the template
            for (const [key, value] of Object.entries(pattern.detail)) {
              if (Array.isArray(value)) {
                templateEvent.detail[key] = value[0];
              } else if (typeof value === 'object') {
                // For nested objects, create a template object
                templateEvent.detail[key] = {};
                for (const [nestedKey, nestedValue] of Object.entries(value)) {
                  if (Array.isArray(nestedValue)) {
                    templateEvent.detail[key][nestedKey] = nestedValue[0];
                  } else {
                    templateEvent.detail[key][nestedKey] = nestedValue;
                  }
                }
              } else {
                templateEvent.detail[key] = value;
              }
            }
          }
          
          // Set the textarea value to the formatted template
          eventJsonTextarea.value = JSON.stringify(templateEvent, null, 2);
          
          // Show success message
          statusElement.textContent = "Template applied";
          statusElement.className = "text-xs text-green-500";
          
          // Clear message after 3 seconds
          setTimeout(() => {
            statusElement.textContent = "";
          }, 3000);
        } catch (error) {
          console.error("Error creating template:", error);
          statusElement.textContent = `Error creating template: ${error.message}`;
          statusElement.className = "text-xs text-red-500";
        }
      });
    }
    
    // Add event listener for the Format JSON button
    if (formatJsonBtn && eventJsonTextarea && statusElement) {
      formatJsonBtn.addEventListener("click", function() {
        try {
          // Parse the current JSON in the textarea
          const jsonData = JSON.parse(eventJsonTextarea.value);
          
          // Format the JSON with indentation and write it back to the textarea
          eventJsonTextarea.value = JSON.stringify(jsonData, null, 2);
          
          // Show success message
          statusElement.textContent = "JSON formatted";
          statusElement.className = "text-xs text-green-500";
          
          // Clear message after 3 seconds
          setTimeout(() => {
            statusElement.textContent = "";
          }, 3000);
        } catch (error) {
          console.error("Error formatting JSON:", error);
          statusElement.textContent = `Error: ${error.message}`;
          statusElement.className = "text-xs text-red-500";
        }
      });
    }
    
    if (sendButton && eventJsonTextarea && statusElement) {
      sendButton.onclick = function() {
        // Get the rule name and event data
        const ruleName = this.getAttribute("data-rule-name");
        let eventData;
        
        try {
          eventData = JSON.parse(eventJsonTextarea.value);
          statusElement.textContent = "Sending event...";
          statusElement.className = "text-xs text-blue-500";
          
          // Send the event
          sendEventToEventBus(eventData, ruleName, statusElement);
        } catch (error) {
          statusElement.textContent = `Error: ${error.message}`;
          statusElement.className = "text-xs text-red-500";
        }
      };
    }
  }
}

// Function to send a test event to the EventBridge event bus
function sendEventToEventBus(eventData, ruleName, statusElement) {
  // Get the currently selected event bus
  const eventBusSelect = document.getElementById("event-bus-select");
  const eventBusName = eventBusSelect ? eventBusSelect.value : 'default';
  
  // Send the event to the API
  fetch('/api/send_event', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      event_data: eventData,
      event_bus_name: eventBusName
    })
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Show success message
      statusElement.textContent = data.message;
      statusElement.className = "text-xs text-green-500";
      
      // Clear success message after 5 seconds
      setTimeout(() => {
        statusElement.textContent = "";
      }, 5000);
    } else {
      // Show error message
      statusElement.textContent = `Error: ${data.message}`;
      statusElement.className = "text-xs text-red-500";
    }
  })
  .catch(error => {
    // Show error message
    statusElement.textContent = `Error: ${error.message}`;
    statusElement.className = "text-xs text-red-500";
    console.error("Error sending test event:", error);
  });
}

// Format log text with Tailwind styling

// Function to fetch logs from a specific stream and display them in a modal
function showStreamLogsInModal(logGroup, logStream, searchTerm = '') {
  if (!logGroup || !logStream) {
    console.error("Log group or stream name missing");
    return;
  }

  console.log(`Showing logs from stream: ${logStream} in group: ${logGroup}`);
  console.log(`Initial search term: ${searchTerm}`);

  // Show the modal and update the title
  const targetNameElement = document.getElementById("log-target-name");
  if (targetNameElement) {
    targetNameElement.textContent = `Stream: ${logStream}`;
  }
  
  // Use the centralized function to show the modal
  showLogViewerModal();

  // Show loading indicator
  const logContentContainer = document.getElementById("log-content-container");
  if (logContentContainer) {
    logContentContainer.innerHTML = '<div class="flex justify-center items-center h-full"><div class="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-aws-orange"></div></div>';
  }

  // Set the search term if provided
  const searchInput = document.getElementById("log-search-input");
  if (searchInput && searchTerm) {
    searchInput.value = searchTerm;
  }

  // Fetch logs from the stream
  fetch('/api/stream_logs', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      logGroup: logGroup,
      logStream: logStream,
      // Use a 30-year range to get all logs
      startTime: Math.floor(new Date().getTime() / 1000) - (30 * 365 * 24 * 60 * 60),
      endTime: Math.floor(new Date().getTime() / 1000),
      limit: 500  // increased from 100 to show more logs
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }
    return response.json();
  })
  .then(data => {
    if (data.success) {
      // Update the modal content
      const logContentContainer = document.getElementById("log-content-container");
      if (logContentContainer) {
        // Process logs with timestamps and formatting
        logContentContainer.innerHTML = formatLogsWithTailwind(data.logs);
        
        // Setup search functionality
        setupLogSearch();
        
        // If search term was provided, trigger search immediately
        if (searchTerm && searchInput) {
          // Set input value again to ensure it's set after everything is rendered
          searchInput.value = searchTerm;
          console.log(`Triggering search for: ${searchTerm}`);
          // Trigger the input event to activate the search
          setTimeout(() => {
            const event = new Event('input', { bubbles: true });
            searchInput.dispatchEvent(event);
          }, 100);
        }
      }
    } else {
      const logContentContainer = document.getElementById("log-content-container");
      if (logContentContainer) {
        logContentContainer.innerHTML = `<div class="text-red-500 p-4">Error: ${data.message || 'Failed to load logs'}</div>`;
      }
    }
  })
  .catch(error => {
    console.error("Error fetching stream logs:", error);
    const logContentContainer = document.getElementById("log-content-container");
    if (logContentContainer) {
      logContentContainer.innerHTML = `<div class="text-red-500 p-4">Error: ${error.message}</div>`;
    }
  });
}

// Set up search functionality for logs
function setupLogSearch() {
  const searchInput = document.getElementById("log-search-input");
  const logContentContainer = document.getElementById("log-content-container");
  const searchNavControls = document.getElementById("search-nav-controls");
  const searchMatchCount = document.getElementById("search-match-count");
  const prevMatchBtn = document.getElementById("prev-match-btn");
  const nextMatchBtn = document.getElementById("next-match-btn");
  
  if (!searchInput || !logContentContainer) {
    console.error("Search input or log container not found");
    return;
  }
  
  console.log("Setting up log search functionality");
  
  // Track current position in search results
  let currentMatchIndex = -1;
  let matchElements = [];
  
  // Store the original content to avoid cumulative highlights on multiple searches
  const originalContent = logContentContainer.innerHTML;
  
  // Add event listener for search input
  searchInput.removeEventListener("input", searchInput.searchHandler); // Remove any existing handler
  
  searchInput.searchHandler = function() {
    const searchTerm = this.value.trim();
    console.log(`Searching for: "${searchTerm}"`);
    
    // Reset match tracking
    currentMatchIndex = -1;
    matchElements = [];
    
    // Restore original content to avoid cumulative highlights
    logContentContainer.innerHTML = originalContent;
    
    // Hide navigation controls if search is empty
    if (searchNavControls) {
      if (!searchTerm) {
        searchNavControls.classList.add("hidden");
        return;
      } else {
        searchNavControls.classList.remove("hidden");
      }
    }
    
    // Highlight matches with the search term
    if (searchTerm) {
      try {
        // Create a safe regex pattern, escaping special characters
        const escapedSearchTerm = searchTerm.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        const searchRegex = new RegExp(`(${escapedSearchTerm})`, 'gi');
        
        // Apply highlighting by replacing text nodes
        highlightSearchTermInDOM(logContentContainer, searchRegex);
        
        // Collect all match elements for navigation
        matchElements = Array.from(logContentContainer.querySelectorAll(".search-match"));
        console.log(`Found ${matchElements.length} matches for "${searchTerm}"`);
        
        // Update match count
        if (searchMatchCount) {
          searchMatchCount.textContent = `${matchElements.length} match${matchElements.length !== 1 ? 'es' : ''}`;
        }
        
        // If we have matches, set the first one as current
        if (matchElements.length > 0) {
          currentMatchIndex = 0;
          matchElements[currentMatchIndex].classList.add("current-match");
          scrollToCurrentMatch();
        } else {
          // Show "no matches found" message
          const noMatchesMsg = document.createElement('div');
          noMatchesMsg.className = 'fixed bottom-20 left-1/2 transform -translate-x-1/2 bg-gray-800 text-white px-4 py-2 rounded-lg';
          noMatchesMsg.textContent = `No matches found for "${searchTerm}"`;
          document.body.appendChild(noMatchesMsg);
          
          // Remove message after 3 seconds
          setTimeout(() => {
            if (noMatchesMsg.parentNode) {
              noMatchesMsg.parentNode.removeChild(noMatchesMsg);
            }
          }, 3000);
        }
      } catch (error) {
        console.error("Error in search:", error);
      }
    }
  };
  
  searchInput.addEventListener("input", searchInput.searchHandler);
  
  // Add event listeners for navigation buttons
  if (prevMatchBtn) {
    prevMatchBtn.onclick = function() {
      if (matchElements.length === 0) return;
      
      // Remove current highlight
      matchElements[currentMatchIndex].classList.remove("current-match");
      
      // Move to previous match
      currentMatchIndex = (currentMatchIndex - 1 + matchElements.length) % matchElements.length;
      
      // Highlight new current match
      matchElements[currentMatchIndex].classList.add("current-match");
      scrollToCurrentMatch();
    };
  }
  
  if (nextMatchBtn) {
    nextMatchBtn.onclick = function() {
      if (matchElements.length === 0) return;
      
      // Remove current highlight
      matchElements[currentMatchIndex].classList.remove("current-match");
      
      // Move to next match
      currentMatchIndex = (currentMatchIndex + 1) % matchElements.length;
      
      // Highlight new current match
      matchElements[currentMatchIndex].classList.add("current-match");
      scrollToCurrentMatch();
    };
  }
  
  // Check if we already have a search term in the input (pre-filled)
  // and trigger the search if we do
  if (searchInput.value.trim()) {
    console.log(`Pre-filled search term found: ${searchInput.value}`);
    searchInput.dispatchEvent(new Event('input'));
  }
  
  // Helper function to scroll to current match
  function scrollToCurrentMatch() {
    if (currentMatchIndex >= 0 && currentMatchIndex < matchElements.length) {
      const currentElement = matchElements[currentMatchIndex];
      currentElement.scrollIntoView({
        behavior: "smooth",
        block: "center"
      });
    }
  }
}

// Recursively traverse DOM and highlight search term in text nodes
function highlightSearchTermInDOM(element, regex) {
  if (!element) return;
  
  // Handle text nodes
  if (element.nodeType === Node.TEXT_NODE) {
    const content = element.textContent;
    if (regex.test(content)) {
      // Create a wrapper span
      const wrapper = document.createElement('span');
      
      // Replace occurrences with highlighted spans
      wrapper.innerHTML = content.replace(regex, '<span class="search-match bg-yellow-300 text-gray-900 font-semibold">$1</span>');
      
      // Replace the text node with our wrapper
      if (element.parentNode) {
        element.parentNode.replaceChild(wrapper, element);
      }
    }
    return;
  }
  
  // Skip search-match elements to avoid recursive highlighting
  if (element.classList && element.classList.contains('search-match')) {
    return;
  }
  
  // Process child nodes recursively
  const childNodes = Array.from(element.childNodes);
  childNodes.forEach(child => highlightSearchTermInDOM(child, regex));
}

// Format logs with search term highlights
function formatLogsWithHighlights(logs, searchTerm) {
  if (!logs || !searchTerm) return logs;
  
  try {
    // Create regex for the search term with proper escaping
    const searchRegex = new RegExp(`(${escapeRegExp(searchTerm)})`, 'gi');
    
    // Replace all occurrences with highlighted version
    return logs.replace(searchRegex, '<span class="search-match bg-yellow-300 text-gray-900 font-semibold">$1</span>');
  } catch (error) {
    console.error('Error highlighting logs:', error);
    return logs;
  }
}

// Helper function to escape regular expression special characters
function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
}