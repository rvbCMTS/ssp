// Styling dataTable
$(document).ready(function() {
    $("#idResultTable").DataTable( {
        paging: false,
        searching: false,
        fixedHeader: true,
        responsive: true,

        // column 0 equal exam_name. Sorted by, group name and hidden.
        orderFixed: [0, 'asc'],
        rowGroup: {
            dataSrc: 0
        },
        "columnDefs": [
            {
                "targets": [ 0 ],
                "visible": false,
            }
        ]
    } );

    $("#idHistoryTable").DataTable( {
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

    $.ajax({
        type: "GET",
        url: $("#idPexRead").html(),
        dataType: 'json',
        data : '',
        success: function(data) {
        }
    });
}

// History
function viewHistory(pk){
    $('#idHistoryRow').removeClass('hidden');

    $.ajax({
        type: "GET",
        url: $("#idViewHistory").html(),
        dataType: 'json',
        data : {'pk': pk},
        success: function(data) {
            var table = $("#idHistoryTable").DataTable();
            table.clear().rows.add(data.data).draw();
        }
    });

}

function closeHistory(){
    $('#idHistoryRow').addClass('hidden');
}