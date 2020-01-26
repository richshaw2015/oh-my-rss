
const { gulp, series, parallel, src, dest } = require('gulp');
const concat = require('gulp-concat');
const compiler = require('gulp-closure-compiler');
const cleancss = require('gulp-clean-css');

function jsLibTask() {
    return src('src/js/vendor/*.js', {ignore: 'src/js/vendor/echarts.min.js'})
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
        .pipe(compiler({
            compilerPath: './node_modules/google-closure-compiler/compiler.jar',
            fileName: 'pc.js',
            compilation_level: 'SIMPLE',
            compilerFlags: {
                language_in: 'ECMASCRIPT6',
                language_out: 'ES5'
            }
        }))
        .pipe(dest('assets/js'))
}

function jsMobileTask() {
    return src(['src/js/ohmyrss.js', 'src/js/mobile.js'])
        .pipe(compiler({
            compilerPath: './node_modules/google-closure-compiler/compiler.jar',
            fileName: 'mobile.js',
            compilation_level: 'SIMPLE',
            compilerFlags: {
                language_in: 'ECMASCRIPT6',
                language_out: 'ES5'
            }
        }))
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

exports.default = parallel(jsEchartsTask, fontTask, jsLibTask, jsPcTask, jsMobileTask, cssLibTask, cssPcTask,
    cssMobileTask
);
