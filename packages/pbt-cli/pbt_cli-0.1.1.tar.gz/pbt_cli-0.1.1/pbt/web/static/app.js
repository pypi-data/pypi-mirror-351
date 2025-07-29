// PBT Studio - Interactive Web UI

// Global state
let currentComparison = null;
let variableCount = 0;
let ws = null;
let isDarkMode = false;
let logger = null;

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    initLogger();
    initTheme();
    loadModels();
    setupEventListeners();
    loadSavedState();
    initWebSocket();
    createFloatingParticles();
    initSmoothAnimations();
    initEnhancedAnimations();
    logger.log('🚀 PBT Studio initialized successfully');
});

// Setup event listeners
function setupEventListeners() {
    // Temperature slider
    const temperatureSlider = document.getElementById('temperature');
    const temperatureValue = document.getElementById('temperature-value');
    temperatureSlider.addEventListener('input', (e) => {
        temperatureValue.textContent = e.target.value;
    });

    // Auto-detect variables in prompt
    const promptInput = document.getElementById('prompt-input');
    promptInput.addEventListener('input', detectVariables);

    // Save state on change
    promptInput.addEventListener('change', saveState);
    document.getElementById('expected-output').addEventListener('change', saveState);
}

// Load available models from API
async function loadModels() {
    try {
        const response = await fetch('/api/models');
        const data = await response.json();
        
        const modelSelector = document.querySelector('.model-selector');
        modelSelector.innerHTML = '';
        
        data.models.forEach(model => {
            const label = document.createElement('label');
            label.className = 'model-checkbox';
            label.innerHTML = `
                <input type="checkbox" value="${model.id}" ${['claude', 'gpt-4', 'gpt-3.5-turbo'].includes(model.id) ? 'checked' : ''}>
                <span>${model.name}</span>
            `;
            modelSelector.appendChild(label);
        });
    } catch (error) {
        console.error('Failed to load models:', error);
    }
}

// Detect variables in prompt template
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
        currentVars.add(input.value);
    });
    
    // Add new detected variables
    detectedVars.forEach(varName => {
        if (!currentVars.has(varName)) {
            addVariable(varName);
        }
    });
}

