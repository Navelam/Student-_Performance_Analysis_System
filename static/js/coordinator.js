// static/js/coordinator.js

// Coordinator Dashboard Functions
var CoordinatorDashboard = {
    init: function() {
        this.loadStats();
        this.loadRecentActivities();
        this.initCharts();
    },
    
    loadStats: function() {
        $.get('/coordinator/api/stats', function(data) {
            $('#upcoming-exams').text(data.upcoming_exams);
            $('#rooms-allocated').text(data.rooms_allocated);
            $('#invigilators-assigned').text(data.invigilators_assigned);
            $('#conflicts-detected').text(data.conflicts_detected);
        });
    },
    
    loadRecentActivities: function() {
        $.get('/coordinator/api/recent-timetable', function(data) {
            let html = '';
            data.forEach(function(item) {
                html += `
                    <tr>
                        <td>${item.date}</td>
                        <td>${item.session}</td>
                        <td>${item.department}</td>
                        <td>${item.subject}</td>
                    </tr>
                `;
            });
            $('#recent-timetable').html(html || '<tr><td colspan="4" class="text-center">No recent activities</td></tr>');
        });
        
        $.get('/coordinator/api/recent-rooms', function(data) {
            let html = '';
            data.forEach(function(item) {
                html += `
                    <tr>
                        <td>${item.date}</td>
                        <td>${item.room}</td>
                        <td>${item.block}</td>
                        <td>${item.department}</td>
                    </tr>
                `;
            });
            $('#recent-rooms').html(html || '<tr><td colspan="4" class="text-center">No recent allocations</td></tr>');
        });
    },
    
    initCharts: function() {
        // Exam distribution chart
        if ($('#examChart').length) {
            new Chart(document.getElementById('examChart'), {
                type: 'doughnut',
                data: {
                    labels: ['Internal 1', 'Internal 2', 'Semester'],
                    datasets: [{
                        data: [45, 40, 15],
                        backgroundColor: ['#6f42c1', '#9b59b6', '#e83e8c']
                    }]
                }
            });
        }
        
        // Room utilization chart
        if ($('#roomChart').length) {
            new Chart(document.getElementById('roomChart'), {
                type: 'bar',
                data: {
                    labels: ['Block A', 'Block B', 'Block C'],
                    datasets: [{
                        label: 'Utilization %',
                        data: [85, 78, 92],
                        backgroundColor: '#6f42c1'
                    }]
                }
            });
        }
    }
};

