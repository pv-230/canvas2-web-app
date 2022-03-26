'use strict';

// Course module
(() => {
  // Frames
  const mainContent = document.querySelector('.main-content');
  const popupBg = document.querySelector('.popup-bg');
  const popupWindows = [...document.querySelectorAll('.popup-window')];
  const submitWindow = document.querySelector('.submit-window');
  const addAssignmentWindow = document.querySelector('.add-assignment-window');

  // Buttons
  const assignmentBtn = document.querySelector('.assignment-btn');
  const assignmentCard = document.querySelector('.add-assignment-card');
  const closeBtns = [...document.querySelectorAll('.close-btn')];

  // Forms
  const popupForm = document.forms['popup-form'];

  /**
   * Opens a popup window and blurs the background.
   */
  const openPopup = (e) => {
    mainContent.style.cssText = 'filter: blur(5px);';
    popupBg.removeAttribute('hidden');

    if (e.currentTarget === assignmentBtn) {
      submitWindow.removeAttribute('hidden');
    } else if (e.currentTarget === assignmentCard) {
      addAssignmentWindow.removeAttribute('hidden');
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
    mainContent.removeAttribute('style');
    popupBg.setAttribute('hidden', '');
  };

  // Event listeners
  closeBtns.forEach((button) => button.addEventListener('click', closePopup));

  if (assignmentCard) {
    assignmentCard.addEventListener('click', openPopup);
  }

  if (assignmentBtn.classList.contains('submit-btn')) {
    assignmentBtn.addEventListener('click', openPopup);
  }
})();
