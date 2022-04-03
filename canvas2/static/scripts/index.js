const index = (() => {
  const profileBtn = document.querySelector('.profile-btn', HTMLElement);
  const menuBox = document.querySelector('.menu-box', HTMLElement);

  // Shows the profile menu when the profile icon is clicked
  const openProfileMenu = (e) => {
    e.stopPropagation(); // Prevents closing after profile button is clicked
    menuBox.removeAttribute('hidden');
  };

  // Hides the profile menu when the user clicks on an option or outside of it
  const closeProfileMenu = (e) => {
    if (
      !e.target.classList.contains('menu-box') &&
      !menuBox.hasAttribute('hidden')
    ) {
      menuBox.setAttribute('hidden', '');
    }
  };

  // Event listeners
  window.addEventListener('click', closeProfileMenu);
  profileBtn.addEventListener('click', openProfileMenu);
})();
