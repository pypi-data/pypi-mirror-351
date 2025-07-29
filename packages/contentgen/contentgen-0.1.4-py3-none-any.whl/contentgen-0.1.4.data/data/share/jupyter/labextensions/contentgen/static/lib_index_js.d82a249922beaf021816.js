"use strict";
(self["webpackChunkcontentgen"] = self["webpackChunkcontentgen"] || []).push([["lib_index_js"],{

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   requestAPI: () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


/**
 * Call the API extension
 *
 * @param endPoint API REST end point for the extension
 * @param init Initial values for the request
 * @returns The response body interpreted as JSON
 */
async function requestAPI(endPoint = '', init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'contentgen', // API Namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    let data = await response.text();
    if (data.length > 0) {
        try {
            data = JSON.parse(data);
        }
        catch (error) {
            console.log('Not a JSON response body.', response);
        }
    }
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _handler_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./handler.js */ "./lib/handler.js");
/* harmony import */ var _style_index_css__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! ../style/index.css */ "./style/index.css");







// Add these at the top level, before the plugin definition
let isFollowupMode = false;
let previousQuestion = "";
let lastInsertedCellIndex = -1;
let notebookDirectory = ''; // current notebook directory
let notebookName = ''; // current notebook name
let currentRowId = null;
let userDecision = null;
let notebookStructure = null;
/**
 * Initialization data for the contentgen extension.
 */
const plugin = {
    id: 'contentgen:plugin',
    description: 'An instructor-assistant JupyterLab extension for generating in-context lecture questions and supplementary teaching materials.',
    autoStart: true,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__.INotebookTracker],
    optional: [_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILayoutRestorer],
    activate: async (app, notebookTracker, restorer) => {
        console.log('JupyterLab extension contentgen is activated!');
        const newWidget = async () => {
            const content = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_2__.Widget();
            content.node.classList.add('chatbot-panel');
            // Create chat container first
            const chatContainer = document.createElement('div');
            chatContainer.classList.add('chat-container');
            // Create header inside chat container
            const chatHeader = document.createElement('div');
            chatHeader.classList.add('chat-header');
            // Add notebook name and model info
            const notebookNameDiv = document.createElement('div');
            notebookNameDiv.classList.add('model-info');
            notebookNameDiv.textContent = 'No notebook open';
            const modelInfo = document.createElement('div');
            modelInfo.classList.add('notebook-name-display');
            modelInfo.textContent = 'gemini-2.0-flash';
            // Add notebook index
            const notebookIndexDiv = document.createElement('div');
            notebookIndexDiv.classList.add('model-info');
            notebookIndexDiv.textContent = 'Notebook Index: ';
            chatHeader.appendChild(notebookNameDiv);
            chatHeader.appendChild(notebookIndexDiv);
            chatHeader.appendChild(modelInfo);
            chatContainer.appendChild(chatHeader);
            // Create messages container
            const messagesContainer = document.createElement('div');
            messagesContainer.classList.add('messages-container');
            chatContainer.appendChild(messagesContainer);
            // Create input container
            const inputContainer = document.createElement('div');
            inputContainer.classList.add('input-container');
            // Add text input
            const inputBox = document.createElement('textarea');
            inputBox.classList.add('chat-input');
            inputBox.placeholder = 'Generate a practice question based on selected code...';
            // Create mode toggle button
            const modeToggleButton = document.createElement('button');
            modeToggleButton.textContent = '📝';
            modeToggleButton.classList.add('mode-toggle');
            modeToggleButton.title = 'Toggle between Question Generation and URL Summary';
            let isUrlMode = false;
            if (notebookStructure === null) {
                sendNotebookContent(notebookTracker).then((result) => {
                    notebookStructure = result;
                });
            }
            // Simplify mode toggle functionality
            modeToggleButton.addEventListener('click', () => {
                isUrlMode = !isUrlMode;
                isFollowupMode = false; // Reset follow-up mode when switching modes
                if (isUrlMode) {
                    modeToggleButton.textContent = '🔗';
                    inputBox.placeholder = 'Enter URL to summarize content...';
                }
                else {
                    modeToggleButton.textContent = '📝';
                    inputBox.placeholder = 'Generate a practice question based on selected code...';
                }
            });
            // Simplify interface assembly
            inputContainer.appendChild(modeToggleButton);
            inputContainer.appendChild(inputBox);
            chatContainer.appendChild(inputContainer);
            // Append chat container to content
            content.node.appendChild(chatContainer);
            // Create button container for Apply/Cancel
            const buttonContainer = document.createElement('div');
            buttonContainer.id = "chat-buttons-container";
            content.node.appendChild(buttonContainer);
            // Modify the handleMessage function to handle follow-up questions
            const handleMessage = async () => {
                var _a, _b, _c, _d, _e, _f, _g, _h;
                const message = inputBox.value.trim();
                if (message) {
                    // Show user message immediately
                    addMessageToChat('user', message);
                    inputBox.value = ''; // Clear input
                    // Show loading indicator
                    showLoadingIndicator();
                    try {
                        // Get current notebook
                        const currentNotebook = notebookTracker.currentWidget;
                        const notebookContent = [];
                        updateNotebookDirectory();
                        const notebookCodeCells = [];
                        const dataLoadingPattern = /(pd\.read_(csv|excel|json|html)\(|sns\.load_dataset\(|pd\.DataFrame\(|pd\.DataFrame\.from_dict\(|pd\.DataFrame\.from_records\()/; // Regular expression pattern to detect DataFrame creation
                        const dataLoadingCells = []; // List to store indices of dataset-loading cells
                        if (currentNotebook && currentNotebook.content) {
                            const notebook = currentNotebook.content;
                            const notebookModel = notebook === null || notebook === void 0 ? void 0 : notebook.model;
                            if (notebookModel) {
                                try {
                                    const cells = notebookModel.cells;
                                    const notebookWidget = currentNotebook.content; // Get notebook widget properly
                                    if (!notebookWidget) {
                                        addMessageToChat('system', 'Error: No active notebook');
                                        return;
                                    }
                                    // Get selected cells using notebook's active cell index
                                    const activeIndex = (_b = (_a = notebookTracker.currentWidget) === null || _a === void 0 ? void 0 : _a.content.activeCellIndex) !== null && _b !== void 0 ? _b : 0;
                                    const selectedCells = [cells.get(activeIndex)]; // Use active cell as selected cell
                                    // Handle cells differently based on mode
                                    if (isUrlMode) {
                                        // URL mode - process all cells
                                        for (let i = 0; i < cells.length; i++) {
                                            const cell = cells.get(i);
                                            notebookContent.push({
                                                index: i + 1,
                                                content: cell.sharedModel.getSource()
                                            });
                                        }
                                    }
                                    else {
                                        // Question mode - require cell selection
                                        if (selectedCells.length === 0) {
                                            addMessageToChat('system', '⚠️ Warning: Please select cells to generate a question about their content');
                                            return;
                                        }
                                        for (let i = 0; i < cells.length; i++) {
                                            const cell = cells.get(i);
                                            const cellContent = cell.sharedModel.getSource();
                                            notebookContent.push({
                                                index: i + 1,
                                                content: cellContent
                                            });
                                            if (cell.type === 'code') {
                                                const loadsData = dataLoadingPattern.test(cellContent);
                                                let dataframeVar = null; // DataFrame variable name
                                                if (loadsData) {
                                                    dataLoadingCells.push(i + 1);
                                                    const dataLoadingPattern = /(\b\w+)\s*=\s*(?:pd\.read_\w+\(|sns\.load_dataset\(|pd\.DataFrame\()/;
                                                    const assignmentMatch = cellContent.match(dataLoadingPattern);
                                                    if (assignmentMatch) {
                                                        dataframeVar = assignmentMatch[1]; // Extract variable name
                                                    }
                                                }
                                                console.log('DataFrame detected: ' + dataframeVar);
                                                notebookCodeCells.push({
                                                    index: i + 1,
                                                    content: cellContent,
                                                    isDataLoading: loadsData,
                                                    dataframeVar: dataframeVar
                                                });
                                            }
                                        }
                                    }
                                    // For URL mode, we don't need cell content <-- Ylesia: actually we do
                                    console.log(isUrlMode ? 'URL mode - processing all cells' : 'Selected cells content:', selectedCells);
                                    // Prepare the request body with follow-up information if needed
                                    let relevantContent;
                                    if (!isUrlMode) {
                                        // Get only selected cells
                                        // relevantContent = selectedCells.map((cell, index) => ({
                                        //     index: index + 1,
                                        //     content: cell.model.sharedModel.getSource()
                                        // send up to past 5 ' #', or headers of notebook content for the topic range from the active cell index
                                        const activeIndex = (_d = (_c = notebookTracker.currentWidget) === null || _c === void 0 ? void 0 : _c.content.activeCellIndex) !== null && _d !== void 0 ? _d : 0;
                                        const cells = notebookModel.cells;
                                        const relevantCells = [];
                                        let headerCount = 0;
                                        for (let i = activeIndex; i >= 0; i--) {
                                            const cell = cells.get(i);
                                            if (cell.type === 'markdown' && cell.sharedModel.getSource().startsWith('#')) {
                                                headerCount++;
                                            }
                                            if (headerCount >= 5) {
                                                break;
                                            }
                                            relevantCells.unshift({
                                                index: i + 1,
                                                content: cell.sharedModel.getSource()
                                            });
                                        }
                                        relevantContent = relevantCells;
                                        console.log("Relevant Content: " + JSON.stringify(relevantContent));
                                    }
                                    const requestBody = {
                                        message: message,
                                        notebookContent: relevantContent || notebookContent,
                                        promptType: isUrlMode ? 'summary' : 'question',
                                        selectedCell: !isUrlMode ? selectedCells[selectedCells.length - 1].sharedModel.getSource() : null,
                                        questionType: !isUrlMode ? 'coding' : null,
                                        activeCellIndex: (_f = (_e = notebookTracker.currentWidget) === null || _e === void 0 ? void 0 : _e.content.activeCellIndex) !== null && _f !== void 0 ? _f : 0,
                                        isFollowup: isFollowupMode,
                                        previousQuestion: previousQuestion,
                                        notebookStructure: notebookStructure,
                                        notebookName: notebookName,
                                        ...(isUrlMode ? {} : {
                                            notebookDirectory,
                                            notebookCodeCells
                                        })
                                    };
                                    console.log("Request body:", requestBody);
                                    // for debugging follow up question logging
                                    if (isFollowupMode) {
                                        console.log('Before sending followed up logging request...');
                                        console.log('currentRowId: ' + currentRowId);
                                        console.log('userDecision: ' + userDecision);
                                    }
                                    // log user decision if is a follow up
                                    if (isFollowupMode && currentRowId !== null && userDecision === null) {
                                        await (0,_handler_js__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('log-usage', {
                                            method: 'POST',
                                            body: JSON.stringify({ row_id: currentRowId, user_decision: 'followed_up' })
                                        });
                                    }
                                    // Making POST request to message endpoint
                                    const response = await (0,_handler_js__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('message', {
                                        method: 'POST',
                                        body: JSON.stringify(requestBody)
                                    });
                                    console.log("Working up to here");
                                    // console.log(response.reply)
                                    console.log(response);
                                    // record row_id
                                    currentRowId = response.row_id;
                                    // reset user decision
                                    userDecision = null;
                                    // Process response and update UI
                                    const croppedString = response.reply.substring(7, response.reply.length - 4);
                                    let llmOutput;
                                    try {
                                        console.log("Cropped string: " + croppedString);
                                        llmOutput = JSON.parse(croppedString);
                                    }
                                    catch (error) {
                                        console.error('Error parsing JSON:', error);
                                        addMessageToChat('system', 'Error: Failed to parse server response');
                                        hideLoadingIndicator();
                                        return;
                                    }
                                    let returnedIndex;
                                    if (isFollowupMode) {
                                        returnedIndex = (_g = notebookTracker.currentWidget) === null || _g === void 0 ? void 0 : _g.content.activeCellIndex;
                                    }
                                    else {
                                        returnedIndex = ((_h = notebookTracker.currentWidget) === null || _h === void 0 ? void 0 : _h.content.activeCellIndex) + 1;
                                    }
                                    const summary = llmOutput.summary;
                                    // Hide loading indicator before showing response
                                    hideLoadingIndicator();
                                    // Show response
                                    const safeIndex = returnedIndex;
                                    addMessageToChat('assistant', 'Location: ' + safeIndex + '\n\nSummary: ' + summary);
                                    console.log(`Inserting new cell at index ${safeIndex} with summary:`, summary);
                                    const pageTitle = llmOutput.title || inputBox.value; // Use title if available, otherwise fallback to URL
                                    // If in follow-up mode, remove the previous cell before inserting the new one
                                    if (isFollowupMode && lastInsertedCellIndex >= 0 && notebookModel) {
                                        console.log(`Removing previous cell at index ${lastInsertedCellIndex}`);
                                        // Remove the previous cell
                                        notebookModel.sharedModel.deleteCell(lastInsertedCellIndex);
                                        console.log(`Deleted previous cell at index ${lastInsertedCellIndex}`);
                                        // Remove existing buttons from chat area
                                        removeChatButtons();
                                    }
                                    // Insert the new cell
                                    notebookModel.sharedModel.insertCell(safeIndex, {
                                        cell_type: 'markdown',
                                        source: formatQuestionCell(pageTitle, summary),
                                        metadata: {
                                            temporary: true,
                                        }
                                    });
                                    // Update tracking variables for potential follow-up
                                    lastInsertedCellIndex = safeIndex;
                                    previousQuestion = summary;
                                    isFollowupMode = true; // Enable follow-up mode after generating content
                                    if (notebookTracker.currentWidget && notebookTracker.currentWidget.content) {
                                        notebookTracker.currentWidget.content.activeCellIndex = safeIndex;
                                    }
                                    attachButtonsBelowChat(safeIndex, notebookModel);
                                    setTimeout(() => attachButtonListeners(safeIndex, notebookModel), 100);
                                }
                                catch (error) {
                                    // Hide loading indicator on error
                                    hideLoadingIndicator();
                                    console.error('Failed to get response:', error);
                                    addMessageToChat('system', 'Error: Failed to get response');
                                    isFollowupMode = false; // Reset follow-up mode on error
                                }
                            }
                        }
                    }
                    catch (error) {
                        // Hide loading indicator on error
                        hideLoadingIndicator();
                        console.error('Error in handleMessage:', error);
                        addMessageToChat('system', 'Error: Failed to process request');
                        isFollowupMode = false; // Reset follow-up mode on error
                    }
                }
            };
            // Add event listeners
            // sendButton.addEventListener('click', handleMessage);
            inputBox.addEventListener('keypress', (event) => {
                if (event.key === 'Enter' && !event.shiftKey) { // Allow Shift+Enter for new lines
                    event.preventDefault(); // Prevent default to avoid new line
                    if (isUrlMode) {
                        // URL mode validation
                        if (inputBox.value.trim()) {
                            console.log('Valid URL:', inputBox.value);
                            handleMessage();
                        }
                        else {
                            addMessageToChat('system', 'Error: Please input a valid link to get response');
                        }
                    }
                    else {
                        // Question mode - no URL validation needed
                        if (inputBox.value.trim()) {
                            handleMessage();
                        }
                        else {
                            addMessageToChat('system', 'Error: Please enter a question');
                        }
                    }
                }
            });
            // Function to add messages to chat with better code formatting
            const addMessageToChat = (role, text) => {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('chat-message', role);
                // For assistant messages, format code blocks
                if (role === 'assistant') {
                    // Simple regex to identify Python code blocks
                    const formattedText = text.replace(/```python\s*([\s\S]*?)```/g, '<pre class="python-code"><code>$1</code></pre>');
                    messageDiv.innerHTML = formattedText.replace(/\n/g, "<br>");
                }
                else {
                    messageDiv.innerHTML = text.replace(/\n/g, "<br>");
                }
                // Add to messages container
                messagesContainer.appendChild(messageDiv);
                // Scroll to bottom of messages container
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            };
            // Add a loading indicator function
            const showLoadingIndicator = () => {
                const loadingDiv = document.createElement('div');
                loadingDiv.classList.add('chat-message', 'system', 'loading-indicator');
                loadingDiv.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div> Generating response...';
                loadingDiv.id = 'loading-indicator';
                messagesContainer.appendChild(loadingDiv);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            };
            // Remove loading indicator
            const hideLoadingIndicator = () => {
                const loadingIndicator = document.getElementById('loading-indicator');
                if (loadingIndicator) {
                    loadingIndicator.remove();
                }
            };
            // Update notebook name
            const updateNotebookName = () => {
                // Get current notebook
                const currentNotebook = notebookTracker.currentWidget;
                if (currentNotebook instanceof _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__.NotebookPanel) {
                    const name = currentNotebook.title.label;
                    notebookName = name;
                    // Get notebook name
                    notebookNameDiv.textContent = `Notebook: ${notebookName}`;
                }
                else {
                    notebookNameDiv.textContent = 'No notebook detected...';
                }
            };
            const updateNotebookDirectory = async () => {
                const currentNotebook = notebookTracker.currentWidget;
                if (currentNotebook && currentNotebook.context) {
                    const notebookPath = currentNotebook.context.path;
                    // console.log("notebookPath: " + notebookPath);
                    // notebookDirectory = notebookPath.substring(0, notebookPath.lastIndexOf('/'));
                    const lastSlashIndex = notebookPath.lastIndexOf('/');
                    // If '/' is found, extract the directory path; otherwise, default to "."
                    notebookDirectory = lastSlashIndex !== -1
                        ? notebookPath.substring(0, lastSlashIndex)
                        : "."; // Current directory if no `/` is found
                    console.log("Notebook Directory updated:", notebookDirectory);
                    notebookStructure = await sendNotebookContent(notebookTracker);
                }
            };
            function clearChatHistory() {
                const messagesContainer = document.querySelector('.messages-container');
                if (messagesContainer) {
                    messagesContainer.innerHTML = '';
                }
            }
            // Listen for changes in the active notebook
            notebookTracker.currentChanged.connect(() => {
                updateNotebookName();
                updateNotebookDirectory();
                clearChatHistory();
                removeChatButtons();
            });
            //if index is changed, update the index
            notebookTracker.activeCellChanged.connect(() => {
                var _a, _b;
                const activeIndex = (_b = (_a = notebookTracker.currentWidget) === null || _a === void 0 ? void 0 : _a.content.activeCellIndex) !== null && _b !== void 0 ? _b : 0;
                notebookIndexDiv.textContent = `Notebook Index: ${activeIndex}`;
            });
            // Initial update
            updateNotebookName();
            updateNotebookDirectory;
            const widget = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.MainAreaWidget({ content });
            widget.id = 'chatbot-widget';
            widget.title.label = 'ContentGen';
            widget.title.closable = true;
            // Add widget to the right panel
            app.shell.add(widget, 'right');
            if (restorer) {
                restorer.add(widget, 'chatbot-widget');
            }
            return widget;
        };
        const createApiKeyWidget = async () => {
            const content = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_2__.Widget();
            content.node.classList.add('api-key-panel');
            // Create Header Section
            const headerContainer = document.createElement('div');
            headerContainer.classList.add('api-key-header-container');
            // Create container
            const mainContainer = document.createElement('div');
            mainContainer.classList.add('api-key-container');
            // Create header
            const header = document.createElement('div');
            header.classList.add('api-key-header');
            header.textContent = 'Gemini API Key Required';
            // Create description
            const description = document.createElement('div');
            description.classList.add('api-key-description');
            description.textContent = 'Please enter your Gemini API key to use the ContentGen features.';
            // Create input container
            const inputContainer = document.createElement('div');
            inputContainer.classList.add('api-key-input-container');
            // Create input field
            const inputField = document.createElement('input');
            inputField.type = 'password';
            inputField.classList.add('api-key-input');
            inputField.placeholder = 'Enter your Gemini API key...';
            // Create submit button
            const submitButton = document.createElement('button');
            submitButton.textContent = 'Save API Key';
            submitButton.classList.add('api-key-submit');
            // Create error message container
            const errorMessage = document.createElement('div');
            errorMessage.textContent = 'Please enter a valid API key.';
            errorMessage.classList.add('api-key-error');
            errorMessage.style.visibility = 'hidden';
            // Add sign-up message and link
            const signupMessage = document.createElement('div');
            signupMessage.classList.add('api-key-signup');
            signupMessage.innerHTML = 'Need a Gemini API key? <a href="https://aistudio.google.com/app/apikey" target="_blank">Visit Google AI Studio</a>';
            const handleApiKeySubmit = async () => {
                const apiKey = inputField.value.trim();
                // Basic format validation before contacting the backend
                const apiKeyFormatIsValid = /^AIza[a-zA-Z0-9_-]{35}$/.test(apiKey);
                console.log("apiKeyFormatIsValid: " + apiKeyFormatIsValid);
                if (!apiKeyFormatIsValid) {
                    console.log("Invalid API key format.");
                    errorMessage.textContent = 'Invalid API key format. Please check and try again.';
                    errorMessage.style.visibility = 'visible';
                    return; // Prevent backend request if format is obviously invalid
                }
                try {
                    const response = await (0,_handler_js__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('save-api-key', {
                        method: 'POST',
                        body: JSON.stringify({ api_key: apiKey })
                    });
                    if (response.valid) {
                        window.location.reload();
                    }
                    else {
                        console.log("Backend validation failed. API key is invalid.");
                        errorMessage.textContent = 'Invalid API key. Please check and try again.';
                        errorMessage.style.visibility = 'visible';
                    }
                }
                catch (error) {
                    console.log("Error during API call: ", error);
                    errorMessage.textContent = 'Failed to save API key. Please try again.';
                    errorMessage.style.visibility = 'visible';
                }
            };
            // Handle button click
            submitButton.onclick = handleApiKeySubmit;
            // Handle Enter key press in the input field
            inputField.addEventListener('keydown', (event) => {
                if (event.key === 'Enter') {
                    handleApiKeySubmit();
                }
            });
            // Add elements to containers
            headerContainer.appendChild(header);
            headerContainer.appendChild(description);
            inputContainer.appendChild(inputField);
            inputContainer.appendChild(submitButton);
            mainContainer.appendChild(inputContainer);
            mainContainer.appendChild(errorMessage);
            mainContainer.appendChild(signupMessage);
            // Add to content
            content.node.appendChild(headerContainer);
            content.node.appendChild(mainContainer);
            const widget = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.MainAreaWidget({ content });
            widget.id = 'api-key-widget';
            widget.title.label = 'ContentGen';
            widget.title.closable = true;
            // Add widget to the right panel
            app.shell.add(widget, 'right');
            // Add to restorer
            if (restorer) {
                restorer.add(widget, 'api-key-widget');
            }
            return widget;
        };
        const hasApiKey = await checkGeminiApiKey();
        console.log("Has API key:", hasApiKey);
        if (!hasApiKey) {
            createApiKeyWidget();
        }
        else {
            newWidget();
        }
    }
};
// Add these helper functions
const removeChatButtons = () => {
    const panel = document.getElementById("chat-buttons-container");
    if (panel) {
        panel.innerHTML = ""; // Clear the buttons from the UI
    }
};
const attachButtonsBelowChat = (index, notebookModel) => {
    console.log(`Adding buttons below chat for cell at index ${index}`);
    // Ensure the chat buttons container exists
    let panel = document.getElementById("chat-buttons-container");
    if (!panel) {
        console.error("Chat buttons container not found!");
        return;
    }
    // Create Apply button
    const applyBtn = document.createElement("button");
    applyBtn.textContent = "✅ Apply";
    applyBtn.className = "apply-btn";
    applyBtn.onclick = () => applyChanges(index, notebookModel);
    // Create Cancel button
    const cancelBtn = document.createElement("button");
    cancelBtn.textContent = "❌ Cancel";
    cancelBtn.className = "cancel-btn";
    cancelBtn.onclick = () => cancelChanges(index, notebookModel);
    // Add buttons to the panel
    panel.appendChild(applyBtn);
    panel.appendChild(cancelBtn);
};
const attachButtonListeners = (index, notebookModel) => {
    // Implementation details
};
const applyChanges = async (index, notebookModel) => {
    console.log(`Applying changes for cell at index ${index}`);
    // Remove temporary metadata
    if (notebookModel.sharedModel.cells[index]) {
        delete notebookModel.sharedModel.cells[index].metadata.temporary;
    }
    // Reset follow-up mode
    isFollowupMode = false;
    previousQuestion = "";
    lastInsertedCellIndex = -1;
    // Remove the buttons from the chat area
    removeChatButtons();
    // log user decision
    userDecision = 'applied';
    await (0,_handler_js__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('log-usage', {
        method: 'POST',
        body: JSON.stringify({ row_id: currentRowId, user_decision: 'applied' })
    });
};
const cancelChanges = async (index, notebookModel) => {
    console.log(`Cancelling changes and deleting cell at index ${index}`);
    // Remove the inserted summary cell
    notebookModel.sharedModel.deleteCell(index);
    // Reset follow-up mode
    isFollowupMode = false;
    previousQuestion = "";
    lastInsertedCellIndex = -1;
    // Remove the buttons from the chat area
    removeChatButtons();
    // log user decision
    userDecision = 'canceled';
    await (0,_handler_js__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('log-usage', {
        method: 'POST',
        body: JSON.stringify({ row_id: currentRowId, user_decision: 'canceled' })
    });
};
// Update the helper function to format the cell content
const formatQuestionCell = (title, content) => {
    // Split the content into question and answer parts
    const parts = content.split(/Answer:\s*```python/);
    if (parts.length < 2) {
        // If we can't split properly, return the original content
        return `### ${title}\n\n${content}`;
    }
    // Extract question and answer
    let question = parts[0].replace('Question:', '').trim();
    let answer = '```python' + parts[1];
    // Format with orange alert for question and collapsible section for answer
    return `<div class="alert alert-warning">
  <h3>Question 🤔 ${title}</h3>
  
  ${question}
</div>

<details>
  <summary><strong>Click to reveal answer</strong></summary>
  
${answer}
</details>`;
};
const sendNotebookContent = async (notebookTracker) => {
    var _a;
    console.log("Inside sendNoteboookContent function!");
    try {
        // Get current notebook
        const currentNotebook = notebookTracker.currentWidget;
        if (!currentNotebook) {
            console.error('No active notebook detected');
            return;
        }
        await currentNotebook.context.ready;
        const notebookModel = (_a = currentNotebook.content) === null || _a === void 0 ? void 0 : _a.model;
        if (!notebookModel) {
            console.error('No active notebook model detected');
            return;
        }
        const cells = notebookModel.cells;
        const notebookContent = [];
        for (let i = 0; i < cells.length; i++) {
            const cell = cells.get(i);
            notebookContent.push({
                index: i + 1,
                content: cell.sharedModel.getSource()
            });
        }
        console.log(notebookContent);
        if (notebookContent.length <= 2) {
            return null;
        }
        const requestBody = {
            notebookContent: notebookContent
        };
        console.log("requestBody for notebook processing:", requestBody);
        const response = await (0,_handler_js__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('process_notebook', {
            method: 'POST',
            body: JSON.stringify(requestBody)
        });
        console.log("Notebook content processed:", response);
        return response;
    }
    catch (error) {
        console.error('Failed to send notebook content:', error);
    }
};
// Function to check if Gemini API key exists
async function checkGeminiApiKey() {
    try {
        console.log("Checking Gemini API key...");
        const response = await (0,_handler_js__WEBPACK_IMPORTED_MODULE_5__.requestAPI)('check-api-key');
        console.log("Response from check-api-key:", response);
        return response.hasKey;
    }
    catch (error) {
        console.error('Error checking Gemini API key:', error);
        return false;
    }
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./style/index.css":
/*!***************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/index.css ***!
  \***************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! -!../node_modules/css-loader/dist/cjs.js!./base.css */ "./node_modules/css-loader/dist/cjs.js!./style/base.css");
// Imports



var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
___CSS_LOADER_EXPORT___.i(_node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_2__["default"]);
// Module
___CSS_LOADER_EXPORT___.push([module.id, `/* Base container styles */
.chatbot-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #ffffff;
  position: relative;
  font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;
  padding: 0 16px;
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  color: #1f1f1f;
  font-size: 14px;
}

/* Messages area */
.messages-container {
  position: absolute;
  top: 16px;
  left: 0;
  right: 0;
  bottom: 210px;
  overflow-y: scroll;
  padding: 20px;
  z-index: 95;
}

/* Message bubbles */
.chat-message {
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
  line-height: 1.5;
  max-width: 85%;
  margin: 8px 0;
}

.chat-message.user {
  background: #e8f0fe;
  margin-left: auto;
  border-bottom-right-radius: 4px;
}

.chat-message.assistant {
  background: #f8f9fa;
  border-bottom-left-radius: 4px;
}

.chat-message.system {
  background: #f1f3f4;
  color: #5f6368;
  font-style: italic;
  text-align: center;
  max-width: 100%;
}

/* Code block styling in chat messages */
.chat-message pre {
  background-color: #f5f5f5;
  border-radius: 4px;
  padding: 10px;
  margin: 8px 0;
  overflow-x: auto;
  border-left: 3px solid #3498db;
}

.chat-message code {
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}

/* Python code specific styling */
.chat-message pre.python-code {
  background-color: #f5f5f5;
  border-radius: 4px;
  padding: 10px;
  margin: 8px 0;
  overflow-x: auto;
  border-left: 3px solid #4b8bf4;
  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;
  font-size: 0.9em;
}

/* Question styling */
.chat-message .question-text {
  font-weight: 500;
  margin-bottom: 10px;
}

/* Answer label styling */
.chat-message .answer-label {
  font-weight: 600;
  color: #2c3e50;
  margin-top: 15px;
  margin-bottom: 5px;
}

/* Input area */
.input-container {
  position: absolute;
  bottom: 50px;
  left: 16px;
  right: 16px;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  background: #ffffff;
  border: 1px solid rgba(0, 0, 0, 0.08);
  border-radius: 12px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  z-index: 98;
}

.chat-input {
  flex: 1;
  font-family: inherit;
  font-size: 13px;
  padding: 12px 16px;
  border: none;
  background: transparent;
  resize: none;
  min-height: 24px;
  max-height: 120px;
  border-radius: 8px;
}

.chat-input:focus {
  outline: none;
}

/* Placeholder text size */
.chat-input::placeholder {
  font-size: 13px;
  color: #5f6368;
}

/* Buttons */
.mode-toggle {
  width: 40px;
  height: 40px;
  padding: 0;
  font-size: 18px;
  border-radius: 50%;
  border: 1px solid #dadce0;
  background: transparent;
  color: #1a73e8;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

#chat-buttons-container {
  position: absolute;
  bottom: 130px;
  right: 24px;
  display: flex;
  gap: 12px;
  padding: 8px 16px;
  z-index: 99;
  background: #ffffff;
}

.apply-btn,
.cancel-btn {
  font-family: inherit;
  font-size: 14px;
  font-weight: 500;
  padding: 0 24px;
  height: 36px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.apply-btn {
  background: #1a73e8;
  color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);
}

.cancel-btn {
  background: #fff;
  color: #1a73e8;
  border: 1px solid rgba(26, 115, 232, 0.5);
}

/* Header */
.chat-header {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  background: #ffffff;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  height: 36px;
  z-index: 97;
}

.notebook-name-display {
  color: #5f6368;
  font-size: 13px;
  font-weight: 500;
  padding: 8px 0;
}

.model-info {
  color: #1a73e8;
  font-size: 13px;
  font-weight: 500;
  padding: 4px 12px;
  background: rgba(26, 115, 232, 0.08);
  border-radius: 8px;
}

/* Hover states */
.mode-toggle:hover { background: rgba(26, 115, 232, 0.08); }
.apply-btn:hover { background: #1557b0; }
.cancel-btn:hover { background: rgba(26, 115, 232, 0.04); }

/* Loading indicator */
.loading-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.typing-indicator {
  display: flex;
  align-items: center;
}

.typing-indicator span {
  height: 8px;
  width: 8px;
  background: #3498db;
  border-radius: 50%;
  display: inline-block;
  margin: 0 2px;
  animation: bounce 1.5s infinite ease-in-out;
}

.typing-indicator span:nth-child(1) {
  animation-delay: 0s;
}

.typing-indicator span:nth-child(2) {
  animation-delay: 0.2s;
}

.typing-indicator span:nth-child(3) {
  animation-delay: 0.4s;
}

@keyframes bounce {
  0%, 60%, 100% {
    transform: translateY(0);
  }
  30% {
    transform: translateY(-5px);
  }
}

/* Alert styling */
.alert {
  padding: 15px;
  margin-bottom: 20px;
  border: 1px solid transparent;
  border-radius: 4px;
}

.alert-warning {
  color: #8a6d3b;
  background-color: #fcf8e3;
  border-color: #faebcc;
}

/* Question title styling */
.alert h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #8a6d3b;
}

/* Details/Summary styling */
details {
  margin: 15px 0;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

details summary {
  cursor: pointer;
  padding: 5px;
  color: #1a73e8;
}

details summary:hover {
  color: #1557b0;
}

/* Add your styles here */

`, "",{"version":3,"sources":["webpack://./style/index.css"],"names":[],"mappings":"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","sourcesContent":["@import url('base.css');\n\n/* Base container styles */\n.chatbot-panel {\n  display: flex;\n  flex-direction: column;\n  height: 100%;\n  background: #ffffff;\n  position: relative;\n  font-family: 'Google Sans', -apple-system, BlinkMacSystemFont, sans-serif;\n  padding: 0 16px;\n}\n\n.chat-container {\n  display: flex;\n  flex-direction: column;\n  height: 100%;\n  color: #1f1f1f;\n  font-size: 14px;\n}\n\n/* Messages area */\n.messages-container {\n  position: absolute;\n  top: 16px;\n  left: 0;\n  right: 0;\n  bottom: 210px;\n  overflow-y: scroll;\n  padding: 20px;\n  z-index: 95;\n}\n\n/* Message bubbles */\n.chat-message {\n  padding: 12px 16px;\n  border-radius: 8px;\n  font-size: 13px;\n  line-height: 1.5;\n  max-width: 85%;\n  margin: 8px 0;\n}\n\n.chat-message.user {\n  background: #e8f0fe;\n  margin-left: auto;\n  border-bottom-right-radius: 4px;\n}\n\n.chat-message.assistant {\n  background: #f8f9fa;\n  border-bottom-left-radius: 4px;\n}\n\n.chat-message.system {\n  background: #f1f3f4;\n  color: #5f6368;\n  font-style: italic;\n  text-align: center;\n  max-width: 100%;\n}\n\n/* Code block styling in chat messages */\n.chat-message pre {\n  background-color: #f5f5f5;\n  border-radius: 4px;\n  padding: 10px;\n  margin: 8px 0;\n  overflow-x: auto;\n  border-left: 3px solid #3498db;\n}\n\n.chat-message code {\n  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;\n  font-size: 0.9em;\n}\n\n/* Python code specific styling */\n.chat-message pre.python-code {\n  background-color: #f5f5f5;\n  border-radius: 4px;\n  padding: 10px;\n  margin: 8px 0;\n  overflow-x: auto;\n  border-left: 3px solid #4b8bf4;\n  font-family: 'Menlo', 'Monaco', 'Courier New', monospace;\n  font-size: 0.9em;\n}\n\n/* Question styling */\n.chat-message .question-text {\n  font-weight: 500;\n  margin-bottom: 10px;\n}\n\n/* Answer label styling */\n.chat-message .answer-label {\n  font-weight: 600;\n  color: #2c3e50;\n  margin-top: 15px;\n  margin-bottom: 5px;\n}\n\n/* Input area */\n.input-container {\n  position: absolute;\n  bottom: 50px;\n  left: 16px;\n  right: 16px;\n  display: flex;\n  align-items: center;\n  gap: 12px;\n  padding: 8px;\n  background: #ffffff;\n  border: 1px solid rgba(0, 0, 0, 0.08);\n  border-radius: 12px;\n  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);\n  z-index: 98;\n}\n\n.chat-input {\n  flex: 1;\n  font-family: inherit;\n  font-size: 13px;\n  padding: 12px 16px;\n  border: none;\n  background: transparent;\n  resize: none;\n  min-height: 24px;\n  max-height: 120px;\n  border-radius: 8px;\n}\n\n.chat-input:focus {\n  outline: none;\n}\n\n/* Placeholder text size */\n.chat-input::placeholder {\n  font-size: 13px;\n  color: #5f6368;\n}\n\n/* Buttons */\n.mode-toggle {\n  width: 40px;\n  height: 40px;\n  padding: 0;\n  font-size: 18px;\n  border-radius: 50%;\n  border: 1px solid #dadce0;\n  background: transparent;\n  color: #1a73e8;\n  display: flex;\n  align-items: center;\n  justify-content: center;\n  line-height: 1;\n}\n\n#chat-buttons-container {\n  position: absolute;\n  bottom: 130px;\n  right: 24px;\n  display: flex;\n  gap: 12px;\n  padding: 8px 16px;\n  z-index: 99;\n  background: #ffffff;\n}\n\n.apply-btn,\n.cancel-btn {\n  font-family: inherit;\n  font-size: 14px;\n  font-weight: 500;\n  padding: 0 24px;\n  height: 36px;\n  border-radius: 8px;\n  border: none;\n  cursor: pointer;\n  display: inline-flex;\n  align-items: center;\n  justify-content: center;\n  transition: all 0.2s ease;\n}\n\n.apply-btn {\n  background: #1a73e8;\n  color: white;\n  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.12);\n}\n\n.cancel-btn {\n  background: #fff;\n  color: #1a73e8;\n  border: 1px solid rgba(26, 115, 232, 0.5);\n}\n\n/* Header */\n.chat-header {\n  position: absolute;\n  bottom: 0;\n  left: 0;\n  right: 0;\n  display: flex;\n  justify-content: space-between;\n  align-items: center;\n  padding: 16px 20px;\n  background: #ffffff;\n  border-top: 1px solid rgba(0, 0, 0, 0.06);\n  height: 36px;\n  z-index: 97;\n}\n\n.notebook-name-display {\n  color: #5f6368;\n  font-size: 13px;\n  font-weight: 500;\n  padding: 8px 0;\n}\n\n.model-info {\n  color: #1a73e8;\n  font-size: 13px;\n  font-weight: 500;\n  padding: 4px 12px;\n  background: rgba(26, 115, 232, 0.08);\n  border-radius: 8px;\n}\n\n/* Hover states */\n.mode-toggle:hover { background: rgba(26, 115, 232, 0.08); }\n.apply-btn:hover { background: #1557b0; }\n.cancel-btn:hover { background: rgba(26, 115, 232, 0.04); }\n\n/* Loading indicator */\n.loading-indicator {\n  display: flex;\n  align-items: center;\n  justify-content: center;\n  gap: 10px;\n}\n\n.typing-indicator {\n  display: flex;\n  align-items: center;\n}\n\n.typing-indicator span {\n  height: 8px;\n  width: 8px;\n  background: #3498db;\n  border-radius: 50%;\n  display: inline-block;\n  margin: 0 2px;\n  animation: bounce 1.5s infinite ease-in-out;\n}\n\n.typing-indicator span:nth-child(1) {\n  animation-delay: 0s;\n}\n\n.typing-indicator span:nth-child(2) {\n  animation-delay: 0.2s;\n}\n\n.typing-indicator span:nth-child(3) {\n  animation-delay: 0.4s;\n}\n\n@keyframes bounce {\n  0%, 60%, 100% {\n    transform: translateY(0);\n  }\n  30% {\n    transform: translateY(-5px);\n  }\n}\n\n/* Alert styling */\n.alert {\n  padding: 15px;\n  margin-bottom: 20px;\n  border: 1px solid transparent;\n  border-radius: 4px;\n}\n\n.alert-warning {\n  color: #8a6d3b;\n  background-color: #fcf8e3;\n  border-color: #faebcc;\n}\n\n/* Question title styling */\n.alert h3 {\n  margin-top: 0;\n  margin-bottom: 15px;\n  color: #8a6d3b;\n}\n\n/* Details/Summary styling */\ndetails {\n  margin: 15px 0;\n  padding: 10px;\n  background-color: #f8f9fa;\n  border-radius: 4px;\n}\n\ndetails summary {\n  cursor: pointer;\n  padding: 5px;\n  color: #1a73e8;\n}\n\ndetails summary:hover {\n  color: #1557b0;\n}\n\n/* Add your styles here */\n\n"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./style/index.css":
/*!*************************!*\
  !*** ./style/index.css ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js */ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/styleDomAPI.js */ "./node_modules/style-loader/dist/runtime/styleDomAPI.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/insertBySelector.js */ "./node_modules/style-loader/dist/runtime/insertBySelector.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/setAttributesWithoutAttributes.js */ "./node_modules/style-loader/dist/runtime/setAttributesWithoutAttributes.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/insertStyleElement.js */ "./node_modules/style-loader/dist/runtime/insertStyleElement.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/styleTagTransform.js */ "./node_modules/style-loader/dist/runtime/styleTagTransform.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! !!../node_modules/css-loader/dist/cjs.js!./index.css */ "./node_modules/css-loader/dist/cjs.js!./style/index.css");

      
      
      
      
      
      
      
      
      

var options = {};

options.styleTagTransform = (_node_modules_style_loader_dist_runtime_styleTagTransform_js__WEBPACK_IMPORTED_MODULE_5___default());
options.setAttributes = (_node_modules_style_loader_dist_runtime_setAttributesWithoutAttributes_js__WEBPACK_IMPORTED_MODULE_3___default());

      options.insert = _node_modules_style_loader_dist_runtime_insertBySelector_js__WEBPACK_IMPORTED_MODULE_2___default().bind(null, "head");
    
options.domAPI = (_node_modules_style_loader_dist_runtime_styleDomAPI_js__WEBPACK_IMPORTED_MODULE_1___default());
options.insertStyleElement = (_node_modules_style_loader_dist_runtime_insertStyleElement_js__WEBPACK_IMPORTED_MODULE_4___default());

var update = _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default()(_node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_6__["default"], options);




       /* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_6__["default"] && _node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_6__["default"].locals ? _node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_6__["default"].locals : undefined);


/***/ })

}]);
//# sourceMappingURL=lib_index_js.d82a249922beaf021816.js.map