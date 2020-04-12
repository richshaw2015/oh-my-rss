
function initLayout() {
    // 初始化组件
    $('.tooltipped').tooltip();
    $('.modal').modal();
    $('.tabs').tabs();
    $('.sidenav').sidenav({"edge": "right"});

    // 右侧滚动条
    resetHeight();

    // 使页面主内容区域获得焦点，这样快捷键就生效了
    $('#omrss-main').click();
}


function getPageSize() {
    // 每次都动态取，以防窗口变化
    const itemHeight = $('#omrss-cnt-list ul li:first').outerHeight(true);
    const containerHeight = $(window).height() - $('#omrss-header').height() - $('#omrss-pager').height() - 20;

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
        'height': ($(window).height() - 64) + 'px'
    });
    // 左侧内容栏
    if ($(window).width() >= 1600 ) {
        $('#omrss-cnt-list').css({
            'max-height': ($(window).height() - 64 - 60) + 'px'
        });
    } else {
        $('#omrss-cnt-list').css({
            'max-height': ($(window).height() - 64 - 50) + 'px'
        });
    }
}

function setRecommendArticles(articleId) {
    if (getLoginId()) {
        setTimeout(function () {
            $.post("/api/html/recommend/articles", {uid: getOrSetUid(), id: articleId}, function(data){
                $('#omrss-recommend').html(data);
            });
        }, 2000);
    }
}

