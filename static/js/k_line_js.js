function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
};

$(function () {
    $(".shenglva").click(function () {
        $(".hi_jinbi,.hi_jinbi tab").hide();
        $(".hi_jinbi_hi,.hi_jinbi_hi tab").show();
    });

    $(".jinbiba").click(function () {
        $(".hi_jinbi_hi,.hi_jinbi_hi tab").hide();
        $(".hi_jinbi,.hi_jinbi tab").show();
    });

    $(".guanbi").click(function () {
        $("#result").hide();
    });
});

/*设置页面tab*/
$(function () {
    // 点击弹出设置页面
    $("#Setup").click(function () {
        $(".Setup_beijing").show();
    });

    //点击图像变更
    $("#avatarchange").click(function () {
        $(".Setup_navbox li a").attr("class","");
        $(this).addClass("dise bianjitouxiang_b");
        $("#parameters").addClass("canshushezhi_a");
        $("#nickmodify").addClass("xiugainice_a");

        $(".Setup_beijing").show();
        $(".Setup_nichengbox").hide();
        $(".Setup_canshubox").hide();
        $(".Setup_touxiangbox").show();
        //
        var src = $("#MyAvatar")[0].src;
        // alert(src);
        if(src.indexOf("/") > -1){
            var arr = src.split('/');
            var afile = arr[arr.length-1];
        }
        else{
            var afile = src;
        }

        var arr2 = afile.match(/(\d+)./);
        var avatar = Number(arr2[1]) || 1;
        // alert(avatar);

        $("#avatars span").removeClass("gou");
        var span = $("#avatars span").eq(avatar-1);
        span.addClass("gou");
    });

    //点击昵称修改
    $("#nickmodify").click(function () {
        $(".Setup_navbox li a").attr("class","");
        $(this).addClass("dise xiugainice_b");
        $("#avatarchange").addClass("bianjitouxiang_a");
        $("#parameters").addClass("canshushezhi_a");

        $(".Setup_beijing").show();
        $(".Setup_touxiangbox").hide();
        $(".Setup_canshubox").hide();
        $(".Setup_nichengbox").show();
    });

    //点击参数设置
    $("#parameters").click(function () {
        $(".Setup_navbox li a").attr("class","");
        $(this).addClass("dise canshushezhi_b");
        $("#avatarchange").addClass("bianjitouxiang_a");
        $("#nickmodify").addClass("xiugainice_a");

        $(".Setup_beijing").show();
        $(".Setup_nichengbox").hide();
        $(".Setup_touxiangbox").hide();
        $(".Setup_canshubox").show();
    });

    //修改昵称
    $('#setname').click(function () {
            var data = {};
            data['nick'] = $("#name").val();
            data['_xsrf'] = getCookie("_xsrf");
            if (data['nick'] == "") {
                alert("昵称不能为空");
                return false;
            }
            if (data['nick'].length > 32) {
                alert("昵称过长,超过32位");
                return false;
            }
            else {
                $.ajax({
                    url: "/rename",
                    type: "post",
                    data: data,
                    success: function (re) {
                        var jsons = jQuery.parseJSON(re);
                        if (jsons['status'] == 'success') {
                            if (jsons['error'] == '') {
                                $(".Setup_beijing").hide();
                                location.reload();
                            }
                            else {
                                alert(jsons['msg']);
                                return false;
                            }
                        }
                        else {
                            alert("其他错误！");
                            return false;
                        }
                    }
                });
            }
        });

    //修改图像
    $('#setavatar').click(function () {
        var avatar = 0;
        $("#avatars span").each(function(){
            if($(this).hasClass('gou')){
                avatar = $(this).index()+1;
                return false;
            }
        });

        // alert(avatar);
        var data = {};
        data['_xsrf'] = getCookie("_xsrf");
        data['avatar'] = avatar;
        $.ajax({
            url: "/ajax/setavatar",
            type: "post",
            data: data,
            success: function (re) {
                var jsons = jQuery.parseJSON(re);
                if (jsons['status'] == 'success') {
                    if (jsons['error'] == '') {
                        $(".Setup_beijing").hide();
                        location.reload();
                    }
                    else {
                        alert(jsons['msg']);
                    }
                }
                else {
                    alert("其他错误！");
                }
                $(".Continuouslanding").hide();
                location.reload();
            }
        });
    });

    // 参数设置，最多三个限制
    $(".on,.off").click(function () {
        var _this = this;
        if ($(this).hasClass("on")) {
            $(this).removeClass('on');
            $(this).addClass('off');
        }
        else {
            if ($(".ma_anniubox").find(".on").length < 3) {
                $(_this).removeClass('off');
                $(_this).addClass('on');
            }
            else {
                alert("最多选3个");
            }
        }
    });

    // 参数设置：恢复默认设置
    $(".anniuzhu").click(function () {
        document.getElementById('set1').setAttribute("class", "off");
        document.getElementById('set2').setAttribute("class", "on");
        document.getElementById('set3').setAttribute("class", "on");
        document.getElementById('set4').setAttribute("class", "off");
        document.getElementById('set5').setAttribute("class", "on");
    });

    // 参数设置：保存提交
    $(".baocuna").click(function () {
        var data = {};
        $('.ma_anniubox').find('li div').each(function () {
            var key = $(this).data('key');
            if ($(this).attr("class") == "on") {
                data[key] = "1";
            }
            else {
                data[key] = "0";
            }
        });

        data['_xsrf'] = getCookie("_xsrf");
        $.ajax({
            url: "/ajax/setting",
            type: "post",
            data: data,
            success: function (re) {
                var jsons = jQuery.parseJSON(re);
                if (jsons['status'] == 'success') {
                    if (jsons['error'] == '') {
                        $(".Setup_beijing").hide();
                        location.reload();
                    }
                    else {
                        alert(jsons['msg']);
                        return false;
                    }
                }
                else {
                    alert("其他错误！");
                    return false;
                }
            }
        });
    });

    /*头像选项*/
    $("#avatars span").click(function () {
        $("#avatars span").removeClass("gou");
        $(this).toggleClass("gou");
    })
});



