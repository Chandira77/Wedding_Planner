document.addEventListener("DOMContentLoaded", function () {
    let filterButton = document.getElementById("apply_filter");
    let resetButton = document.getElementById("reset_filter");
    let venueResults = document.getElementById("venueResults");
    let loadingIndicator = document.getElementById("loading");

    function fetchVenues() {
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

        loadingIndicator.style.display = "block"; // Show loading spinner

        fetch(venueUrl + `?${params.toString()}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(response => response.json())
            .then(data => {
                venueResults.innerHTML = "";
                loadingIndicator.style.display = "none"; // Hide loader

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

                attachRequestPricingEventListeners();
            })
            .catch(error => {
                console.error("Error:", error);
                loadingIndicator.style.display = "none";
                venueResults.innerHTML = "<p>Something went wrong! Please try again.</p>";
            });
    }

    if (filterButton) {
        filterButton.addEventListener("click", fetchVenues);
    }

    if (resetButton) {
        resetButton.addEventListener("click", function () {
            document.getElementById("venueType").value = "";
            document.getElementById("city").value = "";
            document.querySelectorAll("input[type='checkbox']").forEach(cb => cb.checked = false);
            document.getElementById("minPrice").value = "";
            document.getElementById("maxPrice").value = "";
            document.getElementById("sortBy").value = "";
            fetchVenues();
        });
    }

    function attachRequestPricingEventListeners() {
        document.querySelectorAll(".request-pricing").forEach(button => {
            button.addEventListener("click", function () {
                let venueId = this.getAttribute("data-venue-id");
                let venueName = this.getAttribute("data-venue-name");

                document.getElementById("venueId").value = venueId;
                document.getElementById("venueName").value = venueName;

                let modal = new bootstrap.Modal(document.getElementById("requestPricingModal"));
                modal.show();
            });
        });
    }

    fetchVenues(); // Load venues on page load
});
