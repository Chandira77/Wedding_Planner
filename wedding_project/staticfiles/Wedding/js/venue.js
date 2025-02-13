const venueUrl = "/api/venues"; // Define the venueUrl before using it

document.addEventListener("DOMContentLoaded", function () {
    let filterButton = document.getElementById("apply_filter");
    let resetButton = document.getElementById("reset_filter");
    let venueResults = document.getElementById("venueResults");
    let loading = document.getElementById("loading");

    // Step 1: Debugging - Check if elements exist
    if (!filterButton) console.error("❌ ERROR: filterButton (apply_filter) not found!");
    if (!resetButton) console.error("❌ ERROR: resetButton (reset_filter) not found!");
    if (!venueResults) console.error("❌ ERROR: venueResults not found!");
    if (!loading) console.error("❌ ERROR: loading not found!");

    function fetchVenues() {
        let venueType = document.getElementById("venueType")?.value || "";
        let city = document.getElementById("city")?.value || "";
        let guestNumbers = [...document.querySelectorAll("input[name='guest_number']:checked")].map(cb => cb.value);
        let settings = [...document.querySelectorAll("input[name='settings']:checked")].map(cb => cb.value);
        let amenities = [...document.querySelectorAll("input[name='amenities']:checked")].map(cb => cb.value);
        let minPrice = document.getElementById("minPrice")?.value || "";
        let maxPrice = document.getElementById("maxPrice")?.value || "";
        let sortBy = document.getElementById("sortBy")?.value || "";

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

        console.log("🚀 Fetching venues with URL:", venueUrl + `?${params.toString()}`); // Step 3 Debugging

        loading.style.display = "block"; // Show loading spinner

        fetch(venueUrl + `?${params.toString()}`, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
            .then(response => response.json())
            .then(data => {
                console.log("📡 Response received:", data); // Step 3 Debugging
                venueResults.innerHTML = "";
                loading.style.display = "none"; // Hide loader

                if (!data.venues || data.venues.length === 0) {
                    console.warn("⚠️ No venues found matching criteria.");
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
                console.error("❌ Fetch error:", error); // Step 4 Debugging
                loading.style.display = "none";
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