function loadPage(page) {
    // UI状态
    $('#omrss-loader').removeClass('hide');

    // 网络请求，区分已登录用户或者游客
    let subFeeds = '';
    let unSubFeeds = '';

    if (!getLoginId()) {
        subFeeds = Object.keys(getSubFeeds()).join(',');
        unSubFeeds = Object.keys(getUnsubFeeds()).join(',');
    }
    $.post("/api/html/articles/list", {
        uid: getOrSetUid(), page_size: getPageSize(), page: page, sub_feeds: subFeeds, unsub_feeds: unSubFeeds
    }, function (data) {
        let destDom = $(data);

        // 是否已读，是否点赞
        destDom.find('.collection li[id]').each(function (index) {
            // 默认已读状态；已读变未读
            if (!hasReadArticle(this.id)) {
                // 提示图标
                const unread_el = $(this).find('i.read');
                unread_el.removeClass('read').addClass('unread');
                unread_el.text('lens');

                // 文字样式
                $(this).find('.omrss-title').removeClass('omrss-title-read').addClass('omrss-title-unread');
            }
            if (hasLikeArticle(this.id)) {
                // 点赞图标，本地判断
                const thumb_el = $(this).find('i.thumb-icon');
                thumb_el.addClass('omrss-color');
            }
            if (hasOpenSrc(this.id)) {
                // 打开图标，本地判断
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
        warnToast(NET_ERROR_MSG);
    }).always(function () {
        // UI状态
        $('#omrss-loader').addClass('hide');

        // 记录当前页数
        localStorage.setItem('CURPG', page);
    });
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
    setToreadList(notify=false);

    // 计算未读数，定时执行，?个小时算一次
    setInterval(function () {
        if (isBgWin === true) {
            setToreadList(notify=true);
        } else {
            setToreadList(notify=false);
        }
    }, 4 * 3600 * 1000);
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

            // trim third content style tag
            fixThirdStyleTag();

            // 代码样式
            codeHighlight();

            // 数据统计
            updateReadStats();

            // 同步状态
            if (!hasReadArticle(article_id)) {
                // 未读变为已读
                setReadArticle(article_id, ev_target);

                // 剩余未读数
                updateUnreadCount();
            }

            // linkify
            setThirdLinkify();

            target.scrollTop(0);

            // 推荐文章
            setRecommendArticles(article_id);
        } else {
            // 没有缓存数据，走网络请求
            $('#omrss-loader').removeClass('hide');
            $.post("/api/html/article/detail", {uid: getOrSetUid(), id: article_id}, function (data) {
                // 缓存数据
                setLruCache(article_id, data);

                // 渲染
                const target = $('#omrss-main');
                target.html(data);

                // trim third content style tag
                fixThirdStyleTag();

                // 代码样式
                codeHighlight();

                // 更新统计
                updateReadStats();

                // 未读变为已读
                setReadArticle(article_id, ev_target);

                // 剩余未读数
                updateUnreadCount();

                // linkify
                setThirdLinkify();

                target.scrollTop(0);

                // 浏览打点
                setTimeout(function () {
                    $.post("/api/actionlog/add", {uid: getOrSetUid(), id: article_id, action: "VIEW"}, function(){
                    });
                }, 1000);

                // 推荐文章
                setRecommendArticles(article_id);
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
    });

    // 我的订阅点击
    $(document).on('click', '.ev-my-feed', function () {
        $('#omrss-loader').removeClass('hide');
        user = getLoginId();

        $.post("/api/html/feeds/all", {uid: getOrSetUid()}, function (data) {
            // 游客需要本地判断订阅状态
            if (!user) {
                let destDom = $(data);

                destDom.find('.omrss-item').each(function (index) {
                    const siteName = $(this).attr('data-name');
                    const siteStar = parseInt($(this).attr('data-star'));

                    if (isVisitorSubFeed(siteName)) {
                        $(this).find('a.ev-toggle-feed').text('取消订阅');
                        $(this).find('a.ev-toggle-feed').addClass('omrss-bgcolor');
                    } else if (isVisitorUnSubFeed(siteName)) {
                        $(this).find('a.ev-toggle-feed').text('订阅');
                        $(this).find('a.ev-toggle-feed').removeClass('omrss-bgcolor');
                    } else {
                        // 根据推荐决定
                        if (siteStar >= 20) {
                            // 取消订阅
                            $(this).find('a.ev-toggle-feed').text('取消订阅');
                            $(this).find('a.ev-toggle-feed').addClass('omrss-bgcolor')
                        } else {
                            // 订阅
                            $(this).find('a.ev-toggle-feed').text('订阅');
                            $(this).find('a.ev-toggle-feed').removeClass('omrss-bgcolor');
                        }
                    }
                });
                $('#omrss-main').html(destDom).scrollTop(0);
            } else {
                $('#omrss-main').html(data).scrollTop(0);
            }
            // 初始化组件
            $('.tooltipped').tooltip();
            $('.tabs').tabs();
            resetHeight();
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
        });
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

    // 提交订阅源
    $(document).on('click', '.ev-submit-feed', function () {
        const url = $('#omrss-feed-input').val().trim();
        if (url) {
            $('#omrss-loader').removeClass('hide');
            $.post("/api/feed/add", {uid: getOrSetUid(), url: url}, function (data) {
                subFeed(data.name);
                toast("添加成功，预计一小时内收到更新^o^", 3000);
            }).fail(function () {
                warnToast('RSS地址解析失败，管理员稍后会跟进处理！');
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
        const feedName = $(this).attr('data-name');
        const user = getLoginId();
        const feedEl = $(this);

        if (curStat === '订阅') {
            if (!user) {
                subFeed(feedName);
                toast('订阅成功^o^');
                $(this).text('取消订阅');
                $(this).addClass('omrss-bgcolor');
            } else {
                $('#omrss-loader').removeClass('hide');
                $.post("/api/feed/subscribe", {uid: getOrSetUid(), feed: feedName}, function (data) {
                    toast('订阅成功^o^');
                    feedEl.text('取消订阅');
                    feedEl.addClass('omrss-bgcolor');
                }).fail(function () {
                    warnToast(NET_ERROR_MSG);
                }).always(function () {
                    $('#omrss-loader').addClass('hide');
                });
            }
       } else if (curStat === '取消订阅') {
           if (!user) {
                unsubFeed(feedName);
                toast('取消订阅成功^o^');
                $(this).removeClass('omrss-bgcolor');
                $(this).text('订阅');
            } else {
                $('#omrss-loader').removeClass('hide');
                $.post("/api/feed/unsubscribe", {uid: getOrSetUid(), feed: feedName}, function (data) {
                    toast('取消订阅成功^o^');
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

    // 设置所有已读，区分是否已登录状态
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
            }).fail(function () {
                warnToast(NET_ERROR_MSG);
            })
        } else {
            markReadAll(toReads);
            updateUnreadCount();
            toast("已将全部设为已读^o^");
        }
    });

    // 关于
    $(document).on('click', '.ev-intro', function () {
        $('#omrss-loader').removeClass('hide');

        $.post("/api/html/homepage/intro", {uid: getOrSetUid()}, function (data) {
            target = $('#omrss-main');
            target.html(data);
            target.scrollTop(0);
            resetHeight();
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

        $.post("/api/html/faq", {uid: getOrSetUid()}, function (data) {
            target = $('#omrss-main');
            target.html(data);
            target.scrollTop(0);
            resetHeight();
            updateReadStats();
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
        })
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
        $.post("/api/html/homepage/intro", {uid: getOrSetUid()}, function (data) {
            $('#omrss-main').html(data);
            $('#omrss-main').scrollTop(0);
            resetHeight();
            updateReadStats();
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
        })
    });

    // tips
    $('.ev-tips').click(function () {
        $('#omrss-loader').removeClass('hide');
        $.post("/api/html/homepage/tips", {uid: getOrSetUid()}, function (data) {
            $('#omrss-main').html(data);
            $('#omrss-main').scrollTop(0);
            resetHeight();
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
        })
    });

    // 留言页面
    $(document).on('click', '.ev-leave-msg', function() {
        $('#omrss-loader').removeClass('hide');
        $.post("/api/html/issues/all", {uid: getOrSetUid()}, function (data) {
            $('#omrss-main').html(data);
            $('#omrss-main').scrollTop(0);
            resetHeight();
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
        })
    });

    // 发现页面
    $(document).on('click', '.ev-explore', function() {
        $('#omrss-loader').removeClass('hide');
        $.post("/api/html/explore", {uid: getOrSetUid()}, function (data) {
            if (!getLoginId()) {
                // 游客用户
                let destDom = $(data);

                destDom.find('span.ev-sub-feed').each(function () {
                    const siteName = $(this).attr('data-name');

                    if (isVisitorSubFeed(siteName)) {
                        $(this).text('已订阅');
                        $(this).removeClass('waves-effect').removeClass('btn-small').removeClass('ev-sub-feed');
                    }
                });

                $('#omrss-main').html(destDom);
            } else {
                $('#omrss-main').html(data);
            }
            resetHeight();
            $('#omrss-main').scrollTop(0);
            $('.tabs').tabs();
            $('.tooltipped').tooltip();
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
        })
    });
    // 发现界面切换到 最近提交内容 TAB
    $(document).on('click', '.ev-recent-article', function () {
        $('#omrss-loader').removeClass('hide');
        
        const recommend = $(this).attr('data-type');

        $.post("/api/html/recent/articles", {uid: getOrSetUid(), recommend: recommend}, function (data) {
            if (!getLoginId()) {
                // 游客用户
                let destDom = $(data);

                destDom.find('span.ev-sub-feed').each(function () {
                    const siteName = $(this).attr('data-name');

                    if (isVisitorSubFeed(siteName)) {
                        $(this).text('已订阅');
                        $(this).removeClass('waves-effect').removeClass('btn-small').removeClass('ev-sub-feed');
                    }
                });

                $('#omrss-explore').html(destDom);
            } else {
                $('#omrss-explore').html(data);
            }
            $('#omrss-explore').scrollTop(0);
            $('.tooltipped').tooltip();
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
        });
    });

    // 发现界面切换到 新提交源 TAB
    $(document).on('click', '.ev-new-site', function () {
        $('#omrss-loader').removeClass('hide');
        $.post("/api/html/recent/sites", {uid: getOrSetUid()}, function (data) {
            if (!getLoginId()) {
                // 游客用户
                let destDom = $(data);

                destDom.find('span.ev-sub-feed').each(function () {
                    const siteName = $(this).attr('data-name');

                    if (isVisitorSubFeed(siteName)) {
                        $(this).text('已订阅');
                        $(this).removeClass('waves-effect').removeClass('btn-small').removeClass('ev-sub-feed');
                    }
                });

                $('#omrss-explore').html(destDom);
            } else {
                $('#omrss-explore').html(data);
            }

            $('#omrss-explore').scrollTop(0);
            $('.tooltipped').tooltip();
        }).fail(function () {
            warnToast(NET_ERROR_MSG);
        }).always(function () {
            $('#omrss-loader').addClass('hide');
        });
    });

    // 发现界面订阅
    $(document).on('click', '.ev-sub-feed', function () {
        const feedName = $(this).attr('data-name');
        const user = getLoginId();
        const evTarget = $(this);

        if (!user) {
            subFeed(feedName);
            toast('订阅成功^o^');
            evTarget.text('已订阅');
            evTarget.removeClass('waves-effect').removeClass('btn-small').removeClass('ev-sub-feed');
        } else {
            $('#omrss-loader').removeClass('hide');
            $.post("/api/feed/subscribe", {uid: getOrSetUid(), feed: feedName}, function (data) {
                toast('订阅成功^o^');
                evTarget.text('已订阅');
                evTarget.removeClass('waves-effect').removeClass('btn-small').removeClass('ev-sub-feed');
            }).fail(function () {
                warnToast(NET_ERROR_MSG);
            }).always(function () {
                $('#omrss-loader').addClass('hide');
            });
        }
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
                toast("留言成功^o^");
            }).fail(function () {
                warnToast(NET_ERROR_MSG);
            }).always(function () {
                $('#omrss-loader').addClass('hide');
            })
        }
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

    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState !== 'visible') {
            isBgWin = true;
            console.log('转到后台：' + (new Date()));
        } else {
            isBgWin = false;
            console.log('转到前台：' + (new Date()));
        }
    });
    /* 事件处理结束 */
});
