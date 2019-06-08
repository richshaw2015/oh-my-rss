$(document).ready(function () {

    // 初始化组件
    $('.fixed-action-btn').floatingActionButton();
    $('.tooltipped').tooltip();
    $('.materialboxed').materialbox();
    $('.modal').modal({"dismissible": false});
    $('#modal-qrcode').modal({"dismissible": true});
    $('textarea#issue-input-detail, input#issue-input-name, input#issue-input-contact').characterCounter();

    // 页面样式
    const cntHeight = ($(window).height() - $('.page-footer').height() - $('header').height()) + 'px';

    $('.cnt-right').css({'height': cntHeight, 'maxHeight': cntHeight});
    $('.cnt-left').css({'height': cntHeight, 'maxHeight': cntHeight});

    $('#page').css({'bottom': $('.page-footer').height() + 'px'});
});