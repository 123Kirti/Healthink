// Backend API Configuration
const API_BASE_URL = "http://localhost:5000";
let currentUser = null;
let currentPassword = "";
let selectedRole = "patient";

// Initialize on page load
document.addEventListener("DOMContentLoaded", async () => {
    setupNavigation();
    setupLoginToggle();
    document.getElementById("login-form").addEventListener("submit", handleLogin);
    document.getElementById("patient-form").addEventListener("submit", submitPatientData);
    document.getElementById("hospital-profile-form").addEventListener("submit", updateHospitalProfile);
    document.getElementById("logout-button").addEventListener("click", logout);
    document.getElementById("logout-button-hospital").addEventListener("click", logout);
    document.getElementById("logout-button-admin").addEventListener("click", logout);
    document.getElementById("cta-login-btn").addEventListener("click", () => showLoginPage());
    await Promise.all([loadSchemes(), loadHospitals()]);
});

function setupNavigation() {
    document.getElementById("nav-home").addEventListener("click", (e) => {
        e.preventDefault();
        showLandingPage();
    });

    document.getElementById("nav-schemes").addEventListener("click", (e) => {
        e.preventDefault();
        showSchemesPage();
    });

    document.getElementById("nav-login").addEventListener("click", (e) => {
        e.preventDefault();
        showLoginPage();
    });
}

function showLandingPage() {
    document.getElementById("landing-page").classList.remove("hidden");
    document.getElementById("login-section").classList.add("hidden");
    document.getElementById("schemes-section").classList.add("hidden");
    document.getElementById("patient-dashboard").classList.add("hidden");
    document.getElementById("hospital-dashboard").classList.add("hidden");
    document.getElementById("admin-dashboard").classList.add("hidden");
    updateNavLinks("home");
}

function showLoginPage() {
    document.getElementById("landing-page").classList.add("hidden");
    document.getElementById("login-section").classList.remove("hidden");
    document.getElementById("schemes-section").classList.add("hidden");
    document.getElementById("patient-dashboard").classList.add("hidden");
    document.getElementById("hospital-dashboard").classList.add("hidden");
    document.getElementById("admin-dashboard").classList.add("hidden");
    updateNavLinks("login");
}

function showSchemesPage() {
    document.getElementById("landing-page").classList.add("hidden");
    document.getElementById("login-section").classList.add("hidden");
    document.getElementById("schemes-section").classList.remove("hidden");
    document.getElementById("patient-dashboard").classList.add("hidden");
    document.getElementById("hospital-dashboard").classList.add("hidden");
    document.getElementById("admin-dashboard").classList.add("hidden");
    updateNavLinks("schemes");
}

function updateNavLinks(active) {
    document.getElementById("nav-home").classList.remove("active");
    document.getElementById("nav-schemes").classList.remove("active");
    document.getElementById("nav-login").classList.remove("active");
    
    if (active === "home") document.getElementById("nav-home").classList.add("active");
    else if (active === "schemes") document.getElementById("nav-schemes").classList.add("active");
    else if (active === "login") document.getElementById("nav-login").classList.add("active");
}

function setupLoginToggle() {
    const buttons = document.querySelectorAll(".toggle-btn");
    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            buttons.forEach((btn) => btn.classList.remove("active"));
            button.classList.add("active");
            selectedRole = button.dataset.role;
        });
    });
}

async function handleLogin(event) {
    event.preventDefault();
    const username = document.getElementById("login-username").value.trim();
    const password = document.getElementById("login-password").value.trim();

    if (!username || !password) {
        showStatus("Please enter both username and password.", "error");
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password, role: selectedRole })
        });

        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.error || "Login failed");
        }

        currentUser = result;
        currentPassword = password;
        document.getElementById("landing-page").classList.add("hidden");
        document.getElementById("login-section").classList.add("hidden");
        document.getElementById("schemes-section").classList.add("hidden");

        showStatus(`Logged in as ${currentUser.role}`, "success");
        if (currentUser.role === "patient") {
            showPatientDashboard();
        } else if (currentUser.role === "hospital") {
            showHospitalDashboard();
        } else if (currentUser.role === "admin") {
            showAdminDashboard();
        }
    } catch (error) {
        console.error("Login error:", error);
        showStatus(error.message, "error");
    }
}

function getAuthPayload() {
    return {
        username: currentUser?.username || "",
        password: currentPassword
    };
}

function showPatientDashboard() {
    document.getElementById("landing-page").classList.add("hidden");
    document.getElementById("login-section").classList.add("hidden");
    document.getElementById("schemes-section").classList.add("hidden");
    document.getElementById("hospital-dashboard").classList.add("hidden");
    document.getElementById("admin-dashboard").classList.add("hidden");
    document.getElementById("patient-dashboard").classList.remove("hidden");
    loadPatientData();
}

