const API_BASE = '/api';

// State
let items = [];
let workshops = [];
let categories = [];
let orders = [];
let logs = [];
let currentFilter = 'all';
let searchTerm = '';
let editingWorkshopId = null;

// Element References
const inventoryList = document.getElementById('inventory-list');
const workshopStats = document.getElementById('workshop-stats');
const modal = document.getElementById('add-item-modal');
const modalContent = document.getElementById('modal-content');
const categorySelect = document.getElementById('category-select');
const workshopSelect = document.getElementById('workshop-select');

// Order Elements
const ordersList = document.getElementById('orders-list');
const orderModal = document.getElementById('add-order-modal');
const orderModalContent = document.getElementById('order-modal-content');
const orderItemSelect = document.getElementById('order-item-select');
const inventoryView = document.getElementById('inventory-view');
const ordersView = document.getElementById('orders-view');
const btnOrders = document.getElementById('btn-orders');

const categoryModal = document.getElementById('category-modal');
const categoryModalContent = document.getElementById('category-modal-content');
const categoryList = document.getElementById('category-list');

const workshopModal = document.getElementById('workshop-modal');
const workshopModalContent = document.getElementById('workshop-modal-content');
const workshopList = document.getElementById('workshop-list');

const filterContainer = document.getElementById('filter-container'); // Might be null now, but we use sidebar-categories

// Init
async function init() {
    try {
        await Promise.all([fetchItems(), fetchWorkshops(), fetchCategories(), fetchLogs()]);
    } catch (e) { console.error('Failed to init', e); }

    render();
    setupSearch();
    renderFilters();
}

// Fetching
async function fetchItems() {
    const res = await fetch(`${API_BASE}/items/`);
    items = await res.json();
}

async function fetchLogs() {
    const res = await fetch(`${API_BASE}/logs/`);
    logs = await res.json();
}

async function fetchWorkshops() {
    const res = await fetch(`${API_BASE}/workshops/`);
    workshops = await res.json();
}

async function fetchCategories() {
    const res = await fetch(`${API_BASE}/categories/`);
    categories = await res.json();
}

// Rendering
function render() {
    renderStats();
    renderInventory();
    renderDropdowns();
}

function renderStats() {
    if (!workshopStats) return;
    workshopStats.innerHTML = workshops.map(ws => {
        const wsItems = items.filter(i => i.workshop_id === ws.id);
        const totalItems = wsItems.reduce((acc, curr) => acc + curr.quantity, 0);
        const lowStock = wsItems.filter(i => i.quantity < i.min_quantity).length;

        // Incident Logic
        // Get all item IDs in this workshop
        const wsItemIds = new Set(wsItems.map(i => i.id));

        // Count logs for these items where reason contains Lost/Damaged
        const incidents = logs.filter(l =>
            wsItemIds.has(l.item_id) &&
            l.reason &&
            (l.reason.toLowerCase().includes('lost') || l.reason.toLowerCase().includes('damaged'))
        ).length;

        const isEditing = editingWorkshopId === ws.id;

        return `
        <div class="bg-slate-800 p-6 rounded-xl shadow-md border border-slate-700 hover:border-slate-600 transition-colors relative group">
            ${isEditing ? `
                <div class="mb-4">
                    <input type="text" id="edit-name-${ws.id}" value="${ws.name}" class="bg-slate-900 text-white rounded p-1 w-full mb-2 border border-slate-600">
                    <input type="text" id="edit-location-${ws.id}" value="${ws.location || ''}" class="bg-slate-900 text-slate-400 text-sm rounded p-1 w-full border border-slate-600">
                    <div class="flex gap-2 mt-2 justify-end">
                        <button onclick="saveWorkshop(${ws.id})" class="text-xs bg-emerald-600 text-white px-2 py-1 rounded hover:bg-emerald-500">Save</button>
                        <button onclick="cancelEdit()" class="text-xs bg-slate-600 text-white px-2 py-1 rounded hover:bg-slate-500">Cancel</button>
                    </div>
                </div>
            ` : `
                <div class="absolute top-4 right-4 hidden group-hover:block transition-all">
                     <button onclick="enableEditMode(${ws.id})" class="text-slate-400 hover:text-blue-400 transition-colors p-1 rounded hover:bg-slate-700">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                        </svg>
                    </button>
                </div>
                <div class="flex justify-between items-start mb-4">
                    <div>
                        <h3 class="text-xl font-bold text-white">${ws.name}</h3>
                        <p class="text-slate-400 text-sm">${ws.location || 'Unknown Location'}</p>
                    </div>
                    <div class="bg-slate-900 p-2 rounded-lg">
                        <span class="text-2xl font-bold text-blue-400">${totalItems}</span>
                    </div>
                </div>
            `}
            <div class="flex items-center gap-4 text-sm mt-3">
                <span class="${lowStock > 0 ? 'text-red-400' : 'text-emerald-400'} font-medium flex items-center gap-1">
                    ${lowStock > 0 ? '⚠️ ' + lowStock + ' Low Stock' : '✅ All Good'}
                </span>
                ${incidents > 0 ? `
                <span class="text-amber-500 font-medium flex items-center gap-1">
                     <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                    ${incidents} Incidents
                </span>` : ''}
            </div>
        </div>
        `;
    }).join('');
}

