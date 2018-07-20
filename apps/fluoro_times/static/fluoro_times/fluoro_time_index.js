$(document).ready(function() {
    $.ajax({
        url: $("#idUpdateDataUrl").html(),
        dataType: 'json',
        success: function(result, status, xhr) {
            $('#idLoaderRow').toggleClass('hidden');
            _updateTable(result.tableData);

            pie_w = 0.9 * $('#idCurrentYearPie').width();
            w_median = 0.9 * $('#idCurrentYearPie').width();

            pie_h = 400;
            h_median = w_median / 20 * result.layouts.medianHeight;

            _plotFluoroPlot([result.pieChart.currentYear], result.layouts.pieCharts.currentYear, 'idCurrentYearPie', pie_w, pie_h);
            _plotFluoroPlot([result.pieChart.previousYear], result.layouts.pieCharts.previousYear, 'idPreviousYearPie', pie_w, pie_h);
            _plotFluoroPlot(result.medianPlot, result.layouts.medianPlot, 'idMedianPlot', w_median, h_median);
        },
        error: function(xhr, status, error) {
            alert('Kunde inte ladda in data');
            $('#idLoaderRow').toggleClass('hidden');
        }
    })
});

function _updateTable(data){
    var table = $('#idSummaryTable');
    table.html();
    var rowData = [];
    let n = 0;
    for (ind in data) {
        if (n < 1) {
            let header = '<thead><tr><th rowspan="3">Område</th>';
            for (hospital in data[ind]) {
                header = header + '<th colspan="2">' + hospital + '</th>';
            }
            header = header + '</tr><<tr>';
            for (i2 in data[ind]) {
                header = header + '<th rowspan="2">Antal</th><th>Mediantid</th>';
            }
            header = header + '</tr><<tr>';
            for (i2 in data[ind]) {
                header = header + '<th>(mm:ss)</th>';
            }
            header = header + '</tr></thead>';
            table.html(header);
            table = $('#idSummaryTable');
            table = table.DataTable({
                paging: false,
                searching: false,
            });
        }
        n++;
        var tmpRow = [ind];
        for (hospital in data[ind]) {
            tmpRow.push(data[ind][hospital]['count']);
            tmpRow.push(data[ind][hospital]['median_time'])
        }
        rowData.push(tmpRow)
    }
    table.rows.add(rowData).draw();
}

function _plotFluoroPlot(plotData, layout, plotId, pw, ph){
    layout.height = ph;
    layout.width = pw;
    layout.autosize=false;
    Plotly.react(plotId, plotData, layout)
}