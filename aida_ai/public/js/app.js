// Aida AI App Initialization

frappe.provide('aida_ai');

aida_ai = {
    version: '0.0.1',
    
    init: function() {
        console.log('Aida AI app initialized');
        this.setup_routes();
        this.setup_global_handlers();
    },
    
    setup_routes: function() {
        // Setup any custom routes for the app
        frappe.route_options = frappe.route_options || {};
    },
    
    setup_global_handlers: function() {
        // Setup global event handlers
        $(document).on('app_ready', function() {
            console.log('Aida AI: App ready event triggered');
        });
    },
    
    // Utility functions
    utils: {
        show_alert: function(message, indicator = 'blue') {
            frappe.show_alert({
                message: message,
                indicator: indicator
            });
        },
        
        format_currency: function(amount, currency = 'USD') {
            return format_currency(amount, currency);
        }
    }
};

// Initialize when DOM is ready
$(document).ready(function() {
    if (typeof frappe !== 'undefined') {
        aida_ai.init();
    }
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = aida_ai;
}