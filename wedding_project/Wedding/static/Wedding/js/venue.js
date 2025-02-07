document.getElementById("apply_filter").addEventListener("click", function() {
    let venueType = document.getElementById("venueType").value;
    let city = document.getElementById("city").value;
    let guestNumbers = [...document.querySelectorAll("input[name='guest_number']:checked")].map(cb => cb.value);
    let settings = [...document.querySelectorAll("input[name='settings']:checked")].map(cb => cb.value);
    let amenities = [...document.querySelectorAll("input[name='amenities']:checked")].map(cb => cb.value);

    let params = new URLSearchParams({
        venue_type: venueType,
        city: city,
        guest_number: guestNumbers.join(','),
        settings: settings.join(','),
        amenities: amenities.join(',')
    });

    fetch(`/venues/?${params.toString()}`, {
        headers: {'X-Requested-With': 'XMLHttpRequest'}
    })
    .then(response => response.json())
    .then(data => {
        let venueResults = document.getElementById("venueResults");
        venueResults.innerHTML = "";

        data.venues.forEach(venue => {
            venueResults.innerHTML += `
                <div class="venue-item d-flex">
                    <img src="${venue.photo}" class="venue-img">
                    <div class="venue-details">
                        <h4>${venue.name}</h4>
                        <p><strong>Rating:</strong> ⭐⭐⭐⭐</p>
                        <p>${venue.about}</p>
                        <button class="btn btn-success">Request Pricing</button>
                    </div>
                </div>
            `;
        });
    });
});
