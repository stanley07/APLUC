// payment_functions.js

function selectPaymentOption(paymentOption) {
    var selectedPropertyId = document.querySelector('input[name="selected_property"]:checked');
    if (selectedPropertyId) {
        selectedPropertyId = selectedPropertyId.value;
        console.log("Selected Property ID:", selectedPropertyId);

        var paymentOptionInput = document.getElementById("paymentOption");
        console.log("Payment Option Input:", paymentOptionInput);

        var selectedPropertyIdInput = document.getElementById("selectedPropertyId");
        console.log("Selected Property ID Input:", selectedPropertyIdInput);

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
