class MMCRAGRequest {
    constructor(query) {
        this.query = query
    }
}

class MMCRAGResponse {
    constructor(images, content, error, cause, httpStatusCode) {
        this.images = images
        this.content = content
        this.error = error
        this.cause = cause
        this.httpStatusCode = httpStatusCode
    }
}