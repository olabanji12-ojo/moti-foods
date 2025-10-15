document.addEventListener("DOMContentLoaded", function () {
    if (window.AOS) {
      AOS.init({
        duration: 1000,
        once: false,
      });
    } else {
      console.error("AOS not found. Make sure it's bundled.");
    }
  });
  