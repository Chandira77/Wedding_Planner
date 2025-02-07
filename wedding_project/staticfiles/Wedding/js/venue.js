document.addEventListener("DOMContentLoaded", function () {
    let filterButton = document.getElementById("apply_filter");

    if (filterButton) {
        filterButton.addEventListener("click", function () {
            let venueType = document.getElementById("venueType").value;
            let city = document.getElementById("city").value;
            let guestNumbers = [...document.querySelectorAll("input[name='guest_number']:checked")].map(cb => cb.value);
            let settings = [...document.querySelectorAll("input[name='settings']:checked")].map(cb => cb.value);
            let amenities = [...document.querySelectorAll("input[name='amenities']:checked")].map(cb => cb.value);
            let minPrice = document.getElementById("minPrice").value;
            let maxPrice = document.getElementById("maxPrice").value;
            let sortBy = document.getElementById("sortBy").value;

            let params = new URLSearchParams({
                venue_type: venueType,
                city: city,
                guest_number: guestNumbers.join(','),
                settings: settings.join(','),
                amenities: amenities.join(','),
                min_price: minPrice,
                max_price: maxPrice,
                sort_by: sortBy
            });

            fetch(venueUrl + `?${params.toString()}`, {
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            
            .then(response => response.json())
            .then(data => {
                let venueResults = document.getElementById("venueResults");
                venueResults.innerHTML = "";

                if (data.venues.length === 0) {
                    venueResults.innerHTML = "<p>No venues found matching your criteria.</p>";
                    return;
                }

                data.venues.forEach(venue => {
                    venueResults.innerHTML += `
                        <div class="venue-item d-flex">
                            <img src="${venue.photo}" class="venue-img">
                            <div class="venue-details">
                                <h4>${venue.name}</h4>
                                <p><strong>Rating:</strong> ${"⭐".repeat(venue.rating)}</p>
                                <p>${venue.about}</p>
                                <p><strong>Location:</strong> ${venue.location}</p>
                                <p><strong>Price:</strong> $${venue.price}</p>
                                <button class="btn btn-success request-pricing" 
                                    data-venue-id="${venue.id}" 
                                    data-venue-name="${venue.name}">
                                    Request Pricing
                                </button>
                            </div>
                        </div>
                    `;
                });

                // Attach event listeners to dynamically loaded buttons
                attachRequestPricingEventListeners();
            });
        });
    }

    function attachRequestPricingEventListeners() {
        document.querySelectorAll(".request-pricing").forEach(button => {
            button.addEventListener("click", function () {
                let venueId = this.getAttribute("data-venue-id");
                let venueName = this.getAttribute("data-venue-name");

                document.getElementById("venueId").value = venueId;
                document.getElementById("venueName").value = venueName;

                // Open modal
                let modal = new bootstrap.Modal(document.getElementById("requestPricingModal"));
                modal.show();
            });
        });
    }

    // Attach event listeners on initial load
    attachRequestPricingEventListeners();

    // Handle Form Submission for Request Pricing
    let pricingForm = document.getElementById("requestPricingForm");

    if (pricingForm) {
        pricingForm.addEventListener("submit", function (e) {
            e.preventDefault();

            let formData = new FormData(this);

            fetch("{% url 'send_request' %}", {  // Ensure 'send_request' is correctly mapped in Django URLs
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Request sent successfully!");
                    let modal = bootstrap.Modal.getInstance(document.getElementById("requestPricingModal"));
                    modal.hide();
                } else {
                    alert("Failed to send request. Please try again.");
                }
            })
            .catch(error => console.error("Error:", error));
        });
    }
});
