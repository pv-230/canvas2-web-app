'use strict';

// Assignment management module
(() => {
  // Frames
  const requestsView = document.querySelector('.requests-view', HTMLElement);
  const usersView = document.querySelector('.users-view', HTMLElement);
  const coursesView = document.querySelector('.courses-view', HTMLElement);
  const usersTableBody = document.querySelector('.users-tbody', HTMLElement);
  const searchBar = document.querySelector('.search-bar', HTMLElement);

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

  /**
   *
   * @param {Array} users
   */
  const populateTable = (users) => {
    // Clears the table
    while (usersTableBody.firstElementChild) {
      usersTableBody.removeChild(usersTableBody.firstElementChild);
    }

    if (users.length > 0) {
      users.forEach((user) => {
        const tableRow = document.createElement('tr');
        const tableData1 = document.createElement('td');
        tableData1.textContent = `${user['lastname']}, ${user['firstname']}`;
        tableRow.appendChild(tableData1);

        const tableData2 = document.createElement('td');
        tableData2.textContent = `${user['username']}`;
        tableRow.appendChild(tableData2);

        const tableData3 = document.createElement('td');
        tableData3.textContent = `${user['email']}`;
        tableRow.appendChild(tableData3);

        const tableData4 = document.createElement('td');
        tableData4.classList.add('btn-cell');
        tableData4.textContent = 'BUTTONS';
        tableRow.appendChild(tableData4);
        usersTableBody.appendChild(tableRow);
      });
    } else {
      const tableRow = document.createElement('tr');
      const tableData = document.createElement('td');
      tableData.classList.add('empty-cell');
      tableData.setAttribute('colspan', '4');
      tableData.textContent = 'No users found';
      usersTableBody.appendChild(tableData);
    }
  };

  /**
   * Sends a search string to the server and returns matching users.
   * @param {Event} e
   */
  const searchUsers = (e) => {
    // Builds the POST request
    const request = new Request(`/admin/search-users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(e.target.value),
    });

    // Retrieves the users object
    fetch(request)
      .then((response) => {
        if (response.ok) {
          response.json().then((data) => {
            populateTable(data);
          });
        }
      })
      .catch((error) => {
        console.log(error);
      });
  };

  // Event listeners
  sidebarBtns.forEach((btn) => {
    btn.addEventListener('click', selectView);
  });
  searchBar.addEventListener('change', searchUsers);
})();
