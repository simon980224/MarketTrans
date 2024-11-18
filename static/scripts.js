// static/scripts/script.js

// 顯示成功訊息
function showSuccess(title, text) {
  Swal.fire({
    icon: 'success',
    title: title,
    text: text,
  });
}

// 顯示錯誤訊息
function showError(title, text) {
  Swal.fire({
    icon: 'error',
    title: title,
    text: text,
  });
}

// 顯示警告訊息
function showWarning(title, text) {
  Swal.fire({
    icon: 'warning',
    title: title,
    text: text,
  });
}
