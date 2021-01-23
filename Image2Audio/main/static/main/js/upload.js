const inputImgFile = document.getElementById("input-img");
const inputImgBtn = document.getElementById("btn-input-img");
const inputImgText = document.getElementById("text-input-img");

const uploadBtn = document.getElementById("btn-upload");

inputImgBtn.addEventListener("click", function () {
  inputImgFile.click();
});

inputImgFile.addEventListener("change", function () {
  if (inputImgFile.value) {
    inputImgText.innerHTML = inputImgFile.value.match(/[\/\\]([\w\d\s.\-\(\)]+)$/)[1];
  } else {
    inputImgText.innerHTML = "No file chosen yet.";
  }
});

function showResults() {
    document.getElementById("container-results").style.display = "block";
}