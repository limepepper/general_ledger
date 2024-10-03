// bank-statement-chart.js

function createBankStatementChart(baseUrl, containerId, bankId, startDate, endDate) {
  // Fetch data from the API
  fetch(baseUrl + `?bank_id=${bankId}&start_date=${startDate}&end_date=${endDate}`)
    .then(response => response.json())
    .then(data => {
      // Prepare the data for ApexCharts
      const chartData = {
        dates: data.map(item => item.balance_date),
        amounts: data.map(item => parseFloat(item.balance))
      };

      // Configure the chart options
      const options = {
        chart: {
          type: 'area',
          height: 350,
          zoom: {
            enabled: false
          }
        },
        // title: {
        //   text: 'Bank Statement Summary',
        //   align: 'center'
        // },
        series: [{
          name: 'Daily Total',
          data: chartData.amounts
        }],
        stroke: {
          curve: 'stepline',
        },
        dataLabels: {
          enabled: false,
        },
        xaxis: {
          type: 'datetime',
          categories: chartData.dates
        },
        yaxis: {
          title: {
            text: 'Amount'
          },
          labels: {
            formatter: function (value) {
              return value.toFixed(2);
            }
          }
        },
        // fill: {
        //   type: 'gradient',
        //   gradient: {
        //     shadeIntensity: 1,
        //     opacityFrom: 0.7,
        //     opacityTo: 0.9,
        //     stops: [0, 100],
        //     colorStops: []
        //   }
        // },
        fill: {
          colors: [function({ value, seriesIndex, w }) {
            if(value < 55) {
                return '#7E36AF'
            } else if (value >= 55 && value < 80) {
                return '#164666'
            } else {
                return '#00ff00'
            }
          }]
        },
        // colors: ['#00ff00','#2E93fA', '#66DA26', '#546E7A', '#E91E63', '#FF9800'],  // Default color (green)
        colors: [
          function({ value, seriesIndex, w }) {
            return value >= 0 ? '#0000FF' : '#FF0000'; // Blue for positive, red for negative
          },
        ],
        tooltip: {
          y: {
            formatter: function(value) {
              return value.toFixed(2);
            }
          }
        }
      };

      // // Custom function to set fill colors based on value
      // const setFillColors = (value, _, { dataPointIndex }) => {
      //   const baseColor = value < 0 ? '#ff0000' : '#00ff00';
      //   return [
      //     {
      //       offset: 0,
      //       color: baseColor,
      //       opacity: 0.8
      //     },
      //     {
      //       offset: 100,
      //       color: baseColor,
      //       opacity: 0
      //     }
      //   ];
      // };

      // options.fill.gradient.colorStops.push(setFillColors);

      // Create the chart
      const chart = new ApexCharts(document.querySelector(`#${containerId}`), options);
      chart.render();
    })
    .catch(error => console.error('Error fetching data:', error));
}

// Usage example:
// createBankStatementChart('chartContainer', '123e4567-e89b-12d3-a456-426614174000', '2024-01-01', '2024-12-31');