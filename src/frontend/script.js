async function searchMatches() {
    const userData = {
        // user details (all mandatory)
        gender: document.getElementById("gender").value,
        sexual_orientation: document.getElementById("sexual_orientation").value,
        location_type: document.getElementById("location_type").value,
        income_bracket: document.getElementById("income_bracket").value,
        education_level: document.getElementById("education_level").value,
        interest_tags: document.getElementById("interest_tags").value,

        // partner preferences (only interests mandatory)
        partner_gender: document.getElementById("partner_gender").value || null,
        partner_sexual_orientation: document.getElementById("partner_sexual_orientation").value || null,
        partner_location_type: document.getElementById("partner_location_type").value || null,
        partner_income_bracket: document.getElementById("partner_income_bracket").value || null,
        partner_education_level: document.getElementById("partner_education_level").value || null,
        partner_interest_tags: document.getElementById("partner_interest_tags").value
    };

    // show loading
    document.getElementById("loading").style.display = "block";

    try {
        const response = await fetch("http://127.0.0.1:5000/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(userData)
        });

        const data = await response.json();

        // hide loading
        document.getElementById("loading").style.display = "none";

        // store results globally
        window.newUserId = data.new_user_id;
        window.matches = data.matches;
        window.currentIndex = 0;

        showNextProfile();
    } catch (error) {
        console.error("Error fetching matches:", error);
        document.getElementById("loading").innerText = "❌ Error fetching matches. Check backend.";
    }
}

function showNextProfile() {
    if (!window.matches || window.currentIndex >= window.matches.length) {
        document.getElementById("profile-card").innerHTML = `
            <p>✅ Thank you! No more matches to show.</p>`;
        return;
    }

    const profile = window.matches[window.currentIndex];

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

function interested() {
    alert("💚 Thank you, your response will be shared to this user.");
    window.currentIndex++;
    showNextProfile();
}

function notInterested() {
    window.currentIndex++;
    showNextProfile();
}
