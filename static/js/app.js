function genUid() {
    /* 生成用户id，自带校验  */
    const sec_key = "bDNsU3BxNXM2b1NyRFJ0dFQwa1o="; // l3lSpq5s6oSrDRttT0kZ
    const sec_ver = 'MDA='; // 00
    const uuid_str = uuid.v4();
    const sign = md5(uuid_str + atob(sec_key)).substring(0, 10)
    return uuid_str + atob(sec_ver) + sign
}

function toast(msg) {
    // 普通
    M.toast({html: msg, displayLength: 1000});
}

function warnToast(msg) {
    // 带样式的
    const html = '<span style="color: #eeff41;">' + msg + '</span>';
    M.toast({html: html, displayLength: 3000});
}

function getOrSetUid() {
    const uid = localStorage.getItem('UID');
    if (uid) {
        return uid;
    } else {
        localStorage.setItem('UID', genUid());
    }
    return localStorage.getItem('UID');
}

function hasReadArticle(id) {
    return localStorage.getItem('READ/' + id);
}

function setReadArticle(id) {
    localStorage.setItem('READ/' + id, '1');
}

function hasLikeArticle(id) {
    return localStorage.getItem('LIKE/' + id);
}

function setLikeArticle(id) {
    localStorage.setItem('LIKE/' + id, '1');
}

function hasOpenSrc(id) {
    return localStorage.getItem('OPEN/' + id);
}

function setOpenSrc(id) {
    localStorage.setItem('OPEN/' + id, '1');
}

function getSubFeeds() {
    const subFeeds = localStorage.getItem('SUBS');
    if (subFeeds) {
        return JSON.parse(subFeeds);
    }
    return {};
}

function getUnsubFeeds() {
    const unsubFeeds = localStorage.getItem('UNSUBS');
    if (unsubFeeds) {
        return JSON.parse(unsubFeeds);
    }
    return {};
}

function subFeed(name) {
    // 订阅
    const subFeeds = getSubFeeds();
    const unsubFeeds = getUnsubFeeds();

    delete unsubFeeds[name];
    subFeeds[name] = 1;

    localStorage.setItem('SUBS', JSON.stringify(subFeeds));
    localStorage.setItem('UNSUBS', JSON.stringify(unsubFeeds));
}

function unsubFeed(name) {
    // 取消订阅
    const subFeeds = getSubFeeds();
    const unsubFeeds = getUnsubFeeds();

    delete subFeeds[name];
    unsubFeeds[name] = 1;

    localStorage.setItem('SUBS', JSON.stringify(subFeeds));
    localStorage.setItem('UNSUBS', JSON.stringify(unsubFeeds));
}

function enterFullscreen() {
    /* 全屏 */
    const el = document.documentElement;
    const rfs = el.requestFullscreen || el.webkitRequestFullScreen || el.mozRequestFullScreen || el.msRequestFullscreen;
    rfs.call(el);
}

function isInFullscreen() {
    /* 是否全屏 */
    return (document.fullscreenElement && document.fullscreenElement !== null) ||
        (document.webkitFullscreenElement && document.webkitFullscreenElement !== null) ||
        (document.mozFullScreenElement && document.mozFullScreenElement !== null) ||
        (document.msFullscreenElement && document.msFullscreenElement !== null);
}


function exitFullscreen() {
    /* 退出全屏 */
    try {
        if (document.exitFullscreen) document.exitFullscreen();
        else if (document.webkitExitFullscreen) document.webkitExitFullscreen();
        else if (document.mozCancelFullScreen) document.mozCancelFullScreen();
        else if (document.msExitFullscreen) document.msExitFullscreen();
    } catch (err) {
        console.warn("退出全屏时遇到异常", err.msg)
    }
    return true;
}

function getPageSize() {
    // 每次都动态取，以防窗口变化
    const pageSize = Math.floor(($(window).height() - $('#omrss-footer').height() - $('#omrss-header').height() -
        60 - 16 * 1.5) / 70);
    return pageSize;
}

function getCurPage() {
    const page = localStorage.getItem('CURPG');
    if (page) {
        return page;
    }
    return '1';
}

function initLayout() {
    $('.tooltipped').tooltip();

    // 使页面主内容区域获得焦点，这样快捷键就生效了
    $('#omrss-main').click();
}

