// ============================================================
// EXPENSE CATEGORY CHART
// ============================================================

const expenseCanvas = document.getElementById("expenseChart");

let categoryChart = null;

if (expenseCanvas) {

    const categoryLabels = JSON.parse(
        expenseCanvas.dataset.labels
    );

    const categoryValues = JSON.parse(
        expenseCanvas.dataset.values
    );

    categoryChart = new Chart(expenseCanvas, {

        type: "doughnut",

        data: {

            labels: categoryLabels,

            datasets: [
                {
                    data: categoryValues
                }
            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {
                    position: "bottom"
                },

                title: {

                    display: true,

                    text: "Expenses by Category"

                }

            }

        }

    });

}


// ============================================================
// MONTHLY EXPENSE TREND
// ============================================================

const monthlyCanvas = document.getElementById(
    "monthlyExpenseChart"
);

let monthlyChart = null;

let originalMonthlyLabels = [];
let originalMonthlyValues = [];


if (monthlyCanvas) {

    originalMonthlyLabels = JSON.parse(
        monthlyCanvas.dataset.labels
    );

    originalMonthlyValues = JSON.parse(
        monthlyCanvas.dataset.values
    );


    monthlyChart = new Chart(monthlyCanvas, {

        type: "line",

        data: {

            labels: originalMonthlyLabels,

            datasets: [

                {

                    label: "Monthly Expenses",

                    data: originalMonthlyValues,

                    tension: 0.3,

                    fill: false,

                    borderWidth: 3,

                    pointRadius: 5

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

            },

            plugins: {

                legend: {

                    display: true

                },

                title: {

                    display: true,

                    text: "Monthly Spending Trend"

                }

            }

        }

    });

}


// ============================================================
// SPENDING PERIOD FILTER
// ============================================================

const spendingPeriod = document.getElementById(
    "spendingPeriod"
);


function getCurrentDate() {

    return new Date();

}


function getMonthKey(year, month) {

    const monthNumber = String(
        month + 1
    ).padStart(2, "0");

    return `${year}-${monthNumber}`;

}


function filterMonthlyData(period) {

    if (!originalMonthlyLabels.length) {

        return {
            labels: [],
            values: []
        };

    }


    const today = getCurrentDate();

    const currentYear = today.getFullYear();

    const currentMonth = today.getMonth();


    // --------------------------------------------------------
    // THIS MONTH
    // --------------------------------------------------------

    if (period === "this-month") {

        const currentKey = getMonthKey(
            currentYear,
            currentMonth
        );

        const index = originalMonthlyLabels.indexOf(
            currentKey
        );


        if (index === -1) {

            return {
                labels: [currentKey],
                values: [0]
            };

        }


        return {

            labels: [
                originalMonthlyLabels[index]
            ],

            values: [
                originalMonthlyValues[index]
            ]

        };

    }


    // --------------------------------------------------------
    // LAST MONTH
    // --------------------------------------------------------

    if (period === "last-month") {

        let year = currentYear;

        let month = currentMonth - 1;


        if (month < 0) {

            month = 11;

            year--;

        }


        const lastMonthKey = getMonthKey(
            year,
            month
        );

        const index = originalMonthlyLabels.indexOf(
            lastMonthKey
        );


        if (index === -1) {

            return {

                labels: [lastMonthKey],

                values: [0]

            };

        }


        return {

            labels: [
                originalMonthlyLabels[index]
            ],

            values: [
                originalMonthlyValues[index]
            ]

        };

    }


    // --------------------------------------------------------
    // LAST 3 MONTHS
    // --------------------------------------------------------

    if (period === "last-3-months") {

        const labels = [];
        const values = [];


        for (let i = 2; i >= 0; i--) {

            let year = currentYear;

            let month = currentMonth - i;


            while (month < 0) {

                month += 12;

                year--;

            }


            const key = getMonthKey(
                year,
                month
            );


            const index = originalMonthlyLabels.indexOf(
                key
            );


            labels.push(key);


            if (index === -1) {

                values.push(0);

            } else {

                values.push(
                    originalMonthlyValues[index]
                );

            }

        }


        return {
            labels: labels,
            values: values
        };

    }


    // --------------------------------------------------------
    // THIS YEAR
    // --------------------------------------------------------

    if (period === "this-year") {

        const labels = [];
        const values = [];


        for (let month = 0; month < 12; month++) {

            const key = getMonthKey(
                currentYear,
                month
            );


            const index = originalMonthlyLabels.indexOf(
                key
            );


            labels.push(key);


            if (index === -1) {

                values.push(0);

            } else {

                values.push(
                    originalMonthlyValues[index]
                );

            }

        }


        return {
            labels: labels,
            values: values
        };

    }


    // --------------------------------------------------------
    // ALL TIME
    // --------------------------------------------------------

    return {

        labels: originalMonthlyLabels,

        values: originalMonthlyValues

    };

}


// ============================================================
// UPDATE CHART
// ============================================================

function updateMonthlyChart(period) {

    if (!monthlyChart) {

        return;

    }


    const filteredData = filterMonthlyData(
        period
    );


    monthlyChart.data.labels =
        filteredData.labels;


    monthlyChart.data.datasets[0].data =
        filteredData.values;


    monthlyChart.update();

}


// ============================================================
// DROPDOWN EVENT
// ============================================================

if (spendingPeriod) {

    spendingPeriod.addEventListener(
        "change",
        function() {

            updateMonthlyChart(
                this.value
            );

        }
    );


    // Load "This Month" initially

    updateMonthlyChart(
        "this-month"
    );

}

// ============================================================
// INCOME VS EXPENSES CHART
// ============================================================

const incomeExpenseCanvas = document.getElementById(
    "incomeExpenseChart"
);

if (incomeExpenseCanvas) {

    const totalIncome = parseFloat(
        incomeExpenseCanvas.dataset.income
    );

    const totalExpenses = parseFloat(
        incomeExpenseCanvas.dataset.expenses
    );


    new Chart(incomeExpenseCanvas, {

        type: "bar",

        data: {

            labels: [
                "Income",
                "Expenses"
            ],

            datasets: [

                {
                    label: "Amount",

                    data: [
                        totalIncome,
                        totalExpenses
                    ],

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

            },

            plugins: {

                legend: {

                    display: false

                },

                title: {

                    display: true,

                    text: "Income vs Expenses"

                }

            }

        }

    });

}