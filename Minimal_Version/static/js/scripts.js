// API Base URL
const API_BASE = window.location.origin + '/api';

// ========================================
// Cookie Utility Functions
// ========================================

function setCookie(name, value, days = 30) {
    const expires = new Date();
    expires.setTime(expires.getTime() + (days * 24 * 60 * 60 * 1000));
    document.cookie = `${name}=${encodeURIComponent(value)};expires=${expires.toUTCString()};path=/`;
}

function getCookie(name) {
    const nameEQ = name + "=";
    const ca = document.cookie.split(';');
    for(let i = 0; i < ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') c = c.substring(1, c.length);
        if (c.indexOf(nameEQ) === 0) return decodeURIComponent(c.substring(nameEQ.length, c.length));
    }
    return null;
}

function saveFormDataToCookies(formId, data) {
    setCookie(`form_${formId}`, JSON.stringify(data));
}

function loadFormDataFromCookies(formId) {
    const data = getCookie(`form_${formId}`);
    return data ? JSON.parse(data) : null;
}

function clearFormCookie(formId) {
    document.cookie = `form_${formId}=;expires=Thu, 01 Jan 1970 00:00:00 UTC;path=/;`;
}

function populateFormFromCookies(formId) {
    const savedData = loadFormDataFromCookies(formId);
    if (!savedData) return false;
    
    const form = document.getElementById(formId);
    if (!form) return false;
    
    Object.keys(savedData).forEach(key => {
        const field = form.querySelector(`[name="${key}"]`);
        if (field) {
            field.value = savedData[key];
            // Trigger change event for any listeners
            field.dispatchEvent(new Event('change', { bubbles: true }));
        }
    });
    
    return true;
}

// ========================================
// Utility Functions
// ========================================

function showMessage(message, type = 'success') {
    const statusDiv = document.getElementById('status-message');
    if (!statusDiv) return;
    
    const styles = {
        success: 'border-green-500/50 bg-green-500/10 text-green-500',
        error: 'border-destructive/50 bg-destructive/10 text-destructive',
        warning: 'border-yellow-500/50 bg-yellow-500/10 text-yellow-500',
        info: 'border-blue-500/50 bg-blue-500/10 text-blue-500'
    };
    
    const icons = {
        success: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>',
        error: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>',
        warning: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path></svg>',
        info: '<svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>'
    };
    
    // Convert newlines to <br> for multi-line messages
    const formattedMessage = message.replace(/\\n/g, '<br>');
    
    statusDiv.innerHTML = `
        <div class="rounded-lg border ${styles[type]} p-4">
            <div class="flex items-start gap-3">
                <span class="flex-shrink-0">${icons[type]}</span>
                <div class="text-sm font-medium flex-1">${formattedMessage}</div>
            </div>
        </div>
    `;
    statusDiv.classList.remove('hidden');
    
    // Auto-hide after 8 seconds for errors (more time to read), 5 seconds for success
    setTimeout(() => {
        statusDiv.classList.add('hidden');
    }, type === 'error' ? 8000 : 5000);
}

function showLoadingModal(show = true) {
    const modal = document.getElementById('loading-modal');
    if (modal) {
        if (show) {
            modal.classList.remove('hidden');
        } else {
            modal.classList.add('hidden');
        }
    }
}

function updateLoadingStatus(message, agentStatuses = null) {
    const statusEl = document.getElementById('loading-status');
    if (statusEl) {
        statusEl.textContent = message;
    }
    
    const currentActivityEl = document.getElementById('current-activity');
    if (currentActivityEl) {
        currentActivityEl.textContent = message;
    }
    
    if (agentStatuses) {
        const agentStatusEl = document.getElementById('agent-status');
        if (agentStatusEl) {
            agentStatusEl.innerHTML = agentStatuses.map(status => `
                <div class="flex items-center">
                    <span class="text-${status.done ? 'green' : 'yellow'}-400 mr-2 w-4 h-4">
                        ${status.done ? 
                            '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>' : 
                            '<svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10" stroke-dasharray="4 2"></circle></svg>'
                        }
                    </span>
                    <span class="text-gray-300">${status.name}</span>
                </div>
            `).join('');
        }
    }
}

function updateApiKeyStatus(keyName, isRotation = false) {
    const apiKeyStatusEl = document.getElementById('api-key-status');
    if (!apiKeyStatusEl) return;
    
    if (isRotation) {
        apiKeyStatusEl.innerHTML = `
            <span class="text-yellow-400">⚠️ Rotating to: ${keyName}</span>
        `;
        // Add to conversation log
        addDebateMessage('SYSTEM', 'API Key Rotation', `Switched to API key: ${keyName}`, 'warning');
    } else {
        apiKeyStatusEl.innerHTML = `
            <span class="text-green-400">✓ Using: ${keyName}</span>
        `;
    }
}

function addDebateMessage(agentName, messageType, content, style = 'default') {
    const conversationEl = document.getElementById('debate-conversation');
    if (!conversationEl) return;
    
    // Remove "waiting" message on first real message
    const waitingMsg = conversationEl.querySelector('.italic');
    if (waitingMsg) {
        conversationEl.innerHTML = '';
    }
    
    const agentColors = {
        'TrendAgent': 'text-blue-400 border-blue-500/30 bg-blue-500/5',
        'BrandAgent': 'text-purple-400 border-purple-500/30 bg-purple-500/5',
        'ComplianceAgent': 'text-yellow-400 border-yellow-500/30 bg-yellow-500/5',
        'RiskAgent': 'text-red-400 border-red-500/30 bg-red-500/5',
        'EngagementAgent': 'text-green-400 border-green-500/30 bg-green-500/5',
        'CMOAgent': 'text-indigo-400 border-indigo-500/30 bg-indigo-500/5',
        'SYSTEM': 'text-gray-400 border-gray-500/30 bg-gray-500/5'
    };
    
    const colorClass = agentColors[agentName] || 'text-gray-400 border-border bg-muted/50';
    
    const messageEl = document.createElement('div');
    messageEl.className = `rounded-lg border p-3 ${colorClass} text-sm`;
    messageEl.innerHTML = `
        <div class="flex items-start gap-2">
            <span class="font-semibold flex-shrink-0">${agentName}:</span>
            <div class="flex-1">
                <div class="font-medium mb-1">${messageType}</div>
                <div class="text-xs text-muted-foreground whitespace-pre-wrap">${content}</div>
            </div>
        </div>
    `;
    
    conversationEl.appendChild(messageEl);
    // Auto-scroll to bottom
    conversationEl.scrollTop = conversationEl.scrollHeight;
}

