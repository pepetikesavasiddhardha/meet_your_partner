// ==========================
// Main function: searchMatches()
// ==========================
// Collects user input from the form, sends it to backend via POST request,
// retrieves top matches from BigQuery, and starts displaying results.
async function searchMatches() {
    const userData = {
        // User details (all fields mandatory in form)
        gender: document.getElementById("gender").value,
        sexual_orientation: document.getElementById("sexual_orientation").value,
        location_type: document.getElementById("location_type").value,
        income_bracket: document.getElementById("income_bracket").value,
        education_level: document.getElementById("education_level").value,
        interest_tags: document.getElementById("interest_tags").value,

        // Partner preferences (only interests mandatory, rest optional)
        partner_gender: document.getElementById("partner_gender").value || null,
        partner_sexual_orientation: document.getElementById("partner_sexual_orientation").value || null,
        partner_location_type: document.getElementById("partner_location_type").value || null,
        partner_income_bracket: document.getElementById("partner_income_bracket").value || null,
        partner_education_level: document.getElementById("partner_education_level").value || null,
        partner_interest_tags: document.getElementById("partner_interest_tags").value
    };

    // Show loading indicator while backend request is running
    document.getElementById("loading").style.display = "block";

    try {
        // Send POST request to backend with user + partner preferences
        const response = await fetch("http://127.0.0.1:5000/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        // Hide loading once results are received
        document.getElementById("loading").style.display = "none";

        // Store matches globally so they can be accessed across functions
        window.newUserId = data.new_user_id;
        window.matches = data.matches;
        window.currentIndex = 0;

        // Start showing the first profile card
        showNextProfile();
    } catch (error) {
        console.error("Error fetching matches:", error);
        document.getElementById("loading").innerText =
            "❌ Error fetching matches. Check backend.";
    }
}

// ==========================
// Display next profile card
// ==========================
// Shows a single user profile at a time, with option to view details
// and mark as Interested / Not Interested.
function showNextProfile() {
    // If no more matches remain, show a thank-you message
    if (!window.matches || window.currentIndex >= window.matches.length) {
        document.getElementById("profile-card").innerHTML = `
            <p>✅ Thank you! No more matches to show.</p>`;
        return;
    }

    const profile = window.matches[window.currentIndex];

    // Render profile card UI with avatar, ID, and "view details" button
    document.getElementById("profile-card").innerHTML = `
        <div class="card">
            <img src="images/avatar.png" alt="User" class="profile-pic">
            <p><strong>ID:</strong> ${profile.id}</p>
            <button onclick="viewDetails(${window.currentIndex})">Click to View Details</button>
        </div>
        <div id="details"></div>
        <div class="actions">
            <button class="btn red" onclick="notInterested()">Not Interested</button>
            <button class="btn green" onclick="interested()">Interested</button>
        </div>
    `;
}

// ==========================
// View detailed profile info
// ==========================
// Expands the profile card to show all user details (traits + interests).
function viewDetails(index) {
    const profile = window.matches[index];
    document.getElementById("details").innerHTML = `
        <p><strong>Gender:</strong> ${profile.gender}</p>
        <p><strong>Orientation:</strong> ${profile.sexual_orientation}</p>
        <p><strong>Location:</strong> ${profile.location_type}</p>
        <p><strong>Income:</strong> ${profile.income_bracket}</p>
        <p><strong>Education:</strong> ${profile.education_level}</p>
        <p><strong>Interests:</strong> ${profile.interest_tags}</p>
    `;
}

// ==========================
// Match decision handlers
// ==========================
// "Interested" → notify user, then move to next profile.
// "Not Interested" → simply move to next profile.
function interested() {
    alert("💚 Thank you, your response will be shared to this user.");
    window.currentIndex++;
    showNextProfile();
}

function notInterested() {
    window.currentIndex++;
    showNextProfile();
}
