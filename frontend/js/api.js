const API_BASE_URL = 'http://localhost:8000';  

async function makeRequest(url, method = 'GET', body = null, requiresAuth = true) {
    const headers = {
        'Content-Type': 'application/json',
    };
    
    if (requiresAuth) {
        const token = localStorage.getItem('token');
        if (!token) {
            window.location.href = 'login.html';
            return;
        }
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const config = {
        method,
        headers,
    };
    
    if (body) {
        config.body = JSON.stringify(body);
    }
    
    try {
        const response = await fetch(`${API_BASE_URL}${url}`, config);
        
        if (response.status === 401) {
            localStorage.removeItem('token');
            window.location.href = 'login.html';
            return;
        }
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.detail || 'Request failed');
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token && !window.location.pathname.endsWith('login.html')) {
        window.location.href = 'login.html';
    }
}

async function getCustomers() {
    return makeRequest('/customers');
}

async function saveCustomer(customerData, customerId = null) {
    const url = customerId ? `/customers/${customerId}` : '/customers';
    const method = customerId ? 'PUT' : 'POST';
    return makeRequest(url, method, customerData);
}

async function deleteCustomer(customerId) {
    return makeRequest(`/customers/${customerId}`, 'DELETE');
}

async function getOrders(customerId = null) {
    const url = customerId ? `/orders/${customerId}` : '/orders';
    return makeRequest(url);
}

async function saveOrder(orderData, orderId = null) {
    const url = orderId ? `/orders/${orderId}` : '/orders';
    const method = orderId ? 'PUT' : 'POST';
    return makeRequest(url, method, orderData);
}

async function deleteOrder(orderId) {
    return makeRequest(`/orders/${orderId}`, 'DELETE');
}

async function login(username, password) {
    return makeRequest('/login', 'POST', { username, password }, false);
}

async function register(username, password) {
    return makeRequest('/register', 'POST', { username, password }, false);
}