document.addEventListener("DOMContentLoaded", function () {
  // Sample data for cash flow (in thousands)
  const cashFlowData = {
    "January": { incoming: 500, outgoing: 300 },
    "February": { incoming: 700, outgoing: 200 },
    "March": { incoming: 600, outgoing: 400 },
    "April": { incoming: 800, outgoing: 500 },
    "May": { incoming: 900, outgoing: 600 },
    "June": { incoming: 1000, outgoing: 700 },
    "July": { incoming: 1100, outgoing: 800 },
    "August": { incoming: 1200, outgoing: 900 },
    "September": { incoming: 1300, outgoing: 1000 },
    "October": { incoming: 1400, outgoing: 1100 },
    "November": { incoming: 1500, outgoing: 1200 },
    "December": { incoming: 1600, outgoing: 1300 }
  };

  // Function to generate chart data based on selected range
  function getChartData(range) {
    let months = Object.keys(cashFlowData);
    let incomingData = months.map(month => cashFlowData[month].incoming);
    let outgoingData = months.map(month => cashFlowData[month].outgoing);

    if (range === "3") {
      months = months.slice(-3);
      incomingData = incomingData.slice(-3);
      outgoingData = outgoingData.slice(-3);
    } else if (range === "6") {
      months = months.slice(-6);
      incomingData = incomingData.slice(-6);
      outgoingData = outgoingData.slice(-6);
    } else if (range === "12") {
      months = months.slice(-12);
      incomingData = incomingData.slice(-12);
      outgoingData = outgoingData.slice(-12);
    }

    return { months, incomingData, outgoingData };
  }

  // Initialize the chart
  const options = {
    chart: {
      type: 'bar',
      height: '100%',  // Make height responsive
      width: '100%',    // Make width responsive
      zoom: {
        enabled: false
      },
      toolbar: {
        tools: {
          download: false,
          // selection: true,
          // zoom: true,
          // zoomin: true,
          // zoomout: true,
          // pan: true,
          // reset: true,
          // customIcons: [{
          //   icon: '<i class="bi bi-gear">',
          //   index: -1,
          //   title: 'Change Time Range',
          //   class: 'custom-icon',
          //   click: function (chart, options, e) {
          //     toggleDropdown();
          //   }
          // }]
        }
      }
    },
    series: [{
      name: 'Incoming',
      data: getChartData("12").incomingData
    }, {
      name: 'Outgoing',
      data: getChartData("12").outgoingData
    }],
    xaxis: {
      categories: getChartData("12").months
    },
    yaxis: {
      labels: {
        formatter: function (value) {
          return `£${value}k`; // Add currency symbol
        }
      }
    },
    plotOptions: {
      bar: {
        dataLabels: {
          position: 'top',
        },
        columnWidth: '50%',
      }
    },
    colors: ['#288F0E', '#B31129'],  // Blue for incoming, Red for outgoing
    dataLabels: {
      enabled: true,
      formatter: function (val) {
        return `£${val}k`; // Add currency symbol to data labels
      },
      offsetY: -20,
      style: {
        fontSize: '12px',
        colors: ["#304758"]
      }
    },
    responsive: [{
      breakpoint: 1000,
      options: {
        chart: {
          width: '100%',
          height: '100%'
        },
        plotOptions: {
          bar: {
            horizontal: false
          }
        }
      }
    }]
  };

  const chart = new ApexCharts(document.querySelector("#chart"), options);
  chart.render();

  // Function to create and toggle the dropdown menu
  function toggleDropdown() {
    let dropdown = document.getElementById('timeRangeDropdown');
    if (!dropdown) {
      dropdown = document.createElement('select');
      dropdown.id = 'timeRange';
      dropdown.style.position = 'absolute';
      dropdown.style.top = '50px';
      dropdown.style.right = '50px';
      dropdown.innerHTML = `
                <option value="3">Last 3 Months</option>
                <option value="6">Last 6 Months</option>
                <option value="12" selected>Last 12 Months</option>
                <option value="all">All Time</option>
            `;
      document.body.appendChild(dropdown);
      dropdown.addEventListener('change', function () {
        updateChart(dropdown.value);
      });
    } else {
      dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
    }
  }

  // Update the chart when the time range changes
  window.updateChart = function () {
    const range = document.getElementById('timeRange').value;
    const chartData = getChartData(range);

    chart.updateOptions({
      xaxis: {
        categories: chartData.months
      },
      series: [{
        name: 'Incoming',
        data: chartData.incomingData
      }, {
        name: 'Outgoing',
        data: chartData.outgoingData
      }]
    });
  }

  // Resize chart on window resize
  window.addEventListener('resize', function () {
    chart.resize();
  });
});
