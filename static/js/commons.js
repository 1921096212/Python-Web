/*===  navMenuStart ===*/
/*===  菜单栏底下的状态条 ===*/
$(() => {
    let $navLi = $('#header .nav .menu li');
    $navLi.click(function () {
        $(this).addClass('active').siblings('li').removeClass('active')
    });
});
/*===  navMenuEnd ===*/

// 如果访问主页,返回访问者的公网ip
$(function () {
    var ip = returnCitySN["cip"];
    $.ajax({
        url: "/user/getip/?pwd=" + ip,
        type: "GET",
    })
});
// 音乐播放器
// var ap = new APlayer({
//     element: document.getElementById('player1'),
//     narrow: false,
//     autoplay: true,
//     showlrc: false,
//     music: {
//         title: '遇见',
//         author: '孙燕姿',
//         url: 'http://music.163.com/song/media/outer/url?id=287035.mp3',
//         pic: 'http://y.gtimg.cn/music/photo_new/T002R300x300M000002ehzTm0TxXC2.jpg'
//     }
// });
// ap.init();

// 名言警句
$(function () {
    let content = ``;
    $.ajax({
        url: "/user/catchphrase/",
        type: "GET",
    })
        .done(function (res) {
            if (res.errno === "0") {
                content = res.data;
                $("#activities-title").append(content);
            }
        })
});

// http://192.168.31.200:8000/course/
let url = window.location.href;
// http/https
let protocol = window.location.protocol;
// 192.168.31.200:8000
let host = window.location.host;
let domain = protocol + '//' + host;
let path = url.replace(domain, '');
// console.log(path);
let liDomArr = document.querySelectorAll('.nav .menu li');
for (let i = 0; i < liDomArr.length; i++) {
    let aDom = liDomArr[i].querySelector('a');
    if (aDom.href === url) {
        liDomArr[i].className = 'active';
    }
}

/*== logErrorStart ==*/
function logError(err) {
    console.log(err);
    console.log(err.status + "===" + err.statusText);
}
/*== logErrorEnd ==*/

/*== 封装 JQ 的 Ajax ==*/
function selfAjax(url, method, data, successCallback) {
    $.ajax({
        url,
        method,
        data,
        dataType: "json",
        success: successCallback || function (res) {
            console.log(res);
        },
        error: err => {
            logError(err);
        }
    });
}


/*======= 日期格式化 =======*/
function dateFormat(time) {
    // 获取当前的时间戳
    let timeNow = Date.now();
    // 获取发表文章的时间戳
    let TimeStamp = new Date(time).getTime();
    // 转为秒
    let second = (timeNow - TimeStamp) / 1000;
    if (second < 60) {
        return '刚刚'
    } else if (second >= 60 && second < 60 * 60) {
        let minute = Math.floor(second / 60);
        return `${minute}分钟前`;
    } else if (second >= 60 * 60 && second < 60 * 60 * 24) {
        let hour = Math.floor(second / 60 / 60);
        return `${hour}小时前`;
    } else if (second >= 60 * 60 * 24 && second < 60 * 60 * 24 * 30) {
        let day = Math.floor(second / 60 / 60 / 24);
        return `${day}天前`;
    } else {
        let date = new Date(TimeStamp);
        let Y = date.getFullYear() + '/';
        let M = (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1) + '/';
        let D = (date.getDate() < 10 ? '0' + (date.getDate()) : date.getDate()) + ' ';
        let h = (date.getHours() < 10 ? '0' + date.getHours() : date.getHours()) + ':';
        let m = (date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes());
        return Y + M + D + h + m;
    }
}