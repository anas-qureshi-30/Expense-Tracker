document.addEventListener("DOMContentLoaded", function () {
    const first_name = document.getElementById("first-name");
    const last_name = document.getElementById("last-name");
    const email = document.getElementById("email");
    const phone_no = document.getElementById("phone");
    const submitBtn = document.getElementById("submitBtn");

    const currency = document.getElementById("currency");
    const income = document.getElementById("income");
    const financial_goals = document.getElementById('financial-goals');
    const payday = document.getElementById('payday');

    const budget_alerts = document.getElementById('budget-alerts');
    const unusual_spending = document.getElementById('unusual-spending');
    const investment_insights = document.getElementById('investment-insights');

    const currency_symbol = document.querySelector('.currency-symbol')
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
    fetch('/api/settingDetails')
        .then(response => response.json())
        .then(data => {
            first_name.value = data.first_name || "";
            last_name.value = data.last_name || "";
            email.value = data.email || "";
            phone_no.value = data.phone_no || "";
            income.value = data.monthly_income || "";
            currency.value = data.currency || "";
            financial_goals.value = data.financial_goal || "";
            payday.value = data.payday || "";
            budget_alerts.checked = data.budget_alert === "True";
            unusual_spending.checked = data.unusual_spend_alert === "True";
            investment_insights.checked = data.investment_insights === "True";
            if (currencySymbols[currency.value]) {
                currency_symbol.innerHTML = currencySymbols[currency.value];
            } else {
                currency_symbol.innerHTML = "₹";
            }
        });

    submitBtn.addEventListener("click", function () {
        const data = {
            email: email.value,
            phone_no: phone_no.value,
            currency: currency.value,
            income: income.value,
            financial_goals: financial_goals.value,
            payday: payday.value,
            budget_alerts: budget_alerts.checked,
            unusual_spending: unusual_spending.checked,
            investment_insights: investment_insights.checked,
        };

        fetch('/api/settingsUpdate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
            .then(res => res.text())
            .then(alert("Updated Successfully"))
            .catch(err => console.error(err));
    });


});