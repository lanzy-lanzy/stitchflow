/**
 * Shared Pricing Logic for StitchFlow Tailoring System
 * This module provides consistent pricing calculations across all templates
 */

// Static pricing configuration matching business_logic.py
const GARMENT_PRICES = {
    'BLOUSE': 550.00,
    'PANTS': 650.00,
    'SKIRT': 500.00,
    'DRESS': 800.00,
    'JACKET': 750.00,
    'OTHERS': 600.00
};

/**
 * Pricing Manager - Core pricing functions
 */
class PricingManager {
    /**
     * Get the fixed price for a garment type
     * @param {string} garmentType - The garment type (BLOUSE, PANTS, etc.)
     * @returns {number} The price for the garment type
     */
    static getGarmentPrice(garmentType) {
        return GARMENT_PRICES[garmentType] || GARMENT_PRICES['OTHERS'];
    }

    /**
     * Calculate total order amount based on garment type and quantity
     * @param {string} garmentType - The garment type
     * @param {number} quantity - The quantity (default: 1)
     * @returns {number} The total amount
     */
    static calculateOrderTotal(garmentType, quantity = 1) {
        const basePrice = this.getGarmentPrice(garmentType);
        return basePrice * quantity;
    }

    /**
     * Calculate 50% down payment of total amount
     * @param {number} totalAmount - The total amount
     * @returns {number} The down payment amount (50% of total)
     */
    static calculateDownPayment(totalAmount) {
        return totalAmount * 0.5;
    }

    /**
     * Calculate remaining balance after down payment
     * @param {number} totalAmount - The total amount
     * @param {number} downPaymentAmount - The down payment amount
     * @returns {number} The remaining balance
     */
    static calculateRemainingBalance(totalAmount, downPaymentAmount) {
        return totalAmount - downPaymentAmount;
    }

    /**
     * Format currency amount with ₱ symbol
     * @param {number} amount - The amount to format
     * @param {number} decimals - Number of decimal places (default: 2)
     * @returns {string} Formatted currency string
     */
    static formatCurrency(amount, decimals = 2) {
        const numAmount = parseFloat(amount) || 0;
        return `₱${numAmount.toFixed(decimals)}`;
    }

    /**
     * Update pricing display elements on a page
     * @param {Object} options - Configuration options
     * @param {string} options.garmentTypeSelector - Selector for garment type element
     * @param {string} options.quantitySelector - Selector for quantity element
     * @param {string} options.garmentPriceSelector - Selector for garment price display
     * @param {string} options.totalAmountSelector - Selector for total amount display
     * @param {string} options.downPaymentSelector - Selector for down payment display
     * @param {string} options.totalAmountInputSelector - Selector for total amount input (optional)
     */
    static updatePricingDisplay(options) {
        const {
            garmentTypeSelector = '#garment_type',
            quantitySelector = '#quantity',
            garmentPriceSelector = '#garment_price_display',
            totalAmountSelector = '#total_amount_display',
            downPaymentSelector = '#down_payment_display',
            totalAmountInputSelector = '#total_amount'
        } = options;

        const garmentTypeElement = document.querySelector(garmentTypeSelector);
        const quantityElement = document.querySelector(quantitySelector);
        const garmentPriceElement = document.querySelector(garmentPriceSelector);
        const totalAmountElement = document.querySelector(totalAmountSelector);
        const downPaymentElement = document.querySelector(downPaymentSelector);
        const totalAmountInputElement = document.querySelector(totalAmountInputSelector);

        if (!garmentTypeElement) return;

        const garmentType = garmentTypeElement.value || 'OTHERS';
        const quantity = parseInt(quantityElement?.value) || 1;

        // Calculate pricing
        const garmentPrice = this.getGarmentPrice(garmentType);
        const totalAmount = this.calculateOrderTotal(garmentType, quantity);
        const downPayment = this.calculateDownPayment(totalAmount);

        // Update display elements
        if (garmentPriceElement) {
            garmentPriceElement.textContent = this.formatCurrency(garmentPrice);
        }

        if (totalAmountElement) {
            totalAmountElement.textContent = this.formatCurrency(totalAmount);
        }

        if (downPaymentElement) {
            downPaymentElement.textContent = this.formatCurrency(downPayment);
        }

        if (totalAmountInputElement) {
            totalAmountInputElement.value = totalAmount.toFixed(2);
        }
    }

    /**
     * Initialize pricing display with event listeners
     * @param {Object} options - Configuration options (same as updatePricingDisplay)
     */
    static initializePricingDisplay(options = {}) {
        const {
            garmentTypeSelector = '#garment_type',
            quantitySelector = '#quantity'
        } = options;

        // Initial update
        this.updatePricingDisplay(options);

        // Add event listeners
        const garmentTypeElement = document.querySelector(garmentTypeSelector);
        const quantityElement = document.querySelector(quantitySelector);

        if (garmentTypeElement) {
            garmentTypeElement.addEventListener('change', () => {
                this.updatePricingDisplay(options);
            });
        }

        if (quantityElement) {
            quantityElement.addEventListener('change', () => {
                this.updatePricingDisplay(options);
            });
        }
    }

    /**
     * Get pricing information for display in tables or cards
     * @param {Object} order - Order object with garment_type, quantity, total_amount
     * @returns {Object} Formatted pricing information
     */
    static getOrderPricingInfo(order) {
        const garmentType = order.garment_type || 'OTHERS';
        const quantity = order.quantity || 1;
        const totalAmount = parseFloat(order.total_amount) || this.calculateOrderTotal(garmentType, quantity);
        const downPayment = this.calculateDownPayment(totalAmount);
        const remainingBalance = this.calculateRemainingBalance(totalAmount, downPayment);

        return {
            garmentType,
            quantity,
            garmentPrice: this.getGarmentPrice(garmentType),
            totalAmount,
            downPayment,
            remainingBalance,
            formattedGarmentPrice: this.formatCurrency(this.getGarmentPrice(garmentType)),
            formattedTotalAmount: this.formatCurrency(totalAmount),
            formattedDownPayment: this.formatCurrency(downPayment),
            formattedRemainingBalance: this.formatCurrency(remainingBalance)
        };
    }

    /**
     * Validate pricing data
     * @param {string} garmentType - The garment type
     * @param {number} quantity - The quantity
     * @param {number} totalAmount - The total amount to validate
     * @returns {Object} Validation result
     */
    static validatePricing(garmentType, quantity, totalAmount) {
        const expectedTotal = this.calculateOrderTotal(garmentType, quantity);
        const isValid = Math.abs(expectedTotal - totalAmount) < 0.01; // Allow for small floating point differences

        return {
            isValid,
            expectedTotal,
            actualTotal: totalAmount,
            difference: totalAmount - expectedTotal,
            message: isValid ? 'Pricing is correct' : `Expected ${this.formatCurrency(expectedTotal)}, got ${this.formatCurrency(totalAmount)}`
        };
    }
}

// Export for use in other modules (if using ES6 modules)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { GARMENT_PRICES, PricingManager };
}

// Make available globally for template usage
window.GARMENT_PRICES = GARMENT_PRICES;
window.PricingManager = PricingManager;
