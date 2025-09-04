const categoryIcons = document.querySelectorAll('.category-icon');
const categorySelect = document.getElementById('category');
const currency_symbols = document.querySelectorAll(".currency_symbol")
const setBudgetForm = document.getElementById("setBudgetForm")
let monthly_income = 0
const total_budget = document.getElementById("total-budget")
const budget_start_date = document.getElementById("budget-start-date")
const budget_end_date = document.getElementById("budget-end-date")
const budget_description = document.getElementById("budget-description")
const monthly_budget = document.getElementById("monthly_budget")
const allocatedDate = document.getElementById("allocatedDate")
const categoryForm = document.getElementById("categoryForm")
const category = document.getElementById('category')
const category_amount = document.getElementById('category-amount')
const category_notes = document.getElementById("category-notes")
const spend = document.getElementById('spend')
const remaining = document.getElementById('remaining')
const spentSummary = document.getElementById('spentSummary')
const remainingSummary = document.getElementById('remainingSummary')
const progress_labels_main = document.querySelectorAll('.progress-labels_main')
const allocatedProgress = document.getElementById('allocatedProgress')
const remainingProgress = document.getElementById('remainingProgress')
const today = new Date()
const formatted_today = today.toISOString().split('T')[0]
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
const icons = {
    "groceries": "fas fa-shopping-basket",
    "entertainment": "fas fa-film",
    "shopping": "fas fa-shopping-bag",
    "utilities": "fas fa-bolt",
    "transportation": "fas fa-plane",
    "healthcare": "fas fa-heartbeat",
    "education": "fas fa-graduation-cap",
    "travel": "fas fa-plane",
    "dining": "fas fa-utensils",
    "other": "fas fa-ellipsis-h"
};

function showLoader() {
    document.getElementById('loader').style.display = "flex";
}

function getProgressColorClass(percentage) {
    if (percentage >= 90) return 'progress-danger';
    if (percentage >= 70) return 'progress-warning';
    return 'progress-good';
}

function getProgressColorClassRemaining(percentage) {
    if (percentage >= 60) return 'progress-good';
    if (percentage >= 30) return 'progress-warning';
    return 'progress-danger';
}

async function budget() {
    const response = await fetch("/api/budget");
    const data = await response.json()

    currency = data.currency
    monthly_income = data.monthly_income
    monthly_budget.innerHTML = data.total_budget
    spend.innerHTML = data.spend
    remaining.innerHTML = data.remaining
    if (data.total_budget != null && data.spend != null && data.remaining != null) {
        allocatedPercentage = (data.spend / data.total_budget) * 100
        remainingPercentage = (data.remaining / data.total_budget) * 100
        if (isNaN(allocatedPercentage) && isNaN(remainingPercentage)) {
            spentSummary.innerHTML = `0% of total budget`
            remainingSummary.innerHTML = `0% of total budget left`
        } else {
            spentSummary.innerHTML = `${allocatedPercentage.toFixed(2)}% of total budget`
            remainingSummary.innerHTML = `${remainingPercentage.toFixed(2)}% of total budget left`
        }
        progress_labels_main.forEach(label => {
            if (currencySymbols[currency] === undefined) {
                label.innerHTML = `<span>₹0</span><span>₹${data.total_budget}</span>`
            } else {
                label.innerHTML = `<span>${currencySymbols[currency]}0</span><span>${currencySymbols[currency]}${data.total_budget}</span>`
            }
            allocatedProgress.style.width = `${allocatedPercentage}%`
            remainingProgress.style.width = `${remainingPercentage}%`
            allocatedProgress.className = `progress-fill ${getProgressColorClass(allocatedPercentage)}`
            remainingProgress.className = `progress-fill ${getProgressColorClassRemaining(remainingPercentage)}`
        });
    }

    if (currencySymbols[currency]) {
        currency_symbols.forEach(span => {
            span.innerHTML = currencySymbols[currency];
        })
    } else {
        currency_symbols.forEach(span => {
            span.innerHTML = "₹";
        })
    }

    if (data.end_date != "") {
        const startDate = new Date(data.start_date);
        const endDate = new Date(data.end_date);
        const options = { day: '2-digit', month: 'short', year: 'numeric' };
        allocatedDate.innerHTML = `<span>${startDate.toLocaleDateString('en-GB', options)} - ${endDate.toLocaleDateString('en-GB', options)}</span>`;
    }

}

