// Handle auction selection change
document.addEventListener('DOMContentLoaded', function() {
    const auctionSelect = document.getElementById('auction-id-select');
    const productSelect = document.getElementById('product-id-select');
    
    if (auctionSelect) {
        auctionSelect.addEventListener('change', function() {
            // If we're on the product page and have a product select
            if (productSelect) {
                // Submit the form to reload the page with the new auction
                this.form.submit();
            }
        });
    }
});