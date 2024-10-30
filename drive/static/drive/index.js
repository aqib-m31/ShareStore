import { removeFile } from "./removeFile.js";

const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
const removeBtns = document.querySelectorAll('.remove-file');

if (removeBtns.length > 0 && csrfTokenElement) {
    const csrf = csrfTokenElement.value;

    removeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            removeFile(btn.dataset.id, csrf);
        });
    });
}