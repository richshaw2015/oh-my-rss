$(document).ready(function() {

    // 页面样式
    height = ($(window).height() - $('.page-footer').height() - $('header').height())  + 'px';
    $('.cnt-detail').css({'height': height, 'maxHeight': height})
});