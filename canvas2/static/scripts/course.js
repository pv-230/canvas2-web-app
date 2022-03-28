'use strict';

// Course module
(() => {
  // Module state
  const roleRequests = {};

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
  const roleBtn = document.querySelector('.role-btn');
  const tableIcons = [...document.querySelectorAll('.table-icon')];

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

  /**
   * Allows teachers to add or remove the teaching assistant role for users.
   */
  const manageRoles = (e) => {
    if (e.currentTarget.classList.contains('manage')) {
      // Goes into "edit" mode
      roleBtn.textContent = 'Save';
      roleBtn.classList.remove('manage');
      roleBtn.classList.add('save');
      tableIcons.forEach((icon) => {
        icon.removeAttribute('hidden');
      });
    } else {
      roleBtn.textContent = 'Manage';
      roleBtn.classList.remove('save');
      roleBtn.classList.add('manage');

      // Builds the POST request of role requests
      const request = new Request('./change-roles', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(roleRequests),
      });

      fetch(request)
        .then((response) => {
          if (response.status === 200) {
            window.location.reload();
          }
        })
        .catch((error) => {
          console.error(error);
        });
    }
  };

  /**
   * Selects a user that was chosen by a teacher for role change.
   */
  const changeRole = (e) => {
    const rowCell = e.currentTarget.parentElement.parentElement;
    const roleCell = e.currentTarget.parentElement;
    const role = roleCell.getAttribute('data-role');
    const userId = roleCell.getAttribute('data-id');

    if (role === 'ta') {
      rowCell.style.backgroundColor = 'rgba(255, 0, 0, 0.25)';
      roleRequests[userId] = 'student';
    } else if (role === 'student') {
      rowCell.style.backgroundColor = 'rgba(43, 255, 0, 0.25)';
      roleRequests[userId] = 'ta';
    }
  };

  // Event listeners
  closeBtns.forEach((button) => button.addEventListener('click', closePopup));

  if (assignmentCard) {
    assignmentCard.addEventListener('click', openPopup);
  }

  if (assignmentBtn && assignmentBtn.classList.contains('submit-btn')) {
    assignmentBtn.addEventListener('click', openPopup);
  }

  if (roleBtn) {
    roleBtn.addEventListener('click', manageRoles);
  }

  if (tableIcons) {
    tableIcons.forEach((ti) => {
      ti.addEventListener('click', changeRole);
    });
  }
})();
