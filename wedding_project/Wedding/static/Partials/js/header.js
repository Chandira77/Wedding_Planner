document.addEventListener("DOMContentLoaded", function () {
    const header = document.querySelector(".header");

    if (header) {  // ✅ Check if header exists
        header.style.opacity = "0";

        setTimeout(() => {
            header.style.transition = "opacity 1s ease-in-out";
            header.style.opacity = "1";
        }, 500);
    } else {
        console.warn("⚠️ Warning: Header element (.header) not found! Check if it's present in the HTML.");
    }
});
