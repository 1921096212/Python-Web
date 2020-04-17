// 视频播放功能

$(function () {
    // 得到视频控件
    let $course_data = $(".course-data");
    let sVideoUrl = $course_data.data('video-url');
    let sCoverUrl = $course_data.data('cover-url');

    let player = cyberplayer("course-video").setup({
        width: '100%',
        height: 650,
        file: sVideoUrl,
        image: sCoverUrl,
        autostart: false,
        stretching: "uniform",
        repeat: false,
        volume: 100,
        controls: true,
        ak: '449769c4341c41aeabb693512d547155'
    });

});