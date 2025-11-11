document.addEventListener("DOMContentLoaded", function () {
  const fileInput = document.getElementById("file");
  const fileDisplay = document.getElementById("file-name-display");

  if (fileInput && fileDisplay) {
    fileInput.addEventListener("change", function (e) {
      if (e.target.files.length > 0) {
        fileDisplay.textContent = e.target.files[0].name;
      } else {
        fileDisplay.textContent = "Nenhum arquivo selecionado";
      }
    });
  }
});
