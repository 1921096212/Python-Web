/**
 * Created 蓝羽教学 on 2019/11/1.
 */
$(function () {

  // 删除标签
  let $courseDel = $(".btn-del");  // 1. 获取删除按钮
  $courseDel.click(function () {   // 2. 点击触发事件
    let _this = this;
    let sCourseId = $(this).parents('tr').data('id');
    let sGroupName = $(this).parents('tr').data('name');
    //获取用户数量
    let num_users = $(this).parents('tr').find('td:nth-child(2)').html();
    // 判断组成员是否为空
      if (num_users>'0'){
          message.showError('组成员不能为空');
          return
      }
    fAlert.alertConfirm({
      title: "确定删除 \$(sGroupName) 吗？",
      type: "error",
      confirmText: "确认删除",
      cancelText: "取消删除",
      confirmCallback: function confirmCallback() {

        $.ajax({
          url: "/admin/groups/" + sCourseId + "/",  // url尾部需要添加/
          // 请求方式
          type: "DELETE",
          dataType: "json",
        })
          .done(function (res) {
            if (res.errno === "0") {
              message.showSuccess("用户组删除成功");
              $(_this).parents('tr').remove();
            } else {
              swal.showInputError(res.errmsg);
            }
          })
          .fail(function () {
            message.showError('服务器超时，请重试！');
          });
      }
    });
  });


  // get cookie using jQuery
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      let cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        let cookie = jQuery.trim(cookies[i]);
        // Does this cookie string begin with the name we want?
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
  }

  // Setting the token on the AJAX request
  $.ajaxSetup({
    beforeSend: function (xhr, settings) {
      if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
        xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
      }
    }
  });

});
