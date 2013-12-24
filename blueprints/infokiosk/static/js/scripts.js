$(document).ready(function () {

//    Проверка данных в формах
    $('#dd').keypress(function(event) {
        if (event.which && (event.which < 48 || event.which > 57) && (event.which != 8)) {
            event.preventDefault();
        }
    });
    $('#mm').keypress(function(event) {
        if (event.which && (event.which < 48 || event.which > 57) && (event.which != 8)) {
            event.preventDefault();
        }
    });
    $('#yy').keypress(function(event) {
        if (event.which && (event.which < 48 || event.which > 57) && (event.which != 8)) {
            event.preventDefault();
        }
    });
    $('#client_id').keypress(function(event) {
        if (event.which && (event.which < 48 || event.which > 57) && (event.which != 8)) {
            event.preventDefault();
        }
    });

});
function show_doc_fields(doc_type){
    $('.doc_div').addClass('hidden');
    if (doc_type){
        $('.' + doc_type).removeClass('hidden');
        $('.doc_div').find('input').attr("disabled","disabled");
        $('.' + doc_type).find('input').removeAttr("disabled");
    }
}