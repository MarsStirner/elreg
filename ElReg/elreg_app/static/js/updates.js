$(document).ready(function () {
    $('#rrr').click(function() {
        $.getJSON("/updates/", function(data) {
            $.each(data, function(entryIndex, entry) {
                var html = '<div class="ht"';
                html += '<h3>' + entry['pk'] + '</h3>';
                if (entry['fields']) {
                    $.each(entry['fields'], function(lineIndex, line) {
//                        if (lineIndex == "1") {
                            html += '<p><a>' + line + '</a></p>'
//                        }
                    });
                }
                html += '</div>';
                $('#ttt').append(html);
            })
        });
    });
});