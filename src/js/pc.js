function initReadMode() {
    const mode = getReadMode();

    if (mode === 'article') {
        $('.ev-toggle-readmode i').text('view_list')
    } else {
        $('.ev-toggle-readmode i').text('view_module')
    }
}

function initOnlyUnreadSwitch() {
    const onlyUnread = getOnlyUnreadSwitch();

    if (onlyUnread === 'yes') {
        $('.ev-toggle-onlyunread i').text('lens');
        $('.ev-toggle-onlyunread i').css('font-size', '18px');
    } else {
        $('.ev-toggle-onlyunread i').text('visibility');
        $('.ev-toggle-onlyunread i').css('font-size', '24px');
    }
}

function isIE() {
    return /Trident\/|MSIE/.test(navigator.userAgent)
}


function initMaterialUI() {
    $('.modal').modal();
    $('#modal-submit-rss').modal({"dismissible": false});
    $('#modal-omrss-ie').modal({"dismissible": false});
    $('#modal-add-issue').modal({"dismissible": false});

    $('.tabs').tabs();
    $('.fixed-action-btn').floatingActionButton();
    $('.tooltipped').tooltip();

    $('textarea#omrss-feed-input').characterCounter();
    $('textarea#issue-input-detail, input#issue-input-name, input#issue-input-contact').characterCounter();
}

function initLayout() {
    // 初始化组件
    initMaterialUI();

    $('.sidenav').sidenav({"edge": "right"});

    // 阅读模式
    initReadMode();
    // 只看未读开关
    initOnlyUnreadSwitch();

    // 右侧滚动条
    resetHeight();

    // 使页面主内容区域获得焦点，这样快捷键就生效了
    $('#omrss-main').focus();
}

// 用于返回上级
function setLastLeftDom(dom){
    sessionStorage.setItem('LLD', dom);
}
function getLastLeftDom(){
    return sessionStorage.getItem('LLD');
}

// 全局保存当前激活站点的未读数
let curSiteUnreadCount = 0;


function getCurSiteUnreadCount() {
    const curSiteUnreadStr = $('.ev-cnt-list.active').find('.omrss-unread-count').text().trim();

    if (curSiteUnreadStr >= 0) {
        curSiteUnreadCount = parseInt(curSiteUnreadStr);
        return curSiteUnreadCount;
    } else {
        return 0;
    }
}

function setCurSiteUnreadCount() {
    $('.ev-cnt-list.active').find('.omrss-unread-count').html(curSiteUnreadCount);

    if (curSiteUnreadCount === 0 ) {
        const unread_el = $('.ev-cnt-list.active').find('i.unread');
        if (unread_el.length !== 0) {
            unread_el.removeClass('unread').addClass('read');
            unread_el.text('check');
        }
        $('.ev-cnt-list.active').find('.omrss-title').removeClass('omrss-title-unread').addClass('omrss-title-read');
        
        if (getReadMode() === 'site') {
            $('.ev-cnt-list.active').find('.omrss-unread-count').addClass('omrss-not-visual');
            $('.ev-cnt-list.active').find('i.visibility-icon').addClass('omrss-not-visual');
        }
    }

    return curSiteUnreadCount;
}

function updateSiteUnreadCount(read=0, abs=null) {
    if ($('#omrss-cur-site-unread').length === 0) {
        return;
    }

    if (abs !== null) {
        curSiteUnreadCount = abs;
        $('#omrss-cur-site-unread').html(abs);
    } else {
        if (read > 0) {
            // 每新增一篇阅读，更新一次
            curSiteUnreadCount -= read;
        }
        if (curSiteUnreadCount >= 0) {
            $('#omrss-cur-site-unread').html(curSiteUnreadCount);
        }
    }
}

function getPageSize(reflow=false) {
    // 每次都动态取，以防窗口变化
    const itemHeight = $('#omrss-cnt-list ul li:first').outerHeight(true);
    let containerHeight = $(window).height() - $('#omrss-header').outerHeight() - $('#omrss-pager').outerHeight() - 20;

    const siteNavHeight = $('#omrss-site-nav').outerHeight();
    if (siteNavHeight !== undefined) {
        containerHeight = containerHeight - siteNavHeight;
    }
    if (reflow) {
        if (siteNavHeight === undefined) {
            containerHeight = containerHeight - 50;
        } else {
            containerHeight = containerHeight + 50;
        }
    }

    let pageSize = 1;
    if (itemHeight > 0) {
        pageSize = Math.floor(containerHeight / itemHeight);
    }
    return pageSize;
}

