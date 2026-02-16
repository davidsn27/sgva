// ================================================
// SGVA Dashboard - JavaScript
// ================================================

const API_BASE = 'http://127.0.0.1:8000/api';
let token = localStorage.getItem('token');
let currentUser = JSON.parse(localStorage.getItem('user') || '{}');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    if (token) {
        showPage('dashboard');
        loadDashboard();
    } else {
        showPage('login');
    }
});

// API Requests
async function apiCall(endpoint, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            ...options,
            headers,
        });

        if (response.status === 401) {
            logout();
            return null;
        }

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'API Error');
        }

        return await response.json();
    } catch (error) {
        showToast(error.message, 'error');
        console.error('API Error:', error);
        return null;
    }
}

// Navigation
function goToPage(page) {
    showPage(`${page}-page`);
    if (page === 'dashboard') loadDashboard();
    if (page === 'postulaciones') loadPostulaciones();
    if (page === 'analytics') loadAnalytics();
}

function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
    const page = document.getElementById(pageId);
    if (page) page.classList.add('active');
    if (pageId !== 'login-page') {
        document.querySelector('.navbar').classList.remove('hidden');
    } else {
        document.querySelector('.navbar').classList.add('hidden');
    }
}

// Auth
async function handleLogin(e) {
    e.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    
    const response = await apiCall('/token/', {
        method: 'POST',
        body: JSON.stringify({ username, password }),
    });

    if (response) {
        token = response.access;
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(response.user || {}));
        currentUser = response.user || {};
        document.getElementById('username').value = '';
        document.getElementById('password').value = '';
        showToast('¡Sesión iniciada!', 'success');
        goToPage('dashboard');
    }
}

function oauthLogin(provider) {
    const redirectUri = `${window.location.origin}/oauth-callback`;
    window.location.href = `/oauth/${provider}/?redirect_uri=${redirectUri}`;
}

function logout() {
    token = null;
    currentUser = {};
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    showPage('login-page');
    showToast('Sesión cerrada', 'success');
}

// Dashboard
async function loadDashboard() {
    // Update user info
    document.getElementById('user-info').textContent = 
        currentUser.nombre ? `Bienvenido, ${currentUser.nombre}!` : 'Bienvenido';

    // Load postulaciones
    const postulaciones = await apiCall('/postulaciones/');
    if (postulaciones) {
        const total = postulaciones.length || postulaciones.count || 0;
        const aceptadas = postulaciones.filter?.((p) => p.estado === 'SELECCIONADO').length || 0;
        const pendientes = postulaciones.filter?.((p) => p.estado === 'PENDIENTE').length || 0;

        document.getElementById('stat-postulaciones').textContent = total;
        document.getElementById('stat-aceptadas').textContent = aceptadas;
        document.getElementById('stat-pendientes').textContent = pendientes;

        // Recent postulaciones
        const recent = Array.isArray(postulaciones) 
            ? postulaciones.slice(0, 3)
            : postulaciones.results?.slice(0, 3) || [];
        renderPostulations(recent, 'recent-postulaciones');
    }

    // Load ratings
    const ratings = await apiCall('/calificaciones/mi_promedio/');
    if (ratings) {
        document.getElementById('stat-rating').textContent = 
            ratings.promedio ? ratings.promedio.toFixed(1) : '-';
    }
}

// Postulaciones
async function loadPostulaciones() {
    const postulaciones = await apiCall('/postulaciones/');
    if (postulaciones) {
        const items = Array.isArray(postulaciones) ? postulaciones : postulaciones.results || [];
        renderPostulations(items, 'postulaciones-container');
    }
}

function renderPostulations(postulaciones, containerId) {
    const container = document.getElementById(containerId);
    if (!postulaciones || postulaciones.length === 0) {
        container.innerHTML = '<div class="text-center">No hay postulaciones</div>';
        return;
    }

    container.innerHTML = postulaciones.map(post => `
        <div class="postulation-item">
            <div class="postulation-header">
                <div class="postulation-title">${post.empresa_nombre || 'Empresa'}</div>
                <span class="status-badge status-${post.estado.toLowerCase()}">
                    ${post.estado}
                </span>
            </div>
            <div class="postulation-meta">
                <div><strong>Fecha:</strong> ${new Date(post.fecha_postulacion).toLocaleDateString('es-ES')}</div>
                <div><strong>Aprendiz:</strong> ${post.aprendiz_nombre || 'N/A'}</div>
            </div>
            <div class="postulation-description">
                Días restantes: <strong>${post.dias_restantes || 0}</strong>
            </div>
            <div class="postulation-actions">
                <button class="btn-primary" onclick="viewPostulation(${post.id})">
                    <i class="fas fa-eye"></i> Ver detalles
                </button>
                ${post.estado === 'PENDIENTE' ? `
                    <button class="btn-secondary" onclick="updatePostulationStatus(${post.id}, 'SELECCIONADO')">
                        <i class="fas fa-check"></i> Aceptar
                    </button>
                    <button class="btn-danger" onclick="updatePostulationStatus(${post.id}, 'RECHAZADO')">
                        <i class="fas fa-times"></i> Rechazar
                    </button>
                ` : ''}
            </div>
        </div>
    `).join('');
}

function viewPostulation(id) {
    alert(`Ver detalles de postulación ${id}`);
}

async function updatePostulationStatus(id, status) {
    const response = await apiCall(`/postulaciones/${id}/cambiar_estado/`, {
        method: 'POST',
        body: JSON.stringify({ estado: status }),
    });

    if (response) {
        showToast('Postulación actualizada', 'success');
        loadPostulaciones();
    }
}

// Analytics
async function loadAnalytics() {
    const stats = await apiCall('/analytics/estadisticas/');
    if (stats) {
        document.getElementById('conversion-rate').textContent = 
            stats.tasa_conversion ? `${stats.tasa_conversion.toFixed(1)}%` : '0%';
        document.getElementById('total-aprendices').textContent = 
            stats.total_aprendices || 0;
        document.getElementById('total-empresas').textContent = 
            stats.total_empresas || 0;
    }

    // Load postulaciones por estado
    const porEstado = await apiCall('/analytics/postulaciones_por_estado/');
    if (porEstado) {
        renderEstadosChart(porEstado);
    }
}

function renderEstadosChart(data) {
    const chart = document.getElementById('chart-estados');
    if (!data || data.length === 0) {
        chart.innerHTML = '<div class="text-center">No hay datos</div>';
        return;
    }

    const html = data.map(item => `
        <div class="stat-item">
            <span>${item.estado}</span>
            <strong>${item.count} postulaciones</strong>
        </div>
    `).join('');

    chart.innerHTML = `<div class="stats-list">${html}</div>`;
}

// Utils
function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Event Listeners
document.getElementById('search-input')?.addEventListener('input', async (e) => {
    const query = e.target.value;
    if (query.length > 0) {
        const postulaciones = await apiCall(`/postulaciones/?search=${query}`);
        if (postulaciones) {
            const items = Array.isArray(postulaciones) ? postulaciones : postulaciones.results || [];
            renderPostulations(items, 'postulaciones-container');
        }
    } else {
        loadPostulaciones();
    }
});

document.getElementById('estado-filter')?.addEventListener('change', async (e) => {
    const estado = e.target.value;
    if (estado) {
        const postulaciones = await apiCall(`/postulaciones/?estado=${estado}`);
        if (postulaciones) {
            const items = Array.isArray(postulaciones) ? postulaciones : postulaciones.results || [];
            renderPostulations(items, 'postulaciones-container');
        }
    } else {
        loadPostulaciones();
    }
});

console.log('SGVA Dashboard initialized');
