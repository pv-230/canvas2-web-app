// Global element variables
const addCourse = document.querySelector('.add-course');

const addCourseItem = () => {
  if (!addCourse) return;

  const courseGrid = document.querySelector('.course-grid', HTMLElement);
  const courseCard = document.createElement('button', HTMLElement);

  courseCard.classList.add('course-card');
  courseCard.setAttribute('type', 'button');
  courseCard.textContent = 'New Course';

  courseGrid.insertBefore(courseCard, addCourse);
};

// Event listeners
if (addCourse) {
  addCourse.addEventListener('click', addCourseItem);
}
