const errorBox = document.querySelector('.error-box');
const flashedMessages = [...document.querySelectorAll('.flashed-message')];
const checkbox = document.getElementById('teacher-check');
const teacherNotice = document.querySelector('.teacher-notice');
const submitButton = document.querySelector('button');
const password = document.getElementById('password');
const passwordConfirm = document.getElementById('password-confirm');
const form = document.getElementById('signup-form');
const errorMessage = document.querySelector('.error-message');

// Shows the message flash box when there are flashed messages
if (flashedMessages.length > 0) {
  errorBox.toggleAttribute('hidden');
}

// Shows a notice when the teacher account checkbox is checked
checkbox.addEventListener('change', (e) => {
  if (e.target.checked) {
    teacherNotice.removeAttribute('hidden');
  } else {
    teacherNotice.setAttribute('hidden', '');
  }
});

// Checks passwords for sameness before form submission
submitButton.addEventListener('click', (e) => {
  e.preventDefault();
  isValid = form.checkValidity();
  form.reportValidity();

  if (isValid) {
    if (password.value === passwordConfirm.value && password.value) {
      form.submit();
    } else {
      password.style.cssText = 'border: 1px solid rgb(255, 0, 0, .5)';
      passwordConfirm.style.cssText = 'border: 1px solid rgb(255, 0, 0, .5)';
      errorMessage.textContent = 'Passwords are not the same';

      if (errorBox.hasAttribute('hidden')) {
        errorBox.toggleAttribute('hidden');
      } else {
        for (flashedMessage of flashedMessages) {
          flashedMessage.textContent = '';
        }
      }

      if (errorMessage.hasAttribute('hidden')) {
        errorMessage.toggleAttribute('hidden');
      }
    }
  }
});
