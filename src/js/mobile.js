
function getPageSize() {
    return 12;
}

function loadPage(page) {
    // UI状态
    $('#omrss-loader').removeClass('hide');

    // 网络请求
    $.post("/api/html/articles/list", {
        uid: getOrSetUid(), page_size: getPageSize(), page: page, mobile: true,
        sub_feeds: Object.keys(getSubFeeds()).join(','), unsub_feeds: Object.keys(getUnsubFeeds()).join(',')
    }, function (data) {
        let destDom = $(data);

        // 是否已读，是否点赞
        destDom.find('.collection li[id]').each(function (index) {
            if (!hasReadArticle(this.id)) {
                // 提示图标；变为未读状态
                const unread_el = $(this).find('i.read');
                unread_el.removeClass('read').addClass('unread');
                unread_el.text('lens');

                // 文字样式
                $(this).find('.omrss-title').removeClass('omrss-title-read').addClass('omrss-title-unread');
            }
            if (hasLikeArticle(this.id)) {
                // 点赞图标
                const thumb_el = $(this).find('i.thumb-icon');
                thumb_el.addClass('omrss-color');
            }
            if (hasOpenSrc(this.id)) {
                // 打开图标
                const open_el = $(this).find('i.open-icon');
                open_el.addClass('omrss-color');
            }
        });

        // 时间更新
        destDom.find(".prettydate").prettydate();

        // 渲染
        $('#omrss-main').html(destDom);
    }).fail(function (xhr) {
        warnToast(NET_ERROR_MSG);
    }).always(function () {
        // UI状态
        $('#omrss-loader').addClass('hide');

        // 记录当前页数
        localStorage.setItem('CURPG', page);

        //置顶
        document.body.scrollTop = document.documentElement.scrollTop = 0;
    });
}


$(document).ready(function () {
    /* 首页初始化开始 */
    // 登录初始化
    getOrSetUid();

    // 初始化组件
    $('.modal').modal();

    // 加载列表内容，只有首页才加载
    if (window.location.pathname === '/') {
        loadPage(1);
    }

    if (window.location.pathname !== '/') {
        // 首页文章统计数据，只有非首页才加载
        updateReadStats();

        // FIX 第三方标签样式
        fixThirdStyleTag();
    }

    // 更新未读数
    setToreadList(notify=false);

    /* 首页初始化结束 */

    /* 事件处理开始 */
    // 文章内容点击
    $(document).on('click', '.ev-cnt-list', function () {

        const article_id = this.id;
        const ev_target = $(this);

        // 未读变为已读
        if (!hasReadArticle(article_id)) {
            setReadArticle(article_id, ev_target);

            // 剩余未读数
            updateUnreadCount();

            // 浏览打点
            setTimeout(function () {
                $.post("/api/actionlog/add", {uid: getOrSetUid(), id: article_id, action: "VIEW"}, function () {
                });
            }, 1000);
        }
    });

    // 关于
    $(document).on('click', '.ev-intro', function () {
        $('#omrss-loader').removeClass('hide');

        $.post("/api/html/homepage/intro", {uid: getOrSetUid(), mobile: true}, function (data) {
            target = $('#omrss-article').length !== 0 ? $('#omrss-article') : $('#omrss-main');
            target.html(data);
            target.scrollTop(0);
            updateReadStats();
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
        })
    });

    // FAQ
    $(document).on('click', '.ev-faq', function () {
        $('#omrss-loader').removeClass('hide');

        $.post("/api/html/faq", {uid: getOrSetUid(), mobile: true}, function (data) {
            target = $('#omrss-article').length !== 0 ? $('#omrss-article') : $('#omrss-main');
            target.html(data);
            target.scrollTop(0);
            updateReadStats();
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
        })
    });

    // 设置所有已读
    $(document).on('click', '.ev-mark-readall', function () {
        const toReads = JSON.parse(localStorage.getItem('TOREADS'));

        if (getLoginId()) {
            // 登录用户需要同步服务端状态
            $.post("/api/mark/read", {
                uid: getOrSetUid(),
                ids: toReads.toString()
            }, function (data) {
                markReadAll(toReads);
                updateUnreadCount();
                toast("已将全部设为已读^o^");
            })
        } else {
            markReadAll(toReads);
            updateUnreadCount();
            toast("已将全部设为已读^o^");
        }
    });

    // TODO 支持我的订阅设置
    $(document).on('click', '.ev-my-feed', function () {
        warnToast("功能正在开发中，敬请期待^o^");
    });

    // 提交订阅源，移动端不提供这个入口

    // 切换订阅状态，移动端不提供这个入口

    // 翻页处理
    $(document).on('click', '.ev-page', function () {
        const page = $(this).attr('data-page');
        loadPage(page);
    });

    // 点赞处理
    $(document).on('click', '#omrss-like', function () {
        const id = $(this).attr('data-id');
        if (hasLikeArticle(id)) {
            warnToast("已经点过赞了！");
        } else {
            $.post("/api/actionlog/add", {uid: getOrSetUid(), id: id, action: "THUMB"}, function (data) {
                setLikeArticle(id);
                toast("点赞成功^o^");
            }).fail(function () {
                warnToast(NET_ERROR_MSG);
            });
        }
    });

    // 打开原站
    $(document).on('click', '.ev-open-src', function () {
        const id = $(this).attr('data-id');
        if (!hasOpenSrc(id)) {
            $.post("/api/actionlog/add", {uid: getOrSetUid(), id: id, action: "OPEN"}, function (data) {
                setOpenSrc(id);
            });
        }
    });

    // 关于

    // tips 广告暂时不在移动端适配

    // RSS加载更多

    $(document).on('click', '.ev-window-close', function() {
        if (isInWebview()) {
            location.href = '/';
        } else {
            window.close();
        }
    });

    // 确定取消订阅
    $(document).on('click', '#omrss-unlike', function () {
        const site = $(this).attr('data-site');
        const user = getLoginId();

        if (!user) {
            unsubFeed(site);
            toast("取消订阅成功^o^");
        } else {
            $.post("/api/feed/unsubscribe", {uid: getOrSetUid(), feed: site}, function (data) {
                toast('取消订阅成功^o^');
            }).fail(function () {
                warnToast(NET_ERROR_MSG);
            });
        }
    });
    // 留言页面，暂时不提供留言功能

    // 切换全屏，移动端不提供功能

    /* 事件处理结束 */
});
