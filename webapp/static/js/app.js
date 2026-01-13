// Tab Switching
const tabButtons = document.querySelectorAll('.tab-button');
const tabContents = document.querySelectorAll('.tab-content');

tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        const tabName = button.getAttribute('data-tab');

        // Remove active class from all tabs
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));

        // Add active class to clicked tab
        button.classList.add('active');
        document.getElementById(`${tabName}-tab`).classList.add('active');
    });
});

// Alert Functions
function showAlert(elementId, message, type) {
    const alert = document.getElementById(elementId);
    alert.textContent = message;
    alert.className = `alert alert-${type} show`;

    setTimeout(() => {
        alert.classList.remove('show');
    }, 5000);
}

function hideAlert(elementId) {
    const alert = document.getElementById(elementId);
    alert.classList.remove('show');
}

// Loading State
function setButtonLoading(button, isLoading) {
    const btnText = button.querySelector('.btn-text');

    if (isLoading) {
        button.disabled = true;
        btnText.innerHTML = '<span class="spinner"></span> Generating...';
    } else {
        button.disabled = false;
        btnText.textContent = 'Generate Data';
    }
}

// Download File
function downloadFile(blob, filename) {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    document.body.removeChild(a);
}

// ============================================
// PROMPT-BASED GENERATION
// ============================================
const promptForm = document.getElementById('prompt-form');

promptForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = promptForm.querySelector('button[type="submit"]');
    const prompt = document.getElementById('prompt-input').value.trim();
    const rows = parseInt(document.getElementById('prompt-rows').value);
    const format = document.getElementById('prompt-format').value;

    if (!prompt) {
        showAlert('prompt-alert', 'Please enter a data description', 'error');
        return;
    }

    if (rows < 1 || rows > 100000) {
        showAlert('prompt-alert', 'Number of rows must be between 1 and 100,000', 'error');
        return;
    }

    hideAlert('prompt-alert');
    setButtonLoading(submitBtn, true);

    try {
        const response = await fetch('/api/generate/prompt', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ prompt, rows, format })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Generation failed');
        }

        const blob = await response.blob();
        downloadFile(blob, `synthetic_data.${format}`);
        showAlert('prompt-alert', `✅ Successfully generated ${rows} rows!`, 'success');

    } catch (error) {
        showAlert('prompt-alert', `❌ Error: ${error.message}`, 'error');
    } finally {
        setButtonLoading(submitBtn, false);
    }
});

// ============================================
// FILE-BASED GENERATION
// ============================================
const fileForm = document.getElementById('file-form');
const fileInput = document.getElementById('file-input');
const fileUploadArea = document.getElementById('file-upload-area');
const fileName = document.getElementById('file-name');

// Click to upload
fileUploadArea.addEventListener('click', () => {
    fileInput.click();
});

// File selection
fileInput.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        fileName.textContent = `Selected: ${file.name}`;
    }
});

// Drag and drop
fileUploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    fileUploadArea.classList.add('dragover');
});

fileUploadArea.addEventListener('dragleave', () => {
    fileUploadArea.classList.remove('dragover');
});

fileUploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    fileUploadArea.classList.remove('dragover');

    const file = e.dataTransfer.files[0];
    if (file) {
        // Check file type
        const validTypes = ['text/csv', 'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
        const validExtensions = ['.csv', '.xlsx', '.xls'];
        const hasValidExtension = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));

        if (validTypes.includes(file.type) || hasValidExtension) {
            fileInput.files = e.dataTransfer.files;
            fileName.textContent = `Selected: ${file.name}`;
        } else {
            showAlert('file-alert', 'Invalid file type. Please upload CSV or Excel files.', 'error');
        }
    }
});

// Form submission
fileForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = fileForm.querySelector('button[type="submit"]');
    const file = fileInput.files[0];
    const rows = parseInt(document.getElementById('file-rows').value);
    const format = document.getElementById('file-format').value;
    const preserveStats = document.getElementById('preserve-stats').checked;

    if (!file) {
        showAlert('file-alert', 'Please select a file to upload', 'error');
        return;
    }

    if (rows < 1 || rows > 100000) {
        showAlert('file-alert', 'Number of rows must be between 1 and 100,000', 'error');
        return;
    }

    hideAlert('file-alert');
    setButtonLoading(submitBtn, true);

    try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('rows', rows);
        formData.append('format', format);
        formData.append('preserve_stats', preserveStats);

        const response = await fetch('/api/generate/file', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Generation failed');
        }

        const blob = await response.blob();
        downloadFile(blob, `synthetic_data.${format}`);
        showAlert('file-alert', `✅ Successfully generated ${rows} rows!`, 'success');

    } catch (error) {
        showAlert('file-alert', `❌ Error: ${error.message}`, 'error');
    } finally {
        setButtonLoading(submitBtn, false);
    }
});

// ============================================
// SCHEMA-BASED GENERATION
// ============================================
const schemaForm = document.getElementById('schema-form');

schemaForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const submitBtn = schemaForm.querySelector('button[type="submit"]');
    const schemaText = document.getElementById('schema-input').value.trim();
    const rows = parseInt(document.getElementById('schema-rows').value);
    const format = document.getElementById('schema-format').value;

    if (!schemaText) {
        showAlert('schema-alert', 'Please enter a JSON schema', 'error');
        return;
    }

    // Validate JSON
    let schema;
    try {
        schema = JSON.parse(schemaText);
    } catch (error) {
        showAlert('schema-alert', 'Invalid JSON format. Please check your schema.', 'error');
        return;
    }

    if (rows < 1 || rows > 100000) {
        showAlert('schema-alert', 'Number of rows must be between 1 and 100,000', 'error');
        return;
    }

    hideAlert('schema-alert');
    setButtonLoading(submitBtn, true);

    try {
        const response = await fetch('/api/generate/schema', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ schema, rows, format })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Generation failed');
        }

        const blob = await response.blob();
        downloadFile(blob, `synthetic_data.${format}`);
        showAlert('schema-alert', `✅ Successfully generated ${rows} rows!`, 'success');

    } catch (error) {
        showAlert('schema-alert', `❌ Error: ${error.message}`, 'error');
    } finally {
        setButtonLoading(submitBtn, false);
    }
});

// ============================================
// TIME SERIES GENERATION
// ============================================
const tsForm = document.getElementById('timeseries-form');
const tsInput = document.getElementById('timeseries-file-input');
const tsUploadArea = document.getElementById('timeseries-file-upload-area');
const tsFileName = document.getElementById('timeseries-file-name');

// Only attach handlers if elements exist (to avoid errors)
if (tsUploadArea && tsInput && tsForm && tsFileName) {
    // Click to upload
    tsUploadArea.addEventListener('click', () => {
        tsInput.click();
    });

    // File selection
    tsInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (file) {
            tsFileName.textContent = `Selected: ${file.name}`;
        }
    });

    // Drag and drop
    tsUploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        tsUploadArea.classList.add('dragover');
    });

    tsUploadArea.addEventListener('dragleave', () => {
        tsUploadArea.classList.remove('dragover');
    });

    tsUploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        tsUploadArea.classList.remove('dragover');

        const file = e.dataTransfer.files[0];
        if (file) {
            const validExtensions = ['.csv'];
            const hasValidExtension = validExtensions.some(ext => file.name.toLowerCase().endsWith(ext));

            if (hasValidExtension) {
                tsInput.files = e.dataTransfer.files;
                tsFileName.textContent = `Selected: ${file.name}`;
            } else {
                showAlert('timeseries-alert', 'Invalid file type. Please upload a CSV file.', 'error');
            }
        }
    });

    // Form submission
    tsForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const submitBtn = tsForm.querySelector('button[type="submit"]');
        const rows = parseInt(document.getElementById('timeseries-rows').value);
        const file = tsInput.files[0];

        if (!file) {
            showAlert('timeseries-alert', 'Please select a CSV file to upload', 'error');
            return;
        }

        if (rows < 1 || rows > 100000) {
            showAlert('timeseries-alert', 'Number of rows must be between 1 and 100,000', 'error');
            return;
        }

        hideAlert('timeseries-alert');

        const btnText = submitBtn.querySelector('.btn-text');
        const originalText = btnText.textContent;
        submitBtn.disabled = true;
        btnText.innerHTML = '<span class="spinner"></span> Generating...';

        try {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('rows', rows);

            const response = await fetch('/api/generate/timeseries', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                let errorMsg = 'Generation failed';
                try {
                    const error = await response.json();
                    errorMsg = error.error || errorMsg;
                } catch (_) {}
                throw new Error(errorMsg);
            }

            const blob = await response.blob();
            downloadFile(blob, 'synthetic_timeseries_data.csv');
            showAlert('timeseries-alert', `✅ Successfully generated ${rows} synthetic time series rows!`, 'success');

        } catch (error) {
            showAlert('timeseries-alert', `❌ Error: ${error.message}`, 'error');
        } finally {
            submitBtn.disabled = false;
            btnText.textContent = originalText;
        }
    });
}

// ============================================
// EDA REPORT GENERATION (ydata-profiling)
// ============================================
const edaButton = document.getElementById('eda-button');
const edaFileInput = document.getElementById('eda-file-input');
const edaAlert = document.getElementById('eda-alert');

if (edaButton && edaFileInput && edaAlert) {
    // When button is clicked, ask for file
    edaButton.addEventListener('click', () => {
        hideAlert('eda-alert');
        edaFileInput.value = ''; // reset
        edaFileInput.click();
    });

    // When file is selected, upload & generate report
    edaFileInput.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        const originalText = edaButton.textContent;
        edaButton.disabled = true;
        edaButton.textContent = 'Generating EDA...';

        try {
            const formData = new FormData();
            formData.append('file', file);

            const res = await fetch('/api/eda/report', {
                method: 'POST',
                body: formData
            });

            if (!res.ok) {
                let msg = 'EDA report generation failed';
                try {
                    const err = await res.json();
                    msg = err.error || msg;
                } catch (_) {}
                showAlert('eda-alert', `❌ ${msg}`, 'error');
                return;
            }

            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);

            // Open report in a new tab
            window.open(url, '_blank');

            showAlert('eda-alert', '✅ EDA report generated. Opened in a new tab.', 'success');
        } catch (err) {
            showAlert('eda-alert', `❌ Error: ${err.message}`, 'error');
        } finally {
            edaButton.disabled = false;
            edaButton.textContent = originalText;
        }
    });
}

// ============================================
// INITIALIZATION
// ============================================
console.log('🚀 Synthetic Data Generator initialized');
