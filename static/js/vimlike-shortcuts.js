/**
 * @fileoverview
 *
 * NOTE:
 *   - 在 keypress 中绑定可见按键的事件
 *   - 在 keyup/keydown 中绑定不可见按键的事件, keyup/keydown 添加的 action 的 pattern 不会生效，通过 filter 过滤
 * 
 * Helpers:
 *   logger
 *   utils
 *   Proto
 *   Event
 *
 * Core Classes:
 *   KeyStroke
 *   ActionContainer
 *   Router
 *   Controller
 * 
 * Functions for initializing
 *   extractToWindow
 *   main
 */

(function() {

function logger() {
    if (logger.LOG_LEVEL !== 'debug') {
        return;
    }

    var args = Array.prototype.slice.call(arguments);
    // args.unshift(+new Date + ':');

    var console = window.console;
    var log = console && console.log;
    if (log) {
        if (log.apply) {
            log.apply(console, args);
        } else {
            console.log(args);
        }
    } 
}
logger.LOG_LEVEL = '@debug@';

var utils = {
    in_array: function(item, array) {
        if (!(array instanceof Array)) {
            return false;
        }

        var nativeIndexOf = Array.prototype.indexOf;
        if (nativeIndexOf && array.indexOf === nativeIndexOf) {
            return array.indexOf(item) !== -1;
        } else {
            for (var i = 0, len = array.length; i < len; ++i) {
                if (item === array[i]) {
                    return true;
                }
            }

            return false;
        }
    },

    trim: function (str) {
        var TRIM_REG = /^\s+|\s+$/g;

        var nativeTrim = String.prototype.trim;

        str = String(str);
        if (nativeTrim && nativeTrim === str.trim) {
            return str.trim(str);
        } else {
            return str.replace(TRIM_REG, '');
        }
    } 
};

/**
 * @param __constructor {Function}
 * @param proto {Object}
 */ 
function Proto(__constructor, proto) {
    if (typeof __constructor !== 'function') {
        throw new TypeError('Argument "__constructor" of "Proto" need to be an instance of a "Function"!');
    }
    if (!(proto && (proto instanceof Object))) {
        return __constructor.prototype;
    }

    this.constructor = __constructor;
    for (var p in proto) {
        if (proto.hasOwnProperty(p)) {
            this[p] = proto[p];
        }
    }
}

var Event = {
    addListener: function() {
        if (document.addEventListener) {
            return function(node, type, fn) {
                node.addEventListener(type, fn, false);
            }
        } else if (document.attachEvent) {
            return function(node, type, fn) {
                node.attachEvent('on' + type, fn);
            }
        } else {
            return function(node, type, fn) {
                throw 'cannot bind event"' + type + '"';
            }
        }
    }(),

    removeListener: function() {
        if (document.removeEventListener) {
            return function(node, type, fn) {
                node.removeEventListener(type, fn, false);
            }
        } else if (document.detachEvent) {
            return function(node, type, fn) {
                node.detachEvent('on' + type, fn);
            }
        } else {
            return function(node, type) {
                throw 'cannot remove event"' + type + '"';
            }
        }
    }(),

    /**
     * return Event object with normalized interface
     */
    EventObject: function(event) {
        event = event || window.event;
        
        // COPY property
        var e = {};
        e.originalEvent = event;
        var props = 'type altKey attrChange attrName bubbles button cancelable charCode clientX clientY ctrlKey currentTarget data detail eventPhase fromElement handler keyCode layerX layerY metaKey newValue offsetX offsetY originalTarget pageX pageY prevValue relatedNode relatedTarget screenX screenY shiftKey srcElement target toElement view wheelDelta which'.split(' ');
        var l = props.length, prop;
        while (l) {
            prop = props[--l];
            e[prop] = event[prop];
        }

        // normalize if necessary
        if (!e.target) {
            e.target = event.srcElement || document;
        }
        
        // add which for key events
        if (e.which === undefined) {
            e.which = (event.charCode !== undefined) ? event.charCode : event.keyCode;
        }

        if (!e.stopPropagation) {
            e.stopPropagation = function() {
                event.cancelBubble = true;
            }
        }
        if (!e.preventDefault) {
            e.preventDefault = function() {
                event.returnValue = false;
            }
        }

        return e;
    }
};

/**
 * @param Event: wrapped native Event object
 */
function KeyStroke(event) {
    this.event = event;
}
KeyStroke.prototype = new Proto(KeyStroke, {
    isEscape: function() { // esc
        return this.getKeyCode() == 27;
    },

    isValidKeyStroke: function() {
        var INVALID_TARGETS = ['input', 'textarea'];

        var target = this.event.target;

        var tagName = target.tagName.toLowerCase();

        if (utils.in_array(tagName, INVALID_TARGETS)) {
            return false;
        }

        // contenteditable
        var contenteditable = target.getAttribute('contenteditable');
        // ie8 的 ie7 模式下返回 inherit, WHAT THE HELL!, 其他情况没有测试
        if (contenteditable && contenteditable !== 'inherit') {
            return false;
        }

        return true;
    },

    isKeydown: function() {
        return this.getEventType() === 'keydown';
    },

    isKeypress: function () {
        return this.getEventType() === 'keypress';
    },

    isKeyup: function() {
        return this.getEventType() === 'keyup';
    },

    getKeyCode: function() {
        return this.event.which;
    },

    getKeyStroke: function() {
        return String.fromCharCode(this.getKeyCode());
    },

    getEventType: function() {
        return this.event.type;
    },

    getEvent: function() {
        return this.event;
    }
});

function ActionContainer() {
    this.actions = {
        keydown: [],
        keypress: [],
        keyup: []
    };
}
ActionContainer.prototype = new Proto(ActionContainer, {
    /**
     * @param {Object}
     * Object example:
     * {
     *   type: 'keypress',
     *   pattern: {
     *     isRegExp: false,
     *     value: 'zhanglin'
     *   },
     *   fns: {
     *     filter: function(currentKeyStroke, keyStrokes, keyStroke) {},
     *     execute: function(currentKeyStroke, keyStrokes, keyStroke) {},
     *     clear: function(currentKeyStroke, keyStrokes, keyStroke) {}
     *   }
     * }
     */
    // TODO: check properties of action
    addAction: function(action) {
        var type = utils.trim(action.type || '').toLowerCase();

        if (!this.actions[type]) {
            throw new TypeError('Invalid "type" of "action" in [ActionContainer::addAction]');
        }

        this.actions[type].push(action);
    },

    getActions: function (type) {
        return this.actions[type] || [];
    },

    getAllActions: function() {
        return this.actions;
    }
});

function Router(actionContainer) {
    this.actionContainer = actionContainer;

    this.keyStrokes = '';
    this.prevKeypressActions = null;
}
Router.prototype = new Proto(Router, {
    handle: function (keyStroke) {
        if (keyStroke.isKeypress()) {
            // 只在 keypress 中获取字符
            this.keyStrokes += keyStroke.getKeyStroke();
            this.handleKeypress(keyStroke);
        } else {
            this.handleKeyHit(keyStroke);
        }
    },

    handleKeypress: function(keyStroke) {
        var actions = this.getPrevKeypressActions();
        actions = this.filterKeypresActions(actions, keyStroke);
        this.setPrevKeypressActions(actions);

        this.execute(actions, keyStroke);
    },

    handleKeyHit: function(keyStroke) {
        var actions = this.actionContainer.getActions(keyStroke.getEventType());
        actions = this.filterKeyHitActions(actions, keyStroke);

        this.execute(actions, keyStroke);
    },

    filterKeypresActions: function(actions, keyStroke) {
        var results = [],
            currentKeyStroke = keyStroke.getKeyStroke(),
            keyStrokes = this.keyStrokes;

        var i = 0,
            len = actions.length;
        for (; i < len; ++i) {
            filter(actions[i]);
        }

        return results;

        function filter(action) {
            var value,
                pattern = action.pattern,
                pattern_filter_ret;

            if (pattern) {
                value = pattern.value;
                if (pattern.isRegExp) {
                    value = new RegExp(value);
                    pattern_filter_ret = value.test(keyStrokes);
                } else {
                    pattern_filter_ret = value.indexOf(keyStrokes) === 0;
                }

                if (pattern_filter_ret && filterByFn(action)) {
                    results.push(action);
                } else {
                    // 执行不符合要求的 clear 函数, 因为之前执行了他的 execute 方法, 可能需要清理
                    executeClear(action);
                }
            } else {
                filterByFn(action);
            }
        }

        function filterByFn(action) {
            var filter = action.fns && action.fns.filter;
            if (typeof filter === 'function') {
                if (filter(currentKeyStroke, keyStrokes, keyStroke)) {
                    return true;
                } else {
                    return false;
                }
            } else {
                return true;
            }
        }

        // 执行被过滤掉的 clear 函数
        function executeClear(action) {
            var clear = action.fns && action.fns.clear;

            if (typeof clear === 'function') {
                clear(currentKeyStroke, keyStrokes, keyStroke);
            }
        }
    },

    // keydown/keyup 只通过 filter 函数过滤, 只有 filter 函数返回 真才会执行
    filterKeyHitActions: function(actions, keyStroke) {
        var i = 0,
            len = actions.length,
            action,
            filter,
            results = [],
            currentKeyStroke = keyStroke.getKeyStroke(),
            keyStrokes = this.keyStrokes;

        for (; i < len; ++i) {
            action = actions[i];
            filter = action.fns && action.fns.filter;
            if (typeof filter === 'function' && filter(currentKeyStroke, keyStrokes, keyStroke)) {
                results.push(action);
            }
        }

        return results;
    },

    execute: function (actions, keyStroke) {
        var currentKeyStroke = keyStroke.getKeyStroke(),
            keyStrokes = this.keyStrokes;

        var len = actions.length;
        if (len > 0) {
            var i = 0,
                fns,
                execute,
                allFinished = true,
                ret,
                pattern;
            for (; i < len; ++i) {
                pattern = actions[i].pattern;
                // keydown/keyup 没有 pattern
                // 对于 字符串 pattern, 只有完全输入才执行
                if (pattern && !pattern.isRegExp && keyStrokes !== pattern.value ) {
                    ret = false;
                } else {
                    fns = actions[i].fns;
                    execute = fns.execute;

                    logger('[Router::execute], ',this,currentKeyStroke, keyStrokes, keyStroke);
                    ret = execute(currentKeyStroke, keyStrokes, keyStroke);
                }

                allFinished = ret && allFinished;
            }

            // keyup/keydown 函数都返回真也会清空输入!!!
            if (allFinished) {
                this.clearKeyStrokes();
                this.clearPrevKeypressActions();
            }
        } else if (keyStroke.isKeypress()) { // 防止 keydown/keyup 中清空
            this.clearKeyStrokes();
            this.clearPrevKeypressActions();
        }
    },

    getPrevKeypressActions: function() {
        return this.prevKeypressActions == null ?
                    this.actionContainer.getActions('keypress') :
                    this.prevKeypressActions;
    },

    setPrevKeypressActions: function(actions) {
        if (actions.length > 0) {
            this.prevKeypressActions = actions;
        } else {
            this.clearPrevKeypressActions();
        }
    },

    clearPrevKeypressActions: function() {
        this.prevKeypressActions = null;
    },

    clearKeyStrokes: function () {
        this.keyStrokes = '';
    }
});

function Controller(router) {
    this.router = router;

    this.bindedEvents = {};
    this.handlers = {};

    this.setHandlers();
}
Controller.prototype = new Proto(Controller, {
    setHandlers: function() {
        var self = this;

        var handle = function (event) {
            var keyStroke = new KeyStroke(Event.EventObject(event));

            self.router.handle(keyStroke);
        };

        this.handlers.keydown = handle;
        this.handlers.keypress = handle;
        this.handlers.keyup  = handle;
    },

    bindEvent: function (type) {
        if (!this.bindedEvents[type]) {
            this.bindedEvents[type] = true;
            Event.addListener(document, type, this.handlers[type]);

            logger('[Controller::bindEvent], bind Event: "' + type + '"');
        }
    },

    unbindEvent: function (type) {
        if (this.bindedEvents[type]) {
            this.bindedEvents[type] = false;
            Event.removeListener(document, type, this.handlers[type]);
            logger('[Controller::unbindEvent], unbind Event: "' + type + '"');
        }
    }
});

function extractToWindow(controller, actionContainer) {
    window.shortcuts = {
        bindEvents: function(types) {
            if (types instanceof Array) {
                for (var i = 0, len = types.length; i < len; ++i) {
                    bind(types[i]);
                }
            } else {
                bind(types);
            }

            function bind(type) {
                if (isValidEventType(type)) {
                    controller.bindEvent(type);
                } else {
                    throw new TypeError('[shortcuts::bindEvents], invalid types: ' + types);
                }
            }
        },

        unBindEvents: function(types) {
            for (var i = 0, l = types.length; i < l; ++i) {
                controller.unbindEvent(types[i]);
            }
        },

        addActions: function (actions) {
            if (actions instanceof Array) {
                for (var i = 0, len = actions.length; i < len; ++i) {
                    add(actions[i]);
                }
            } else {
                add(actions);
            }

            function add(action) {
                var type = utils.trim(action.type || '');

                if (isValidEventType(type)) {
                    actionContainer.addAction(action);
                } else {
                    throw new TypeError('[shortcuts::addActions], invalid type: ' + action.type);
                }
            }
        },
        
        getActions: function(type) {
            var ret = [];
            if (isValidEventType(type)) {
                ret = actionContainer.getActions(type);
            } else {
                ret = actionContainer.getAllActions();
            }

            return ret;
        },

        logger: {
            on: function() {
                logger.LOG_LEVEL = 'debug';
            },
            off: function() {
                logger.LOG_LEVEL = 'Hello World!~';
            },
            log: function() {
                logger.apply(null, arguments);
            }
        } 
    }

    // guard for api
    function isValidEventType (type) {
        var validTypes = ['keydown', 'keypress', 'keyup'];
        if (utils.in_array(type, validTypes)) {
            return true;
        } else {
            return false;
        }
    }
}
function main() {
    var actionContainer = new ActionContainer(),
        router = new Router(actionContainer),
        controller = new Controller(router);

    extractToWindow(controller, actionContainer);
}

main();

})();
/**
 * @fileoverview
 * 
 * Helpers:
 *   DOM
 *   utils
 *   logger
 *
 * Core
 *   V
 *
 * Functions for initializing
 */
