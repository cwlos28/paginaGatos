document.getElementById("colorMode").onclick = () => {
    const html = document.documentElement;
    html.setAttribute("data-bs-theme", html.getAttribute("data-bs-theme") === "dark" ? "light" : "dark");
  };

  document.getElementById("filtroFechas").addEventListener("submit", function (e) {
    e.preventDefault();
    const inicio = document.getElementById("fechaInicio").value;
    const fin = document.getElementById("fechaFin").value;
    renderDashboard(inicio, fin);
  });

  async function renderDashboard(inicio = '', fin = '') {
    const res = await fetch(`/dashboard/data?inicio=${inicio}&fin=${fin}`);
    const d = await res.json();

    const sum = arr => arr.reduce((a, b) => a + b, 0).toFixed(2);

    document.getElementById("ingresosTotal").textContent = "S/" + sum(d.ingresos);
    document.getElementById("gastosTotal").textContent = "S/" + sum(d.gastos);

    // ✅ Usar directamente el valor del backend
    document.getElementById("presupuestoTotal").textContent = "S/" + (d.presupuesto_total_asignado || 0).toFixed(2);

    document.getElementById("ultimoIngreso").textContent = d.ultimo_ingreso || "-";
    document.getElementById("ultimoGasto").textContent = d.ultimo_gasto || "-";
    document.getElementById("ultimoPresupuesto").textContent = d.ultimo_presupuesto || "-";

    new Chart("barChart", {
      type: "bar",
      data: {
        labels: d.labels,
        datasets: [
          { label: "Ingresos", data: d.ingresos, backgroundColor: "#0dcaf0" },
          { label: "Gastos", data: d.gastos, backgroundColor: "#198754" }
        ]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: "top" } },
        scales: { y: { beginAtZero: true } }
      }
    });

    new Chart("donutChart", {
      type: "doughnut",
      data: {
        labels: d.categorias.map(c => c.nombre),
        datasets: [{
          data: d.categorias.map(c => c.total),
          backgroundColor: ['#0d6efd', '#ffc107', '#20c997', '#dc3545', '#6f42c1']
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: "bottom" } }
      }
    });

    new Chart("budgetChart", {
      type: "bar",
      data: {
        labels: d.presupuesto_vs_gasto.map(p => p.categoria),
        datasets: [
          { label: "Presupuesto", data: d.presupuesto_vs_gasto.map(p => p.presupuesto), backgroundColor: "#0d6efd" },
          { label: "Gasto Real", data: d.presupuesto_vs_gasto.map(p => p.gasto), backgroundColor: "#dc3545" }
        ]
      },
      options: {
        responsive: true,
        plugins: { legend: { position: "top" } },
        scales: { y: { beginAtZero: true } }
      }
    });
  }

  renderDashboard();