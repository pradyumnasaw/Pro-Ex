document.addEventListener("DOMContentLoaded", function () {
  document.getElementById("uploadForm").addEventListener("submit", function (e) {
      e.preventDefault();
      
      let fileInput = document.getElementById("csvFile");
      let file = fileInput.files[0]; // ✅ Ensure we get the file

      if (!file) {
          alert("Please select a file to upload.");
          return;
      }

      let formData = new FormData();
      formData.append("csv_file", file);
  
      let csrfToken = document.getElementById("csrf_token").value;

      fetch("/api/upload/", {
          method: "POST",
          headers: {
              "X-CSRFToken": csrfToken  // ✅ Send CSRF token
          },
          body: formData
      })
      .then(response => response.json())
      .then(data => {
          alert(data.message || data.error);
          location.reload(); // ✅ Refresh to load new company data
      })
      .catch(error => console.error("Error uploading file:", error));
  });

  window.loadCompanyData = function (companyName) {
    fetch(`/api/company/${encodeURIComponent(companyName)}/`) // ✅ Properly encode URL
        .then(response => response.json())
        .then(data => {
            console.log("API Response:", data);  // ✅ Debugging Step

            if (data.error) {
                alert(data.error); // ✅ Show error if no data
                return;
            }

            // ✅ Check if data contains valid entries
            if (!Array.isArray(data) || data.length === 0) {
                alert("No data available for this company.");
                return;
            }

            // ✅ Extract data for visualization
            let labels = data.map(item => item.Date || "");  // Ensure Date exists
            let values = data.map(item => parseFloat(item.Value) || 0);  // Ensure Value is numeric

            console.log("Chart Labels:", labels);
            console.log("Chart Values:", values);

            updateChart(labels, values);
        })
        .catch(error => console.error("Error loading data:", error));
};

function updateChart(labels, values) {
    let ctx = document.getElementById("chart").getContext("2d");

    // Destroy old chart before creating a new one
    if (window.companyChartInstance) {
        window.companyChartInstance.destroy();
    }

    // ✅ Create a new chart with data
    window.companyChartInstance = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: "Company Data",
                data: values,
                borderColor: "blue",
                borderWidth: 2,
                fill: false
              }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false
        }
      });
  }
});
