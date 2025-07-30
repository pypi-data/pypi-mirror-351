/**
 * ModelManager - Handles all model-related functionality
 */
class ModelManager {
    constructor(app) {
        this.app = app;
        this.modelStatus = {
            ai_engine_loaded: false,
            query_generator_available: false
        };
    }

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
                            <button class="btn btn-sm btn-primary" onclick="app.modelManager.switchToModel('${model.model_variant}')">
                                <i class="fas fa-exchange-alt"></i> Make Active
                            </button>
                        ` : ''}
                        <button class="btn btn-sm btn-danger" onclick="app.modelManager.unloadModel('${model.model_variant}')">
                            <i class="fas fa-times"></i> Unload
                        </button>
                    </div>
                </div>
            `;
        });
        
        loadedModelsList.innerHTML = html;
    }

    async loadModel(modelVariant) {
        const normalizedModelVariant = this.normalizeModelName(modelVariant);
        
        try {
            this.app.uiManager.showToast(`Loading model ${normalizedModelVariant}...`, 'info');
            
            const response = await fetch('/models/load', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model_variant: normalizedModelVariant,
                    force_reload: false
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to load model');
            }
            
            const data = await response.json();
            
            if (data.loaded) {
                this.app.uiManager.showToast(`Model ${normalizedModelVariant} loaded successfully!`, 'success');
                
                this.modelStatus.ai_engine_loaded = true;
                this.updateModelStatus();
                
                await this.updateLoadedModelsDisplay();
                await this.updateAvailableModelsDisplay();
                await this.app.apiClient.checkHealth();
                
            } else {
                this.app.uiManager.showToast(`Failed to load model: ${data.message}`, 'error');
            }
            
        } catch (error) {
            this.app.uiManager.showToast(`Model loading failed: ${error.message}`, 'error');
        }
    }

    async unloadModel(modelVariant) {
        try {
            this.app.uiManager.showToast('Unloading model...', 'info');
            
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
            this.app.uiManager.showToast(data.message, 'success');
            
            await this.updateLoadedModelsDisplay();
            await this.app.apiClient.checkHealth();
            
        } catch (error) {
            this.app.uiManager.showToast('Model unloading failed: ' + error.message, 'error');
        }
    }

    async switchToModel(modelVariant) {
        try {
            this.app.uiManager.showToast('Switching model...', 'info');
            
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
            this.app.uiManager.showToast(data.message, 'success');
            
            await this.updateLoadedModelsDisplay();
            await this.app.apiClient.checkHealth();
            
        } catch (error) {
            this.app.uiManager.showToast('Model switching failed: ' + error.message, 'error');
        }
    }

    showModelManager() {
        const modal = document.getElementById('model-modal');
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
        
        // Update displays when modal opens
        this.updateAvailableModelsDisplay();
        this.updateLoadedModelsDisplay();
    }

    hideModelManager() {
        const modal = document.getElementById('model-modal');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }

    showModelVariants(modelName) {
        console.log(`Showing variants for model: ${modelName}`);
    }

    async downloadModel(modelId) {
        console.log(`🔄 Starting download for model: ${modelId}`);
        
        try {
            this.app.uiManager.showToast('Starting model download...', 'info');
            
            const response = await fetch('/models/download', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    model_id: modelId
                })
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Failed to start download');
            }
            
            const data = await response.json();
            console.log('📥 Download started:', data);
            
            this.app.uiManager.showToast(`Download started for ${modelId}`, 'success');
            
            const modelCard = document.querySelector(`[data-model-id="${modelId}"]`);
            if (modelCard) {
                const statusElement = modelCard.querySelector('.download-status');
                const actionButton = modelCard.querySelector('.download-btn');
                
                if (statusElement) {
                    statusElement.innerHTML = `
                        <div class="download-progress">
                            <div class="progress-bar-container">
                                <div class="progress-bar" style="width: 0%">0%</div>
                            </div>
                            <small>Starting download...</small>
                        </div>
                    `;
                }
                
                if (actionButton) {
                    actionButton.innerHTML = '<i class="fas fa-times"></i> Cancel';
                    actionButton.className = 'btn btn-sm btn-danger';
                    actionButton.onclick = () => this.cancelDownload();
                }
            }
            
            setTimeout(() => this.pollDownloadStatus(modelId), 1000);
            
        } catch (error) {
            console.error('❌ Download failed:', error);
            this.app.uiManager.showToast(`Download failed: ${error.message}`, 'error');
        }
    }

    async pollDownloadStatus(modelId) {
        try {
            const response = await fetch('/models/download/status');
            if (!response.ok) return;
            
            const data = await response.json();
            
            if (data.downloading && data.model_id === modelId) {
                const progress = Math.round((data.downloaded / data.total) * 100);
                
                const modelCard = document.querySelector(`[data-model-id="${modelId}"]`);
                if (modelCard) {
                    const statusElement = modelCard.querySelector('.download-status');
                    if (statusElement) {
                        statusElement.innerHTML = `
                            <div class="download-progress">
                                <div class="progress-bar-container">
                                    <div class="progress-bar" style="width: ${progress}%">${progress}%</div>
                                </div>
                                <small>${this.formatFileSize(data.downloaded)} / ${this.formatFileSize(data.total)}</small>
                            </div>
                        `;
                    }
                }
                
                setTimeout(() => this.pollDownloadStatus(modelId), 1000);
            } else {
                await this.updateAvailableModelsDisplay();
            }
            
        } catch (error) {
            console.error('Error polling download status:', error);
        }
    }

    async cancelDownload() {
        try {
            const response = await fetch('/models/download/cancel', {
                method: 'POST'
            });
            
            if (!response.ok) {
                throw new Error('Failed to cancel download');
            }
            
            this.app.uiManager.showToast('Download cancelled', 'info');
            await this.updateAvailableModelsDisplay();
            
        } catch (error) {
            this.app.uiManager.showToast('Failed to cancel download: ' + error.message, 'error');
        }
    }

    normalizeModelName(modelName) {
        const normalizations = {
            'law-chat': 'law-chat:latest',
            'llama3.2': 'llama3.2:latest',
            'mxbai-embed-large': 'mxbai-embed-large:latest'
        };
        return normalizations[modelName] || modelName;
    }

    getModelDisplayInfo(modelName, modelData) {
        const sizeGB = modelData.size ? (modelData.size / (1024**3)).toFixed(1) : 'Unknown';
        
        const modelInfo = {
            'law-chat:latest': {
                description: 'Specialized legal AI model trained on legal documents and case law.',
                features: ['Legal Analysis', 'Case Research', 'Document Review'],
                provider: 'Custom'
            },
            'llama3.2:latest': {
                description: 'Meta\'s Llama 3.2 model optimized for general purpose tasks.',
                features: ['General Purpose', 'Reasoning', 'Code Generation'],
                provider: 'Meta'
            },
            'mxbai-embed-large:latest': {
                description: 'High-quality embedding model for semantic search and similarity.',
                features: ['Text Embeddings', 'Semantic Search', 'Document Similarity'],
                provider: 'mixedbread.ai'
            }
        };
        
        const defaultInfo = {
            description: 'AI model for text generation and analysis.',
            features: ['Text Generation', 'Analysis'],
            provider: 'Unknown'
        };
        
        const info = modelInfo[modelName] || defaultInfo;
        
        return {
            name: modelName,
            size: sizeGB,
            downloaded: modelData.downloaded || false,
            ...info
        };
    }

    createModelCard(modelName, modelData) {
        const info = this.getModelDisplayInfo(modelName, modelData);
        const statusClass = info.downloaded ? 'downloaded' : 'not-downloaded';
        const statusText = info.downloaded ? 'Downloaded' : 'Not Downloaded';
        const actionButton = info.downloaded ? 
            `<button class="btn btn-primary load-btn" onclick="app.modelManager.loadModel('${modelName}')">
                <i class="fas fa-play"></i> Load
            </button>` :
            `<button class="btn btn-primary download-btn" onclick="app.modelManager.downloadModel('${modelName}')">
                <i class="fas fa-download"></i> Download
            </button>`;
        
        return `
            <div class="model-card" data-model-id="${modelName}">
                <div class="model-header">
                    <h4>${info.name}</h4>
                    <span class="model-badge">${info.provider}</span>
                </div>
                <div class="model-info">
                    <p>${info.description}</p>
                    <div class="model-features">
                        ${info.features.map(feature => `<span class="feature-tag">${feature}</span>`).join('')}
                    </div>
                    <div class="model-stats">
                        <small>Size: ${info.size} GB</small>
                    </div>
                </div>
                <div class="model-status">
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
                <div class="model-actions">
                    ${actionButton}
                </div>
            </div>
        `;
    }

    async updateAvailableModelsDisplay() {
        try {
            console.log('🔍 Fetching available models...');
            const response = await fetch('/models/available');
            
            if (!response.ok) {
                throw new Error('Failed to fetch available models');
            }
            
            const data = await response.json();
            console.log('📋 Available models data:', data);
            
            const models = data.available_models || {};
            const downloadStatus = data.download_status || {};
            
            const modelsContainer = document.querySelector('.model-grid');
            if (!modelsContainer) {
                console.error('❌ Models container not found');
                return;
            }
            
            // Keep the "coming soon" placeholder
            const comingSoonCard = modelsContainer.querySelector('.coming-soon');
            const comingSoonHTML = comingSoonCard ? comingSoonCard.outerHTML : '';
            
            if (Object.keys(models).length === 0) {
                modelsContainer.innerHTML = '<p>No models available</p>' + comingSoonHTML;
                return;
            }
            
            let html = '';
            Object.entries(models).forEach(([modelName, modelData]) => {
                html += this.createModelCard(modelName, modelData);
            });
            
            // Add the coming soon card at the end
            html += comingSoonHTML;
            
            modelsContainer.innerHTML = html;
            console.log('✅ Models display updated');
            
        } catch (error) {
            console.error('❌ Error updating available models display:', error);
            const modelsContainer = document.querySelector('.model-grid');
            if (modelsContainer) {
                modelsContainer.innerHTML = '<p class="error">Error loading models</p>';
            }
        }
    }

    formatFileSize(bytes) {
        if (!bytes) return '0 B';
        const sizes = ['B', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return `${(bytes / Math.pow(1024, i)).toFixed(1)} ${sizes[i]}`;
    }
}

// Export for use in main app
window.ModelManager = ModelManager; 