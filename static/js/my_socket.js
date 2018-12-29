
$(document).ready(function() {
    if (!window.console) window.console = {};
    if (!window.console.log) window.console.log = function() {};


    //$(".bishai_liaotian").live("submit", function() {
    //    newMessage($(this));
    //    return false;
    //});

    //$(".bishai_liaotian").live("keypress", function(e) {
    //    if (e.keyCode == 13) {
    //        newMessage($(this));
    //        return false;
    //    }
    //});



    MySocket.start();
});

function get_kline(){
    //ajax
    var data={
        "_xsrf":$("input[name='_xsrf']").val(),
        "userid":$("#MyAvatar").data("userid"),
        "roomid":content.roomid,
        "status":2
    };
    $.ajax({
        url: "/ajax/kline",
        type: "post",
        data: data,
        success: function (rs) {
            // alert(rs);
           var jsons = jQuery.parseJSON(rs);
           // alert(jsons.status);
           if (jsons['status'] != 'error') {
               $("#k_lineganme").show();

               countdown = 60;
               beginning = 1;
               start_timer(countdown);
           }
        },
        error: function (XMLHttpRequest, textStatus, errorThrown) {
            alert(XMLHttpRequest.status);
            alert(XMLHttpRequest.readyState);
            alert(textStatus);
        }
    });
}

// Send Websocket data
//function send(message) {
//    if (!window.WebSocket) {
//        return;
//    }
//    if (socket.readyState == WebSocket.OPEN) {
//        socket.send(message);
//        alert("finish sending!");
//    } else {
//        alert("The socket is not open.");
//    }
//}
/*
*message id:
*       1:user login;
*       2:chat message;
*       3.game command:
*    +       1:game ready;
*    +       2.game start;
*    +       3.game over;
*    +       4.game quit;
*    +       5.game exit;
*    +       6.game restart;
*       4:challege request;
*       5:challege response;
*/
var MySocket = {
    socket: null,

    start: function () {
        var url = "ws://" + location.host + "/websocket";
        if (!window.WebSocket) {
            window.WebSocket = window.MozWebSocket;
        }

        // Javascript Websocket Client
        if (window.WebSocket && !MySocket.socket) {
            MySocket.socket = new WebSocket(url);

            MySocket.socket.onopen = function (event) {
                var uid = $("#MyAvatar").data("userid");
                var nick = $("#MyAvatar").data("nick");
                if(nick == undefined)
                    nick = "pond";
                if(nick.length < 1)
                    return;

                var userobj = {"from": uid, "msgid": 1, "content": nick};
                MySocket.socket.send(JSON.stringify(userobj));
            };

            MySocket.socket.onmessage = function(event) {
                var rs = JSON.parse(event.data);
                // alert("receive message from websocket!"+event.data);
                if(rs["msgid"] == 4){ /*popup a challege window!*/
                    var r = confirm('来自' + rs['content'] + '挑战,是否接收');
                    if (r == true) {
                        // alert('挑战进行');
                        var nick = rs['content'];
                        var challengersp = {"from": rs['to'],"to": rs['from'], "msgid": 5, "status": 1};
                        MySocket.socket.send(JSON.stringify(challengersp));

                        window.location.href = "play?field=4&type=fight&from="+rs["from"];
                    }
                    else {
                        var challengersp = {"from": rs['to'],"to": rs['from'], "msgid": 5, "status": 0};
                        MySocket.socket.send(JSON.stringify(challengersp));
                    }
                }else if(rs["msgid"] == 5){ /*accept the challege*/
                    // alert("KKKKKKKKKKKKKKKKKK");
                    if(rs.status>0)
                        window.location.href = "play?field=4&type=fight&from="+rs["from"];
                    else
                        alert("2222");
                }else if(rs["msgid"] == 2){ /*receive a message from the peer*/
                     $(".l_bgs ul").append(rs['content']);
                     $(".l_bgs").scrollTop($(".l_bgs")[0].scrollHeight);
                }
                else if(rs["msgid"] == 3){ /*game control message*/
                    var content = rs.content;

                    if(content.cmdid == 2)
                    {
                        $("#Toprepare2").hide();
                        $("#peer_ok").show();

                        var xhtml = "<div class=\"nicheng_box\">\n" +
                            "            <div class=\"nicheng\">\n" +
                            "                <p class=\"name\">"+content.rival.nick+"</p>\n" +
                            "                <p class=\"jinbi\">"+content.rival.gold+"</p>\n" +
                            "            </div>\n" +
                            "        </div>\n" +
                            "        <img id=\"rival\" src=\""+"/static/imgs/avatar/"+content.rival.avatar+".png\" data-userid="+content.rival.userid+" data-nick="+content.rival.nick+">\n" +
                            "        <span class=\"shuju\">0.0%↓</span>";

                        $("#rivalinfo").html(xhtml);
                        // alert($(".k_line_bigbox.k_line_box.bisai_head.bishai_touxiang").html());
                        // $("#peer_ok").delay(3000);

                        setTimeout("get_kline()",1000);
                    }
                     // $(".l_bgs ul").append(rs['content']);
                     // $(".l_bgs").scrollTop($(".l_bgs")[0].scrollHeight);
                }
            };

            // showMessage: function(message) {
            //     var existing = $("#m" + message.id);
            //     if (existing.length > 0) return;
            //
            //     var node = $(message.html);
            //     node.hide();
            //     $("#inbox").append(node);
            //     node.slideDown();
            // },
            // RefuseFight: function(challege) {
            //     var existing = $("#m" + message.id);
            //     if (existing.length > 0) return;
            //
            //     var node = $(message.html);
            //     node.hide();
            //     $("#inbox").append(node);
            //     node.slideDown();
            // },
        }
    }
};