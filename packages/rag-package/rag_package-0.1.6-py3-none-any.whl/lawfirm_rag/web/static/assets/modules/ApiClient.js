/**
 * ApiClient - Handles all HTTP requests and API communication
 */
class ApiClient {
    constructor(app) {
        this.app = app;
    }

    getAuthHeaders() {
        // For now, return empty object since auth headers aren't implemented yet
        // This can be extended later if API key authentication is needed
        return {};
    }

    async checkHealth() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            
            // Update model status based on health check
            if (data.ai_engine && data.ai_engine.status === 'ready') {
                this.app.modelManager.modelStatus.ai_engine_loaded = true;
            } else {
                this.app.modelManager.modelStatus.ai_engine_loaded = false;
            }
            
            if (data.query_generator && data.query_generator.status === 'ready') {
                this.app.modelManager.modelStatus.query_generator_available = true;
            } else {
                this.app.modelManager.modelStatus.query_generator_available = false;
            }
            
            this.app.modelManager.updateModelStatus();
            
        } catch (error) {
            console.error('Health check failed:', error);
            this.app.modelManager.modelStatus.ai_engine_loaded = false;
            this.app.modelManager.modelStatus.query_generator_available = false;
            this.app.modelManager.updateModelStatus();
        }
    }

    async uploadFiles(files) {
        const formData = new FormData();
        
        Array.from(files).forEach(file => {
            formData.append('files', file);
        });

        try {
            this.app.uiManager.showLoading('Uploading files...');
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            this.app.uiManager.hideLoading();

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Upload failed');
            }

            const data = await response.json();
            this.app.uiManager.showToast('Files uploaded successfully!', 'success');
            
            return data;

        } catch (error) {
            this.app.uiManager.hideLoading();
            this.app.uiManager.showToast('Upload failed: ' + error.message, 'error');
            throw error;
        }
    }

    async analyzeDocuments(sessionId) {
        try {
            this.app.uiManager.showLoading('Analyzing documents...');
            
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    session_id: sessionId
                })
            });

            this.app.uiManager.hideLoading();

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Analysis failed');
            }

            const data = await response.json();
            this.app.uiManager.showToast('Analysis completed!', 'success');
            
            return data;

        } catch (error) {
            this.app.uiManager.hideLoading();
            this.app.uiManager.showToast('Analysis failed: ' + error.message, 'error');
            throw error;
        }
    }

    async generateQuery(sessionId, database) {
        try {
            this.app.uiManager.showLoading('Generating search query...');
            
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    database: database
                })
            });

            this.app.uiManager.hideLoading();

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Query generation failed');
            }

            const data = await response.json();
            this.app.uiManager.showToast('Query generated successfully!', 'success');
            
            return data;

        } catch (error) {
            this.app.uiManager.hideLoading();
            this.app.uiManager.showToast('Query generation failed: ' + error.message, 'error');
            throw error;
        }
    }

    async generateAllQueries(sessionId) {
        try {
            this.app.uiManager.showLoading('Generating queries for all databases...');
            
            const response = await fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders()
                },
                body: JSON.stringify({
                    session_id: sessionId,
                    all_databases: true
                })
            });

            this.app.uiManager.hideLoading();

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Query generation failed');
            }

            const data = await response.json();
            this.app.uiManager.showToast('All queries generated successfully!', 'success');
            
            return data;

        } catch (error) {
            this.app.uiManager.hideLoading();
            this.app.uiManager.showToast('Query generation failed: ' + error.message, 'error');
            throw error;
        }
    }

    async fetchAvailableModels() {
        try {
            const response = await fetch('/models/available');
            if (!response.ok) {
                throw new Error('Failed to fetch available models');
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching available models:', error);
            throw error;
        }
    }

    async fetchLoadedModels() {
        try {
            const response = await fetch('/models/loaded');
            if (!response.ok) {
                throw new Error('Failed to fetch loaded models');
            }
            return await response.json();
        } catch (error) {
            console.error('Error fetching loaded models:', error);
            throw error;
        }
    }
}

// Export for use in main app
window.ApiClient = ApiClient; 