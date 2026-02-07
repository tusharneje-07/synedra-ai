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

// Enhanced live agent debate simulation
const agentThinkingPhrases = {
    trend: [
        "Analyzing current social media trends...",
        "Checking viral content patterns...",
        "Evaluating platform-specific trends...",
        "Assessing hashtag relevance...",
        "Reviewing audience engagement metrics...",
        "Completed trend analysis!"
    ],
    brand: [
        "Reviewing brand voice guidelines...",
        "Checking tone consistency...",
        "Validating messaging alignment...",
        "Analyzing brand archetype match...",
        "Verifying emotional valence...",
        "Brand analysis complete!"
    ],
    compliance: [
        "Scanning for compliance issues...",
        "Checking regulatory requirements...",
        "Validating ethical standards...",
        "Reviewing legal constraints...",
        "Assessing risk factors...",
        "Compliance check complete!"
    ],
    risk: [
        "Identifying potential risks...",
        "Analyzing crisis scenarios...",
        "Evaluating reputation impact...",
        "Checking controversial elements...",
        "Assessing backlash probability...",
        "Risk assessment complete!"
    ],
    engagement: [
        "Analyzing engagement potential...",
        "Checking call-to-action effectiveness...",
        "Evaluating virality factors...",
        "Assessing community response...",
        "Reviewing interaction triggers...",
        "Engagement analysis complete!"
    ],
    cmo: [
        "Reviewing all agent recommendations...",
        "Weighing strategic priorities...",
        "Analyzing consensus points...",
        "Evaluating business impact...",
        "Making final decision...",
        "Decision finalized!"
    ]
};

function simulateAgentThinking(agentKey, duration = 10000) {
    const phrases = agentThinkingPhrases[agentKey];
    const thinkingEl = document.getElementById(`agent-thinking-${agentKey}`);
    const statusEl = document.getElementById(`agent-status-${agentKey}`);
    const cardEl = document.getElementById(`agent-card-${agentKey}`);
    
    if (!thinkingEl || !phrases) return;
    
    // Activate card
    cardEl?.classList.remove('opacity-50');
    cardEl?.classList.add('ring-2', 'ring-primary');
    statusEl.textContent = '🔄';
    
    let currentPhrase = 0;
    const interval = duration / phrases.length;
    
    const updatePhrase = () => {
        if (currentPhrase < phrases.length) {
            thinkingEl.textContent = phrases[currentPhrase];
            
            // Mark as complete on last phrase
            if (currentPhrase === phrases.length - 1) {
                statusEl.innerHTML = '<svg class="w-4 h-4 text-green-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M5 13l4 4L19 7"></path></svg>';
                cardEl?.classList.remove('ring-primary');
                cardEl?.classList.add('border-green-500/50');
                thinkingEl.classList.remove('italic');
                thinkingEl.classList.add('text-green-500', 'font-medium');
            }
            
            currentPhrase++;
            if (currentPhrase < phrases.length) {
                setTimeout(updatePhrase, interval);
            }
        }
    };
    
    updatePhrase();
}

function simulateDebateProgress(totalDuration = 50000) {
    const progressBar = document.getElementById('progress-bar');
    const currentActivity = document.getElementById('current-activity');
    
    const agents = [
        { key: 'trend', name: 'TrendAgent', delay: 2000, duration: 8000 },
        { key: 'brand', name: 'BrandAgent', delay: 10000, duration: 8000 },
        { key: 'compliance', name: 'ComplianceAgent', delay: 18000, duration: 7000 },
        { key: 'risk', name: 'RiskAgent', delay: 25000, duration: 7000 },
        { key: 'engagement', name: 'EngagementAgent', delay: 32000, duration: 8000 },
        { key: 'cmo', name: 'CMO', delay: 40000, duration: 9000 }
    ];
    
    // Update current activity
    const activities = [
        { time: 0, text: 'Initializing debate orchestrator...' },
        { time: 2000, text: 'TrendAgent is analyzing market trends...' },
        { time: 10000, text: 'BrandAgent is reviewing brand alignment...' },
        { time: 18000, text: 'ComplianceAgent is checking regulations...' },
        { time: 25000, text: 'RiskAgent is assessing potential risks...' },
        { time: 32000, text: 'EngagementAgent is evaluating viral potential...' },
        { time: 40000, text: 'CMO is making final arbitration...' },
        { time: 49000, text: 'Finalizing results...' }
    ];
    
    activities.forEach(activity => {
        setTimeout(() => {
            if (currentActivity) {
                currentActivity.textContent = activity.text;
            }
        }, activity.delay);
    });
    
    // Start each agent's thinking simulation
    agents.forEach(agent => {
        setTimeout(() => {
            simulateAgentThinking(agent.key, agent.duration);
        }, agent.delay);
    });
    
    // Animate progress bar
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 100 / (totalDuration / 200);
        if (progress >= 100) {
            progress = 100;
            clearInterval(progressInterval);
        }
        if (progressBar) {
            progressBar.style.width = `${progress}%`;
        }
    }, 200);
}

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
            
            // Start the visual debate simulation
            simulateDebateProgress(50000);
            
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
            
            // Start debate process
            const debateResponse = await fetch(`${API_BASE}/debates/start`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ post_input_id: postInputId })
            });
            
            const debateData = await debateResponse.json();
            
            showLoadingModal(false);
            
            if (debateData.success) {
                // Clear form cookie after successful submission
                clearFormCookie('post-form');
                // Redirect to debate page
                window.location.href = `/debate/${postInputId}`;
            } else {
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
                    <p class="mt-1">${debate.recommendation}</p>
                </div>
                
                <div>
                    <span class="font-medium text-muted-foreground">Reasoning:</span>
                    <p class="mt-1 text-muted-foreground">${debate.reasoning}</p>
                </div>
                
                ${debate.concerns ? `
                <div>
                    <span class="font-medium text-muted-foreground">Concerns:</span>
                    <p class="mt-1 text-yellow-500">${debate.concerns}</p>
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
                    <p class="mt-1">${cmoDebate.recommendation}</p>
                </div>
                <div>
                    <span class="font-medium text-muted-foreground">Reasoning:</span>
                    <p class="mt-1 text-muted-foreground">${cmoDebate.reasoning}</p>
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
            
            <div class="flex items-center justify-between pt-4 border-t border-border">
                <span class="text-sm text-muted-foreground">Variation ${post.variation_number} | Score: ${post.final_score?.toFixed(0) || 'N/A'}%</span>
                <button onclick="copyToClipboard(${index})" 
                    class="btn btn-secondary h-9 px-4 flex items-center gap-2">
                    <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                    <span>Copy Content</span>
                </button>
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