/*经典模式tab*/
$(function () {
    $(".ClassicMode_box_nav div").click(function () {
        $(".ClassicMode_box_nav div").removeClass("selected");
        $(this).addClass("selected");
    })
});

$(function () {
    $("#duikang").click(function () {
        $(".darensai_box").hide();
        $(".duikangsai_box").show();
        $(".hunzhansai_box").hide();
    });

    $("#hunzhan").click(function () {
        $(".darensai_box").hide();
        $(".duikangsai_box").hide();
        $(".hunzhansai_box").show();
    });

    $("#danren").click(function () {
        $(".darensai_box").show();
        $(".duikangsai_box").hide();
        $(".hunzhansai_box").hide();
    });
});

/*比赛模式*/
$(function () {
    $("#tiaozhansai").click(function () {
        $(".dajiangsai_box").hide();
        $(".tiaozhansai_box").show();
        $(".huafeisai_box").hide();
    });

    $("#dajiangsai").click(function () {
        $(".tiaozhansai_box").hide();
        $(".huafeisai_box").hide();
        $(".dajiangsai_box").show();
    });

    $("#huafeisai").click(function () {
        $(".huafeisai_box").show();
        $(".dajiangsai_box").hide();
        $(".tiaozhansai_box").hide();
    });
});

/*挑战弹窗*/
$(function () {
    $(".challenge_box_anniu div").click(function () {
        $(".challenge_box").hide();
    });

    $("#challenger").click(function () {
        $(".challenge_box").show();
    })
});


/*连续登陆*/
$(function () {
    $(".klingqujiangli").click(function () {
        //$(".Continuouslanding").hide();
    })
});

