
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

    // ajax call for ExamsTable
    $.ajax({
            type: "GET",
            url: $("#idPopulateExams").html(),
            dataType: 'json',
            success: function(data) {
                var table = $("#idExamsTable").DataTable();
                table.clear().rows.add(data.data).draw();;
            },
    })

    var table = $("#idExamsTable").DataTable( {

        'select': {
            style: 'multi',
            selector: 'td:not(:first-child)'
        },

        'columns': [
            {title: '', target: 0, className: 'treegrid-control', width: '1em', data: function (item) { if (item.children) { return '<i class="fas fa-caret-right"></i>'; } return ''; }},
            {title: 'Exam / Protokoll', target: 1,  width: '5em', data: function (item) { return item.exam_name }},
            {title: 'Modalitet', target: 2, width: '18em', data: function (item) { return item.machine }},
        ],

        'treeGrid': {
            left : 10,
            expandIcon: '<i class="fas fa-caret-right"></i>',
            collapseIcon: '<i class="fas fa-caret-down"></i>'
        },

        'order': ([1, 'asc']),

        'paging': false,
        'searching': true,
        'responsive': false,
        'fixedHeader': true,
        'destroy': false,

    });

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