// Add a variable input
function addVariable(name = '') {
    const container = document.getElementById('variables-container');
    const variableId = `var-${variableCount++}`;
    
    const variableItem = document.createElement('div');
    variableItem.className = 'variable-item';
    variableItem.id = variableId;
    variableItem.innerHTML = `
        <input type="text" placeholder="Variable name" value="${name}" ${name ? 'readonly' : ''}>
        <input type="text" placeholder="Variable value">
        <button onclick="removeVariable('${variableId}')" title="Remove variable">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(variableItem);
}

// Remove a variable
function removeVariable(id) {
    document.getElementById(id).remove();
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
            const response = await fetch('/api/compare', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    prompt,
                    models: selectedModels,
                    variables,
                    expected_output: expectedOutput,
                    temperature,
                    max_tokens: maxTokens
                })
            });
            
            const data = await response.json();
            displayResults(data);
        }
    } catch (error) {
        console.error('Comparison failed:', error);
        alert('Failed to compare models. Please try again.');
        hideLoadingState();
    }
}

// Show loading state
function showLoadingState(models) {
    document.getElementById('loading-state').style.display = 'block';
    document.getElementById('results-container').innerHTML = '';
    document.getElementById('metrics-summary').style.display = 'none';
    document.getElementById('recommendations').style.display = 'none';
    document.getElementById('result-actions').style.display = 'none';
    
    // Show progress for each model
    const progressDiv = document.getElementById('loading-progress');
    progressDiv.innerHTML = models.map(model => 
        `<div id="progress-${model}">⏳ ${model}: Waiting...</div>`
    ).join('');
}

// Hide loading state
function hideLoadingState() {
    document.getElementById('loading-state').style.display = 'none';
}

// Display comparison results
function displayResults(data) {
    currentComparison = data;
    hideLoadingState();
    
    // Log the received data for debugging
    console.log('DisplayResults data:', data);
    console.log('Has expected output:', data.has_expected_output);
    
    // Show result actions
    document.getElementById('result-actions').style.display = 'flex';
    
    // Display model responses
    const container = document.getElementById('results-container');
    container.innerHTML = '<div class="model-results"></div>';
    const modelResults = container.querySelector('.model-results');
    
    data.models.forEach(model => {
        // Log model data for debugging
        console.log(`Model ${model.model}:`, {
            score: model.score,
            evaluation: model.evaluation,
            hasScore: model.score !== null && model.score !== undefined
        });
        
        const scoreClass = model.score >= 8 ? 'score-high' : 
                          model.score >= 6 ? 'score-medium' : 'score-low';
        
        const modelCard = document.createElement('div');
        modelCard.className = 'model-card';
        
        // Show score loading indicator if expected output was provided but score is not yet calculated
        let scoreDisplay = '';
        let matchIndicator = '';
        if (data.has_expected_output) {
            if (model.score !== null && model.score !== undefined) {
                scoreDisplay = `<span class="score-badge ${scoreClass}">${model.score.toFixed(1)}/10</span>`;
                // Add context match indicator if available
                if (model.evaluation && model.evaluation.contains_expected !== undefined) {
                    const matchValue = model.evaluation.contains_expected;
                    const matchPercent = Math.round(matchValue * 100);
                    const matchClass = matchValue >= 0.8 ? 'match-high' : 
                                     matchValue >= 0.5 ? 'match-medium' : 'match-low';
                    const matchText = matchValue === 1.0 ? '✓ Match' : `${matchPercent}%`;
                    matchIndicator = `<span class="match-indicator ${matchClass}" title="Context Match: ${matchPercent}%">${matchText}</span>`;
                }
            } else {
                scoreDisplay = `<span class="score-loading">Calculating...</span>`;
            }
        }
        
        modelCard.innerHTML = `
            <div class="model-card-header">
                <div class="model-header-left">
                    <span class="model-name">${model.model}</span>
                    <div class="score-container">
                        ${scoreDisplay}
                        ${matchIndicator}
                    </div>
                </div>
                <div class="model-stats">
                    <span class="stat-item"><i class="fas fa-clock"></i> ${model.response_time.toFixed(2)}s</span>
                    <span class="stat-item"><i class="fas fa-coins"></i> $${model.cost.toFixed(4)}</span>
                    <span class="stat-item"><i class="fas fa-file-alt"></i> ${model.tokens} tokens</span>
                </div>
            </div>
            <div class="model-card-body">
                <div class="output-text">${escapeHtml(model.output)}</div>
            </div>
        `;
        modelResults.appendChild(modelCard);
    });
    
    // Display metrics summary only if we have scores
    const hasScores = data.models.some(m => m.score !== null && m.score !== undefined);
    if (hasScores) {
        displayMetricsSummary(data.models);
    } else {
        document.getElementById('metrics-summary').style.display = 'none';
    }
    
    // Display recommendations
    displayRecommendations(data.recommendations);
}

// Format metric names (kept for potential future use)
function formatMetricName(key) {
    return key.split('_').map(word => 
        word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
}

// Display metrics summary
function displayMetricsSummary(models) {
    const metricsDiv = document.getElementById('metrics-summary');
    
    // Only show metrics if we have actual data
    if (!models || models.length === 0) {
        metricsDiv.style.display = 'none';
        return;
    }
    
    // Calculate average metrics
    const avgResponseTime = models.reduce((sum, m) => sum + m.response_time, 0) / models.length;
    const totalCost = models.reduce((sum, m) => sum + m.cost, 0);
    const avgTokens = models.reduce((sum, m) => sum + m.tokens, 0) / models.length;
    const avgScore = models.filter(m => m.score).reduce((sum, m) => sum + m.score, 0) / 
                     models.filter(m => m.score).length || 0;
    
    // Only show if we have meaningful metrics
    if (avgResponseTime > 0 || totalCost > 0 || avgTokens > 0 || avgScore > 0) {
        metricsDiv.style.display = 'block';
        const metricsGrid = metricsDiv.querySelector('.metrics-grid');
        metricsGrid.innerHTML = `
            <div class="metric-card">
                <h4>Avg Response Time</h4>
                <div class="value">${avgResponseTime.toFixed(2)}s</div>
            </div>
            <div class="metric-card">
                <h4>Total Cost</h4>
                <div class="value">$${totalCost.toFixed(4)}</div>
            </div>
            <div class="metric-card">
                <h4>Avg Tokens</h4>
                <div class="value">${avgTokens.toFixed(0)}</div>
            </div>
            ${avgScore > 0 ? `
            <div class="metric-card">
                <h4>Avg Score</h4>
                <div class="value">${avgScore.toFixed(1)}/10</div>
            </div>
            ` : ''}
        `;
    } else {
        metricsDiv.style.display = 'none';
    }
}

// Display recommendations
function displayRecommendations(recommendations) {
    const recsDiv = document.getElementById('recommendations');
    recsDiv.style.display = 'block';
    
    const recsCards = recsDiv.querySelector('.recommendation-cards');
    recsCards.innerHTML = Object.entries(recommendations).map(([category, model]) => {
        const icon = {
            'best_quality': 'fa-trophy',
            'best_speed': 'fa-bolt',
            'best_cost': 'fa-dollar-sign',
            'balanced': 'fa-balance-scale'
        }[category] || 'fa-star';
        
        const title = category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        return `
            <div class="recommendation-card ${category === 'balanced' ? 'best' : ''}">
                <h4><i class="fas ${icon}"></i> ${title}</h4>
                <div class="model">${model}</div>
            </div>
        `;
    }).join('');
}

// Export results
async function exportResults(format) {
    if (!currentComparison) return;
    
    if (format === 'json') {
        const dataStr = JSON.stringify(currentComparison, null, 2);
        downloadFile('comparison.json', dataStr, 'application/json');
    } else if (format === 'markdown') {
        const markdown = generateMarkdown(currentComparison);
        downloadFile('comparison.md', markdown, 'text/markdown');
    }
}

// Generate markdown report
function generateMarkdown(data) {
    let md = `# Model Comparison Report\n\n`;
    md += `**Date**: ${new Date(data.timestamp).toLocaleString()}\n\n`;
    md += `## Prompt\n\`\`\`\n${data.prompt}\n\`\`\`\n\n`;
    
    if (Object.keys(data.variables).length > 0) {
        md += `## Variables\n`;
        Object.entries(data.variables).forEach(([key, value]) => {
            md += `- **${key}**: ${value}\n`;
        });
        md += `\n`;
    }
    
    md += `## Results\n\n`;
    data.models.forEach(model => {
        md += `### ${model.model}\n`;
        md += `- **Response Time**: ${model.response_time.toFixed(2)}s\n`;
        md += `- **Tokens**: ${model.tokens}\n`;
        md += `- **Cost**: $${model.cost.toFixed(4)}\n`;
        if (model.score) {
            md += `- **Score**: ${model.score.toFixed(1)}/10\n`;
        }
        md += `\n**Output:**\n\`\`\`\n${model.output}\n\`\`\`\n\n`;
    });
    
    md += `## Recommendations\n`;
    Object.entries(data.recommendations).forEach(([category, model]) => {
        const title = category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        md += `- **${title}**: ${model}\n`;
    });
    
    return md;
}

