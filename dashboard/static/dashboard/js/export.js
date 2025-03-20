/**
 * Export functionality for the Auction Analysis Dashboard
 */

document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners to all export buttons
    const exportButtons = document.querySelectorAll('.export-btn');
    
    exportButtons.forEach(button => {
        button.addEventListener('click', function() {
            const dataType = this.getAttribute('data-type');
            const productId = this.getAttribute('data-product');
            
            // Show loading state
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="bi bi-hourglass-split"></i> Exporting...';
            this.disabled = true;
            
            // Create form data
            const formData = new FormData();
            formData.append('data_type', dataType);
            
            // Get auction ID from URL or input field
            let auctionId = document.getElementById('auction-id-input')?.value;
            if (!auctionId) {
                const urlParams = new URLSearchParams(window.location.search);
                auctionId = urlParams.get('auction_id');
            }
            
            formData.append('auction_id', auctionId);
            
            // Add product ID if available
            if (productId) {
                formData.append('product_id', productId);
            }
            
            // Send request to export endpoint
            fetch('/export/', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Export failed');
                }
                return response.blob();
            })
            .then(blob => {
                // Create a download link
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                
                // Set filename based on data type
                let filename = `${dataType}_${auctionId}.csv`;
                if (productId) {
                    filename = `product_${productId}_auction_${auctionId}.csv`;
                }
                
                a.download = filename;
                
                // Trigger download
                document.body.appendChild(a);
                a.click();
                
                // Clean up
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                // Reset button state
                this.innerHTML = originalText;
                this.disabled = false;
                
                // Show success message
                showNotification('Export successful', 'success');
            })
            .catch(error => {
                console.error('Error exporting data:', error);
                
                // Reset button state
                this.innerHTML = originalText;
                this.disabled = false;
                
                // Show error message
                showNotification('Export failed. Please try again.', 'error');
            });
        });
    });
    
    /**
     * Shows a notification message
     * @param {string} message - The message to display
     * @param {string} type - The type of notification (success, error)
     */
    function showNotification(message, type) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="bi ${type === 'success' ? 'bi-check-circle' : 'bi-exclamation-circle'}"></i>
                <span>${message}</span>
            </div>
        `;
        
        // Add to document
        document.body.appendChild(notification);
        
        // Show notification
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Remove after delay
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
    
    // Add notification styles if not already present
    if (!document.getElementById('notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            .notification {
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 15px 20px;
                border-radius: 4px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                z-index: 9999;
                transform: translateY(-20px);
                opacity: 0;
                transition: all 0.3s ease;
            }
            
            .notification.show {
                transform: translateY(0);
                opacity: 1;
            }
            
            .notification.success {
                background-color: #d4edda;
                border-left: 4px solid #28a745;
                color: #155724;
            }
            
            .notification.error {
                background-color: #f8d7da;
                border-left: 4px solid #dc3545;
                color: #721c24;
            }
            
            .notification-content {
                display: flex;
                align-items: center;
            }
            
            .notification-content i {
                margin-right: 10px;
                font-size: 1.2rem;
            }
        `;
        document.head.appendChild(style);
    }
});