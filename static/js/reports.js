const incomeExpenseCanvas = document.getElementById(
    "reportIncomeExpenseChart"
);

if (incomeExpenseCanvas) {

    const labels = JSON.parse(
        incomeExpenseCanvas.dataset.income
    );

    const incomeValues = JSON.parse(
        incomeExpenseCanvas.dataset.incomeValues
    );

    const expenseValues = JSON.parse(
        incomeExpenseCanvas.dataset.expenseValues
    );

    new Chart(
        incomeExpenseCanvas,
        {
            type: "bar",

            data: {
                labels: labels,

                datasets: [
                    {
                        label: "Income",
                        data: incomeValues,
                        borderWidth: 1
                    },
                    {
                        label: "Expenses",
                        data: expenseValues,
                        borderWidth: 1
                    }
                ]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                scales: {
                    y: {
                        beginAtZero: true,

                        ticks: {
                            callback: function(value) {
                                return "₹" + value;
                            }
                        }
                    }
                }
            }
        }
    );
}


const categoryCanvas = document.getElementById(
    "reportCategoryChart"
);

if (categoryCanvas) {

    const labels = JSON.parse(
        categoryCanvas.dataset.labels
    );

    const values = JSON.parse(
        categoryCanvas.dataset.values
    );

    new Chart(
        categoryCanvas,
        {
            type: "doughnut",

            data: {
                labels: labels,

                datasets: [
                    {
                        data: values
                    }
                ]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                plugins: {
                    legend: {
                        position: "bottom"
                    }
                }
            }
        }
    );
}