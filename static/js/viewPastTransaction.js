let transactions = [];
let filteredTransactions = [];
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
let currency = ""
function renderTransactions() {
    const container = document.getElementById('transactionsContainer');

    if (filteredTransactions.length === 0) {
        container.innerHTML = `
                <div class="no-transactions">
                    <i class="fas fa-inbox"></i>
                    <h3>No transactions found</h3>
                    <p>Try a different search term</p>
                </div>
            `;
        return;
    }

    container.innerHTML = filteredTransactions.map(transaction => `
            <div class="transaction-item">
                <div class="transaction-info">
                    <div class="transaction-description">${transaction.description}</div>
                    <div class="transaction-date">${formatDate(transaction.date)}</div>
                </div>
                <div class="transaction-amount ${transaction.expense > 0 ? 'amount-positive' : 'amount-negative'}">
                    ${transaction.expense > 0 ? '+' : ''}${currencySymbols[currency]}${Math.abs(transaction.expense).toFixed(2)}
                </div>
            </div>
        `).join('');
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
        year: 'numeric'
    });
}

function searchTransactions() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();

    filteredTransactions = transactions.filter(transaction =>
        transaction.description.toLowerCase().includes(searchTerm)
    );

    renderTransactions();
}

document.addEventListener('DOMContentLoaded', function () {
    fetch('/api/getExpense')
        .then(response => response.json())
        .then(data => {
            transactions = data.values;
            currency = data.currency;
            filteredTransactions = [...transactions];
            renderTransactions();
        })
        .catch(error => {
            console.error("Failed to fetch transactions:", error);
        });
});
