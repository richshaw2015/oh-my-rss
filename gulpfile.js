
const { series, parallel, src, dest, watch } = require('gulp');
const concat = require('gulp-concat');
const compiler = require('gulp-closure-compiler');
const cleancss = require('gulp-clean-css');
const gulpif = require('gulp-if');

let prod = true;


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

exports.build = series(jsEchartsTask, fontTask, 
    jsLibTask, cssLibTask,
    parallel(cssMobileTask, cssPcTask),
    parallel(jsPcTask, jsMobileTask),
);

exports.default = function() {
    // prod = false;
    watch(['src/js/*.js'], parallel(jsPcTask, jsMobileTask));
    watch(['src/css/*.css'], parallel(cssMobileTask, cssPcTask));
};