// All fake simulation code removed - using real backend data only

// ========================================
// Brand Management Functions
// ========================================

async function loadBrands() {
    try {
        const response = await fetch(`${API_BASE}/brands`);
        const data = await response.json();
        
        if (data.success) {
            displayBrands(data.brands);
        } else {
            showMessage('Failed to load brands', 'error');
        }
    } catch (error) {
        console.error('Error loading brands:', error);
        showMessage('Error loading brands', 'error');
    }
}

function displayBrands(brands) {
    const brandsList = document.getElementById('brands-list');
    if (!brandsList) return;
    
    if (brands.length === 0) {
        brandsList.innerHTML = '<p class="text-muted-foreground">No brands configured yet. Create one below.</p>';
        return;
    }
    
    brandsList.innerHTML = brands.map(brand => `
        <div class="rounded-lg border border-border bg-card p-4 hover:bg-accent transition-colors">
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div class="flex-1">
                    <h4 class="font-semibold text-lg mb-1">${brand.brand_name}</h4>
                    <p class="text-sm text-muted-foreground mb-3">${brand.brand_description}</p>
                    <div class="flex flex-wrap gap-2">
                        <span class="badge badge-default">${brand.brand_tone}</span>
                        <span class="badge badge-outline">${brand.target_audience}</span>
                    </div>
                </div>
                <button onclick="selectBrandForPosting(${brand.id})" 
                    class="btn btn-primary h-9 px-4 shrink-0">
                    Create Post
                </button>
            </div>
        </div>
    `).join('');
}

function selectBrandForPosting(brandId) {
    window.location.href = `/create-post?brand=${brandId}`;
}

function setupBrandForm() {
    const form = document.getElementById('brand-form');
    if (!form) return;
    
    // Load saved form data from cookies
    const savedData = populateFormFromCookies('brand-form');
    if (savedData) {
        showMessage('Previous form data restored', 'info');
    }
    
    // Save form data on input change
    form.addEventListener('input', (e) => {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        saveFormDataToCookies('brand-form', data);
    });
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const formData = new FormData(form);
        const brandData = Object.fromEntries(formData.entries());
        
        try {
            const submitBtn = document.getElementById('submit-btn');
            submitBtn.disabled = true;
            submitBtn.textContent = 'Creating...';
            
            const response = await fetch(`${API_BASE}/brands`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(brandData)
            });
            
            const data = await response.json();
            
            if (data.success) {
                showMessage('Brand created successfully!', 'success');
                form.reset();
                clearFormCookie('brand-form'); // Clear saved data after successful submission
                loadBrands();
            } else {
                showMessage(data.error || 'Failed to create brand', 'error');
            }
        } catch (error) {
            console.error('Error creating brand:', error);
            showMessage('Error creating brand', 'error');
        } finally {
            const submitBtn = document.getElementById('submit-btn');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Create Brand Configuration';
        }
    });
}

// ========================================
// Post Creation Functions
// ========================================

async function loadBrandsForPostCreation() {
    try {
        const response = await fetch(`${API_BASE}/brands`);
        const data = await response.json();
        
        if (data.success) {
            populateBrandSelector(data.brands);
            
            // Check if brand ID in URL
            const urlParams = new URLSearchParams(window.location.search);
            const brandId = urlParams.get('brand');
            if (brandId) {
                document.getElementById('selected_brand').value = brandId;
                showBrandInfo(brandId, data.brands);
            }
        }
    } catch (error) {
        console.error('Error loading brands:', error);
    }
}

function populateBrandSelector(brands) {
    const selector = document.getElementById('selected_brand');
    if (!selector) return;
    
    if (brands.length === 0) {
        selector.innerHTML = '<option value="">No brands available - create one first</option>';
        return;
    }
    
    selector.innerHTML = '<option value="">Select a brand...</option>' +
        brands.map(brand => `
            <option value="${brand.id}">${brand.brand_name}</option>
        `).join('');
    
    selector.addEventListener('change', (e) => {
        showBrandInfo(e.target.value, brands);
    });
}

function showBrandInfo(brandId, brands) {
    const brand = brands.find(b => b.id == brandId);
    const infoDiv = document.getElementById('brand-info');
    
    if (!brand || !infoDiv) return;
    
    document.getElementById('info-tone').textContent = brand.brand_tone;
    document.getElementById('info-audience').textContent = brand.target_audience;
    document.getElementById('info-platforms').textContent = brand.social_platforms;
    document.getElementById('info-segment').textContent = brand.market_segment;
    
    infoDiv.classList.remove('hidden');
}