function renderInventory() {
    let filtered = items;

    // Filter by Category
    if (currentFilter !== 'all') {
        filtered = filtered.filter(i => i.category.name === currentFilter);
    }

    // Filter by Search
    if (searchTerm) {
        const term = searchTerm.toLowerCase();
        filtered = filtered.filter(i => i.name.toLowerCase().includes(term));
    }

    if (!inventoryList) return;
    inventoryList.innerHTML = filtered.map(item => `
        <tr class="hover:bg-slate-700/30 transition-colors group">
            <td class="p-4">
                <div class="font-medium text-white">${item.name}</div>
                ${item.quantity < item.min_quantity ? '<span class="text-xs text-red-400">Low Stock</span>' : ''}
            </td>
            <td class="p-4 text-slate-300">${item.category.name}</td>
            <td class="p-4 text-slate-300">${item.workshop.name}</td>
            <td class="p-4 text-center">
                <div class="inline-flex items-center bg-slate-900 rounded-lg p-1">
                    <button onclick="updateQuantity(${item.id}, -1)" class="w-6 h-6 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700 rounded">-</button>
                    <span class="mx-3 font-mono font-medium ${item.quantity < item.min_quantity ? 'text-red-400' : 'text-white'}">${item.quantity}</span>
                    <button onclick="updateQuantity(${item.id}, 1)" class="w-6 h-6 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700 rounded">+</button>
                </div>
            </td>
            <td class="p-4 text-right flex justify-end gap-2">
                <button onclick="openReportModal(${item.id}, 'lost')" title="Report Lost" class="text-amber-500 hover:text-amber-400 transition-colors p-2 rounded hover:bg-slate-700">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                </button>
                <button onclick="openReportModal(${item.id}, 'damaged')" title="Report Damaged" class="text-red-500 hover:text-red-400 transition-colors p-2 rounded hover:bg-slate-700">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                       <path fill-rule="evenodd" d="M12.395 2.553a1 1 0 00-1.45-.385c-.345.23-.614.558-.822.88-.214.33-.403.713-.57 1.116-.334.804-.614 1.768-.84 2.734a31.365 31.365 0 00-.613 3.58 2.64 2.64 0 01-.945-1.067c-.328-.68-.398-1.534-.398-2.654A1 1 0 005.05 6.05 6.981 6.981 0 003 11a7 7 0 1011.95-4.95c-.592-.591-.98-.985-1.348-1.467-.363-.476-.724-1.063-1.207-2.03zM12.12 15.12a3 3 0 10-4.24-4.24 3 3 0 004.24 4.24z" clip-rule="evenodd" />
                    </svg>
                </button>
                <button onclick="deleteItem(${item.id})" title="Delete" class="text-slate-500 hover:text-red-400 transition-colors p-2 rounded hover:bg-slate-700">
                     <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                    </svg>
                </button>
            </td>
        </tr>
    `).join('');
}

function renderDropdowns() {
    if (categorySelect) categorySelect.innerHTML = categories.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    if (workshopSelect) workshopSelect.innerHTML = workshops.map(w => `<option value="${w.id}">${w.name}</option>`).join('');
    if (orderItemSelect) orderItemSelect.innerHTML = items.map(i => `<option value="${i.id}">${i.name} (Qty: ${i.quantity})</option>`).join('');
}

