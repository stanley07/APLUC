// payment_functions.js

console.log("JavaScript file loaded");

function selectPaymentOption(paymentOption) {
    console.log("selectPaymentOption function called");
    var selectedPropertyId = document.querySelector('input[name="selected_property"]:checked');
    if (selectedPropertyId) {
        selectedPropertyId = selectedPropertyId.value;

        var paymentOptionInput = document.getElementById("paymentOption");
        var selectedPropertyIdInput = document.getElementById("selectedPropertyId");

        if (paymentOption === 'full') {
            // Check if property_id is valid
            if (!selectedPropertyId || isNaN(selectedPropertyId)) {
                console.error("Invalid property selected.");
                return;
            }
            // Redirect to full payment form with property_id
            window.location.href = `${window.location.origin}/full-payment/${selectedPropertyId}/`;
        } else {
            if (paymentOptionInput && selectedPropertyIdInput) {
                paymentOptionInput.value = paymentOption;
                selectedPropertyIdInput.value = selectedPropertyId;
                document.getElementById("paymentForm").submit();
            } else {
                console.error("Payment form inputs not found.");
            }
        }
    } else {
        console.error("No property selected.");
    }
}
