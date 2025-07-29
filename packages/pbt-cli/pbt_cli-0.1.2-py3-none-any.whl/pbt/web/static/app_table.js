// PBT Studio 2.0 - Table Layout JavaScript

// Global variables
let ws = null;
let currentComparison = null;
let apiEndpoint = '/api';

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    loadModels();
    loadSavedState();
    createFloatingParticles();
    initWebSocket();
    
    // Set up event listeners
    document.getElementById('prompt-input').addEventListener('input', () => {
        detectVariables();
        saveState();
    });
    
    document.getElementById('expected-output').addEventListener('input', saveState);
    document.getElementById('temperature').addEventListener('input', saveState);
    document.getElementById('max-tokens').addEventListener('input', saveState);
});

// Initialize app
function initializeApp() {
    // Check for saved theme
    const savedTheme = localStorage.getItem('pbt-theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        updateThemeToggle();
    }
}

// Load available models
async function loadModels() {
    try {
        const response = await fetch(`${apiEndpoint}/models`);
        const data = await response.json();
        
        const modelSelector = document.getElementById('model-selector');
        modelSelector.innerHTML = '';
        
        data.models.forEach(model => {
            const label = document.createElement('label');
            label.className = 'model-checkbox';
            label.innerHTML = `
                <input type="checkbox" value="${model.id}" 
                       ${['claude', 'gpt-4', 'gpt-3.5-turbo'].includes(model.id) ? 'checked' : ''}>
                <span>${model.name}</span>
            `;
            modelSelector.appendChild(label);
        });
    } catch (error) {
        console.error('Failed to load models:', error);
    }
}

// Compare models
async function compareModels() {
    // Get input values
    const prompt = document.getElementById('prompt-input').value;
    const expectedOutput = document.getElementById('expected-output').value;
    const temperature = parseFloat(document.getElementById('temperature').value);
    const maxTokens = parseInt(document.getElementById('max-tokens').value);
    
    // Get selected models
    const selectedModels = [];
    document.querySelectorAll('.model-checkbox input:checked').forEach(checkbox => {
        selectedModels.push(checkbox.value);
    });
    
    if (!prompt) {
        alert('Please enter a prompt');
        return;
    }
    
    if (selectedModels.length === 0) {
        alert('Please select at least one model');
        return;
    }
    
    // Get variables
    const variables = {};
    document.querySelectorAll('.variable-item').forEach(item => {
        const inputs = item.querySelectorAll('input[type="text"]');
        if (inputs[0].value && inputs[1].value) {
            variables[inputs[0].value] = inputs[1].value;
        }
    });
    
    // Show loading state
    showLoadingState(selectedModels);
    
    // Clear existing model columns
    const modelColumns = document.getElementById('model-columns');
    modelColumns.innerHTML = '';
    
    // Create columns for each model
    selectedModels.forEach(model => {
        createModelColumn(model);
    });
    
    try {
        // Use WebSocket for streaming if connected
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({
                prompt,
                models: selectedModels,
                variables,
                expected_output: expectedOutput,
                temperature,
                max_tokens: maxTokens
            }));
        } else {
            // Fallback to REST API
            const response = await fetch(`${apiEndpoint}/compare`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    prompt,
                    models: selectedModels,
                    variables,
                    expected_output: expectedOutput,
                    temperature,
                    max_tokens: maxTokens
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            displayResults(data);
        }
    } catch (error) {
        console.error('Comparison failed:', error);
        alert(`Failed to compare models: ${error.message}`);
        hideLoadingState();
    }
}

// Create model column
function createModelColumn(modelId) {
    const column = document.createElement('div');
    column.className = 'model-column';
    column.id = `model-column-${modelId}`;
    column.innerHTML = `
        <div class="model-header" id="model-header-${modelId}">
            <div class="model-name-section">
                <span class="model-name">${modelId}</span>
                <div class="score-container" id="score-${modelId}"></div>
            </div>
            <div class="model-stats" id="stats-${modelId}">
                <span class="stat-item"><i class="fas fa-spinner fa-spin"></i> Processing...</span>
            </div>
        </div>
        <div class="model-output" id="output-${modelId}">
            <div class="output-text">Waiting for response...</div>
        </div>
    `;
    
    document.getElementById('model-columns').appendChild(column);
}

