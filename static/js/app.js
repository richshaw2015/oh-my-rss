function genUid() {
    /* 生成用户id，自带校验  */
    const sec_key = "bDNsU3BxNXM2b1NyRFJ0dFQwa1o="; // l3lSpq5s6oSrDRttT0kZ
    const sec_ver = 'MDA='; // 00
    const uuid_str = uuid.v4();
    const sign = md5(uuid_str + atob(sec_key)).substring(0, 10)
    return uuid_str + atob(sec_ver) + sign
}

function getUid() {
    return localStorage.getItem('UID');
}

function setUid() {
    localStorage.setItem('UID', genUid());
}


$(document).ready(function () {

    // 页面样式
    const cntHeight = ($(window).height() - $('.page-footer').height() - $('header').height()) + 'px';

    $('.cnt-right').css({'height': cntHeight, 'maxHeight': cntHeight});
    $('.cnt-left').css({'height': cntHeight, 'maxHeight': cntHeight});

    $('#page').css({'bottom': $('.page-footer').height() + 'px'});

    const cntList = ($(window).height() - $('.page-footer').height() - $('header').height() - $('#page').height()) + 'px';
    $('#cnt-list').css({'height': cntList, 'maxHeight': cntList});

    // 隐藏 loading
    $('#omrss-loader').addClass('hide');

    /* 登录初始化 TODO 特性支持检测 */
    if (!getUid()) {
        setUid()
    }


    /* 事件处理 */
    $('.ev-cnt-list').click(function () {
        // UI状态切换
        $('.ev-cnt-list.active').removeClass('active');
        $(this).addClass('active');
        $('#omrss-loader').removeClass('hide');

        // 网络请求
        $.post("/api/article", {uid: getUid(), id: this.id}, function (data) {
            $('#omrss-main').html(data);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
        })
    });

});