// Download file
function downloadFile(filename, content, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
}

// Save prompt
function savePrompt() {
    document.getElementById('save-prompt-modal').style.display = 'block';
}

// Confirm save prompt
async function confirmSavePrompt() {
    const name = document.getElementById('prompt-name').value;
    const description = document.getElementById('prompt-description').value;
    const prompt = document.getElementById('prompt-input').value;
    const expectedOutput = document.getElementById('expected-output').value;
    
    if (!name) {
        alert('Please enter a prompt name');
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
    
    // Get selected models
    const models = [];
    document.querySelectorAll('.model-checkbox input:checked').forEach(checkbox => {
        models.push(checkbox.value);
    });
    
    try {
        const response = await fetch('/api/prompts/save', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name,
                description,
                prompt,
                variables,
                models,
                expected_output: expectedOutput
            })
        });
        
        if (response.ok) {
            closeModal('save-prompt-modal');
            alert('Prompt saved successfully!');
        } else {
            const error = await response.json();
            alert(`Failed to save prompt: ${error.detail || 'Unknown error'}`);
        }
    } catch (error) {
        console.error('Failed to save prompt:', error);
        alert(`Failed to save prompt: ${error.message}`);
    }
}

// Show saved prompts
async function showSavedPrompts() {
    try {
        const response = await fetch('/api/prompts');
        const data = await response.json();
        
        // Create saved prompts modal if it doesn't exist
        let modal = document.getElementById('saved-prompts-modal');
        if (!modal) {
            modal = createSavedPromptsModal();
        }
        
        // Populate saved prompts
        const promptsList = modal.querySelector('#saved-prompts-list');
        promptsList.innerHTML = '';
        
        if (data.prompts && data.prompts.length > 0) {
            data.prompts.forEach(prompt => {
                const promptItem = document.createElement('div');
                promptItem.className = 'saved-prompt-item';
                promptItem.innerHTML = `
                    <div class="prompt-info">
                        <h4>${prompt.name}</h4>
                        <p>${prompt.description || 'No description'}</p>
                        <span class="prompt-date">${new Date(prompt.created_at).toLocaleDateString()}</span>
                    </div>
                    <div class="prompt-actions">
                        <button class="btn btn-sm btn-primary" onclick="loadSavedPrompt('${prompt.id}')">
                            <i class="fas fa-upload"></i> Load
                        </button>
                        <button class="btn btn-sm btn-outline" onclick="deleteSavedPrompt('${prompt.id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                `;
                promptsList.appendChild(promptItem);
            });
        } else {
            promptsList.innerHTML = '<p class="empty-state">No saved prompts yet. Save your first prompt to see it here!</p>';
        }
        
        modal.style.display = 'block';
    } catch (error) {
        console.error('Failed to load saved prompts:', error);
        alert('Failed to load saved prompts. Please try again.');
    }
}

