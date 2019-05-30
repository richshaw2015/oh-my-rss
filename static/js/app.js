jQuery(document).ready(function () {
    M.AutoInit();

    //Init Collapsible
    jQuery('.collapsible').collapsible();

    var elem = document.querySelector('.collapsible');
    var instance = new M.Collapsible(elem, {
        // inDuration: 1000,
        // outDuration: 1000
    });

    // 页面样式
    const height = ($(window).height() - $('.page-footer').height() - $('header').height()) + 'px';
    $('.cnt-detail').css({'height': height, 'maxHeight': height});
    $('.cnt-index').css({'height': height, 'maxHeight': height});
});