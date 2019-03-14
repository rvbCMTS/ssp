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
        responsive: true,
    } );

    var table = $("#idExamsTable").DataTable( {

        paging: false,
        searching: false,
        responsive: true,

        ajax: ({
            type: "GET",
            url: $("#idPopulateExams").html(),
            dataType: 'json',
            success: function(data) {
                table.clear().rows.add(data.data).draw();
            }
        }),

        columns: [
                {
                className: "details-control",
                orderable: false,
                data: null,
                defaultContent: ''
                },
                { data: 0 },
                { data: 1 },
                { data: 2 }
              ],

        order: ([1, 'asc']),

    });

    // Add event listener for opening and closing details
    $('#idExamsTable tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );

        if ( row.child.isShown() ) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child(
            $(
                '<tr>'+
                    '<td></td>'+
                    '<td>'+row.data()[1]+'</td>'+
                    '<td>'+row.data()[2]+'</td>'+
                '</tr>'
            )
            ).show();
            tr.addClass('shown');
        }
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

