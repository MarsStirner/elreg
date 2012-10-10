$(document).ready(function () {
    $('a.spec').live("click", function() {
        var $clickSpec = this.id;
        $.getJSON("/updates/", {clickSpec: $clickSpec}, function(data) {
            var $items = [];
            $.each(data, function(key, val) {
                $items.push('<a class="prof">' + val + '</a>');
            });
//            $('#ttt').append(data);
            $('table.secondTable').hide();
            $('<tr><td>' + $items.join('') + '</td></tr>').fadeIn('slow').appendTo('table.secondTable');
        });
    });

    $('a.prof').live("click", function() {
        var $clickProf = $(this).text();
        $.getJSON("/updates/", {clickProf: $clickProf}, function(data) {
            var $items = [];
            $.each(data, function(key, val) {
                $items.push('<a href="vremya/' + key + '"/">' + val + '</a>');
            }); // проверить адрес ссылки!!!
            $('table.thirdTable').hide();
            $('<tr><td>' + $items.join('') + '</td></tr>').fadeIn('slow').appendTo('table.thirdTable');
        });
    });
});
