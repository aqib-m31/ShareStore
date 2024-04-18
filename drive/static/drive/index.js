import { removeFile } from "./removeFile.js";

const csrf = document.querySelector('[name=csrfmiddlewaretoken]').value;
const removeBtns = document.querySelectorAll('.remove-file');

removeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        removeFile(btn.dataset.id, csrf);
    });
});