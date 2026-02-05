class NSKKSchoolApp {
    constructor() {
        this.currentPage = 'home';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadStats();
        this.loadBusRoutes();
        this.loadLibraryBooks();
        this.loadEvents();
        this.loadAlumni();
    }

    setupEventListeners() {
        // Admission form
        document.getElementById('admission-form').addEventListener('submit', (e) => this.handleAdmissionSubmit(e));

        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                const href = e.target.getAttribute('href');
                if (href && href.startsWith('#')) {
                    e.preventDefault();
                    document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
                    e.target.classList.add('active');
                    // Close mobile menu
                    this.closeMobileMenu();
                }
            });
        });

        // Event filters
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.filterEvents(e));
        });

        // Contact form
        document.querySelector('.contact-form')?.addEventListener('submit', (e) => this.handleContactSubmit(e));

        // Hamburger menu
        document.querySelector('.hamburger')?.addEventListener('click', () => this.toggleMobileMenu());
        
        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            const navMenu = document.querySelector('.nav-menu');
            const hamburger = document.querySelector('.hamburger');
            if (navMenu && hamburger && !navMenu.contains(e.target) && !hamburger.contains(e.target)) {
                this.closeMobileMenu();
            }
        });
    }

    toggleMobileMenu() {
        const navMenu = document.querySelector('.nav-menu');
        const hamburger = document.querySelector('.hamburger');
        navMenu?.classList.toggle('active');
        hamburger?.classList.toggle('active');
    }

    closeMobileMenu() {
        const navMenu = document.querySelector('.nav-menu');
        const hamburger = document.querySelector('.hamburger');
        navMenu?.classList.remove('active');
        hamburger?.classList.remove('active');
    }

    async loadStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            document.getElementById('stat-students').textContent = data.total_students;
            document.getElementById('stat-staff').textContent = data.total_staff;
            document.getElementById('stat-events').textContent = data.total_events;
            document.getElementById('stat-alumni').textContent = data.total_alumni;
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    async loadBusRoutes() {
        try {
            const response = await fetch('/api/bus/routes');
            const routes = await response.json();
            const container = document.getElementById('bus-routes');
            
            if (routes.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #999;">No bus routes available</p>';
                return;
            }

            container.innerHTML = routes.map(route => `
                <div class="bus-card">
                    <h4>🚌 ${route.route_name}</h4>
                    <p><strong>Bus Number:</strong> ${route.bus_number}</p>
                    <p><strong>Driver:</strong> ${route.driver_name}</p>
                    <p><strong>Current Location:</strong> ${route.current_location}</p>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading bus routes:', error);
        }
    }

    async loadLibraryBooks() {
        try {
            const response = await fetch('/api/library/books');
            const books = await response.json();
            const container = document.getElementById('library-books');
            
            if (books.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #999;">No books available</p>';
                return;
            }

            container.innerHTML = books.map(book => `
                <div class="book-card">
                    <div class="book-cover">📖</div>
                    <div class="book-info">
                        <h4>${this.escapeHtml(book.title)}</h4>
                        <p><strong>Author:</strong> ${this.escapeHtml(book.author)}</p>
                        <p><strong>Category:</strong> ${book.category}</p>
                        <p><strong>Available:</strong> ${book.available}</p>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading library books:', error);
        }

        document.getElementById('library-category').addEventListener('change', async (e) => {
            const category = e.target.value;
            const url = category ? `/api/library/books?category=${category}` : '/api/library/books';
            const response = await fetch(url);
            const books = await response.json();
            const container = document.getElementById('library-books');
            
            container.innerHTML = books.map(book => `
                <div class="book-card">
                    <div class="book-cover">📖</div>
                    <div class="book-info">
                        <h4>${this.escapeHtml(book.title)}</h4>
                        <p><strong>Author:</strong> ${this.escapeHtml(book.author)}</p>
                        <p><strong>Category:</strong> ${book.category}</p>
                        <p><strong>Available:</strong> ${book.available}</p>
                    </div>
                </div>
            `).join('');
        });
    }

    async loadEvents() {
        try {
            const response = await fetch('/api/events');
            const events = await response.json();
            const container = document.getElementById('events-grid');
            
            if (events.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #999;">No events scheduled</p>';
                return;
            }

            container.innerHTML = events.map(event => `
                <div class="event-card" data-category="${event.category}">
                    <div class="event-image">🎉</div>
                    <div class="event-content">
                        <span class="event-badge">${event.category}</span>
                        <h4>${this.escapeHtml(event.title)}</h4>
                        <p class="event-meta">📅 ${event.event_date}</p>
                        <p class="event-meta">📍 ${this.escapeHtml(event.location)}</p>
                        <p style="color: #666; margin-top: 0.5rem;">${this.escapeHtml(event.description)}</p>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading events:', error);
        }
    }

    filterEvents(e) {
        document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');

        const filter = e.target.dataset.filter;
        const cards = document.querySelectorAll('.event-card');

        cards.forEach(card => {
            if (filter === 'all' || card.dataset.category === filter) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }

    async loadAlumni() {
        try {
            const response = await fetch('/api/alumni');
            const alumni = await response.json();
            const container = document.getElementById('alumni-grid');
            
            if (alumni.length === 0) {
                container.innerHTML = '<p style="text-align: center; color: #999;">No alumni records yet</p>';
                return;
            }

            container.innerHTML = alumni.map(person => `
                <div class="alumni-card">
                    <div class="alumni-photo">👨‍🎓</div>
                    <div class="alumni-info">
                        <div class="alumni-name">${this.escapeHtml(person.full_name)}</div>
                        <div class="alumni-designation">${person.designation || 'Not specified'}</div>
                        <div class="alumni-org">${person.current_organization || 'Not specified'}</div>
                        <small style="color: #999;">Class of ${person.graduation_year}</small>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading alumni:', error);
        }
    }

    async handleAdmissionSubmit(e) {
        e.preventDefault();
        
        const formData = new FormData(e.target);
        const data = Object.fromEntries(formData);

        try {
            const response = await fetch('/api/admission/apply', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });

            if (response.ok) {
                this.showNotification('Admission application submitted successfully!', 'success');
                e.target.reset();
            } else {
                this.showNotification('Error submitting application', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Error submitting application', 'error');
        }
    }

    async handleContactSubmit(e) {
        e.preventDefault();
        this.showNotification('Thank you for contacting us! We will get back to you soon.', 'success');
        e.target.reset();
    }

    showNotification(message, type) {
        const notification = document.getElementById('notification');
        notification.textContent = message;
        notification.className = `notification show ${type}`;
        
        setTimeout(() => {
            notification.classList.remove('show');
        }, 3000);
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

document.addEventListener('DOMContentLoaded', () => {
    new NSKKSchoolApp();
});
