// HR模块交互逻辑
document.addEventListener("DOMContentLoaded", function() {
    const hrLoginForm = document.getElementById("hrLoginForm");
    if (hrLoginForm) {
      hrLoginForm.addEventListener("submit", async function(e) {
        e.preventDefault();
        const email = document.getElementById("email").value;
        const password = document.getElementById("password").value;
        const data = { email, password };
        try {
          const res = await postData("/auth/login", data);
          if (res.access_token) {
            localStorage.setItem("hr_token", res.access_token);
            alert("登录成功！");
            window.location.href = "job_create.html";
          } else {
            alert("登录失败");
          }
        } catch (err) {
          console.error(err);
        }
      });
    }
  
    // HR岗位创建逻辑已在job_create.html中处理
  });
  