function setupPostForm() {
    const form = document.getElementById('post-form');
    if (!form) return;
    
    // Load saved form data from cookies
    const savedData = populateFormFromCookies('post-form');
    if (savedData) {
        showMessage('Previous form data restored', 'info');
    }
    
    // Save form data on input change
    form.addEventListener('input', (e) => {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        saveFormDataToCookies('post-form', data);
    });
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const brandId = document.getElementById('selected_brand').value;
        if (!brandId) {
            showMessage('Please select a brand first', 'warning');
            return;
        }
        
        const formData = new FormData(form);
        const postData = Object.fromEntries(formData.entries());
        postData.brand_id = parseInt(brandId);
        
        try {
            const submitBtn = document.getElementById('submit-btn');
            submitBtn.disabled = true;
            
            showLoadingModal(true);
            
            // DO NOT start fake debate simulation - we'll use real updates
            // simulateDebateProgress(50000); // REMOVED
            
            // Start polling for live debate updates
            let debatePollingInterval = null;
            let lastMessageIndex = 0;
            
            function pollDebateUpdates(postId) {
                debatePollingInterval = setInterval(async () => {
                    try {
                        const response = await fetch(`${API_BASE}/debates/${postId}/live-progress`);
                        const data = await response.json();
                        
                        console.log('Polling response:', data); // DEBUG
                        
                        if (data.success && data.messages) {
                            console.log(`Total messages: ${data.messages.length}, Last index: ${lastMessageIndex}`); // DEBUG
                            // Display new messages
                            const newMessages = data.messages.slice(lastMessageIndex);
                            console.log('New messages:', newMessages); // DEBUG
                            newMessages.forEach(msg => {
                                displayLiveMessage(msg);
                            });
                            lastMessageIndex = data.messages.length;
                            
                            // Update progress based on message count (approximate)
                            const progress = Math.min((lastMessageIndex / 20) * 100, 95);
                            const progressBar = document.getElementById('progress-bar');
                            if (progressBar) {
                                progressBar.style.width = `${progress}%`;
                            }
                            
                            // Stop polling if complete
                            if (data.status === 'complete') {
                                clearInterval(debatePollingInterval);
                                if (progressBar) {
                                    progressBar.style.width = '100%';
                                }
                            }
                        }
                    } catch (error) {
                        console.error('Error polling debate updates:', error);
                    }
                }, 1000); // Poll every 1 second for real-time feel
            }
            
            function displayLiveMessage(msg) {
                const agent = msg.agent;
                const type = msg.type;
                const content = msg.content;
                
                // Map agent names to card keys
                const agentKeyMap = {
                    'TrendAgent': 'trend',
                    'BrandAgent': 'brand',
                    'ComplianceAgent': 'compliance',
                    'RiskAgent': 'risk',
                    'EngagementAgent': 'engagement',
                    'CMOAgent': 'cmo',
                    'CMO': 'cmo'
                };
                
                const agentKey = agentKeyMap[agent];
                
                // Update agent card status in real-time
                if (agentKey) {
                    const cardEl = document.getElementById(`agent-card-${agentKey}`);
                    const thinkingEl = document.getElementById(`agent-thinking-${agentKey}`);
                    const statusEl = document.getElementById(`agent-status-${agentKey}`);
                    
                    // Activate card (remove waiting state)
                    if (cardEl) {
                        cardEl.classList.remove('opacity-50');
                        cardEl.classList.add('ring-2', 'ring-primary');
                    }
                    
                    // Update status icon to show activity
                    if (statusEl) {
                        statusEl.innerHTML = '<svg class="w-4 h-4 text-blue-400 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v4m0 12v4M4.93 4.93l2.83 2.83m8.48 8.48l2.83 2.83M2 12h4m12 0h4M4.93 19.07l2.83-2.83m8.48-8.48l2.83-2.83"></path></svg>';
                    }
                    
                    // Update thinking text with actual content
                    if (thinkingEl) {
                        thinkingEl.textContent = content.substring(0, 100) + (content.length > 100 ? '...' : '');
                        thinkingEl.classList.remove('italic');
                        thinkingEl.classList.add('text-foreground');
                    }
                }
                
                // Update current activity
                updateLoadingStatus(`${agent}: ${content.substring(0, 50)}...`);
                
                // Add to conversation log
                if (type === 'thinking') {
                    addDebateMessage(agent, 'Thinking', content);
                } else if (type === 'reaction') {
                    addDebateMessage(agent, 'Initial Reaction', content);
                    if (msg.reasoning) {
                        addDebateMessage(agent, 'Reasoning', msg.reasoning);
                    }
                } else if (type === 'message') {
                    // Show vote with full explanation
                    const voteLabel = msg.vote ? msg.vote.toUpperCase() : 'UNKNOWN';
                    const argument = msg.argument || content || 'No argument provided';
                    const reasoning = msg.reasoning || '';
                    
                    // Combine vote, argument and reasoning into one clear message
                    let fullMessage = `📋 VOTE: ${voteLabel}\n\n`;
                    fullMessage += `💭 ${argument}`;
                    if (reasoning) {
                        fullMessage += `\n\n🔍 WHY: ${reasoning}`;
                    }
                    
                    addDebateMessage(agent, 'Decision', fullMessage);
                    
                    // Mark agent as complete when they finish speaking
                    if (agentKey && msg.vote) {
                        const cardEl = document.getElementById(`agent-card-${agentKey}`);
                        const statusEl = document.getElementById(`agent-status-${agentKey}`);
                        const thinkingEl = document.getElementById(`agent-thinking-${agentKey}`);
                        
                        if (statusEl) {
                            statusEl.innerHTML = '<svg class="w-4 h-4 text-green-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"></path></svg>';
                        }
                        
                        if (cardEl) {
                            cardEl.classList.remove('ring-primary');
                            cardEl.classList.add('border-green-500/50');
                        }
                        
                        if (thinkingEl) {
                            thinkingEl.textContent = `Vote: ${msg.vote} - Analysis complete!`;
                            thinkingEl.classList.add('text-green-500', 'font-medium');
                        }
                    }
                }
            }
            
            // Create post input
            const createResponse = await fetch(`${API_BASE}/post-inputs`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(postData)
            });
            
            const createData = await createResponse.json();
            
            if (!createData.success) {
                throw new Error(createData.error || 'Failed to create post input');
            }
            
            const postInputId = createData.post_input_id;
            
            // Start polling for LIVE debate updates immediately
            pollDebateUpdates(postInputId);
            
            // Update modal to show API key check
            updateLoadingStatus('Checking API keys...');
            
            // Fetch and display current API key IMMEDIATELY
            try {
                const apiKeyResponse = await fetch(`${API_BASE}/debates/current-api-key`);
                const apiKeyData = await apiKeyResponse.json();
                if (apiKeyData.success && apiKeyData.api_key_name) {
                    console.log('🔑 Current API Key:', apiKeyData.api_key_name);
                    updateApiKeyStatus(apiKeyData.api_key_name, false);
                    updateLoadingStatus('Using API Key: ' + apiKeyData.api_key_name);
                    // Add to conversation log
                    addDebateMessage('SYSTEM', 'API Key Selected', `Using: ${apiKeyData.api_key_name}`);
                } else {
                    updateApiKeyStatus('No active key', false);
                    addDebateMessage('SYSTEM', 'Warning', 'No active API key found');
                }
            } catch (error) {
                console.warn('Could not fetch current API key:', error);
                updateApiKeyStatus('Checking...', false);
            }
            
            // Start debate process
            updateLoadingStatus('Starting debate process...');
            addDebateMessage('SYSTEM', 'Debate Starting', 'Initializing 6-agent council debate...');
            
            const debateResponse = await fetch(`${API_BASE}/debates/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ post_input_id: postInputId })
            });
            
            const debateData = await debateResponse.json();
            
            // Stop polling - debate is complete
            if (debatePollingInterval) {
                clearInterval(debatePollingInterval);
            }
            
            // Debug logging
            console.log('📥 Received debate response:', debateData);
            console.log('API Key Name:', debateData.api_key_name);
            console.log('Conversation Log Length:', debateData.conversation_log ? debateData.conversation_log.length : 0);
            
            if (debateData.success) {
                // Keep modal open to display final results
                updateLoadingStatus('Debate Complete! ✅');
                
                // Update progress bar to 100%
                const progressBar = document.getElementById('progress-bar');
                if (progressBar) {
                    progressBar.style.width = '100%';
                }
                
                // Display API key that was used
                if (debateData.api_key_name) {
                    console.log('Displaying API key:', debateData.api_key_name);
                    updateApiKeyStatus(debateData.api_key_name, false);
                }
                
                // Display conversation log
                if (debateData.conversation_log && debateData.conversation_log.length > 0) {
                    console.log('Displaying conversation log:', debateData.conversation_log.length, 'messages');
                    debateData.conversation_log.forEach(msg => {
                        if (msg.type === 'system') {
                            addDebateMessage(msg.agent, 'system', msg.message);
                        } else if (msg.type === 'phase') {
                            addDebateMessage(msg.agent, 'phase', msg.message);
                        } else if (msg.type === 'thinking') {
                            addDebateMessage(msg.agent, 'thinking', msg.message);
                        } else if (msg.type === 'reaction') {
                            addDebateMessage(msg.agent, 'reaction', msg.message);
                        } else if (msg.type === 'speaking') {
                            addDebateMessage(msg.agent, 'speaking', msg.message);
                        } else if (msg.type === 'message') {
                            addDebateMessage(msg.agent, 'message', msg.message, msg.vote);
                        } else if (msg.type === 'decision') {
                            addDebateMessage(msg.agent, 'decision', msg.message);
                        }
                    });
                } else {
                    console.warn('No conversation log received from backend');
                }
                
                // Clear form cookie after successful submission
                clearFormCookie('post-form');
                
                // Wait to show completion, then close modal and redirect
                setTimeout(() => {
                    showLoadingModal(false);
                    window.location.href = `/debate/${postInputId}`;
                }, 3000);
            } else {
                showLoadingModal(false);
                // Check if it's a rate limit error
                if (debateData.error_type === 'rate_limit' || debateResponse.status === 429) {
                    const rateLimitMsg = debateData.message || '🚫 API Rate Limit Exceeded\n\nGroq API has reached its daily token limit (100,000 tokens).\n\nPlease wait 20-30 minutes and try again, or upgrade your Groq plan.';
                    throw new Error(rateLimitMsg);
                }
                throw new Error(debateData.error || 'Debate process failed');
            }
            
        } catch (error) {
            console.error('Error:', error);
            showLoadingModal(false);
            showMessage(error.message || 'Error processing post', 'error');
            const submitBtn = document.getElementById('submit-btn');
            submitBtn.disabled = false;
        }
    });
}

// ========================================
// Debate Viewer Functions
// ========================================

async function loadDebateData(postInputId) {
    try {
        // Load post input context
        const postResponse = await fetch(`${API_BASE}/post-inputs/${postInputId}`);
        const postData = await postResponse.json();
        
        if (postData.success) {
            displayPostContext(postData.post_input);
        }
        
        // Load debates
        const debateResponse = await fetch(`${API_BASE}/debates/${postInputId}`);
        const debateData = await debateResponse.json();
        
        if (debateData.success) {
            displayDebates(debateData.debates, postInputId);
        }
        
    } catch (error) {
        console.error('Error loading debate data:', error);
        showMessage('Error loading debate data', 'error');
    }
}

function displayPostContext(postInput) {
    document.getElementById('ctx-topic').textContent = postInput.post_topic;
    document.getElementById('ctx-platform').textContent = postInput.target_platform;
    document.getElementById('ctx-objective').textContent = postInput.post_objective;
    document.getElementById('ctx-type').textContent = postInput.content_type;
}

function displayDebates(debates, postInputId) {
    const container = document.getElementById('debates-container');
    if (!container) return;
    
    if (debates.length === 0) {
        container.innerHTML = '<p class="text-gray-400">No debates found.</p>';
        return;
    }
    
    // Group by agent
    const agentOrder = ['TrendAgent', 'BrandAgent', 'ComplianceAgent', 'RiskAgent', 'EngagementAgent', 'CMOAgent'];
    const groupedDebates = {};
    
    debates.forEach(debate => {
        if (!groupedDebates[debate.agent_name]) {
            groupedDebates[debate.agent_name] = debate;
        }
    });
    
    container.innerHTML = agentOrder
        .filter(agentName => groupedDebates[agentName])
        .map(agentName => {
            const debate = groupedDebates[agentName];
            return renderDebateCard(debate);
        }).join('');
    
    // Check if CMO is present and show results button
    if (groupedDebates['CMOAgent']) {
        const resultsBtn = document.getElementById('view-results-btn');
        if (resultsBtn) {
            resultsBtn.classList.remove('hidden');
            resultsBtn.onclick = () => {
                window.location.href = `/results/${postInputId}`;
            };
        }
        
        // Show CMO decision
        displayCMODecision(groupedDebates['CMOAgent']);
    }
}

function renderDebateCard(debate) {
    const voteStyles = {
        approve: { 
            badge: 'border-green-500/50 bg-green-500/10 text-green-500',
            score: 'text-green-500'
        },
        conditional: { 
            badge: 'border-yellow-500/50 bg-yellow-500/10 text-yellow-500',
            score: 'text-yellow-500'
        },
        reject: { 
            badge: 'border-red-500/50 bg-red-500/10 text-red-500',
            score: 'text-red-500'
        }
    };
    
    const style = voteStyles[debate.vote] || { 
        badge: 'border-border bg-muted text-foreground',
        score: 'text-foreground'
    };
    
    const agentIcons = {
        'TrendAgent': '<svg class="w-5 h-5 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>',
        'BrandAgent': '<svg class="w-5 h-5 text-purple-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="13.5" cy="6.5" r=".5"></circle><circle cx="17.5" cy="10.5" r=".5"></circle><circle cx="8.5" cy="7.5" r=".5"></circle><circle cx="6.5" cy="12.5" r=".5"></circle><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"></path></svg>',
        'ComplianceAgent': '<svg class="w-5 h-5 text-yellow-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 3v18M3 12h18M5.6 5.6l12.8 12.8M5.6 18.4L18.4 5.6"></path></svg>',
        'RiskAgent': '<svg class="w-5 h-5 text-red-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>',
        'EngagementAgent': '<svg class="w-5 h-5 text-green-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>',
        'CMOAgent': '<svg class="w-5 h-5 text-indigo-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>'
    };
    
    const icon = agentIcons[debate.agent_name] || '<svg class="w-5 h-5 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line></svg>';
    
    return `
        <div class="card p-6">
            <div class="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4 mb-4">
                <div>
                    <h4 class="text-xl font-semibold flex items-center gap-2">
                        <span>${icon}</span>
                        <span>${debate.agent_name}</span>
                    </h4>
                    <p class="text-sm text-muted-foreground mt-1">${debate.agent_role}</p>
                </div>
                <div class="flex items-center gap-3">
                    <div class="text-2xl font-bold ${style.score}">${debate.score || 'N/A'}</div>
                    <div class="rounded-md border ${style.badge} px-2.5 py-0.5 text-xs font-semibold uppercase">
                        ${debate.vote}
                    </div>
                </div>
            </div>
            
            <div class="space-y-4 text-sm">
                <div>
                    <span class="font-medium text-muted-foreground">Recommendation:</span>
                    <p class="mt-2 leading-relaxed">${debate.recommendation || 'No recommendation provided'}</p>
                </div>
                
                <div>
                    <span class="font-medium text-muted-foreground">Reasoning:</span>
                    <p class="mt-2 text-muted-foreground leading-relaxed whitespace-pre-line">${debate.reasoning || 'No detailed reasoning provided'}</p>
                </div>
                
                ${debate.concerns ? `
                <div>
                    <span class="font-medium text-muted-foreground">Concerns:</span>
                    <p class="mt-2 text-yellow-500 leading-relaxed">${debate.concerns}</p>
                </div>
                ` : ''}
            </div>
        </div>
    `;
}

function displayCMODecision(cmoDebate) {
    const container = document.getElementById('cmo-decision-container');
    if (!container) return;
    
    const voteStyles = {
        approve: { 
            border: 'border-green-500/50',
            bg: 'bg-green-500/10',
            text: 'text-green-500',
            title: 'Success! Post Approved'
        },
        conditional: { 
            border: 'border-yellow-500/50',
            bg: 'bg-yellow-500/10',
            text: 'text-yellow-500',
            title: 'Conditional Approval'
        },
        reject: { 
            border: 'border-red-500/50',
            bg: 'bg-red-500/10',
            text: 'text-red-500',
            title: 'Rejected'
        }
    };
    
    const style = voteStyles[cmoDebate.vote] || {
        border: 'border-border',
        bg: 'bg-muted/50',
        text: 'text-foreground',
        title: 'Unknown'
    };
    
    container.innerHTML = `
        <div class="rounded-lg border-2 ${style.border} ${style.bg} p-6">
            <h3 class="text-2xl font-bold ${style.text} mb-4 flex items-center gap-2">
                <svg class="w-6 h-6 text-indigo-400 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>
                <span>CMO Final Decision: ${style.title}</span>
            </h3>
            <div class="space-y-4 text-sm">
                <div>
                    <span class="font-medium text-muted-foreground">Recommendation:</span>
                    <p class="mt-2 leading-relaxed">${cmoDebate.recommendation || 'No recommendation provided'}</p>
                </div>
                <div>
                    <span class="font-medium text-muted-foreground">Reasoning:</span>
                    <p class="mt-2 text-muted-foreground leading-relaxed whitespace-pre-line">${cmoDebate.reasoning || 'No detailed reasoning provided'}</p>
                </div>
                <div class="flex items-center justify-between pt-2 border-t border-border">
                    <span class="text-sm text-muted-foreground">Confidence Score: ${cmoDebate.score}%</span>
                </div>
            </div>
        </div>
    `;
}

// ========================================
// Results Viewer Functions
// ========================================

async function loadGeneratedPosts(postInputId) {
    try {
        const response = await fetch(`${API_BASE}/generated-posts/${postInputId}`);
        const data = await response.json();
        
        if (data.success) {
            if (data.posts.length > 0) {
                displayGeneratedPosts(data.posts);
            } else {
                document.getElementById('posts-container').classList.add('hidden');
                document.getElementById('no-posts').classList.remove('hidden');
            }
        } else {
            showMessage('Error loading posts', 'error');
        }
    } catch (error) {
        console.error('Error loading generated posts:', error);
        showMessage('Error loading posts', 'error');
    }
}

function displayGeneratedPosts(posts) {
    const container = document.getElementById('posts-container');
    if (!container) return;
    
    container.innerHTML = posts.map((post, index) => `
        <div class="card overflow-hidden hover:border-primary transition-colors">
            <div class="bg-gradient-to-r from-primary/10 to-accent/10 border-b border-border p-4">
                <div class="flex items-center justify-between">
                    <h3 class="text-xl font-bold">Option ${post.variation_number}</h3>
                    <div class="rounded-full bg-primary/20 px-3 py-1">
                        <span class="text-sm font-semibold">${post.final_score?.toFixed(0) || 'N/A'}%</span>
                    </div>
                </div>
            </div>
            
            <div class="p-6 space-y-4">
                <div>
                    <h4 class="text-sm font-medium text-muted-foreground mb-2">Title</h4>
                    <p class="font-semibold">${post.post_title}</p>
                </div>
                
                <div>
                    <h4 class="text-sm font-medium text-muted-foreground mb-2">Content</h4>
                    <p class="text-sm text-muted-foreground line-clamp-4">${post.post_content.substring(0, 150)}${post.post_content.length > 150 ? '...' : ''}</p>
                </div>
                
                <div>
                    <h4 class="text-sm font-medium text-muted-foreground mb-2">Hashtags</h4>
                    <p class="text-sm text-primary">${post.hashtags}</p>
                </div>
                
                <button onclick="viewPostDetail(${index})" 
                    class="btn btn-primary w-full h-10">
                    View Full Details
                </button>
            </div>
        </div>
    `).join('');
    
    // Store posts globally for modal access
    window.generatedPosts = posts;
}

function viewPostDetail(index) {
    const post = window.generatedPosts[index];
    if (!post) return;
    
    const modal = document.getElementById('post-modal');
    const modalTitle = document.getElementById('modal-title');
    const modalContent = document.getElementById('modal-content');
    
    modalTitle.textContent = `Post Option ${post.variation_number} - Full Details`;
    
    modalContent.innerHTML = `
        <div class="space-y-6">
            <div>
                <h4 class="text-lg font-semibold text-primary mb-2 flex items-center gap-2">
                    <svg class="w-5 h-5 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                    <span>Title</span>
                </h4>
                <p class="text-lg font-semibold">${post.post_title}</p>
            </div>
            
            <div>
                <h4 class="text-lg font-semibold text-primary mb-2 flex items-center gap-2">
                    <svg class="w-5 h-5 text-gray-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
                    <span>Full Content</span>
                </h4>
                <div class="rounded-lg border border-border bg-muted/50 p-4 whitespace-pre-wrap text-sm">${post.post_content}</div>
            </div>
            
            <div>
                <h4 class="text-lg font-semibold text-primary mb-2 flex items-center gap-2">
                    <svg class="w-5 h-5 text-blue-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="4" y1="9" x2="20" y2="9"></line><line x1="4" y1="15" x2="20" y2="15"></line><line x1="10" y1="3" x2="8" y2="21"></line><line x1="16" y1="3" x2="14" y2="21"></line></svg>
                    <span>Hashtags</span>
                </h4>
                <p class="text-primary">${post.hashtags}</p>
            </div>
            
            <div>
                <h4 class="text-lg font-semibold text-primary mb-2 flex items-center gap-2">
                    <svg class="w-5 h-5 text-purple-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="13.5" cy="6.5" r=".5"></circle><circle cx="17.5" cy="10.5" r=".5"></circle><circle cx="8.5" cy="7.5" r=".5"></circle><circle cx="6.5" cy="12.5" r=".5"></circle><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10c.926 0 1.648-.746 1.648-1.688 0-.437-.18-.835-.437-1.125-.29-.289-.438-.652-.438-1.125a1.64 1.64 0 0 1 1.668-1.668h1.996c3.051 0 5.555-2.503 5.555-5.554C21.965 6.012 17.461 2 12 2z"></path></svg>
                    <span>Image Generation Prompt</span>
                </h4>
                <div class="rounded-lg border border-border bg-muted/50 p-4 text-sm">${post.image_prompt}</div>
            </div>
            
            ${post.story_image_prompt ? `
            <div>
                <h4 class="text-lg font-semibold text-primary mb-2 flex items-center gap-2">
                    <svg class="w-5 h-5 text-pink-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"></path><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"></path></svg>
                    <span>Story-Based Image Prompt</span>
                </h4>
                <div class="rounded-lg border border-border bg-muted/50 p-4 text-sm">${post.story_image_prompt}</div>
            </div>
            ` : ''}
            
            ${post.reel_script ? `
            <div>
                <div class="flex items-center justify-between mb-2">
                    <h4 class="text-lg font-semibold text-primary flex items-center gap-2">
                        <svg class="w-5 h-5 text-red-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"></polygon><rect x="1" y="5" width="15" height="14" rx="2" ry="2"></rect></svg>
                        <span>Reel/Video Script</span>
                    </h4>
                    <button onclick="readScript(${index})" id="read-script-btn-${index}"
                        class="btn btn-secondary h-9 px-4 flex items-center gap-2">
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
                            <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
                            <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
                        </svg>
                        <span id="read-script-text-${index}">Read Script</span>
                    </button>
                </div>
                <div class="rounded-lg border border-border bg-muted/50 p-6 text-sm">
                    ${formatReelScript(post.reel_script)}
                </div>
            </div>
            ` : ''}
            
            <div class="flex items-center justify-between pt-4 border-t border-border">
                <span class="text-sm text-muted-foreground">Variation ${post.variation_number} | Score: ${post.final_score?.toFixed(0) || 'N/A'}%</span>
                <div class="flex gap-2">
                    <button onclick="savePost(${post.id})" 
                        class="btn btn-primary h-9 px-4 flex items-center gap-2">
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
                        <span>Save Post</span>
                    </button>
                    <button onclick="copyToClipboard(${index})" 
                        class="btn btn-secondary h-9 px-4 flex items-center gap-2">
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                        <span>Copy Content</span>
                    </button>
                </div>
            </div>
        </div>
    `;
    
    modal.classList.remove('hidden');
}

function copyToClipboard(index) {
    const post = window.generatedPosts[index];
    if (!post) return;
    
    const textToCopy = `${post.post_title}\n\n${post.post_content}\n\n${post.hashtags}`;
    
    navigator.clipboard.writeText(textToCopy).then(() => {
        showMessage('Post content copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showMessage('Failed to copy to clipboard', 'error');
    });
}

// Format reel script for better readability
function formatReelScript(script) {
    if (!script) return '';
    
    // Split by lines and format each section
    const lines = script.split('\n');
    let formatted = '<div class="space-y-4">';
    
    lines.forEach(line => {
        line = line.trim();
        if (!line) return;
        
        // Check if line has timestamp [0:00-0:05]
        const timestampMatch = line.match(/^\[([^\]]+)\]/);
        
        if (timestampMatch) {
            const timestamp = timestampMatch[1];
            const content = line.replace(/^\[([^\]]+)\]\s*/, '');
            
            // Extract label (HOOK, PROBLEM, etc.) if present
            const labelMatch = content.match(/^([A-Z\s]+):\s*/);
            if (labelMatch) {
                const label = labelMatch[1];
                const text = content.replace(/^([A-Z\s]+):\s*/, '');
                
                formatted += `
                    <div class="flex gap-3 items-start">
                        <div class="flex-shrink-0 w-24 text-xs font-mono text-blue-400 bg-blue-500/10 px-2 py-1 rounded">${timestamp}</div>
                        <div class="flex-1">
                            <div class="font-semibold text-primary mb-1">${label}</div>
                            <div class="text-muted-foreground">${text}</div>
                        </div>
                    </div>
                `;
            } else {
                formatted += `
                    <div class="flex gap-3 items-start">
                        <div class="flex-shrink-0 w-24 text-xs font-mono text-blue-400 bg-blue-500/10 px-2 py-1 rounded">${timestamp}</div>
                        <div class="flex-1 text-muted-foreground">${content}</div>
                    </div>
                `;
            }
        } else {
            // Line without timestamp
            formatted += `<div class="text-muted-foreground pl-28">${line}</div>`;
        }
    });
    
    formatted += '</div>';
    return formatted;
}

// Text-to-Speech for script reading
let currentSpeech = null;
let isReading = false;

function readScript(index) {
    const post = window.generatedPosts[index];
    if (!post || !post.reel_script) {
        showMessage('No script available to read', 'warning');
        return;
    }
    
    const button = document.getElementById(`read-script-btn-${index}`);
    const buttonText = document.getElementById(`read-script-text-${index}`);
    
    // Check if browser supports Speech Synthesis
    if (!('speechSynthesis' in window)) {
        showMessage('Text-to-speech not supported in this browser', 'error');
        return;
    }
    
    // If already reading, stop
    if (isReading) {
        window.speechSynthesis.cancel();
        isReading = false;
        buttonText.textContent = 'Read Script';
        button.classList.remove('bg-red-500/20', 'border-red-500');
        return;
    }
    
    // Clean script - remove timestamps and brackets
    let cleanScript = post.reel_script
        .replace(/\[[\d:]+\-[\d:]+\]/g, '') // Remove timestamps [0:00-0:05]
        .replace(/\[|\]/g, '') // Remove any remaining brackets
        .replace(/HOOK:|PROBLEM:|SOLUTION:|CTA:|CLOSING:/gi, '') // Remove section labels
        .trim();
    
    // Validate cleaned script
    if (!cleanScript || cleanScript.length < 10) {
        showMessage('Script is too short or empty to read', 'warning');
        return;
    }
    
    // Limit length to avoid errors (max 4096 characters)
    if (cleanScript.length > 4096) {
        cleanScript = cleanScript.substring(0, 4096) + '...';
    }
    
    try {
        // Create speech synthesis utterance
        const utterance = new SpeechSynthesisUtterance(cleanScript);
        
        // Configure voice settings
        utterance.rate = 0.9; // Slightly slower for clarity
        utterance.pitch = 1.0;
        utterance.volume = 1.0;
        utterance.lang = 'en-US';
        
        // Try to find a good English voice
        const voices = window.speechSynthesis.getVoices();
        const englishVoice = voices.find(voice => 
            voice.lang.startsWith('en') && !voice.localService
        ) || voices.find(voice => voice.lang.startsWith('en'));
        
        if (englishVoice) {
            utterance.voice = englishVoice;
        }
        
        // Event handlers
        utterance.onstart = () => {
            isReading = true;
            buttonText.textContent = 'Stop Reading';
            button.classList.add('bg-red-500/20', 'border-red-500');
        };
        
        utterance.onend = () => {
            isReading = false;
            buttonText.textContent = 'Read Script';
            button.classList.remove('bg-red-500/20', 'border-red-500');
        };
        
        utterance.onerror = (event) => {
            console.error('Speech synthesis error:', event);
            isReading = false;
            buttonText.textContent = 'Read Script';
            button.classList.remove('bg-red-500/20', 'border-red-500');
            
            // Don't show error for 'interrupted' or 'canceled' errors
            if (event.error !== 'interrupted' && event.error !== 'canceled') {
                showMessage('Could not read script. Please try again.', 'warning');
            }
        };
        
        // Start speaking
        currentSpeech = utterance;
        window.speechSynthesis.speak(utterance);
        
    } catch (error) {
        console.error('Error creating speech:', error);
        showMessage('Error initializing text-to-speech', 'error');
    }
}

// Load voices (needed for some browsers)
if ('speechSynthesis' in window) {
    window.speechSynthesis.onvoiceschanged = () => {
        window.speechSynthesis.getVoices();
    };
}

// Close modal and stop any speech
function closePostModal() {
    // Stop any ongoing speech
    if (isReading && 'speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        isReading = false;
    }
    
    // Close modal
    const modal = document.getElementById('post-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Save post to database
async function savePost(postId) {
    if (!postId) {
        showMessage('Invalid post ID', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/save-post/${postId}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        
        if (data.success) {
            showMessage('Post saved successfully! View it in Saved Posts.', 'success');
        } else {
            showMessage(data.message || 'Failed to save post', 'error');
        }
    } catch (error) {
        console.error('Error saving post:', error);
        showMessage('Error saving post', 'error');
    }
}

// Load all saved posts
async function loadSavedPosts() {
    try {
        const response = await fetch(`${API_BASE}/saved-posts`);
        const data = await response.json();
        
        if (data.success) {
            if (data.posts.length > 0) {
                displaySavedPosts(data.posts);
            } else {
                document.getElementById('saved-posts-container').classList.add('hidden');
                document.getElementById('no-saved-posts').classList.remove('hidden');
            }
        } else {
            showMessage('Error loading saved posts', 'error');
        }
    } catch (error) {
        console.error('Error loading saved posts:', error);
        showMessage('Error loading saved posts', 'error');
    }
}

// Display saved posts in grid
function displaySavedPosts(posts) {
    const container = document.getElementById('saved-posts-container');
    if (!container) return;
    
    container.innerHTML = posts.map(post => {
        const savedDate = new Date(post.saved_at).toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        });
        
        return `
            <div class="card overflow-hidden hover:border-primary transition-colors">
                <div class="bg-gradient-to-r from-primary/10 to-accent/10 border-b border-border p-4">
                    <div class="flex items-center justify-between mb-2">
                        <h3 class="text-xl font-bold">${post.brand_name}</h3>
                        <div class="rounded-full bg-primary/20 px-3 py-1">
                            <span class="text-sm font-semibold">${post.final_score?.toFixed(0) || 'N/A'}%</span>
                        </div>
                    </div>
                    <div class="flex items-center gap-2 text-sm text-muted-foreground">
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <circle cx="12" cy="12" r="10"></circle>
                            <polyline points="12 6 12 12 16 14"></polyline>
                        </svg>
                        <span>Saved ${savedDate}</span>
                    </div>
                </div>
                
                <div class="p-6 space-y-4">
                    <div>
                        <h4 class="text-sm font-medium text-muted-foreground mb-1">Topic</h4>
                        <p class="text-sm">${post.post_topic}</p>
                    </div>
                    
                    <div>
                        <h4 class="text-sm font-medium text-muted-foreground mb-1">Title</h4>
                        <p class="font-semibold">${post.post_title}</p>
                    </div>
                    
                    <div>
                        <h4 class="text-sm font-medium text-muted-foreground mb-1">Platform</h4>
                        <div class="flex items-center gap-2">
                            <span class="text-sm text-primary">${post.target_platform}</span>
                            <span class="text-muted-foreground">•</span>
                            <span class="text-sm text-muted-foreground">${post.content_type}</span>
                        </div>
                    </div>
                    
                    <button onclick="viewSavedPostDetail(${post.id})" 
                        class="btn btn-primary w-full h-10">
                        View Full Details & Debate History
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

// View detailed saved post with debate history
async function viewSavedPostDetail(postId) {
    try {
        const response = await fetch(`${API_BASE}/saved-post/${postId}`);
        const data = await response.json();
        
        if (!data.success || !data.post) {
            showMessage('Could not load post details', 'error');
            return;
        }
        
        const post = data.post;
        const modal = document.getElementById('saved-post-modal');
        const modalTitle = document.getElementById('modal-title');
        const modalContent = document.getElementById('saved-modal-content');
        
        modalTitle.textContent = `${post.brand_name} - ${post.post_title}`;
        
        // Build debate history HTML
        let debateHtml = '';
        if (post.debates && post.debates.length > 0) {
            debateHtml = `
                <div class="mb-8">
                    <h4 class="text-xl font-semibold text-primary mb-4 flex items-center gap-2">
                        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
                        </svg>
                        <span>Agent Debate History</span>
                    </h4>
                    <div class="space-y-3">
                        ${post.debates.map(debate => `
                            <div class="rounded-lg border border-border bg-muted/30 p-4">
                                <div class="flex items-start justify-between mb-2">
                                    <div class="flex items-center gap-2">
                                        <span class="font-semibold text-primary">${debate.agent_name}</span>
                                        <span class="text-xs text-muted-foreground">(${debate.agent_role})</span>
                                    </div>
                                    <span class="text-xs px-2 py-1 rounded ${
                                        debate.vote === 'APPROVE' ? 'bg-green-500/20 text-green-400' :
                                        debate.vote === 'REJECT' ? 'bg-red-500/20 text-red-400' :
                                        'bg-yellow-500/20 text-yellow-400'
                                    }">${debate.vote}</span>
                                </div>
                                ${debate.analysis ? `<p class="text-sm text-muted-foreground mb-2">${debate.analysis}</p>` : ''}
                                ${debate.reasoning ? `
                                    <div class="text-sm">
                                        <span class="font-medium text-primary">Reasoning:</span>
                                        <span class="text-muted-foreground">${debate.reasoning}</span>
                                    </div>
                                ` : ''}
                                ${debate.concerns ? `
                                    <div class="text-sm mt-2">
                                        <span class="font-medium text-yellow-400">Concerns:</span>
                                        <span class="text-muted-foreground">${debate.concerns}</span>
                                    </div>
                                ` : ''}
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        modalContent.innerHTML = `
            <div class="space-y-6">
                <!-- Original Requirements -->
                <div class="rounded-lg border border-primary/30 bg-primary/5 p-4">
                    <h4 class="text-lg font-semibold text-primary mb-3">Original Requirements</h4>
                    <div class="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <span class="font-medium">Topic:</span>
                            <p class="text-muted-foreground">${post.post_topic}</p>
                        </div>
                        <div>
                            <span class="font-medium">Objective:</span>
                            <p class="text-muted-foreground">${post.post_objective}</p>
                        </div>
                        <div>
                            <span class="font-medium">Platform:</span>
                            <p class="text-muted-foreground">${post.target_platform}</p>
                        </div>
                        <div>
                            <span class="font-medium">Content Type:</span>
                            <p class="text-muted-foreground">${post.content_type}</p>
                        </div>
                        <div class="col-span-2">
                            <span class="font-medium">Key Message:</span>
                            <p class="text-muted-foreground">${post.key_message}</p>
                        </div>
                        ${post.call_to_action ? `
                            <div class="col-span-2">
                                <span class="font-medium">Call to Action:</span>
                                <p class="text-muted-foreground">${post.call_to_action}</p>
                            </div>
                        ` : ''}
                    </div>
                </div>
                
                ${debateHtml}
                
                <!-- Generated Post Content -->
                <div>
                    <h4 class="text-lg font-semibold text-primary mb-2">Final Generated Post</h4>
                    <div class="rounded-lg border border-border bg-muted/50 p-4 whitespace-pre-wrap text-sm">${post.post_content}</div>
                </div>
                
                <div>
                    <h4 class="text-lg font-semibold text-primary mb-2">Hashtags</h4>
                    <p class="text-primary">${post.hashtags}</p>
                </div>
                
                <div>
                    <h4 class="text-lg font-semibold text-primary mb-2">Image Generation Prompt</h4>
                    <div class="rounded-lg border border-border bg-muted/50 p-4 text-sm">${post.image_prompt}</div>
                </div>
                
                ${post.story_image_prompt ? `
                    <div>
                        <h4 class="text-lg font-semibold text-primary mb-2">Story-Based Image Prompt</h4>
                        <div class="rounded-lg border border-border bg-muted/50 p-4 text-sm">${post.story_image_prompt}</div>
                    </div>
                ` : ''}
                
                ${post.reel_script ? `
                    <div>
                        <h4 class="text-lg font-semibold text-primary mb-2">Reel/Video Script</h4>
                        <div class="rounded-lg border border-border bg-muted/50 p-6 text-sm">
                            ${formatReelScript(post.reel_script)}
                        </div>
                    </div>
                ` : ''}
                
                <div class="flex items-center justify-between pt-4 border-t border-border">
                    <span class="text-sm text-muted-foreground">Score: ${post.final_score?.toFixed(0) || 'N/A'}%</span>
                    <button onclick="copyToClipboard(null, ${JSON.stringify(post).replace(/"/g, '&quot;')})" 
                        class="btn btn-secondary h-9 px-4 flex items-center gap-2">
                        <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                        <span>Copy Content</span>
                    </button>
                </div>
            </div>
        `;
        
        modal.classList.remove('hidden');
    } catch (error) {
        console.error('Error loading saved post detail:', error);
        showMessage('Error loading post details', 'error');
    }
}

// Close saved post modal
function closeSavedPostModal() {
    const modal = document.getElementById('saved-post-modal');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// ========================================
// Global Functions
// ========================================

window.loadBrands = loadBrands;
window.setupBrandForm = setupBrandForm;
window.loadBrandsForPostCreation = loadBrandsForPostCreation;
window.setupPostForm = setupPostForm;
window.loadDebateData = loadDebateData;
window.loadGeneratedPosts = loadGeneratedPosts;
window.viewPostDetail = viewPostDetail;
window.copyToClipboard = copyToClipboard;
window.selectBrandForPosting = selectBrandForPosting;
window.formatReelScript = formatReelScript;
window.readScript = readScript;
window.closePostModal = closePostModal;
window.savePost = savePost;
window.loadSavedPosts = loadSavedPosts;
window.viewSavedPostDetail = viewSavedPostDetail;
window.closeSavedPostModal = closeSavedPostModal;
