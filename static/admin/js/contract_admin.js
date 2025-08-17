document.addEventListener('DOMContentLoaded', function() {
    // Function to toggle roe_end field based on on_going checkbox
    function toggleEndDate() {
        const onGoingCheckbox = document.getElementById('id_on_going');
        const roeEndField = document.getElementById('id_roe_end');
        const roeEndLabel = document.querySelector('label[for="id_roe_end"]');
        const roeEndWrapper = roeEndField ? roeEndField.closest('.field-roe_end') : null;
        
        if (onGoingCheckbox && roeEndField) {
            if (onGoingCheckbox.checked) {
                roeEndField.disabled = true;
                roeEndField.value = '';
                roeEndField.style.backgroundColor = '#f0f0f0';
                if (roeEndLabel) {
                    roeEndLabel.style.color = '#999';
                }
                if (roeEndWrapper) {
                    roeEndWrapper.style.opacity = '0.5';
                }
            } else {
                roeEndField.disabled = false;
                roeEndField.style.backgroundColor = '';
                if (roeEndLabel) {
                    roeEndLabel.style.color = '';
                }
                if (roeEndWrapper) {
                    roeEndWrapper.style.opacity = '1';
                }
            }
        }
    }
    
    // Add event listener to on_going checkbox
    const onGoingCheckbox = document.getElementById('id_on_going');
    if (onGoingCheckbox) {
        onGoingCheckbox.addEventListener('change', toggleEndDate);
        // Initialize state
        toggleEndDate();
    }
    
    // Add HTML5 date input type to date fields
    const dateFields = ['id_roe_begin', 'id_roe_end', 'id_dob'];
    dateFields.forEach(function(fieldId) {
        const field = document.getElementById(fieldId);
        if (field && field.type === 'text') {
            field.type = 'date';
            field.style.width = '150px';
        }
    });
    
    // Add drag and drop functionality for image fields
    function addDragDropToImageField(fieldId) {
        const fileInput = document.getElementById(fieldId);
        if (!fileInput) return;
        
        const wrapper = fileInput.parentElement;
        wrapper.style.position = 'relative';
        wrapper.style.border = '2px dashed #ddd';
        wrapper.style.padding = '20px';
        wrapper.style.borderRadius = '5px';
        wrapper.style.transition = 'border-color 0.3s ease';
        
        // Create drag drop overlay
        const overlay = document.createElement('div');
        overlay.innerHTML = '<p>Drag and drop image here or click to browse</p>';
        overlay.style.position = 'absolute';
        overlay.style.top = '0';
        overlay.style.left = '0';
        overlay.style.right = '0';
        overlay.style.bottom = '0';
        overlay.style.display = 'flex';
        overlay.style.alignItems = 'center';
        overlay.style.justifyContent = 'center';
        overlay.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
        overlay.style.pointerEvents = 'none';
        overlay.style.zIndex = '1';
        
        wrapper.appendChild(overlay);
        
        // Drag events
        wrapper.addEventListener('dragover', function(e) {
            e.preventDefault();
            wrapper.style.borderColor = '#007cba';
            wrapper.style.backgroundColor = '#f0f8ff';
        });
        
        wrapper.addEventListener('dragleave', function(e) {
            wrapper.style.borderColor = '#ddd';
            wrapper.style.backgroundColor = '';
        });
        
        wrapper.addEventListener('drop', function(e) {
            e.preventDefault();
            wrapper.style.borderColor = '#ddd';
            wrapper.style.backgroundColor = '';
            
            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].type.startsWith('image/')) {
                fileInput.files = files;
                overlay.innerHTML = '<p>Image selected: ' + files[0].name + '</p>';
            }
        });
        
        // Update overlay when file is selected normally
        fileInput.addEventListener('change', function(e) {
            if (e.target.files.length > 0) {
                overlay.innerHTML = '<p>Image selected: ' + e.target.files[0].name + '</p>';
            } else {
                overlay.innerHTML = '<p>Drag and drop image here or click to browse</p>';
            }
        });
    }
    
    // Apply drag and drop to image fields
    const imageFields = ['id_photo', 'id_logo', 'id_image'];
    imageFields.forEach(addDragDropToImageField);
});
