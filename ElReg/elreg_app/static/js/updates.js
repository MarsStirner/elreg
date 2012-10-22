$(document).ready(function () {
    $('a.spec').live("click", function() {
        var $clickSpec = this.id;
        var $value = $(this).text();
        $('table.secondTable tr').hide();
        $('table.thirdTable tr').hide();
        $.getJSON("/updates/", {clickSpec: $clickSpec, value: $value}, function(data) {
            var $items = [];
            $.each(data, function(key, val) {
                $items.push('<tr><td><a class="prof">' + val + '</a></td></tr>');
            });
            $($items.join('')).fadeIn('fast').appendTo('table.secondTable');
        $('body,html').animate({
            scrollTop: 0
        }, 300);
        });
    });

    $('a.prof').live("click", function() {
        var $clickProf = $(this).text();
        $('table.thirdTable tr').hide();
        $.getJSON("/updates/", {clickProf: $clickProf}, function(data) {
            var $items = [];
            $.each(data, function(key, val) {
                $items.push('<tr><td><a href="/time/' + key + '"/">' + val + '</a></td></tr>');
            });
            $($items.join('')).fadeIn('fast').appendTo('table.thirdTable');
            $('body,html').animate({
                scrollTop: 0
            }, 300);
        });
    });
});
