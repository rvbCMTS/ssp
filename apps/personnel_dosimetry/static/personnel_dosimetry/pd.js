$(document).ready(function() {
    $("#idSummaryTable").DataTable( {
        paging: false,
        searching: false,
    } );
});

//$('.update-data').change(function(event) {
//    updatePdData(event.target.id);
//});

$('.update-filter-choices').change(function(event) {
    $('#idLoaderRow').toggleClass('hidden');
    updateFilterValues(event.target.id);
});

function updateFilterValues(triggeringId) {
    const timeInterval = $("#idTime").val();
    const clinic = $("idClinic").val();
    const profession = $("idPersonnelCategory").val();
    const personnel = $("idPersonnel").val();
    const dosimeterPlacement = $("idDosimeterPlacement").val();

    $.ajax({
        url: $("#idFilterChoicesUrl").html(),
        data: {'timeInterval': timeInterval, 'clinic': clinic, 'profession': profession, 'personnel': personnel,
            'dosimeterPlacement': dosimeterPlacement, 'triggeringElement': triggeringId},
        dataType: 'json',
        success: function(result, status, xhr) {
            _updateFilterChoices(result, triggeringId)
        },
        error: function(xhr, status, error){
            alert('Kunde inte uppdatera filtervalen')
        }
    });
}

function updatePdData(triggeringId) {
    const timeInterval = $("#idTime").val();
    const clinic = $("#idClinic").val();
    const profession = $("#idPersonnelCategory").val();
    const personnel = $("#idPersonnel").val();
    const dosimeterPlacement = $("#idDosimeterPlacement").val();
    const spotcheck = $("#idSpotcheck:checked").length;
    const areameasurement = $("#idAreaMeasurement:checked").length;

    $.ajax({
        type: "GET",
        url: $("#idUpdatePlotsUrl").html(),
        data: {'timeInterval': timeInterval, 'clinic': clinic, 'profession': profession,
            'personnel': personnel, 'dosimeterPlacement': dosimeterPlacement, 'spotcheck': spotcheck,
            'areameasurement': areameasurement, 'triggeringElement': triggeringId},
        dataType: 'json',
        success: function(result, status, xhr) {
            _plotPdResults(result.plotData);
            _updateResultTable(result.tableData)
        },
        error: function(xhr, status, error){
            alert(error)
        }
    });
}

function _plotPdResults(plotData){
    for (pd in plotData){
        Plotly.newPlot(plotData[pd].id, plotData[pd].data, plotData[pd].layout, plotData[pd].layout2)
    }
}

function _updateResultTable(data){
    var table = $("#idSummaryTable").DataTable();

    table.clear().rows.add(data.data).draw();
    $('#idLoaderRow').toggleClass('hidden');
}

function _updateFilterChoices(data, triggeringId) {
    for (ind in data) {
        let selectList = $(data[ind].id);
        selectList.empty();

        for (ind2 in data[ind].choices) {
            let option = $('<option></option>').attr("value", data[ind].choices[ind2].id ).text(data[ind].choices[ind2].name);
            selectList.append(option)
        }
        selectList.val(data[ind].selectedValue);
    }
    updatePdData(triggeringId);
}