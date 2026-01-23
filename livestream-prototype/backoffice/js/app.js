// Configuration
const API_URL = 'http://localhost:5000/api';
const SOCKET_URL = 'http://localhost:5000';

// Global State
let socket = null;
let talents = [];
let livestreams = [];
let currentTalent = null;

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    initializeSocket();
    loadInitialData();
    setupEventListeners();
});

// Socket.IO Connection
function initializeSocket() {
    socket = io(SOCKET_URL);

    socket.on('connect', () => {
        console.log('Connected to server');
        showToast('Connected to server', 'success');
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        showToast('Disconnected from server', 'error');
    });

    // Real-time updates
    socket.on('talent_updated', (talent) => {
        updateTalentInList(talent);
        showToast(`Talent ${talent.name} updated`, 'info');
    });

    socket.on('talent_status_changed', (data) => {
        const talent = talents.find(t => t.id === data.talent_id);
        if (talent) {
            talent.status = data.status;
            updateTalentInList(talent);
        }
    });

    socket.on('livestream_started', (livestream) => {
        livestreams.push(livestream);
        renderLivestreams();
        updateStats();
        showToast(`New livestream started: ${livestream.title}`, 'success');
    });

    socket.on('livestream_ended', (data) => {
        livestreams = livestreams.filter(ls => ls.id !== data.livestream_id);
        renderLivestreams();
        updateStats();
        showToast('Livestream ended', 'info');
    });

    socket.on('viewer_joined', (data) => {
        const livestream = livestreams.find(ls => ls.id === data.livestream_id);
        if (livestream) {
            livestream.viewers = data.viewers;
            renderLivestreams();
        }
    });

    socket.on('viewer_left', (data) => {
        const livestream = livestreams.find(ls => ls.id === data.livestream_id);
        if (livestream) {
            livestream.viewers = data.viewers;
            renderLivestreams();
        }
    });

    socket.on('gift_received', (data) => {
        const livestream = livestreams.find(ls => ls.id === data.livestream_id);
        if (livestream) {
            livestream.diamonds = data.total_diamonds;
            renderLivestreams();
        }
        showToast(`Gift received: ${data.amount} diamonds`, 'success');
    });
}

// Load Initial Data
async function loadInitialData() {
    try {
        await Promise.all([
            loadTalents(),
            loadLivestreams(),
            loadStats()
        ]);
    } catch (error) {
        console.error('Error loading initial data:', error);
        showToast('Error loading data', 'error');
    }
}

// API Calls
async function loadTalents() {
    try {
        const response = await fetch(`${API_URL}/talents`);
        const data = await response.json();

        if (data.success) {
            talents = data.data;
            renderTalents();
            renderTopTalents();
        }
    } catch (error) {
        console.error('Error loading talents:', error);
    }
}

async function loadLivestreams() {
    try {
        const response = await fetch(`${API_URL}/livestreams`);
        const data = await response.json();

        if (data.success) {
            livestreams = data.data;
            renderLivestreams();
        }
    } catch (error) {
        console.error('Error loading livestreams:', error);
    }
}