// Timetable Generator Functions
var TimetableGenerator = {
    init: function() {
        this.loadDepartments();
        this.setupEventListeners();
    },
    
    loadDepartments: function() {
        $.get('/api/departments', function(data) {
            let html = '';
            data.forEach(function(dept) {
                html += `
                    <div class="col-md-4 mb-2">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" name="departments" 
                                   value="${dept.id}" id="dept_${dept.id}" checked>
                            <label class="form-check-label" for="dept_${dept.id}">
                                ${dept.name} (${dept.code})
                            </label>
                        </div>
                    </div>
                `;
            });
            $('#departmentsList').html(html);
        });
    },
    
    setupEventListeners: function() {
        $('#timetableForm').on('submit', function(e) {
            e.preventDefault();
            TimetableGenerator.generate();
        });
        
        $('#session').on('change', function() {
            if ($(this).val() === 'BOTH') {
                $('#split-info').show();
            } else {
                $('#split-info').hide();
            }
        });
    },
    
    generate: function() {
        const formData = {
            exam_date: $('#examDate').val(),
            session: $('#session').val(),
            academic_year: $('#academicYear').val(),
            exam_type: $('#examType').val(),
            duration: $('#duration').val(),
            departments: $('input[name="departments"]:checked').map(function() { 
                return $(this).val(); 
            }).get(),
            ai_optimize: $('#aiOptimize').is(':checked')
        };
        
        if (!formData.exam_date || !formData.session || !formData.academic_year || 
            !formData.exam_type || formData.departments.length === 0) {
            alert('Please fill all required fields');
            return;
        }
        
        $('#generateBtn').html('<i class="fas fa-spinner fa-spin me-2"></i>Generating...')
                        .prop('disabled', true);
        
        $.ajax({
            url: '/coordinator/api/generate-timetable',
            method: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function(response) {
                TimetableGenerator.displayPreview(response.timetable);
                $('#generateBtn').html('<i class="fas fa-magic me-2"></i>Generate Timetable')
                                .prop('disabled', false);
            },
            error: function(xhr) {
                alert('Error generating timetable: ' + xhr.responseJSON.error);
                $('#generateBtn').html('<i class="fas fa-magic me-2"></i>Generate Timetable')
                                .prop('disabled', false);
            }
        });
    },
    
    displayPreview: function(timetable) {
        let html = '';
        
        // Group by session
        const morningExams = timetable.filter(e => e.session === '10AM');
        const afternoonExams = timetable.filter(e => e.session === '2PM');
        
        if (morningExams.length > 0) {
            html += '<tr><td colspan="6" class="table-purple-light"><strong>Morning Session (10:00 AM)</strong></td></tr>';
            morningExams.forEach(exam => {
                html += `
                    <tr>
                        <td>${exam.date}</td>
                        <td>${exam.session}</td>
                        <td>${exam.department}</td>
                        <td>${exam.subject}</td>
                        <td>Semester ${exam.semester}</td>
                        <td>${exam.duration} min</td>
                    </tr>
                `;
            });
        }
        
        if (afternoonExams.length > 0) {
            html += '<tr><td colspan="6" class="table-purple-light"><strong>Afternoon Session (2:00 PM)</strong></td></tr>';
            afternoonExams.forEach(exam => {
                html += `
                    <tr>
                        <td>${exam.date}</td>
                        <td>${exam.session}</td>
                        <td>${exam.department}</td>
                        <td>${exam.subject}</td>
                        <td>Semester ${exam.semester}</td>
                        <td>${exam.duration} min</td>
                    </tr>
                `;
            });
        }
        
        $('#previewBody').html(html);
        $('#previewSection').show();
    },
    
    confirmAllocation: function() {
        if (!window.generatedTimetable) return;
        
        $.ajax({
            url: '/coordinator/api/confirm-timetable',
            method: 'POST',
            data: JSON.stringify({ timetable: window.generatedTimetable }),
            contentType: 'application/json',
            success: function(response) {
                alert('Timetable confirmed successfully!');
                window.location.href = '/coordinator/schedule-view';
            },
            error: function(xhr) {
                alert('Error confirming timetable: ' + xhr.responseJSON.error);
            }
        });
    }
};

