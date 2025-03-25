// 前端与后端API通信示例
const API_BASE_URL = "http://localhost:8000";

async function postData(url = '', data = {}) {
  const response = await fetch(API_BASE_URL + url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  });
  return response.json();
}

// 示例导出（如使用ES模块，则可改为export）
