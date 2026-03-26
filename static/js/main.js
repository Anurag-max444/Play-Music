function togglePassword() {
  var pass = document.getElementById("password");
  var icon = document.getElementById("eyeIcon");

  if (pass.type === "password") {
    pass.type = "text";
    icon.classList.remove("fa-eye");
    icon.classList.add("fa-eye-slash");
  } else {
    pass.type = "password";
    icon.classList.remove("fa-eye-slash");
    icon.classList.add("fa-eye");
  }
}