// Room Allocation Functions
var RoomAllocator = {
    init: function() {
        this.loadExamDates();
        this.loadRooms();
        this.setupEventListeners();
    },
    
    loadExamDates: function() {
        $.get('/coordinator/api/exam-dates', function(data) {
            let options = '<option value="">Choose date...</option>';
            data.forEach(function(date) {
                options += `<option value="${date}">${date}</option>`;
            });
            $('#examDate').html(options);
        });
    },
    
    loadRooms: function() {
        $.get('/coordinator/api/rooms', function(data) {
            let html = '';
            data.forEach(function(room) {
                html += `
                    <div class="col-md-4 mb-2">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" name="rooms" 
                                   value="${room.id}" id="room_${room.id}" checked>
                            <label class="form-check-label" for="room_${room.id}">
                                ${room.block} - ${room.room_number} (Capacity: ${room.capacity})
                            </label>
                        </div>
                    </div>
                `;
            });
            $('#roomsList').html(html);
        });
    },
    
    setupEventListeners: function() {
        $('#roomAllocationForm').on('submit', function(e) {
            e.preventDefault();
            RoomAllocator.allocate();
        });
        
        $('#examDate, #session').on('change', function() {
            if ($('#examDate').val() && $('#session').val()) {
                RoomAllocator.loadStudents();
            }
        });
    },
    
    loadStudents: function() {
        const examDate = $('#examDate').val();
        const session = $('#session').val();
        
        $.get(`/coordinator/api/students-for-exam?date=${examDate}&session=${session}`, function(data) {
            window.studentsForExam = data;
            $('#student-count').text(data.length);
        });
    },
    
    allocate: function() {
        const formData = {
            exam_date: $('#examDate').val(),
            session: $('#session').val(),
            rooms: $('input[name="rooms"]:checked').map(function() { return $(this).val(); }).get(),
            students: window.studentsForExam || [],
            ai_optimize: $('#aiOptimize').is(':checked')
        };
        
        if (!formData.exam_date || !formData.session || formData.rooms.length === 0) {
            alert('Please select date, session and rooms');
            return;
        }
        
        $('#allocateBtn').html('<i class="fas fa-spinner fa-spin me-2"></i>Allocating...')
                        .prop('disabled', true);
        
        $.ajax({
            url: '/coordinator/api/allocate-rooms',
            method: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function(response) {
                RoomAllocator.displayPreview(response.allocations);
                $('#allocateBtn').html('<i class="fas fa-magic me-2"></i>Allocate Rooms')
                                .prop('disabled', false);
            },
            error: function(xhr) {
                alert('Error allocating rooms: ' + xhr.responseJSON.error);
                $('#allocateBtn').html('<i class="fas fa-magic me-2"></i>Allocate Rooms')
                                .prop('disabled', false);
            }
        });
    },
    
    displayPreview: function(allocations) {
        let html = '';
        allocations.forEach(function(allocation) {
            html += `
                <tr>
                    <td>${allocation.room_number}</td>
                    <td>${allocation.block}</td>
                    <td>${allocation.student_name}</td>
                    <td>${allocation.registration_no}</td>
                    <td>${allocation.department}</td>
                    <td>Semester ${allocation.semester}</td>
                </tr>
            `;
        });
        $('#allocationPreviewBody').html(html);
        $('#allocationPreview').show();
        window.currentAllocation = allocations;
    },
    
    confirmAllocation: function() {
        if (!window.currentAllocation) return;
        
        $.ajax({
            url: '/coordinator/api/confirm-room-allocation',
            method: 'POST',
            data: JSON.stringify({ allocations: window.currentAllocation }),
            contentType: 'application/json',
            success: function(response) {
                alert('Room allocation confirmed successfully!');
                location.reload();
            },
            error: function(xhr) {
                alert('Error confirming allocation: ' + xhr.responseJSON.error);
            }
        });
    }
};

