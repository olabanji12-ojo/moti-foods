// Star Rating System
const starButtons = document.querySelectorAll('.star-btn');
const ratingInput = document.getElementById('ratingValue');
const ratingText = document.getElementById('ratingText');
let selectedRating = 0;

starButtons.forEach(btn => {
  // Hover effect
  btn.addEventListener('mouseenter', function() {
    const rating = parseInt(this.dataset.rating);
    highlightStars(rating);
  });

  // Click to select
  btn.addEventListener('click', function(e) {
    e.preventDefault();
    selectedRating = parseInt(this.dataset.rating);
    ratingInput.value = selectedRating;
    highlightStars(selectedRating);
    
    const ratingLabels = ['Poor', 'Fair', 'Good', 'Very Good', 'Excellent'];
    ratingText.textContent = ratingLabels[selectedRating - 1];
    ratingText.classList.add('text-[#8B5E3C]', 'font-semibold');
  });
});

// Reset to selected rating on mouse leave
document.getElementById('starRating').addEventListener('mouseleave', function() {
  highlightStars(selectedRating);
});

function highlightStars(rating) {
  starButtons.forEach((btn, index) => {
    if (index < rating) {
      btn.classList.remove('text-gray-300');
      btn.classList.add('text-yellow-400');
    } else {
      btn.classList.remove('text-yellow-400');
      btn.classList.add('text-gray-300');
    }
  });
}

// Form validation
document.getElementById('reviewForm').addEventListener('submit', function(e) {
  if (selectedRating === 0) {
    e.preventDefault();
    alert('Please select a rating before submitting your review.');
    return false;
  }
});