/*竞技模式切换*/
$(function () {
    var flag = 0;
    $(".right_anniu").click(function () {
        $(".big_img").animate({
            left: +100
        }, 100, function () {
            $(".ClassicModeimg_box li:last").insertBefore($(".ClassicModeimg_box li:first"));
            $(".ClassicModeimg_box li a").removeClass("big_img");
            $(".ClassicModeimg_box li").eq(1).find("a").addClass("big_img");
            flag++;
            if (flag >= $(".ClassicModeimg_box li").length) {
                $(".big_img").css("left", "-24px");
            }
        });

    });

    $(".left_anniu").click(function () {
        $(".big_img").animate({
            left: -124
        }, 100, function () {
            $(".ClassicModeimg_box li:first").insertAfter($(".ClassicModeimg_box li:last"));
            $(".ClassicModeimg_box li a").removeClass("big_img");
            $(".ClassicModeimg_box li").eq(1).find("a").addClass("big_img");
            flag++;
            if (flag >= $(".ClassicModeimg_box li").length) {
                $(".big_img").css("left", "-24px");
            }
        });
    });
});

/*120倒計時*/
var intDiff = parseInt(119); //120秒倒计时总秒数量

function timer(intDiff) {
    window.setInterval(function () {
        var day = 0,
            hour = 0,
            minute = 0,
            second = 0; //时间默认值
        if (intDiff > 0) {
            second = Math.floor(intDiff) - (day * 24 * 60 * 60) - (hour * 60 * 60) - (minute * 60);
        }
        if (minute <= 9) minute = '0' + minute;
        if (second <= 9) second = '0' + second;
        $('#second_show').html('<s></s>' + second + '秒');
        intDiff--;
    }, 1000);
}

$(function () {
    // timer(intDiff);
});

/*60秒倒计时*/
// var intDiff2 = parseInt(60);
// function timer(intDiff2) {
//     var ii = window.setInterval(function () {
//         var day = 0,
//             hour = 0,
//             minute = 0,
//             second = 0; //时间默认值
//         if (intDiff2 >= 0) {
//             second = Math.floor(intDiff2) - (day * 24 * 60 * 60) - (hour * 60 * 60) - (minute * 60);
//         }
//         if (minute <= 9) minute = '0' + minute;
//         if (second <= 9) second = '0' + second;
//         $('#sixaoji').html('<s></s>' + second + ' ');
//         // $('#js-sec-text').html('<s></s>' + second + ' ');
//         // var e = Math.round(intDiff / 60 * 226);
//         // $("#js-sec-circle").css("strokeDashoffset" , (e - 226).toString());
//         intDiff2--;
//         if (intDiff2 < 0) {
//             $("#k_lineganme").hide();
//             clearTimeout(ii);
//         }
//     }, 1000);
// }

var countdown = 60;
function start_timer(countdown) {
    var timer = window.setInterval(function(){
        var day = 0,
            hour = 0,
            minute = 0,
            second = 0; //时间默认值
        // console.log(countdown);
        second = Math.floor(countdown) - (day * 24 * 60 * 60) - (hour * 60 * 60) - (minute * 60);
        if (minute <= 9) minute = '0' + minute;
        if (second <= 9) second = '0' + second;
        $('#sixaoji').html(second);

        countdown--;
        if (countdown < 0) {
            // $("#k_lineganme").hide();
            clearTimeout(timer);
            beginning = 0;

            $("#result").show();
        }

    }, 1000);
}

var beginning = 0;
$(function () {
    /*k线弹窗*/
    // $("#Toprepare").click(function () {
    //     $("#Toprepare").hide();
    //     $("#my_ok").show();
    //     $("#k_lineganme").show();
    //
    //     countdown = 1;
    //     beginning = 1;
    //     start_timer(countdown);
    // });
});

/*短信倒计时*/

/*挑戰賽倒計時*/
$(function () {
    $("#gold_challenge,#integral_challenge").click(function () {
        var n = 0;
        var time = setInterval(changImg, 1000);

        function changImg() {
            n + 1
            if (n >= 11) {
                clearInterval(time);//停止计时器
                $(".challenge_box").hide();
                return false; // 结束循环;
            } else {
                n = n + 1;
            }
            $(".daoshu li").removeClass("daoshu_show")
            $(".daoshu li").eq(n - 1).addClass("daoshu_show")
        };

        /*取消挑战弹窗*/
        $("#cancel, #to_hall").click(function () {
            clearInterval(time);//停止计时器
            $(".challenge_box").hide();
        });
    });


    /*挑战失败*/
    $(function () {
        $("#succeeds_again").click(function () {
            $(".He_succeeds").hide();
        })
    });

    /*k线底部切换*/
    $(function () {
        $("#tt").click(function () {
            $("#tt,#ff").hide();
            $("#dd").show();
        });
        $("#ff").click(function () {
            $("#ff,#dd").hide();
            $("#tt").show();
        });
        $("#dd").click(function () {
            $("#dd,#tt").hide();
            $("#ff").show();

        });
    });
});

