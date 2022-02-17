// Shows the message flash box when there are flashed messages
const errorBox = document.querySelector('.error-box');
const flashedMessage = document.querySelector('.flashed-message');
if (flashedMessage) {
  errorBox.toggleAttribute('hidden');
}

// Shows a notice when the teacher account checkbox is checked
const checkbox = document.querySelector('#teacher-check');
checkbox.addEventListener('change', (e) => {
  const teacherNotice = document.querySelector('.teacher-notice');
  if (e.target.checked) {
    teacherNotice.removeAttribute('hidden');
  } else {
    teacherNotice.setAttribute('hidden', '');
  }
});
