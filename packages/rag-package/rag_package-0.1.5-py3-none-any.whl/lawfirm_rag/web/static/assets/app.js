// LawFirm-RAG Frontend Application
class LawFirmRAG {
    constructor() {
        this.currentSession = null;
        this.selectedFiles = [];
        this.modelStatus = {
            ai_engine_loaded: false,
            query_generator_available: false
        };
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.checkHealth();
        this.updateModelStatus();
    }

    // Model Management
    updateModelStatus() {
        const statusText = document.getElementById('model-status-text');
        const statusDot = document.querySelector('.status-dot');
        const statusTextModal = document.getElementById('status-text');
        const queryGenStatus = document.getElementById('query-gen-status');

        if (this.modelStatus.ai_engine_loaded) {
            statusText.textContent = 'AI Model Loaded - Ready for advanced analysis';
            statusDot.style.color = '#28a745';
            statusTextModal.textContent = 'AI model loaded and ready';
            queryGenStatus.textContent = 'Available (AI-powered)';
        } else {
            statusText.textContent = 'No AI model loaded - Using fallback mode';
            statusDot.style.color = '#ffc107';
            statusTextModal.textContent = 'No AI model loaded';
            queryGenStatus.textContent = 'Available (fallback mode)';
        }
    }

    async updateLoadedModelsDisplay() {
        try {
            const response = await fetch('/models/loaded');
            if (!response.ok) {
                throw new Error('Failed to fetch loaded models');
            }
            
            const data = await response.json();
            
            // Update the loaded models section in the modal
            const loadedModelsSection = document.getElementById('loaded-models-section');
            if (!loadedModelsSection) {
                // Create the section if it doesn't exist
                this.createLoadedModelsSection();
            }
            
            this.displayLoadedModels(data);
            
        } catch (error) {
            console.error('Error updating loaded models display:', error);
        }
    }

    createLoadedModelsSection() {
        const modalBody = document.querySelector('.modal-body');
        const loadedModelsHTML = `
            <div class="loaded-models-section" id="loaded-models-section">
                <h3>Loaded Models</h3>
                <div id="loaded-models-list" class="loaded-models-list">
                    <p class="text-muted">No models currently loaded</p>
                </div>
            </div>
        `;
        
        // Insert after the model status section
        const statusSection = document.querySelector('.model-status-section');
        statusSection.insertAdjacentHTML('afterend', loadedModelsHTML);
    }

    displayLoadedModels(data) {
        const loadedModelsList = document.getElementById('loaded-models-list');
        
        if (data.loaded_models.length === 0) {
            loadedModelsList.innerHTML = '<p class="text-muted">No models currently loaded</p>';
            return;
        }
        
        let html = '';
        data.loaded_models.forEach(model => {
            const memoryMB = model.memory_usage ? (model.memory_usage / (1024 * 1024)).toFixed(0) : 'Unknown';
            const loadedDate = new Date(model.loaded_at).toLocaleString();
            
            html += `
                <div class="loaded-model-item ${model.is_active ? 'active-model' : ''}">
                    <div class="model-info">
                        <h4>${model.model_variant} ${model.is_active ? '<span class="active-badge">ACTIVE</span>' : ''}</h4>
                        <p><strong>Path:</strong> ${model.model_path}</p>
                        <p><strong>Loaded:</strong> ${loadedDate}</p>
                        <p><strong>Memory:</strong> ~${memoryMB} MB</p>
                    </div>
                    <div class="model-actions">
                        ${!model.is_active ? `
                            <button class="btn btn-sm btn-primary" onclick="app.switchToModel('${model.model_variant}')">
                                <i class="fas fa-exchange-alt"></i> Make Active
                            </button>
                        ` : ''}
                        <button class="btn btn-sm btn-danger" onclick="app.unloadModel('${model.model_variant}')">
                            <i class="fas fa-times"></i> Unload
                        </button>
                    </div>
                </div>
            `;
        });
        
        loadedModelsList.innerHTML = html;
    }

