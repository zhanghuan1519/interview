// 面试者模块交互逻辑
/*
document.addEventListener("DOMContentLoaded", function() {
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
      loginForm.addEventListener("submit", async function(e) {
        e.preventDefault();
        const phone = document.getElementById("contact").value;
        const code = document.getElementById("code").value;
        const data = { phone, code };
        try {
          const res = await postData("/candidate/login", data);
          if (res.message === "登录成功") {
            // 保存登录状态
            localStorage.setItem("candidate_id", res.candidate_id);
            //alert("登录成功！");
            window.location.href = "profile_confirm.html";
          } else {
            //alert(res.detail || "登录失败");
          }
        } catch (err) {
          console.error(err);
        }
      });
    }
  });*/
  