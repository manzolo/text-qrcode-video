// Additional JavaScript functionality
class QRVideoEncoder {
    constructor() {
        this.initEventListeners();
        this.checkServerHealth();
    }

    initEventListeners() {
        // Add keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'e') {
                e.preventDefault();
                switchTab('encode');
            } else if (e.ctrlKey && e.key === 'd') {
                e.preventDefault();
                switchTab('decode');
            }
        });

        // Auto-save text to localStorage
        const textInput = document.getElementById('text-input');
        if (textInput) {
            textInput.addEventListener('input', () => {
                localStorage.setItem('draft-text', textInput.value);
            });

            // Restore draft on load
            const draft = localStorage.getItem('draft-text');
            if (draft) {
                textInput.value = draft;
            }
        }
    }

    async checkServerHealth() {
        try {
            const response = await fetch('/health');
            const data = await response.json();
            if (data.status !== 'healthy') {
                this.showNotification('Server is not responding correctly', 'error');
            }
        } catch (error) {
            this.showNotification('Cannot connect to server', 'error');
        }
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 20px;
            background: ${type === 'error' ? '#f44336' : '#4CAF50'};
            color: white;
            border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            z-index: 1000;
            animation: slideIn 0.3s ease;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    formatBytes(bytes) {
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        if (bytes === 0) return '0 Bytes';
        const i = Math.floor(Math.log(bytes) / Math.log(1024));
        return Math.round(bytes / Math.pow(1024, i) * 100) / 100 + ' ' + sizes[i];
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    new QRVideoEncoder();
});