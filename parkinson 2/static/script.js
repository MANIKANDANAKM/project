document.addEventListener("DOMContentLoaded", () => {
    const uploadForm = document.getElementById("uploadForm");
    const fileInput = document.getElementById("fileInput");
    const loading = document.getElementById("loading");
    const resultDiv = document.getElementById("result");

    uploadForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (!fileInput.files.length) {
            alert("Please select a file.");
            return;
        }

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);

        loading.classList.remove("hidden");
        resultDiv.innerHTML = "";

        try {
            const response = await fetch("/upload", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();
            loading.classList.add("hidden");

            if (data.error) {
                resultDiv.innerHTML = `<p style="color: red;">Error: ${data.error}</p>`;
            } else {
                resultDiv.innerHTML = `<h2>Insights</h2><p>${data.insights}</p>`;
            }
        } catch (error) {
            loading.classList.add("hidden");
            resultDiv.innerHTML = `<p style="color: red;">Failed to fetch insights.</p>`;
        }
    });
});
