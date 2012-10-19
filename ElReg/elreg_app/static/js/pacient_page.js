$(document).ready(function () {

//    Проверка чекбокса "Согласие..."
    $ ('#confirm').click(function() {
        if($('#confirm').is(':checked')==true){
            $('#button-submit').prop('disabled', false).attr('class', 'sendsubmityes');
        }
        else{
            $('#button-submit').prop('disabled', true).attr('class', 'sendsubmit');
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
    $('#chb').click(function() {
        document.getElementById('email').disabled=(this.checked!=true);
        document.getElementById('email').value='';
        document.getElementById('email').focus();
        });
  $('#pacient_form').submit(function() {
    var $lastName = $('#lastName');
    var $firstName = $('#firstName');
    var $patromymic = $('#patronymic');
    var $dd = $('#dd');
    var $mm = $('#mm');
    var $yy = $('#yy');
    var $policy2 = $('#policy2');
    var $email = $('#email');
      if (!$lastName.val()) {
          $('#note1').hide();
          $('<span id="note1"><strong> Введите фамилию</strong></span>').fadeIn('slow').insertAfter($lastName);
          $lastName.focus();
          return false;
      }
      else {
          $('#note1').hide();
      }
      if (!$firstName.val()) {
          $('#note2').hide();
          $('<span id="note2"><strong> Введите имя</strong></span>').fadeIn('slow').insertAfter($firstName);
          $firstName.focus();
          return false;
      }
      else {
          $('#note2').hide();
      }
      if (!$patromymic.val()) {
          $('#note3').hide();
          $('<span id="note3"><strong> Введите отчество</strong></span>').fadeIn('slow').insertAfter($patromymic);
          $patromymic.focus();
          return false;
      }
      else {
          $('#note3').hide();
      }
      if (!$dd.val() || !$mm.val() || !$yy.val()) {
          $('#note4').hide();
          $('<span id="note4"><strong> Введите полностью дату рождения</strong></span>').fadeIn('slow').insertAfter($yy);
          $patromymic.focus();
          return false;
      }
      else {
          $('#note4').hide();
      }
      if (!$policy2.val()) {
          $('#note5').hide();
          $('<span id="note5"><strong> Введите номер полиса</strong></span>').fadeIn('slow').insertAfter($policy2);
          $policy2.focus();
          return false;
      }
      else {
          $('#note5').hide();
      }
      if ($email.val()) {
          $('#note6').hide();
          var regex = /^([A-Za-z0-9_\-\.])+\@([A-Za-z0-9_\-\.])+\.([A-Za-z]{2,4})$/;
          if(!regex.test($email.val())){
          $('<span id="note6"><strong> Введите корректно email</strong></span>').fadeIn('slow').insertAfter($email);
          $email.focus();
              return false;
          }
      }
      else {
          $('#note6').hide();
      }
    return true;
  })
});
