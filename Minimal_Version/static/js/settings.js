// Settings Page JavaScript

const API_BASE = 'http://localhost:5000/api';

// Tab switching
function switchTab(tabName) {
    // Remove active class from all tabs and contents
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Add active class to selected tab and content
    event.target.closest('.tab').classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Load data for the active tab
    if (tabName === 'brand') loadBrands();
    if (tabName === 'agents') loadAgents();
    if (tabName === 'api') loadApiKeys();
    if (tabName === 'model') loadModels();
}

// ===== BRAND CONFIGURATION =====

async function loadBrands() {
    try {
        const response = await fetch(`${API_BASE}/brands`);
        const data = await response.json();
        
        const brandList = document.getElementById('brand-list');
        if (data.brands && data.brands.length > 0) {
            brandList.innerHTML = data.brands.map(brand => `
                <div class="card p-4">
                    <div class="flex items-start justify-between">
                        <div class="flex-1">
                            <h3 class="font-semibold text-lg">${brand.brand_name}</h3>
                            <p class="text-sm text-muted-foreground mt-1">${brand.industry}</p>
                            <p class="text-sm mt-2"><span class="font-medium">Voice:</span> ${brand.brand_voice}</p>
                        </div>
                        <div class="flex gap-2">
                            <button onclick="editBrand(${brand.id})" class="btn btn-secondary h-9 px-3">
                                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                            </button>
                            <button onclick="deleteBrand(${brand.id})" class="btn btn-danger h-9 px-3">
                                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            brandList.innerHTML = '<p class="text-muted-foreground">No brands configured yet.</p>';
        }
    } catch (error) {
        console.error('Error loading brands:', error);
        showMessage('Failed to load brands', 'error');
    }
}

function showAddBrandModal() {
    document.getElementById('brand-modal-title').textContent = 'Add New Brand';
    document.getElementById('brand-form').reset();
    document.getElementById('brand-id').value = '';
    document.getElementById('brand-modal').classList.remove('hidden');
    document.getElementById('brand-modal').classList.add('flex');
}

async function editBrand(brandId) {
    try {
        const response = await fetch(`${API_BASE}/brands/${brandId}`);
        const data = await response.json();
        
        document.getElementById('brand-modal-title').textContent = 'Edit Brand';
        document.getElementById('brand-id').value = data.brand.id;
        document.getElementById('brand-name').value = data.brand.brand_name;
        document.getElementById('brand-industry').value = data.brand.brand_description || data.brand.market_segment || '';
        document.getElementById('brand-audience').value = data.brand.target_audience;
        document.getElementById('brand-voice').value = data.brand.brand_tone;
        document.getElementById('brand-values').value = data.brand.brand_keywords;
        document.getElementById('brand-prohibited').value = '[]';  // Not stored in DB, use empty array
        
        document.getElementById('brand-modal').classList.remove('hidden');
        document.getElementById('brand-modal').classList.add('flex');
    } catch (error) {
        console.error('Error loading brand:', error);
        showMessage('Failed to load brand details', 'error');
    }
}

function closeBrandModal() {
    document.getElementById('brand-modal').classList.add('hidden');
    document.getElementById('brand-modal').classList.remove('flex');
}

document.getElementById('brand-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const brandId = document.getElementById('brand-id').value;
    const brandData = {
        brand_name: document.getElementById('brand-name').value,
        brand_tone: document.getElementById('brand-voice').value,
        brand_description: document.getElementById('brand-industry').value,
        product_list: '[]',  // Empty array for now
        target_audience: document.getElementById('brand-audience').value,
        brand_keywords: document.getElementById('brand-values').value,
        messaging_guidelines: 'Professional and engaging',
        social_platforms: '["LinkedIn", "Twitter", "Facebook"]',
        posting_frequency: 'Daily',
        competitors: '[]',
        market_segment: document.getElementById('brand-industry').value
    };
    
    try {
        const url = brandId ? `${API_BASE}/brands/${brandId}` : `${API_BASE}/brands`;
        const method = brandId ? 'PUT' : 'POST';
        
        const response = await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(brandData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage(brandId ? 'Brand updated successfully' : 'Brand created successfully', 'success');
            closeBrandModal();
            loadBrands();
        } else {
            showMessage(data.error || 'Failed to save brand', 'error');
        }
    } catch (error) {
        console.error('Error saving brand:', error);
        showMessage('Failed to save brand', 'error');
    }
});

async function deleteBrand(brandId) {
    if (!confirm('Are you sure you want to delete this brand?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/brands/${brandId}`, { method: 'DELETE' });
        const data = await response.json();
        
        if (data.success) {
            showMessage('Brand deleted successfully', 'success');
            loadBrands();
        } else {
            showMessage(data.error || 'Failed to delete brand', 'error');
        }
    } catch (error) {
        console.error('Error deleting brand:', error);
        showMessage('Failed to delete brand', 'error');
    }
}

// ===== AGENT CONFIGURATION =====

async function loadAgents() {
    try {
        const response = await fetch(`${API_BASE}/settings/agents`);
        const data = await response.json();
        
        const agentList = document.getElementById('agent-list');
        if (data.agents && data.agents.length > 0) {
            agentList.innerHTML = data.agents.map(agent => `
                <div class="card p-4">
                    <div class="flex items-start justify-between">
                        <div class="flex-1">
                            <div class="flex items-center gap-2">
                                <h3 class="font-semibold text-lg">${agent.name}</h3>
                                <span class="text-xs px-2 py-1 rounded ${agent.enabled ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}">
                                    ${agent.enabled ? 'Enabled' : 'Disabled'}
                                </span>
                            </div>
                            <p class="text-sm text-muted-foreground mt-1">${agent.role}</p>
                            <p class="text-sm mt-2"><span class="font-medium">Temperature:</span> ${agent.temperature}</p>
                        </div>
                        <div class="flex gap-2">
                            <button onclick="editAgent('${agent.name}')" class="btn btn-secondary h-9 px-3">
                                <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                            </button>
                        </div>
                    </div>
                </div>
            `).join('');
        } else {
            agentList.innerHTML = '<p class="text-muted-foreground">No agents configured.</p>';
        }
    } catch (error) {
        console.error('Error loading agents:', error);
        showMessage('Failed to load agents', 'error');
    }
}

function showAddAgentModal() {
    document.getElementById('agent-modal-title').textContent = 'Add New Agent';
    document.getElementById('agent-form').reset();
    document.getElementById('agent-id').value = '';
    document.getElementById('agent-modal').classList.remove('hidden');
    document.getElementById('agent-modal').classList.add('flex');
}

async function editAgent(agentName) {
    try {
        const response = await fetch(`${API_BASE}/settings/agents/${agentName}`);
        const data = await response.json();
        
        document.getElementById('agent-modal-title').textContent = 'Edit Agent';
        document.getElementById('agent-id').value = data.agent.name;
        document.getElementById('agent-name').value = data.agent.name;
        document.getElementById('agent-role').value = data.agent.role;
        document.getElementById('agent-temperature').value = data.agent.temperature;
        document.getElementById('agent-enabled').checked = data.agent.enabled;
        
        document.getElementById('agent-modal').classList.remove('hidden');
        document.getElementById('agent-modal').classList.add('flex');
    } catch (error) {
        console.error('Error loading agent:', error);
        showMessage('Failed to load agent details', 'error');
    }
}

function closeAgentModal() {
    document.getElementById('agent-modal').classList.add('hidden');
    document.getElementById('agent-modal').classList.remove('flex');
}

document.getElementById('agent-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const agentName = document.getElementById('agent-id').value || document.getElementById('agent-name').value;
    const agentData = {
        name: document.getElementById('agent-name').value,
        role: document.getElementById('agent-role').value,
        temperature: parseFloat(document.getElementById('agent-temperature').value),
        enabled: document.getElementById('agent-enabled').checked
    };
    
    try {
        const response = await fetch(`${API_BASE}/settings/agents/${agentName}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(agentData)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('Agent updated successfully', 'success');
            closeAgentModal();
            loadAgents();
        } else {
            showMessage(data.error || 'Failed to save agent', 'error');
        }
    } catch (error) {
        console.error('Error saving agent:', error);
        showMessage('Failed to save agent', 'error');
    }
});

// ===== API KEY POOL =====

async function loadApiKeys() {
    try {
        const response = await fetch(`${API_BASE}/settings/api-keys`);
        const data = await response.json();
        
        const apiKeyList = document.getElementById('api-key-list');
        if (data.keys && data.keys.length > 0) {
            apiKeyList.innerHTML = data.keys.map((key, index) => `
                <div class="flex items-center gap-2 p-3 card">
                    <span class="flex-1 font-mono text-sm">${maskApiKey(key.key)}</span>
                    <span class="text-xs px-2 py-1 rounded ${key.active ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}">
                        ${key.active ? 'Active' : 'Inactive'}
                    </span>
                    <button onclick="removeApiKey(${key.id})" class="btn btn-danger h-8 px-3 text-sm">
                        <svg class="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                    </button>
                </div>
            `).join('');
        } else {
            apiKeyList.innerHTML = '<p class="text-muted-foreground text-sm">No API keys configured.</p>';
        }
    } catch (error) {
        console.error('Error loading API keys:', error);
        showMessage('Failed to load API keys', 'error');
    }
}

function maskApiKey(key) {
    if (!key) return '';
    return key.substring(0, 10) + '...' + key.substring(key.length - 4);
}

async function addApiKey() {
    const keyInput = document.getElementById('new-api-key');
    const apiKey = keyInput.value.trim();
    
    if (!apiKey) {
        showMessage('Please enter an API key', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/settings/api-keys`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('API key added successfully', 'success');
            keyInput.value = '';
            loadApiKeys();
        } else {
            showMessage(data.error || 'Failed to add API key', 'error');
        }
    } catch (error) {
        console.error('Error adding API key:', error);
        showMessage('Failed to add API key', 'error');
    }
}

async function removeApiKey(keyId) {
    if (!confirm('Are you sure you want to remove this API key?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/settings/api-keys/${keyId}`, { method: 'DELETE' });
        const data = await response.json();
        
        if (data.success) {
            showMessage('API key removed successfully', 'success');
            loadApiKeys();
        } else {
            showMessage(data.error || 'Failed to remove API key', 'error');
        }
    } catch (error) {
        console.error('Error removing API key:', error);
        showMessage('Failed to remove API key', 'error');
    }
}

// ===== MODEL SELECTION =====

const GROQ_MODELS = [
    { id: 'llama-3.3-70b-versatile', name: 'Llama 3.3 70B Versatile', description: 'Best overall performance, balanced speed and quality' },
    { id: 'llama-3.1-70b-versatile', name: 'Llama 3.1 70B Versatile', description: 'High-quality responses, versatile use cases' },
    { id: 'llama-3.1-8b-instant', name: 'Llama 3.1 8B Instant', description: 'Fastest responses, good for quick tasks' },
    { id: 'mixtral-8x7b-32768', name: 'Mixtral 8x7B', description: 'Large context window (32K tokens)' },
    { id: 'gemma2-9b-it', name: 'Gemma 2 9B', description: 'Efficient, good for general tasks' }
];

async function loadModels() {
    try {
        const response = await fetch(`${API_BASE}/settings/model`);
        const data = await response.json();
        
        const currentModel = data.model || 'llama-3.3-70b-versatile';
        document.getElementById('current-model').textContent = currentModel;
        
        const modelList = document.getElementById('model-list');
        modelList.innerHTML = GROQ_MODELS.map(model => `
            <div class="card p-4 cursor-pointer hover:border-blue-500/50 transition ${model.id === currentModel ? 'border-blue-500' : ''}" 
                 onclick="selectModel('${model.id}')">
                <div class="flex items-start justify-between">
                    <div class="flex-1">
                        <h3 class="font-semibold">${model.name}</h3>
                        <p class="text-sm text-muted-foreground mt-1">${model.description}</p>
                    </div>
                    ${model.id === currentModel ? `
                        <svg class="w-5 h-5 text-blue-400 flex-shrink-0 ml-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M5 13l4 4L19 7"></path>
                        </svg>
                    ` : ''}
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading models:', error);
        showMessage('Failed to load models', 'error');
    }
}

async function selectModel(modelId) {
    try {
        const response = await fetch(`${API_BASE}/settings/model`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model: modelId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('Model updated successfully', 'success');
            loadModels();
        } else {
            showMessage(data.error || 'Failed to update model', 'error');
        }
    } catch (error) {
        console.error('Error updating model:', error);
        showMessage('Failed to update model', 'error');
    }
}

// ===== UTILITY FUNCTIONS =====

function showMessage(message, type = 'info') {
    const colors = {
        success: 'bg-green-500',
        error: 'bg-red-500',
        warning: 'bg-yellow-500',
        info: 'bg-blue-500'
    };
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `fixed top-4 right-4 ${colors[type]} text-white px-6 py-3 rounded-lg shadow-lg z-50 transition-all`;
    messageDiv.textContent = message;
    
    document.body.appendChild(messageDiv);
    
    setTimeout(() => {
        messageDiv.style.opacity = '0';
        setTimeout(() => messageDiv.remove(), 300);
    }, 3000);
}

// Load initial data
document.addEventListener('DOMContentLoaded', () => {
    loadBrands();
});
