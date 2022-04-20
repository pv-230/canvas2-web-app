'use strict';

// Assignment management module
(() => {
  // State
  let newGrades = {};

  // Frames
  const mainContent = document.querySelector('.main-content');
  const popupBg = document.querySelector('.popup-bg');
  const popupWindows = [...document.querySelectorAll('.popup-window')];
  const editAssgWindow = document.querySelector('.edit-assg-window');
  const manageSubWindow = document.querySelector('.manage-sub-window');
  const submissionContents = document.querySelector('.submission-contents');
  const commentGroup = document.querySelector('.comment-group');
  const windowGrade = document.getElementById('window-grade');
  const gradeCells = [...document.querySelectorAll('.grade-cell')];
  const simScore = document.querySelector('.simscore');
  const confModal = document.querySelector('.confirmation-modal', HTMLElement);
  const subIdInput = document.querySelector('.sub-id-input');

  // Buttons
  const viewBtns = [...document.querySelectorAll('.view-btn')];
  const closeBtnEditAssg = document.querySelector('.close-btn-edit-assg');
  const closeBtnManageSub = document.querySelector('.close-btn-manage-sub');
  const editBtn = document.querySelector('.edit-details-btn');
  const revertBtn = document.querySelector('.revert-btn');
  const saveBtn = document.querySelector('.save-btn');
  const delAssgBtn = document.querySelector('.del-assg-btn');
  const delSubBtn = [...document.querySelectorAll('.del-sub-btn')];
  const cancelBtn = document.querySelector('.cancel-btn');
  const reportBtn = document.querySelector('.report-btn');

  // Forms
  const editAssgForm = document.forms['edit-assg-form'];
  const manageSubForm = document.forms['manage-sub-form'];
  const delBtnForm = document.forms['del-btn-form'];

  /**
   * Requests information for the specified submission from the db.
   *
   * @param {String} sid Submission id
   */
  const loadSubContents = (sid) => {
    submissionContents.textContent = 'Loading contents...';
    commentGroup.textContent = 'Loading comments...';
    windowGrade.value = '*';
    simScore.textContent = 'Loading...';

    reportBtn.setAttribute('data-id', sid);

    // Builds the GET request
    const request = new Request(`/secretary/s/${sid}/submission-info`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    fetch(request)
      .then((response) => {
        if (response.ok) {
          response.json().then((data) => {
            // Adds submission contents to the window
            submissionContents.textContent = data['contents'];

            // Remove the "Loading comments" string
            commentGroup.removeChild(commentGroup.firstChild);

            if (data['comments'].length > 0) {
              // Adds any comments to the comment block
              data['comments'].forEach((comment) => {
                const commentPara = document.createElement('p');
                const username = comment['username'];
                const timestamp = new Date(
                  comment['timestamp']
                ).toLocaleString();
                const contents = comment['contents'];
                commentPara.textContent = `${username} (${timestamp}): ${contents}`;
                commentGroup.appendChild(commentPara);
              });
            } else {
              // No comments found
              const commentPara = document.createElement('p');
              commentPara.textContent = 'No comments.';
              commentGroup.appendChild(commentPara);
            }

            windowGrade.value = data['grade'];
            simScore.textContent = data['simscore'];
          });
        }
      })
      .catch((error) => {
        console.log(error);
      });
  };

  /**
   * Opens a popup window and blurs the background.
   *
   * @param {Event} e
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
   * Closes the popup window for editing assignment details.
   */
  const closePopupEditAssg = () => {
    popupWindows.forEach((window) => {
      if (!window.hasAttribute('hidden')) {
        window.setAttribute('hidden', '');
      }
    });

    editAssgForm.reset();
    mainContent.removeAttribute('style'); // Removes blur effect
    popupBg.setAttribute('hidden', '');
  };

  /**
   * Closes the popup window for managing submissions.
   */
  const closePopupManageSub = () => {
    popupWindows.forEach((window) => {
      if (!window.hasAttribute('hidden')) {
        window.setAttribute('hidden', '');
      }
    });

    manageSubForm.reset();
    manageSubForm.removeAttribute('action');

    // Clears the comment section
    while (commentGroup.childElementCount > 0) {
      commentGroup.removeChild(commentGroup.firstElementChild);
    }

    mainContent.removeAttribute('style'); // Removes blur effect
    popupBg.setAttribute('hidden', '');
  };

  /**
   * Allows the user to edit grades directly from the table.
   *
   * @param {Event} e
   */
  const editGrades = (e) => {
    // These values go into the updated grades object
    const subId = e.currentTarget.getAttribute('data-id');
    const newGrade = Number.parseFloat(e.currentTarget.value);

    if (newGrade && newGrade >= 0 && newGrade <= 100) {
      // newGrade was a valid float
      newGrades[subId] = newGrade.toFixed(2);
      e.currentTarget.value = newGrade.toFixed(2);

      // Change color of buttons
      if (revertBtn.classList.contains('inactive')) {
        revertBtn.classList.remove('inactive');
        revertBtn.removeAttribute('disabled');
      }
      if (saveBtn.classList.contains('inactive')) {
        saveBtn.classList.remove('inactive');
        saveBtn.removeAttribute('disabled');
      }
    } else {
      // newGrade was an invalid value, resets grade input to original
      const oldGrade = e.currentTarget.getAttribute('value');
      e.currentTarget.value = oldGrade;

      // Sets the grade in the updated grades object to the original if exists
      if (newGrades[subId] && newGrades[subId] !== oldGrade) {
        newGrades[subId] = oldGrade;
      }
    }
  };

  /**
   * Resets the grades that were edited in the table.
   */
  const resetGrades = () => {
    // Reset values
    gradeCells.forEach((cell) => {
      cell.value = cell.getAttribute('value');
    });

    // Deactivate buttons
    revertBtn.classList.add('inactive');
    revertBtn.setAttribute('disabled', true);
    saveBtn.classList.add('inactive');
    saveBtn.setAttribute('disabled', true);

    // Reset state
    newGrades = {};
  };

  /**
   * Sends the grades in the newGrades object as a JSON to the server.
   */
  const sendNewGrades = () => {
    // Deactivate buttons
    revertBtn.classList.add('inactive');
    revertBtn.setAttribute('disabled', true);
    saveBtn.classList.add('inactive');
    saveBtn.setAttribute('disabled', true);

    // Builds the POST request
    const request = new Request(`/secretary/update-grades`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(newGrades),
    });

    fetch(request)
      .then((response) => {
        if (response.ok) {
          window.location.reload();
        }
      })
      .catch((error) => {
        console.error(error);
      });
  };

  /**
   * Displays the confirmation modal.
   * @param {Event} e
   */
  const showConfirmation = (e) => {
    const id = e.currentTarget.getAttribute('data-id');
    confModal.removeAttribute('hidden');
    confModal.style = `left: ${e.x - 220}px; top: ${e.y - 75}px;`;

    if (e.currentTarget.classList.contains('del-assg-btn')) {
      delBtnForm.setAttribute('action', '/secretary/delete_assg');
    } else if (e.currentTarget.classList.contains('del-sub-btn')) {
      delBtnForm.setAttribute('action', '/secretary/delete_sub');
      subIdInput.setAttribute('value', id);
    }
  };

  /**
   * Hides the confirmation modal.
   * @param {Event} e
   */
  const hideConfirmation = (e) => {
    confModal.setAttribute('hidden', true);
    confModal.style = '';
  };

  /**
   * Returns a report of the similar sentences in the assignment.
   */
  const getSimilarityReport = () => {
    const sid = reportBtn.getAttribute('data-id');

    const request = new Request(`/secretary/s/${sid}/similarity-report`, {
      method: 'GET',
    });

    fetch(request).then((response) => {
      if (response.ok) {
        response.json().then((data) => {
          if (data['error']) {
            alert(data['error']);
          } else {
            const a = document.createElement('a');
            a.href = `data:text/plain;charset=utf-8,${encodeURIComponent(
              data
            )}`;
            a.download = `similarity-report-${sid}.txt`;
            a.click();
          }
        });
      }
    });
  };
  // Event listeners

  closeBtnEditAssg.addEventListener('click', closePopupEditAssg);
  closeBtnManageSub.addEventListener('click', closePopupManageSub);

  if (viewBtns) {
    viewBtns.forEach((viewBtn) => {
      viewBtn.addEventListener('click', openPopup);
    });
  }

  if (editBtn) {
    editBtn.addEventListener('click', openPopup);
  }

  if (gradeCells) {
    gradeCells.forEach((cell) => {
      cell.addEventListener('change', editGrades);
    });
  }

  if (reportBtn) {
    reportBtn.addEventListener('click', getSimilarityReport);
  }

  revertBtn.addEventListener('click', resetGrades);
  saveBtn.addEventListener('click', sendNewGrades);

  delAssgBtn.addEventListener('click', showConfirmation);
  delSubBtn.forEach((btn) => {
    btn.addEventListener('click', showConfirmation);
  });
  cancelBtn.addEventListener('click', hideConfirmation);
})();
