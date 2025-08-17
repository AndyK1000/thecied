// Drag and Drop Upload JavaScript for Django Admin
document.addEventListener('DOMContentLoaded', function() {
    // Initialize drag and drop for all image fields in drag-drop-upload fieldsets
    const dragDropFieldsets = document.querySelectorAll('.drag-drop-upload');
    
    dragDropFieldsets.forEach(fieldset => {
        const imageFields = fieldset.querySelectorAll('input[type="file"]');
        imageFields.forEach(field => {
            if (field.accept === '' || field.accept.includes('image')) {
                initializeDragDrop(field);
            }
        });
    });
});

function initializeDragDrop(fileInput) {
    const formRow = fileInput.closest('.form-row');
    if (!formRow) return;

    // Create drag and drop zone
    const dropZone = createDropZone(fileInput);
    
    // Hide the original input and insert drop zone
    fileInput.style.display = 'none';
    fileInput.parentNode.insertBefore(dropZone, fileInput);
    
    // Show current file if exists
    showCurrentFile(fileInput, dropZone);
    
    // Set up event listeners
    setupEventListeners(fileInput, dropZone);
}

function createDropZone(fileInput) {
    const dropZone = document.createElement('div');
    dropZone.className = 'drag-drop-zone';
    
    const icon = document.createElement('div');
    icon.className = 'drag-drop-icon';
    icon.innerHTML = '📁'; // Using emoji for cross-browser compatibility
    
    const text = document.createElement('div');
    text.className = 'drag-drop-text';
    text.textContent = 'Drag and drop an image here, or click to browse';
    
    const progressBar = document.createElement('div');
    progressBar.className = 'upload-progress';
    progressBar.innerHTML = '<div class="upload-progress-bar"></div>';
    
    dropZone.appendChild(icon);
    dropZone.appendChild(text);
    dropZone.appendChild(progressBar);
    
    return dropZone;
}

function setupEventListeners(fileInput, dropZone) {
    // Click to open file browser
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files[0], fileInput, dropZone);
    });
    
    // Drag and drop events
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });
    
    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        if (!dropZone.contains(e.relatedTarget)) {
            dropZone.classList.remove('drag-over');
        }
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (isValidImageFile(file)) {
                handleFileSelect(file, fileInput, dropZone);
            } else {
                showError(dropZone, 'Please select a valid image file (JPG, PNG, GIF, WebP)');
            }
        }
    });
}

function handleFileSelect(file, fileInput, dropZone) {
    if (!file) return;
    
    // Validate file
    if (!isValidImageFile(file)) {
        showError(dropZone, 'Please select a valid image file (JPG, PNG, GIF, WebP)');
        return;
    }
    
    // Check file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
        showError(dropZone, 'File size must be less than 10MB');
        return;
    }
    
    // Clear any previous errors
    clearError(dropZone);
    
    // Update drop zone appearance
    dropZone.classList.add('has-file');
    
    // Show preview
    showImagePreview(file, dropZone);
    
    // Update the icon and text
    const icon = dropZone.querySelector('.drag-drop-icon');
    const text = dropZone.querySelector('.drag-drop-text');
    icon.innerHTML = '✅';
    text.textContent = `Selected: ${file.name}`;
    
    // Create a new FileList with the selected file
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    fileInput.files = dataTransfer.files;
    
    // Trigger change event
    fileInput.dispatchEvent(new Event('change', { bubbles: true }));
}

function showCurrentFile(fileInput, dropZone) {
    // Check if there's already a file uploaded
    const currentFileLink = fileInput.parentNode.querySelector('a[href*="media/"]');
    if (currentFileLink) {
        const fileName = currentFileLink.textContent.trim();
        if (fileName && fileName !== 'Currently:') {
            dropZone.classList.add('has-file');
            const icon = dropZone.querySelector('.drag-drop-icon');
            const text = dropZone.querySelector('.drag-drop-text');
            icon.innerHTML = '🖼️';
            text.textContent = `Current file: ${fileName}`;
            
            // Try to show preview if it's an image
            const imageUrl = currentFileLink.href;
            showImagePreviewFromUrl(imageUrl, dropZone);
        }
    }
}

function showImagePreview(file, dropZone) {
    const reader = new FileReader();
    reader.onload = function(e) {
        showImagePreviewFromUrl(e.target.result, dropZone);
    };
    reader.readAsDataURL(file);
}

function showImagePreviewFromUrl(url, dropZone) {
    // Remove any existing preview
    const existingPreview = dropZone.querySelector('.preview-container');
    if (existingPreview) {
        existingPreview.remove();
    }
    
    const previewContainer = document.createElement('div');
    previewContainer.className = 'preview-container';
    
    const img = document.createElement('img');
    img.src = url;
    img.className = 'image-preview';
    img.alt = 'Image preview';
    
    previewContainer.appendChild(img);
    dropZone.appendChild(previewContainer);
}

function isValidImageFile(file) {
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    return validTypes.includes(file.type.toLowerCase());
}

function showError(dropZone, message) {
    clearError(dropZone);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'drag-drop-error';
    errorDiv.textContent = message;
    
    dropZone.parentNode.appendChild(errorDiv);
    
    // Auto-hide error after 5 seconds
    setTimeout(() => {
        clearError(dropZone);
    }, 5000);
}

function clearError(dropZone) {
    const existingError = dropZone.parentNode.querySelector('.drag-drop-error');
    if (existingError) {
        existingError.remove();
    }
}

// Additional utility functions for better UX
function simulateProgress(dropZone) {
    const progressBar = dropZone.querySelector('.upload-progress');
    const progressFill = dropZone.querySelector('.upload-progress-bar');
    
    if (!progressBar || !progressFill) return;
    
    progressBar.style.display = 'block';
    let width = 0;
    
    const interval = setInterval(() => {
        width += 10;
        progressFill.style.width = width + '%';
        
        if (width >= 100) {
            clearInterval(interval);
            setTimeout(() => {
                progressBar.style.display = 'none';
                progressFill.style.width = '0%';
            }, 500);
        }
    }, 50);
}
