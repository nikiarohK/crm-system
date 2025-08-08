document.addEventListener('DOMContentLoaded', async () => {
    checkAuth();
    
    const ordersTable = document.querySelector('#ordersTable tbody');
    const addOrderBtn = document.getElementById('addOrderBtn');
    const orderModal = document.getElementById('orderModal');
    const orderForm = document.getElementById('orderForm');
    const modalTitle = document.getElementById('orderModalTitle');
    const closeModal = document.querySelector('#orderModal .close');
    const customerFilter = document.getElementById('customerFilter');
    const orderCustomerId = document.getElementById('orderCustomerId');
    
    let customers = [];
    let orders = [];
    
    async function loadData() {
        try {
            customers = await getCustomers();
            loadOrders();
            populateCustomerFilters();
        } catch (error) {
            alert(error.message);
        }
    }
    
    async function loadOrders(customerId = null) {
        try {
            if (customerId) {
                orders = await makeRequest(`/orders/${customerId}`);
            } else {
                orders = await makeRequest(`/orders?page=1&limit=10`);
            }
            renderOrders();
        } catch (error) {
            alert(error.message);
        }
    }
    
    function renderOrders() {
        ordersTable.innerHTML = '';
        
        orders.forEach(order => {
            const customer = customers.find(c => c.id === order.customer_id) || {};
            
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${order.id}</td>
                <td>${customer.name || 'Unknown'}</td>
                <td>${order.product_name}</td>
                <td>$${order.price.toFixed(2)}</td>
                <td>${new Date(order.created_at).toLocaleString()}</td>
                <td>
                    <button class="delete-btn danger" data-id="${order.id}">Delete</button>
                </td>
            `;
            
            ordersTable.appendChild(row);
        });
        
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', () => deleteOrderHandler(btn.dataset.id));
        });
    }
    
    function populateCustomerFilters() {
        customerFilter.innerHTML = '<option value="">All Customers</option>';
        orderCustomerId.innerHTML = '';
        
        customers.forEach(customer => {
            const option1 = document.createElement('option');
            option1.value = customer.id;
            option1.textContent = customer.name;
            customerFilter.appendChild(option1);
            
            const option2 = document.createElement('option');
            option2.value = customer.id;
            option2.textContent = customer.name;
            orderCustomerId.appendChild(option2);
        });
    }
    
    function openAddModal() {
        modalTitle.textContent = 'Add Order';
        orderForm.reset();
        document.getElementById('orderId').value = '';
        orderModal.style.display = 'block';
    }
    
    orderForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const orderData = {
            customer_id: document.getElementById('orderCustomerId').value,
            product_name: document.getElementById('productName').value,
            price: parseFloat(document.getElementById('price').value)
        };
        
        try {
            await saveOrder(orderData);
            orderModal.style.display = 'none';
            loadOrders(customerFilter.value || null);
        } catch (error) {
            alert(error.message);
        }
    });
    
    async function deleteOrderHandler(orderId) {
        if (!confirm('Вы уверены, что хотите удалить этот заказ?')) return;
        
        try {
            const response = await makeRequest(
                `/orders/${orderId}`,
                'DELETE'
            );
            
            if (response.success) {
                loadOrders(customerFilter.value || null);
            } else {
                alert('Не удалось удалить заказ');
            }
        } catch (error) {
            alert('Ошибка при удалении заказа: ' + error.message);
        }
    }
    
    async function getOrders(customerId = null, page = 1, limit = 10) {
        if (customerId) {
            return makeRequest(`/orders/${customerId}`);
        } else {
            return makeRequest(`/orders?page=${page}&limit=${limit}`);
        }
    }
    customerFilter.addEventListener('change', () => {
        loadOrders(customerFilter.value || null);
    });
    
    closeModal.addEventListener('click', () => {
        orderModal.style.display = 'none';
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === orderModal) {
            orderModal.style.display = 'none';
        }
    });
    
    addOrderBtn.addEventListener('click', openAddModal);
    loadData();
    
});

