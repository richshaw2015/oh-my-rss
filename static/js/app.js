$(document).ready(function() {

    // 页面样式
    const height = ($(window).height() - $('.page-footer').height() - $('header').height())  + 'px';
    $('.cnt-detail').css({'height': height, 'maxHeight': height});
    $('.cnt-index').css({'height': height, 'maxHeight': height});
});