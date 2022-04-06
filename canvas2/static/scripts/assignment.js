'use strict';

// Assignment management module
(() => {
  // Frames
  const mainContent = document.querySelector('.main-content');
  const popupBg = document.querySelector('.popup-bg');
  const popupWindows = [...document.querySelectorAll('.popup-window')];
  const editAssgWindow = document.querySelector('.edit-assg-window');

  // Buttons
  const viewBtns = [...document.querySelectorAll('.view-btn')];
  const closeBtns = [...document.querySelectorAll('.close-btn')];
  const editBtn = document.querySelector('.edit-details-btn');

  // Forms
  const popupForm = document.forms['popup-form'];

  /**
   * Opens a popup window and blurs the background.
   */
  const openPopup = (e) => {
    mainContent.style.cssText = 'filter: blur(5px);';
    popupBg.removeAttribute('hidden');

    if (e.currentTarget === editBtn) {
      editAssgWindow.removeAttribute('hidden');
    }
  };

  /**
   * Closes popup window and hides any frames that were shown inside.
   */
  const closePopup = () => {
    popupWindows.forEach((window) => {
      if (!window.hasAttribute('hidden')) {
        window.setAttribute('hidden', '');
      }
    });

    popupForm.reset();
    mainContent.removeAttribute('style'); // Removes blur effect
    popupBg.setAttribute('hidden', '');
  };

  // Event listeners
  closeBtns.forEach((button) => button.addEventListener('click', closePopup));

  // if (viewBtns) {
  //   viewBtns.forEach((viewBtn) => {
  //     viewBtn.addEventListener('click', openPopup);
  //   });
  // }

  if (editBtn) {
    editBtn.addEventListener('click', openPopup);
  }
})();
