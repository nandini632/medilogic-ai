const button = document.getElementById("analyzeBtn");
const input = document.getElementById("inputText");
const output = document.getElementById("output");

let chartInstance = null; // 🔥 prevent duplicate charts

button.addEventListener("click", async () => {
    const text = input.value;

    const res = await fetch("/analyze", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ text })
    });

    const data = await res.json();

    // 🔥 STORE DATA FOR PDF
    window.lastData = data;

    // ===== OUTPUT DISPLAY =====
    output.innerHTML = `
        <h3>🧠 Diagnosis Summary:</h3>
        <p style="font-weight:bold; color:#1E40AF;">
            ${data.summary}
        </p>

        <h3>🧾 Symptoms:</h3>
        ${data.symptoms.join(", ") || "None"}

        <h3>📊 Predictions:</h3>
        ${Object.entries(data.prediction)
            .map(([d, p]) => `${d}: ${p}`)
            .join("<br>")}

        <h3>🧠 Reasoning:</h3>
        ${data.logic.length > 0 
            ? data.logic.map(l => `<div>➡️ ${l}</div>`).join("") 
            : "No reasoning available"}

        <button onclick="downloadReport()" style="margin-top:10px;">
            📄 Download Report
        </button>

        <button onclick="loadCases()" style="margin-top:10px;">
            📊 View Case History
        </button>

        <canvas id="chart"></canvas>

        <div id="network" style="height:400px; margin-top:20px;"></div>
    `;

    // ===== BAR CHART =====
    const labels = Object.keys(data.prediction);
    const values = Object.values(data.prediction);

    const ctx = document.getElementById("chart").getContext("2d");

    // 🔥 destroy previous chart if exists
    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Disease Probability",
                data: values,
                backgroundColor: [
                    "#3B82F6",
                    "#10B981",
                    "#F59E0B",
                    "#EF4444",
                    "#8B5CF6"
                ]
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    // ===== LOGIC GRAPH =====
    const nodes = [];
    const edges = [];

    data.symptoms.forEach((symptom, i) => {
        nodes.push({
            id: "s" + i,
            label: symptom,
            color: "#3B82F6"
        });
    });

    let count = 0;

    data.logic.forEach((relation) => {
        const [symptom, disease] = relation.split(" → ");

        const symptomNode = nodes.find(
            n => n.label.toLowerCase() === symptom.toLowerCase()
        );

        if (symptomNode) {
            const diseaseId = "d" + count;

            nodes.push({
                id: diseaseId,
                label: disease,
                color: "#10B981"
            });

            edges.push({
                from: symptomNode.id,
                to: diseaseId,
                arrows: "to"
            });

            count++;
        }
    });

    const container = document.getElementById("network");

    const graphData = {
        nodes: new vis.DataSet(nodes),
        edges: new vis.DataSet(edges)
    };

    const options = {
        nodes: {
            shape: "dot",
            size: 20
        },
        edges: {
            arrows: "to"
        },
        physics: {
            enabled: true
        }
    };

    new vis.Network(container, graphData, options);
});


// ===== DOWNLOAD REPORT FUNCTION =====
function downloadReport() {
    if (!window.lastData) {
        alert("Run analysis first!");
        return;
    }

    fetch("/report", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(window.lastData)
    })
    .then(res => res.json())
    .then(() => {
        alert("✅ Report generated! Check your project folder.");
    });
}


// ===== LOAD CASE HISTORY =====
function loadCases() {
    fetch("/cases")
    .then(res => res.json())
    .then(data => {
        let html = "<h3>📊 Case History:</h3>";

        data.forEach((c, i) => {
            html += `
                <div style="margin-bottom:10px; padding:10px; border:1px solid #ccc;">
                    <b>Case ${i+1}</b><br>
                    ⏰ ${c.time}<br>
                    🧾 ${c.symptoms.join(", ")}<br>
                    🧠 ${c.summary}
                </div>
            `;
        });

        output.innerHTML = html;
    });
}