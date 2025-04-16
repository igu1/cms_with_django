/**
 * Task Countdown Timer
 * 
 * This script adds live countdown timers to task due dates in the admin interface.
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all countdown timers
    initializeCountdowns();
    
    // Update countdowns every minute
    setInterval(updateAllCountdowns, 60000);
});

/**
 * Initialize all countdown elements on the page
 */
function initializeCountdowns() {
    // Find all task due dates with countdown data attributes
    const taskRows = document.querySelectorAll('tr[data-due-date]');
    
    taskRows.forEach(row => {
        const dueDate = new Date(row.getAttribute('data-due-date'));
        const status = row.getAttribute('data-status');
        
        // Skip completed or cancelled tasks
        if (status === 'COMPLETED' || status === 'CANCELLED') {
            return;
        }
        
        // Get the countdown cell
        const countdownCell = row.querySelector('.field-due_date_display .countdown');
        if (countdownCell) {
            updateCountdown(countdownCell, dueDate);
        }
    });
}

/**
 * Update all countdown timers on the page
 */
function updateAllCountdowns() {
    const taskRows = document.querySelectorAll('tr[data-due-date]');
    
    taskRows.forEach(row => {
        const dueDate = new Date(row.getAttribute('data-due-date'));
        const status = row.getAttribute('data-status');
        
        // Skip completed or cancelled tasks
        if (status === 'COMPLETED' || status === 'CANCELLED') {
            return;
        }
        
        // Get the countdown cell
        const countdownCell = row.querySelector('.field-due_date_display .countdown');
        if (countdownCell) {
            updateCountdown(countdownCell, dueDate);
        }
    });
}

/**
 * Update a single countdown element
 */
function updateCountdown(element, dueDate) {
    const now = new Date();
    const timeRemaining = dueDate - now;
    
    // Format the countdown text
    let countdownText = '';
    let iconClass = '';
    let textColor = '';
    
    if (timeRemaining < 0) {
        // Overdue
        const millisecondsOverdue = Math.abs(timeRemaining);
        const daysOverdue = Math.floor(millisecondsOverdue / (1000 * 60 * 60 * 24));
        const hoursOverdue = Math.floor((millisecondsOverdue % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        
        if (daysOverdue > 0) {
            countdownText = `Overdue by ${daysOverdue}d ${hoursOverdue}h`;
        } else {
            countdownText = `Overdue by ${hoursOverdue}h`;
        }
        
        iconClass = 'fas fa-exclamation-triangle';
        textColor = '#C62828';
    } else if (timeRemaining < 24 * 60 * 60 * 1000) {
        // Due soon (within 24 hours)
        const hoursLeft = Math.floor(timeRemaining / (1000 * 60 * 60));
        const minutesLeft = Math.floor((timeRemaining % (1000 * 60 * 60)) / (1000 * 60));
        
        if (hoursLeft > 0) {
            countdownText = `${hoursLeft}h ${minutesLeft}m left`;
        } else {
            countdownText = `${minutesLeft}m left`;
        }
        
        iconClass = 'fas fa-clock';
        textColor = '#F57F17';
    } else {
        // Not due soon
        const daysLeft = Math.floor(timeRemaining / (1000 * 60 * 60 * 24));
        const hoursLeft = Math.floor((timeRemaining % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        
        countdownText = `${daysLeft}d ${hoursLeft}h left`;
        iconClass = 'fas fa-calendar-alt';
        textColor = '#1565C0';
    }
    
    // Update the element
    element.innerHTML = `<i class="${iconClass}"></i> ${countdownText}`;
    element.style.color = textColor;
}

/**
 * Add data attributes to task rows when the change list page loads
 */
document.addEventListener('DOMContentLoaded', function() {
    // Check if we're on the task change list page
    if (document.querySelector('#changelist-form')) {
        const taskRows = document.querySelectorAll('#result_list tbody tr');
        
        taskRows.forEach(row => {
            // Get the due date cell
            const dueDateCell = row.querySelector('.field-due_date_display');
            if (dueDateCell) {
                // Extract the date string
                const dateText = dueDateCell.textContent.trim().split('\n')[0];
                if (dateText && dateText !== '-') {
                    try {
                        // Parse the date (format: YYYY-MM-DD HH:MM)
                        const dateParts = dateText.match(/(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2})/);
                        if (dateParts) {
                            const dueDate = new Date(
                                parseInt(dateParts[1]), // year
                                parseInt(dateParts[2]) - 1, // month (0-based)
                                parseInt(dateParts[3]), // day
                                parseInt(dateParts[4]), // hour
                                parseInt(dateParts[5])  // minute
                            );
                            
                            // Add data attribute to the row
                            row.setAttribute('data-due-date', dueDate.toISOString());
                            
                            // Add countdown span to the cell
                            const countdownSpan = document.createElement('span');
                            countdownSpan.className = 'countdown';
                            countdownSpan.style.display = 'block';
                            countdownSpan.style.fontSize = '0.8em';
                            countdownSpan.style.marginTop = '4px';
                            dueDateCell.appendChild(countdownSpan);
                            
                            // Get the status
                            const statusCell = row.querySelector('.field-status_badge');
                            if (statusCell) {
                                const statusText = statusCell.textContent.trim();
                                if (statusText.includes('COMPLETED')) {
                                    row.setAttribute('data-status', 'COMPLETED');
                                } else if (statusText.includes('CANCELLED')) {
                                    row.setAttribute('data-status', 'CANCELLED');
                                } else {
                                    row.setAttribute('data-status', 'ACTIVE');
                                }
                            }
                        }
                    } catch (e) {
                        console.error('Error parsing date:', e);
                    }
                }
            }
        });
        
        // Initialize countdowns
        initializeCountdowns();
    }
});