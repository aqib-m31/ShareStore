/**
 * Sends a DELETE request to the server to remove a file.
 * It asks for user confirmation and sends a DELETE request
 * to the server with a specific 'id'. It includes a CSRF token in the request headers
 * for security. If the response is a redirection, it redirects the user to the specified URL,
 * and it also logs any error message from the response.
 */
export async function removeFile(id, csrf) {
    if (confirm("Are you sure?")) {
        // Send DELETE request
        const response = await fetch(`/file/${id}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrf
            }
        });

        if (response.redirected) {
            window.location = response.url;
        }

        const res = await response.json();

        if (res.error) {
            console.log(`Error: ${res.error}`);
        }
    }
}