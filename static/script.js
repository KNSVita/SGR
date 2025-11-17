document.addEventListener("DOMContentLoaded", function () {
  const fileInput = document.getElementById("file");
  const fileLabelSpan = document.querySelector(".custom-file-upload span");

  if (fileInput && fileLabelSpan) {
    fileInput.addEventListener("change", function (e) {
      if (e.target.files.length > 0) {
        fileLabelSpan.innerText = e.target.files[0].name;
      } else {
        fileLabelSpan.innerText = "Clique para selecionar a planilha";
      }
    });
  }

  const uploadForm = document.querySelector(".form-upload");
  const loader = document.getElementById("loading-overlay");

  if (loader) {
    loader.style.display = "none";
  }

  if (uploadForm && loader) {
    uploadForm.addEventListener("submit", function () {
      loader.style.display = "flex";
    });
  }
});
