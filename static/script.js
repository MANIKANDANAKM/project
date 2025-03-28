document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("uploadForm");
    const fileInput = document.getElementById("fileInput");
    const loading = document.getElementById("loading");
    const resultDiv = document.getElementById("result");
    const container = document.querySelector(".container");

    uploadForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (!fileInput.files.length) {
            alert("Please select a file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        // Show loading
        loading.style.display = "block";
        resultDiv.classList.remove("show");
        container.classList.remove("expanded");
        resultDiv.innerHTML = "";

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();
            loading.style.display = "none"; // Hide loading after response

            if (data.error) {
                resultDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
            } else {
                // Process and format AI response
                let formattedInsights = formatInsights(data.insights);
                let diagnosisColor = data.diagnosis.includes("has Parkinson's disease") ? "red" : "green";

                resultDiv.innerHTML = `
                    <h2 class="subheading">Insights</h2>
                    <p class="diagnosis" style="color: ${diagnosisColor}; font-weight: bold;">${data.diagnosis}</p>
                    <div class="insights">${formattedInsights}</div>
                `;
                resultDiv.classList.add("show");
                container.classList.add("expanded");
            }
        } catch (error) {
            loading.style.display = "none"; // Hide loading on error
            resultDiv.innerHTML = `<p style="color: red;">Failed to fetch insights.</p>`;
        }
    });

    function formatInsights(insights) {
        return insights
            .replace(/\*\*(.*?)\*\*/g, '<h3 class="highlight">$1</h3>') // Convert **text** to a heading
            .replace(/\*(.*?)\*/g, '<strong>$1</strong>') // Convert *text* to bold
            .replace(/^\* /gm, '') // Remove bullet points at the start of lines
    }
});
