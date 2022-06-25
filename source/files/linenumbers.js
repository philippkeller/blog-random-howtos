$(document).ready(function() {
    setTimeout(function() {
        $('code.hljs').each(function(i, block) {
            hljs.lineNumbersBlock(block);
        });
    }, 500);
});
