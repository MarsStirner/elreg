$(document).ready(function () {

//    Проверка данных в формах
    $('#dd').keypress(function(event) {
        if (event.which && (event.which < 48 || event.which > 57) && (event.which != 8)) {
            event.preventDefault();
        }
    });
    $('#dd').keyup(function(event) {
        if ($('#dd').val().length == 2){
            $('#mm').focus();
        }
    });
    $('#mm').keypress(function(event) {
        if (event.which && (event.which < 48 || event.which > 57) && (event.which != 8)) {
            event.preventDefault();
        }
    });
    $('#mm').keyup(function(event) {
        if ($('#mm').val().length == 2){
            $('#yy').focus();
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
$(document).ready(function(){
    $('select#doc_type_selector').change(function(){
        $('.doc_div').addClass('hidden');
        if ($(this).val()){
            $('.' + $(this).val()).removeClass('hidden');
            $('.doc_div').find('input').attr("disabled","disabled");
            $('.' + $(this).val()).find('input').removeAttr("disabled");
        }
        show_doc($(this).val());
    });
});