    async loadModel(modelVariant) {
        try {
            this.showToast('Loading model...', 'info');
            
            const response = await fetch('/models/load', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model_variant: modelVariant,
                    force_reload: false
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to load model');
            }
            
            const data = await response.json();
            
            if (data.loaded) {
                this.showToast(`Model ${modelVariant} loaded successfully!`, 'success');
                
                // Update model status
                this.modelStatus.ai_engine_loaded = true;
                this.updateModelStatus();
                
                // Update loaded models display
                await this.updateLoadedModelsDisplay();
                
                // Update health status
                await this.checkHealth();
                
            } else {
                this.showToast(`Failed to load model: ${data.message}`, 'error');
            }
            
        } catch (error) {
            this.showToast('Model loading failed: ' + error.message, 'error');
        }
    }

    async unloadModel(modelVariant) {
        try {
            this.showToast('Unloading model...', 'info');
            
            const response = await fetch('/models/unload', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model_variant: modelVariant
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to unload model');
            }
            
            const data = await response.json();
            this.showToast(data.message, 'success');
            
            // Update loaded models display
            await this.updateLoadedModelsDisplay();
            
            // Update health status
            await this.checkHealth();
            
        } catch (error) {
            this.showToast('Model unloading failed: ' + error.message, 'error');
        }
    }

    async switchToModel(modelVariant) {
        try {
            this.showToast('Switching model...', 'info');
            
            const response = await fetch('/models/switch', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model_variant: modelVariant
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to switch model');
            }
            
            const data = await response.json();
            this.showToast(data.message, 'success');
            
            // Update model status
            this.modelStatus.ai_engine_loaded = true;
            this.updateModelStatus();
            
            // Update loaded models display
            await this.updateLoadedModelsDisplay();
            
        } catch (error) {
            this.showToast('Model switching failed: ' + error.message, 'error');
        }
    }

    showModelManager() {
        document.getElementById('model-modal').style.display = 'block';
        // Update loaded models when modal opens
        this.updateLoadedModelsDisplay();
        // Check downloaded models and update button visibility
        this.updateDownloadedModelsDisplay();
    }

    hideModelManager() {
        document.getElementById('model-modal').style.display = 'none';
    }

    showModelVariants(modelName) {
        const variantsSection = document.getElementById('model-variants');
        if (variantsSection.style.display === 'none') {
            variantsSection.style.display = 'block';
        } else {
            variantsSection.style.display = 'none';
        }
    }

