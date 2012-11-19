jQuery.support.cors = true;

$(document).ready(function () {
    $('a.spec').live("click", function() {
        $(this).closest('ul').children('li').removeClass('active');
//        $('.specActive').removeClass('specActive').addClass('spec');
        $(this).closest('li').addClass('active');
        var $clickSpec = this.id;
        var $value = $(this).text();
        $('ul.secondTable').html("");
        $('ul.thirdTable').html("");
        $.ajax({
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
            }
        });
    });

    $('a.prof').live("click", function() {
        $(this).closest('ul').children('li').removeClass('active');
//        $('.specActive').removeClass('specActive').addClass('spec');
        $(this).closest('li').addClass('active');
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
//                сортировка третьего столбца на странице Подраздеелние:
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
                    $items.push('<li><a href="/time/' + val.uid + '/">' + val.name + '</a></li>');
                });
                $('ul.thirdTable').html($($items.join('')).fadeIn('fast'));
                $('body,html').animate({
                    scrollTop: 0
                }, 300);
            }
        });
    });
});
$(document).ready(function () {

//    Проверка чекбокса "Согласие..."
    $ ('#confirm').click(function() {
        $('#button-submit').toggleClass('disabled');
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
        var $policy2 = $('#policy2');
        var $email = $('#email');
        if (!$lastName.val()) {
            $('#lastName').closest('.control-group').removeClass('success').addClass('error');
            if($('#note1')){
                $('#note1').hide();
            }
            $('<span class="help-inline" id="note1">Введите фамилию</span>').fadeIn('slow').insertAfter($lastName);
            $lastName.focus();
            return false;
        }else {
            if($('#note1')){
                $('#note1').hide();
            }
            $('#lastName').closest('.control-group').removeClass('error').addClass('success');
        }
        if (!$firstName.val()) {
            $('#firstName').closest('.control-group').removeClass('success').addClass('error');
            if($('#note2')){
                $('#note2').hide();
            }
            $('<span class="help-inline" id="note2">Введите имя</span>').fadeIn('slow').insertAfter($firstName);
            $firstName.focus();
            return false;
        }else {
            if($('#note2')){
                $('#note2').hide();
            }
            $('#firstName').closest('.control-group').removeClass('error').addClass('success');
        }
        if (!$patronymic.val()) {
            $('#patronymic').closest('.control-group').removeClass('success').addClass('error');
            if($('#note3')){
                $('#note3').hide();
            }
            $('<span class="help-inline" id="note3">Введите отчество</span>').fadeIn('slow').insertAfter($patronymic);
            $patromymic.focus();
            return false;
        }else {
            if($('#note3')){
                $('#note3').hide();
            }
            $('#patronymic').closest('.control-group').removeClass('error').addClass('success');
        }
        if (!$dd.val() || !$mm.val() || !$yy.val()) {
            $('#dd').closest('.control-group').removeClass('success').addClass('error');
            if($('#note4')){
                $('#note4').hide();
            }
            $('<span class="help-inline" id="note4">Введите полностью дату рождения</span>').fadeIn('slow').insertAfter($yy);
            $dd.focus();
            return false;
        }
        else {
            if($('#note4')){
                $('#note4').hide();
            }
            $('#dd').closest('.control-group').removeClass('error').addClass('success');
        }
        if(!$('#radio1').is(":checked") && !$('#radio2').is(":checked")){
            $('#radio1').closest('.control-group').removeClass('success').addClass('error');
            if($('#note5')){
                $('#note5').hide();
            }
            $('#radio1').closest('.controls').append( $('<span class="help-inline" id="note5">Выберите пол</span>').fadeIn('slow') );
            return false;
        }else{
            if($('#note5')){
                $('#note5').hide();
            }
            $('#radio1').closest('.control-group').removeClass('error').addClass('success');
        }
        if (!$policy2.val()) {
            $('#policy2').closest('.control-group').addClass('error');
            if($('#note6')){
                $('#note6').hide();
            }
            $('<span class="help-inline" id="note6">Введите номер полиса</span>').fadeIn('slow').insertAfter($policy2);
            $policy2.focus();
            return false;
        }else {
            if($('#note6')){
                $('#note6').hide();
            }
            $('#policy2').closest('.control-group').removeClass('error').addClass('success');
        }
        if ($email.val()) {
            $('#email').closest('.control-group').removeClass('success').addClass('error');
            if($('#note7')){
                $('#note7').hide();
            }
            var regex = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
            if(!regex.test($email.val())){
                $('<span class="help-inline" id="note6">Введите корректно email</span>').fadeIn('slow').insertAfter($email);
                $email.focus();
                return false;
            }
        } else {
            if($('#note7')){
                $('#note7').hide();
            }
            $('#email').closest('.control-group').removeClass('error').addClass('success');
        }
        return true;
    })
});