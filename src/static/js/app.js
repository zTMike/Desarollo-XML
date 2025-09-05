/**
 * Procesador de Facturas XML - JavaScript
 * Versión 2.0.0
 */

class InvoiceProcessor {
    constructor() {
        this.selectedFiles = [];
        this.currentFileId = null;
        this.initializeElements();
        this.bindEvents();
    }

    initializeElements() {
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.submitBtn = document.getElementById('submitBtn');
        this.progressContainer = document.getElementById('progressContainer');
        this.progressBar = document.getElementById('progressBar');
        this.progressText = document.getElementById('progressText');
        this.form = document.getElementById('uploadForm');
        this.fileList = document.getElementById('fileList');
        this.fileCounter = document.getElementById('fileCounter');
        this.fileCount = document.getElementById('fileCount');
        this.errorContainer = document.getElementById('error-container');
        this.errorMessage = document.getElementById('error-message');
        this.successContainer = document.getElementById('success-container');
        this.successMessage = document.getElementById('success-message');
        this.uploadSection = document.getElementById('upload-section');
        this.resultsSection = document.getElementById('results-section');
        this.statsGrid = document.getElementById('statsGrid');
        this.downloadBtn = document.getElementById('downloadBtn');
    }

    bindEvents() {
        // Drag and drop functionality
        this.uploadArea.addEventListener('dragover', this.handleDragOver.bind(this));
        this.uploadArea.addEventListener('dragleave', this.handleDragLeave.bind(this));
        this.uploadArea.addEventListener('drop', this.handleDrop.bind(this));

        // File input change
        this.fileInput.addEventListener('change', this.handleFileSelect.bind(this));

        // Form submission
        this.form.addEventListener('submit', this.handleFormSubmit.bind(this));

        // Click on upload area
        this.uploadArea.addEventListener('click', (e) => {
            if (e.target.tagName !== 'BUTTON') {
                this.fileInput.click();
            }
        });
    }

    handleDragOver(e) {
        e.preventDefault();
        this.uploadArea.classList.add('dragover');
    }

    handleDragLeave() {
        this.uploadArea.classList.remove('dragover');
    }

    handleDrop(e) {
        e.preventDefault();
        this.uploadArea.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files);
        const zipFiles = files.filter(file => file.name.toLowerCase().endsWith('.zip'));
        
