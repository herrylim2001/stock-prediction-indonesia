// Configuration
const API_URL = 'http://localhost:5000/api';
const SOCKET_URL = 'http://localhost:5000';

// Global State
let socket = null;
let livestreams = [];
let talents = [];
let currentLivestream = null;
let currentUsername = 'User' + Math.floor(Math.random() * 10000);

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
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
    });

    // Real-time updates
    socket.on('livestream_started', (livestream) => {
        livestreams.push(livestream);
        renderLivestreams();
        updateLiveCount();
    });

    socket.on('livestream_ended', (data) => {
        livestreams = livestreams.filter(ls => ls.id !== data.livestream_id);
        renderLivestreams();
        updateLiveCount();

        // Close viewer if watching ended livestream
        if (currentLivestream && currentLivestream.id === data.livestream_id) {
            closeViewer();
            showNotification('This livestream has ended');
        }
    });

    socket.on('viewer_joined', (data) => {
        if (currentLivestream && currentLivestream.id === data.livestream_id) {
            updateViewerCount(data.viewers);
        }
        updateLivestreamViewers(data.livestream_id, data.viewers);
    });

    socket.on('viewer_left', (data) => {
        if (currentLivestream && currentLivestream.id === data.livestream_id) {
            updateViewerCount(data.viewers);
        }
        updateLivestreamViewers(data.livestream_id, data.viewers);
    });

    socket.on('new_comment', (data) => {
        if (currentLivestream) {
            addChatMessage(data.username, data.message);
        }
    });

    socket.on('like_animation', (data) => {
        if (currentLivestream && currentLivestream.id === data.livestream_id) {
            document.getElementById('like-count').textContent = data.likes;
            showLikeAnimation();
        }
    });

    socket.on('gift_received', (data) => {
        if (currentLivestream && currentLivestream.id === data.livestream_id) {
            showNotification(`Someone sent ${data.amount} diamonds! 💎`);
        }
    });
}

// Load Initial Data
async function loadInitialData() {
    showLoading();
    try {
        await Promise.all([
            loadLivestreams(),
            loadTalents()
        ]);
    } catch (error) {
        console.error('Error loading initial data:', error);
    } finally {
        hideLoading();
    }
}

// API Calls
async function loadLivestreams() {
    try {
        const response = await fetch(`${API_URL}/livestreams`);
        const data = await response.json();

        if (data.success) {
            livestreams = data.data;
            renderLivestreams();
            updateLiveCount();
        }
    } catch (error) {
        console.error('Error loading livestreams:', error);
    }
}

async function loadTalents() {
    try {
        const response = await fetch(`${API_URL}/talents`);
        const data = await response.json();

        if (data.success) {
            talents = data.data;
            renderTalents();
        }
    } catch (error) {
        console.error('Error loading talents:', error);
    }
}

