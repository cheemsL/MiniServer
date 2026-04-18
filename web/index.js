console.log(`welcome to mini server.`)


const host_ip = "192.168.0.102"
const port = 9000


const messageContainer = document.querySelector("#message-container")
const getButton = document.querySelector('#get-button')
const postButton = document.querySelector('#post-button')
const websocketButton = document.querySelector('#websocket-button')


const websocket = new WebSocket(`ws://${host_ip}:${port}/test`)
websocket.onmessage = (event) => {
    const message = event.data
    appendMessage(message)
}


function getCurrentTime() {
    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    const seconds = String(now.getSeconds()).padStart(2, '0');
    return `${hours}:${minutes}:${seconds}`;
}


/**
 * @param {string} message
 */
function appendMessage(message) {
    const messageElement = document.createElement("div")
    const currentTime = getCurrentTime()
    messageElement.classList.add("message")
    messageElement.innerHTML = `<span style="color: #77777777">${currentTime}</span><span>${message}</span>`
    messageContainer.appendChild(messageElement)
}


getButton.addEventListener('click', async (event) => {
    console.log('get button clicked')
    const response = await fetch(
        `http://${host_ip}:${port}/test`,
        {
            method: 'GET',
        }
    )
    const data = await response.text()
    appendMessage(data)

})


postButton.addEventListener('click', async (event) => {
    console.log('post button clicked')
    const response = await fetch(
        `http://${host_ip}:${port}/test`,
        {
            method: 'POST',
        }
    )
    const data = await response.text()
    appendMessage(data)
})


websocketButton.addEventListener('click', async (event) => {
    console.log('websocket button clicked')
    websocket.send(JSON.stringify({}))
})



