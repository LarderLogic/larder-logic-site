document.addEventListener("DOMContentLoaded", () => {
  const input = document.getElementById("tags-input");
  if (!input) return;

  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      input.value = input.value.replace(/,+$/, ""); // strip trailing commas
    }
  });
});