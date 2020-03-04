
// Styling dataTable
$(document).ready(function() {
    $("#idResultTable").DataTable( {
        paging: false,
        searching: false,
        fixedHeader: true,
        responsive: true,

        columns: [
        {"data": "exam_name"},
        {"data": "ris_name", width: '15em'},
        {"data": "machine__hospital_name"},
        {"data": "kv"},
        {"data": "sensitivity"},
        {"data": "mas"},
        {"data": "filter_cu"},
        {"data": "focus"},
        {"data": "grid"},
        {"data": "lut"},
        {"data": "diamond_view"},
        {"data": "image_amp"},
        {"data": "edge"},
        {"data": "harm"},
        {"data": "fp_set"},
        {"data": "datum"},
        {"data": "history"},
        ],

        // column 0 equal exam_name. Sorted by, group name and hidden.
        orderFixed: [[0, 'asc'], [1, 'asc']],
        rowGroup: {
            dataSrc: [ "exam_name"]
        },
        columnDefs: [
            {
                "targets": [ 0  ],
                "visible": false,
            }
        ],

    } );

    $("#idHistoryTable").DataTable( {
        paging: false,
        searching: false,
        responsive: true,

        columns: [
        {"data": "ris_name"},
        {"data": "machine__hospital_name"},
        {"data": "datum"},
        {"data": "kv"},
        {"data": "sensitivity"},
        {"data": "mas"},
        {"data": "filter_cu"},
        {"data": "focus"},
        {"data": "grid"},
        {"data": "lut"},
        {"data": "diamond_view"},
        {"data": "image_amp"},
        {"data": "edge"},
        {"data": "harm"},
        {"data": "fp_set"},
        ],

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

    const urlParams = new URLSearchParams(window.location.search);
    const pks = urlParams.getAll('pk[]');

    if (pks.length !==0){
        // ajax call for Results table
        $.ajax({
                type: "GET",
                url: $("#idUpdateResults").html(),
                dataType: 'json',
                data: {'pk': pks},
                success: function(data) {
                    var table = $("#idResultTable").DataTable();
                    table.clear().rows.add(data.data).draw();
                },
        })
    }


    var table = $("#idExamsTable").DataTable( {

        select: {
            style: 'multi',
            selector: 'td:not(:first-child)'
        },

        columns: [
            {title: '', target: 0, className: 'treegrid-control', width: '1em', data: function (item) { if (item.children) { return '<i class="fas fa-caret-right"></i>'; } return ''; }},
            {title: 'Exam / Protokoll',  width: '5em', data: function (item) { return item.fc }},
            {title: 'Modalitet',  width: '18em', data: function (item) { return item.sc }},
            {title: 'Senast ändrad',  width: '6em', data: function (item) { return item.date_latest }},
            {title: 'Pk', width: '18em', visible: false, data: function (item) { return item.pk }},
        ],

        treeGrid: {
            left : 10,
            expandIcon: '<i class="fas fa-caret-right"></i>',
            collapseIcon: '<i class="fas fa-caret-down"></i>'
        },

        order: ([1, 'asc']),

        paging: false,
        searching: true,
        responsive: false,
        fixedHeader: true,
        destroy: false,

    });


 });

// Compare button in Exam view
$('#idCompareButton').click( function () {
    var table = $("#idExamsTable").DataTable()
    var data = table.rows('.selected').data()
    var pkArray = data.map(a => a.pk);
    var pk = [].concat.apply([], pkArray)
    var queryString = Object.keys(pk).map(key => 'pk%5B%5D' + '=' + pk[key]).join('&');

    window.open($("#idCompareProtocols").html() + '?' + queryString,"_self")

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