/*k线绘制*/
var flag = false;
var count = 0;
var timeout;
function writeJx() {
    var bgcolor;
    var top;
    var bordercolor;
    var bgcolor;
    if (flag) {  //涨
        bgcolor = "black";
        flag = false;
        top = "0";
        bordercolor = "#ff0404";
    } else {    //跌
        bgcolor = "#04fcff";
        flag = true;
        top = "0";
        bordercolor = bgcolor;
    }

    var number = Math.random();
    numbera = Math.ceil(number * 10);
    numberr = Math.ceil(number * 30);
    numberb = Math.ceil(number * 50);
    numbert = Math.ceil(number * 70);
    var autoheight = numbert;
    var jjstyle = "style='width:1px;height:" + autoheight + "px;border-left:1px solid " + bordercolor + ";position:relative;float:left;margin-left:5px;top:" + numberr + "px;z-index:8;'";
    var ybstyle = "style='position:relative;top:0;width:5px;display:inline-block;height:60px;float:left;margin-left:2px;'";
    var jg = "<div style='position:absolute;bottom:0;width:4.5px;display:inline-block;height:" + numbera + "px; background:" + bgcolor + ";border:1px solid " + bordercolor + "'></div>";
    var jp = "<div style='position:absolute;bottom:0;width:4.5px;display:inline-block;height:" + numberb + "px; background:" + bgcolor + ";border:1px solid " + bordercolor + "'></div>";
    var ja = "<div style='position:absolute;bottom:0;width:4.5px;display:inline-block;height:" + numberr + "px; background:" + bgcolor + ";border:1px solid " + bordercolor + "'></div>";
    var jx = "<div style='position:absolute;top:" + numbera + "px;left:-4px; width:4.5px;display:inline-block;height:" + top + numberr + "px;background:" + bgcolor + ";border:1px solid " + bordercolor + ";z-index:9;'></div>";
    var jj = "<div " + jjstyle + ">" + jx + "</div>";
    var yb = "<div " + ybstyle + ">" + ja + "</div>";
    var gb = "<div " + ybstyle + ">" + jg + "</div>";
    var pb = "<div " + ybstyle + ">" + jp + "</div>";
    $("#kline").append(jj);
    $("#volume").append(yb);
    $("#greenrece").append(gb);
    $("#macd").append(pb);
    timeout = setTimeout(writeJx, 1000);
    count++;
    count %= 60;
    if (count == 0) {
        clearTimeout(timeout);
    }
}

// var nbr = 0;
// var daylines = JSON.parse("{{ daylines }}");
// var maxhigh = parseFloat("{{ maxhigh }}");
// function DrawKline() {
//     var top="0";
//     var bordercolor= "#ff0404";
//     var bgcolor="black";
//
//     var daydata = daylines[nbr];
//     var upline = 0;
//     var downline = 0;
//     /*1:open;2:high;3:low;4:close*/
//     var lineheight = daydata[2]-daydata[3];
//     var rectheight = Math.abs(daydata[1]-daydata[4]);
//     var linetop = maxhigh - daydata[2];
//     var recttop = maxhigh - daydata[1];
//     if(daydata[1]>daydata[4]) /*open>close:跌*/
//     {
//         bgcolor = "#04fcff";
//         bordercolor = bgcolor;
//     }
//
//     // var number = Math.random();
//     // numbera = Math.ceil(number * 10);
//     // numberr = Math.ceil(number * 30);
//     // numbert = Math.ceil(number * 70);
//     // var autoheight = daydata[];
//     var jjstyle = "style='width:1px;height:" + lineheight + "px;border-left:1px solid " + bordercolor + ";position:relative;float:left;margin-left:5px;top:" + margintop + "px;z-index:8;'";
//     var jx = "<div style='position:absolute;top:" + recttop + "px;left:-4px; width:5px;display:inline-block;height:" + rectheight + "px;background:" + bgcolor + ";border:1px solid " + bordercolor + ";z-index:9;'></div>";
//     var jj = "<div " + jjstyle + ">" + jx + "</div>";
//     $("#kline").append(jj);
//     timeout = setTimeout(DrawKline, 1000);
//     count++;
//     count %= 60;
//     if (count == 0) {
//         clearTimeout(timeout);
//     }
// }

