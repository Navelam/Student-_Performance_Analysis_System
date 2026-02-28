// main.js - Shared JavaScript functions for teacher module

// Allow only numbers (no decimals)
function onlyNumbers(e) {
    var charCode = (e.which) ? e.which : e.keyCode;
    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        return false;
    }
    return true;
}

// Calculate row function for enter_marks page
function calculateRow(studentId) {
    let row = document.getElementById(`row-${studentId}`);
    if (!row) return;
    
    // Get values
    let total_classes = parseInt(row.querySelector('input[name="total_classes[]"]').value) || 0;
    let attended = parseInt(row.querySelector('input[name="attended_classes[]"]').value) || 0;
    let i1 = parseInt(row.querySelector('input[name="internal1[]"]').value) || 0;
    let i2 = parseInt(row.querySelector('input[name="internal2[]"]').value) || 0;
    let assign = parseInt(row.querySelector('input[name="assignment[]"]').value) || 0;
    let sem = parseInt(row.querySelector('input[name="seminar[]"]').value) || 0;
    
    // Validate ranges
    let hasError = false;
    
    if (attended > total_classes) {
        row.querySelector('input[name="attended_classes[]"]').classList.add('error');
        hasError = true;
    } else {
        row.querySelector('input[name="attended_classes[]"]').classList.remove('error');
    }
    
    if (i1 < 0 || i1 > 70) {
        row.querySelector('input[name="internal1[]"]').classList.add('error');
        hasError = true;
    } else {
        row.querySelector('input[name="internal1[]"]').classList.remove('error');
    }
    
    if (i2 < 0 || i2 > 70) {
        row.querySelector('input[name="internal2[]"]').classList.add('error');
        hasError = true;
    } else {
        row.querySelector('input[name="internal2[]"]').classList.remove('error');
    }
    
    if (assign < 0 || assign > 10) {
        row.querySelector('input[name="assignment[]"]').classList.add('error');
        hasError = true;
    } else {
        row.querySelector('input[name="assignment[]"]').classList.remove('error');
    }
    
    if (sem < 0 || sem > 10) {
        row.querySelector('input[name="seminar[]"]').classList.add('error');
        hasError = true;
    } else {
        row.querySelector('input[name="seminar[]"]').classList.remove('error');
    }
    
    if (hasError) {
        document.getElementById(`total-${studentId}`).textContent = 'ERR';
        document.getElementById(`final-${studentId}`).textContent = 'ERR';
        document.getElementById(`final-calc-${studentId}`).value = '0';
        document.getElementById(`grade-${studentId}`).innerHTML = '-';
        document.getElementById(`risk-${studentId}`).innerHTML = '-';
        return;
    }
    
    // Calculate attendance percentage
    let attendance_percent = total_classes > 0 ? Math.round((attended / total_classes) * 100) : 0;
    
    // Calculate total marks
    let total = i1 + i2 + assign + sem;
    document.getElementById(`total-${studentId}`).textContent = total;
    
    // Calculate final marks
    let final = Math.round((total / 160) * 20);
    document.getElementById(`final-${studentId}`).textContent = final;
    document.getElementById(`final-calc-${studentId}`).value = final;
    
    // Calculate grade
    let grade = '';
    if (final >= 18) grade = 'A+';
    else if (final >= 15) grade = 'A';
    else if (final >= 12) grade = 'B';
    else if (final >= 10) grade = 'C';
    else grade = 'D';
    
    let gradeClass = '';
    if (grade == 'A+') gradeClass = 'grade-aplus';
    else if (grade == 'A') gradeClass = 'grade-a';
    else if (grade == 'B') gradeClass = 'grade-b';
    else if (grade == 'C') gradeClass = 'grade-c';
    else gradeClass = 'grade-d';
    
    document.getElementById(`grade-${studentId}`).innerHTML = 
        `<span class="grade-badge ${gradeClass}">${grade}</span>`;
    
    // Calculate risk
    let risk = '';
    if (attendance_percent < 70 || final < 10) risk = 'Critical';
    else if (final < 15) risk = 'Average';
    else if (final == 20) risk = 'Best';
    else risk = 'Safe';
    
    let riskClass = '';
    if (risk == 'Critical') riskClass = 'risk-critical';
    else if (risk == 'Average') riskClass = 'risk-average';
    else if (risk == 'Safe') riskClass = 'risk-safe';
    else riskClass = 'risk-best';
    
    document.getElementById(`risk-${studentId}`).innerHTML = 
        `<span class="risk-badge ${riskClass}">${risk}</span>`;
}

// Format number with leading zeros
function padNumber(num, size) {
    let s = num + "";
    while (s.length < size) s = "0" + s;
    return s;
}

// Show notification
function showNotification(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'danger' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.getElementById('notification-area') || document.querySelector('.container');
    if (container) {
        container.insertAdjacentHTML('afterbegin', alertHtml);
        
        // Auto dismiss after 5 seconds
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) alert.remove();
        }, 5000);
    }
}

// Initialize DataTables
$(document).ready(function() {
    if ($.fn.DataTable) {
        $('.datatable').DataTable({
            responsive: true,
            pageLength: 10,
            language: {
                search: "_INPUT_",
                searchPlaceholder: "Search...",
                paginate: {
                    first: '<i class="fas fa-angle-double-left"></i>',
                    previous: '<i class="fas fa-angle-left"></i>',
                    next: '<i class="fas fa-angle-right"></i>',
                    last: '<i class="fas fa-angle-double-right"></i>'
                }
            }
        });
    }
});