function showHospitalDashboard() {
    document.getElementById("landing-page").classList.add("hidden");
    document.getElementById("login-section").classList.add("hidden");
    document.getElementById("schemes-section").classList.add("hidden");
    document.getElementById("patient-dashboard").classList.add("hidden");
    document.getElementById("admin-dashboard").classList.add("hidden");
    document.getElementById("hospital-dashboard").classList.remove("hidden");
    loadHospitalProfile();
    loadHospitalData();
}

function showAdminDashboard() {
    document.getElementById("landing-page").classList.add("hidden");
    document.getElementById("login-section").classList.add("hidden");
    document.getElementById("schemes-section").classList.add("hidden");
    document.getElementById("patient-dashboard").classList.add("hidden");
    document.getElementById("hospital-dashboard").classList.add("hidden");
    document.getElementById("admin-dashboard").classList.remove("hidden");
    loadAdminRecords();
}

function logout() {
    currentUser = null;
    currentPassword = "";
    showLandingPage();
    document.getElementById("login-form").reset();
    showStatus("Logged out successfully.", "success");
}

async function submitPatientData(event) {
    event.preventDefault();

    if (!currentUser || currentUser.role !== "patient") {
        showStatus("You must be logged in as a patient to submit data.", "error");
        return;
    }

    const details = document.getElementById("patient-details").value.trim();
    const hospitalId = document.getElementById("patient-hospital").value;
    const schemeId = document.getElementById("patient-scheme").value;
    const prescriptionFile = document.getElementById("patient-prescription").files[0];

    if (!hospitalId) {
        showStatus("Please select a hospital.", "error");
        return;
    }

    if (!details) {
        showStatus("Please provide your medical details.", "error");
        return;
    }

    const formData = new FormData();
    formData.append("username", currentUser.username);
    formData.append("password", currentPassword);
    formData.append("details", details);
    formData.append("hospital_id", hospitalId);

    if (schemeId) {
        formData.append("scheme_id", schemeId);
    }

    if (prescriptionFile) {
        formData.append("prescription_image", prescriptionFile);
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/patient-data/submit`, {
            method: "POST",
            body: formData
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Submission failed");
        }

        document.getElementById("patient-form").reset();
        showStatus(result.message, "success");
        loadPatientData();
    } catch (error) {
        console.error("Submission error:", error);
        showStatus(error.message, "error");
    }
}

async function loadPatientData() {
    if (!currentUser || currentUser.role !== "patient") return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/patient-data`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(getAuthPayload())
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Unable to load patient data");
        }

        renderPatientData(result);
    } catch (error) {
        console.error("Patient data error:", error);
        document.getElementById("patient-data-container").innerHTML = `<div class="info-box">${error.message}</div>`;
    }
}

async function loadHospitalData() {
    if (!currentUser || currentUser.role !== "hospital") return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/hospital-data`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(getAuthPayload())
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Unable to load hospital data");
        }

        renderHospitalData(result);
    } catch (error) {
        console.error("Hospital data error:", error);
        document.getElementById("hospital-data-container").innerHTML = `<div class="info-box">${error.message}</div>`;
    }
}

async function loadAdminRecords() {
    if (!currentUser || currentUser.role !== "admin") return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/admin/records`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(getAuthPayload())
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Unable to load admin records");
        }

        renderAdminRecords(result);
    } catch (error) {
        console.error("Admin records error:", error);
        document.getElementById("admin-records-container").innerHTML = `<div class="info-box">${error.message}</div>`;
    }
}

async function loadHospitals() {
    const hospitalSelect = document.getElementById("patient-hospital");
    if (!hospitalSelect) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/hospitals`);
        const hospitals = await response.json();

        if (!response.ok) {
            throw new Error(hospitals.error || "Unable to load hospitals");
        }

        hospitalSelect.innerHTML = '<option value="">Select a hospital</option>';
        hospitals.forEach((hospital) => {
            const option = document.createElement("option");
            option.value = hospital.id;
            option.textContent = `${hospital.name} — ${hospital.address}`;
            hospitalSelect.appendChild(option);
        });
    } catch (error) {
        console.error("Hospital loading error:", error);
        hospitalSelect.innerHTML = '<option value="">Unable to load hospitals</option>';
    }
}

async function loadHospitalProfile() {
    if (!currentUser || currentUser.role !== "hospital") return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/hospital-profile`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(getAuthPayload())
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Unable to load hospital profile");
        }

        document.getElementById("hospital-name").value = result.hospital_name || "";
        document.getElementById("hospital-address").value = result.address || "";
        document.getElementById("hospital-camp-details").value = result.camp_details || "";
    } catch (error) {
        console.error("Hospital profile error:", error);
        showStatus(error.message, "error");
    }
}

