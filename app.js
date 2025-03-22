document.addEventListener('DOMContentLoaded', function() {
    const apiKey = '5IBYSDENE7DOH373';
    const stockSymbol = 'AAPL';
    const stockNameElement = document.getElementById('stockName');
    const stockPriceElement = document.getElementById('stockPrice');
    const lastUpdatedElement = document.getElementById('lastUpdated');
    const suggestionTextElement = document.getElementById('suggestionText');
    const chartElement = document.getElementById('stockChart');

    let stockChart;

    function fetchStockData() {
        fetch(`https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=${stockSymbol}&interval=1min&apikey=${apiKey}`)
            .then(response => response.json())
            .then(data => {
                console.log('API Response:', data);

                // Check for API error messages
                if (data['Information'] || data['Error Message']) {
                    console.error('API Error:', data['Information'] || data['Error Message']);
                    return;
                }

                // Check if the expected fields exist
                if (!data['Meta Data'] || !data['Time Series (1min)']) {
                    console.error('Invalid API Response: Missing required fields');
                    return;
                }

                const lastRefreshed = data['Meta Data']['3. Last Refreshed'];
                const timeSeries = data['Time Series (1min)'][lastRefreshed];

                if (!timeSeries) {
                    console.error('Invalid API Response: Missing data for last refreshed time');
                    return;
                }

                const price = parseFloat(timeSeries['1. open']).toFixed(2);
                const change = ((price - parseFloat(timeSeries['4. close'])) / parseFloat(timeSeries['4. close']) * 100).toFixed(2);

                // Update the stock info
                stockNameElement.textContent = stockSymbol;
                stockPriceElement.textContent = `Price: $${price} (${change}%)`;
                lastUpdatedElement.textContent = `Last updated: ${new Date(lastRefreshed).toLocaleTimeString()}`;

                // Update the chart
                updateChart(data);

                // Provide a buy/sell suggestion
                provideSuggestion(price, change);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }

    function updateChart(data) {
        const timeSeries = data['Time Series (1min)'];
        const labels = Object.keys(timeSeries).reverse();
        const prices = labels.map(time => parseFloat(timeSeries[time]['1. open']));

        const options = {
            chart: {
                type: 'line',
                height: 350,
                animations: {
                    enabled: false // Disable animations for better performance
                }
            },
            series: [{
                name: 'Stock Price',
                data: prices.map((price, index) => ({
                    x: labels[index],
                    y: price
                }))
            }],
            xaxis: {
                type: 'datetime',
                labels: {
                    format: 'HH:mm' // Format for time display
                }
            },
            yaxis: {
                title: {
                    text: 'Price (USD)'
                }
            },
            tooltip: {
                x: {
                    format: 'HH:mm' // Tooltip time format
                }
            }
        };

        if (stockChart) {
            stockChart.updateOptions(options);
        } else {
            stockChart = new ApexCharts(chartElement, options);
            stockChart.render();
        }
    }

    function provideSuggestion(price, change) {
        if (change > 0) {
            suggestionTextElement.textContent = 'Buy: The stock is trending upwards.';
        } else {
            suggestionTextElement.textContent = 'Sell: The stock is trending downwards.';
        }
    }

    // Update data every 5 minutes (300,000 milliseconds)
    setInterval(fetchStockData, 300000);

    // Fetch data immediately on page load
    fetchStockData();
});

async function getStockPrediction(stockSymbol) {
    const response = await fetch('http://127.0.0.1:5000/predict', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ stock_symbol: stockSymbol })
    });

    const data = await response.json();
    if (response.ok) {
        document.getElementById("stockName").innerText = stockSymbol.toUpperCase();
        document.getElementById("stockPrice").innerText = `Predicted Price: $${data.predicted_price}`;
    } else {
        alert("Error: " + data.error);
    }
}

// Example: Fetch prediction when the page loads
document.addEventListener("DOMContentLoaded", () => {
    getStockPrediction("AAPL"); // Default stock symbol
});