// Update model column with results
function updateModelColumn(model) {
    const scoreContainer = document.getElementById(`score-${model.model}`);
    const statsContainer = document.getElementById(`stats-${model.model}`);
    const outputContainer = document.getElementById(`output-${model.model}`);
    
    // Update scores if available
    if (scoreContainer && model.score !== null && model.score !== undefined) {
        const scoreClass = model.score >= 8 ? 'score-high' : 
                          model.score >= 6 ? 'score-medium' : 'score-low';
        let scoreHTML = `<span class="score-badge ${scoreClass}">${model.score.toFixed(1)}/10</span>`;
        
        if (model.evaluation && model.evaluation.contains_expected !== undefined) {
            const matchValue = model.evaluation.contains_expected;
            const matchPercent = Math.round(matchValue * 100);
            const matchClass = matchValue >= 0.8 ? 'match-high' : 
                             matchValue >= 0.5 ? 'match-medium' : 'match-low';
            const matchText = matchValue === 1.0 ? '✓ Match' : `${matchPercent}%`;
            scoreHTML += `<span class="match-indicator ${matchClass}" title="Context Match: ${matchPercent}%">${matchText}</span>`;
        }
        
        scoreContainer.innerHTML = scoreHTML;
    }
    
    // Update stats
    if (statsContainer) {
        statsContainer.innerHTML = `
            <span class="stat-item"><i class="fas fa-clock"></i> ${model.response_time.toFixed(2)}s</span>
            <span class="stat-item"><i class="fas fa-coins"></i> $${model.cost.toFixed(4)}</span>
            <span class="stat-item"><i class="fas fa-file-alt"></i> ${model.tokens} tokens</span>
        `;
    }
    
    // Update output
    if (outputContainer) {
        outputContainer.innerHTML = `<div class="output-text">${escapeHtml(model.output)}</div>`;
    }
}

// Display results
function displayResults(data) {
    currentComparison = data;
    hideLoadingState();
    
    // Update each model column
    data.models.forEach(model => {
        updateModelColumn(model);
    });
    
    // Update metrics bar
    updateMetricsBar(data.models);
}

// Update metrics bar
function updateMetricsBar(models) {
    if (!models || models.length === 0) {
        document.getElementById('metrics-bar').style.display = 'none';
        return;
    }
    
    const avgResponseTime = models.reduce((sum, m) => sum + m.response_time, 0) / models.length;
    const totalCost = models.reduce((sum, m) => sum + m.cost, 0);
    const scores = models.filter(m => m.score).map(m => m.score);
    const bestScore = scores.length > 0 ? Math.max(...scores) : 0;
    const fastestModel = models.reduce((fastest, model) => 
        model.response_time < fastest.response_time ? model : fastest
    );
    
    document.getElementById('avg-response-time').textContent = `${avgResponseTime.toFixed(2)}s`;
    document.getElementById('total-cost').textContent = `$${totalCost.toFixed(4)}`;
    document.getElementById('best-score').textContent = bestScore > 0 ? `${bestScore.toFixed(1)}/10` : '-';
    document.getElementById('fastest-model').textContent = fastestModel.model;
    
    document.getElementById('metrics-bar').style.display = 'block';
}

// Show loading state
function showLoadingState(models) {
    document.getElementById('loading-overlay').style.display = 'flex';
    
    const progressDiv = document.getElementById('loading-progress');
    progressDiv.innerHTML = models.map(model => 
        `<div id="progress-${model}">⏳ ${model}: Waiting...</div>`
    ).join('');
}

// Hide loading state
function hideLoadingState() {
    document.getElementById('loading-overlay').style.display = 'none';
}

