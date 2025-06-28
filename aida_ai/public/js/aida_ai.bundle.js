// Aida AI JavaScript Bundle
// This file contains the main JavaScript functionality for the Aida AI app

// Initialize Aida AI when the page loads
frappe.ready(function() {
    console.log('Aida AI app loaded successfully');
    
    // Add any global JavaScript functionality here
    window.aida_ai = {
        version: '0.0.1',
        initialized: true
    };
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = window.aida_ai;
}