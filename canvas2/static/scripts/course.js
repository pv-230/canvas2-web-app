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
  const submitBtns = [...document.querySelectorAll('.submit-btn')];
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

    if (e.currentTarget.classList.contains('submit-btn')) {
      // Opens the assignment submission window and sets the assignment id
      // in submission form to the id of the assignment that was opened
      const assignmentCard = e.currentTarget.parentElement.parentElement;
      const assgId = assignmentCard.getAttribute('data-id');
      popupForm.elements['assg-id'].setAttribute('value', assgId);
      submitWindow.removeAttribute('hidden');
    } else if (e.currentTarget === assignmentCard) {
      // Opens the popup form to allow teachers to add assignments
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

    // Clears assignment id from the form if it exists
    if (popupForm.elements['assg-id']) {
      popupForm.elements['assg-id'].removeAttribute('value');
    }

    popupForm.reset();
    mainContent.removeAttribute('style'); // Removes blur effect
    popupBg.setAttribute('hidden', '');
  };

  // Event listeners
  closeBtns.forEach((button) => button.addEventListener('click', closePopup));

  if (assignmentCard) {
    assignmentCard.addEventListener('click', openPopup);
  }

  if (submitBtns) {
    submitBtns.forEach((submitBtn) => {
      if (submitBtn.classList.contains('assignment-btn')) {
        // Only adds the event to buttons of unsubmitted assignments
        submitBtn.addEventListener('click', openPopup);
      }
    });
  }
})();
