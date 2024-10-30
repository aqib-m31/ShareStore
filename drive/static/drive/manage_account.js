let tapCount = 0;
let tapTimeout;

document.getElementById('username-nav').addEventListener('click', () => {
    console.log('hello', tapCount);

    tapCount++;
    clearTimeout(tapTimeout);
    tapTimeout = setTimeout(() => {
        tapCount = 0;
    }, 1000); // Reset tap count after 1 second

    if (tapCount === 7) {
        document.getElementById('deleteAccountForm').style.display = 'block';
        document.getElementById('changePasswordForm').style.display = 'none';
        tapCount = 0;
    }
});