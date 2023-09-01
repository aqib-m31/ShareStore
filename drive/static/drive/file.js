const id = document.querySelector('#manage-access').dataset.id;
function toggleAlterPermissions() {
    document.querySelector('#ma-form').classList.toggle('d-none');
}
async function removePermissions(username) {
    const result = await fetch(`/permissions/${id}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            permission: document.querySelector('#access').value,
            username: username
        })
    })
        .then(response => response.json())
        .then(result => {
            return result;
        });

    return result;
}

function updateSharedWith() {
    fetch(`/file/shared-with/${id}`)
        .then(response => response.json())
        .then(result => {
            if (result.error) {
                console.log(`Error: ${error}`);
                return;
            }
            const users = document.querySelector('.sw');
            users.innerHTML = '';

            if (!result.usernames.length) {
                if (document.querySelector('#access').value === "Restricted") {
                    users.innerHTML = `No user selected yet! <button class="btn btn-sm btn-success ms-3" onclick="toggleAlterPermissions();"><i class="fa fa-plus" aria-hidden="true"></i></button>`;
                } else {
                    users.innerHTML = `No user selected yet!`;
                }
            } else {
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
                    li.setAttribute('class', 'list-group-item d-flex rounded-3');
                    ul.appendChild(li);
                }
                users.appendChild(ul);

                document.querySelectorAll('.remove-access').forEach(btn => {
                    btn.addEventListener('click', async (event) => {
                        const username = event.target.parentElement.previousSibling.innerText;
                        const res = await removePermissions(username);
                        if (res.message) {
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
updateSharedWith();
document.querySelector('#manage-access').addEventListener('click', toggleAlterPermissions);
document.querySelector('#access').addEventListener('change', function () {
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

function changePermissions() {
    fetch(`/permissions/${id}`, {
        method: 'PUT',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
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
                msg.classList.remove('bg-success');
                msg.classList.add('bg-danger');
                msg.textContent = data.error;
            } else if (data.message) {
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

                updateSharedWith();
                toggleAlterPermissions();
            }
            document.querySelector('#username').value = '';
        });
}

document.querySelector('#remove-file').addEventListener('click', () => {
    if (confirm("Are you sure?")) {
        fetch(`/file/${id}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        }).then(response => {
            if (response.redirected) {
                window.location = response.url;
            }
            return response.json();
        }).then(res => {
            console.log(`Error: ${res.error}`);
        });
    }
});