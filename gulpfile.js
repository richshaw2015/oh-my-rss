
const { series, parallel, src, dest, watch } = require('gulp');
const concat = require('gulp-concat');
const compiler = require('gulp-closure-compiler');
const cleancss = require('gulp-clean-css');
const gulpif = require('gulp-if');
const del = require('del');

let prod = true;

function cleanTask() {
    return del([
        'assets/js/*.js',
        'assets/css/*.css',
        'assets/font/*',
    ])
}

function jsLibTask() {
    return src(['src/js/vendor/jquery.min.js', 'src/js/vendor/materialize.min.js',
        'src/js/vendor/prettydate.min.js', 'src/js/vendor/prettydate.zh-CN.min.js', 
        'src/js/vendor/uuid.js', 'src/js/vendor/md5.min.js', 'src/js/vendor/js.cookie.min.js',
        'src/js/vendor/cache.js', 'src/js/vendor/prism.js', 'src/js/vendor/highlight.min.js',
        'src/js/vendor/linkify.min.js', 'src/js/vendor/linkify-jquery.min.js'])
        .pipe(concat('lib.js'))
        .pipe(dest('assets/js'))
}

function fontTask() {
    return src('src/font/*')
        .pipe(dest('assets/font/'))
}

function jsEchartsTask() {
    return src('src/js/vendor/echarts.min.js')
        .pipe(dest('assets/js'))
}

function jsPcTask() {
    return src(['src/js/ohmyrss.js', 'src/js/pc.js', 'src/js/vimlike-shortcuts.js'])
        .pipe(gulpif(prod === true, compiler({
            compilerPath: './node_modules/google-closure-compiler/compiler.jar',
            fileName: 'pc.js',
            compilation_level: 'SIMPLE',
            compilerFlags: {
                language_in: 'ECMASCRIPT6',
                language_out: 'ES5'
            }
        })))
        .pipe(gulpif(prod === false ,concat('pc.js')))
        .pipe(dest('assets/js'))
}

function jsMobileTask() {
    return src(['src/js/ohmyrss.js', 'src/js/mobile.js'])
        .pipe(gulpif(prod === true, compiler({
            compilerPath: './node_modules/google-closure-compiler/compiler.jar',
            fileName: 'mobile.js',
            compilation_level: 'SIMPLE',
            compilerFlags: {
                language_in: 'ECMASCRIPT6',
                language_out: 'ES5'
            }
        })))
        .pipe(gulpif(prod === false ,concat('mobile.js')))
        .pipe(dest('assets/js'))
}

function cssLibTask() {
    return src('src/css/vendor/*.css')
        .pipe(concat('lib.css'))
        .pipe(cleancss())
        .pipe(dest('assets/css'))
}

function cssPcTask() {
    return src('src/css/pc.css')
        .pipe(cleancss())
        .pipe(dest('assets/css'))
}

function cssMobileTask() {
    return src('src/css/mobile.css')
        .pipe(cleancss())
        .pipe(dest('assets/css'))
}

exports.build = series(
    cleanTask,
    jsEchartsTask, fontTask, 
    jsLibTask, cssLibTask,
    parallel(cssMobileTask, cssPcTask),
    parallel(jsPcTask, jsMobileTask),
);

exports.default = function() {
    prod = false;
    watch(['src/js/*.js'], parallel(jsPcTask, jsMobileTask));
    watch(['src/css/*.css'], parallel(cssMobileTask, cssPcTask));
};

exports.clean = series(cleanTask)