// WebSocket setup
function initWebSocket() {
    const wsUrl = `ws://${window.location.host}/ws`;
    ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'model_start') {
            const progressDiv = document.getElementById(`progress-${data.model}`);
            if (progressDiv) {
                progressDiv.innerHTML = `⏳ ${data.model}: Processing...`;
            }
        } else if (data.type === 'model_complete') {
            const progressDiv = document.getElementById(`progress-${data.model}`);
            if (progressDiv) {
                progressDiv.innerHTML = `✅ ${data.model}: Complete`;
            }
            
            // Update the model column
            updateModelColumn(data.response);
            
            // Update current comparison
            if (!currentComparison) {
                currentComparison = {
                    models: [],
                    has_expected_output: !!document.getElementById('expected-output').value
                };
            }
            currentComparison.models.push(data.response);
            
            // Update metrics
            updateMetricsBar(currentComparison.models);
            
            // Hide loading when all models complete
            const selectedModels = Array.from(document.querySelectorAll('.model-checkbox input:checked'))
                .map(cb => cb.value);
            if (currentComparison.models.length === selectedModels.length) {
                hideLoadingState();
            }
        } else if (data.type === 'score_update') {
            // Update score for existing model
            const model = currentComparison.models.find(m => m.model === data.model);
            if (model) {
                model.score = data.score;
                model.evaluation = data.evaluation;
                updateModelColumn(model);
                updateMetricsBar(currentComparison.models);
            }
        }
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected');
        setTimeout(initWebSocket, 5000);
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

// Variable management
function detectVariables() {
    const prompt = document.getElementById('prompt-input').value;
    const variablePattern = /\{\{(\w+)\}\}/g;
    const detectedVars = new Set();
    
    let match;
    while ((match = variablePattern.exec(prompt)) !== null) {
        detectedVars.add(match[1]);
    }
    
    // Get current variables
    const currentVars = new Set();
    document.querySelectorAll('.variable-item input[type="text"]').forEach(input => {
        if (input.classList.contains('var-name')) {
            currentVars.add(input.value);
        }
    });
    
    // Add new detected variables
    detectedVars.forEach(varName => {
        if (!currentVars.has(varName)) {
            addVariable(varName);
        }
    });
}