// Create saved prompts modal
function createSavedPromptsModal() {
    const modal = document.createElement('div');
    modal.id = 'saved-prompts-modal';
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content modal-large">
            <h3>Saved Prompts</h3>
            <div id="saved-prompts-list" class="saved-prompts-list">
                <!-- Saved prompts will be added here -->
            </div>
            <div class="modal-actions">
                <button class="btn btn-secondary" onclick="closeModal('saved-prompts-modal')">Close</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

// Load a saved prompt
async function loadSavedPrompt(promptId) {
    try {
        const response = await fetch(`/api/prompts/${promptId}`);
        const prompt = await response.json();
        
        // Load prompt data into the UI
        document.getElementById('prompt-input').value = prompt.prompt || '';
        document.getElementById('expected-output').value = prompt.expected_output || '';
        
        // Load variables
        document.getElementById('variables-container').innerHTML = '';
        if (prompt.variables) {
            Object.entries(prompt.variables).forEach(([key, value]) => {
                addVariable(key);
                setTimeout(() => {
                    const lastVariable = document.querySelector('.variable-item:last-child');
                    if (lastVariable) {
                        lastVariable.querySelectorAll('input')[1].value = value;
                    }
                }, 100);
            });
        }
        
        // Load selected models
        document.querySelectorAll('.model-checkbox input').forEach(checkbox => {
            checkbox.checked = prompt.models && prompt.models.includes(checkbox.value);
        });
        
        closeModal('saved-prompts-modal');
        logger.success('✅ Loaded saved prompt successfully');
    } catch (error) {
        console.error('Failed to load prompt:', error);
        alert('Failed to load prompt. Please try again.');
    }
}

// Delete a saved prompt
async function deleteSavedPrompt(promptId) {
    if (!confirm('Are you sure you want to delete this prompt?')) return;
    
    try {
        const response = await fetch(`/api/prompts/${promptId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            logger.success('🗑️ Prompt deleted successfully');
            showSavedPrompts(); // Refresh the list
        } else {
            throw new Error('Failed to delete prompt');
        }
    } catch (error) {
        console.error('Failed to delete prompt:', error);
        alert('Failed to delete prompt. Please try again.');
    }
}

// Show history
async function showHistory() {
    try {
        const response = await fetch('/api/history?limit=20');
        const data = await response.json();
        
        const historyList = document.getElementById('history-list');
        historyList.innerHTML = '';
        
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
        
        document.getElementById('history-modal').style.display = 'block';
    } catch (error) {
        console.error('Failed to load history:', error);
    }
}

// Load history item
function loadHistoryItem(item) {
    closeModal('history-modal');
    displayResults(item);
}

// Show settings
function showSettings() {
    alert('Settings feature coming soon!');
}

// Load example
function loadExample() {
    document.getElementById('prompt-input').value = `Summarize the following text in {{num_sentences}} sentences:

{{text}}

Focus on the key points and maintain the original tone.`;
    
    // Add example variables
    document.getElementById('variables-container').innerHTML = '';
    addVariable('num_sentences');
    addVariable('text');
    
    // Set example values
    setTimeout(() => {
        const inputs = document.querySelectorAll('.variable-item input[type="text"]');
        inputs[1].value = '3';
        inputs[3].value = 'Artificial intelligence is rapidly transforming industries worldwide. Machine learning algorithms can now process vast amounts of data to identify patterns and make predictions that were previously impossible. This technological revolution is creating new opportunities while also raising important questions about privacy, employment, and the future of human-machine interaction.';
    }, 100);
    
    document.getElementById('expected-output').value = 'Artificial intelligence and machine learning are revolutionizing industries by processing large datasets to identify patterns and make unprecedented predictions. This transformation brings significant opportunities but also raises concerns about privacy, job displacement, and human-machine relationships. The rapid advancement of AI technology is fundamentally changing how businesses operate and society functions.';
}

// Close modal
function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Save state to localStorage
function saveState() {
    const state = {
        prompt: document.getElementById('prompt-input').value,
        expectedOutput: document.getElementById('expected-output').value,
        temperature: document.getElementById('temperature').value,
        maxTokens: document.getElementById('max-tokens').value
    };
    localStorage.setItem('pbt-studio-state', JSON.stringify(state));
}

// Load saved state
function loadSavedState() {
    const savedState = localStorage.getItem('pbt-studio-state');
    if (savedState) {
        const state = JSON.parse(savedState);
        document.getElementById('prompt-input').value = state.prompt || '';
        document.getElementById('expected-output').value = state.expectedOutput || '';
        document.getElementById('temperature').value = state.temperature || '0.7';
        document.getElementById('max-tokens').value = state.maxTokens || '1000';
        document.getElementById('temperature-value').textContent = state.temperature || '0.7';
        
        // Detect variables
        detectVariables();
    }
}

// Initialize WebSocket connection
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
            
            // Update results incrementally
            if (!currentComparison) {
                currentComparison = {
                    models: [],
                    timestamp: new Date().toISOString(),
                    has_expected_output: !!document.getElementById('expected-output').value
                };
            }
            currentComparison.models.push(data.response);
            
            // Re-render results
            displayResults(currentComparison);
        } else if (data.type === 'score_update') {
            // Update score for existing model
            console.log('Score update received:', data);
            if (currentComparison && currentComparison.models) {
                const modelIndex = currentComparison.models.findIndex(m => m.model === data.model);
                if (modelIndex !== -1) {
                    currentComparison.models[modelIndex].score = data.score;
                    currentComparison.models[modelIndex].evaluation = data.evaluation;
                    // Re-render results with updated scores
                    displayResults(currentComparison);
                }
            }
        }
    };
    
    ws.onclose = () => {
        console.log('WebSocket disconnected');
        // Attempt to reconnect after 5 seconds
        setTimeout(initWebSocket, 5000);
    };
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatMetricName(name) {
    return name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

// Create floating particles background effect
function createFloatingParticles() {
    const particlesContainer = document.getElementById('particles');
    const particleCount = 30;
    
    for (let i = 0; i < particleCount; i++) {
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Random positioning
        particle.style.left = Math.random() * 100 + '%';
        particle.style.top = Math.random() * 100 + '%';
        
        // Random animation delay
        particle.style.animationDelay = Math.random() * 6 + 's';
        particle.style.animationDuration = (Math.random() * 4 + 4) + 's';
        
        // Random opacity
        particle.style.opacity = Math.random() * 0.6 + 0.2;
        
        particlesContainer.appendChild(particle);
    }
}

// Initialize smooth animations and interactions
function initSmoothAnimations() {
    // Animate form groups on scroll
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.animationPlayState = 'running';
            }
        });
    }, { threshold: 0.1 });
    
    document.querySelectorAll('.form-group').forEach(group => {
        observer.observe(group);
    });
    
    // Add smooth hover effects to buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
    
    // Add ripple effect to buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            ripple.style.position = 'absolute';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(255, 255, 255, 0.3)';
            ripple.style.transform = 'scale(0)';
            ripple.style.animation = 'ripple 0.6s linear';
            ripple.style.pointerEvents = 'none';
            
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
    
    // Add CSS for ripple animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
        .btn {
            position: relative;
            overflow: hidden;
        }
    `;
    document.head.appendChild(style);
    
    // Smooth scrolling for better UX
    document.documentElement.style.scrollBehavior = 'smooth';
    
    // Add parallax effect to background
    let ticking = false;
    function updateParallax() {
        const scrolled = window.pageYOffset;
        const parallax = document.querySelector('body::before');
        if (parallax) {
            const speed = scrolled * 0.5;
            parallax.style.transform = `translate3d(0, ${speed}px, 0)`;
        }
        ticking = false;
    }
    
    window.addEventListener('scroll', function() {
        if (!ticking) {
            requestAnimationFrame(updateParallax);
            ticking = true;
        }
    });
    
    // Add glow effect to active elements
    document.querySelectorAll('input, textarea').forEach(input => {
        input.addEventListener('focus', function() {
            this.style.boxShadow = '0 0 20px rgba(0, 122, 255, 0.3)';
            this.style.borderColor = '#007AFF';
        });
        
        input.addEventListener('blur', function() {
            this.style.boxShadow = '';
            this.style.borderColor = '';
        });
    });
    
    // Add smooth transitions for model cards
    const modelObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateX(0)';
                }, index * 100);
            }
        });
    }, { threshold: 0.1 });
    
    // Observe model cards when they're created
    const originalDisplayResults = displayResults;
    window.displayResults = function(data) {
        originalDisplayResults(data);
        
        // Re-observe new model cards
        setTimeout(() => {
            document.querySelectorAll('.model-card').forEach(card => {
                card.style.opacity = '0';
                card.style.transform = 'translateX(30px)';
                card.style.transition = 'all 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
                modelObserver.observe(card);
            });
        }, 100);
    };
}