(function(S) {

var logger = S.logger;
// logger.off();

var DOM = (function() {
var doc = document,
    isStrictMode = doc.compatMode === 'CSS1Compat';

return {
    /**
     * 元素是否被隐藏了 (display:none|visibility:hidden|祖先被隐藏)
     */
    isVisible: function(ele) {
        var rect = ele.getBoundingClientRect();
        var props = ['top', 'right', 'bottom', 'left'];

        var ret;
        ret = utils.every(props, function(value, index) {
            if (rect[value] === 0) {
                return true;
            }
        });

        return !ret;
    },

    isInView: function(ele) {
        if (!DOM.isVisible(ele)) { // 被隐藏
            return false;
        } else {
            var rect = ele.getBoundingClientRect();
            var props = ['top'];

            var ret;
            // 上面
            ret = utils.every(props, function(value, index) {
                if (rect[value] < 0) {
                    return true;
                }
            });
            if (ret) {
                return false;
            }

            // 下面
            var viewHeight = DOM.getViewHeight();
            ret = utils.every(props, function(value, index) {
                if (viewHeight - rect[value] <= 0) {
                    return true;
                }
            });
            if (ret) {
                return false;
            }

            return true;
        }
    },

    getElementsInView: function(tagName) {
        var eles;
        if (typeof tagName == 'string') {
            eles = doc.getElementsByTagName(tagName);
        } else {
            eles = tagName;
        }

        var tmp = [];

        try {
            tmp = Array.prorotype.slice.call(eles);
        } catch(e) {
            var len = eles.length;
            // TODO: test reverse speed and unshift
            while (len--) {
                tmp.push(eles[len]);
            }
            tmp.reverse();
        }

        eles = utils.filter(tmp, function(ele, key) {
            if (DOM.isInView(ele)) {
                return true;
            }
        });

        return eles;
    },

    getElementPosition: function(ele) {
        var ele_rect = ele.getBoundingClientRect(ele);

        return {
            top : DOM.getDocScrollTop() + ele_rect.top,
            left: DOM.getDocScrollLeft() + ele_rect.left 
        };
    },

    getDocScrollTop: function() {
        return doc.documentElement.scrollTop || doc.body.scrollTop;
    },

    getDocScrollLeft: function() {
        return doc.documentElement.scrollLeft || doc.body.scrollLeft;
    },

    getViewHeight: function() {
        var height = window.innerHeight;
            
        if (typeof height == 'undefined') {
            height = isStrictMode ? doc.documentElement.clientHeight : doc.body.clientHeight;
        }

        return height;
    },

    getViewWidth: function() {
        // window.innerWidth 包含滚动条
        return isStrictMode ? doc.documentElement.clientWidth : doc.body.clientWidth;
    },

    getDocHeight: function() {
        return Math.max(doc.documentElement.scrollHeight, doc.body.scrollHeight);
    },

    addStyleSheet: function(clsText, attrs) {
        var style = doc.createElement('style');

        style.type = 'text/css';
        if (style.styleSheet) {
            style.styleSheet.cssText = clsText;
        } else {
            var rules = doc.createTextNode(clsText);
            style.appendChild(rules);
        }

        for (var p in attrs) {
            if (attrs.hasOwnProperty(p)) {
                style.setAttribute(p, attrs[p]);
            }
        }

        doc.body.appendChild(style);
    }
};
})();

// like underscore
var utils = (function() {
    var arrayProto = Array.prototype;

    var nativeIndexOf = arrayProto.indexOf,
        nativeForEach = arrayProto.forEach,
        nativeMap     = arrayProto.map,
        nativeFilter  = arrayProto.filter,
        nativeEvery   = arrayProto.every,
        nativeTrim    = String.prototype.trim;

    var _ = {};

    _.indexOf = function(array, item) {
        if (array == null) {
            return -1;
        }

        if (nativeIndexOf && nativeIndexOf === array.indexOf) {
            return array.indexOf(item);
        } else {
            for (var i = 0, len = array.length; i < len; ++i) {
                if (item === array[i]) {
                    return i;
                }
            }

            return -1;
        }
    };

    _.in_array = function(item, array) {
        return _.indexOf(array, item) === -1 ? false : true;
    };

    _.forEach = function(obj, iterator, context) {
        if (obj == null) {
            return;
        }

        if (nativeForEach && nativeForEach === obj.forEach) {
            obj.forEach(iterator, context);
        } else if (obj instanceof Array) {
            for (var i = 0, len = obj.length; i < len; ++i) {
                if (iterator.call(context, obj[i], i, obj) === false) {
                    return;
                }
            }
        } else {
            for (var key in obj) {
                if (obj.hasOwnProperty(key)) {
                    if (iterator.call(context, obj[key], key, obj) === false) {
                        return;
                    }
                }
            }
        }
    };

    _.map = function(obj, iterator, context) {
        if (obj == null) {
            return;
        }

        if (nativeMap && nativeMap === obj.map) {
            return obj.map(iterator, context);
        } else {
            var results = obj instanceof Array ? [] : {};
            _.forEach(obj, function(value, key, list) {
                if (results instanceof Array) {
                    results.push(iterator.call(context, value, key, list));
                } else {
                    results[key] = iterator.call(context, value, key, list);
                }
            });

            return results;
        }
    };

    _.filter = function(obj, iterator, context) {
        if (obj == null) {
            return;
        }

        if (nativeFilter && nativeFilter === obj.filter) {
            return obj.filter(iterator, context);
        } else {
            var results = (obj instanceof Array) ? [] : {};

            utils.forEach(obj, function(value, index, list) {
                if (iterator.call(context, value, index, list)) {
                    if (results instanceof Array) {
                        results.push(value);
                    } else {
                        results[index] = value;
                    }
                }
            });

            return results;
        }
    };

    _.every = function(obj, iterator, context) {
        if (obj == null) {
            return true;
        }

        if (nativeEvery && nativeEvery == obj.every) {
            return obj.every(iterator, context);
        } else {
            var ret = true;
            utils.forEach(obj, function(value, index, list) {
                if (!(ret = ret && iterator.call(context, value, index, list))) {
                    return false;
                }
            });

            return ret;
        }
    };

    _.isEmptyObject = function(obj) {
        var isEmptyObject = true;

        for (var p in obj) {
            if (obj.hasOwnProperty(p)) {
                isEmptyObject = false;
                break;
            }
        }

        return isEmptyObject;
    };

    _.trim = function(str) {
        var TRIM_REG = /^\s+|\s+$/g;

        str = String(str);
        if (nativeTrim && nativeTrim === str.trim) {
            return str.trim(str);
        } else {
            return str.replace(TRIM_REG, '');
        }
    };

    _.upperFirst = function(str) {
        str = String(str);
        return str.charAt(0).toUpperCase() + str.substr(1);
    };

    return _;
})();


// 便于功能模块的增加
var V = (function() {
    var ids = [],
        modules = [];

    var getModule = function(module) {
        return typeof module === 'function' ? module() : module;
    },
    add = function(type, module, id) {
        module = getModule(module);
        module.type = type;

        ids.push(id);
        modules.push(module);
    };

    return {
        addKeydown: function(id, module) {
            add('keydown', module, id);
        },
        addKeypress: function (id, module) {
            add('keypress', module, id);
        },
        addKeyup: function (id, module) {
            add('keyup', module, id);
        },

        /**
         * @param blackList {Array}
         */
        init: function (blackList) {
            blackList = blackList || [];
            for (var i = 0, len = ids.length; i < len; ++i) {
                if (!utils.in_array(ids[i]), blackList) {
                    S.addActions(modules[i]);
                    
                    logger.log('[V::init], add action: "' + ids[i] +'"');
                }
            }
        }
    };
})();

var CONSTANTS = {
    SCROLL_STEP: 200,
    FIND_STYLE: {
        STYLE_ID: 'vimlike:findStyleId',
        STYLE: '.vimlike-shortcuts-found-tag{position:absolute;z-index:99999;background-color:yellow;color:black;padding:0 1px;border:solid 1px #E3BE23;text-decoration:none;font:bold 12px "Helvetica Neue", "Helvetica", "Arial", "Sans";}'
    }
};
var filterByTarget = function(c, s, keyStroke) {
    return keyStroke.isValidKeyStroke();
};

V.addKeypress('srcollDown', {
    pattern: {
        value: 'j'
    },
    fns: {
        filter: filterByTarget,
        execute: function() {
            var scrollTop = $('#omrss-main').scrollTop();
            $('#omrss-main').scrollTop(scrollTop + CONSTANTS.SCROLL_STEP);
            return true;
        }
    }
});

V.addKeypress('srcollDown', {
    pattern: {
        value: ' '
    },
    fns: {
        filter: filterByTarget,
        execute: function() {
            var scrollTop = $('#omrss-main').scrollTop();
            $('#omrss-main').scrollTop(scrollTop + 3 * CONSTANTS.SCROLL_STEP);
            return true;
        }
    }
});

V.addKeypress('scrollUp', {
    pattern: {
        value: 'k'
    },
    fns: {
        filter: filterByTarget,
        execute: function() {
            var scrollTop = $('#omrss-main').scrollTop();
            $('#omrss-main').scrollTop(scrollTop - CONSTANTS.SCROLL_STEP);
            return true;
        }
    }
});

V.addKeypress('goTop', {
    pattern: {
        value: 'gg'
    },
    fns: {
        filter: filterByTarget,
        execute: function (c, keyStrokes) {
            logger.log('gotop');
            $('#omrss-main').scrollTop(0);
            return true;
        }
    }
});

V.addKeypress('goBottom', {
    pattern: {
        value: 'G'
    },
    fns: {
        filter: filterByTarget,
        execute: function () {
            var offsetHeight = $('#omrss-main')[0].scrollHeight;
            $('#omrss-main').scrollTop(offsetHeight);
            return true;
        }
    }
});

V.addKeypress('nextArticle', {
    pattern: {
        value: 'n'
    },
    fns: {
        filter: filterByTarget,
        execute: function() {
            const target = $('.ev-cnt-list.active')
            if (target.length == 0) {
                $('.ev-cnt-list')[0].click();
            }else {
                $('.ev-cnt-list.active').next().click();
            }
            return true;
        }
    }
});

V.addKeypress('prevArticle', {
    pattern: {
        value: 'p'
    },
    fns: {
        filter: filterByTarget,
        execute: function() {
            $('.ev-cnt-list.active').prev().click();
            return true;
        }
    }
});

(function() {
    var tagContainer,
        findedLinkTagPair;

    function generateTag(len) {
        var keys = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'],
            z26s = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p'],
            key_len = keys.length,
            dig_cnt = Number(len-1).toString(key_len).length;

        var tags = [],
            i = 0,
            j,
            k,
            idx,
            n26,
            tag;
        for (; i < len; ++i) {
            j = 0;
            tag = '';
            n26 = i.toString(key_len);
            while (k = n26.charAt(j++)) {
                idx = utils.indexOf(z26s, k);
                tag += keys[idx];
            }
            if (tag.length < dig_cnt) {
                tag = (new Array(dig_cnt - tag.length + 1)).join(keys[0]) + tag;
            }

            tags.push(tag);
        }

        return tags;
    }
    function filterLinks(findedLinkTagPair, currentKeyStrokes, tagContainer) {
        var suffix = currentKeyStrokes.substr(1);

        return utils.filter(findedLinkTagPair, function(pair, idx) {
            if (pair[0].indexOf(suffix) === 0) {
                return true;
            } else {
                // remove tag and link
                tagContainer.removeChild(pair[2]);
                pair[0] = pair[1] = pair[2] = null;
            }
        });
    }
    function tagEachLink(links, tagContainer) {
        var findedLinkTagPair = [],
            tags = generateTag(links.length);

        utils.forEach(links, function(link, index) {
            var ins = document.createElement('ins');
            ins.className = 'vimlike-shortcuts-found-tag'; 
            var ele_pos = DOM.getElementPosition(link);
            var cssText = 'left:' + ele_pos.left + 'px;top:' + ele_pos.top + 'px;';
            ins.style.cssText = cssText;
            var tag = tags[index];
            ins.innerHTML = tag; 
            tagContainer.appendChild(ins);

            findedLinkTagPair.push([tag, link, ins]);
        });

        // 没有样式时添加
        var FIND_STYLE = CONSTANTS.FIND_STYLE;
        if (!document.getElementById(FIND_STYLE.STYLE_ID)) {
            DOM.addStyleSheet(FIND_STYLE.STYLE, {
                id: FIND_STYLE.STYLE_ID
            });
        }
        document.body.appendChild(tagContainer);

        return findedLinkTagPair;
    }
    function click(ele, new_tab) {
        var attr_target = ele.getAttribute('target');
        if (new_tab) {
            ele.setAttribute('target', '_blank');
        }
        fireClick(ele);
        if (new_tab) {
            setTimeout(function() {
                ele.setAttribute('target', attr_target);
                ele = null;
            }, 10);
        }
    }
    function fireClick(ele) {
        // hack for so safe Firefox;
        if (/Firefox/.test(navigator.userAgent)) {
            logger.log('[fireClick], firefox, special click');
            var attr_target = ele.getAttribute('target'),
                selfOpen = true;

            if (!attr_target) {
                var base_eles = document.getElementsByTagName('head')[0].getElementsByTagName('base'),
                    i = 0,
                    len = base_eles.length;
                while (i < len) {
                    if (base_eles[i].getAttribute('target') == '_self') {
                        selfOpen = true;
                    } else {
                        selfOpen = false;
                    }
                    ++i;
                }
            } else if (attr_target == '_self') {
                selfOpen = true;
            }

            if (selfOpen) { // self tab
                window.location.href = ele.href;
            } else { // new tab
                window.open(ele.href);
            }
            return;
        }

        if (document.createEvent) {
            var evt = document.createEvent("MouseEvents");
            evt.initMouseEvent("click", true, true, window,
            0, 0, 0, 0, 0, false, false, false, false, 0, null);
            var canceled = ! ele.dispatchEvent(evt);
            if(canceled) {
                // A handler called preventDefault
                logger.log("[fireClick], canceled");
            } else {
                // None of the handlers called preventDefault
                logger.log("[fireClick], not canceled");
            }
        } else {
            ele.click();
        }
    }
    function clear() {
        try {
            document.body.removeChild(tagContainer);
        } catch (e) {}
        tagContainer = null;
        findedLinkTagPair = null;
    }

    function execute(currentKeyStroke, keyStrokes, keyStroke) {
        var links,
            keyStrokes = keyStrokes;

        if (keyStrokes.toLowerCase() == 'f') { // 'f' 编号
            links = document.links;
            links = DOM.getElementsInView(links);

            tagContainer = document.createElement('div');
            links = tagEachLink(links, tagContainer);
            findedLinkTagPair = links;

            if (links.length == 0) {
                return true;
            }

            return;
        } else { // 筛选
            findedLinkTagPair = filterLinks(findedLinkTagPair, keyStrokes, tagContainer); // 过滤 & 更新 tag
            links = findedLinkTagPair;
        }

        var len = links.length;
        if (len > 1) {
            return;
        } else if (len === 1){
            click(links[0][1], true);
            clear();
        }

        return true;
    }

    var finderFactory = function(pattern) {
        return {
            type: pattern,
            pattern: {
                isRegExp: true,
                value: pattern
            },
            fns: {
                filter: filterByTarget,
                execute: execute
            }
        };
    };
    V.addKeypress('findf', finderFactory('^f.*'));
    V.addKeyup('clearFind', {
        fns: {
            filter: function (c, s, keyStroke) {
                return keyStroke.isEscape();
            },
            execute: function() {
                clear();
                // fix ie6/7 blur when hit escape
                window.focus();
                return true;
            }
        }
    });
})();


(function() {
function blurElements() {
    if (document.activeElement) {
        try {
            document.activeElement.blur();
        } catch(e) {}
    }
    blurFocus(document.getElementsByTagName('input'));
    blurFocus(document.getElementsByTagName('textarea'));
}
function blurFocus(eles) {
    for (var i = 0,len = eles.length; i < len; ++i) {
        try {
            eles[i].blur();
        } catch(e){}
    }
}

V.addKeyup('blur', {
    fns: {
        filter: function (c, s, keyStroke) {
            return keyStroke.isEscape();
        },
        execute: function(c, s, keyStroke) {
            blurElements();

            window.focus();
            return true;
        }
    }
});

})();


var vimlikeStateMgr = (function() {
    var vimlike_binded = false;

    return {
        isOn: function() {
            return vimlike_binded;
        },
        setOn: function() {
            vimlike_binded = true;
            S.bindEvents(['keypress', 'keyup']);
        },
        setOff: function() {
            vimlike_binded = false;
            S.unBindEvents(['keypress', 'keyup']);
        },
        toggle: function() {
            vimlike_binded ? 
                vimlikeStateMgr.setOff() :
                vimlikeStateMgr.setOn();
        }
    }
})();

function extractAPI() {
    S.toggleVimlike = vimlikeStateMgr.toggle;
    S.isVimlikeOn   = vimlikeStateMgr.isOn;
}
 
function init() {
    V.init();
    vimlikeStateMgr.setOn();
    extractAPI()
}

init();
})(this.shortcuts);