function addVariable(name = '') {
    const container = document.getElementById('variables-container');
    const varId = `var-${Date.now()}`;
    
    const varItem = document.createElement('div');
    varItem.className = 'variable-item';
    varItem.id = varId;
    varItem.innerHTML = `
        <input type="text" class="var-name" placeholder="Variable name" value="${name}">
        <input type="text" class="var-value" placeholder="Value">
        <button class="btn btn-sm btn-outline" onclick="removeVariable('${varId}')">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(varItem);
}

function removeVariable(id) {
    document.getElementById(id).remove();
}

// Theme management
function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    updateThemeToggle();
    
    // Save preference
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('pbt-theme', isDark ? 'dark' : 'light');
}

function updateThemeToggle() {
    const toggle = document.getElementById('theme-toggle');
    const text = document.getElementById('theme-text');
    const isDark = document.body.classList.contains('dark-mode');
    
    toggle.innerHTML = `<i class="fas fa-${isDark ? 'sun' : 'moon'}"></i> <span id="theme-text">${isDark ? 'Light' : 'Dark'}</span>`;
}

// State management
function saveState() {
    const state = {
        prompt: document.getElementById('prompt-input').value,
        expectedOutput: document.getElementById('expected-output').value,
        temperature: document.getElementById('temperature').value,
        maxTokens: document.getElementById('max-tokens').value
    };
    localStorage.setItem('pbt-studio-state', JSON.stringify(state));
}

function loadSavedState() {
    const savedState = localStorage.getItem('pbt-studio-state');
    if (savedState) {
        const state = JSON.parse(savedState);
        document.getElementById('prompt-input').value = state.prompt || '';
        document.getElementById('expected-output').value = state.expectedOutput || '';
        document.getElementById('temperature').value = state.temperature || '0.7';
        document.getElementById('max-tokens').value = state.maxTokens || '1000';
        document.getElementById('temperature-value').textContent = state.temperature || '0.7';
        
        detectVariables();
    }
}

// Example prompt
function loadExample() {
    document.getElementById('prompt-input').value = `Write a {{style}} story about {{topic}} in {{num_sentences}} sentences.

The story should be appropriate for {{audience}} and include a {{ending_type}} ending.`;
    
    detectVariables();
    
    // Set example variable values
    setTimeout(() => {
        const varInputs = document.querySelectorAll('.variable-item');
        if (varInputs[0]) varInputs[0].querySelector('.var-value').value = 'funny';
        if (varInputs[1]) varInputs[1].querySelector('.var-value').value = 'a robot learning to cook';
        if (varInputs[2]) varInputs[2].querySelector('.var-value').value = '5';
        if (varInputs[3]) varInputs[3].querySelector('.var-value').value = 'children';
        if (varInputs[4]) varInputs[4].querySelector('.var-value').value = 'happy';
    }, 100);
    
    document.getElementById('expected-output').value = 'A lighthearted story with humor that teaches a positive lesson.';
}

// History management
async function showHistory() {
    try {
        const response = await fetch(`${apiEndpoint}/history?limit=20`);
        const data = await response.json();
        
        const historyList = document.getElementById('history-list');
        historyList.innerHTML = '';
        
        if (data.history.length === 0) {
            historyList.innerHTML = '<p class="text-muted">No comparison history yet.</p>';
        } else {
            data.history.forEach(item => {
                const historyItem = document.createElement('div');
                historyItem.className = 'history-item';
                historyItem.onclick = () => loadHistoryItem(item);
                historyItem.innerHTML = `
                    <div class="history-meta">
                        <span>${new Date(item.timestamp).toLocaleString()}</span>
                        <span>${item.models.length} models</span>
                    </div>
                    <div class="history-prompt">${item.prompt}</div>
                `;
                historyList.appendChild(historyItem);
            });
        }
        
        document.getElementById('history-modal').style.display = 'block';
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

function loadHistoryItem(item) {
    closeModal('history-modal');
    displayResults(item);
}

// Saved prompts management
async function showSavedPrompts() {
    document.getElementById('saved-prompts-modal').style.display = 'block';
    
    try {
        const response = await fetch(`${apiEndpoint}/prompts`);
        const data = await response.json();
        
        const promptsList = document.getElementById('saved-prompts-list');
        
        if (data.prompts.length === 0) {
            promptsList.innerHTML = '<p class="text-muted">No saved prompts yet.</p>';
        } else {
            promptsList.innerHTML = data.prompts.map(prompt => `
                <div class="saved-prompt-item">
                    <div class="prompt-header">
                        <h4>${escapeHtml(prompt.name)}</h4>
                        <div class="prompt-actions">
                            <button class="btn btn-sm btn-outline" onclick="loadPrompt('${prompt.id}')">
                                <i class="fas fa-upload"></i> Load
                            </button>
                            <button class="btn btn-sm btn-outline" onclick="deletePrompt('${prompt.id}')">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                    <p class="prompt-preview">${escapeHtml(prompt.prompt)}</p>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Failed to load saved prompts:', error);
        document.getElementById('saved-prompts-list').innerHTML = 
            '<p class="text-danger">Failed to load saved prompts.</p>';
    }
}

// Settings
function showSettings() {
    document.getElementById('settings-modal').style.display = 'block';
}

// Modal management
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Utility functions
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Visual effects
function createFloatingParticles() {
    const container = document.getElementById('particles-container');
    
    for (let i = 0; i < 20; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        particle.style.width = Math.random() * 4 + 2 + 'px';
        particle.style.height = particle.style.width;
        particle.style.left = Math.random() * 100 + '%';
        particle.style.animationDelay = Math.random() * 20 + 's';
        particle.style.animationDuration = 20 + Math.random() * 10 + 's';
        container.appendChild(particle);
    }
}

// Expose functions to window for onclick handlers
window.compareModels = compareModels;
window.toggleTheme = toggleTheme;
window.showHistory = showHistory;
window.showSavedPrompts = showSavedPrompts;
window.showSettings = showSettings;
window.closeModal = closeModal;
window.loadExample = loadExample;
window.addVariable = addVariable;
window.removeVariable = removeVariable;
window.detectVariables = detectVariables;