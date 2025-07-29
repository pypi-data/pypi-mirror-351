import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin,
  ILayoutRestorer
} from '@jupyterlab/application';

import { MainAreaWidget } from '@jupyterlab/apputils';
import { Widget } from '@lumino/widgets';
import { INotebookTracker } from '@jupyterlab/notebook';
import { requestAPI } from './handler.js';
import '../style/index.css';
import { NotebookPanel } from '@jupyterlab/notebook';

// Add these at the top level, before the plugin definition
let isFollowupMode = false;
let previousQuestion = "";
let lastInsertedCellIndex = -1;
let notebookDirectory: string = ''; // current notebook directory
let notebookName: string = ''; // current notebook name
let currentRowId: number | null = null;
let userDecision: 'applied' | 'canceled' | 'followed_up' | null = null;
let notebookStructure: any = null;

/**
 * Initialization data for the contentgen extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'contentgen:plugin',
  description: 'An instructor-assistant JupyterLab extension for generating in-context lecture questions and supplementary teaching materials.',
  autoStart: true,
  requires: [INotebookTracker],
  optional: [ILayoutRestorer],
  activate: async (app: JupyterFrontEnd, notebookTracker: INotebookTracker, restorer: ILayoutRestorer | null) => {
    console.log('JupyterLab extension contentgen is activated!');

    const newWidget = async () => {
      const content = new Widget();
      
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
      
      if ( notebookStructure === null) {
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
        } else {
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
            const notebookContent: { index: number; content: string }[] = [];

            updateNotebookDirectory();
            
            const notebookCodeCells: {
              index: number;          // Cell index in the notebook
              content: string;        // Raw code content of the cell
              isDataLoading: boolean; // Whether this cell loads a dataset
              dataframeVar: string | null; // Variable name of the loaded DataFrame (if any)
            }[] = [];
          
            const dataLoadingPattern = /(pd\.read_(csv|excel|json|html)\(|sns\.load_dataset\(|pd\.DataFrame\(|pd\.DataFrame\.from_dict\(|pd\.DataFrame\.from_records\()/; // Regular expression pattern to detect DataFrame creation
            const dataLoadingCells: number[] = []; // List to store indices of dataset-loading cells
            if (currentNotebook && currentNotebook.content) {
              const notebook = currentNotebook.content;
              const notebookModel = notebook?.model;

              if (notebookModel) {
                try {
                  const cells = notebookModel.cells;
                  const notebookWidget = currentNotebook.content; // Get notebook widget properly
                  if (!notebookWidget) {
                    addMessageToChat('system', 'Error: No active notebook');
                    return;
                  }

                  // Get selected cells using notebook's active cell index
                  const activeIndex = notebookTracker.currentWidget?.content.activeCellIndex ?? 0;
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
                  } else {
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

                        let dataframeVar: string | null = null; // DataFrame variable name
                        if (loadsData) { 

                          dataLoadingCells.push(i + 1);

                          const dataLoadingPattern = /(\b\w+)\s*=\s*(?:pd\.read_\w+\(|sns\.load_dataset\(|pd\.DataFrame\()/;
                          const assignmentMatch = cellContent.match(dataLoadingPattern);

                          if (assignmentMatch) {
                              dataframeVar = assignmentMatch[1];  // Extract variable name
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
                          const activeIndex = notebookTracker.currentWidget?.content.activeCellIndex ?? 0;
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
                    activeCellIndex: notebookTracker.currentWidget?.content.activeCellIndex ?? 0,
                    isFollowup: isFollowupMode,
                    previousQuestion: previousQuestion,
                    notebookStructure:  notebookStructure,
                    notebookName: notebookName,
                    ...(isUrlMode ? {} : { 
                      notebookDirectory,
                      notebookCodeCells
                    })
                  };
                  console.log("Request body:", requestBody);
                  
                  // for debugging follow up question logging
                  if (isFollowupMode) {
                    console.log('Before sending followed up logging request...')
                    console.log('currentRowId: ' + currentRowId);
                    console.log('userDecision: ' + userDecision);
                  }

                  // log user decision if is a follow up
                  if (isFollowupMode && currentRowId !== null && userDecision === null) {
                    await requestAPI('log-usage', {
                      method: 'POST',
                      body: JSON.stringify({ row_id: currentRowId, user_decision: 'followed_up' })
                    });
                  }
                  

                  // Making POST request to message endpoint
                  const response = await requestAPI<any>('message', {
                    method: 'POST',
                    body: JSON.stringify(requestBody)
                  });

                  console.log("Working up to here");
                  // console.log(response.reply)
                  console.log(response)
                  
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
                  } catch (error) {
                    console.error('Error parsing JSON:', error);
                    addMessageToChat('system', 'Error: Failed to parse server response');
                    hideLoadingIndicator();
                    return;
                  }
                  let returnedIndex;
                  if (isFollowupMode){
                    returnedIndex = notebookTracker.currentWidget?.content.activeCellIndex;
                  }
                  else{
                    returnedIndex = notebookTracker.currentWidget?.content.activeCellIndex + 1;
                  }
                  const summary = llmOutput.summary;

                  // Hide loading indicator before showing response
                  hideLoadingIndicator();
                  
                  // Show response
                  const safeIndex = returnedIndex;
                  addMessageToChat('assistant', 'Location: ' + safeIndex + '\n\nSummary: ' + summary);
                  
                  console.log(`Inserting new cell at index ${safeIndex} with summary:`, summary);

                  const pageTitle = llmOutput.title || inputBox.value;  // Use title if available, otherwise fallback to URL

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
                } catch (error) {
                  // Hide loading indicator on error
                  hideLoadingIndicator();
                  console.error('Failed to get response:', error);
                  addMessageToChat('system', 'Error: Failed to get response');
                  isFollowupMode = false; // Reset follow-up mode on error
                }
              }
            }
          } catch (error) {
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
            } else {
              addMessageToChat('system', 'Error: Please input a valid link to get response');
            }
          } else {
            // Question mode - no URL validation needed
            if (inputBox.value.trim()) {
              handleMessage();
            } else {
              addMessageToChat('system', 'Error: Please enter a question');
            }
          }
        }
      });
    
      // Function to add messages to chat with better code formatting
      const addMessageToChat = (role: string, text: string) => {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('chat-message', role);
        
        // For assistant messages, format code blocks
        if (role === 'assistant') {
          // Simple regex to identify Python code blocks
          const formattedText = text.replace(
            /```python\s*([\s\S]*?)```/g,
            '<pre class="python-code"><code>$1</code></pre>'
          );
          messageDiv.innerHTML = formattedText.replace(/\n/g, "<br>");
        } else {
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

        if (currentNotebook instanceof NotebookPanel) {
          const name = currentNotebook.title.label;
          notebookName = name;

          // Get notebook name
          notebookNameDiv.textContent = `Notebook: ${notebookName}`;
          
        } else {
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
                : ".";  // Current directory if no `/` is found

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
        const activeIndex = notebookTracker.currentWidget?.content.activeCellIndex ?? 0;
        notebookIndexDiv.textContent = `Notebook Index: ${activeIndex}`;
      });

      // Initial update
      updateNotebookName();
      updateNotebookDirectory;

      const widget = new MainAreaWidget({ content });
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
      const content = new Widget();
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
            const response = await requestAPI('save-api-key', {
                method: 'POST',
                body: JSON.stringify({ api_key: apiKey })
            }) as { status: string; valid: boolean };
    
            if (response.valid) {
                window.location.reload();
            } else {
                console.log("Backend validation failed. API key is invalid.");
                errorMessage.textContent = 'Invalid API key. Please check and try again.';
                errorMessage.style.visibility = 'visible';
            }
        } catch (error: any) {
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
    
      const widget = new MainAreaWidget({ content });
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
    else{
      newWidget();
    }
  }
};

// Add these helper functions
const removeChatButtons = () => {
  const panel = document.getElementById("chat-buttons-container");
  if (panel) {
    panel.innerHTML = "";  // Clear the buttons from the UI
  }
};

const attachButtonsBelowChat = (index: number, notebookModel: any) => {
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

const attachButtonListeners = (index: number, notebookModel: any) => {
  // Implementation details
};

const applyChanges = async (index: number, notebookModel: any) => {
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
  await requestAPI('log-usage', {
    method: 'POST',
    body: JSON.stringify({ row_id: currentRowId, user_decision: 'applied' })
  });
};

const cancelChanges = async (index: number, notebookModel: any) => {
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
  await requestAPI('log-usage', {
    method: 'POST',
    body: JSON.stringify({ row_id: currentRowId, user_decision: 'canceled' })
  });
};

// Update the helper function to format the cell content
const formatQuestionCell = (title: string, content: string): string => {
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

const sendNotebookContent = async (notebookTracker: INotebookTracker) => {
  console.log("Inside sendNoteboookContent function!")
  try {
    // Get current notebook
    const currentNotebook = notebookTracker.currentWidget;
    
    if (!currentNotebook) {
      console.error('No active notebook detected');
      return;
    }
    
    await currentNotebook.context.ready;

    const notebookModel = currentNotebook.content?.model;
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
    const response = await requestAPI<any>('process_notebook', {
      method: 'POST',
      body: JSON.stringify(requestBody)
    });
    console.log("Notebook content processed:", response);
    return response;
  } catch (error) {
    console.error('Failed to send notebook content:', error);
  }
};

// Function to check if Gemini API key exists
async function checkGeminiApiKey(): Promise<boolean> {
  try {
    console.log("Checking Gemini API key...");
    const response = await requestAPI<any>('check-api-key');
    console.log("Response from check-api-key:", response);
    return response.hasKey;
  } catch (error) {
    console.error('Error checking Gemini API key:', error);
    return false;
  }
}

export default plugin;
