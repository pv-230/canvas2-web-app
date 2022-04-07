'use strict';

// Assignment management module
(() => {
  // Frames
  const mainContent = document.querySelector('.main-content');
  const popupBg = document.querySelector('.popup-bg');
  const popupWindows = [...document.querySelectorAll('.popup-window')];
  const editAssgWindow = document.querySelector('.edit-assg-window');
  const manageSubWindow = document.querySelector('.manage-sub-window');
  const submissionContents = document.querySelector('.submission-contents');
  const submissionComments = document.getElementById('comments');

  // Buttons
  const viewBtns = [...document.querySelectorAll('.view-btn')];
  const closeBtns = [...document.querySelectorAll('.close-btn')];
  const editBtn = document.querySelector('.edit-details-btn');

  // Forms
  const editAssgForm = document.forms['edit-assg-form'];
  const manageSubForm = document.forms['manage-sub-form'];

  /**
   * Requests information for the specified submission from the db.
   *
   * @param {String} sid Submission id
   */
  const loadSubContents = (sid) => {
    // Builds the POST request
    const request = new Request(`/secretary/s/${sid}/submission-info`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    fetch(request)
      .then((response) => {
        if (response.ok) {
          // Adds the submission info the submission management window
          response.json().then((contents) => {
            submissionContents.textContent = contents[0]['contents'];
            if (contents[0]['comments'].length > 0) {
              console.log(contents[0]['comments']);
            } else {
              console.log('Empty comments');
            }
          });
        }
      })
      .catch((error) => {
        console.log(error);
      });
  };

  /**
   * Opens a popup window and blurs the background.
   */
  const openPopup = (e) => {
    mainContent.style.cssText = 'filter: blur(5px);';
    popupBg.removeAttribute('hidden');

    if (e.currentTarget === editBtn) {
      // Unhides the edit assignment window
      editAssgWindow.removeAttribute('hidden');
    } else if (e.currentTarget.classList.contains('view-btn')) {
      // Loads and unhides the submission management window
      const sid = e.currentTarget.getAttribute('data-id');
      loadSubContents(sid);
      manageSubForm.setAttribute(
        'action',
        `/secretary/s/${sid}/submission-info`
      );
      manageSubWindow.removeAttribute('hidden');
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

    editAssgForm.reset();
    manageSubForm.reset();
    manageSubForm.removeAttribute('action');
    mainContent.removeAttribute('style'); // Removes blur effect
    popupBg.setAttribute('hidden', '');
  };

  // Event listeners
  closeBtns.forEach((button) => button.addEventListener('click', closePopup));

  if (viewBtns) {
    viewBtns.forEach((viewBtn) => {
      viewBtn.addEventListener('click', openPopup);
    });
  }

  if (editBtn) {
    editBtn.addEventListener('click', openPopup);
  }
})();
