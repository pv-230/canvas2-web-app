// Global element variables
const profileBtn = document.querySelector('.profile-btn', HTMLElement);
const menuBox = document.querySelector('.menu-box', HTMLElement);

// Shows the profile menu when the profile icon is clicked
const openProfileMenu = (e) => {
  e.stopPropagation(); // Prevents menu from closing (event bubbling)
  menuBox.classList.remove('hidden');
};

// Hides the profile menu when the user clicks on an option or outside of it
const closeProfileMenu = (e) => {
  if (
    !e.target.classList.contains('menu-box') &&
    !menuBox.classList.contains('hidden')
  ) {
    menuBox.classList.add('hidden');
  }
};

// Event listeners
window.addEventListener('click', closeProfileMenu);
profileBtn.addEventListener('click', openProfileMenu);
