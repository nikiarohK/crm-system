document.addEventListener('DOMContentLoaded', async () => {
    checkAuth();
    
    const customersTable = document.querySelector('#customersTable tbody');
    const addCustomerBtn = document.getElementById('addCustomerBtn');
    const customerModal = document.getElementById('customerModal');
    const customerForm = document.getElementById('customerForm');
    const modalTitle = document.getElementById('modalTitle');
    const closeModal = document.querySelector('.close');
    
    async function loadCustomers() {
        try {
            const customers = await getCustomers();
            renderCustomers(customers);
        } catch (error) {
            alert(error.message);
        }
    }
    
    function renderCustomers(customers) {
        customersTable.innerHTML = '';
        
        customers.forEach(customer => {
            const row = document.createElement('tr');
            
            row.innerHTML = `
                <td>${customer.id}</td>
                <td>${customer.name}</td>
                <td>${customer.email}</td>
                <td>${new Date(customer.created_at).toLocaleString()}</td>
                <td>
                    <button class="edit-btn" data-id="${customer.id}">Edit</button>
                    <button class="delete-btn danger" data-id="${customer.id}">Delete</button>
                </td>
            `;
            
            customersTable.appendChild(row);
        });
        
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', () => openEditModal(btn.dataset.id));
        });
        
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', () => deleteCustomerHandler(btn.dataset.id));
        });
    }
    
    function openAddModal() {
        modalTitle.textContent = 'Add Customer';
        customerForm.reset();
        document.getElementById('customerId').value = '';
        customerModal.style.display = 'block';
    }
    
    async function openEditModal(customerId) {
        try {
            const customer = await makeRequest(`/customers/${customerId}`);
            
            modalTitle.textContent = 'Edit Customer';
            document.getElementById('customerId').value = customer.id;
            document.getElementById('customerName').value = customer.name;
            document.getElementById('customerEmail').value = customer.email;
            
            customerModal.style.display = 'block';
        } catch (error) {
            alert(error.message);
        }
    }
    
    customerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const customerId = document.getElementById('customerId').value;
        const name = document.getElementById('customerName').value;
        const email = document.getElementById('customerEmail').value;
        
        try {
            const customerData = { name, email };
            
            if (customerId) {
                await saveCustomer(customerData, customerId);
            } else {
                await saveCustomer(customerData);
            }
            
            customerModal.style.display = 'none';
            loadCustomers();
        } catch (error) {
            alert(error.message);
        }
    });
    
    async function deleteCustomerHandler(customerId) {
        if (!confirm('Are you sure you want to delete this customer?')) return;
        
        try {
            await deleteCustomer(customerId);
            loadCustomers();
        } catch (error) {
            alert(error.message);
        }
    }
    
    closeModal.addEventListener('click', () => {
        customerModal.style.display = 'none';
    });
    
    window.addEventListener('click', (e) => {
        if (e.target === customerModal) {
            customerModal.style.display = 'none';
        }
    });
    
    addCustomerBtn.addEventListener('click', openAddModal);
    loadCustomers();
});