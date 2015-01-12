function isMobile(){if(/android|blackberry|iphone|ipad|ipod|iemobile|wap|mobile/i.test(navigator.userAgent.toLowerCase())){return true;}else{return false;}}
$(function(){
    $("#find-sth a").click(function(){
        var wclicked = $(this);

        var action = (wclicked.attr('data-search-type'));

        $("#find-sth").attr("action", action );
        $("#find-sth input").attr("placeHolder", "找找看("+wclicked.text()+")");

    })
});
