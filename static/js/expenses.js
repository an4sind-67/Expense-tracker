const searchInput = document.getElementById("expenseSearch");

searchInput.addEventListener("input", function () {

    const searchText = this.value.toLowerCase();

    const rows = document.querySelectorAll(
        "#expenseTable tr"
    );

    rows.forEach(function (row) {

        const rowText = row.textContent.toLowerCase();

        if (rowText.includes(searchText)) {

            row.style.display = "";

        } else {

            row.style.display = "none";

        }

    });

});