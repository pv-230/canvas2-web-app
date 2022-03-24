'use strict';

(() => {
  const mainContent = document.querySelector('.main-content');
  const popupBg = document.querySelector('.popup-bg');
  const assignmentBtn = document.querySelector('.assignment-btn');
  const closeBtnFrame = document.querySelector('.close-btn');
  const uploadFrame = document.querySelector('.upload-frame');
  const uploadForm = document.forms['upload-form'];
  const submitFormBtn = document.querySelector('.submit-form-btn');

  // Displays the upload assignment form and blurs the background
  const openUploadPopup = () => {
    mainContent.style.cssText = 'filter: blur(5px);';
    popupBg.removeAttribute('hidden');
    uploadFrame.removeAttribute('hidden');
  };

  // Closes popup window and hides any frames that were shown inside
  const closePopup = () => {
    if (!uploadFrame.hasAttribute('hidden')) {
      uploadForm.reset();
      uploadFrame.setAttribute('hidden', '');
    }

    mainContent.removeAttribute('style');
    popupBg.setAttribute('hidden', '');
  };

  // Event listeners
  closeBtnFrame.addEventListener('click', closePopup);
  if (assignmentBtn.classList.contains('upload-btn')) {
    assignmentBtn.addEventListener('click', openUploadPopup);
  }
})();
