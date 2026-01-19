/**
 * Multi-Agent GitHub README Updater - Frontend JavaScript
 */

// =============================================================================
// LOADING OVERLAY
// =============================================================================

function showLoading(message = 'Loading...') {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.className = 'loading-overlay';
    overlay.innerHTML = `
        <div class="text-center">
            <div class="loading-spinner mx-auto mb-3"></div>
            <p class="text-muted">${message}</p>
        </div>
    `;
    document.body.appendChild(overlay);
}

function hideLoading() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}

// =============================================================================
// REPOSITORY SELECTION & GENERATION
// =============================================================================

async function generateReadmes() {
    const checkboxes = document.querySelectorAll('.repo-checkbox:checked');
    
    if (checkboxes.length === 0) {
        alert('Please select at least one repository');
        return;
    }
    
    const selectedRepos = Array.from(checkboxes).map(cb => cb.value);
    
    showLoading(`Generating README for ${selectedRepos.length} repository(s)... This may take a moment.`);
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ repos: selectedRepos })
        });
        
        const data = await response.json();
        
        if (data.success && data.redirect) {
            window.location.href = data.redirect;
        } else if (data.error) {
            hideLoading();
            alert('Error: ' + data.error);
        }
    } catch (error) {
        hideLoading();
        console.error('Error:', error);
        alert('Failed to generate README. Please try again.');
    }
}

// =============================================================================
// COMMIT FUNCTIONALITY
// =============================================================================

async function commitReadme(repoName, readmeContent, createPr = false, commitMessage = null) {
    showLoading('Committing to GitHub...');
    
    try {
        const response = await fetch('/commit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                repo_name: repoName,
                readme_content: readmeContent,
                create_pr: createPr,
                commit_message: commitMessage
            })
        });
        
        const data = await response.json();
        hideLoading();
        
        return data;
    } catch (error) {
        hideLoading();
        console.error('Error:', error);
        throw error;
    }
}

// =============================================================================
// UTILITY FUNCTIONS
// =============================================================================

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showToast('Failed to copy', 'error');
    });
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type === 'error' ? 'danger' : type} position-fixed`;
    toast.style.cssText = 'bottom: 20px; right: 20px; z-index: 9999; min-width: 200px;';
    toast.innerHTML = `
        <i class="bi bi-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-triangle' : 'info-circle'} me-2"></i>
        ${message}
    `;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('fade');
        setTimeout(() => toast.remove(), 150);
    }, 3000);
}

// =============================================================================
// FORM HANDLING
// =============================================================================

document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    document.querySelectorAll('.alert-dismissible').forEach(alert => {
        setTimeout(() => {
            const closeBtn = alert.querySelector('.btn-close');
            if (closeBtn) closeBtn.click();
        }, 5000);
    });
    
    // Handle form submissions with loading states
    document.querySelectorAll('form[data-loading]').forEach(form => {
        form.addEventListener('submit', function() {
            const message = this.dataset.loading || 'Processing...';
            showLoading(message);
        });
    });
    
    // Initialize tooltips
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(el => new bootstrap.Tooltip(el));
});

// =============================================================================
// KEYBOARD SHORTCUTS
// =============================================================================

document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + Enter to submit forms
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        const form = document.querySelector('form:not([data-no-shortcut])');
        if (form) {
            form.requestSubmit();
        }
    }
    
    // Escape to close modals
    if (e.key === 'Escape') {
        const modal = document.querySelector('.modal.show');
        if (modal) {
            bootstrap.Modal.getInstance(modal)?.hide();
        }
    }
});

// =============================================================================
// EXPORTS (for use in templates)
// =============================================================================

window.App = {
    showLoading,
    hideLoading,
    generateReadmes,
    commitReadme,
    copyToClipboard,
    showToast
};
