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
        currency: 'PHP',
        currencyDisplay: 'symbol'
    }).format(amount).replace(/PHP/, '₱');
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

// Get auth token from localStorage or sessionStorage
function getAuthToken() {
    return localStorage.getItem('authToken') || sessionStorage.getItem('authToken');
}

// Set up authentication headers
function getAuthHeaders() {
    const token = getAuthToken();
    const headers = {
        'Content-Type': 'application/json'
    };
    
    // Add auth token if available
    if (token) {
        headers['Authorization'] = `Token ${token}`;
    }
    
    // Try to get CSRF token from the page, or from sessionStorage as fallback
    const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
    if (csrfInput) {
        headers['X-CSRFToken'] = csrfInput.value;
        // Store in sessionStorage for other pages
        sessionStorage.setItem('csrfToken', csrfInput.value);
    } else if (sessionStorage.getItem('csrfToken')) {
        headers['X-CSRFToken'] = sessionStorage.getItem('csrfToken');
    }
    
    return headers;
}

// Handle API errors
function handleApiError(response) {
    if (!response.ok) {
        // Check if response is HTML (likely a login page)
        if (response.headers.get('content-type')?.includes('text/html')) {
            console.error('Authentication error - received HTML response');
            throw new Error('Authentication error. Please refresh the page and try again.');
        }
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
                headers: getAuthHeaders(),
                credentials: 'include'
            })
            .then(response => {
                if (response.ok) {
                    // Clear all tokens
                    localStorage.removeItem('authToken');
                    sessionStorage.removeItem('authToken');
                    sessionStorage.removeItem('csrfToken');
                    window.location.href = '/login/';
                } else {
                    throw new Error('Logout failed');
                }
            })
            .catch(error => {
                console.error('Logout error:', error);
                // Clear all tokens on error too
                localStorage.removeItem('authToken');
                sessionStorage.removeItem('authToken');
                sessionStorage.removeItem('csrfToken');
                window.location.href = '/login/';
            });
        });
    });
});