// Shows the message flash box when there are flashed messages
const messageFlashBox = document.querySelector('.message-flash-box');
const flashedMessage = document.querySelector('.flashed-message');
if (flashedMessage) {
  messageFlashBox.toggleAttribute('hidden');
}
