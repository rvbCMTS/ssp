$(document).ready(function() {
    var filter_data = $.parseJSON($('#idFilterData').html());
    var years = Object.keys(filter_data);
    var yearSelect = $('#idYear');
    for (var i = years.length - 1; i >=0; --i){
        yearSelect.append($('<option></option>').attr("value", parseInt(years[i])).text(years[i]))
    }
    yearSelect.val(parseInt(years.slice(-1)[0]));
    yearSelect.change();

    $("#idAreaStat").DataTable( {
        paging: false,
        searching: false,
    } );
    $("#idOperatorStat").DataTable( {
        paging: false,
        searching: false,
    } );
});

$('.update-filter-choices').change(function(event) {
    var filter_data =  $.parseJSON($('#idFilterData').html());
    var filter_year = $('#idYear').val();
    let clinicList = $('#idClinic');
    clinicList.empty();
    clinicList.append(
        $('<option></option>').attr("value", null).text('-- Välj klinik --')
    );
    for (clinic in filter_data[filter_year]){
        clinicList.append(
            $('<option></option>').attr("value", parseInt(clinic)).text(filter_data[filter_year][clinic])
        )
    }
});

$('.update-data').change(function(event){
    let loaderRow = $('#idLoaderRow');
    if (loaderRow.hasClass('hidden')){
        loaderRow.removeClass('hidden')
    }
    const year = parseInt($('#idYear').val());
    const clinic = parseInt($('#idClinic').val());

    let reportRow = $('.report-row');
    $.ajax({
        url: $("#idUpdateUrl").html(),
        data: {'year': year, 'clinic': clinic},
        dataType: 'json',
        success: function(result, status, xhr) {
            $('#idReportHeader').html(result.reportHeader);
            loaderRow.addClass('hidden');
            _updateTable(result.operatorTable);
            _updateTable(result.anatomyRegionTable);
            _updatePlot(result.bubblePlot);
            if (reportRow.hasClass('hidden')){
                reportRow.removeClass('hidden')
            }
        },
        error: function(xhr, status, error){
            if (!loaderRow.hasClass('hidden')){
                loaderRow.addClass('hidden')
            }
            if (!reportRow.hasClass('hidden')){
                reportRow.addClass('hidden')
            }
            $('#idReportHeader').html('');
            alert('Kunde inte hämta data för årsrapporten')
        }
    })

});

function _updateTable(data) {
    let table = $('#' + data.tableId).DataTable();

    table.clear().rows.add(data.data).draw();
}

function _updatePlot(data) {
    /*
    var d3 = Plotly.d3;

    var WIDTH_IN_PERCENT_OF_PARENT = 90,
        HEIGHT_IN_PERCENT_OF_PARENT = 60;

    var gd3 = d3.select(data.id)
        .append('div').style({
            width: WIDTH_IN_PERCENT_OF_PARENT + '%',
            'margin-left': (100 - WIDTH_IN_PERCENT_OF_PARENT) / 2 + '%',
            height: HEIGHT_IN_PERCENT_OF_PARENT + '%',
            'margin-top': (100 - HEIGHT_IN_PERCENT_OF_PARENT) / 2 + 'vh'
        });

    var gd = gd3.node();

    Plotly.plot(gd, data.data, data.layout);

    window.onresize = function () {
        Plotly.Plots.resize(gd);
    }
    */
    data.layout.width = 0.9 * $('#idFilterRow').width();
    data.layout.height = 0.6 * data.layout.width;
    for (ind in data.data) {
        data.data[ind].marker.sizeref = data.maxCount / (data.layout.width * 2 * 3.14 / data.cols)
    }

    Plotly.react(data.id, data.data, data.layout)
}