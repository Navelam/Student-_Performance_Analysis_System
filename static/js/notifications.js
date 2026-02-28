/**
 * Notification System JavaScript
 * Handles notification fetching, display, and interactions
 */

// Global variables
let notificationCheckInterval = null;
let lastNotificationId = null;
let notificationSound = null;

// Initialize notification sound (optional)
try {
    notificationSound = new Audio('/static/sounds/notification.mp3');
} catch (e) {
    console.log('Notification sound not available');
}

/**
 * Initialize notification system
 */
function initNotifications() {
    console.log('Initializing notification system...');
    
    // Load initial notification count
    updateNotificationCount();
    
    // Load notification list (for dropdown)
    loadNotificationList();
    
    // Check for popup notifications
    checkForPopupNotification();
    
    // Set up periodic checking (every 30 seconds)
    if (notificationCheckInterval) {
        clearInterval(notificationCheckInterval);
    }
    
    notificationCheckInterval = setInterval(function() {
        updateNotificationCount();
        checkForPopupNotification();
    }, 30000);
    
    // Add click handler to notification bell
    $('#notificationBell, #notification-system .nav-link').on('click', function(e) {
        e.preventDefault();
        loadNotificationList();
    });
    
    // Mark all as read button
    $('#mark-all-read').on('click', function() {
        markAllAsRead();
    });
}

/**
 * Update notification count badge
 */
function updateNotificationCount() {
    $.get('/api/notifications/unread-count')
        .done(function(data) {
            if (data.success) {
                let count = data.count;
                let badge = $('#notification-badge');
                
                if (count > 0) {
                    badge.text(count).show();
                    
                    // Play sound for new notifications (only if count changed)
                    let lastCount = badge.data('last-count') || 0;
                    if (count > lastCount && notificationSound) {
                        notificationSound.play().catch(e => console.log('Sound play failed'));
                    }
                    badge.data('last-count', count);
                } else {
                    badge.hide();
                    badge.data('last-count', 0);
                }
            }
        })
        .fail(function(xhr, status, error) {
            console.error('Failed to fetch notification count:', error);
        });
}

/**
 * Load notification list into dropdown
 */
function loadNotificationList() {
    $('#notification-list').html(`
        <div class="text-center py-4 text-muted">
            <i class="fas fa-spinner fa-spin fa-2x mb-2"></i>
            <p class="mb-0">Loading...</p>
        </div>
    `);
    
    $.get('/api/notifications/list')
        .done(function(data) {
            if (data.success) {
                displayNotificationList(data.notifications);
            }
        })
        .fail(function(xhr, status, error) {
            console.error('Failed to load notifications:', error);
            $('#notification-list').html(`
                <div class="text-center p-3 text-danger">
                    <i class="fas fa-exclamation-circle fa-2x mb-2"></i>
                    <p class="mb-0">Failed to load notifications</p>
                </div>
            `);
        });
}

/**
 * Display notifications in dropdown
 */
function displayNotificationList(notifications) {
    let html = '';
    
    if (notifications.length === 0) {
        html = `
            <div class="text-center p-4 text-muted">
                <i class="fas fa-bell-slash fa-3x mb-3"></i>
                <h6>No notifications</h6>
                <p class="small">You're all caught up!</p>
            </div>
        `;
    } else {
        notifications.slice(0, 10).forEach(function(notif) {
            let icon = getNotificationIcon(notif.notification_type);
            let bgClass = notif.is_read ? '' : 'bg-light-unread';
            let textClass = notif.is_read ? '' : 'fw-bold';
            
            html += `
                <div class="notification-item ${bgClass} p-3 border-bottom" data-id="${notif.id}" onclick="markNotificationRead(${notif.id}, '${notif.link || '#'}')">
                    <div class="d-flex align-items-start">
                        <div class="me-3">
                            <i class="fas ${icon} fa-lg text-purple"></i>
                        </div>
                        <div class="flex-grow-1">
                            <div class="d-flex justify-content-between align-items-center mb-1">
                                <h6 class="mb-0 ${textClass}">${notif.title}</h6>
                                <small class="text-muted">${notif.time_ago}</small>
                            </div>
                            <p class="small text-muted mb-0">${truncateText(notif.message, 80)}</p>
                            ${notif.is_read ? '' : '<span class="badge bg-purple mt-1">New</span>'}
                        </div>
                    </div>
                </div>
            `;
        });
        
        if (notifications.length > 10) {
            html += `
                <div class="text-center p-2 border-top">
                    <small class="text-muted">+${notifications.length - 10} more notifications</small>
                </div>
            `;
        }
    }
    
    $('#notification-list').html(html);
}

/**
 * Check for latest notification to show popup
 */
function checkForPopupNotification() {
    // Don't show popup if user is not logged in
    if (!isLoggedIn()) return;
    
    // Check if popup was shown recently (within last hour)
    let lastShown = localStorage.getItem('notificationPopupLastShown');
    if (lastShown) {
        let lastTime = parseInt(lastShown);
        let now = Date.now();
        let hourInMs = 60 * 60 * 1000;
        
        if (now - lastTime < hourInMs) {
            return; // Don't show again within an hour
        }
    }
    
    $.get('/api/notifications/latest')
        .done(function(data) {
            if (data.success && data.notification) {
                let notif = data.notification;
                
                // Check if this is a new notification we haven't seen
                if (notif.id !== lastNotificationId) {
                    lastNotificationId = notif.id;
                    showNotificationPopup(notif);
                    localStorage.setItem('notificationPopupLastShown', Date.now());
                }
            }
        })
        .fail(function() {
            console.error('Failed to check for popup notification');
        });
}

