const minimizeButton = document.getElementById("minimize-chat");
const closeButton = document.getElementById("close-chat");
const chatBox = document.querySelector(".main-box");

if (chatBox) {
    chatBox.classList.add("minimized");
    minimizeButton.innerHTML = '<i class="fa-solid fa-caret-up"></i>';

    minimizeButton.addEventListener("click", function () {
        chatBox.classList.toggle("minimized");
        if (chatBox.classList.contains("minimized")) {
            minimizeButton.innerHTML = '<i class="fa-solid fa-caret-up"></i>';
        } else {
            minimizeButton.innerHTML = '<i class="fa-solid fa-minus"></i>';
        }
    });

    closeButton.addEventListener("click", function () {
        chatBox.style.display = "none";
    });
}