function DrawKDJ() {
    var bgcolor;
    var top;
    var bordercolor;
    var bgcolor;
    if (flag) {
        bgcolor = "black";
        flag = false;
        top = "0";
        bordercolor = "#ff0404";
    } else {
        bgcolor = "#04fcff";
        flag = true;
        top = "0";
        bordercolor = bgcolor;
    }

    var number = Math.random();
    numbera = Math.ceil(number * 10);
    numberr = Math.ceil(number * 30);
    numberb = Math.ceil(number * 50);
    numbert = Math.ceil(number * 70);
    var autoheight = numbert;
    var jjstyle = "style='width:1px;height:" + autoheight + "px;border-left:1px solid " + bordercolor + ";position:relative;float:left;margin-left:5px;top:" + numberr + "px;z-index:8;'";
    var ybstyle = "style='position:relative;top:0;width:5px;display:inline-block;height:60px;float:left;margin-left:2px;'";
    var jg = "<div style='position:absolute;bottom:0;width:5px;display:inline-block;height:" + numbera + "px; background:" + bgcolor + ";border:1px solid " + bordercolor + "'></div>";
    var jp = "<div style='position:absolute;bottom:0;width:5px;display:inline-block;height:" + numberb + "px; background:" + bgcolor + ";border:1px solid " + bordercolor + "'></div>";
    var ja = "<div style='position:absolute;bottom:0;width:5px;display:inline-block;height:" + numberr + "px; background:" + bgcolor + ";border:1px solid " + bordercolor + "'></div>";
    var jx = "<div style='position:absolute;top:" + numbera + "px;left:-4px; width:5px;display:inline-block;height:" + top + numberr + "px;background:" + bgcolor + ";border:1px solid " + bordercolor + ";z-index:9;'></div>";
    var jj = "<div " + jjstyle + ">" + jx + "</div>";
    var yb = "<div " + ybstyle + ">" + ja + "</div>";
    var gb = "<div " + ybstyle + ">" + jg + "</div>";
    var pb = "<div " + ybstyle + ">" + jp + "</div>";
    $("#kline").append(jj);
    $("#volume").append(yb);
    $("#greenrece").append(gb);
    $("#macd").append(pb);
    timeout = setTimeout(writeJx, 1000);
    count++;
    count %= 60;
    if (count == 0) {
        clearTimeout(timeout);
    }
    // if(count == 30)
    //     console.log(jj);
    // console.log($("#content").html());
}

