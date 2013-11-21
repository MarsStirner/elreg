jQuery.support.cors = true;

$(document).ready(function () {
    var jqXHR = [];

    function abort_ajax(){
        for (var i in jqXHR){
            jqXHR[i].abort();
        }
    }

    function division_handler() {
        abort_ajax();
        $('a.division').off("click", division_handler);
        $(this).closest('ul').children('li').removeClass('active');
        $(this).closest('li').addClass('active');
        var href = $(this).attr('href');
        $('ul.secondTable').html("");
        $('ul.thirdTable').html("");
        jqXHR.push($.ajax({
            url: href,
            crossDomain: true,
            cache: false, // обязательно для IE
            dataType: 'json',
            success: function (data) {
                var str = '<li class="nav-header">Выбор мед. специализации</li>';
                if(data['result'].length > 0){
                $.each(data['result'], function(key, val) {
                    str += '<li><a class="speciality" href="' + href.replace('ajax_specialities', 'ajax_doctors') + '?sp=' + encodeURIComponent(val) + '">' + val.replace('(', '<br>(') + '</a></li>';
                });
                } else{
                    str += '<li><div class="alert alert-error">Данные по специальностям врачей выбранного подразделения отсутствуют, попробуйте зайти на страницу позже или выберите другое подразделение.</div></li>';
                }
                $('ul.secondTable').html(str);
                $('body,html').animate({
                    scrollTop: 0
                }, 300);
                $('a.division').on("click", division_handler);
                $('a.speciality').on("click", speciality_handler);
            }
        }));
        return false;
    }
    $('a.division').on("click", division_handler);

    function speciality_handler(){
        abort_ajax();
        $(this).closest('ul').children('li').removeClass('active');
//        $('.specActive').removeClass('specActive').addClass('spec');
        $(this).closest('li').addClass('active');
        $('.specialityActive').removeClass('specialityActive').addClass('speciality');
        $(this).addClass('specialityActive');
        var href = $(this).attr('href');
        $('ul.thirdTable').html("");
        jqXHR.push($.ajax({
            url: href,
            crossDomain: true,
            cache: false, // обязательно для IE
            dataType: 'json',
            success: function (data) {
                var str = '<li class="nav-header">Выбор Врача<span class="pull-right">Ближайшая свободная запись/Расписание</span></li>';
                var doctor;
                if(data.result.length > 0){
                    $.each(data.result, function(key, val) {
                        doctor = '<li class="clearfix"><a class="span7" href="' + val.schedule_href + '">' + val.name + '</a>';
                        doctor += '<div class="btn-group pull-right">';
                        if (val.tickets.length > 0){
                           doctor += '<a href="' + val.tickets[0].href + '" class="btn btn-small btn-success">' + val.tickets[0].info + '</a>';
                        }
                        doctor += '<a href="' + val.schedule_href + '" class="btn btn-small btn-warning" type="button">Расписание</a>';
                        doctor += '</div>';
                        doctor += '</li>';
                        str += doctor;
                    });
                } else {
                    str += '<li><div class="alert alert-error">Данные по врачам выбранной специальности отсутствуют, попробуйте зайти на страницу позже или выберите другую специальность.</div></li>';
                }
                $('ul.thirdTable').html(str);
                $('body,html').animate({
                    scrollTop: 0
                }, 300);
            }
        }));
        return false;
    }
});

