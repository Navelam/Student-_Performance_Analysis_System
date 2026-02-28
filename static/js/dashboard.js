// Dashboard JavaScript for SPAS

var Dashboard = {
    init: function() {
        this.loadStats();
        this.loadCharts();
        this.loadRecentActivity();
        this.setupRefreshTimer();
    },
    
    loadStats: function() {
        $.get('/api/dashboard/stats', function(data) {
            $('#total-students').text(data.total_students);
            $('#total-teachers').text(data.total_teachers);
            $('#total-subjects').text(data.total_subjects);
            $('#attendance-avg').text(data.attendance_avg + '%');
            $('#risk-students').text(data.risk_students);
            
            // Animate counters
            $('.counter').each(function() {
                var $this = $(this);
                $({ Counter: 0 }).animate({ Counter: $this.text() }, {
                    duration: 1000,
                    easing: 'swing',
                    step: function() {
                        $this.text(Math.ceil(this.Counter));
                    }
                });
            });
        });
    },
    
    loadCharts: function() {
        // Attendance Chart
        if ($('#attendanceChart').length) {
            $.get('/api/charts/attendance', function(data) {
                new Chart(document.getElementById('attendanceChart'), {
                    type: 'line',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Attendance %',
                            data: data.values,
                            borderColor: '#6f42c1',
                            backgroundColor: 'rgba(111, 66, 193, 0.1)',
                            tension: 0.4
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                display: false
                            }
                        }
                    }
                });
            });
        }
        
        // Performance Chart
        if ($('#performanceChart').length) {
            $.get('/api/charts/performance', function(data) {
                new Chart(document.getElementById('performanceChart'), {
                    type: 'bar',
                    data: {
                        labels: data.labels,
                        datasets: [{
                            label: 'Internal 1',
                            data: data.internal1,
                            backgroundColor: '#6f42c1',
                        }, {
                            label: 'Internal 2',
                            data: data.internal2,
                            backgroundColor: '#9b59b6',
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                            y: {
                                beginAtZero: true,
                                max: 20
                            }
                        }
                    }
                });
            });
        }
        
        // Risk Distribution Chart
        if ($('#riskChart').length) {
            $.get('/api/charts/risk-distribution', function(data) {
                new Chart(document.getElementById('riskChart'), {
                    type: 'doughnut',
                    data: {
                        labels: ['Critical', 'High', 'Medium', 'Low'],
                        datasets: [{
                            data: [data.critical, data.high, data.medium, data.low],
                            backgroundColor: ['#dc3545', '#fd7e14', '#ffc107', '#28a745']
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: 'bottom'
                            }
                        }
                    }
                });
            });
        }
    },
    
    loadRecentActivity: function() {
        $.get('/api/dashboard/recent-activity', function(data) {
            var container = $('#recent-activity');
            container.empty();
            
            data.forEach(function(activity) {
                var html = `
                    <div class="activity-item mb-3">
                        <div class="d-flex">
                            <div class="activity-icon me-3">
                                <i class="fas fa-${activity.icon} text-purple"></i>
                            </div>
                            <div class="flex-grow-1">
                                <p class="mb-1">${activity.description}</p>
                                <small class="text-muted">${activity.time}</small>
                            </div>
                        </div>
                    </div>
                `;
                container.append(html);
            });
        });
    },
    
    setupRefreshTimer: function() {
        setInterval(function() {
            Dashboard.loadStats();
        }, 60000); // Refresh every minute
    }
};

// Initialize dashboard
$(document).ready(function() {
    if ($('.dashboard-page').length) {
        Dashboard.init();
    }
});