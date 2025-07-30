/**
 * UIManager - Handles UI utilities, toasts, loading states, and general interface management
 */
class UIManager {
    constructor(app) {
        this.app = app;
    }

    showSections(sectionIds) {
        // Hide all sections first
        const allSections = ['upload-section', 'analysis-section', 'query-section'];
        allSections.forEach(id => {
            const section = document.getElementById(id);
            if (section) section.style.display = 'none';
        });

        // Show requested sections
        sectionIds.forEach(id => {
            const section = document.getElementById(id);
            if (section) section.style.display = 'block';
        });
    }

    showLoading(message = 'Processing...') {
        const spinner = document.getElementById('loading-spinner');
        const loadingText = document.getElementById('loading-text');
        
        if (spinner) spinner.style.display = 'flex';
        if (loadingText) loadingText.textContent = message;
    }

    hideLoading() {
        const spinner = document.getElementById('loading-spinner');
        if (spinner) spinner.style.display = 'none';
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const toastHtml = `
            <div class="toast ${type}">
                <i class="${this.getToastIcon(type)}"></i>
                <span>${message}</span>
                <button class="toast-close" onclick="this.parentElement.remove()">&times;</button>
            </div>
        `;

        container.insertAdjacentHTML('beforeend', toastHtml);
        
        // Auto-remove after 4 seconds
        const toastElement = container.lastElementChild;
        setTimeout(() => {
            if (toastElement && toastElement.parentNode) {
                toastElement.remove();
            }
        }, 4000);
    }

    getToastIcon(type) {
        const icons = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        };
        return icons[type] || 'fas fa-info-circle';
    }

    updateUploadButton() {
        const uploadBtn = document.getElementById('upload-btn');
        const fileInput = document.getElementById('file-input');
        
        if (uploadBtn && fileInput) {
            uploadBtn.disabled = fileInput.files.length === 0;
        }
    }

    getFileIcon(mimeType) {
        if (mimeType.includes('pdf')) return 'fas fa-file-pdf text-danger';
        if (mimeType.includes('word')) return 'fas fa-file-word text-primary';
        if (mimeType.includes('text')) return 'fas fa-file-alt text-secondary';
        return 'fas fa-file text-muted';
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    displayAnalysisResult(data) {
        const resultDiv = document.getElementById('analysis-result');
        if (!resultDiv) return;

        let html = '<div class="analysis-results">';
        
        if (data.result) {
            html += `
                <div class="card mb-3">
                    <div class="card-header">
                        <h4><i class="fas fa-file-alt me-2"></i>Analysis Result</h4>
                        <small class="text-muted">Method: ${data.method || 'unknown'}</small>
                    </div>
                    <div class="card-body">
                        <p>${data.result}</p>
                    </div>
                </div>
            `;
        } else {
            html += `
                <div class="card mb-3">
                    <div class="card-body">
                        <p class="text-muted">No analysis result available.</p>
                    </div>
                </div>
            `;
        }

        html += '</div>';
        resultDiv.innerHTML = html;
    }

    displayQueryResult(data) {
        const resultDiv = document.getElementById('query-result');
        if (!resultDiv) return;

        let html = '<div class="query-results">';
        
        if (data.query) {
            html += `
                <div class="card mb-3">
                    <div class="card-header">
                        <h4><i class="fas fa-search me-2"></i>${data.database || 'Legal Database'} Query</h4>
                        <button class="copy-btn" onclick="navigator.clipboard.writeText('${data.query.replace(/'/g, "\\'")}')">
                            <i class="fas fa-copy"></i> Copy
                        </button>
                    </div>
                    <div class="card-body">
                        <code class="query-text">${data.query}</code>
                        ${data.confidence ? `<p class="mt-2"><strong>Confidence:</strong> ${Math.round(data.confidence * 100)}%</p>` : ''}
                    </div>
                </div>
            `;
        }

        if (data.suggestions && data.suggestions.length > 0) {
            html += `
                <div class="card mb-3">
                    <div class="card-header">
                        <h4><i class="fas fa-lightbulb me-2"></i>Suggestions</h4>
                    </div>
                    <div class="card-body">
                        <ul>
                            ${data.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
        }

        html += '</div>';
        resultDiv.innerHTML = html;
    }

    displayAllQueriesResult(data) {
        const resultDiv = document.getElementById('query-result');
        if (!resultDiv) return;

        let html = '<div class="all-queries-results">';
        
        if (data.queries && Array.isArray(data.queries)) {
            data.queries.forEach((queryData, index) => {
                html += `
                    <div class="card mb-4">
                        <div class="card-header">
                            <h4><i class="fas fa-search me-2"></i>${queryData.database || `Database ${index + 1}`} Query</h4>
                        </div>
                        <div class="card-body">
                            <div class="mb-3">
                                <div class="query-header">
                                    <h5>${queryData.database || 'Query'}</h5>
                                    <button class="copy-btn" onclick="navigator.clipboard.writeText('${queryData.query ? queryData.query.replace(/'/g, "\\'") : ''}')">
                                        <i class="fas fa-copy"></i> Copy
                                    </button>
                                </div>
                                <code class="query-text">${queryData.query || 'No query available'}</code>
                                ${queryData.confidence ? `<p class="mt-2"><strong>Confidence:</strong> ${Math.round(queryData.confidence * 100)}%</p>` : ''}
                            </div>
                            
                            ${queryData.suggestions && queryData.suggestions.length > 0 ? `
                                <div class="mt-3">
                                    <h6><i class="fas fa-lightbulb me-2"></i>Suggestions</h6>
                                    <ul>
                                        ${queryData.suggestions.map(suggestion => `<li>${suggestion}</li>`).join('')}
                                    </ul>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            });
        } else {
            html += `
                <div class="card">
                    <div class="card-body">
                        <p class="text-muted">No queries available</p>
                    </div>
                </div>
            `;
        }

        html += '</div>';
        resultDiv.innerHTML = html;
    }

    showSessionInfo(data) {
        const sessionDiv = document.getElementById('session-info');
        if (!sessionDiv) return;

        let html = `
            <div class="alert alert-info">
                <h5><i class="fas fa-info-circle me-2"></i>Session Information</h5>
                <p><strong>Session ID:</strong> ${data.session_id}</p>
                <p><strong>Files:</strong> ${data.file_count} uploaded</p>
                <p><strong>Status:</strong> ${data.status}</p>
            </div>
        `;
        
        sessionDiv.innerHTML = html;
        sessionDiv.style.display = 'block';
    }
}

// Export for use in main app
window.UIManager = UIManager; 