$(document).ready(function () {

//    Проверка чекбокса "Согласие..."
    if($('#confirm').is(':checked')){
        $('#button-submit').removeClass('disabled').attr('disabled', false);
    } else {
        $('#button-submit').addClass('disabled').attr('disabled', true);
    }
    $('#confirm').click(function() {
        if($('#confirm').is(':checked')){
            $('#button-submit').toggleClass('disabled').attr('disabled', false);
        } else {
            $('#button-submit').toggleClass('disabled').attr('disabled', true);
        }
    });

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
    $('#captcha').keypress(function(event) {
        if (event.which && (event.which < 48 || event.which > 57) && (event.which != 8)) {
            event.preventDefault();
        }
    });
    $('#chb').click(function() {
        document.getElementById('email').disabled=(this.checked!=true);
        document.getElementById('email').value='';
        document.getElementById('email').focus();
    });
    $('#patient_form').submit(function() {
        var $lastname = $('#lastname');
        var $firstname = $('#firstname');
        var $patronymic = $('#patronymic');
        var $dd = $('#dd');
        var $mm = $('#mm');
        var $yy = $('#yy');
        var $policy1 = $('#policy1');
        var $policy2 = $('#policy2');
        var $email = $('#email');
        if (!$lastname.val()) {
            $('#lastname').closest('.control-group').removeClass('success').addClass('error');
            if($('#note1')){
                $('#note1').remove();
            }
            $('<span class="help-inline" id="note1">Введите фамилию</span>').fadeIn('slow').insertAfter($lastname);
            $lastname.focus();
            return false;
        }else {
            if($('#note1')){
                $('#note1').remove();
            }
            $('#lastname').closest('.control-group').removeClass('error').addClass('success');
        }
        if (!$firstname.val()) {
            $('#firstname').closest('.control-group').removeClass('success').addClass('error');
            if($('#note2')){
                $('#note2').remove();
            }
            $('<span class="help-inline" id="note2">Введите имя</span>').fadeIn('slow').insertAfter($firstname);
            $firstname.focus();
            return false;
        }else {
            if($('#note2')){
                $('#note2').remove();
            }
            $('#firstname').closest('.control-group').removeClass('error').addClass('success');
        }
        if (!$patronymic.val()) {
            $('#patronymic').closest('.control-group').removeClass('success').addClass('error');
            if($('#note3')){
                $('#note3').remove();
            }
            $('<span class="help-inline" id="note3">Введите отчество</span>').fadeIn('slow').insertAfter($patronymic);
            $patronymic.focus();
            return false;
        }else {
            if($('#note3')){
                $('#note3').remove();
            }
            $('#patronymic').closest('.control-group').removeClass('error').addClass('success');
        }
        if (!$dd.val() || !$mm.val() || !$yy.val()) {
            $('#dd').closest('.control-group').removeClass('success').addClass('error');
            if($('#note4')){
                $('#note4').remove();
            }
            $('<span class="help-inline" id="note4">Введите полностью дату рождения</span>').fadeIn('slow').insertAfter($yy);
            $dd.focus();
            return false;
        } else if ($yy.val().length<4) {
            $('#dd').closest('.control-group').removeClass('success').addClass('error');
            if($('#note4')){
                $('#note4').remove();
            }
            $('<span class="help-inline" id="note4">Введите четырёхзначное значение года рождения</span>').fadeIn('slow').insertAfter($yy);
            $yy.focus();
            return false;
        }
        else {
            if($('#note4')){
                $('#note4').remove();
            }
            $('#dd').closest('.control-group').removeClass('error').addClass('success');
        }
        if(!$('#gender-0').is(":checked") && !$('#gender-1').is(":checked")){
            $('#gender').closest('.control-group').removeClass('success').addClass('error');
            if($('#note5')){
                $('#note5').remove();
            }
            $('#gender').closest('.controls').append( $('<span class="help-inline" id="note5">Выберите пол</span>').fadeIn('slow') );
            return false;
        }else{
            if($('#note5')){
                $('#note5').remove();
            }
            $('#gender').closest('.control-group').removeClass('error').addClass('success');
        }
        if ( $('#chb').is(':checked') && $email.val()) {
            $('#email').closest('.control-group').removeClass('error').addClass('success');
            if($('#note6')){
                $('#note6').remove();
            }
            var regex = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
            if(!regex.test($email.val())){
                $('<span class="help-inline" id="note6">Введите корректно email</span>').fadeIn('slow').insertAfter($email);
                $email.focus();
                $('#email').closest('.control-group').removeClass('success').addClass('error');
                return false;
            }
        } else if($('#chb').is(':checked')) {
            if($('#note6')){
                $('#note6').remove();
            }
            $('<span class="help-inline" id="note6">Не указан email</span>').fadeIn('slow').insertAfter($email);
            $('#email').closest('.control-group').removeClass('success').addClass('error');
            return false;
        }else{
            $('#email').closest('.control-group').removeClass('error').addClass('success');
        }
        if(!$('select#doc_type_selector').val()){
            $('#doc_type_selector').closest('.control-group').removeClass('success').addClass('error');
            if($('#note9')){
                $('#note9').remove();
            }
            $('<span class="help-inline" id="note9">Выберите тип документа</span>').fadeIn('slow').insertAfter($('#doc_type_selector'));
            return false;
        } else {
            var regex = /^([0-9])+$/;

            $('#note9').remove();
            $('#note10').remove();
            $('#doc_type_selector').closest('.control-group').removeClass('error').addClass('success');

            var comment = {};
            comment['doc_series'] = 'серию';
            comment['series'] = 'серию';
            comment['policy_series'] = 'серию';
            comment['number'] = 'номер';
            comment['client_id'] = 'номер';
            comment['doc_number'] = 'номер';
            comment['policy_number'] = 'номер';
            var i=10;
            var is_valid = true;
            $('.doc_div:visible').find('input').each(function(){
                if($('#note' + i)){
                    $('#note' + i).remove();
                }
                if($(this).closest('.control-group').find('.text-error')[0] && $(this).closest('.control-group').find('.text-error')[0].innerText=='*' && !$(this).val()/* || ($(this).attr('name')=='number' && !regex.test($(this).val()))*/){
                    $(this).closest('.control-group').removeClass('success').addClass('error');
                    $('<span class="help-inline" id="note' + i + '">Введите '+ comment[$(this).attr('name')] +'</span>').fadeIn('slow').insertAfter($(this));
                    is_valid = false;
                } else {
                    $(this).closest('.control-group').removeClass('error').addClass('success');
                }
                i++;
            });
            if (!is_valid){
                return false;
            }
        }
        if (!$('#captcha').val()){
            $('#captcha').closest('.control-group').removeClass('success').addClass('error');
            if($('#note8')){
                $('#note8').remove();
            }
            $('<span class="help-inline" id="note8">Введите результат выражения</span>').fadeIn('slow').insertAfter($('#captcha'));
            $('#captcha').focus();
            return false;
        } else {
            if($('#note8')){
                $('#note8').remove();
            }
            $('#captcha').closest('.control-group').removeClass('error').addClass('success');
        }
        return true;
    })
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
function show_doc(type){
    var src_sm = "";
    var src = "";
    var $doc_example = $('#doc_example');
    $doc_example.hide();
    if (type == 'policy_type_4'){
        src_sm = $STATIC_DIR + 'i/docs/polis_sm.jpg';
        src = $STATIC_DIR + 'i/docs/polis.jpg';
    }else if (type == 'policy_type_2'){
        src_sm = $STATIC_DIR + 'i/docs/old_polis_sm.jpg';
        src = $STATIC_DIR + 'i/docs/old_polis.jpg';
    }
    $doc_example.find('img').attr('src', src_sm);
    $('#doc_example_modal').find('img').attr('src', src);
    $('#show_big_doc').click(function(){
        $('#doc_example_modal').modal();
    });
    if(src_sm){
        $doc_example.show();
    }
}
