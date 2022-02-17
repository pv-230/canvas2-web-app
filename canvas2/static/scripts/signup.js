// Shows the message flash box when there are flashed messages
const errorBox = document.querySelector('.error-box');
const flashedMessage = document.querySelector('.flashed-message');
if (flashedMessage) {
  errorBox.toggleAttribute('hidden');
}