function loadPage(page) {
    // UI状态
    $('#omrss-loader').removeClass('hide');

    // 网络请求
    $.post("/api/ajax/myarticles", {
        uid: getOrSetUid(), page_size: getPageSize(), page: page,
        sub_feeds: Object.keys(getSubFeeds()).join(','), unsub_feeds: Object.keys(getUnsubFeeds()).join(',')
    }, function (data) {
        let destDom = $(data);

        // 是否已读，是否点赞
        destDom.find('.collection li[id]').each(function (index) {
            if (hasReadArticle(this.id)) {
                // 提示图标
                const unread_el = $(this).find('i.unread');
                unread_el.removeClass('unread').addClass('read');
                unread_el.text('check');

                // 文字样式
                $(this).find('.omrss-title').removeClass('omrss-title-unread');
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
        $('#omrss-left').html(destDom);

        // 初始化
        initLayout();
    }).fail(function (xhr) {
        warnToast(xhr.responseText);
    }).always(function () {
        // UI状态
        $('#omrss-loader').addClass('hide');

        // 记录当前页数
        localStorage.setItem('CURPG', page);
    });
}

function updateUnreadCount() {
    // 设置未读数，同时写入缓存，用于后续通知
    const toReads = JSON.parse(localStorage.getItem('TOREADS'));
    let unread = 0;
    if (toReads) {
        for (let i = 0; i < toReads.length; i++) {
            if (!hasReadArticle(toReads[i])) {
                unread += 1;
            }
        }
        if (unread > 0) {
            $('#omrss-unread').html(`<a href="#!"><span class="new badge">${unread}</span></a>`);
            localStorage.setItem('NEW', unread.toString());
        } else {
            $('#omrss-unread').html('');
        }
    }
    return unread;
}

function setToreadList() {
    // 从网络读取列表，然后更新未读数
    $.post("/api/ajax/mytoreads", {
        uid: getOrSetUid(),
        sub_feeds: Object.keys(getSubFeeds()).join(','),
        unsub_feeds: Object.keys(getUnsubFeeds()).join(',')
    }, function (data) {
        localStorage.setItem('TOREADS', JSON.stringify(data.result));
        updateUnreadCount();
    })
}

// 全局LRU缓存服务
let lruCache = new Cache(50, false, new Cache.LocalStorageCacheStorage('OMRSS'));
// 缓存版本号，每次上线需要更新
const cacheVer = '13';

function setLruCache(key, value) {
    if (value.length < 40 * 1024 && value.length > 512) {
        lruCache.setItem(cacheVer + key, value);
        return true;
    }
    return false;
}

function getLruCache(key) {
    return lruCache.getItem(cacheVer + key);
}

// 判断是否是后台窗口
let isBgWin = false;


$(document).ready(function () {
    /* 首页初始化开始 */
    // 样式初始化
    initLayout();

    // 登录初始化 TODO 特性支持检测
    getOrSetUid();

    // 加载列表内容
    loadPage(1);

    // 先更新未读数
    setToreadList();

    // 计算未读数，定时执行，4个小时算一次
    setInterval(function () {
        if (isBgWin === true) {
            setToreadList();
            const newNum = parseInt(localStorage.getItem('NEW'));
            if (newNum > 0) {
                // 发通知
                if (window.Notification && Notification.permission === "granted") {
                    const notify = new Notification(`您有${newNum}条未读订阅`, {
                        tag: "OMRSS",
                        // TODO 增加logo
                        icon: "",
                        body: "请刷新页面后查看"
                    });
                }
            }
        }
    }, 14400000);
    /* 首页初始化结束 */


    /* 事件处理开始 */
    // 文章内容点击
    $(document).on('click', '.ev-cnt-list', function () {
        // UI状态切换
        $('.ev-cnt-list.active').removeClass('active');
        $(this).addClass('active');

        const article_id = this.id;
        const ev_target = $(this);

        // 是否有本地缓存
        const cachedData = getLruCache(article_id);
        if (cachedData) {
            // 直接渲染
            const target = $('#omrss-main');
            target.html(cachedData);

            // 代码样式
            Prism.highlightAll();

            target.scrollTop(0);
            return true;
        }

        // 继续走网络请求
        $('#omrss-loader').removeClass('hide');
        $.post("/api/html/article", {uid: getOrSetUid(), id: article_id}, function (data) {
            // 缓存数据
            setLruCache(article_id, data);

            // 渲染
            const target = $('#omrss-main');
            target.html(data);

            // 代码样式
            Prism.highlightAll();

            target.scrollTop(0);

            if (!hasReadArticle(article_id)) {
                // 未读变为已读
                setReadArticle(article_id);

                const target = ev_target.find('i.unread');
                target.removeClass('unread').addClass('read');
                target.text('check');
                // 文字样式
                ev_target.find('.omrss-title').removeClass('omrss-title-unread');

                // 剩余未读数
                updateUnreadCount();

                // 浏览打点
                setTimeout(function () {
                    $.post("/api/ajax/actionlog", {uid: getOrSetUid(), id: article_id, action: "VIEW"}, function () {
                    });
                }, 1000);
            }
        }).always(function () {
            $('#omrss-loader').addClass('hide');
        });

        // 申请通知权限，5分钟以后
        setTimeout(function () {
            if (Notification.permission === 'default') {
                Notification.requestPermission();
            }
        }, 300000);
    });

    // 我的订阅点击
    $('.ev-my-feed').click(function () {
        $('#omrss-loader').removeClass('hide');

        $.post("/api/html/feeds", {uid: getOrSetUid()}, function (data) {
            let destDom = $(data);
            const subFeeds = getSubFeeds();
            const unsubFeeds = getUnsubFeeds();

            destDom.find('.omrss-item').each(function (index) {
                const siteName = $(this).attr('data-name');
                const siteStar = parseInt($(this).attr('data-star'));

                if (siteName in subFeeds) {
                    // 取消订阅
                    $(this).find('a.ev-toggle-feed').text('取消订阅');
                } else if (siteName in unsubFeeds) {
                    // 订阅
                    $(this).find('a.ev-toggle-feed').text('订阅');
                } else {
                    // 根据推荐决定
                    if (siteStar >= 20) {
                        // 取消订阅
                        $(this).find('a.ev-toggle-feed').text('取消订阅');
                    } else {
                        // 订阅
                        $(this).find('a.ev-toggle-feed').text('订阅');
                    }
                }
            });

            $('#omrss-main').html(destDom).scrollTop(0);

        }).always(function () {
            $('#omrss-loader').addClass('hide');
        });
    });

    // 确定取消订阅
    $(document).on('click', '#omrss-unlike', function () {
        const site = $(this).attr('data-site');
        unsubFeed(site);
        toast("取消订阅成功");
    });

    // 切换订阅状态
    $(document).on('click', '.ev-toggle-feed', function () {
        const curStat = $(this).text();
        const feedName = $(this).attr('data-name');

        if (curStat === '订阅') {
            subFeed(feedName);
            toast('订阅成功');
            $(this).text('取消订阅');
        } else if (curStat === '取消订阅') {
            unsubFeed(feedName);
            toast('取消订阅成功');
            $(this).text('订阅');
        }
    });

    // 翻页处理
    $(document).on('click', '.ev-page', function () {
        const page = $(this).attr('data-page');
        loadPage(page);
    });

    // 点赞处理
    $(document).on('click', '#omrss-like', function () {
        const id = $(this).attr('data-id');
        if (hasLikeArticle(id)) {
            warnToast("已经点赞过了");
        } else {
            $.post("/api/ajax/actionlog", {uid: getOrSetUid(), id: id, action: "LIKE"}, function (data) {
                setLikeArticle(id);
                toast("点赞成功");
            });
        }
    });

    // 打开原站
    $(document).on('click', '.ev-open-src', function () {
        const id = $(this).attr('data-id');
        if (!hasOpenSrc(id)) {
            $.post("/api/ajax/actionlog", {uid: getOrSetUid(), id: id, action: "OPEN"}, function (data) {
                setOpenSrc(id);
            });
        }
    });

    // 设置页面
    $('.ev-settings').click(function () {
        $('#omrss-loader').removeClass('hide');
        $.post("/api/html/settings", {uid: getOrSetUid()}, function (data) {
            $('#omrss-main').html(data);
            $('#omrss-main').scrollTop(0);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
        })
    });

    // 首页
    $('#omrss-logo-font').click(function () {
        $('#omrss-loader').removeClass('hide');
        $.post("/api/html/homepage", {uid: getOrSetUid()}, function (data) {
            $('#omrss-main').html(data);
            $('#omrss-main').scrollTop(0);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
        })
    });

    // 留言页面
    $(document).on('click', '.ev-leave-msg', function() {
        $('#omrss-loader').removeClass('hide');
        $.post("/api/html/issues", {uid: getOrSetUid()}, function (data) {
            $('#omrss-main').html(data);
            $('#omrss-main').scrollTop(0);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
        })
    });

    // 切换全屏
    $('.ev-toggle-fullscreen').click(function () {
        if (isInFullscreen()) {
            exitFullscreen();
            $(this).find('i').text('fullscreen');
            // 重新加载页面
            setTimeout(function () {
                loadPage(getCurPage());
            }, 200);

        } else {
            enterFullscreen();
            $(this).find('i').text('fullscreen_exit');
            // 重新加载页面
            setTimeout(function () {
                loadPage(getCurPage());
            }, 200);
        }
    });

    $(window).bind('focus', function () {
        isBgWin = false;
        console.log('转到前台');
    });

    $(window).bind('blur', function () {
        isBgWin = true;
        console.log('转到后台');
    });
    /* 事件处理结束 */
});