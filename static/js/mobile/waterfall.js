$(function () {
    let iPage = 1;  //默认第1页
    let iTotalPage = 1; //默认总页数为1
    let bIsLoadData = true;   // false:关闭加载数据

    fn_load_content();  // 首次启动加载

    window.onscroll = function () {
        // 滑动滑动条加载更多
        if (checkscrollside()) {
            if (bIsLoadData) {  // 防止在还没有加载完成继续请求加载的数据
                bIsLoadData = false;
                // 如果当前页数据如果小于总页数，那么才去加载数据
                if (iPage < iTotalPage) {
                    iPage += 1;
                    // 去加载数据
                    fn_load_content()
                } else {
                    message.showInfo('已全部加载，没有更多内容！');
                }
            }
        }
    };
    // $(window).scroll(function () {
    //     // 滑动滑动条加载更多
    //     if (checkscrollside()) {
    //         if (bIsLoadData) {  // 防止在还没有加载完成继续请求加载的数据
    //             bIsLoadData = false;
    //             // 如果当前页数据如果小于总页数，那么才去加载数据
    //             if (iPage < iTotalPage) {
    //                 iPage += 1;
    //                 // 去加载数据
    //                 fn_load_content()
    //             } else {
    //                 message.showInfo('已全部加载，没有更多内容！');
    //             }
    //         }
    //     }
    // });

    $(".btn-more").click(function () {
        if (bIsLoadData) {  // 防止在还没有加载完成继续请求加载的数据
            bIsLoadData = false;
            // 如果当前页数据如果小于总页数，那么才去加载数据
            if (iPage < iTotalPage) {
                iPage += 1;
                // 去加载数据
                fn_load_content()
            } else {
                message.showInfo('已全部加载，没有更多内容！');
            }
        }
    });

    // 请求并加载数据
    function fn_load_content() {
        let sDataParams = {
            "page": iPage
        };
        $.ajax({
            url: "/mobile/flowImageApi",  // url尾部需要添加/
            type: "GET",
            data: sDataParams,
            dataType: "json",
        })
            .done(function (res) {
                if (res.errno === "0") {
                    iTotalPage = res.data.total_pages;  // 后端传过来的总页数
                    // 遍历值
                    $.each(res.data.news, function (index, value) {
                        var $oPin = $('<div>').addClass('pin').appendTo($("#main"));
                        var $oBox = $('<div>').addClass('box').appendTo($oPin);
                        $('<img>').attr('src', '' + $(value).attr('image_url')).appendTo($oBox);
                    });
                    waterfall();
                    bIsLoadData = true;
                    message.showInfo('加载完成');
                } else {
                }
            })
            .fail(function () {
            });
    }

    /*
        parend 父级id
        pin 元素id
    */
    function waterfall(parent, pin) {
        var $aPin = $("#main>div");
        var iPinW = $aPin.eq(0).width();// 一个块框pin的宽
        var num = Math.floor($(window).width() / iPinW);//每行中能容纳的pin个数【窗口宽度除以一个块框宽度】
        //oParent.style.cssText='width:'+iPinW*num+'px;ma rgin:0 auto;';//设置父级居中样式：定宽+自动水平外边距
        $("#main").css({
            'width:': iPinW * num,
            'margin': '0 auto'
        });

        var pinHArr = [];//用于存储 每列中的所有块框相加的高度。

        $aPin.each(function (index, value) {
            var pinH = $aPin.eq(index).height();
            if (index < num) {
                pinHArr[index] = pinH; //第一行中的num个块框pin 先添加进数组pinHArr
            } else {
                var minH = Math.min.apply(null, pinHArr);//数组pinHArr中的最小值minH
                var minHIndex = $.inArray(minH, pinHArr);
                $(value).css({
                    'position': 'absolute',
                    'top': minH + 15,
                    'left': $aPin.eq(minHIndex).position().left,
                });
                //数组 最小高元素的高 + 添加上的aPin[i]块框高
                pinHArr[minHIndex] += $aPin.eq(index).height() + 15;//更新添加了块框后的列高
            }
        });
    }

    function checkscrollside() {
        var $aPin = $("#main>div");
        var lastPinH = $aPin.last().get(0).offsetTop + Math.floor($aPin.last().height() / 2);//创建【触发添加块框函数waterfall()】的高度：最后一个块框的距离网页顶部+自身高的一半(实现未滚到底就开始加载)
        var scrollTop = $(window).scrollTop();//注意解决兼容性
        var documentH = $(document).width();//页面高度
        return (lastPinH < scrollTop + documentH);//到达指定高度后 返回true，触发waterfall()函数
    }
});