// Logic
async function updateQuantity(id, change) {
    const reason = change > 0 ? 'Manual Increase' : 'Manual Decrease';
    await fetch(`${API_BASE}/items/${id}/quantity?change=${change}&reason=${encodeURIComponent(reason)}`, { method: 'PUT' });
    await fetchItems();
    await fetchLogs();
    render();
}

async function deleteItem(id) {
    if (!confirm('Are you sure you want to delete this item?')) return;
    await fetch(`${API_BASE}/items/${id}`, { method: 'DELETE' });
    await Promise.all([fetchItems(), fetchLogs()]);
    render();
}

// Report Incident Logic
const reportModal = document.getElementById('report-modal');
const reportModalContent = document.getElementById('report-modal-content');

function openReportModal(id, type) {
    document.getElementById('report-item-id').value = id;
    document.getElementById('report-quantity').value = 1;
    document.getElementById('report-notes').value = '';

    // Select Radio
    const radios = document.getElementsByName('type');
    for (const r of radios) {
        if (r.value === type) r.checked = true;
    }

    reportModal.classList.remove('opacity-0', 'pointer-events-none');
    reportModalContent.classList.remove('scale-95');
    reportModalContent.classList.add('scale-100');
}

function closeReportModal() {
    reportModal.classList.add('opacity-0', 'pointer-events-none');
    reportModalContent.classList.add('scale-95');
    reportModalContent.classList.remove('scale-100');
}

async function submitReport(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const itemId = formData.get('item_id');
    const type = formData.get('type');
    const qty = parseInt(formData.get('quantity'));
    const notes = formData.get('notes');

    const typeLabel = type.charAt(0).toUpperCase() + type.slice(1);
    const reason = `${typeLabel} - ${notes}`;

    try {
        await fetch(`${API_BASE}/items/${itemId}/quantity?change=-${qty}&reason=${encodeURIComponent(reason)}`, { method: 'PUT' });
        await Promise.all([fetchItems(), fetchLogs()]);
        render();
        closeReportModal();
        showToast(`${typeLabel} report submitted`);
    } catch (err) {
        alert('Failed to submit report');
    }
}

// Orders Logic
async function fetchOrders() {
    const res = await fetch(`${API_BASE}/orders/`);
    orders = await res.json();
    renderOrders();
}

function renderOrders() {
    if (!ordersList) return;
    ordersList.innerHTML = orders.map(o => `
        <tr class="hover:bg-slate-700/30 transition-colors">
            <td class="p-4 font-mono text-sm text-slate-400">#${o.id}</td>
            <td class="p-4 text-white">${o.item ? o.item.name : 'Unknown Item'}</td>
            <td class="p-4 text-emerald-400 font-bold">${o.quantity}</td>
            <td class="p-4">
                <span class="px-2 py-1 rounded text-xs font-bold ${o.status === 'Pending' ? 'bg-amber-500/20 text-amber-500' : 'bg-emerald-500/20 text-emerald-500'}">
                    ${o.status}
                </span>
            </td>
            <td class="p-4 text-right">
                ${o.status === 'Pending' ? `
                <button onclick="completeOrder(${o.id})" class="text-emerald-500 hover:text-emerald-400 text-sm font-medium hover:underline">
                    Mark Received
                </button>` : '<span class="text-slate-500 text-sm">Completed</span>'}
            </td>
        </tr>
    `).join('');
}

