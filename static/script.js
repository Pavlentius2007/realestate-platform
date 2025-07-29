// Основной JavaScript для веб-интерфейса транскрибатора

class TranscriberUI {
    constructor() {
        this.currentTaskId = null;
        this.statusInterval = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadTasks();
        this.setupDragAndDrop();
    }

    setupEventListeners() {
        // Форма загрузки
        const uploadForm = document.getElementById('uploadForm');
        uploadForm.addEventListener('submit', (e) => this.handleUpload(e));

        // Выбор файла
        const audioFile = document.getElementById('audioFile');
        audioFile.addEventListener('change', (e) => this.handleFileSelect(e));

        // Кнопка скачивания
        const downloadBtn = document.getElementById('downloadBtn');
        downloadBtn.addEventListener('click', () => this.downloadResult());

        // Обновление истории каждые 5 секунд
        setInterval(() => this.loadTasks(), 5000);
    }

    setupDragAndDrop() {
        const uploadZone = document.getElementById('uploadZone');
        const audioFile = document.getElementById('audioFile');

        // Drag and drop события
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                audioFile.files = files;
                this.handleFileSelect({ target: audioFile });
            }
        });

        // Клик по зоне загрузки
        uploadZone.addEventListener('click', () => {
            audioFile.click();
        });
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.showSelectedFile(file);
            this.enableSubmitButton();
        }
    }

    showSelectedFile(file) {
        const selectedFile = document.getElementById('selectedFile');
        const fileName = document.getElementById('fileName');
        
        fileName.textContent = `${file.name} (${this.formatFileSize(file.size)})`;
        selectedFile.classList.remove('d-none');
        selectedFile.classList.add('fade-in');
    }

    clearFile() {
        const audioFile = document.getElementById('audioFile');
        const selectedFile = document.getElementById('selectedFile');
        
        audioFile.value = '';
        selectedFile.classList.add('d-none');
        this.disableSubmitButton();
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    enableSubmitButton() {
        const submitBtn = document.getElementById('submitBtn');
        submitBtn.disabled = false;
        submitBtn.classList.remove('btn-secondary');
        submitBtn.classList.add('btn-primary');
    }

    disableSubmitButton() {
        const submitBtn = document.getElementById('submitBtn');
        submitBtn.disabled = true;
        submitBtn.classList.remove('btn-primary');
        submitBtn.classList.add('btn-secondary');
    }

    async handleUpload(event) {
        event.preventDefault();
        
        const formData = new FormData(event.target);
        const file = formData.get('file');
        
        if (!file) {
            this.showError('Пожалуйста, выберите файл');
            return;
        }

        try {
            this.showProgress();
            this.disableSubmitButton();
            
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            this.currentTaskId = result.task_id;
            
            this.updateProgressText('Файл загружен, начинаем обработку...');
            this.startStatusPolling();

        } catch (error) {
            console.error('Upload error:', error);
            this.showError('Ошибка при загрузке файла: ' + error.message);
            this.hideProgress();
            this.enableSubmitButton();
        }
    }

    showProgress() {
        const progressSection = document.getElementById('progressSection');
        progressSection.classList.remove('d-none');
        progressSection.classList.add('fade-in');
        
        this.hideResult();
        this.hideError();
    }

    hideProgress() {
        const progressSection = document.getElementById('progressSection');
        progressSection.classList.add('d-none');
    }

    updateProgress(percent, text) {
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');
        
        progressBar.style.width = `${percent}%`;
        progressBar.textContent = `${percent}%`;
        progressText.textContent = text;
    }

    updateProgressText(text) {
        const progressText = document.getElementById('progressText');
        progressText.textContent = text;
    }

    startStatusPolling() {
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
        }

        this.statusInterval = setInterval(() => {
            this.checkStatus();
        }, 2000);
    }

    stopStatusPolling() {
        if (this.statusInterval) {
            clearInterval(this.statusInterval);
            this.statusInterval = null;
        }
    }

    async checkStatus() {
        if (!this.currentTaskId) return;

        try {
            const response = await fetch(`/status/${this.currentTaskId}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const status = await response.json();
            
            this.updateProgress(status.progress, this.getStatusText(status.status));
            
            if (status.status === 'completed') {
                this.stopStatusPolling();
                this.showResult(status);
            } else if (status.status === 'error') {
                this.stopStatusPolling();
                this.showError(status.error || 'Произошла ошибка при обработке');
            }

        } catch (error) {
            console.error('Status check error:', error);
            this.stopStatusPolling();
            this.showError('Ошибка при проверке статуса: ' + error.message);
        }
    }

    getStatusText(status) {
        const statusTexts = {
            'pending': 'Ожидание обработки...',
            'processing': 'Обработка аудио...',
            'completed': 'Завершено!',
            'error': 'Ошибка обработки'
        };
        return statusTexts[status] || 'Обработка...';
    }

    showResult(status) {
        this.hideProgress();
        
        const resultSection = document.getElementById('resultSection');
        const transcriptPreview = document.getElementById('transcriptPreview');
        
        // Загружаем предварительный просмотр
        this.loadTranscriptPreview(status.result_path, transcriptPreview);
        
        resultSection.classList.remove('d-none');
        resultSection.classList.add('fade-in');
        
        // Сохраняем путь для скачивания
        this.currentResultPath = status.download_url;
    }

    hideResult() {
        const resultSection = document.getElementById('resultSection');
        resultSection.classList.add('d-none');
    }

    async loadTranscriptPreview(resultPath, container) {
        try {
            const response = await fetch(`/download/${this.currentTaskId}`);
            if (!response.ok) {
                throw new Error('Не удалось загрузить результат');
            }

            const text = await response.text();
            
            // Показываем первые 500 символов
            const preview = text.length > 500 ? text.substring(0, 500) + '...' : text;
            container.textContent = preview;
            
        } catch (error) {
            console.error('Preview load error:', error);
            container.textContent = 'Не удалось загрузить предварительный просмотр';
        }
    }

    downloadResult() {
        if (this.currentResultPath) {
            window.open(this.currentResultPath, '_blank');
        }
    }

    showError(message) {
        this.hideProgress();
        this.hideResult();
        
        const errorSection = document.getElementById('errorSection');
        const errorMessage = document.getElementById('errorMessage');
        
        errorMessage.textContent = message;
        errorSection.classList.remove('d-none');
        errorSection.classList.add('fade-in');
        
        this.enableSubmitButton();
    }

    hideError() {
        const errorSection = document.getElementById('errorSection');
        errorSection.classList.add('d-none');
    }

    resetForm() {
        this.clearFile();
        this.hideProgress();
        this.hideResult();
        this.hideError();
        this.stopStatusPolling();
        this.currentTaskId = null;
        this.currentResultPath = null;
    }

    async loadTasks() {
        try {
            const response = await fetch('/tasks');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            this.renderTasks(data.tasks);

        } catch (error) {
            console.error('Load tasks error:', error);
        }
    }

    renderTasks(tasks) {
        const tasksList = document.getElementById('tasksList');
        
        if (tasks.length === 0) {
            tasksList.innerHTML = '<p class="text-muted text-center">Нет задач</p>';
            return;
        }

        const tasksHtml = tasks.map(task => this.renderTaskItem(task)).join('');
        tasksList.innerHTML = tasksHtml;
    }

    renderTaskItem(task) {
        const statusClass = `task-status ${task.status}`;
        const statusText = this.getStatusText(task.status);
        
        return `
            <div class="task-item">
                <div class="row align-items-center">
                    <div class="col-md-6">
                        <h6 class="mb-1">${task.filename}</h6>
                        <small class="text-muted">ID: ${task.task_id}</small>
                    </div>
                    <div class="col-md-3">
                        <span class="${statusClass}">${statusText}</span>
                    </div>
                    <div class="col-md-3 text-end">
                        ${task.status === 'completed' ? 
                            `<button class="btn btn-sm btn-success" onclick="transcriberUI.downloadTask('${task.task_id}')">
                                <i class="fas fa-download"></i> Скачать
                            </button>` : 
                            `<div class="progress" style="height: 20px;">
                                <div class="progress-bar" style="width: ${task.progress}%">${task.progress}%</div>
                            </div>`
                        }
                        <button class="btn btn-sm btn-outline-danger ms-2" onclick="transcriberUI.deleteTask('${task.task_id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    async downloadTask(taskId) {
        try {
            window.open(`/download/${taskId}`, '_blank');
        } catch (error) {
            console.error('Download error:', error);
            this.showError('Ошибка при скачивании файла');
        }
    }

    async deleteTask(taskId) {
        if (!confirm('Вы уверены, что хотите удалить эту задачу?')) {
            return;
        }

        try {
            const response = await fetch(`/tasks/${taskId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            // Обновляем список задач
            this.loadTasks();

        } catch (error) {
            console.error('Delete error:', error);
            this.showError('Ошибка при удалении задачи');
        }
    }
}

// Функции для глобального доступа
function copyToClipboard() {
    const transcriptPreview = document.getElementById('transcriptPreview');
    const text = transcriptPreview.textContent;
    
    navigator.clipboard.writeText(text).then(() => {
        // Показываем уведомление
        const notification = document.createElement('div');
        notification.className = 'alert alert-success position-fixed';
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
        notification.textContent = 'Текст скопирован в буфер обмена!';
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }).catch(err => {
        console.error('Copy error:', err);
        alert('Ошибка при копировании в буфер обмена');
    });
}

function clearFile() {
    transcriberUI.clearFile();
}

function resetForm() {
    transcriberUI.resetForm();
}

// Инициализация при загрузке страницы
let transcriberUI;
document.addEventListener('DOMContentLoaded', () => {
    transcriberUI = new TranscriberUI();
});

// Экспорт для глобального доступа
window.transcriberUI = transcriberUI; 