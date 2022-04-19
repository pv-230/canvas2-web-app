'use strict';

// Assignment management module
(() => {
  // Frames
  const view = document.querySelector('.view', HTMLElement);

  // Approval view
  const approvals = document.createElement('div');
  const appr_content = document.createElement('div');
  appr_content.textContent = 'Approvals content';
  approvals.appendChild(appr_content);
  view.appendChild(approvals);

  // Users view
  const users = document.createElement('div');
  const users_content = document.createElement('div');
  users_content.textContent = 'Users content';
  users.appendChild(users_content);

  // Courses view
  const courses = document.createElement('div');
  const courses_content = document.createElement('div');
  courses_content.textContent = 'Course content';
  courses.appendChild(courses_content);

  // Buttons
  const sidebarBtns = [...document.querySelectorAll('.sidebar-btn')];

  // State
  let selected = sidebarBtns[0];

  /**
   * Switches to the selected admin view.
   * @param {Event} e
   */
  const selectView = (e) => {
    if (!e.target.classList.contains('selected')) {
      // Highlights the selected menu button
      e.target.classList.add('selected');
      selected.classList.remove('selected');
      selected = e.target;

      // Switches to the new view.
      if (view.firstChild) {
        view.removeChild(view.firstChild);

        switch (e.target.textContent) {
          case 'Approvals':
            view.appendChild(approvals);
            break;
          case 'Users':
            view.appendChild(users);
            break;
          case 'Courses':
            view.appendChild(courses);
            break;
        }
      }
    }
  };

  // Event listeners
  sidebarBtns.forEach((btn) => {
    btn.addEventListener('click', selectView);
  });
})();
