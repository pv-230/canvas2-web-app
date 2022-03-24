const home = (() => {
  const addCourseCard = document.querySelector('.add-course-card');
  const closeBtnFrame = document.querySelector('.close-btn-frame');
  const mainContent = document.querySelector('.main-content');
  const addCourseBg = document.querySelector('.add-course-bg');
  const addCourseForm = document.forms['add-course-form'];

  // Displays the add course form and blurs the background
  const addCourseItem = () => {
    mainContent.style.cssText = 'filter: blur(5px);';
    addCourseBg.removeAttribute('hidden');
  };

  // Closes the add course form window
  const closeFormWindow = () => {
    addCourseForm.reset();
    mainContent.removeAttribute('style');
    addCourseBg.setAttribute('hidden', '');
  };

  // Event listeners
  if (addCourseCard) {
    addCourseCard.addEventListener('click', addCourseItem);
    closeBtnFrame.addEventListener('click', closeFormWindow);
  }
})();
