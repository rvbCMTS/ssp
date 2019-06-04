$(document).ready(function() {
    // UMD
    (function( factory ) {
        "use strict";

        if ( typeof define === 'function' && define.amd ) {
            // AMD
            define( ['jquery'], function ( $ ) {
                return factory( $, window, document );
            } );
        }
        else if ( typeof exports === 'object' ) {
            // CommonJS
            module.exports = function (root, $) {
                if ( ! root ) {
                    root = window;
                }

                if ( ! $ ) {
                    $ = typeof window !== 'undefined' ?
                        require('jquery') :
                        require('jquery')( root );
                }

                return factory( $, root, root.document );
            };
        }
        else {
            // Browser
            factory( jQuery, window, document );
        }
    }
    (function( $, window, document ) {


    $.fn.dataTable.render.moment = function ( from, to, locale ) {
        // Argument shifting
        if ( arguments.length === 1 ) {
            locale = 'en';
            to = from;
            from = 'YYYY-MM-DD';
        }
        else if ( arguments.length === 2 ) {
            locale = 'en';
        }

        return function ( d, type, row ) {
            var m = window.moment( d, from, locale, true );

            // Order and type get a number value from Moment, everything else
            // sees the rendered value
            return m.format( type === 'sort' || type === 'type' ? 'x' : to );
        };
    };


    }));

    $("#productionTable").DataTable({
        paging: false,
        columns:[
            {title: "Batch #"},
            {title: "Datum"},
            {title: "Aktivitet (MBq)"},
            {title: "Volym (ml)"},
            {title: "Signatur"},
            {title: "Patienter"},
        ],
        columnDefs: [
            {
                targets: 1,
                render: $.fn.dataTable.render.moment('YYYY-MM-DDTHH:mm:ssZ','YY-MM-DD hh:mm')
            },
            {
                targets: 2,
                render: $.fn.dataTable.render.number(' ', ',', 1),
                className: 'dt-body-center'
            },
            {
                targets: 3,
                render: $.fn.dataTable.render.number(' ', ',', 2),
                className: 'dt-body-center'
            }
        ],
        order: [[1, 'desc']]
    })
});

$('#idRadiopharmaceutical').change( function() {
    updateStatistics()
});

$('#idTime').change( function() {
    _updateRadPharmSelect();
});


function updateStatistics() {
    const timeInterval = $("#idTime").val();
    const radiopharmaceutical = $("#idRadiopharmaceutical").val();
    const resultContainer = $("#resultContainer")


    if ( radiopharmaceutical == null || radiopharmaceutical == "null" ){
        if ( !resultContainer.hasClass('hidden')) {
            resultContainer.addClass('hidden');
            return;
        }
    }

    $.ajax({
        url: $("#getStatisticsUrl").html(),
        data: {'timeInterval': timeInterval, 'radiopharmaceutical': radiopharmaceutical},
        dataType: 'json',
        success: function (result, status, xhr) {
            if ( resultContainer.hasClass('hidden')) { resultContainer.removeClass('hidden')}
            _updatePlot(result);
            _updateTable(result);
        },
        error: function (xhr, status, error) {
            alert('Kunde inte hämta data')
        }
    })
}

function _updatePlot(data) {
    x = [];
    y = [];
    annotation = [];
    for (i in data){
        radiopharmaceutical = data[i].radiopharmaceutical.name;
        x.push(data[i].datum);
        y.push(data[i].activity_mbq / 1000);
        annotation.push('Radiofarmaka: ' + radiopharmaceutical + '<br>' + 'Signature: ' + data[i].signature);
    }

    layout = {
        title: radiopharmaceutical,
        yaxis: {
            title: 'Aktivitet (GBq)'
        }
    };

    Plotly.newPlot('productionPlot', [{x: x, y: y, mode: 'markers', text: annotation}], layout, {displayModeBar: false})
}

function _updateTable(data) {
    var table = $("#productionTable").DataTable();

    tableData = [];

    for (i in data){
        tableData.push([
            data[i].batch,
            data[i].datum,
            data[i].activity_mbq,
            data[i].volume_ml,
            data[i].signature,
            data[i].count_patients
        ]);
        radiopharmaceutical = data[i].radiopharmaceutical.name;
        x.push(data[i].datum);
        y.push(data[i].activity_mbq / 1000);
        annotation.push('Radiofarmaka: ' + radiopharmaceutical + '<br>' + 'Signature: ' + data[i].signature);
    }

    table.clear().rows.add(tableData).draw();

}

function _updateRadPharmSelect() {
    var data = JSON.parse($("#yearRadpharmRelationship").text().replace(/'/g, '"'));
    var selectList = $('#idRadiopharmaceutical');
    selectList.empty();
    selectList.append('<option value="null">Välj radiofarmaka</option>');
    for (rpobj in data[$("#idTime").val()]) {
        let option = $('<option></option>').attr("value", data[$("#idTime").val()][rpobj] ).text(data[$("#idTime").val()][rpobj]);
        selectList.append(option)
    }
}
