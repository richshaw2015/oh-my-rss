$(document).ready(function () {

    //Init Collapsible
    $('.collapsible').collapsible();
    // Init Floating Bar
    $('.fixed-action-btn').floatingActionButton();

    // 页面样式
    const cntHeight = ($(window).height() - $('.page-footer').height() - $('header').height()) + 'px';

    $('.cnt-right').css({'height': cntHeight, 'maxHeight': cntHeight});
    $('.cnt-left').css({'height': cntHeight, 'maxHeight': cntHeight});

    $('#page').css({'bottom': $('.page-footer').height() + 'px'});
});