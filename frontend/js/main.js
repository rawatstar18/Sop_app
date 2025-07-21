document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
      loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
  
        const username = document.getElementById("username").value;
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
  
        try {
          const response = await fetch("http://localhost:8000/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
          });
  
          const result = await response.json();
  
          if (response.ok) {
            alert("Login successful");
            // Redirect to dashboard or homepage
            window.location.href = "users.html";
          } else {
            alert(result.detail || "Login failed");
          }
        } catch (error) {
          console.error("Error:", error);
          alert("An error occurred");
        }
      });
    }
  });
  