// Enable drag and drop for model cards
function enableDragAndDrop() {
    let draggedElement = null;
    let placeholder = null;
    
    function handleDragStart(e) {
        draggedElement = this;
        this.style.opacity = '0.6';
        this.style.transform = 'scale(0.95)';
        
        // Create placeholder
        placeholder = document.createElement('div');
        placeholder.className = 'drag-placeholder';
        placeholder.style.height = this.offsetHeight + 'px';
        
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', this.innerHTML);
        
        // Apple-style haptic feedback simulation
        if (navigator.vibrate) navigator.vibrate(10);
    }
    
    function handleDragOver(e) {
        if (e.preventDefault) e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
        
        const afterElement = getDragAfterElement(e.currentTarget, e.clientY);
        const container = e.currentTarget;
        
        if (afterElement == null) {
            container.appendChild(placeholder);
        } else {
            container.insertBefore(placeholder, afterElement);
        }
        
        return false;
    }
    
    function handleDragEnd(e) {
        if (draggedElement) {
            draggedElement.style.opacity = '';
            draggedElement.style.transform = '';
            
            // Smooth animation back
            draggedElement.style.transition = 'all 0.3s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
            
            if (placeholder && placeholder.parentNode) {
                placeholder.parentNode.replaceChild(draggedElement, placeholder);
            }
            
            // Clean up
            draggedElement = null;
            placeholder = null;
            
            logger.log('📦 Model cards reordered');
        }
    }
    
    function getDragAfterElement(container, y) {
        const draggableElements = [...container.querySelectorAll('.model-card:not(.dragging)')];
        
        return draggableElements.reduce((closest, child) => {
            const box = child.getBoundingClientRect();
            const offset = y - box.top - box.height / 2;
            
            if (offset < 0 && offset > closest.offset) {
                return { offset: offset, element: child };
            } else {
                return closest;
            }
        }, { offset: Number.NEGATIVE_INFINITY }).element;
    }
    
    // Attach to model cards
    setTimeout(() => {
        const modelCards = document.querySelectorAll('.model-card');
        const container = document.querySelector('.model-results');
        
        modelCards.forEach(card => {
            card.draggable = true;
            card.addEventListener('dragstart', handleDragStart);
            card.addEventListener('dragend', handleDragEnd);
            
            // Add grab cursor
            card.style.cursor = 'grab';
            card.addEventListener('mousedown', function() {
                this.style.cursor = 'grabbing';
            });
            card.addEventListener('mouseup', function() {
                this.style.cursor = 'grab';
            });
        });
        
        if (container) {
            container.addEventListener('dragover', handleDragOver);
        }
    }, 500);
}

