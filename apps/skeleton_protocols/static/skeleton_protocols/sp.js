// Styling dataTable
$(document).ready(function() {
    $("#idResultTable").DataTable( {
        paging: false,
        searching: false,
    } );

});

// Filter
$("#form").change(function () {
    console.log( $(this).val() );

    $.ajax({
        type: "GET",
        url: $("#idUpdateResults").html(),
        dataType: 'json',
        data : $("#form").serialize(),
        success: function(data) {
            var table = $("#idResultTable").DataTable();
            table.clear().rows.add(data.data).draw();
        }
    });

});

// hide and show spinner animation
var $loading = $('#idLoaderRow').hide();
$(document)
  .ajaxStart(function () {
    $loading.show();
  })
  .ajaxStop(function () {
    $loading.hide();
  });

// PEX
function pexRead(){
    console.log( 'test' );

    $.ajax({
        type: "GET",
        url: $("#idPexRead").html(),
        dataType: 'json',
        data : '',
        success: function(data) {
        }
    });
}