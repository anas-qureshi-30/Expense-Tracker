document.addEventListener('DOMContentLoaded', function () {
    let btn = document.getElementById("btn")
    let userMsg = document.getElementById("userInput")
    let chatSection = document.getElementById("chatSection")
    function printUser() {
        let printUserHtml = `
        <div class="message user-message">
            <div class="message-header user-header">
                 <i class="fas fa-user"></i>You
            </div>
            <div class="message-content">
            ${userMsg.value}
            </div>
    `
        chatSection.innerHTML += printUserHtml
    }
    function printAI(content) {
        let printAiHtml = `
        <div class="message ai-message">
            <div class="message-header ai-header">
                 <i class="fas fa-robot"></i>FinSight AI
            </div>
            <div class="message-content">
            ${content}
            </div>
    `
        chatSection.innerHTML += printAiHtml
    }
    async function chat() {
        const userInput = userMsg.value
        printUser()
        userMsg.value = ""
        const response = await fetch('/chat', {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            }, body: JSON.stringify({ "input": userInput })
        })
        const data = await response.json()
        printAI(data.replay)
    }
    btn.addEventListener('click', async function () {
        chat()
    })
    userMsg.addEventListener('keypress',function(event) {
        if(event.key=="Enter") chat()
    })
})