// Enhanced Logger System
function initLogger() {
    logger = {
        log: (message, type = 'info') => {
            const timestamp = new Date().toISOString();
            const logEntry = {
                timestamp,
                type,
                message,
                url: window.location.href,
                userAgent: navigator.userAgent
            };
            
            // Console output with styling
            const styles = {
                info: 'color: #007AFF; font-weight: bold',
                success: 'color: #30D158; font-weight: bold',
                warning: 'color: #FF9F0A; font-weight: bold',
                error: 'color: #FF453A; font-weight: bold'
            };
            
            console.log(`%c[PBT Studio] ${message}`, styles[type] || styles.info);
            
            // Store in localStorage for debugging
            const logs = JSON.parse(localStorage.getItem('pbt-logs') || '[]');
            logs.push(logEntry);
            if (logs.length > 100) logs.shift(); // Keep last 100 logs
            localStorage.setItem('pbt-logs', JSON.stringify(logs));
            
            // Send to backend if critical
            if (type === 'error') {
                fetch('/api/logs', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(logEntry)
                }).catch(() => {}); // Silent fail
            }
        },
        
        success: (message) => logger.log(message, 'success'),
        warning: (message) => logger.log(message, 'warning'),
        error: (message) => logger.log(message, 'error'),
        
        getLogs: () => JSON.parse(localStorage.getItem('pbt-logs') || '[]'),
        clearLogs: () => localStorage.removeItem('pbt-logs')
    };
}

// Theme Management
function initTheme() {
    // Load saved theme preference
    const savedTheme = localStorage.getItem('pbt-theme') || 'light';
    isDarkMode = savedTheme === 'dark';
    
    // Apply theme
    document.documentElement.setAttribute('data-theme', savedTheme);
    updateThemeButton();
    
    logger.log(`🎨 Theme initialized: ${savedTheme}`);
}

function toggleTheme() {
    isDarkMode = !isDarkMode;
    const newTheme = isDarkMode ? 'dark' : 'light';
    
    // Animate theme transition
    document.body.style.transition = 'all 0.5s cubic-bezier(0.4, 0, 0.2, 1)';
    
    // Apply theme with animation
    setTimeout(() => {
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('pbt-theme', newTheme);
        updateThemeButton();
        
        // Log theme change
        logger.log(`🌙 Theme changed to: ${newTheme}`);
        
        // Add celebration animation
        createThemeChangeEffect();
    }, 50);
    
    // Reset transition
    setTimeout(() => {
        document.body.style.transition = '';
    }, 500);
}

function updateThemeButton() {
    const button = document.getElementById('theme-toggle');
    const icon = button.querySelector('i');
    const text = document.getElementById('theme-text');
    
    if (isDarkMode) {
        icon.className = 'fas fa-sun';
        text.textContent = 'Light';
        button.classList.add('dark-mode');
    } else {
        icon.className = 'fas fa-moon';
        text.textContent = 'Dark';
        button.classList.remove('dark-mode');
    }
}

function createThemeChangeEffect() {
    // Create ripple effect from theme button
    const button = document.getElementById('theme-toggle');
    const rect = button.getBoundingClientRect();
    const centerX = rect.left + rect.width / 2;
    const centerY = rect.top + rect.height / 2;
    
    const ripple = document.createElement('div');
    ripple.style.position = 'fixed';
    ripple.style.left = centerX + 'px';
    ripple.style.top = centerY + 'px';
    ripple.style.width = '20px';
    ripple.style.height = '20px';
    ripple.style.borderRadius = '50%';
    ripple.style.background = isDarkMode ? 'rgba(0, 0, 0, 0.1)' : 'rgba(255, 255, 255, 0.1)';
    ripple.style.pointerEvents = 'none';
    ripple.style.zIndex = '9999';
    ripple.style.transform = 'translate(-50%, -50%) scale(0)';
    ripple.style.transition = 'transform 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
    
    document.body.appendChild(ripple);
    
    // Trigger animation
    setTimeout(() => {
        ripple.style.transform = 'translate(-50%, -50%) scale(100)';
    }, 10);
    
    // Remove after animation
    setTimeout(() => {
        ripple.remove();
    }, 800);
}

