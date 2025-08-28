// Common JavaScript functions for El Senior Dumingag

// Show a toast notification
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type} show`;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    
    // Remove toast after 3 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'PHP'
    }).format(amount);
}

// Format date
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

// Toggle loading state on element
function toggleLoading(element, isLoading) {
    if (isLoading) {
        element.classList.add('loading');
        element.disabled = true;
    } else {
        element.classList.remove('loading');
        element.disabled = false;
    }
}

// Get auth token from localStorage
function getAuthToken() {
    return localStorage.getItem('authToken');
}

// Set up authentication headers
function getAuthHeaders() {
    const token = getAuthToken();
    if (token) {
        return {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json'
        };
    }
    return {
        'Content-Type': 'application/json'
    };
}

// Handle API errors
function handleApiError(response) {
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response;
}

// Initialize common functionality
document.addEventListener('DOMContentLoaded', function() {
    // Add CSRF token to forms if needed
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfToken) {
        document.querySelectorAll('form').forEach(form => {
            if (!form.querySelector('[name=csrfmiddlewaretoken]')) {
                const csrfInput = csrfToken.cloneNode(true);
                form.appendChild(csrfInput);
            }
        });
    }
    
    // Set up logout functionality
    const logoutLinks = document.querySelectorAll('[data-logout]');
    logoutLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            fetch('/api/logout/', {
                method: 'POST',
                headers: getAuthHeaders()
            })
            .then(response => {
                if (response.ok) {
                    localStorage.removeItem('authToken');
                    window.location.href = '/login/';
                } else {
                    throw new Error('Logout failed');
                }
            })
            .catch(error => {
                console.error('Logout error:', error);
                localStorage.removeItem('authToken');
                window.location.href = '/login/';
            });
        });
    });
});