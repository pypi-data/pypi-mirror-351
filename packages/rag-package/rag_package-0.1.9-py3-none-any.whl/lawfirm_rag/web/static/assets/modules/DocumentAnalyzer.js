/**
 * DocumentAnalyzer - Handles document analysis and query generation
 */
class DocumentAnalyzer {
    constructor(app) {
        this.app = app;
    }

    async analyzeDocuments() {
        if (!this.app.currentSession) {
            this.app.uiManager.showToast('No session found. Please upload files first.', 'warning');
            return;
        }

        try {
            const data = await this.app.apiClient.analyzeDocuments(this.app.currentSession);
            
            // Display analysis results
            this.app.uiManager.displayAnalysisResult(data);
            
            // Show analysis section (query section is always visible)
            this.app.uiManager.showSections(['upload-section', 'analysis-section', 'query-section']);
            
            return data;

        } catch (error) {
            console.error('Analysis failed:', error);
            throw error;
        }
    }

    async generateQuery() {
        if (!this.app.currentSession) {
            this.app.uiManager.showToast('No session found. Please upload and analyze files first.', 'warning');
            return;
        }

        const database = document.getElementById('database-select')?.value || 'westlaw';

        try {
            const data = await this.app.apiClient.generateQuery(this.app.currentSession, database);
            
            // Display query results
            this.app.uiManager.displayQueryResult(data);
            
            return data;

        } catch (error) {
            console.error('Query generation failed:', error);
            throw error;
        }
    }

    async generateAllQueries() {
        if (!this.app.currentSession) {
            this.app.uiManager.showToast('No session found. Please upload and analyze files first.', 'warning');
            return;
        }

        try {
            const data = await this.app.apiClient.generateAllQueries(this.app.currentSession);
            
            // Display all queries results
            this.app.uiManager.displayAllQueriesResult(data);
            
            return data;

        } catch (error) {
            console.error('All queries generation failed:', error);
            throw error;
        }
    }
}

// Export for use in main app
window.DocumentAnalyzer = DocumentAnalyzer; 