// Invigilator Assignment Functions
var InvigilatorAssigner = {
    init: function() {
        this.loadExamDates();
        this.loadTeachers();
        this.setupEventListeners();
    },
    
    loadExamDates: function() {
        $.get('/coordinator/api/exam-dates', function(data) {
            let options = '<option value="">Select Date</option>';
            data.forEach(function(date) {
                options += `<option value="${date}">${date}</option>`;
            });
            $('#examDate').html(options);
        });
    },
    
    loadTeachers: function() {
        $.get('/coordinator/api/teachers', function(data) {
            let html = '';
            data.forEach(function(teacher) {
                html += `
                    <div class="col-md-6 mb-2">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" name="teachers" 
                                   value="${teacher.id}" id="teacher_${teacher.id}" checked>
                            <label class="form-check-label" for="teacher_${teacher.id}">
                                ${teacher.name} - ${teacher.department}
                            </label>
                        </div>
                    </div>
                `;
            });
            $('#teachersList').html(html);
        });
    },
    
    setupEventListeners: function() {
        $('#invigilatorForm').on('submit', function(e) {
            e.preventDefault();
            InvigilatorAssigner.assign();
        });
        
        $('#examDate, #session').on('change', function() {
            if ($('#examDate').val() && $('#session').val()) {
                InvigilatorAssigner.loadRooms();
            }
        });
    },
    
    loadRooms: function() {
        const examDate = $('#examDate').val();
        const session = $('#session').val();
        
        $.get(`/coordinator/api/rooms-for-session?date=${examDate}&session=${session}`, function(data) {
            let options = '<option value="">Select Room</option>';
            data.forEach(function(room) {
                options += `<option value="${room.id}">${room.room_number} (${room.block}) - ${room.department}</option>`;
            });
            $('#room').html(options);
        });
    },
    
    assign: function() {
        const formData = {
            exam_date: $('#examDate').val(),
            session: $('#session').val(),
            room_id: $('#room').val(),
            teachers: $('input[name="teachers"]:checked').map(function() { return $(this).val(); }).get(),
            rules: {
                no_consecutive: $('#noConsecutive').is(':checked'),
                fair_distribution: $('#fairDistribution').is(':checked')
            },
            ai_optimize: $('#aiOptimize').is(':checked')
        };
        
        if (!formData.exam_date || !formData.session || !formData.room_id || formData.teachers.length < 2) {
            alert('Please select date, session, room and at least 2 teachers');
            return;
        }
        
        $('#assignBtn').html('<i class="fas fa-spinner fa-spin me-2"></i>Assigning...')
                      .prop('disabled', true);
        
        $.ajax({
            url: '/coordinator/api/assign-invigilators',
            method: 'POST',
            data: JSON.stringify(formData),
            contentType: 'application/json',
            success: function(response) {
                InvigilatorAssigner.displayPreview(response.assignments);
                $('#assignBtn').html('<i class="fas fa-magic me-2"></i>Assign Invigilators')
                              .prop('disabled', false);
            },
            error: function(xhr) {
                alert('Error assigning invigilators: ' + xhr.responseJSON.error);
                $('#assignBtn').html('<i class="fas fa-magic me-2"></i>Assign Invigilators')
                              .prop('disabled', false);
            }
        });
    },
    
    displayPreview: function(assignments) {
        let html = '';
        assignments.forEach(function(assignment) {
            html += `
                <tr>
                    <td>${assignment.date}</td>
                    <td>${assignment.session}</td>
                    <td>${assignment.room}</td>
                    <td>${assignment.block}</td>
                    <td>${assignment.invigilator1}</td>
                    <td>${assignment.invigilator2}</td>
                    <td>${assignment.department}</td>
                </tr>
            `;
        });
        $('#assignmentPreviewBody').html(html);
        $('#assignmentPreview').show();
        window.currentAssignments = assignments;
    },
    
    confirmAssignment: function() {
        if (!window.currentAssignments) return;
        
        $.ajax({
            url: '/coordinator/api/confirm-invigilator-assignment',
            method: 'POST',
            data: JSON.stringify({ assignments: window.currentAssignments }),
            contentType: 'application/json',
            success: function(response) {
                alert('Invigilator assignments confirmed successfully!');
                location.reload();
            },
            error: function(xhr) {
                alert('Error confirming assignments: ' + xhr.responseJSON.error);
            }
        });
    }
};

// Initialize on page load
$(document).ready(function() {
    // Check which page we're on and initialize appropriate module
    if ($('.coordinator-dashboard').length) {
        CoordinatorDashboard.init();
    }
    
    if ($('#timetableForm').length) {
        TimetableGenerator.init();
        window.generatedTimetable = null;
        window.confirmAllocation = TimetableGenerator.confirmAllocation;
    }
    
    if ($('#roomAllocationForm').length) {
        RoomAllocator.init();
        window.confirmRoomAllocation = RoomAllocator.confirmAllocation;
    }
    
    if ($('#invigilatorForm').length) {
        InvigilatorAssigner.init();
        window.confirmInvigilatorAssignment = InvigilatorAssigner.confirmAssignment;
    }
});