$(function() {
    $("#account-sidebar-toggler").click(function(){
        $("#account-sidebar")
            .sidebar({
                overlay: true
            })
            .sidebar('toggle')
        ;
        $("#account-sidebar-toggler").toggleClass('active');
    });
    $(".ui.accordion").accordion();
    $(".ui.dropdown").dropdown();
    $(".tip.button").popup({
        on: 'hover'
    });
    $(".ui.checkbox").checkbox();

});


String.prototype.encodeHtml = function () {
    var str = this;   
    var s = "";   
    if (str.length == 0) return "";   
    s = str.replace(/&/g, "&gt;");   
    s = s.replace(/</g, "&lt;");   
    s = s.replace(/>/g, "&gt;");   
    s = s.replace(/ /g, "&nbsp;");   
    s = s.replace(/\'/g, "&#39;");   
    s = s.replace(/\"/g, "&quot;");   
    s = s.replace(/\n/g, "<br>");   
    return s;   
}   