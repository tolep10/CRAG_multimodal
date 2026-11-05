let container = document.getElementById("container")
let userInput = document.getElementById("user-input")
let sendInput = document.getElementById("send-input")
let divSpinner = null
let spinnerLoader = null
let question = null
let response = null
const basePath = "../"
const apiEndPoint = "http://localhost:8001/api/mmcrag_d_t/"
const testEndPoint = "test"

function loadValues() {
    divSpinner = document.createElement("div")
    spinnerLoader = document.createElement("img")
    spinnerLoader.setAttribute("src", "img/spinner-icon-0.gif")
    spinnerLoader.style.width = "30px"
    spinnerLoader.style.height = "30px"
    divSpinner.appendChild(spinnerLoader)

    question = new MMCRAGRequest(null)
    response = new MMCRAGResponse(null, null, false, null, 200)
}

sendInput.addEventListener("click", (e) => {
    e.target.disabled = true
    getUserInput(e)
})

async function getUserInput(e) {
    let query = userInput.value
    query.trim()

    if (query.length >= 10) {
        question.query = query
        container.appendChild(divSpinner)
        const result = await sendRequest(query)
        userInput.value = ""
        
        if (result) {
            processResponse(query)
        }
    } else{
        alert("Ingresa tu consulta, mínimo debe tener 10 caracteres")
    }

    window.scrollTo(0, document.body.scrollHeight)
    e.target.disabled = false
}

async function sendRequest(queryInput) {
    try {
        const apiResponse = await fetch(`${apiEndPoint}`,{ 
            method: "POST", 
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: queryInput }) 
        })

        const contentType = apiResponse.headers.get('content-type');

        if (apiResponse.ok) {//tod ok
            const data = await apiResponse.json()
            
            if (!data.error) {
                response.images = data.images
                response.content = data.content
                response.error = data.error
                response.cause = data.cause
                response.httpStatusCode = data.http_status_code

                return true
            } else {//errores 400 + que manejo en el back end
                processError(`Error: ${data.cause}`)
                return false
            }
        } else { // errores de pydantic, que no controlo
            if (contentType && contentType.includes('application/json')) {
                const error_json = await apiResponse.json()
                let final_msg = "ERRORES:\n"

                if (error_json.detail) {
                    error_json.detail.forEach(element => {
                        if (element.msg) {
                            final_msg += `${element.msg}\n`
                        }
                    })
                    processError(final_msg)
                } else {
                    processError(`Ha ocurrido un error desconocido: ${JSON.stringify(error_json)}`);
                    
                }
                
            } else {
                const textoError = await apiResponse.text(); // Lee el HTML/texto sin romper la app
                processError('El servidor no devolvió JSON:', textoError);
            }

            return false
        }

    } catch(error) {// solo errores de conexion con el back edn
        alert(`Ocurrió un error en el request: ${error}`)

        return false
    }
}

function processResponse(queryInput) {
    let subContainer = document.createElement("div")
    subContainer.classList.add("sub-container")

    let divPq = document.createElement("div")
    divPq.classList.add("div-pq-pc")
    let divPc = document.createElement("div")
    divPc.classList.add("div-pq-pc")

    let pquery = document.createElement("p")
    pquery.classList.add("p-query")
    pquery.innerText = queryInput
    divPq.appendChild(pquery)
    subContainer.appendChild(divPq)
    

    let pContent = document.createElement("div")
    pContent.classList.add("content-response")
    cleanText = cleanContent(response.content)
    pContent.innerHTML = marked.parse(cleanText)
    divPc.appendChild(pContent)
    

    if (response.images.length > 0) {
        let divImg = document.createElement("div")
        response.images.forEach(element => {
            let image = document.createElement("img")
            image.setAttribute("src", `${basePath}${element}`)
            divImg.appendChild(image)
        });
        subContainer.appendChild(divImg)
    }

    subContainer.appendChild(divPc)
    container.removeChild(divSpinner)
    container.appendChild(subContainer)
}

function processError(error_msg) {
    let subContainer = document.createElement("div")
    subContainer.classList.add("sub-container")

    let divPError = document.createElement("div")
    divPError.classList.add("div-pq-pc")

    let pError = document.createElement("p")
    pError.classList.add("p-query")
    pError.innerText = error_msg
    divPError.appendChild(pError)
    subContainer.appendChild(divPError)
    container.removeChild(divSpinner)
    container.appendChild(subContainer)
}

function cleanContent(responseContent) {
    return responseContent.split('\n').map(linea => linea.trim()).join('\n');

}

document.addEventListener("DOMContentLoaded", (e) => {
    loadValues()
})