/**
 * Show notification popup modal
 */
function showNotificationPopup(notification) {
    let icon = getNotificationIcon(notification.notification_type);
    let bgClass = getNotificationBgClass(notification.notification_type);
    
    let content = `
        <div class="text-center mb-3">
            <div class="notification-icon-large ${bgClass} text-white rounded-circle d-inline-flex align-items-center justify-content-center mb-3" style="width: 70px; height: 70px;">
                <i class="fas ${icon} fa-2x"></i>
            </div>
            <h5 class="fw-bold">${notification.title}</h5>
        </div>
        <p class="mb-2">${notification.message}</p>
        <small class="text-muted d-block mb-3">${notification.time_ago}</small>
    `;
    
    // Create modal if it doesn't exist
    if ($('#notificationPopupModal').length === 0) {
        createPopupModal();
    }
    
    $('#popupNotificationContent').html(content);
    
    // Set up view button
    $('#viewNotificationBtn').off('click').on('click', function() {
        markNotificationRead(notification.id, notification.link);
        $('#notificationPopupModal').modal('hide');
    });
    
    // Show modal
    $('#notificationPopupModal').modal('show');
    
    // Mark as read when modal is hidden
    $('#notificationPopupModal').off('hidden.bs.modal').on('hidden.bs.modal', function() {
        markNotificationRead(notification.id);
    });
}

/**
 * Create popup modal dynamically
 */
function createPopupModal() {
    let modalHtml = `
        <div class="modal fade" id="notificationPopupModal" tabindex="-1" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header bg-purple text-white">
                        <h5 class="modal-title">
                            <i class="fas fa-bell me-2"></i>New Notification
                        </h5>
                        <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body" id="popupNotificationContent">
                        <!-- Popup content will be loaded here -->
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-sm btn-outline-secondary" data-bs-dismiss="modal">
                            <i class="fas fa-clock me-1"></i>Later
                        </button>
                        <button type="button" class="btn btn-sm btn-purple" id="viewNotificationBtn">
                            <i class="fas fa-eye me-1"></i>View Now
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    $('body').append(modalHtml);
}

/**
 * Mark notification as read
 */
function markNotificationRead(notificationId, link = null) {
    $.post(`/api/notifications/${notificationId}/read`)
        .done(function(data) {
            if (data.success) {
                updateNotificationCount();
                
                // If link provided and not '#', redirect
                if (link && link !== '#') {
                    window.location.href = link;
                }
            }
        })
        .fail(function() {
            console.error('Failed to mark notification as read');
        });
}

/**
 * Mark all notifications as read
 */
function markAllAsRead() {
    $.post('/api/notifications/mark-all-read')
        .done(function(data) {
            if (data.success) {
                updateNotificationCount();
                loadNotificationList();
                
                // Show success message
                showToast('All notifications marked as read', 'success');
            }
        })
        .fail(function() {
            console.error('Failed to mark all as read');
            showToast('Failed to mark notifications as read', 'danger');
        });
}

/**
 * Show toast message
 */
function showToast(message, type = 'info') {
    let toastHtml = `
        <div class="position-fixed bottom-0 end-0 p-3" style="z-index: 9999">
            <div class="toast align-items-center text-white bg-${type} border-0 show" role="alert">
                <div class="d-flex">
                    <div class="toast-body">
                        <i class="fas fa-${type === 'success' ? 'check-circle' : 'info-circle'} me-2"></i>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        </div>
    `;
    
    $('body').append(toastHtml);
    setTimeout(() => $('.toast').remove(), 3000);
}

/**
 * Get icon for notification type
 */
function getNotificationIcon(type) {
    const icons = {
        'exam': 'fa-calendar-alt',
        'room': 'fa-door-open',
        'invigilation': 'fa-user-tie',
        'marks': 'fa-chart-line',
        'results': 'fa-star',
        'attendance': 'fa-clock',
        'announcement': 'fa-bullhorn'
    };
    return icons[type] || 'fa-bell';
}

/**
 * Get background class for notification type
 */
function getNotificationBgClass(type) {
    const classes = {
        'exam': 'bg-info',
        'room': 'bg-success',
        'invigilation': 'bg-warning',
        'marks': 'bg-primary',
        'results': 'bg-purple',
        'attendance': 'bg-danger',
        'announcement': 'bg-secondary'
    };
    return classes[type] || 'bg-info';
}

/**
 * Truncate text to specified length
 */
function truncateText(text, maxLength) {
    if (text.length > maxLength) {
        return text.substring(0, maxLength) + '...';
    }
    return text;
}

/**
 * Check if user is logged in
 */
function isLoggedIn() {
    return $('#notification-system').length > 0;
}

/**
 * Clean up interval when page unloads
 */
$(window).on('beforeunload', function() {
    if (notificationCheckInterval) {
        clearInterval(notificationCheckInterval);
    }
});

// Auto-initialize when DOM is ready
$(document).ready(function() {
    if ($('#notification-system').length) {
        initNotifications();
    }
});