async function activeCategory() {
    const response = await fetch('/api/getCateogry');
    const data = await response.json()
    const bugdetsByCategory = data.result
    const currency = data.currency
    const budget_grid = document.getElementById('budget-grid')
    if ((data.result).length == 0) {
        budget_grid.innerHTML = `<div class="no-category">
                    <i class="fas fa-inbox"></i>
                    <h3>No Categories Found</h3>
                    <p>Create a category to get started.</p>
                </div>
            `;
    }
    for (i = 0; i < bugdetsByCategory.length; i++) {
        const b = bugdetsByCategory[i]
        const percentSpent = (((Number(b.spent) / Number(b.amount_allocated)) * 100).toFixed(2))
        const card = document.createElement('div')
        card.className = 'budget-card'
        card.setAttribute("card-id", b.id)
        card.setAttribute('card-category', b.category)
        card.innerHTML = `
            <div class="budget-card-header">
                        <div class="budget-card-left">
                            <div class="budget-card-icon bg-${b.category}">
                                <i class="${icons[b.category]}"></i>
                            </div>
                            <div class="budget-card-title">${(b.category).charAt(0).toUpperCase() + (b.category).slice(1)}</div>
                        </div>
                        <div class="budget-card-actions">
                            <i class="fas fa-edit editBtn"></i>
                            <i class="fas fa-trash deleteBtn"></i>
                        </div>
                    </div>
                    <div class="budget-card-amount">${currencySymbols[currency]}${b.amount_allocated}</div>
                    <div class="budget-card-subtitle">
                        <span class="status-good">${currencySymbols[currency]}${b.remaining} remaining</span> • Spent ${currencySymbols[currency]}${b.spent}
                    </div>
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div class="progress-fill ${getProgressColorClass(percentSpent)}" style="width: ${percentSpent}%;"></div>
                        </div>
                        <div class="progress-labels">
                            <span>${percentSpent}% spent</span>
                            <span>${(100 - percentSpent).toFixed(2)}% left</span>
                        </div>
                    </div>
            `;
        budget_grid.appendChild(card)
    }
}

function setUpListners() {
    budget_start_date.setAttribute("min", formatted_today)
    budget_end_date.setAttribute("min", formatted_today)
    categoryIcons.forEach(icon => {
        icon.addEventListener('click', function () {
            // Remove active class from all icons
            categoryIcons.forEach(i => i.classList.remove('active'));

            // Add active class to clicked icon
            this.classList.add('active');

            // Update hidden select value
            const category = this.getAttribute('data-category');
            categorySelect.value = category;
        });
    });
    setBudgetForm.addEventListener("submit", async function (event) {
        let isValid = true
        if (Number(total_budget.value) > Number(monthly_income)) {
            alert("Budget Cannot be more than Monthly Income")
            isValid = false
        }
        if (budget_end_date.value < budget_start_date.value) {
            alert("End Date Cannot be less than start date")
            isValid = false
        }
        if (budget_start_date.value == budget_end_date.value) {
            alert("Both End Date and start date cannot be same")
            isValid = false
        }
        if (isValid) {
            let input = {
                "total_budget": total_budget.value,
                "budget_start_date": budget_start_date.value,
                "budget_end_date": budget_end_date.value,
                "budget_description": budget_description.value
            }
            const response = await fetch("/api/setBudget", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(input),
                credentials: "include"
            });
            const data = await response.json()
            if (data.result === "Failed") {
                alert("There is already one running budget, so cannot create new!!")
            }
            if (data.result === "success") {
                alert("Created successfully")
            }
        }
    });
    categoryForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        data = {
            "category": category.value,
            "amount_allocated": category_amount.value,
            "category_notes": category_notes.value
        }
        const response = await fetch('/api/setCategory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        try {
            const data = await response.json();
            if (data.error=="noBudget"){
                alert("You need to create a budget before you can add categories.")
                window.open("/budget#set-budget","_self")
            }
            if (data.result == "Failed") {
                alert("Duplicate category: This category is already included in the current budget.")
            }
            if (data.error == "highamount") {
                alert("You don't have enough remaining budget to allocate this amount.")
            }
            if (data.success == "success") {
                alert("New category added successfully.")
                window.location.href = data.redirectURL
            }
        }
        catch (error) {
            alert("Something went wrong", error)
        }

    });
}

function hideLoader() {
    document.getElementById('loader').style.display = 'none';
}

function openEditWindow(url) {
    window.open(
        url,
        '_self'
    )
}

document.addEventListener('DOMContentLoaded', async function () {
    showLoader();
    try {
        await budget();
        await activeCategory();
        setUpListners();
    } catch (error) {
        console.log(error)
    }
    finally {
        hideLoader();
    }
    document.addEventListener('click', async function (e) {
        const editBtn = e.target.closest('.editBtn')
        const deleteBtn = e.target.closest('.deleteBtn')
        if (editBtn) {
            const card = e.target.closest('.budget-card')
            const category = card.getAttribute('card-category')
            const response = await fetch('/api/getEditPageData', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ "category": category })
            });
            const data = await response.json()
            const editWindowData = {
                "category": category,
                "currencySymbol": currencySymbols[currency],
                "icon": icons[category],
                'amount': data.amount_allocated
            }
            sessionStorage.setItem("editWindowData", JSON.stringify(editWindowData))
            openEditWindow('/editPage')
        } else if (deleteBtn) {
            if (confirm("Are you sure to delete the category?")) {
                const card = e.target.closest('.budget-card')
                const category_id = card.getAttribute("card-id")
                const response = await fetch("/api/deleteCategory", {
                    method: "POST",
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ "category_id": category_id })
                });
                const data = await response.json()
                if (data.result == "success") {
                    alert("Successfully deleted category")
                    openEditWindow('/budget')
                }
            } else {
                return
            }
        }
    });
});
