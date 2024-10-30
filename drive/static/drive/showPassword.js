document.querySelectorAll('.show-password-toggle').forEach(showPwd => {    
    showPwd.addEventListener('click', (e) => {
        const pwdField = document.querySelectorAll('.pwd');
        if (e.target.checked) {
            pwdField.forEach(field => {
                field.type = "text";
            });
        } else {
            pwdField.forEach(field => {
                field.type = "password";
            });
        }
    });
});