function getBriefHeight() {
    // 文章摘要的高度计算
    const briefHeight = $(window).outerHeight(true) - $('#omrss-header').outerHeight(true) -
        $('#omrss-article-title').outerHeight(true) - $('#omrss-article-stats').outerHeight(true) -
        $('#omrss-article-bottom').outerHeight(true);
    return parseInt(briefHeight);
}

function resetHeight() {
    // 右侧滚动条
    $('.cnt-right').css({
        'overflow-y': 'auto',
        'height': ($(window).height() - 54) + 'px'
    });
    // 左侧内容栏
    $('#omrss-cnt-list').css({
        'max-height': ($(window).height() - 54 - 42) + 'px'
    });

}

function setCurPage(page) {
    // 记录当前页数
    localStorage.setItem('CURPG', page);
}


function markPageReadAll() {
    // 当前页面文章全部设置已读
    $('#omrss-cnt-list').find('.collection li').each(function (index) {

        if ($(this).find('i.unread').length === 1) {
            const unread_el = $(this).find('i.unread');

            unread_el.removeClass('unread').addClass('read');
            unread_el.text('check');
            $(this).find('.omrss-title').removeClass('omrss-title-unread').addClass('omrss-title-read');
        }
    });
}

function updateVisitorSubStatus(data) {
    // 更新游客已订阅状态
    let destDom = $(data);

    destDom.find('span.ev-sub-feed').each(function () {
        const siteId = $(this).attr('data-site');

        if (isVisitorSubFeed(siteId)) {
            $(this).text('已订阅');
            $(this).removeClass('waves-effect').removeClass('btn-small').removeClass('ev-sub-feed');
        }
    });
    return destDom;
}