// Enhanced Animations
function initEnhancedAnimations() {
    // Add stagger animation to elements
    function staggerAnimate(selector, animationClass, delay = 100) {
        const elements = document.querySelectorAll(selector);
        elements.forEach((el, index) => {
            setTimeout(() => {
                el.classList.add(animationClass);
            }, index * delay);
        });
    }
    
    // Intersection Observer for scroll animations
    const scrollObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                
                // Add specific animations based on element type
                if (entry.target.classList.contains('model-card')) {
                    entry.target.style.animation = 'slideInFromRight 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards';
                } else if (entry.target.classList.contains('metric-card')) {
                    entry.target.style.animation = 'zoomIn 0.5s cubic-bezier(0.4, 0, 0.2, 1) forwards';
                }
            }
        });
    }, { threshold: 0.1, rootMargin: '50px' });
    
    // Enhanced hover effects
    document.querySelectorAll('.btn, .model-checkbox, .variable-item').forEach(el => {
        el.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px) scale(1.02)';
            this.style.filter = 'brightness(1.1)';
        });
        
        el.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.filter = 'brightness(1)';
        });
    });
    
    // Breathing animation for loading states
    // Commented out - not currently used
    // function addBreathingEffect(selector) {
    //     const elements = document.querySelectorAll(selector);
    //     elements.forEach(el => {
    //         el.style.animation = 'breathe 2s ease-in-out infinite';
    //     });
    // }
    
    // Mouse trail effect
    let mouseTrail = [];
    document.addEventListener('mousemove', (e) => {
        mouseTrail.push({ x: e.clientX, y: e.clientY, time: Date.now() });
        if (mouseTrail.length > 10) mouseTrail.shift();
        
        // Create subtle trail particles
        if (Math.random() < 0.1) {
            createMouseParticle(e.clientX, e.clientY);
        }
    });
    
    logger.log('✨ Enhanced animations initialized');
}

function createMouseParticle(x, y) {
    const particle = document.createElement('div');
    particle.style.position = 'fixed';
    particle.style.left = x + 'px';
    particle.style.top = y + 'px';
    particle.style.width = '4px';
    particle.style.height = '4px';
    particle.style.borderRadius = '50%';
    particle.style.background = 'rgba(0, 122, 255, 0.6)';
    particle.style.pointerEvents = 'none';
    particle.style.zIndex = '1000';
    particle.style.animation = 'fadeOut 1s ease-out forwards';
    
    document.body.appendChild(particle);
    
    setTimeout(() => {
        particle.remove();
    }, 1000);
}

// Add CSS for new animations
const enhancedStyles = document.createElement('style');
enhancedStyles.textContent = `
    @keyframes fadeOut {
        from { opacity: 1; transform: scale(1); }
        to { opacity: 0; transform: scale(0.5); }
    }
    
    .animate-in {
        opacity: 1 !important;
        transform: translateY(0) !important;
    }
    
    .model-card, .metric-card {
        opacity: 0;
        transform: translateY(20px);
        transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .score-badge {
        animation: scoreGlow 2s ease-in-out infinite alternate,
                   bounce 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
`;
document.head.appendChild(enhancedStyles);

// Make functions globally available
window.showSavedPrompts = showSavedPrompts;
window.loadSavedPrompt = loadSavedPrompt;
window.deleteSavedPrompt = deleteSavedPrompt;
window.showHistory = showHistory;
window.loadHistoryItem = loadHistoryItem;
window.closeModal = closeModal;
window.confirmSavePrompt = confirmSavePrompt;
window.savePrompt = savePrompt;
window.loadExample = loadExample;
window.compareModels = compareModels;
window.toggleTheme = toggleTheme;
window.showSettings = showSettings;
window.addVariable = addVariable;
window.removeVariable = removeVariable;
window.exportResults = exportResults;

// Expose displayResults to window for WebSocket updates
window.displayResults = displayResults;