async function handlePlaceOrder(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    data.item_id = parseInt(data.item_id);
    data.quantity = parseInt(data.quantity);

    const res = await fetch(`${API_BASE}/orders/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (res.ok) {
        closeOrderModal();
        e.target.reset();
        await fetchOrders();
        showToast('Order placed successfully!');
    } else {
        alert('Failed to place order');
    }
}

async function completeOrder(id) {
    if (!confirm('Confirm receipt of this order? Stock will be updated.')) return;
    const res = await fetch(`${API_BASE}/orders/${id}/complete`, { method: 'PUT' });
    if (res.ok) {
        await fetchOrders();
        await fetchItems(); // Refresh stock
        render();
        showToast('Order received and stock updated!');
    }
}

async function handleAddItem(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());

    // Fix types
    data.category_id = parseInt(data.category_id);
    data.workshop_id = parseInt(data.workshop_id);
    data.quantity = parseInt(data.quantity);
    data.min_quantity = parseInt(data.min_quantity);

    const res = await fetch(`${API_BASE}/items/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    if (res.ok) {
        closeAddItemModal();
        e.target.reset();
        await fetchItems();
        render();
        showToast('Item added successfully!');
    } else {
        alert('Failed to add item');
    }
}

// Category Management
function openCategoryModal() {
    categoryModal.classList.remove('opacity-0', 'pointer-events-none');
    categoryModalContent.classList.remove('scale-95');
    categoryModalContent.classList.add('scale-100');
    renderCategoryList();
}

function closeCategoryModal() {
    categoryModal.classList.add('opacity-0', 'pointer-events-none');
    categoryModalContent.classList.add('scale-95');
    categoryModalContent.classList.remove('scale-100');
}

function renderCategoryList() {
    categoryList.innerHTML = categories.map(c => `
        <div class="flex justify-between items-center bg-slate-900 p-3 rounded-lg border border-slate-700">
            <span class="text-white">${c.name}</span>
            <button onclick="deleteCategory(${c.id})" class="text-slate-500 hover:text-red-400 p-1">
                 <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
            </button>
        </div>
    `).join('');
}

async function createNewCategory() {
    const input = document.getElementById('new-category-name');
    const name = input.value.trim();
    if (!name) return;

    const res = await fetch(`${API_BASE}/categories/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name })
    });

    if (res.ok) {
        await fetchCategories();
        renderCategoryList();
        renderDropdowns();
        renderFilters();
        input.value = '';
        showToast('Category added!');
    } else {
        alert('Failed to add category');
    }
}

async function deleteCategory(id) {
    if (!confirm('Delete this category? Only empty categories can be deleted.')) return;

    const res = await fetch(`${API_BASE}/categories/${id}`, { method: 'DELETE' });
    if (res.ok) {
        await fetchCategories();
        renderCategoryList();
        renderDropdowns();
        renderFilters();
        showToast('Category deleted!');
    } else {
        const data = await res.json();
        alert(data.detail || 'Failed to delete category');
    }
}

// UI Helpers (Sidebar Logic)
function renderFilters() {
    const sidebarCategories = document.getElementById('sidebar-categories');

    // Sidebar items
    if (sidebarCategories) {
        sidebarCategories.innerHTML = categories.map(c => `
            <button onclick="filterItems('${c.name}')"
                class="w-full text-left px-3 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-3 ${currentFilter === c.name ? 'bg-blue-600/10 text-blue-400' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-100'}">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
                ${c.name}
            </button>
        `).join('');
    }

    // Dashboard Active State
    const navDashboard = document.getElementById('nav-dashboard');
    if (navDashboard) {
        if (currentFilter === 'all' && ordersView.classList.contains('hidden')) {
            navDashboard.classList.add('bg-blue-600/10', 'text-blue-400');
            navDashboard.classList.remove('text-slate-400', 'hover:bg-slate-800', 'hover:text-slate-100');
        } else {
            navDashboard.classList.remove('bg-blue-600/10', 'text-blue-400');
            navDashboard.classList.add('text-slate-400', 'hover:bg-slate-800', 'hover:text-slate-100');
        }
    }

    // Orders Active State
    const navOrders = document.getElementById('nav-orders');
    if (navOrders) {
        if (!ordersView.classList.contains('hidden')) {
            navOrders.classList.add('bg-blue-600/10', 'text-emerald-400');
            navOrders.classList.remove('text-slate-400', 'hover:bg-slate-800', 'hover:text-slate-100');
        } else {
            navOrders.classList.remove('bg-blue-600/10', 'text-emerald-400');
            navOrders.classList.add('text-slate-400', 'hover:bg-slate-800', 'hover:text-slate-100');
        }
    }
}

function setupSearch() {
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchTerm = e.target.value;
            renderInventory();
        });
    }
}

function showOrders() {
    inventoryView.classList.add('hidden');
    ordersView.classList.remove('hidden');

    currentFilter = 'orders'; // Hack to help renderFilters clear other active states
    renderFilters();
    fetchOrders();
}

function filterItems(category) {
    inventoryView.classList.remove('hidden');
    ordersView.classList.add('hidden');

    currentFilter = category;
    renderFilters();
    renderInventory();
}

// Workshop Management
function openWorkshopModal() {
    workshopModal.classList.remove('opacity-0', 'pointer-events-none');
    workshopModalContent.classList.remove('scale-95');
    workshopModalContent.classList.add('scale-100');
    renderWorkshopList();
}

function closeWorkshopModal() {
    workshopModal.classList.add('opacity-0', 'pointer-events-none');
    workshopModalContent.classList.add('scale-95');
    workshopModalContent.classList.remove('scale-100');
}

function renderWorkshopList() {
    workshopList.innerHTML = workshops.map(w => `
        <div class="flex justify-between items-center bg-slate-900 p-3 rounded-lg border border-slate-700">
            <div>
                <div class="text-white">${w.name}</div>
                <div class="text-slate-500 text-xs">${w.location || ''}</div>
            </div>
            <button onclick="deleteWorkshop(${w.id})" class="text-slate-500 hover:text-red-400 p-1">
                 <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fill-rule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clip-rule="evenodd" />
                </svg>
            </button>
        </div>
    `).join('');
}

async function createNewWorkshop() {
    const nameInput = document.getElementById('new-workshop-name');
    const locInput = document.getElementById('new-workshop-location');
    const name = nameInput.value.trim();
    const location = locInput.value.trim();

    if (!name) return;

    const res = await fetch(`${API_BASE}/workshops/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, location })
    });

    if (res.ok) {
        await fetchWorkshops();
        renderWorkshopList();
        renderDropdowns();
        renderStats(); // Refresh stats cards

        nameInput.value = '';
        locInput.value = '';
        showToast('Workshop added!');
    } else {
        alert('Failed to add workshop');
    }
}