function DrawMACD() {
    var bgcolor;
    var top;
    var bordercolor;
    var bgcolor;
    if (flag) {
        bgcolor = "black";
        flag = false;
        top = "0";
        bordercolor = "#ff0404";
    } else {
        bgcolor = "#04fcff";
        flag = true;
        top = "0";
        bordercolor = bgcolor;
    }

    var number = Math.random();
    numbera = Math.ceil(number * 10);
    numberr = Math.ceil(number * 30);
    numberb = Math.ceil(number * 50);
    numbert = Math.ceil(number * 70);
    var autoheight = numbert;
    var jjstyle = "style='width:1px;height:" + autoheight + "px;border-left:1px solid " + bordercolor + ";position:relative;float:left;margin-left:5px;top:" + numberr + "px;z-index:8;'";
    var ybstyle = "style='position:relative;top:0;width:5px;display:inline-block;height:60px;float:left;margin-left:2px;'";
    var jg = "<div style='position:absolute;bottom:0;width:5px;display:inline-block;height:" + numbera + "px; background:" + bgcolor + ";border:1px solid " + bordercolor + "'></div>";
    var jp = "<div style='position:absolute;bottom:0;width:5px;display:inline-block;height:" + numberb + "px; background:" + bgcolor + ";border:1px solid " + bordercolor + "'></div>";
    var ja = "<div style='position:absolute;bottom:0;width:5px;display:inline-block;height:" + numberr + "px; background:" + bgcolor + ";border:1px solid " + bordercolor + "'></div>";
    var jx = "<div style='position:absolute;top:" + numbera + "px;left:-4px; width:5px;display:inline-block;height:" + top + numberr + "px;background:" + bgcolor + ";border:1px solid " + bordercolor + ";z-index:9;'></div>";
    var jj = "<div " + jjstyle + ">" + jx + "</div>";
    var yb = "<div " + ybstyle + ">" + ja + "</div>";
    var gb = "<div " + ybstyle + ">" + jg + "</div>";
    var pb = "<div " + ybstyle + ">" + jp + "</div>";
    $("#kline").append(jj);
    $("#volume").append(yb);
    $("#greenrece").append(gb);
    $("#macd").append(pb);
    timeout = setTimeout(writeJx, 1000);
    count++;
    count %= 60;
    if (count == 0) {
        clearTimeout(timeout);
    }
    // if(count == 30)
    //     console.log(jj);
    // console.log($("#content").html());
}

function DrawVOL() {
    var bgcolor;
    var top;
    var bordercolor;
    var bgcolor;
    if (flag) {
        bgcolor = "black";
        flag = false;
        top = "0";
        bordercolor = "#ff0404";
    } else {
        bgcolor = "#04fcff";
        flag = true;
        top = "0";
        bordercolor = bgcolor;
    }

    var number = Math.random();
    numbera = Math.ceil(number * 10);
    numberr = Math.ceil(number * 30);
    numberb = Math.ceil(number * 50);
    numbert = Math.ceil(number * 70);
    var autoheight = numbert;
    var jjstyle = "style='width:1px;height:" + autoheight + "px;border-left:1px solid " + bordercolor + ";position:relative;float:left;margin-left:5px;top:" + numberr + "px;z-index:8;'";
    var ybstyle = "style='position:relative;top:0;width:5px;display:inline-block;height:60px;float:left;margin-left:2px;'";
    var jg = "<div style='position:absolute;bottom:0;width:5px;display:inline-block;height:" + numbera + "px; background:" + bgcolor + ";border:1px solid " + bordercolor + "'></div>";
    var jp = "<div style='position:absolute;bottom:0;width:5px;display:inline-block;height:" + numberb + "px; background:" + bgcolor + ";border:1px solid " + bordercolor + "'></div>";
    var ja = "<div style='position:absolute;bottom:0;width:5px;display:inline-block;height:" + numberr + "px; background:" + bgcolor + ";border:1px solid " + bordercolor + "'></div>";
    var jx = "<div style='position:absolute;top:" + numbera + "px;left:-4px; width:5px;display:inline-block;height:" + top + numberr + "px;background:" + bgcolor + ";border:1px solid " + bordercolor + ";z-index:9;'></div>";
    var jj = "<div " + jjstyle + ">" + jx + "</div>";
    var yb = "<div " + ybstyle + ">" + ja + "</div>";
    var gb = "<div " + ybstyle + ">" + jg + "</div>";
    var pb = "<div " + ybstyle + ">" + jp + "</div>";
    $("#kline").append(jj);
    $("#volume").append(yb);
    $("#greenrece").append(gb);
    $("#macd").append(pb);
    timeout = setTimeout(writeJx, 1000);
    count++;
    count %= 60;
    if (count == 0) {
        clearTimeout(timeout);
    }
}

/*黑色蒙版*/
function showDiv() {
    showIntervalId = setInterval("inc()", 1000);
}

function inc() {
    var div2 = document.getElementById("div2");
    var div1 = document.getElementById("div1");
    var oldwidth = div1.style.width;
    oldwidth = parseInt(oldwidth, 10);
    if (oldwidth <= 0) {
        clearInterval(showIntervalId);//停止计时器
    }

    oldwidth -= 7.;
    div1.style.width = oldwidth + "px";
    div2.style.width = oldwidth + "px";
}
