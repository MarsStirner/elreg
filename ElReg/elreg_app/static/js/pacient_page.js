$(document).ready(function () {

    $('#dd').keypress(function(event) {
        if (event.which && (event.which < 48 || event.which > 57) && (event.which != 08)) {
            event.preventDefault();
        }
    });

    $('#mm').keypress(function(event) {
        if (event.which && (event.which < 48 || event.which > 57) && (event.which != 08)) {
            event.preventDefault();
        }
    });

    $('#yy').keypress(function(event) {
        if (event.which && (event.which < 48 || event.which > 57) && (event.which != 08)) {
            event.preventDefault();
        }
    });

    $('#chb').click(function() {
        document.getElementById('email').disabled=(this.checked==true)?false:true;
        document.getElementById('email').value='';
        document.getElementById('email').focus();
        });

  $('#pacient_form').submit(function() {
    var $lastName = $('#lastName');
    var $firstName = $('#firstName');
    var $patromymic = $('#patronymic');
    var $email = $('#email');

      if (!$lastName.val()) {
          $('#note1').hide();
          $('<ol id="note1">Введите фамилию</ol>').fadeIn('slow').insertAfter($lastName);
          $lastName.focus();
          return false;
      }
      else {
          $('#note1').hide();
      }

      if (!$firstName.val()) {
          $('#note2').hide();
          $('<ol id="note2">Введите имя</ol>').fadeIn('slow').insertAfter($firstName);
          $firstName.focus();
          return false;
      }
      else {
          $('#note2').hide();
      }

      if (!$patromymic.val()) {
          $('#note3').hide();
          $('<ol id="note3">Введите отчество</ol>').fadeIn('slow').insertAfter($patromymic);
          $patromymic.focus();
          return false;
      }
      else {
          $('#note3').hide();
      }

    return true;
  })

});