        if (zipFiles.length > 0) {
            this.addFiles(zipFiles);
        } else {
            this.showError('Por favor arrastra solo archivos ZIP');
        }
    }

    handleFileSelect(e) {
        const files = Array.from(e.target.files);
        this.addFiles(files);
        e.target.value = ''; // Limpiar input
    }

    addFiles(files) {
        const newFiles = files.filter(file => {
            if (!file.name.toLowerCase().endsWith('.zip')) {
                return false;
            }
            // Evitar duplicados
            return !this.selectedFiles.find(f => f.name === file.name && f.size === file.size);
        });
        
        // Sin límite de archivos - solo verificar que no sea excesivo para evitar problemas de memoria
        if (this.selectedFiles.length + newFiles.length > 1000) {
            this.showError('Demasiados archivos seleccionados (máximo 1000 para evitar problemas de rendimiento)');
            return;
        }
        
        this.selectedFiles.push(...newFiles);
        this.updateFileList();
        this.updateSubmitButton();
        this.updateFileCounter();
    }

    removeFile(fileName) {
        this.selectedFiles = this.selectedFiles.filter(file => file.name !== fileName);
        this.updateFileList();
        this.updateSubmitButton();
        this.updateFileCounter();
    }

    updateFileList() {
        this.fileList.innerHTML = '';
        this.selectedFiles.forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div>
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${this.formatFileSize(file.size)}</div>
                </div>
                <button type="button" class="remove-file" onclick="app.removeFile('${file.name}')">
                    <i class="fas fa-times"></i>
                </button>
            `;
            this.fileList.appendChild(fileItem);
        });
    }

    updateFileCounter() {
        this.fileCount.textContent = this.selectedFiles.length;
        this.fileCounter.style.display = this.selectedFiles.length > 0 ? 'block' : 'none';
    }

    updateSubmitButton() {
        this.submitBtn.disabled = this.selectedFiles.length === 0;
        if (this.selectedFiles.length > 0) {
            this.showSuccess(`${this.selectedFiles.length} archivo(s) ZIP seleccionado(s)`);
        } else {
            this.hideMessages();
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    async handleFormSubmit(e) {
        e.preventDefault();
        
        if (this.selectedFiles.length === 0) {
            this.showError('No hay archivos seleccionados');
            return;
        }
        
        const formData = new FormData();
        this.selectedFiles.forEach(file => {
            formData.append('zip_files', file);
        });
        
        this.submitBtn.disabled = true;
        this.submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
        this.showProgress(10);
        
        try {
            this.showSuccess('Iniciando procesamiento...');
            this.showProgress(30);
            
            console.log('Enviando', this.selectedFiles.length, 'archivos al servidor...');
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData,
                signal: AbortSignal.timeout(300000), // 5 minutos timeout
            });
            
            this.showProgress(80);
            console.log('Respuesta recibida:', response.status, response.statusText);
            
            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    this.currentFileId = data.file_id;
                    this.showResults(data);
                    this.showProgress(100);
                } else {
                    this.showError(data.message || 'Error desconocido en el procesamiento');
                }
            } else {
                const errorData = await response.json();
                this.showError(errorData.message || `Error del servidor: ${response.status}`);
            }
        } catch (error) {
            console.error('Error completo:', error);
            
            if (error.name === 'AbortError') {
                this.showError('Error: Tiempo de espera agotado. Los archivos pueden ser muy grandes.');
            } else if (error.name === 'TypeError' && error.message.includes('fetch')) {
                this.showError('Error de conexión: No se puede conectar al servidor. Verifica que la aplicación esté ejecutándose.');
            } else {
                this.showError('Error de conexión: ' + error.message);
            }
        } finally {
            this.submitBtn.disabled = false;
            this.submitBtn.innerHTML = '<i class="fas fa-cogs"></i> Procesar Facturas';
            this.hideProgress();
        }
    }

    showResults(data) {
        this.uploadSection.style.display = 'none';
        this.resultsSection.style.display = 'block';
        
        // Configurar botón de descarga
        this.downloadBtn.href = `/download/${data.file_id}`;
        this.downloadBtn.onclick = () => {
            this.cleanupFile(data.file_id);
        };
        
        // Mostrar estadísticas
        this.displayStats(data);
        
        this.showSuccess(`Procesamiento completado. ${data.stats.filas_totales} registros procesados.`);
    }

    displayStats(data) {
        const stats = data.stats;
        this.statsGrid.innerHTML = `
            <div class="stat-item">
                <div class="stat-number">${stats.filas_totales}</div>
                <div class="stat-label">Registros Procesados</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">${stats.archivos_procesados}</div>
                <div class="stat-label">Archivos Procesados</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">${stats.facturas_extraidas}</div>
                <div class="stat-label">Facturas Extraídas</div>
            </div>
            <div class="stat-item">
                <div class="stat-number">${stats.fecha_procesamiento}</div>
                <div class="stat-label">Fecha de Procesamiento</div>
            </div>
            </div>
        `;
    }

    async cleanupFile(fileId) {
        try {
            await fetch('/cleanup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ file_id: fileId })
            });
        } catch (error) {
            console.error('Error limpiando archivo:', error);
        }
    }

    resetForm() {
        this.selectedFiles = [];
        this.currentFileId = null;
        this.uploadSection.style.display = 'block';
        this.resultsSection.style.display = 'none';
        this.updateFileList();
        this.updateSubmitButton();
        this.updateFileCounter();
        this.hideMessages();
    }

    showProgress(percent) {
        this.progressContainer.style.display = 'block';
        this.progressBar.style.width = percent + '%';
    }

    hideProgress() {
        this.progressContainer.style.display = 'none';
    }

    showError(message) {
        this.errorMessage.textContent = message;
        this.errorContainer.style.display = 'flex';
        this.successContainer.style.display = 'none';
    }

    showSuccess(message) {
        this.successMessage.textContent = message;
        this.successContainer.style.display = 'flex';
        this.errorContainer.style.display = 'none';
    }

    hideMessages() {
        this.errorContainer.style.display = 'none';
        this.successContainer.style.display = 'none';
    }
}

// Función global para resetear el formulario
function resetForm() {
    app.resetForm();
}

// Inicializar la aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.app = new InvoiceProcessor();
});
