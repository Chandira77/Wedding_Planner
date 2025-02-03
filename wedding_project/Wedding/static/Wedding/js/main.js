document.addEventListener("DOMContentLoaded", function() {
    const header = document.querySelector(".header");
    if (header) {
        header.style.opacity = "0";
        setTimeout(() => {
            header.style.transition = "opacity 1s ease-in-out";
            header.style.opacity = "1";
        }, 500);
    }
});
