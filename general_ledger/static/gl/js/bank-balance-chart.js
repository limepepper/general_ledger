// Function to determine fill color based on balance change
function determineFillColor(startBalance, endBalance) {
    var changePercentage = ((endBalance - startBalance) / startBalance) * 100;
    if (changePercentage > 10) {
        return '#0000FF'; // Green
    } else if (changePercentage < -10) {
        return '#FF0000'; // Red
    } else {
        return '#FFFF99'; // Pale Yellow
    }
}

function calculateTrend(startBalance, endBalance, constant = 100) {
    normalized_change = (endBalance - startBalance) / (Math.abs(startBalance) + constant)
    if (normalized_change > 0.05) {
        return '#0000FF'; // Red
    } else if (normalized_change < -0.05) {

        return '#FF0000'; // Red
    } else {
        return '#FFFF99'; // Pale Yellow
    }
}

// Configuration for the chart
var chartConfig = {
    colors: {
        increase: '#0000FF', // Blue if increased
        decrease: '#FF0000'  // Red if decreased
    },
    theme: {
        fill: {
            type: 'gradient',
            gradient: {
                shadeIntensity: 1,
                opacityFrom: 0.7,
                opacityTo: 0.9,
                stops: [0, 90, 100]
            }
        }
    }
};

// generate line chart for bank balance
function renderBankBalanceChart(baseUrl, containerId, bankId, startDate, endDate,) {

    var options = {
        chart: {
            type: 'area',
            height: 350,
            zoom: {
                enabled: false
            }
        },
        series: [{
            name: 'Bank Balance',
            data: []
        }],
        noData: {
          text: 'No data available. Please import your bank data to see your balance over time.',
          align: 'center',
          verticalAlign: 'middle',
          offsetX: 0,
          offsetY: 0,
          style: {
            color: '#000000',
            fontSize: '14px',
            fontFamily: 'Helvetica, Arial, sans-serif',
          }
        },
        stroke: {
            curve: 'stepline',
        },
        dataLabels: {
            enabled: false,
        },
        xaxis: {
            type: 'datetime',
            title: {
                text: 'Date'
            }
        },
        yaxis: {
            title: {
                text: 'Balance ($)'
            }
        },
        title: {
            text: 'Bank Balance Over Time',
            align: 'center'
        },
        fill: chartConfig.theme.fill
    };

    var chart = new ApexCharts(document.querySelector(containerId), options);
    chart.render();

    fetch(`${baseUrl}?bank_id=${bankId}&start_date=${startDate}&end_date=${endDate}`)
        .then(response => response.json())
        .then(data => {
            var seriesData = data.map(item => ({
                x: new Date(item.balance_date).getTime(),
                y: item.balance
            }));

            // Determine the color based on the balance change
            var startBalance = seriesData[0].y;
            var endBalance = seriesData[seriesData.length - 1].y;
            var fillColor = calculateTrend(startBalance, endBalance);

            chart.updateOptions({
                fill: {
                    type: chartConfig.theme.fill.type,
                    colors: [fillColor],
                    gradient: chartConfig.theme.fill.gradient
                }
            });

            chart.updateSeries([{
                name: 'Bank Balance',
                data: seriesData
            }]);
        })
        .catch(error => console.error('Error fetching bank balance data:', error));

}