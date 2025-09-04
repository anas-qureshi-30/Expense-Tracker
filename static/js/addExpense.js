document.addEventListener('DOMContentLoaded', function () {
    const today = new Date();
    const year = today.getFullYear();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    const expenseDate = document.getElementById('expenseDate')
    expenseDate.value = `${year}-${month}-${day}`;

    const hours = String(today.getHours()).padStart(2, '0');
    const minutes = String(today.getMinutes()).padStart(2, '0');
    const expenseTime = document.getElementById('expenseTime')
    expenseTime.value = `${hours}:${minutes}`;

    const categoryIcons = document.querySelectorAll('.category-icon');
    const categorySelect = document.getElementById('category');
    categoryIcons.forEach(icon => {
        icon.addEventListener('click', function () {
            categoryIcons.forEach(icon => {
                icon.classList.remove('active');
            });

            this.classList.add('active');

            const categoryName = this.querySelector('.icon-name').textContent.toLowerCase();
            categorySelect.value = categoryName;
        });
    });

    const form = document.querySelector('.formGrp');
    form.addEventListener('submit', async function (event) {
        const expenseInput = document.getElementById('expense');
        const descriptionInput = document.getElementById('description');
        const dateInput = document.getElementById('expenseDate');

        if (!expenseInput.value || expenseInput.value <= 0) {
            event.preventDefault();
            alert('Please enter a valid expense amount');
            return;
        }

        if (!descriptionInput.value.trim()) {
            event.preventDefault();
            alert('Please enter a description');
            return;
        }

        if (!dateInput.value) {
            event.preventDefault();
            alert('Please select a date');
            return;
        }
        let value = {
            "expense": expenseInput.value,
            "description": descriptionInput.value,
            "category": categorySelect.value,
            "date": expenseDate.value,
            "time": expenseTime.value
        }
        try {
            const response = await fetch('/api/addExpense', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(value)
            });
            if (!response.ok) {
                const errorText = await response.text(); // fallback if response is not JSON
                throw new Error("Server returned non-OK status: " + response.status + " - " + errorText);
            }
            const data = await response.json()
            if (data.result === "Failed") {
                alert("This expense category doesn't exist in your current budget.");
            }
            if (data.result === "highExpense") {
                alert("The expense amount is greater than the available balance in the selected category.");
            }
            if (data.result === "success") {
                alert("Added expense to your budget");
                window.location.href = data.redirectURL
            }
            if (data.error === "dateTimeError") {
                alert("Please select a date within the active budget period")
            }
        }
        catch (error) {
            console.error("Caught Error:", error);
            alert("Something Went Wrong");
        }
    });
});
