const signinButton = document.getElementById("signin-button");
const formContainer = document.getElementById("form-container");
const customerOption = document.getElementById("customer-option");
const orgOption = document.getElementById("org-option");
const userForm = document.getElementById("user-form");
const orgForm = document.getElementById("org-form");

signinButton.addEventListener("click", () => {
  formContainer.style.display = "flex";
});

customerOption.addEventListener("click", () => {
  userForm.style.display = "block";
  orgForm.style.display = "none";
});

orgOption.addEventListener("click", () => {
  userForm.style.display = "none";
  orgForm.style.display = "block";
});
