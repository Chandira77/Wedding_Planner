<script>
document.getElementById("set_price_form").addEventListener("submit", function(event) {
    event.preventDefault();
    
    let formData = new FormData(this);
    fetch("{% url 'save_pricing' %}", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => alert("Pricing Saved Successfully!"))
    .catch(error => console.error("Error:", error));
});
</script>