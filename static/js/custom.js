// Custom JavaScript for alims.co.in

document.addEventListener('DOMContentLoaded', function() {
    // Initialize animations
    initAnimations();

    // Initialize enhanced form elements
    enhanceFormElements();

    // Initialize table enhancements
    enhanceTables();

    // Initialize notifications
    initNotifications();
});

// Add animation classes to elements
function initAnimations() {
    // Add fade-in animation to cards
    document.querySelectorAll('.card-enhanced').forEach((card, index) => {
        card.style.animationDelay = `${index * 0.1}s`;
        card.classList.add('animate-fadeIn');
    });

    // Add slide-in animation to status badges
    document.querySelectorAll('.status-badge').forEach((badge) => {
        badge.classList.add('animate-slideInUp');
    });

    // Add hover effects to buttons
    document.querySelectorAll('.btn-enhanced').forEach((button) => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
            this.style.boxShadow = 'var(--shadow-md)';
        });

        button.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
}



// Enhance form elements
function enhanceFormElements() {
    // Add enhanced styling to form inputs
    document.querySelectorAll('input[type="text"], input[type="email"], input[type="password"], input[type="date"], textarea, select').forEach(input => {
        input.classList.add('form-control-enhanced');
    });

    // Add enhanced styling to buttons
    document.querySelectorAll('button[type="submit"], .btn').forEach(button => {
        button.classList.add('btn-enhanced');

        // Add primary class if it has bg-indigo-600 class
        if (button.classList.contains('bg-indigo-600')) {
            button.classList.add('btn-primary');
        }
    });
}

// Enhance tables
function enhanceTables() {
    document.querySelectorAll('table').forEach(table => {
        table.classList.add('table-enhanced');

        // Add responsive wrapper if not already present
        if (!table.parentElement.classList.contains('table-responsive')) {
            const wrapper = document.createElement('div');
            wrapper.classList.add('table-responsive');
            table.parentNode.insertBefore(wrapper, table);
            wrapper.appendChild(table);
        }
    });
}

// Initialize notifications
function initNotifications() {
    // Find Django messages
    const messages = document.querySelectorAll('.messages .message');

    messages.forEach(message => {
        // Add notification styling
        message.classList.add('notification');

        // Add specific styling based on message tags
        if (message.classList.contains('success')) {
            message.classList.add('notification-success');
        } else if (message.classList.contains('error')) {
            message.classList.add('notification-error');
        } else if (message.classList.contains('info')) {
            message.classList.add('notification-info');
        } else if (message.classList.contains('warning')) {
            message.classList.add('notification-warning');
        }

        // Add close button
        const closeButton = document.createElement('button');
        closeButton.innerHTML = '&times;';
        closeButton.classList.add('notification-close');
        closeButton.addEventListener('click', function() {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        });

        message.appendChild(closeButton);

        // Auto-hide after 5 seconds
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });
}

// Function to show loading spinner
function showLoading(buttonElement) {
    // Save original button content
    buttonElement.dataset.originalContent = buttonElement.innerHTML;

    // Create spinner
    const spinner = document.createElement('span');
    spinner.classList.add('spinner');
    spinner.style.marginRight = '0.5rem';

    // Update button content
    buttonElement.innerHTML = '';
    buttonElement.appendChild(spinner);
    buttonElement.appendChild(document.createTextNode('Loading...'));
    buttonElement.disabled = true;
}

// Function to hide loading spinner
function hideLoading(buttonElement) {
    // Restore original content
    buttonElement.innerHTML = buttonElement.dataset.originalContent;
    buttonElement.disabled = false;
}

// Function to enhance status badges
function enhanceStatusBadges() {
    document.querySelectorAll('[data-status]').forEach(element => {
        const status = element.dataset.status;
        let config = {
            bgColor: 'bg-gray-100',
            textColor: 'text-gray-800',
            icon: 'fas fa-question-circle'
        };

        // Configure based on status
        switch(status) {
            case 'INVALID':
                config = {
                    bgColor: 'bg-red-100',
                    textColor: 'text-red-800',
                    icon: 'fas fa-times-circle'
                };
                break;
            case 'VALID':
                config = {
                    bgColor: 'bg-green-100',
                    textColor: 'text-green-800',
                    icon: 'fas fa-check-circle'
                };
                break;
            case 'CALL_NOT_ATTENDED':
                config = {
                    bgColor: 'bg-yellow-100',
                    textColor: 'text-yellow-800',
                    icon: 'fas fa-phone-slash'
                };
                break;
            case 'PLAN_PRESENTED':
                config = {
                    bgColor: 'bg-purple-100',
                    textColor: 'text-purple-800',
                    icon: 'fas fa-file-alt'
                };
                break;
            case 'INTERESTED':
                config = {
                    bgColor: 'bg-blue-100',
                    textColor: 'text-blue-800',
                    icon: 'fas fa-thumbs-up'
                };
                break;
            case 'NOT_INTERESTED':
                config = {
                    bgColor: 'bg-gray-100',
                    textColor: 'text-gray-800',
                    icon: 'fas fa-thumbs-down'
                };
                break;
            case 'FOLLOW_UP':
                config = {
                    bgColor: 'bg-indigo-100',
                    textColor: 'text-indigo-800',
                    icon: 'fas fa-calendar-check'
                };
                break;
            case 'SHORTLISTED':
                config = {
                    bgColor: 'bg-green-100',
                    textColor: 'text-green-800',
                    icon: 'fas fa-star'
                };
                break;
            case 'CAMPUS_VISIT':
                config = {
                    bgColor: 'bg-orange-100',
                    textColor: 'text-orange-800',
                    icon: 'fas fa-building'
                };
                break;
            case 'REGISTRATION':
                config = {
                    bgColor: 'bg-teal-100',
                    textColor: 'text-teal-800',
                    icon: 'fas fa-clipboard-check'
                };
                break;
            case 'ADMISSION':
                config = {
                    bgColor: 'bg-pink-100',
                    textColor: 'text-pink-800',
                    icon: 'fas fa-graduation-cap'
                };
                break;
        }

        // Apply configuration
        element.classList.add(config.bgColor, config.textColor, 'status-badge');

        // Add icon if not present
        if (!element.querySelector('i')) {
            const icon = document.createElement('i');
            icon.className = config.icon;
            element.prepend(icon);
        }
    });
}