// Fix score display in model results
function displayResults(data) {
    logger.log('📊 Displaying comparison results', 'success');
    
    const container = document.getElementById('results-container');
    container.innerHTML = '';
    
    if (!data || !data.models || data.models.length === 0) {
        container.innerHTML = '<div class="welcome-state"><p>No results to display</p></div>';
        return;
    }
    
    const resultsDiv = document.createElement('div');
    resultsDiv.className = 'model-results';
    
    data.models.forEach((model, index) => {
        const modelCard = document.createElement('div');
        modelCard.className = 'model-card';
        modelCard.style.animationDelay = `${index * 0.1}s`;
        
        // Calculate score display class
        const scoreClass = model.score >= 8 ? 'score-high' : 
                          model.score >= 6 ? 'score-medium' : 'score-low';
        
        modelCard.innerHTML = `
            <div class="model-card-header">
                <div class="model-name">${model.model}</div>
                <div class="model-stats">
                    <div class="stat-item">
                        <i class="fas fa-clock"></i>
                        <span>${model.response_time.toFixed(2)}s</span>
                    </div>
                    <div class="stat-item">
                        <i class="fas fa-coins"></i>
                        <span>$${model.cost.toFixed(4)}</span>
                    </div>
                    <div class="stat-item">
                        <i class="fas fa-hash"></i>
                        <span>${model.tokens} tokens</span>
                    </div>
                    ${model.score ? `<div class="score-badge ${scoreClass}">${model.score.toFixed(1)}</div>` : ''}
                </div>
            </div>
            <div class="model-card-body">
                <div class="output-text">${escapeHtml(model.output)}</div>
                ${model.evaluation ? `
                    <div class="evaluation-details">
                        <h4>Evaluation Metrics</h4>
                        <div class="evaluation-metrics">
                            ${Object.entries(model.evaluation).map(([key, value]) => `
                                <div class="metric-item">
                                    <div class="metric-label">${formatMetricName(key)}</div>
                                    <div class="metric-value">${(value * 100).toFixed(1)}%</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
        
        resultsDiv.appendChild(modelCard);
    });
    
    container.appendChild(resultsDiv);
    
    // Show additional sections
    if (data.has_expected_output) {
        showMetricsSummary(data.models);
    } else {
        document.getElementById('metrics-summary').style.display = 'none';
    }
    showRecommendations(data.recommendations);
    
    // Hide loading state
    hideLoadingState();
    
    // Show result actions
    document.getElementById('result-actions').style.display = 'flex';
    
    // Apply scroll animations
    setTimeout(() => {
        document.querySelectorAll('.model-card').forEach(card => {
            card.classList.add('animate-in');
        });
    }, 100);
    
    // Enable drag and drop
    enableDragAndDrop();
    
    logger.log(`📈 Displayed results for ${data.models.length} models`);
}

function showMetricsSummary(models) {
    const summaryDiv = document.getElementById('metrics-summary');
    if (!summaryDiv) return;
    
    const avgScore = models.filter(m => m.score).reduce((sum, m) => sum + m.score, 0) / 
                     models.filter(m => m.score).length || 0;
    const avgCost = models.reduce((sum, m) => sum + m.cost, 0) / models.length;
    const avgTime = models.reduce((sum, m) => sum + m.response_time, 0) / models.length;
    const totalTokens = models.reduce((sum, m) => sum + m.tokens, 0);
    
    summaryDiv.innerHTML = `
        <h3>Performance Metrics</h3>
        <div class="metrics-grid">
            ${avgScore > 0 ? `
                <div class="metric-card">
                    <h4>Avg Score</h4>
                    <div class="value">${avgScore.toFixed(1)}/10</div>
                </div>
            ` : ''}
            <div class="metric-card">
                <h4>Avg Cost</h4>
                <div class="value">$${avgCost.toFixed(4)}</div>
            </div>
            <div class="metric-card">
                <h4>Avg Time</h4>
                <div class="value">${avgTime.toFixed(2)}s</div>
            </div>
            <div class="metric-card">
                <h4>Total Tokens</h4>
                <div class="value">${totalTokens.toLocaleString()}</div>
            </div>
        </div>
    `;
    
    summaryDiv.style.display = 'block';
    summaryDiv.style.animation = 'slideInFromBottom 0.6s cubic-bezier(0.4, 0, 0.2, 1)';
}

function showRecommendations(recommendations) {
    const recDiv = document.getElementById('recommendations');
    if (!recDiv || !recommendations) return;
    
    recDiv.innerHTML = `
        <h3>🏆 Recommendations</h3>
        <div class="recommendation-cards">
            <div class="recommendation-card best">
                <h4><i class="fas fa-trophy"></i> Best Overall</h4>
                <div class="model">${recommendations.balanced || 'N/A'}</div>
            </div>
            <div class="recommendation-card">
                <h4><i class="fas fa-medal"></i> Best Quality</h4>
                <div class="model">${recommendations.best_quality || 'N/A'}</div>
            </div>
            <div class="recommendation-card">
                <h4><i class="fas fa-tachometer-alt"></i> Fastest</h4>
                <div class="model">${recommendations.best_speed || 'N/A'}</div>
            </div>
            <div class="recommendation-card">
                <h4><i class="fas fa-dollar-sign"></i> Most Cost-Effective</h4>
                <div class="model">${recommendations.best_cost || 'N/A'}</div>
            </div>
        </div>
    `;
    
    recDiv.style.display = 'block';
    recDiv.style.animation = 'slideInFromBottom 0.8s cubic-bezier(0.4, 0, 0.2, 1)';
}