/**
 * FileHandler - Handles file selection, upload, and management
 */
class FileHandler {
    constructor(app) {
        this.app = app;
        this.selectedFiles = [];
    }

    handleFileSelect(files) {
        this.selectedFiles = Array.from(files);
        this.updateFileList();
        this.app.uiManager.updateUploadButton();
    }

    updateFileList() {
        const fileList = document.getElementById('file-list');
        if (!fileList) return;

        if (this.selectedFiles.length === 0) {
            fileList.innerHTML = '<p class="text-muted">No files selected</p>';
            return;
        }

        let html = '<div class="selected-files">';
        this.selectedFiles.forEach((file, index) => {
            html += `
                <div class="file-item d-flex justify-content-between align-items-center p-2 border rounded mb-2">
                    <div class="file-info d-flex align-items-center">
                        <i class="${this.app.uiManager.getFileIcon(file.type)} me-2"></i>
                        <div>
                            <div class="file-name">${file.name}</div>
                            <small class="text-muted">${this.app.uiManager.formatFileSize(file.size)}</small>
                        </div>
                    </div>
                    <button class="btn btn-sm btn-outline-danger" onclick="app.fileHandler.removeFile(${index})">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
        });
        html += '</div>';
        
        fileList.innerHTML = html;
    }

    removeFile(index) {
        this.selectedFiles.splice(index, 1);
        this.updateFileList();
        this.app.uiManager.updateUploadButton();
    }

    async uploadFiles() {
        if (this.selectedFiles.length === 0) {
            this.app.uiManager.showToast('Please select files to upload', 'warning');
            return;
        }

        try {
            const data = await this.app.apiClient.uploadFiles(this.selectedFiles);
            
            // Store session info
            this.app.currentSession = data.session_id;
            
            // Show session info
            this.app.uiManager.showSessionInfo({
                session_id: data.session_id,
                file_count: data.file_count,
                status: 'Uploaded'
            });
            
            // Show next sections
            this.app.uiManager.showSections(['upload-section', 'analysis-section', 'query-section']);
            
            // Clear file selection
            this.selectedFiles = [];
            this.updateFileList();
            
            // Reset file input
            const fileInput = document.getElementById('file-input');
            if (fileInput) fileInput.value = '';
            
            this.app.uiManager.updateUploadButton();
            
            return data;

        } catch (error) {
            console.error('Upload failed:', error);
            throw error;
        }
    }

    setupFileInput() {
        const fileInput = document.getElementById('file-input');
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                this.handleFileSelect(e.target.files);
            });
        }
    }

    setupDragAndDrop() {
        const dropZone = document.getElementById('drop-zone');
        if (!dropZone) return;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        // Highlight drop zone when dragging over it
        ['dragenter', 'dragover'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.add('drag-over');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropZone.addEventListener(eventName, () => {
                dropZone.classList.remove('drag-over');
            });
        });

        // Handle dropped files
        dropZone.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            this.handleFileSelect(files);
            
            // Update the file input to match
            const fileInput = document.getElementById('file-input');
            if (fileInput) {
                fileInput.files = files;
            }
        });
    }

    init() {
        this.setupFileInput();
        this.setupDragAndDrop();
    }
}

// Export for use in main app
window.FileHandler = FileHandler; 