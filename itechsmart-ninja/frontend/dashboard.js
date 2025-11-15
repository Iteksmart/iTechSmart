// ===================================
// iTechSmart Ninja - Dashboard JavaScript
// ===================================

document.addEventListener('DOMContentLoaded', function() {
    
    // ===================================
    // Mobile Menu Toggle
    // ===================================
    const menuToggle = document.querySelector('.menu-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (menuToggle) {
        menuToggle.addEventListener('click', () => {
            sidebar.classList.toggle('active');
        });
    }
    
    // Close sidebar when clicking outside on mobile
    document.addEventListener('click', (e) => {
        if (window.innerWidth <= 768) {
            if (!sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
                sidebar.classList.remove('active');
            }
        }
    });
    
    // ===================================
    // Search Functionality
    // ===================================
    const searchInput = document.querySelector('.search-box input');
    
    if (searchInput) {
        // Keyboard shortcut (Ctrl+K or Cmd+K)
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                searchInput.focus();
            }
        });
        
        // Search functionality
        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.toLowerCase();
            console.log('Searching for:', query);
            // Implement search logic here
        });
    }
    
    // ===================================
    // Performance Chart
    // ===================================
    const performanceChartCanvas = document.getElementById('performanceChart');
    
    if (performanceChartCanvas) {
        const ctx = performanceChartCanvas.getContext('2d');
        
        const gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'rgba(99, 102, 241, 0.3)');
        gradient.addColorStop(1, 'rgba(99, 102, 241, 0)');
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Tasks Completed',
                    data: [65, 78, 66, 85, 72, 90, 95],
                    borderColor: '#6366f1',
                    backgroundColor: gradient,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 6,
                    pointBackgroundColor: '#6366f1',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: '#1e293b',
                        titleColor: '#f1f5f9',
                        bodyColor: '#cbd5e1',
                        borderColor: '#334155',
                        borderWidth: 1,
                        padding: 12,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return context.parsed.y + ' tasks';
                            }
                        }
                    }
                },
                scales: {
                    x: {
                        grid: {
                            display: false,
                            drawBorder: false
                        },
                        ticks: {
                            color: '#94a3b8'
                        }
                    },
                    y: {
                        grid: {
                            color: '#334155',
                            drawBorder: false
                        },
                        ticks: {
                            color: '#94a3b8',
                            callback: function(value) {
                                return value;
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                }
            }
        });
    }
    
    // ===================================
    // Animate Stats on Scroll
    // ===================================
    const animateValue = (element, start, end, duration) => {
        const range = end - start;
        const increment = range / (duration / 16);
        let current = start;
        
        const timer = setInterval(() => {
            current += increment;
            if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                element.textContent = end;
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current);
            }
        }, 16);
    };
    
    const observeStats = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const statValue = entry.target.querySelector('.stat-value');
                const text = statValue.textContent;
                const number = parseInt(text.replace(/\D/g, ''));
                
                if (number && !statValue.classList.contains('animated')) {
                    statValue.classList.add('animated');
                    animateValue(statValue, 0, number, 1500);
                }
            }
        });
    }, { threshold: 0.5 });
    
    document.querySelectorAll('.stat-card').forEach(card => {
        observeStats.observe(card);
    });
    
    // ===================================
    // Progress Bar Animation
    // ===================================
    const observeProgress = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progressFills = entry.target.querySelectorAll('.progress-fill');
                progressFills.forEach(fill => {
                    const width = fill.style.width;
                    fill.style.width = '0%';
                    setTimeout(() => {
                        fill.style.width = width;
                    }, 100);
                });
                observeProgress.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    const agentStats = document.querySelector('.agent-stats');
    if (agentStats) {
        observeProgress.observe(agentStats);
    }
    
    // ===================================
    // Task Checkbox Functionality
    // ===================================
    const taskCheckboxes = document.querySelectorAll('.task-checkbox input[type="checkbox"]');
    
    taskCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const taskItem = this.closest('.task-item');
            if (this.checked) {
                taskItem.style.opacity = '0.5';
                taskItem.querySelector('.task-title').style.textDecoration = 'line-through';
                
                // Show notification
                showNotification('Task completed! 🎉', 'success');
            } else {
                taskItem.style.opacity = '1';
                taskItem.querySelector('.task-title').style.textDecoration = 'none';
            }
        });
    });
    
    // ===================================
    // Quick Actions
    // ===================================
    const quickActionBtns = document.querySelectorAll('.quick-action-btn');
    
    quickActionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.querySelector('span').textContent;
            showNotification(`${action} initiated...`, 'info');
            
            // Add animation
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 100);
        });
    });
    
    // ===================================
    // Integration Connect Buttons
    // ===================================
    const connectBtns = document.querySelectorAll('.connect-btn');
    
    connectBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const integrationItem = this.closest('.integration-item');
            const integrationName = integrationItem.querySelector('span').textContent;
            
            // Simulate connection
            this.textContent = 'Connecting...';
            this.disabled = true;
            
            setTimeout(() => {
                integrationItem.classList.add('connected');
                this.remove();
                
                const statusDot = document.createElement('div');
                statusDot.className = 'status-dot';
                integrationItem.appendChild(statusDot);
                
                showNotification(`${integrationName} connected successfully!`, 'success');
            }, 1500);
        });
    });
    
    // ===================================
    // Notification System
    // ===================================
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = 'notification';
        
        const colors = {
            success: '#10b981',
            error: '#ef4444',
            warning: '#f59e0b',
            info: '#6366f1'
        };
        
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-times-circle',
            warning: 'fa-exclamation-circle',
            info: 'fa-info-circle'
        };
        
        notification.innerHTML = `
            <i class="fas ${icons[type]}"></i>
            <span>${message}</span>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: ${colors[type]};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 0.5rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
            z-index: 9999;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            animation: slideIn 0.3s ease;
            font-weight: 600;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, 3000);
    }
    
    // ===================================
    // Real-time Updates Simulation
    // ===================================
    function simulateRealTimeUpdates() {
        setInterval(() => {
            // Update random stat
            const statCards = document.querySelectorAll('.stat-card');
            const randomCard = statCards[Math.floor(Math.random() * statCards.length)];
            const statValue = randomCard.querySelector('.stat-value');
            
            if (statValue && !statValue.textContent.includes('%') && !statValue.textContent.includes('ms')) {
                const currentValue = parseInt(statValue.textContent.replace(/,/g, ''));
                const newValue = currentValue + Math.floor(Math.random() * 10);
                statValue.textContent = newValue.toLocaleString();
            }
        }, 5000);
    }
    
    // Start real-time updates
    simulateRealTimeUpdates();
    
    // ===================================
    // Time Filter Change
    // ===================================
    const timeFilter = document.querySelector('.time-filter');
    
    if (timeFilter) {
        timeFilter.addEventListener('change', function() {
            console.log('Time filter changed to:', this.value);
            // Update chart data based on selected time range
            showNotification('Chart updated', 'info');
        });
    }
    
    // ===================================
    // Activity Item Click
    // ===================================
    const activityItems = document.querySelectorAll('.activity-item');
    
    activityItems.forEach(item => {
        item.addEventListener('click', function() {
            const title = this.querySelector('.activity-title').textContent;
            console.log('Activity clicked:', title);
            // Show activity details
        });
    });
    
    // ===================================
    // Keyboard Shortcuts
    // ===================================
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + N for new task
        if ((e.ctrlKey || e.metaKey) && e.key === 'n') {
            e.preventDefault();
            showNotification('New task dialog opened', 'info');
        }
        
        // Ctrl/Cmd + / for help
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            showNotification('Keyboard shortcuts: Ctrl+K (Search), Ctrl+N (New Task)', 'info');
        }
    });
    
    // ===================================
    // Auto-refresh Data
    // ===================================
    function refreshDashboardData() {
        console.log('Refreshing dashboard data...');
        // Fetch latest data from API
        // Update UI with new data
    }
    
    // Refresh every 30 seconds
    setInterval(refreshDashboardData, 30000);
    
    // ===================================
    // Smooth Scroll for Navigation
    // ===================================
    document.querySelectorAll('.nav-item').forEach(item => {
        item.addEventListener('click', function(e) {
            // Remove active class from all items
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            // Add active class to clicked item
            this.classList.add('active');
        });
    });
    
    // ===================================
    // Console Welcome Message
    // ===================================
    console.log('%c🚀 iTechSmart Ninja Dashboard', 'font-size: 20px; font-weight: bold; color: #6366f1;');
    console.log('%cDashboard loaded successfully!', 'font-size: 14px; color: #10b981;');
    console.log('%cKeyboard shortcuts: Ctrl+K (Search), Ctrl+N (New Task), Ctrl+/ (Help)', 'font-size: 12px; color: #94a3b8;');
    
    // ===================================
    // Initialize Complete
    // ===================================
    console.log('✅ Dashboard initialized successfully!');
});

// ===================================
// CSS Animations
// ===================================
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;
document.head.appendChild(style);