async function updateHospitalProfile(event) {
    event.preventDefault();

    if (!currentUser || currentUser.role !== "hospital") {
        showStatus("You must be logged in as a hospital to update the profile.", "error");
        return;
    }

    const hospitalName = document.getElementById("hospital-name").value.trim();
    const address = document.getElementById("hospital-address").value.trim();
    const campDetails = document.getElementById("hospital-camp-details").value.trim();

    if (!hospitalName || !address) {
        showStatus("Please fill in the hospital name and address.", "error");
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/hospital-profile`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                ...getAuthPayload(),
                hospital_name: hospitalName,
                address,
                camp_details: campDetails
            })
        });
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Unable to update hospital profile");
        }

        showStatus(result.message, "success");
    } catch (error) {
        console.error("Hospital profile update error:", error);
        showStatus(error.message, "error");
    }
}

function renderPatientData(entries) {
    const container = document.getElementById("patient-data-container");
    container.innerHTML = "";

    if (!entries || entries.length === 0) {
        container.innerHTML = '<div class="info-box">No submitted records yet.</div>';
        return;
    }

    entries.forEach((entry) => {
        const card = document.createElement("div");
        card.className = "data-card";
        const date = new Date(entry.timestamp * 1000).toLocaleString();
        card.innerHTML = `
            <h4>Record #${entry.id}</h4>
            <p><strong>Hospital:</strong> ${entry.hospital || "Not selected"}</p>
            <p><strong>Scheme:</strong> ${entry.scheme || "No scheme"}</p>
            <p>${entry.details}</p>
            <div class="meta">Submitted: ${date}</div>
        `;

        if (entry.image_url) {
            const image = document.createElement("img");
            image.className = "prescription-image";
            image.src = `${API_BASE_URL}${entry.image_url}`;
            image.alt = "Prescription image";
            card.appendChild(image);
        }

        container.appendChild(card);
    });
}

function renderHospitalData(entries) {
    const container = document.getElementById("hospital-data-container");
    container.innerHTML = "";

    if (!entries || entries.length === 0) {
        container.innerHTML = '<div class="info-box">No patient records available yet.</div>';
        return;
    }

    entries.forEach((entry) => {
        const card = document.createElement("div");
        card.className = "data-card";
        const date = new Date(entry.timestamp * 1000).toLocaleString();
        card.innerHTML = `
            <h4>Patient: ${entry.patient}</h4>
            <p><strong>Scheme:</strong> ${entry.scheme || "No scheme"}</p>
            <p>${entry.details}</p>
            <div class="meta">Record ID: ${entry.id} • Submitted: ${date}</div>
        `;

        if (entry.image_url) {
            const image = document.createElement("img");
            image.className = "prescription-image";
            image.src = `${API_BASE_URL}${entry.image_url}`;
            image.alt = "Prescription image";
            card.appendChild(image);
        }

        container.appendChild(card);
    });
}

function renderAdminRecords(entries) {
    const container = document.getElementById("admin-records-container");
    container.innerHTML = "";

    if (!entries || entries.length === 0) {
        container.innerHTML = '<div class="info-box">No audit records to display.</div>';
        return;
    }

    entries.forEach((entry) => {
        const card = document.createElement("div");
        card.className = "data-card";
        const date = new Date(entry.timestamp * 1000).toLocaleString();
        card.innerHTML = `
            <h4>Secure Record #${entry.id}</h4>
            <p><strong>Patient:</strong> ${entry.patient}</p>
            <p><strong>Hospital:</strong> ${entry.hospital}</p>
            <p><strong>Scheme:</strong> ${entry.scheme || "No scheme"}</p>
            <p><strong>Record hash:</strong> <span class="hash-text">${entry.record_hash}</span></p>
            <div class="meta">Submitted: ${date}</div>
        `;
        container.appendChild(card);
    });
}

async function loadSchemes() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/schemes`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const schemes = await response.json();
        renderSchemes(schemes);
        showStatus("Schemes loaded successfully", "success");
    } catch (error) {
        console.error("Error loading schemes:", error);
        showStatus("Failed to load schemes. Please try again later.", "error");
        document.getElementById("schemes-container").innerHTML = 
            `<div class="info-box">Error loading schemes: ${error.message}</div>`;
    }
}

function renderSchemes(schemesData) {
    const container = document.getElementById("schemes-container");
    container.innerHTML = "";

    const schemeSelect = document.getElementById("patient-scheme");
    if (schemeSelect) {
        schemeSelect.innerHTML = '<option value="">Optional scheme selection</option>';
    }

    if (!schemesData || schemesData.length === 0) {
        container.innerHTML = '<div class="info-box">No schemes available at this time.</div>';
        return;
    }

    schemesData.forEach((scheme) => {
        const card = document.createElement("div");
        card.className = "scheme-card";
        card.innerHTML = `
            <h4>${scheme.name}</h4>
            <p>${scheme.details}</p>
            <span class="scheme-id">Scheme ID: ${scheme.id}</span>
        `;
        container.appendChild(card);

        if (schemeSelect) {
            const option = document.createElement("option");
            option.value = scheme.id;
            option.textContent = scheme.name;
            schemeSelect.appendChild(option);
        }
    });
}

// Show status message
function showStatus(message, type) {
    const statusEl = document.getElementById("status-message");
    statusEl.textContent = message;
    statusEl.className = `status-message ${type}`;
    statusEl.style.display = "block";

    setTimeout(() => {
        statusEl.classList.remove("success", "error", "info");
        statusEl.style.display = "none";
    }, 4000);
}
