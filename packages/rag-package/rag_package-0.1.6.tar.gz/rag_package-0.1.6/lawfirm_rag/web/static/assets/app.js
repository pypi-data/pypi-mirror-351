// LawFirm-RAG Frontend Application
console.log('🔥 JavaScript modules loading...');

class LawFirmRAG {
    constructor() {
        console.log('🚀 LawFirmRAG constructor called - JavaScript is loading!');
        this.currentSession = null;
        
        // Initialize managers
        this.uiManager = new UIManager(this);
        this.apiClient = new ApiClient(this);
        this.modelManager = new ModelManager(this);
        this.fileHandler = new FileHandler(this);
        this.documentAnalyzer = new DocumentAnalyzer(this);
        
        console.log('📋 All managers initialized, calling init()...');
        this.init();
    }

    init() {
        console.log('🔧 LawFirmRAG init() called');
        this.setupEventListeners();
        this.apiClient.checkHealth();
        this.modelManager.updateModelStatus();
        this.fileHandler.init();
        console.log('✅ LawFirmRAG initialization complete');
    }

    setupEventListeners() {
        // Upload button
        const uploadBtn = document.getElementById('upload-btn');
        if (uploadBtn) {
            uploadBtn.addEventListener('click', () => this.fileHandler.uploadFiles());
        }

        // Analyze button
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.documentAnalyzer.analyzeDocuments());
        }

        // Generate query button
        const generateQueryBtn = document.getElementById('generate-query-btn');
        if (generateQueryBtn) {
            generateQueryBtn.addEventListener('click', () => this.documentAnalyzer.generateQuery());
        }

        // Generate all queries button
        const generateAllBtn = document.getElementById('generate-all-btn');
        if (generateAllBtn) {
            generateAllBtn.addEventListener('click', () => this.documentAnalyzer.generateAllQueries());
        }

        // Model management modal trigger
        const modelStatusDiv = document.querySelector('.model-status');
        if (modelStatusDiv) {
            modelStatusDiv.addEventListener('click', () => this.modelManager.showModelManager());
        }
    }

    // Proxy methods for legacy inline event handlers
    showModelManager() {
        this.modelManager.showModelManager();
    }

    hideModelManager() {
        this.modelManager.hideModelManager();
    }

    loadAndDisplayModels() {
        this.modelManager.updateAvailableModelsDisplay();
    }
}

// Initialize the application
console.log('🌟 Creating LawFirmRAG instance...');
const app = new LawFirmRAG();
console.log('🎯 LawFirmRAG instance created successfully:', app);

// Make app globally available for inline event handlers
window.app = app; 