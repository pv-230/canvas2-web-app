// Shows the message flash box when there are flashed messages
const infoBox = document.querySelector('.info-box');
const errorBox = document.querySelector('.error-box');
const flashedMessage = document.querySelector('.flashed-message');

if (flashedMessage) {
  if (flashedMessage.parentElement.className === 'info-box') {
    infoBox.toggleAttribute('hidden');
  } else {
    errorBox.toggleAttribute('hidden');
  }
}
