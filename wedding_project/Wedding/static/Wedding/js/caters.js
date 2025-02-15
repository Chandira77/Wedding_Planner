function openRequestForm(serviceId) {
    document.getElementById("serviceId").value = serviceId;
    document.getElementById("requestPricingForm").style.display = "block";
}

function closeRequestForm() {
    document.getElementById("requestPricingForm").style.display = "none";
}