async function deleteWorkshop(id) {
    if (!confirm('Delete this workshop? Only empty workshops can be deleted.')) return;

    const res = await fetch(`${API_BASE}/workshops/${id}`, { method: 'DELETE' });
    if (res.ok) {
        await fetchWorkshops();
        renderWorkshopList();
        renderDropdowns();
        renderStats();
        showToast('Workshop deleted!');

        // If we were editing this workshop, cancel edit
        if (editingWorkshopId === id) {
            editingWorkshopId = null;
            renderStats();
        }
    } else {
        const data = await res.json();
        alert(data.detail || 'Failed to delete workshop');
    }
}

// Workshop Edit Logic
function enableEditMode(id) {
    editingWorkshopId = id;
    renderStats();
}

function cancelEdit() {
    editingWorkshopId = null;
    renderStats();
}

async function saveWorkshop(id) {
    const nameInput = document.getElementById(`edit-name-${id}`);
    const locInput = document.getElementById(`edit-location-${id}`);
    const name = nameInput.value.trim();
    const location = locInput.value.trim();

    if (!name) return;

    try {
        const res = await fetch(`${API_BASE}/workshops/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, location })
        });

        if (res.ok) {
            await fetchWorkshops();
            editingWorkshopId = null;
            renderStats();
            renderDropdowns(); // Update dropdowns too in case name changed
            showToast('Workshop updated!');
        } else {
            alert('Failed to update workshop');
        }
    } catch (e) {
        console.error(e);
        alert('Error updating workshop');
    }
}

// Toast notification
function showToast(message) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = message;
    toast.classList.remove('translate-y-20', 'opacity-0');
    toast.classList.add('translate-y-0', 'opacity-100');
    setTimeout(() => {
        toast.classList.add('translate-y-20', 'opacity-0');
        toast.classList.remove('translate-y-0', 'opacity-100');
    }, 3000);
}

// Modal helpers
function openAddItemModal() {
    modal.classList.remove('opacity-0', 'pointer-events-none');
    modalContent.classList.remove('scale-95');
    modalContent.classList.add('scale-100');
}

function closeAddItemModal() {
    modal.classList.add('opacity-0', 'pointer-events-none');
    modalContent.classList.add('scale-95');
    modalContent.classList.remove('scale-100');
}

function openOrderModal() {
    orderModal.classList.remove('opacity-0', 'pointer-events-none');
    orderModalContent.classList.remove('scale-95');
    orderModalContent.classList.add('scale-100');
    renderDropdowns();
}

function closeOrderModal() {
    orderModal.classList.add('opacity-0', 'pointer-events-none');
    orderModalContent.classList.add('scale-95');
    orderModalContent.classList.remove('scale-100');
}

// Start
init();
