document.addEventListener("DOMContentLoaded", function () {
    const countTransactions = document.getElementById('countTransactions')
    const currencySymbol = document.getElementById("currencySymbol")
    const totalTransactions = document.getElementById("transactionValue")
    const addExpense = document.getElementById("addExpense")
    const addExpenseMain = document.getElementById("addExpenseMain")
    const currencySymbols = {
        "INR - Indian Rupee": "₹",
        "USD - US Dollar": "$",
        "EUR - Euro": "€",
        "GBP - British Pound": "£",
        "CAD - Canadian Dollar": "C$",
        "AUD - Australian Dollar": "A$",
        "JPY - Japanese Yen": "¥",
        "CNY - Chinese Yuan": "¥",
        "RUB - Russian Ruble": "₽",
        "BRL - Brazilian Real": "R$"
    };
    fetch("/api/homePage")
        .then(response => response.json())
        .then(data => {
            if (data.countTransactions) {
                countTransactions.innerHTML = data.countTransactions
            } else {
                countTransactions.innerHTML = 0
            }
            currency = data.currency
            if (currencySymbols[currency]) {
                currencySymbol.innerHTML = currencySymbols[currency];
            } else {
                currencySymbol.innerHTML = "₹";
            }
            if (data.totalTransactions) {
                totalTransactions.textContent = data.totalTransactions
            } else {
                totalTransactions.textContent = "0"
            }
        });
    addExpense.addEventListener("click", async function (event) {
        event.preventDefault();

        const response = await fetch("/api/homePageAddExpense");
        const data = await response.json();
        let anyData = data.result;
        if (anyData != null) {
            window.location.href = "/addExpense";
        } else {
            alert("Budget not found. Please create a budget first.");
        }
    });
    addExpenseMain.addEventListener("click", async function (event) {
        event.preventDefault();

        const response = await fetch("/api/homePageAddExpense");
        const data = await response.json();
        let anyData = data.result;
        if (anyData != null) {
            window.location.href = "/addExpense";
        } else {
            alert("Budget not found. Please create a budget first.");
        }
    });

});