async function loadStats() {
    try {
        const response = await fetch(`${API_URL}/stats`);
        const data = await response.json();

        if (data.success) {
            updateStats(data.data);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

async function updateTalentData(talentId, updates) {
    try {
        const response = await fetch(`${API_URL}/talents/${talentId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(updates)
        });

        const data = await response.json();

        if (data.success) {
            updateTalentInList(data.data);
            showToast('Talent updated successfully', 'success');
            return true;
        }
    } catch (error) {
        console.error('Error updating talent:', error);
        showToast('Error updating talent', 'error');
        return false;
    }
}

async function updateTalentStatus(talentId, status) {
    try {
        const response = await fetch(`${API_URL}/talents/${talentId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`Status updated to ${status}`, 'success');
            return true;
        }
    } catch (error) {
        console.error('Error updating status:', error);
        showToast('Error updating status', 'error');
        return false;
    }
}

// Render Functions
function updateStats(stats) {
    if (!stats) {
        // Calculate from current data
        stats = {
            total_talents: talents.length,
            active_livestreams: livestreams.length,
            total_viewers: livestreams.reduce((sum, ls) => sum + ls.viewers, 0),
            total_diamonds: talents.reduce((sum, t) => sum + t.total_diamonds, 0)
        };
    }

    document.getElementById('total-talents').textContent = stats.total_talents;
    document.getElementById('active-livestreams').textContent = stats.active_livestreams;
    document.getElementById('total-viewers').textContent = stats.total_viewers.toLocaleString();
    document.getElementById('total-diamonds').textContent = stats.total_diamonds.toLocaleString();
}

function renderTalents() {
    const tbody = document.getElementById('talents-tbody');
    tbody.innerHTML = '';

    talents.forEach(talent => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>
                <div class="talent-cell">
                    <img src="${talent.avatar}" alt="${talent.name}">
                    <div class="talent-cell-info">
                        <div class="talent-cell-name">${talent.name}</div>
                        <div class="talent-cell-bio">${talent.bio}</div>
                    </div>
                </div>
            </td>
            <td>@${talent.username}</td>
            <td><span class="status-badge ${talent.status}">${talent.status.toUpperCase()}</span></td>
            <td>${talent.followers.toLocaleString()}</td>
            <td>${talent.total_viewers.toLocaleString()}</td>
            <td>${talent.total_diamonds.toLocaleString()}</td>
            <td>${talent.level}</td>
            <td>
                <button class="btn btn-primary btn-sm" onclick="editTalent('${talent.id}')">
                    <i class="fas fa-edit"></i> Edit
                </button>
                <select class="btn btn-sm" onchange="changeTalentStatus('${talent.id}', this.value)">
                    <option value="">Change Status</option>
                    <option value="online" ${talent.status === 'online' ? 'selected' : ''}>Online</option>
                    <option value="offline" ${talent.status === 'offline' ? 'selected' : ''}>Offline</option>
                    <option value="live" ${talent.status === 'live' ? 'selected' : ''}>Live</option>
                </select>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function renderLivestreams() {
    const container = document.getElementById('livestreams-grid');
    const recentContainer = document.getElementById('recent-livestreams');

    if (!livestreams || livestreams.length === 0) {
        const emptyMessage = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px; color: #95a5a6;">
                <i class="fas fa-broadcast-tower" style="font-size: 60px; margin-bottom: 15px;"></i>
                <p>No active livestreams at the moment</p>
            </div>
        `;
        if (container) container.innerHTML = emptyMessage;
        if (recentContainer) recentContainer.innerHTML = emptyMessage;
        return;
    }

    const livestreamHTML = livestreams.map(ls => `
        <div class="livestream-card">
            <div class="livestream-thumbnail">
                <img src="${ls.thumbnail}" alt="${ls.title}">
                <span class="live-badge">
                    <i class="fas fa-circle"></i> LIVE
                </span>
                <span class="viewer-count">
                    <i class="fas fa-eye"></i> ${ls.viewers}
                </span>
            </div>
            <div class="livestream-info">
                <div class="talent-info">
                    <img src="${ls.talent_avatar}" alt="${ls.talent_name}" class="talent-avatar">
                    <div>
                        <div class="talent-name">${ls.talent_name}</div>
                        <div style="font-size: 12px; color: #7f8c8d;">${ls.title}</div>
                    </div>
                </div>
                <div class="livestream-stats">
                    <span><i class="fas fa-heart"></i> ${ls.likes}</span>
                    <span><i class="fas fa-gem"></i> ${ls.diamonds}</span>
                </div>
            </div>
        </div>
    `).join('');

    if (container) container.innerHTML = livestreamHTML;
    if (recentContainer) recentContainer.innerHTML = livestreamHTML;

    updateStats();
}

function renderTopTalents() {
    const container = document.getElementById('top-talents');
    if (!container) return;

    const topTalents = [...talents]
        .sort((a, b) => b.total_diamonds - a.total_diamonds)
        .slice(0, 5);

    container.innerHTML = topTalents.map((talent, index) => `
        <div class="top-item">
            <div class="top-item-rank">${index + 1}</div>
            <img src="${talent.avatar}" alt="${talent.name}">
            <div class="top-item-info">
                <div class="top-item-name">${talent.name}</div>
                <div class="top-item-stats">
                    ${talent.total_diamonds.toLocaleString()} diamonds •
                    ${talent.followers.toLocaleString()} followers
                </div>
            </div>
        </div>
    `).join('');
}

function updateTalentInList(talent) {
    const index = talents.findIndex(t => t.id === talent.id);
    if (index !== -1) {
        talents[index] = talent;
        renderTalents();
        renderTopTalents();
    }
}

// UI Functions
function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.getAttribute('data-page');
            showPage(page);

            // Update active state
            document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
            item.classList.add('active');
        });
    });

    // Search
    const searchInput = document.getElementById('talent-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            filterTalents(query);
        });
    }
}

function showPage(pageName) {
    // Hide all pages
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));

    // Show selected page
    const page = document.getElementById(`${pageName}-page`);
    if (page) {
        page.classList.add('active');
        document.getElementById('page-title').textContent =
            pageName.charAt(0).toUpperCase() + pageName.slice(1);
    }

    // Load data for specific pages
    if (pageName === 'livestreams') {
        refreshLivestreams();
    }
}

function filterTalents(query) {
    const rows = document.querySelectorAll('#talents-tbody tr');
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(query) ? '' : 'none';
    });
}

function editTalent(talentId) {
    currentTalent = talents.find(t => t.id === talentId);
    if (!currentTalent) return;

    document.getElementById('edit-talent-id').value = currentTalent.id;
    document.getElementById('edit-name').value = currentTalent.name;
    document.getElementById('edit-status').value = currentTalent.status;
    document.getElementById('edit-bio').value = currentTalent.bio;

    showModal();
}

async function saveTalent() {
    const talentId = document.getElementById('edit-talent-id').value;
    const updates = {
        name: document.getElementById('edit-name').value,
        status: document.getElementById('edit-status').value,
        bio: document.getElementById('edit-bio').value
    };

    const success = await updateTalentData(talentId, updates);
    if (success) {
        closeModal();
        await loadTalents();
    }
}

async function changeTalentStatus(talentId, status) {
    if (!status) return;

    const success = await updateTalentStatus(talentId, status);
    if (success) {
        await loadTalents();
    }
}

function showModal() {
    document.getElementById('edit-modal').classList.add('show');
}

function closeModal() {
    document.getElementById('edit-modal').classList.remove('show');
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

async function refreshData() {
    showToast('Refreshing data...', 'info');
    await loadInitialData();
    showToast('Data refreshed', 'success');
}

async function refreshLivestreams() {
    showToast('Refreshing livestreams...', 'info');
    await loadLivestreams();
    showToast('Livestreams refreshed', 'success');
}

// Auto-refresh every 30 seconds
setInterval(() => {
    loadStats();
}, 30000);
