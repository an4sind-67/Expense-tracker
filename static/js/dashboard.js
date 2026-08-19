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

    return {

        labels: originalMonthlyLabels,

        values: originalMonthlyValues

    };

}

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

if (spendingPeriod) {

    spendingPeriod.addEventListener(
        "change",
        function() {

            updateMonthlyChart(
                this.value
            );

        }
    );

    updateMonthlyChart(
        "this-month"
    );

}


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


const progressBar = document.querySelector(
    ".budget-progress-bar"
);

if (progressBar) {

    const progress = parseFloat(
        progressBar.dataset.progress
    );

    progressBar.style.width =
        Math.min(Math.max(progress, 0), 100) + "%";

}