function loadPage(page, site="", reflow=false) {
    // UI状态
    $('#omrss-loader').removeClass('hide');

    // 网络请求，区分已登录用户或者游客
    let user, subFeeds, unSubFeeds, mode, onlyUnread;
    [user, subFeeds, unSubFeeds, mode, onlyUnread] = [getLoginId(), '[]', '[]', getReadMode(), getOnlyUnreadSwitch()]

    if (!user) {
        [subFeeds, unSubFeeds] = [getVisitorSubFeeds(), getVisitorUnsubFeeds()];
    }
    if (mode === "site") {
        if (site === "") {
            // 站点浏览模式下的站点翻页
            $.post("/api/html/sites/list", {
                uid: getOrSetUid(), page_size: getPageSize(reflow), page: page, sub_feeds: subFeeds, unsub_feeds: unSubFeeds,
                onlyunread: onlyUnread
            }, function (data) {
                let destDom = $(data);

                // 是否已读
                destDom.find('.collection li').each(function (index) {
                    let unread_count = 0;

                    if (getLoginId()) {
                        // 登陆用户未读状态
                        unread_count = $(this).find('.omrss-unread-count').html().trim();
                    } else {
                        // 游客用户未读数
                        const unread_list = JSON.parse($(this).find('.omrss-unread-count').attr('data-ids'));

                        for (let i=0; i < unread_list.length; i++) {
                            if (!hasVisitorReadArticle(unread_list[i])) {
                                unread_count += 1;
                            }
                        }
                    }

                    if (unread_count > 0) {
                        const unread_el = $(this).find('i.read');
                        unread_el.removeClass('read').addClass('unread');
                        unread_el.text('lens');
                        $(this).find('.omrss-title').removeClass('omrss-title-read').addClass('omrss-title-unread');

                        if (!getLoginId()) {
                            $(this).find('.omrss-unread-count').html(unread_count)
                        }
                    } else {
                        $(this).find('.omrss-unread-count').addClass('omrss-not-visual');
                        $(this).find('i.visibility-icon').addClass('omrss-not-visual');
                    }
                });

                // 时间更新
                destDom.find(".prettydate").prettydate();
                // 渲染
                $('#omrss-left').html(destDom);

                // 初始化
                initLayout();

                setCurPage(page);
            }).fail(function (xhr) {
                warnToast(NET_ERROR_MSG);
            }).always(function () {
                // UI状态
                $('#omrss-loader').addClass('hide');
            });
        } else {
            // 站点浏览模式下的文章翻页，这时候 pageSize 需要单独计算
            $.post("/api/html/articles/list2", {
                uid: getOrSetUid(), page_size: getPageSize(reflow), page: page, site_id: site, onlyunread: onlyUnread
            }, function (data) {

                if (reflow) {
                    // 进入站点专栏，备份 DOM 数据，用于返回
                    setLastLeftDom($('#omrss-left').html());

                    getCurSiteUnreadCount();
                }

                let destDom = $(data);

                // 是否已读，是否点赞
                destDom.find('.collection li[id]').each(function (index) {
                    // 默认已读状态；已读变未读，只有游客需要变更状态
                    if (!getLoginId()) {
                        const isRecent = $(this).attr('data-recent') === 'True';

                        // 历史文章不默认已读
                        if (isRecent && !hasVisitorReadArticle(this.id)) {
                            // 提示图标
                            const unread_el = $(this).find('i.read');
                            unread_el.removeClass('read').addClass('unread');
                            unread_el.text('lens');
                            $(this).find('.omrss-title').removeClass('omrss-title-read').addClass('omrss-title-unread');
                        }
                    }
                });

                // 时间更新
                destDom.find(".prettydate").prettydate();
                // 渲染
                $('#omrss-left').html(destDom);

                // 站点未读数
                updateSiteUnreadCount();

                // 初始化
                initLayout();

                setCurPage(page);
            }).fail(function (xhr) {
                warnToast(NET_ERROR_MSG);
            }).always(function () {
                // UI状态
                $('#omrss-loader').addClass('hide');
            });
        }
    } else if (mode === 'article') {
        $.post("/api/html/articles/list", {
            uid: getOrSetUid(), page_size: getPageSize(reflow), page: page, sub_feeds: subFeeds, unsub_feeds: unSubFeeds,
            onlyunread: onlyUnread
        }, function (data) {
            let destDom = $(data);

            // 是否已读，是否点赞
            destDom.find('.collection li[id]').each(function (index) {
                // 默认已读状态；已读变未读，只有游客需要变更状态
                if (!getLoginId() && !hasVisitorReadArticle(this.id)) {
                    // 提示图标
                    const unread_el = $(this).find('i.read');
                    unread_el.removeClass('read').addClass('unread');
                    unread_el.text('lens');
                    $(this).find('.omrss-title').removeClass('omrss-title-read').addClass('omrss-title-unread');
                }
            });

            // 时间更新
            destDom.find(".prettydate").prettydate();
            // 渲染
            $('#omrss-left').html(destDom);

            // 初始化
            initLayout();

            setCurPage(page);
        }).fail(function (xhr) {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            // UI状态
            $('#omrss-loader').addClass('hide');
        });
    }
}


