jQuery.support.cors = true;

$(document).ready(function () {
    $('a.spec').live("click", function() {
        $('.specActive').removeClass('specActive').addClass('spec');
        $(this).addClass('specActive');
        var $clickSpec = this.id;
        var $value = $(this).text();
        $('table.secondTable tr').hide();
        $('table.thirdTable tr').hide();
        $.ajax({
            url: '/updates/',
            data: {clickSpec: $clickSpec, value: $value},
            crossDomain: true,
            cache: false, // обязательно для IE
            dataType: 'json',
            success: function (data) {
                var $items = [];
                $.each(data, function(key, val) {
                    $items.push('<tr><td><a class="prof">' + val + '</a></td></tr>');
                });
                $($items.join('')).fadeIn('fast').appendTo('table.secondTable');
                $('body,html').animate({
                    scrollTop: 0
                }, 300);
            }
        });
    });

    $('a.prof').live("click", function() {
        $('.profActive').removeClass('profActive').addClass('prof');
        $(this).addClass('profActive');
        var $clickProf = $(this).text();
        $('table.thirdTable tr').hide();
        $.ajax({
            url: '/updates/',
            data: {clickProf: $clickProf},
            crossDomain: true,
            cache: false, // обязательно для IE
            dataType: 'json',
            success: function (data) {

////////////////////////////////////////////////////////////////////////////
//                var sortable = [];
//                for (var key in data) {
//                    alert([key]);
//                    sortable.push([key, data[key]]);
//                alert (sortable);
//                }
//                for (var i in sortable) {
//                    alert (sortable[i]);
//                }
//                sortable.sort(function(a, b) {return a[1] - b[1]});
//                alert (sortable);
////////////////////////////////////////////////////////////////////////////

                var $items = [];
//                $.each(sortable, function(key, val) {
                $.each(data, function(key, val) {
                    $items.push('<tr><td><a href="/time/' + key + '/">' + val + '</a></td></tr>');
                });
                $($items.join('')).fadeIn('fast').appendTo('table.thirdTable');
                $('body,html').animate({
                    scrollTop: 0
                }, 300);
            }
        });
    });
});
