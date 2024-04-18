import { removeFile } from "./removeFile.js";
const id = document.querySelector('#manage-access').dataset.id;
const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;

// This function toggles the visibility of the form with the ID 'ma-form'.
// It adds or removes the 'd-none' class to show or hide the form, respectively.
function toggleAlterPermissions() {
    document.querySelector('#ma-form').classList.toggle('d-none');
}


// This asynchronous function sends a DELETE request to a server endpoint with a specific 'id' 
// and provided 'username'. It includes a CSRF token in the request headers for security 
// and sends JSON data containing 'permission' and 'username'. It then parses the response as JSON
// and returns the result.
async function removePermissions(username) {
    // Send a DELETE request to the server with 'id' and 'username'
    const result = await fetch(`/permissions/${id}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrf
        },
        body: JSON.stringify({
            permission: document.querySelector('#access').value,
            username: username
        })
    })
    .then(response => response.json())
    .then(result => {
        // Return the parsed JSON result
        return result;
    });

    // Return the result from the DELETE request
    return result;
}


// This function fetches information about users with whom a file is shared and updates
// the UI accordingly. It displays a list of selected users and provides the option to remove them.
function updateSharedWith() {
    // Fetch information about shared users for a specific file ('id')
    fetch(`/file/shared-with/${id}`)
        .then(response => response.json())
        .then(result => {
            if (result.error) {
                // Handle and log any errors if encountered
                console.log(`Error: ${error}`);
                return;
            }
            const users = document.querySelector('.sw');
            users.innerHTML = '';

            if (!result.usernames.length) {
                if (document.querySelector('#access').value === "Restricted") {
                    // Display a message and an option to alter permissions if no users are selected
                    users.innerHTML = `No user selected yet! <button class="btn btn-sm btn-success ms-3" onclick="toggleAlterPermissions();"><i class="fa fa-plus" aria-hidden="true"></i></button>`;
                } else {
                    // Display a message if no users are selected
                    users.innerHTML = `No user selected yet!`;
                }
            } else {
                // Display selected users and an option to remove them
                const selectedUsersTitle = document.createElement('p')
                selectedUsersTitle.classList.add('fw-bold');
                if (document.querySelector('#access').value === "Restricted") {
                    selectedUsersTitle.innerHTML = 'Selected Users <button class="btn btn-sm btn-success ms-3" onclick="toggleAlterPermissions();"><i class="fa fa-plus" aria-hidden="true"></i></button>';
                } else {
                    selectedUsersTitle.innerHTML = 'Selected Users';
                }
                users.appendChild(selectedUsersTitle);
                const ul = document.createElement('ul');
                ul.setAttribute('class', 'list-group list-group-flush');
                for (const username of result.usernames) {
                    const li = document.createElement('li');
                    li.innerHTML += `<div class="d-flex w-50 text-dark align-items-center">${username}</div><div class="d-flex justify-content-end w-50"><button type="button" class="btn btn-sm btn-outline-danger remove-access" aria-label="Remove">Remove</button></div>`;
                    li.setAttribute('class', 'list-group-item d-flex rounded-3 mb-1');
                    ul.appendChild(li);
                }
                users.appendChild(ul);

                // Add event listeners to the "Remove" buttons to remove users
                document.querySelectorAll('.remove-access').forEach(btn => {
                    btn.addEventListener('click', async (event) => {
                        const username = event.target.parentElement.previousSibling.innerText;
                        const res = await removePermissions(username);
                        if (res.message) {
                            // Remove the user from the list and update the UI
                            event.target.parentElement.parentElement.remove();
                            updateSharedWith();
                        } else {
                            console.log(res);
                        }
                    })
                })
            }
        });
}


// This function sends a PUT request to update permissions for a file ('id') on the server.
// It includes a CSRF token in the request headers for security and sends JSON data
// containing the desired 'permission' and 'username'. It handles the response and updates
// the UI based on the permission change.
function changePermissions() {
    fetch(`/permissions/${id}`, {
        method: 'PUT',
        headers: {
            'X-CSRFToken': csrf
        },
        body: JSON.stringify({
            permission: document.querySelector('#access').value,
            username: document.querySelector('#username').value
        })
    })
    .then(response => {
        return response.json()
    })
    .then(data => {
        const msg = document.querySelector('#msg');
        msg.classList.remove('d-none');
        if (data.error) {
            // Handle and display errors in a red background
            msg.classList.remove('bg-success');
            msg.classList.add('bg-danger');
            msg.textContent = data.error;
        } else if (data.message) {
            // Handle success and update UI based on the new permission
            msg.classList.remove('bg-danger');
            msg.classList.add('bg-success');

            const permission = document.querySelector('#permission');
            permission.innerHTML = data.message;

            if (data.message === 'Not Shared') {
                msg.textContent = 'Access permissions set to private!';
                permission.innerHTML += ' <i class="fa fa-lock" aria-hidden="true"></i>';
            } else if (data.message === 'Restricted') {
                msg.innerHTML = `Shared! Only selected users can access this! <button class="btn btn-sm btn-outline-light ms-2" id="add">Add users!</button>`;
                document.querySelector('#add').addEventListener('click', toggleAlterPermissions);
                permission.innerHTML += ' <i class="fa fa-users" aria-hidden="true"></i>';
            } else if (data.message === 'Everyone') {
                msg.textContent = 'Everyone can access now!'
                permission.innerHTML += ' <i class="fa fa-link" aria-hidden="true"></i>';
            }

            // Update the list of shared users and toggle the permissions panel
            updateSharedWith();
            toggleAlterPermissions();
        }
        // Clear the input field for the username
        document.querySelector('#username').value = '';
    });
}


// This function adds an event listener to to remove button
document.querySelector('#remove-file').addEventListener('click', () => {
    removeFile(id, csrf);
});


updateSharedWith();
document.querySelector('#manage-access').addEventListener('click', toggleAlterPermissions);

document.querySelector('#access').addEventListener('change', function() {
    if (this.value === 'Restricted') {
        document.forms[0].classList.remove('d-none');
    } else {
        document.forms[0].classList.add('d-none');
    }
    changePermissions();
});

document.forms[0].onsubmit = (event) => {
    changePermissions();
    event.preventDefault();
}