$(document).ready(function () {
    /* 首页初始化开始 */
    // 样式初始化
    initLayout();

    // 登录初始化 TODO 特性支持检测
    getOrSetUid();

    // 服务器通知
    showServerMsg();
    
    // 加载列表内容
    loadPage(1);

    // 首页文章统计数据
    updateReadStats();

    // 先更新未读数
    setToreadInfo(notify=false);

    // 计算未读数，定时执行，?个小时算一次
    setInterval(function () {
        if (isBgWin === true) {
            setToreadInfo(notify=true);
        } else {
            setToreadInfo(notify=false);
        }
    }, 4 * 3600 * 1000);
    /* 首页初始化结束 */

    setTimeout(function () {
        if (isIE()) {
            $('#modal-omrss-ie').modal('open');
        }
    }, 3500);

    /* 事件处理开始 */
    // 文章内容点击
    $(document).on('click', '.ev-cnt-list', function () {
        // UI状态切换
        $('.ev-cnt-list.active').removeClass('active');
        $(this).addClass('active');

        const articleId = this.id;
        const siteId = $(this).attr('data-site');
        const evTarget = $(this);
        const siteType = $(this).attr('data-type');

        // 文章模式、站点模式
        if (articleId !== undefined && articleId !== "") {
            // 是否有本地缓存
            const cachedData = getLruCache(articleId);

            if (cachedData) {
                // 直接渲染
                const target = $('#omrss-main');
                target.html(cachedData);

                initMaterialUI();

                if (siteType === 'wemp') {
                    fixWempStyleTag();
                    fixArticlePrivilege();
                } else if (siteType === 'podcast') {
                    const episode = $("#omrss-podlove").attr("data-episode")
                    if (episode !== undefined) {
                        window.podlovePlayer("#omrss-podlove", JSON.parse(atob(episode)), podCastConfig)
                    }
                } else {
                    // trim third content style tag
                    fixThirdStyleTag();

                    // 代码样式
                    codeHighlight();

                    // linkify
                    setThirdLinkify();

                    fixArticlePrivilege();
                }

                // 数据统计
                updateReadStats();

                target.scrollTop(0);

                if (evTarget.find('i.unread').length === 1) {
                    // 当前站点未读数更新
                    updateSiteUnreadCount(1);
                    // 未读变为已读
                    setReadArticle(articleId, evTarget);
                    // 剩余未读数
                    updateUnreadCount(1, false);
                }
            } else {
                // 没有缓存数据，走网络请求
                $('#omrss-loader').removeClass('hide');

                $.post("/api/html/article/detail", {uid: getOrSetUid(), id: articleId}, function (data) {
                    // 缓存数据
                    setLruCache(articleId, data);

                    // 渲染
                    const target = $('#omrss-main');

                    target.html(data);

                    initMaterialUI();

                    if (siteType === 'wemp') {
                        fixWempStyleTag();
                        fixArticlePrivilege();
                    } else if (siteType === 'podcast') {
                        const episode = $("#omrss-podlove").attr("data-episode")
                        if (episode !== undefined) {
                            window.podlovePlayer("#omrss-podlove", JSON.parse(atob(episode)), podCastConfig)
                        }
                    } else {
                        // trim third content style tag
                        fixThirdStyleTag();

                        // 代码样式
                        codeHighlight();

                        // linkify
                        setThirdLinkify();

                        fixArticlePrivilege();
                    }

                    // 更新统计
                    updateReadStats();
                    
                    target.scrollTop(0);

                    // 当前站点未读数更新
                    if (evTarget.find('i.unread').length === 1) {
                        // 当前站点未读数更新
                        updateSiteUnreadCount(1);
                        // 未读变为已读
                        setReadArticle(articleId, evTarget);
                        // 剩余未读数
                        updateUnreadCount(1, false);
                    }

                    // 浏览打点
                    setTimeout(function () {
                        $.post("/api/actionlog/add", {uid: getOrSetUid(), id: articleId, action: "VIEW"}, function(){
                        });
                    }, 1000);
                }).fail(function () {
                    warnToast(NET_ERROR_MSG);
                }).always(function () {
                    $('#omrss-loader').addClass('hide');
                });
            }

            // 申请通知权限
            setTimeout(function () {
                if (Notification.permission === 'default') {
                    Notification.requestPermission();
                }
            }, 3600*1000);
        } else if (siteId !== "") {
            // 加载特定站点的文章更新列表
            loadPage(1, siteId, true);
        }

    });

    // 我的订阅点击
    $(document).on('click', '.ev-my-feed', function () {
        $('#omrss-loader').removeClass('hide');

        let user, subFeeds, unSubFeeds;
        [user, subFeeds, unSubFeeds]  = [getLoginId(), '[]', '[]' ]

        if (!user) {
            [subFeeds, unSubFeeds] = [getVisitorSubFeeds(), getVisitorUnsubFeeds()]
        }

        $.post("/api/html/feeds/all", {uid: getOrSetUid(), sub_feeds: subFeeds, unsub_feeds: unSubFeeds}, 
        function (data) {
            $('#omrss-main').html(data).scrollTop(0);

            initMaterialUI();

            resetHeight();
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
            $('#omrss-main').focus();
        });
    });

    // 确定取消订阅
    $(document).on('click', '#omrss-unlike', function () {
        const siteId = $(this).attr('data-site');
        const user = getLoginId();

        if (!user) {
            visitorUnsubFeed(siteId);
            toast("取消订阅成功 ^o^");
        } else {
            $.post("/api/feed/unsubscribe", {uid: getOrSetUid(), site_id: siteId}, function (data) {
                toast('取消订阅成功 ^o^');
            }).fail(function () {
                warnToast(NET_ERROR_MSG);
            });
        }
    });

    $(document).on('click', '.ev-toggle-readmode', function () {
        const mode = toggleReadMode();
        let reflow = false;

        if (mode === 'site') {
            $('.ev-toggle-readmode i').text('view_module');
            toast("切换到站点视图 ^o^");
        } else if (mode === 'article') {
            $('.ev-toggle-readmode i').text('view_list');

            // 从站点视图切换到文章视图，有可能导致分页数变化
            if ($('#omrss-site-nav').outerHeight() !== undefined) {
                reflow = true;
            }
            toast("切换到文章视图 ^o^");
        }
        loadPage(1, "", reflow);
    });

    $(document).on('click', '.ev-toggle-onlyunread', function () {
        if (!getLoginId()) {
            warnToast("登陆后才能只看未读！");
            return false;
        }

        const onlyUnread = toggleOnlyUnread();

        if (onlyUnread === 'yes') {
            $('.ev-toggle-onlyunread i').text('lens');
            $('.ev-toggle-onlyunread i').css('font-size', '18px');
            toast("只看未读 ^o^");
        } else if (onlyUnread === 'no') {
            $('.ev-toggle-onlyunread i').text('visibility');
            $('.ev-toggle-onlyunread i').css('font-size', '24px');
            toast("查看全部 ^o^");
        }
        loadPage(1, "");
    });

    // 自定义订阅源属性
    $(document).on('click', '.ev-submit-custom', function () {
        if (!getLoginId()) {
            $('#omrss-custom-feed').modal('close');
            warnToast('登陆用户才能自定义源！');
            return false;
        }

        const name = $('#omrss-feed-name').val().trim();
        const author = $('#omrss-feed-author').val().trim();
        const site = $('#omrss-custom-feed').attr('data-site').trim();

        if (name && author && site) {
            $('#omrss-loader').removeClass('hide');

            $.post("/api/feed/custom", {uid: getOrSetUid(), site_name: name,
                site_author: author, site_id: site}, function (data) {
                $('#omrss-custom-feed').modal('close');
                toast("更新成功 ^o^");
            }).fail(function () {
                warnToast(NET_ERROR_MSG);
            }).always(function () {
                $('#omrss-loader').addClass('hide');
            });
        } else {
            warnToast('没有输入内容！');
        }
    });

    // 提交订阅源
    $(document).on('click', '.ev-submit-feed', function () {
        const url = $('#omrss-feed-input').val().trim();

        if (url) {
            $('#omrss-loader').removeClass('hide');
            
            $.post("/api/feed/add", {uid: getOrSetUid(), url: url}, function (data) {
                visitorSubFeed(data.site);
                toast("添加成功，预计一天内收到更新 ^o^", 3000);
            }).fail(function () {
                warnToast('RSS 地址解析失败，管理员稍后会跟进处理！');
            }).always(function () {
                $('#omrss-loader').addClass('hide');
            });
        } else {
            warnToast('没有输入内容！');
        }
    });

    // 切换订阅状态
    $(document).on('click', '.ev-toggle-feed', function () {
        const curStat = $(this).text();
        const siteId = $(this).attr('data-site');
        const user = getLoginId();
        const feedEl = $(this);

        if (curStat === '订阅') {
            if (!user) {
                visitorSubFeed(siteId);
                toast('订阅成功 ^o^');
                $(this).text('取消订阅');
                $(this).addClass('omrss-bgcolor');
            } else {
                $('#omrss-loader').removeClass('hide');
                $.post("/api/feed/subscribe", {uid: getOrSetUid(), site_id: siteId}, function (data) {
                    if (data.code === 0) {
                        toast(data.msg);
                        feedEl.text('取消订阅');
                        feedEl.addClass('omrss-bgcolor');
                    } else if (data.code === 1) {
                        warnToast(data.msg);
                    }
                }).fail(function () {
                    warnToast(NET_ERROR_MSG);
                }).always(function () {
                    $('#omrss-loader').addClass('hide');
                });
            }
       } else if (curStat === '取消订阅') {
           if (!user) {
                visitorUnsubFeed(siteId);
                toast('取消订阅成功 ^o^');
                $(this).removeClass('omrss-bgcolor');
                $(this).text('订阅');
            } else {
                $('#omrss-loader').removeClass('hide');
                $.post("/api/feed/unsubscribe", {uid: getOrSetUid(), site_id: siteId}, function (data) {
                    toast('取消订阅成功 ^o^');
                    feedEl.text('订阅');
                    feedEl.removeClass('omrss-bgcolor');
                }).fail(function () {
                    warnToast(NET_ERROR_MSG);
                }).always(function () {
                    $('#omrss-loader').addClass('hide');
                });
            }
        }
    });

    // 翻页处理
    $(document).on('click', '.ev-page', function () {
        const page = $(this).attr('data-page');
        const site = $(this).attr('data-site');

        loadPage(page, site);
    });

    // 左上角返回按钮
    $(document).on('click', '.ev-site-back', function () {
        $('#omrss-loader').removeClass('hide');

        $('#omrss-left').html(getLastLeftDom());

        setCurSiteUnreadCount();

        $('#omrss-loader').addClass('hide');
    });

    // 设置所有已读，区分是否已登录状态
    $(document).on('click', '.ev-mark-readall', function () {
        $('#omrss-loader').removeClass('hide');

        if (getLoginId()) {
            // 登录用户需要同步服务端状态
            $.post("/api/mark/read", {uid: getOrSetUid()}, function (data) {
                // 全局未读数
                setUserUnreadCount(0);
                updateUserUnreadCount();
                // 站点未读数
                updateSiteUnreadCount(0, 0);
                // 页面 UI 状态
                markPageReadAll();

                toast("将全部设为已读 ^o^");
            }).fail(function () {
                warnToast(NET_ERROR_MSG);
            }).always(function () {
                $('#omrss-loader').addClass('hide');
            })
        } else {
            const toReads = JSON.parse(localStorage.getItem('TOREADS'));

            // 全局未读数
            markVisitorReadAll(toReads);
            updateUnreadCount();
            // 站点未读数
            updateSiteUnreadCount(0, 0);
            // 页面 UI 状态
            markPageReadAll();

            $('#omrss-loader').addClass('hide');

            toast("将全部设为已读 ^o^");
        }
    });

    // 设置站点所有已读，区分是否已登录状态
    $(document).on('click', '.ev-site-readall', function () {
        $('#omrss-loader').removeClass('hide');

        let toReads = $(this).attr("data-articles");

        if (getLoginId()) {
            $.post("/api/mark/read", {uid: getOrSetUid(), ids: toReads}, function (data) {
                // 全局未读数
                setUserUnreadCount(data.result);
                updateUserUnreadCount();
                
                // 站点未读数 0
                updateSiteUnreadCount(0, 0);
                // 页面 UI 未读状态
                markPageReadAll();

                toast("已将该站点设为已读 ^o^");
            }).fail(function () {
                warnToast(NET_ERROR_MSG);
            }).always(function () {
                $('#omrss-loader').addClass('hide');
            })
        } else {
            // 全局未读数
            toReads = JSON.parse(toReads);

            markVisitorReadAll(toReads);
            updateUnreadCount();
            // 站点未读数 0
            updateSiteUnreadCount(0, 0);
            // 页面 UI 状态
            markPageReadAll();

            $('#omrss-loader').addClass('hide');

            toast("已将该站点设为已读 ^o^");
        }
    });

    // 立刻更新
    $(document).on('click', '.ev-site-sync', function () {
        $('#omrss-loader').removeClass('hide');

        const siteId = $(this).attr('data-site');

        $.post("/api/update/site", {uid: getOrSetUid(), site_id: siteId}, function (data) {
            toast("刷新成功，请稍后访问 ^o^");
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
        })
    });
        
    // 关于
    $(document).on('click', '.ev-intro', function () {
        $('#omrss-loader').removeClass('hide');

        $.post("/api/html/homepage/intro", {uid: getOrSetUid()}, function (data) {
            target = $('#omrss-main');
            target.html(data);

            initMaterialUI();

            target.scrollTop(0);
            resetHeight();
            updateReadStats();
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
            $('#omrss-main').focus();
        })
    });

    // 首页
    $('#omrss-logo-font').click(function () {
        $('#omrss-loader').removeClass('hide');
        $.post("/api/html/homepage/intro", {uid: getOrSetUid()}, function (data) {
            $('#omrss-main').html(data);

            initMaterialUI();

            $('#omrss-main').scrollTop(0);
            resetHeight();
            updateReadStats();
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
            $('#omrss-main').focus();
        })
    });

    // 留言页面
    $(document).on('click', '.ev-leave-msg', function() {
        $('#omrss-loader').removeClass('hide');
        $.post("/api/html/issues/all", {uid: getOrSetUid()}, function (data) {
            $('#omrss-main').html(data);

            initMaterialUI();

            $('#omrss-main').scrollTop(0);
            resetHeight();
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
            $('#omrss-main').focus();
        })
    });

    // 发现页面
    $(document).on('click', '.ev-explore', function() {
        $('#omrss-loader').removeClass('hide');

        $.post("/api/html/explore", {uid: getOrSetUid()}, function (data) {
            if (!getLoginId()) {
                $('#omrss-main').html(updateVisitorSubStatus(data));
            } else {
                $('#omrss-main').html(data);
            }
            initMaterialUI();

            resetHeight();
            $('#omrss-main').scrollTop(0);
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
            $('#omrss-main').focus();
        })
    });
    // 发现界面切换到 最近提交内容 TAB
    $(document).on('click', '.ev-recent-article', function () {
        $('#omrss-loader').removeClass('hide');
        
        $.post("/api/html/recent/articles", {uid: getOrSetUid()}, function (data) {
            if (!getLoginId()) {
                $('#omrss-explore').html(updateVisitorSubStatus(data));
            } else {
                $('#omrss-explore').html(data);
            }
            initMaterialUI();

            $('#omrss-explore').scrollTop(0);
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
            $('#omrss-main').focus();
        });
    });

    // 发现界面切换到 新提交源 TAB
    $(document).on('click', '.ev-new-site', function () {
        $('#omrss-loader').removeClass('hide');

        $.post("/api/html/recent/sites", {uid: getOrSetUid()}, function (data) {
            if (!getLoginId()) {
                $('#omrss-explore').html(updateVisitorSubStatus(data));
            } else {
                $('#omrss-explore').html(data);
            }
            initMaterialUI();
            $('#omrss-explore').scrollTop(0);
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
            $('#omrss-main').focus();
        });
    });

    // 排行榜
    $(document).on('click', '.ev-ranking', function () {
        $('#omrss-loader').removeClass('hide');

        $.post("/api/html/ranking", {uid: getOrSetUid()}, function (data) {
            if (!getLoginId()) {
                $('#omrss-main').html(updateVisitorSubStatus(data));
            } else {
                $('#omrss-main').html(data);
            }
            initMaterialUI();
            $('#omrss-main').scrollTop(0);
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
            $('#omrss-main').focus();
        });
    });

    $(document).on('click', '.ev-feed-ranking', function () {
        $('#omrss-loader').removeClass('hide');

        $.post("/api/html/feed/ranking", {uid: getOrSetUid()}, function (data) {
            if (!getLoginId()) {
                $('#omrss-ranking').html(updateVisitorSubStatus(data));
            } else {
                $('#omrss-ranking').html(data);
            }
            
            initMaterialUI();
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
            $('#omrss-main').focus();
        });
    });

    $(document).on('click', '.ev-user-ranking', function () {
        $('#omrss-loader').removeClass('hide');

        $.post("/api/html/user/ranking", {uid: getOrSetUid()}, function (data) {
            $('#omrss-ranking').html(data);
            initMaterialUI();
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
            $('#omrss-main').focus();
        });
    });

    // 发现界面订阅
    $(document).on('click', '.ev-sub-feed', function () {
        const siteId = $(this).attr('data-site');
        const user = getLoginId();
        const evTarget = $(this);

        if (!user) {
            visitorSubFeed(siteId);
            toast('订阅成功 ^o^');
            evTarget.text('已订阅');
            evTarget.removeClass('waves-effect').removeClass('btn-small').removeClass('ev-sub-feed');
        } else {
            $('#omrss-loader').removeClass('hide');

            $.post("/api/feed/subscribe", {uid: getOrSetUid(), site_id: siteId}, function (data) {
                if (data.code === 0) {
                    toast(data.msg);
                    evTarget.text('已订阅');
                    evTarget.removeClass('waves-effect').removeClass('btn-small').removeClass('ev-sub-feed');
                } else if (data.code === 1) {
                    warnToast(data.msg);
                }
            }).fail(function () {
                warnToast(NET_ERROR_MSG);
            }).always(function () {
                $('#omrss-loader').addClass('hide');
            });
        }
    });

    // 回到顶部
    $(document).on('click', '#omrss-top', function () {
        $('#omrss-main').scrollTop(0);
    });

    // 提交留言
    $(document).on('click', '.ev-submit-msg', function() {
        if (hasLeaveMsgToday()) {
            warnToast("您今天已经留过言了，明天再来吧！");
        } else {
            $('#omrss-loader').removeClass('hide');
            const content = $('#issue-input-detail').val();
            const nickname = $('#issue-input-name').val();
            const contact = $('#issue-input-contact').val();

            $.post("/api/message/add", {uid: getOrSetUid(), content: content, nickname: nickname,
                contact: contact}, function (data) {
                $('#omrss-main').html(data);
                $('#omrss-main').scrollTop(0);
                setLeaveMsgToday();
                toast("留言成功 ^o^");
            }).fail(function () {
                warnToast(NET_ERROR_MSG);
            }).always(function () {
                $('#omrss-loader').addClass('hide');
                $('#omrss-main').focus();
            })
        }
    });

    // 提交搜索表单
    $(document).on('submit', 'form.omrss-top-form', function(e) {
        const keyword = $("#omrss-search").val().trim();

        if (keyword) {
            $('#omrss-loader').removeClass('hide');

            $.post("/search", {uid: getOrSetUid(), keyword: keyword, scope: 'all'}, function (data) {
                if (!getLoginId()) {
                    $('#omrss-main').html(updateVisitorSubStatus(data));
                } else {
                    $('#omrss-main').html(data);
                }

                // 初始化组件
                initMaterialUI();

                $('#omrss-main').scrollTop(0);
            }).fail(function () {
                warnToast(SEARCH_ERROR_MSG);
            }).always(function () {
                $('#omrss-loader').addClass('hide');
                $('#omrss-main').focus();
            })
        }
        e.preventDefault();
    });
    $(document).on('click', '.ev-search', function(e) {
        const keyword = $(this).attr('data-keyword');
        const scope = $(this).attr('data-scope');

        if (keyword && scope) {
            $('#omrss-loader').removeClass('hide');

            $.post("/search", {uid: getOrSetUid(), keyword: keyword, scope: scope}, function (data) {
                if (!getLoginId()) {
                    $('#omrss-search-result').html(updateVisitorSubStatus(data));
                } else {
                    $('#omrss-search-result').html(data);
                }
                // 初始化组件
                initMaterialUI();

                $('#omrss-search-result').scrollTop(0);
            }).fail(function () {
                warnToast(SEARCH_ERROR_MSG);
            }).always(function () {
                $('#omrss-loader').addClass('hide');
                $('#omrss-main').focus();
            })
        } else {
            warnToast(NEED_REFRESH_MSG);
        }
    });

    // 切换全屏 TODO FIXME
    $('.ev-toggle-fullscreen').click(function () {
        if (isInFullscreen()) {
            exitFullscreen();

            // 重新加载页面
            setTimeout(function () {
                location.reload();
            }, 200);
        } else {
            enterFullscreen();
        }
    });

    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState !== 'visible') {
            isBgWin = true;
            // console.log('转到后台：' + (new Date()));
        } else {
            isBgWin = false;
            // console.log('转到前台：' + (new Date()));
        }
    });
    /* 事件处理结束 */
});
