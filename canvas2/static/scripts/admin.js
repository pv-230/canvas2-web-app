'use strict';

// Assignment management module
(() => {
  // Frames
  const requestsView = document.querySelector('.requests-view', HTMLElement);
  const usersView = document.querySelector('.users-view', HTMLElement);
  const coursesView = document.querySelector('.courses-view', HTMLElement);

  // Buttons
  const sidebarBtns = [...document.querySelectorAll('.sidebar-btn')];

  // State
  let selectedBtn = sidebarBtns[0];
  let selectedView = requestsView;

  /**
   * Switches to the selected admin view.
   * @param {Event} e
   */
  const selectView = (e) => {
    if (!e.target.classList.contains('selected')) {
      // Highlights the selected menu button
      e.target.classList.add('selected');
      selectedBtn.classList.remove('selected');
      selectedBtn = e.target;

      switch (e.target.textContent) {
        case 'Requests':
          selectedView.setAttribute('hidden', true);
          requestsView.removeAttribute('hidden');
          selectedView = requestsView;
          break;
        case 'Users':
          selectedView.setAttribute('hidden', true);
          usersView.removeAttribute('hidden');
          selectedView = usersView;
          break;
        case 'Courses':
          selectedView.setAttribute('hidden', true);
          coursesView.removeAttribute('hidden');
          selectedView = coursesView;
          break;
      }
    }
  };

  // Event listeners
  sidebarBtns.forEach((btn) => {
    btn.addEventListener('click', selectView);
  });
})();