// Render Functions
function renderLivestreams() {
    const container = document.getElementById('livestreams-grid');

    if (!livestreams || livestreams.length === 0) {
        container.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 60px 20px;">
                <i class="fas fa-video" style="font-size: 60px; margin-bottom: 20px; opacity: 0.5;"></i>
                <h3 style="margin-bottom: 10px;">No Live Streams Right Now</h3>
                <p style="opacity: 0.7;">Check back later for live shows!</p>
            </div>
        `;
        return;
    }

    container.innerHTML = livestreams.map(ls => `
        <div class="livestream-card" onclick="openViewer('${ls.id}')">
            <div class="livestream-thumbnail">
                <img src="${ls.thumbnail}" alt="${ls.title}">
                <span class="live-badge">
                    <i class="fas fa-circle"></i> LIVE
                </span>
                <span class="viewer-badge" id="viewer-badge-${ls.id}">
                    <i class="fas fa-eye"></i> ${ls.viewers || 0}
                </span>
            </div>
            <div class="livestream-info">
                <div class="livestream-talent">
                    <img src="${ls.talent_avatar}" alt="${ls.talent_name}">
                    <div>
                        <div class="livestream-talent-name">${ls.talent_name}</div>
                        <div class="livestream-title">${ls.title}</div>
                    </div>
                </div>
                <div class="livestream-stats">
                    <span><i class="fas fa-heart"></i> ${ls.likes || 0}</span>
                    <span><i class="fas fa-gem"></i> ${ls.diamonds || 0}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function renderTalents() {
    const container = document.getElementById('talents-grid');

    // Show only first 10 talents
    const displayTalents = talents.slice(0, 10);

    container.innerHTML = displayTalents.map(talent => `
        <div class="talent-card">
            <div class="talent-avatar-wrapper">
                <img src="${talent.avatar}" alt="${talent.name}" class="talent-avatar">
                <span class="talent-status ${talent.status}"></span>
            </div>
            <div class="talent-card-name">${talent.name}</div>
            <div class="talent-card-followers">
                ${talent.followers.toLocaleString()} followers
            </div>
        </div>
    `).join('');
}

function updateLiveCount() {
    document.getElementById('live-count').textContent = livestreams.length;
}

function updateLivestreamViewers(livestreamId, viewers) {
    const badge = document.getElementById(`viewer-badge-${livestreamId}`);
    if (badge) {
        badge.innerHTML = `<i class="fas fa-eye"></i> ${viewers}`;
    }
}

// Viewer Functions
function openViewer(livestreamId) {
    const livestream = livestreams.find(ls => ls.id === livestreamId);
    if (!livestream) return;

    currentLivestream = livestream;

    // Update viewer UI
    document.getElementById('viewer-talent-avatar').src = livestream.talent_avatar;
    document.getElementById('viewer-talent-name').textContent = livestream.talent_name;
    document.getElementById('viewer-count').textContent = livestream.viewers || 0;
    document.getElementById('like-count').textContent = livestream.likes || 0;

    // Clear chat
    document.getElementById('chat-messages').innerHTML = '';

    // Show modal
    document.getElementById('live-viewer-modal').classList.add('show');

    // Join livestream room
    socket.emit('join_livestream', { livestream_id: livestreamId });

    // Add welcome message
    setTimeout(() => {
        addSystemMessage('Welcome to the live stream! 👋');
    }, 500);
}

function closeViewer() {
    if (currentLivestream) {
        // Leave livestream room
        socket.emit('leave_livestream', { livestream_id: currentLivestream.id });
        currentLivestream = null;
    }

    // Hide modal
    document.getElementById('live-viewer-modal').classList.remove('show');

    // Close gift menu if open
    closeGiftMenu();
}

function updateViewerCount(count) {
    document.getElementById('viewer-count').textContent = count;
}

// Chat Functions
function sendComment() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();

    if (!message || !currentLivestream) return;

    // Send comment via socket
    socket.emit('send_comment', {
        livestream_id: currentLivestream.id,
        username: currentUsername,
        message: message
    });

    // Clear input
    input.value = '';
}

function addChatMessage(username, message) {
    const chatMessages = document.getElementById('chat-messages');

    const messageEl = document.createElement('div');
    messageEl.className = 'chat-message';
    messageEl.innerHTML = `
        <div class="chat-username">${username}</div>
        <div class="chat-text">${escapeHtml(message)}</div>
    `;

    chatMessages.appendChild(messageEl);

    // Auto scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Keep only last 50 messages
    while (chatMessages.children.length > 50) {
        chatMessages.removeChild(chatMessages.firstChild);
    }
}

function addSystemMessage(message) {
    const chatMessages = document.getElementById('chat-messages');

    const messageEl = document.createElement('div');
    messageEl.className = 'chat-message';
    messageEl.style.background = 'rgba(102, 126, 234, 0.5)';
    messageEl.innerHTML = `
        <div class="chat-text">${message}</div>
    `;

    chatMessages.appendChild(messageEl);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Like Functions
function sendLike() {
    if (!currentLivestream) return;

    socket.emit('send_like', {
        livestream_id: currentLivestream.id
    });
}

function showLikeAnimation() {
    const container = document.getElementById('like-animation-container');

    const heart = document.createElement('div');
    heart.className = 'floating-heart';
    heart.innerHTML = '❤️';
    heart.style.left = Math.random() * 30 + 'px';

    container.appendChild(heart);

    // Remove after animation
    setTimeout(() => {
        container.removeChild(heart);
    }, 3000);
}

// Gift Functions
function showGiftMenu() {
    document.getElementById('gift-menu').classList.add('show');
}

function closeGiftMenu() {
    document.getElementById('gift-menu').classList.remove('show');
}

async function sendGift(amount) {
    if (!currentLivestream) return;

    try {
        const response = await fetch(`${API_URL}/livestreams/${currentLivestream.id}/gift`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ amount })
        });

        const data = await response.json();

        if (data.success) {
            showNotification(`You sent ${amount} diamonds! 💎`);
            closeGiftMenu();

            // Show animation
            for (let i = 0; i < 5; i++) {
                setTimeout(() => showLikeAnimation(), i * 100);
            }
        }
    } catch (error) {
        console.error('Error sending gift:', error);
        showNotification('Failed to send gift');
    }
}

// Event Listeners
function setupEventListeners() {
    // Enter key to send comment
    document.getElementById('chat-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendComment();
        }
    });

    // Close modal on escape
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeViewer();
        }
    });
}

// Utility Functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showNotification(message) {
    // Simple notification using chat
    if (currentLivestream) {
        addSystemMessage(message);
    }
}

function showLoading() {
    document.getElementById('loading').classList.add('show');
}

function hideLoading() {
    document.getElementById('loading').classList.remove('show');
}

// Auto-refresh livestreams every 30 seconds
setInterval(() => {
    loadLivestreams();
}, 30000);
