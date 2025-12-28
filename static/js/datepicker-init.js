// static/js/datepicker-init.js
function initializeLostFoundDatePicker() {
    const dateInput = document.getElementById('date-lost-input');
    const calendarBtn = document.getElementById('calendar-trigger');
    
    if (!dateInput || !calendarBtn) return;
    
    const today = new Date();
    const oneYearAgo = new Date();
    oneYearAgo.setFullYear(today.getFullYear() - 1);
    
    // Format: dd/mm/yyyy
    const formatDate = (date) => {
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const year = date.getFullYear();
        return `${day}/${month}/${year}`;
    };
    
    // Validate date string
    const isValidDate = (dateStr) => {
        const regex = /^(\d{2})\/(\d{2})\/(\d{4})$/;
        if (!regex.test(dateStr)) return false;
        
        const [, day, month, year] = dateStr.match(regex);
        const date = new Date(year, month - 1, day);
        
        return date.getDate() == day && 
               (date.getMonth() + 1) == month && 
               date.getFullYear() == year;
    };
    
    // Initialize flatpickr
    const picker = flatpickr(dateInput, {
        dateFormat: "d/m/Y",
        locale: "uk",
        maxDate: today,
        minDate: oneYearAgo,
        allowInput: true,
        clickOpens: true,
        disableMobile: true,
        onChange: function(selectedDates) {
            if (selectedDates[0]) {
                const selected = selectedDates[0];
                if (selected > today) {
                    alert("Cannot select future dates!");
                    picker.clear();
                }
            }
        }
    });
    
    // Open calendar on button click
    calendarBtn.addEventListener('click', () => picker.open());
    
    // Add input formatting
    dateInput.addEventListener('blur', function(e) {
        let value = e.target.value.trim();
        if (value) {
            // Try to parse and reformat
            const parts = value.replace(/[^\d]/g, '/').split('/').filter(p => p);
            if (parts.length >= 3) {
                const day = parts[0].padStart(2, '0');
                const month = parts[1].padStart(2, '0');
                const year = parts[2];
                if (year.length === 4) {
                    e.target.value = `${day}/${month}/${year}`;
                }
            }
        }
    });
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeLostFoundDatePicker);
} else {
    initializeLostFoundDatePicker();
}