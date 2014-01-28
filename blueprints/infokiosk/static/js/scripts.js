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
function printContent(id){
        var str=document.getElementById(id).innerHTML;
        var resolution = 96;
        var width = Math.round(resolution * 8 / 2.54);
        var newwin=window.open('','printwin','left=100,top=100,width='+ width +',height=400,scrollbars=1,resizable=1');
        newwin.document.write('<HTML>\n<HEAD>\n');
        newwin.document.write('<TITLE>Print Page</TITLE>\n');
        newwin.document.write('<script>\n');
        newwin.document.write('function chkstate(){\n');
        newwin.document.write('if(document.readyState=="complete"){\n');
        //newwin.document.write('window.close()\n')
        newwin.document.write('}\n');
        newwin.document.write('else{\n');
        //newwin.document.write('setTimeout("chkstate()",2000)\n')
        newwin.document.write('}\n');
        newwin.document.write('}\n');
        newwin.document.write('function print_win(){\n');
        newwin.document.write('window.print();\n');
        newwin.document.write('chkstate();\n');
        newwin.document.write('}\n');
        newwin.document.write('<\/script>\n');
        newwin.document.write('</HEAD>\n');
        newwin.document.write('<BODY onload="print_win()">\n');
        newwin.document.write('<style>\n');
        newwin.document.write('td { font-family: "Arial Narrow"; font-size: 10pt; }\n');
        newwin.document.write('</style>\n');
        newwin.document.write(str);
        newwin.document.write('</HTML>\n');
        newwin.document.close();
    }