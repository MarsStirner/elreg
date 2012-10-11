$(document).ready(function () {
//    $('table.secondTable').hide();
//    $('table.thirdTable').hide();
    $('a.spec').live("click", function() {
        var $clickSpec = this.id;
        $('table.secondTable tr').hide();
        $('table.thirdTable tr').hide();
        $.getJSON("/updates/", {clickSpec: $clickSpec}, function(data) {
            var $items = [];
            $.each(data, function(key, val) {
                $items.push('<tr><td><a class="prof">' + val + '</a></td></tr>');
            });
//            $('#ttt').append(data);
            $($items.join('')).fadeIn('fast').appendTo('table.secondTable');
        });
    });

    $('a.prof').live("click", function() {
        var $clickProf = $(this).text();
        $('table.thirdTable tr').hide();
        $.getJSON("/updates/", {clickProf: $clickProf}, function(data) {
            var $items = [];
            $.each(data, function(key, val) {
                $items.push('<tr><td><a href="/vremya/' + key + '"/">' + val + '</a></td></tr>');
            });
            $($items.join('')).fadeIn('fast').appendTo('table.thirdTable');
        });
    });
});
