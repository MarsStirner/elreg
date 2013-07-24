jQuery.support.cors = true;

$(document).ready(function () {

    var jqXHR = [];

    function abort_ajax(){
        for (var i in jqXHR){
            jqXHR[i].abort();
        }
    }

    function spec_handler() {
        abort_ajax();
        $('a.spec').off("click", spec_handler);
        $(this).closest('ul').children('li').removeClass('active');
//        $('.specActive').removeClass('specActive').addClass('spec');
        $(this).closest('li').addClass('active');
        var $clickSpec = this.id;
        var $value = $(this).text();
        $('ul.secondTable').html("");
        $('ul.thirdTable').html("");
        jqXHR.push($.ajax({
            url: '/updates/',
            data: {clickSpec: $clickSpec, value: $value},
            crossDomain: true,
            cache: false, // обязательно для IE
            dataType: 'json',
            success: function (data) {
                var $items = [];
                $.each(data, function(key, val) {
                    $items.push('<li><a class="prof" href="javascript:;">' + val + '</a></li>');
                });
                $('ul.secondTable').html($($items.join('')).fadeIn('fast'));
                $('body,html').animate({
                    scrollTop: 0
                }, 300);
                $('a.spec').on("click", spec_handler);
                $('a.prof').on("click", prof_handler);
            }
        }));
    }
    $('a.spec').on("click", spec_handler);

    function prof_handler(){
        abort_ajax();
        $(this).closest('ul').children('li').removeClass('active');
//        $('.specActive').removeClass('specActive').addClass('spec');
        $(this).closest('li').addClass('active');
        $('.profActive').removeClass('profActive').addClass('prof');
        $(this).addClass('profActive');
        var $clickProf = $(this).text();
        $('ul.thirdTable').html("");
        jqXHR.push($.ajax({
            url: '/updates/',
            data: {clickProf: $clickProf},
            crossDomain: true,
            cache: false, // обязательно для IE
            dataType: 'json',
            success: function (data) {
                var $items = [];
                $.each(data, function(key, val) {
                    $items.push('<li><a href="/time/' + val.uid + '/">' + val.name + '</a></li>');
                });
                $('ul.thirdTable').html($($items.join('')).fadeIn('fast'));
                $('body,html').animate({
                    scrollTop: 0
                }, 300);
            }
        }));
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
    $('#chb').click(function() {
        document.getElementById('email').disabled=(this.checked!=true);
        document.getElementById('email').value='';
        document.getElementById('email').focus();
    });
    $('#patient_form').submit(function() {
        var $lastName = $('#lastName');
        var $firstName = $('#firstName');
        var $patronymic = $('#patronymic');
        var $dd = $('#dd');
        var $mm = $('#mm');
        var $yy = $('#yy');
        var $policy1 = $('#policy1');
        var $policy2 = $('#policy2');
        var $email = $('#email');
        if (!$lastName.val()) {
            $('#lastName').closest('.control-group').removeClass('success').addClass('error');
            if($('#note1')){
                $('#note1').remove();
            }
            $('<span class="help-inline" id="note1">Введите фамилию</span>').fadeIn('slow').insertAfter($lastName);
            $lastName.focus();
            return false;
        }else {
            if($('#note1')){
                $('#note1').remove();
            }
            $('#lastName').closest('.control-group').removeClass('error').addClass('success');
        }
        if (!$firstName.val()) {
            $('#firstName').closest('.control-group').removeClass('success').addClass('error');
            if($('#note2')){
                $('#note2').remove();
            }
            $('<span class="help-inline" id="note2">Введите имя</span>').fadeIn('slow').insertAfter($firstName);
            $firstName.focus();
            return false;
        }else {
            if($('#note2')){
                $('#note2').remove();
            }
            $('#firstName').closest('.control-group').removeClass('error').addClass('success');
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
        if(!$('#radio1').is(":checked") && !$('#radio2').is(":checked")){
            $('#radio1').closest('.control-group').removeClass('success').addClass('error');
            if($('#note5')){
                $('#note5').remove();
            }
            $('#radio1').closest('.controls').append( $('<span class="help-inline" id="note5">Выберите пол</span>').fadeIn('slow') );
            return false;
        }else{
            if($('#note5')){
                $('#note5').remove();
            }
            $('#radio1').closest('.control-group').removeClass('error').addClass('success');
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
        if (!$('#captcha_1').val()){
            $('#captcha_1').closest('.control-group').removeClass('success').addClass('error');
            if($('#note8')){
                $('#note8').remove();
            }
            $('<span class="help-inline" id="note8">Введите результат выражения</span>').fadeIn('slow').insertAfter($('#captcha_1'));
            $('#captcha_1').focus();
            return false;
        } else {
            if($('#note8')){
                $('#note8').remove();
            }
            $('#captcha_1').closest('.control-group').removeClass('error').addClass('success');
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
            comment['series'] = 'серию';
            comment['number'] = 'номер';
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
    });
});