    async downloadModel(modelId) {
        const progressContainer = document.getElementById('law-chat-progress');
        const progressFill = progressContainer.querySelector('.progress-fill');
        const progressText = progressContainer.querySelector('.progress-text');
        
        progressContainer.style.display = 'block';
        
        try {
            this.showToast('Starting model download...', 'info');
            
            // Start the download
            const downloadResponse = await fetch('/models/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model_variant: modelId,
                    force: false
                })
            });
            
            if (!downloadResponse.ok) {
                const errorData = await downloadResponse.json();
                throw new Error(errorData.detail || 'Download failed to start');
            }
            
            const downloadData = await downloadResponse.json();
            
            if (!downloadData.download_started) {
                this.showToast(downloadData.message, 'info');
                progressContainer.style.display = 'none';
                return;
            }
            
            this.showToast('Download started successfully!', 'success');
            
            // Poll for progress updates
            const progressInterval = setInterval(async () => {
                try {
                    const progressResponse = await fetch('/models/download-progress');
                    
                    if (!progressResponse.ok) {
                        throw new Error('Failed to get progress');
                    }
                    
                    const progressData = await progressResponse.json();
                    
                    // Update progress bar
                    const progress = Math.round(progressData.progress);
                    progressFill.style.width = progress + '%';
                    
                    // Format progress text with speed and ETA
                    let progressText = `${progress}%`;
                    if (progressData.speed > 0) {
                        const speedMB = (progressData.speed / (1024 * 1024)).toFixed(1);
                        progressText += ` (${speedMB} MB/s)`;
                        
                        if (progressData.eta) {
                            const etaMinutes = Math.round(progressData.eta / 60);
                            progressText += ` - ${etaMinutes}m remaining`;
                        }
                    }
                    
                    document.querySelector('.progress-text').textContent = progressText;
                    
                    // Check if download is complete
                    if (progressData.status === 'completed') {
                        clearInterval(progressInterval);
                        this.showToast('Model download completed successfully!', 'success');
                        progressContainer.style.display = 'none';
                        
                        // Update model status
                        this.modelStatus.ai_engine_loaded = true;
                        this.updateModelStatus();
                        
                        // Update downloaded models display to show load button
                        await this.updateDownloadedModelsDisplay();
                        
                    } else if (progressData.status === 'error') {
                        clearInterval(progressInterval);
                        throw new Error(progressData.error || 'Download failed');
                        
                    } else if (progressData.status === 'cancelled') {
                        clearInterval(progressInterval);
                        this.showToast('Download was cancelled', 'warning');
                        progressContainer.style.display = 'none';
                    }
                    
                } catch (progressError) {
                    clearInterval(progressInterval);
                    throw progressError;
                }
            }, 1000); // Poll every second
            
            // Store interval ID for potential cancellation
            this.currentDownloadInterval = progressInterval;
            
        } catch (error) {
            this.showToast('Download failed: ' + error.message, 'error');
            progressContainer.style.display = 'none';
            
            // Clear any existing interval
            if (this.currentDownloadInterval) {
                clearInterval(this.currentDownloadInterval);
                this.currentDownloadInterval = null;
            }
        }
    }

    async cancelDownload() {
        try {
            const response = await fetch('/models/cancel-download', {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error('Failed to cancel download');
            }
            
            const data = await response.json();
            
            if (data.cancelled) {
                this.showToast('Download cancelled successfully', 'info');
            } else {
                this.showToast('No active download to cancel', 'warning');
            }
            
            // Clear progress interval
            if (this.currentDownloadInterval) {
                clearInterval(this.currentDownloadInterval);
                this.currentDownloadInterval = null;
            }
            
            // Hide progress container
            const progressContainer = document.getElementById('law-chat-progress');
            progressContainer.style.display = 'none';
            
        } catch (error) {
            this.showToast('Failed to cancel download: ' + error.message, 'error');
        }
    }

    // Event Listeners
    setupEventListeners() {
        // File upload
        const fileInput = document.getElementById('file-input');
        const uploadArea = document.getElementById('upload-area');
        const uploadBtn = document.getElementById('upload-btn');

        fileInput.addEventListener('change', (e) => this.handleFileSelect(e.target.files));
        uploadBtn.addEventListener('click', () => this.uploadFiles());

        // Drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            this.handleFileSelect(e.dataTransfer.files);
        });

        // Analysis
        const analyzeBtn = document.getElementById('analyze-btn');
        analyzeBtn.addEventListener('click', () => this.analyzeDocuments());

        // Query generation
        const generateQueryBtn = document.getElementById('generate-query-btn');
        const generateAllBtn = document.getElementById('generate-all-btn');
        
        generateQueryBtn.addEventListener('click', () => this.generateQuery());
        generateAllBtn.addEventListener('click', () => this.generateAllQueries());

        // Modal close on outside click
        window.addEventListener('click', (e) => {
            const modal = document.getElementById('model-modal');
            if (e.target === modal) {
                this.hideModelManager();
            }
        });
    }

    // Health Check
    async checkHealth() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            this.modelStatus = {
                ai_engine_loaded: data.ai_engine_loaded || false,
                query_generator_available: data.query_generator_available || false
            };
            
            this.updateModelStatus();
            this.showToast('System health check completed', 'success');
            
        } catch (error) {
            this.showToast('Health check failed: ' + error.message, 'error');
        }
    }

    // File Handling
    handleFileSelect(files) {
        this.selectedFiles = Array.from(files).filter(file => {
            const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
            return validTypes.includes(file.type);
        });

        this.updateFileList();
        this.updateUploadButton();
    }

    updateFileList() {
        const fileList = document.getElementById('file-list');
        fileList.innerHTML = '';

        this.selectedFiles.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-info">
                    <i class="fas fa-file-${this.getFileIcon(file.type)}"></i>
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">(${this.formatFileSize(file.size)})</span>
                </div>
                <button class="file-remove" onclick="app.removeFile(${index})">
                    <i class="fas fa-times"></i>
                </button>
            `;
            fileList.appendChild(fileItem);
        });
    }

    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.updateFileList();
        this.updateUploadButton();
    }

    updateUploadButton() {
        const uploadBtn = document.getElementById('upload-btn');
        uploadBtn.disabled = this.selectedFiles.length === 0;
    }

    getFileIcon(mimeType) {
        switch (mimeType) {
            case 'application/pdf': return 'pdf';
            case 'application/vnd.openxmlformats-officedocument.wordprocessingml.document': return 'word';
            case 'text/plain': return 'alt';
            default: return 'file';
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // File Upload
    async uploadFiles() {
        if (this.selectedFiles.length === 0) return;

        this.showLoading('Uploading files...');

        try {
            const formData = new FormData();
            this.selectedFiles.forEach(file => {
                formData.append('files', file);
            });

            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Upload failed: ${response.statusText}`);
            }

            const data = await response.json();
            this.currentSession = data.session_id;
            
            this.showSessionInfo(data);
            this.showSections(['session-section', 'analysis-section', 'query-section']);
            this.showToast('Files uploaded successfully!', 'success');

        } catch (error) {
            this.showToast('Upload failed: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    // Document Analysis
    async analyzeDocuments() {
        if (!this.currentSession) {
            this.showToast('Please upload documents first', 'warning');
            return;
        }

        const analysisType = document.getElementById('analysis-type').value;
        this.showLoading('Analyzing documents...');

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.currentSession,
                    analysis_type: analysisType
                })
            });

            if (!response.ok) {
                throw new Error(`Analysis failed: ${response.statusText}`);
            }

            const data = await response.json();
            this.displayAnalysisResult(data);
            this.showToast('Analysis completed!', 'success');

        } catch (error) {
            this.showToast('Analysis failed: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displayAnalysisResult(data) {
        const resultArea = document.getElementById('analysis-result');
        resultArea.innerHTML = `
            <div class="result-header">
                <h4><i class="fas fa-chart-line"></i> ${data.analysis_type.replace('_', ' ').toUpperCase()} Analysis</h4>
                <span class="method-badge ${data.method}">${data.method.toUpperCase()}</span>
            </div>
            <div class="result-content">
                <p>${data.result}</p>
            </div>
        `;
    }

    // Query Generation
    async generateQuery() {
        if (!this.currentSession) {
            this.showToast('Please upload documents first', 'warning');
            return;
        }

        const database = document.getElementById('database-select').value;
        this.showLoading('Generating query...');

        try {
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.currentSession,
                    database: database,
                    all_databases: false
                })
            });

            if (!response.ok) {
                throw new Error(`Query generation failed: ${response.statusText}`);
            }

            const data = await response.json();
            this.displayQueryResult(data);
            this.showToast('Query generated successfully!', 'success');

        } catch (error) {
            this.showToast('Query generation failed: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    async generateAllQueries() {
        if (!this.currentSession) {
            this.showToast('Please upload documents first', 'warning');
            return;
        }

        this.showLoading('Generating queries for all databases...');

        try {
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: this.currentSession,
                    all_databases: true
                })
            });

            if (!response.ok) {
                throw new Error(`Query generation failed: ${response.statusText}`);
            }

            const data = await response.json();
            this.displayAllQueriesResult(data);
            this.showToast('All queries generated successfully!', 'success');

        } catch (error) {
            this.showToast('Query generation failed: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    }

    displayQueryResult(data) {
        const resultArea = document.getElementById('query-result');
        resultArea.innerHTML = `
            <div class="result-header">
                <h4><i class="fas fa-database"></i> ${data.database.toUpperCase()} Query</h4>
                <span class="confidence-badge">Confidence: ${Math.round(data.confidence * 100)}%</span>
            </div>
            <div class="query-text">
                <code>${data.query}</code>
            </div>
            ${data.suggestions && data.suggestions.length > 0 ? `
                <div class="suggestions">
                    <h5>Suggestions:</h5>
                    ${data.suggestions.map(suggestion => `<span class="suggestion-tag">${suggestion}</span>`).join('')}
                </div>
            ` : ''}
        `;
    }

    displayAllQueriesResult(data) {
        const resultArea = document.getElementById('query-result');
        let html = '<div class="all-queries-results">';
        
        Object.entries(data.queries).forEach(([database, queryData]) => {
            html += `
                <div class="query-item">
                    <div class="result-header">
                        <h4><i class="fas fa-database"></i> ${database.toUpperCase()}</h4>
                        <span class="confidence-badge">Confidence: ${Math.round(queryData.confidence * 100)}%</span>
                    </div>
                    <div class="query-text">
                        <code>${queryData.query}</code>
                    </div>
                    ${queryData.suggestions && queryData.suggestions.length > 0 ? `
                        <div class="suggestions">
                            <h5>Suggestions:</h5>
                            ${queryData.suggestions.map(suggestion => `<span class="suggestion-tag">${suggestion}</span>`).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
        });
        
        html += '</div>';
        resultArea.innerHTML = html;
    }

    // UI Helpers
    showSessionInfo(data) {
        const sessionInfo = document.getElementById('session-info');
        sessionInfo.innerHTML = `
            <div class="session-stats">
                <div class="session-stat">
                    <h4>Session ID</h4>
                    <div class="stat-value">${data.session_id}</div>
                </div>
                <div class="session-stat">
                    <h4>Files Processed</h4>
                    <div class="stat-value">${data.processed_files}</div>
                </div>
                <div class="session-stat">
                    <h4>Total Text Length</h4>
                    <div class="stat-value">${data.total_text_length.toLocaleString()} chars</div>
                </div>
            </div>
            <div class="file-details">
                <h5>Uploaded Files:</h5>
                <ul>
                    ${data.files.map(file => `<li>${file.filename} (${this.formatFileSize(file.size)})</li>`).join('')}
                </ul>
            </div>
        `;
    }

    showSections(sectionIds) {
        sectionIds.forEach(id => {
            document.getElementById(id).style.display = 'block';
        });
    }

    showLoading(message = 'Processing...') {
        document.getElementById('loading-text').textContent = message;
        document.getElementById('loading-overlay').style.display = 'block';
    }

    hideLoading() {
        document.getElementById('loading-overlay').style.display = 'none';
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${this.getToastIcon(type)}"></i>
                <span>${message}</span>
            </div>
        `;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 5000);
    }

    getToastIcon(type) {
        switch (type) {
            case 'success': return 'check-circle';
            case 'error': return 'exclamation-circle';
            case 'warning': return 'exclamation-triangle';
            default: return 'info-circle';
        }
    }

    async updateDownloadedModelsDisplay() {
        try {
            const response = await fetch('/models/available');
            if (!response.ok) {
                throw new Error('Failed to fetch available models');
            }
            
            const data = await response.json();
            
            // Update button visibility based on download status
            Object.entries(data.available_models).forEach(([variant, info]) => {
                const downloadBtn = document.getElementById(`download-${variant}`);
                const loadBtn = document.getElementById(`load-${variant}`);
                
                if (downloadBtn && loadBtn) {
                    if (info.downloaded) {
                        // Model is downloaded - show load button, hide download button
                        downloadBtn.style.display = 'none';
                        loadBtn.style.display = 'inline-flex';
                        
                        // Update download button text to show it's downloaded
                        downloadBtn.innerHTML = '<i class="fas fa-check"></i> Downloaded';
                        downloadBtn.disabled = true;
                    } else {
                        // Model not downloaded - show download button, hide load button
                        downloadBtn.style.display = 'inline-flex';
                        loadBtn.style.display = 'none';
                        downloadBtn.disabled = false;
                    }
                }
            });
            
        } catch (error) {
            console.error('Error updating downloaded models display:', error);
        }
    }
}

// Initialize the application
const app = new LawFirmRAG();

// Make app globally available for inline event handlers
window.app = app; 