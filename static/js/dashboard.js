class DashboardApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadDashboardData();
        this.loadAdmissions();
    }

    setupEventListeners() {
        // Tab switching
        document.querySelectorAll('.menu-link').forEach(link => {
            link.addEventListener('click', (e) => this.switchTab(e));
        });

        // Mobile sidebar toggle
        const hamburger = document.querySelector('.hamburger');
        if (hamburger) {
            hamburger.addEventListener('click', () => this.toggleSidebar());
        }

        // Close sidebar when clicking outside
        document.addEventListener('click', (e) => {
            const sidebar = document.querySelector('.sidebar');
            const hamburger = document.querySelector('.hamburger');
            if (sidebar && hamburger && !sidebar.contains(e.target) && !hamburger.contains(e.target)) {
                sidebar.classList.remove('active');
                hamburger.classList.remove('active');
            }
        });

        // Close sidebar when a menu item is clicked (on mobile)
        document.querySelectorAll('.menu-link').forEach(link => {
            link.addEventListener('click', () => {
                const sidebar = document.querySelector('.sidebar');
                if (window.innerWidth <= 768) {
                    sidebar?.classList.remove('active');
                    document.querySelector('.hamburger')?.classList.remove('active');
                }
            });
        });
    }

    toggleSidebar() {
        const sidebar = document.querySelector('.sidebar');
        const hamburger = document.querySelector('.hamburger');
        sidebar?.classList.toggle('active');
        hamburger?.classList.toggle('active');
    }

    switchTab(e) {
        e.preventDefault();
        const tab = e.target.closest('.menu-link').dataset.tab;

        // Update menu
        document.querySelectorAll('.menu-link').forEach(link => {
            link.classList.remove('active');
        });
        e.target.closest('.menu-link').classList.add('active');

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(tab + '-tab').classList.add('active');

        // Load data
        this.loadTabData(tab);
    }

    async loadDashboardData() {
        try {
            const response = await fetch('/api/stats');
            const stats = await response.json();

            document.getElementById('dash-students').textContent = stats.total_students;
            document.getElementById('dash-staff').textContent = stats.total_staff;
            document.getElementById('dash-admissions').textContent = stats.pending_admissions;
            document.getElementById('dash-routes').textContent = stats.active_routes;
        } catch (error) {
            console.error('Error loading dashboard data:', error);
        }
    }

    async loadAdmissions() {
        try {
            const response = await fetch('/api/admission/applications');
            const admissions = await response.json();
            const tbody = document.getElementById('admissions-tbody');

            tbody.innerHTML = admissions.map(app => `
                <tr>
                    <td>${this.escapeHtml(app.full_name)}</td>
                    <td>${this.escapeHtml(app.email)}</td>
                    <td>${app.class_grade}</td>
                    <td>${app.applied_on}</td>
                    <td><span class="status-badge ${app.status}">${app.status}</span></td>
                    <td>
                        <button class="btn btn-sm btn-success" onclick="approveAdmission(${app.id})">Approve</button>
                        <button class="btn btn-sm btn-danger" onclick="rejectAdmission(${app.id})">Reject</button>
                    </td>
                </tr>
            `).join('');
        } catch (error) {
            console.error('Error loading admissions:', error);
        }
    }

    loadTabData(tab) {
        switch(tab) {
            case 'admissions':
                this.loadAdmissions();
                break;
            case 'events':
                this.loadEvents();
                break;
            case 'library':
                this.loadLibraryBooks();
                break;
            case 'alumni':
                this.loadAlumniAdmin();
                break;
            case 'notices':
                this.loadNotices();
                break;
        }
    }

    async loadEvents() {
        try {
            const response = await fetch('/api/events');
            const events = await response.json();
            const container = document.getElementById('events-list');

            container.innerHTML = events.map(event => `
                <div class="event-item">
                    <h4>${this.escapeHtml(event.title)}</h4>
                    <p>${this.escapeHtml(event.description)}</p>
                    <small>📅 ${event.event_date} | 📍 ${event.location}</small>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading events:', error);
        }
    }

    async loadLibraryBooks() {
        try {
            const response = await fetch('/api/library/books');
            const books = await response.json();
            const tbody = document.getElementById('library-tbody');

            tbody.innerHTML = books.map(book => `
                <tr>
                    <td>${this.escapeHtml(book.title)}</td>
                    <td>${this.escapeHtml(book.author)}</td>
                    <td>${book.category}</td>
                    <td>${book.available}</td>
                </tr>
            `).join('');
        } catch (error) {
            console.error('Error loading library books:', error);
        }
    }

    async loadAlumniAdmin() {
        try {
            const response = await fetch('/api/alumni');
            const alumni = await response.json();
            const container = document.getElementById('admin-alumni-grid');

            container.innerHTML = alumni.map(person => `
                <div class="alumni-card">
                    <div class="alumni-photo">👨‍🎓</div>
                    <div class="alumni-info">
                        <div class="alumni-name">${this.escapeHtml(person.full_name)}</div>
                        <div class="alumni-designation">${person.designation || 'N/A'}</div>
                        <div class="alumni-org">${person.current_organization || 'N/A'}</div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading alumni:', error);
        }
    }

    async loadNotices() {
        try {
            const response = await fetch('/api/notices');
            const notices = await response.json();
            const container = document.getElementById('notices-list');

            container.innerHTML = notices.map(notice => `
                <div class="notice-item">
                    <h4>${this.escapeHtml(notice.title)}</h4>
                    <p>${this.escapeHtml(notice.content)}</p>
                    <small>Posted on ${notice.created_at}</small>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading notices:', error);
        }
    }

    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }
}

function approveAdmission(id) {
    fetch(`/api/admission/${id}/approve`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' }
    }).then(() => location.reload());
}

function rejectAdmission(id) {
    if (confirm('Are you sure?')) {
        // Add rejection logic
        location.reload();
    }
}

function showEventModal() {
    document.getElementById('event-modal').classList.add('show');
}

function showBookModal() {
    // Modal for adding books
}

function showAlumniModal() {
    // Modal for adding alumni
}

function showNoticeModal() {
    // Modal for posting notices
}

// Close modal
document.addEventListener('DOMContentLoaded', () => {
    new DashboardApp();

    const modal = document.getElementById('event-modal');
    if (modal) {
        modal.querySelector('.close').addEventListener('click', () => {
            modal.classList.remove('show');
        });
    }
});
