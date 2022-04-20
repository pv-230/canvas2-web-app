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
  let usersObject = null;
  let timeout = null;

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
   * Sends the user details that need to be saved to the server.
   * @param {Event} e
   */
  const saveUserDetails = (e) => {
    const fields = [];

    // Collects the input field data
    const tableRow = e.target.parentNode.parentNode;
    const childrenArr = [...tableRow.children];
    childrenArr.forEach((td) => {
      if (!td.classList.contains('btn-cell')) {
        const input = td.firstElementChild;
        fields.push(input.value);
      }
    });

    // Attach user ID
    fields.push(e.target.getAttribute('data-id'));

    // Builds the POST request
    const request = new Request(`/admin/action/updateUserInfo`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(fields),
    });

    // Sends the request
    fetch(request)
      .then((response) => {
        if (response.ok) {
          // Clears the table
          while (usersTableBody.firstElementChild) {
            usersTableBody.removeChild(usersTableBody.firstElementChild);
          }
        }
      })
      .catch((error) => {
        console.log(error);
      });
  };

  /**
   * Allows an admin to edit details from the table.
   * @param {Event} e
   */
  const editUser = (e) => {
    const userData = {};

    // Clear the previous save button, if exists
    const saveBtn = document.querySelector('.save-btn');
    if (saveBtn) {
      // Swap event listeners
      saveBtn.removeEventListener('click', saveUserDetails);
      saveBtn.addEventListener('click', editUser);

      // Update button
      saveBtn.textContent = 'Edit';
      saveBtn.classList.remove('save-btn');
      saveBtn.classList.add('edit-btn');

      // Tables input fields to table cells
      const tableRow = saveBtn.parentNode.parentNode;
      const childrenArr = [...tableRow.children];
      childrenArr.forEach((td) => {
        if (!td.classList.contains('btn-cell')) {
          const data = td.firstChild.getAttribute('value');
          td.removeChild(td.firstChild);
          td.textContent = data;
        }
      });
    }

    // Changes table cells to input fields
    const tableRow = e.target.parentNode.parentNode;
    const childrenArr = [...tableRow.children];
    childrenArr.forEach((td) => {
      if (!td.classList.contains('btn-cell')) {
        const inputEl = document.createElement('input');
        inputEl.setAttribute('type', 'text');
        inputEl.setAttribute('value', `${td.textContent}`);
        td.textContent = '';
        td.appendChild(inputEl);
      }
    });

    // Swap event listeners
    e.target.removeEventListener('click', editUser);
    e.target.addEventListener('click', saveUserDetails);

    // Update button
    e.target.textContent = 'Save';
    e.target.classList.remove('edit-btn');
    e.target.classList.add('save-btn');
  };

  /**
   * Produces rows in the table containing user data.
   * @param {object} users
   */
  const populateTable = (users) => {
    // Clears the table
    while (usersTableBody.firstElementChild) {
      usersTableBody.removeChild(usersTableBody.firstElementChild);
    }

    if (Object.values(users).length > 0) {
      Object.values(users).forEach((user) => {
        const tableRow = document.createElement('tr');

        const tableData0 = document.createElement('td');
        tableData0.textContent = `${user['lastname']}`;
        tableRow.appendChild(tableData0);

        const tableData1 = document.createElement('td');
        tableData1.textContent = `${user['firstname']}`;
        tableRow.appendChild(tableData1);

        const tableData2 = document.createElement('td');
        tableData2.textContent = `${user['username']}`;
        tableRow.appendChild(tableData2);

        const tableData3 = document.createElement('td');
        tableData3.textContent = `${user['email']}`;
        tableRow.appendChild(tableData3);

        const tableData4 = document.createElement('td');
        tableData4.classList.add('btn-cell');
        const editBtn = document.createElement('button');
        editBtn.classList.add('edit-btn');
        editBtn.setAttribute('type', 'button');
        editBtn.setAttribute('data-id', user['_id']);
        editBtn.textContent = 'Edit';
        editBtn.addEventListener('click', editUser);
        tableData4.appendChild(editBtn);
        tableRow.appendChild(tableData4);
        usersTableBody.appendChild(tableRow);
      });
    } else {
      const tableRow = document.createElement('tr');
      const tableData = document.createElement('td');
      tableData.classList.add('empty-cell');
      tableData.setAttribute('colspan', '5');
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
    clearTimeout(timeout);
    timeout = setTimeout(() => {
      fetch(request)
        .then((response) => {
          if (response.ok) {
            response.json().then((data) => {
              usersObject = data;
              populateTable(usersObject);
            });
          }
        })
        .catch((error) => {
          console.log(error);
        });
    }, 500);
  };

  // Event listeners
  sidebarBtns.forEach((btn) => {
    btn.addEventListener('click', selectView);
  });
  searchBar.addEventListener('input', searchUsers);
})();
