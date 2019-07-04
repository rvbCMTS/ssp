$(document).ready(function() {
    updateFilters(JSON.parse($( "#idFilterData" ).html()))
});

$("#idTime").change(function(event) {
    let loaderRow = $('#idLoaderRow');
    if (loaderRow.hasClass('hidden')) { loaderRow.removeClass('hidden') }

    let plotDiv = $("#idPlotRow");
    if (!plotDiv.hasClass('hidden')) { plotDiv.addClass('hidden') }

    $.ajax({
        url: $("#idFilterChoicesUrl").html(),
        data: {'timeLimit': $("#idTime").val()},
        dataType: 'json',
        success: function(result, status, xhr) {
            updateFilters(result);
            if (!loaderRow.hasClass('hidden')) { loaderRow.addClass('hidden') }
        },
        error: function(xhr, status, error) {
            if (!loaderRow.hasClass('hidden')) { loaderRow.addClass('hidden') }
        }
    })
});
$("#idModality").change(function (event) {
   updateFilters(JSON.parse($( "#idFilterData" ).html()))
});

function updateFilters(filterData) {
    let modalityList = $("#idModality");
    const modality = modalityList.val();
    let coilList = $("#idRfCoil");
    let sequenceList = $("#idSequence");
    const coil = coilList.val();

    if ( modality !== null && modality !== "null") {
        const coilSelected = (coil !== null && coil !== 'all');

        sequenceList.empty().append($('<option></option>').attr(
                "value", "all" ).text("Alla"));
        if (!coilSelected) { coilList.empty().append($('<option></option>').attr(
                "value", "all" ).text("Alla")) }

        coilList.prop('disabled', false);
        sequenceList.prop('disabled', false);

        let coilsInsSelectList = [];
        let sequencesInSelectList = [];

        for (ind in filterData[modality].coilsAndSequences) {
            const co = filterData[modality].coilsAndSequences[ind].coil;
            const so = filterData[modality].coilsAndSequences[ind].sequence;

            let coilOption = $('<option></option>').attr(
                "value", co ).text(co);

            let sequenceOption = $('<option></option>').attr(
                "value", so ).text(so);

            if (coilSelected) {
                if (co === coil) {
                    if (sequencesInSelectList.indexOf(so) < 0){
                        sequenceList.append(sequenceOption);
                        sequencesInSelectList.push(so);
                    }
                }
                continue
            }

            if ( coilsInsSelectList.indexOf(co) < 0){
                coilList.append(coilOption);
                coilsInsSelectList.push(co);
            }
            if (sequencesInSelectList.indexOf(so) < 0){
                sequenceList.append(sequenceOption);
                sequencesInSelectList.push(so);
            }
        }
        return
    }

    modalityList.empty().append($('<option></option>').attr(
                "value", "null" ).text("Välj modalitet"));
    for (ind in filterData){
        modalityList.append($('<option></option>').attr(
                "value", ind ).text(filterData[ind].displayName));
    }

    coilList.empty().append($('<option></option>').attr(
                "value", "all" ).text("Alla"));
    coilList.prop('disabled', 'disabled');

    sequenceList.empty().append($('<option></option>').attr(
                "value", "all" ).text("Alla"));
    sequenceList.prop('disabled', 'disabled');
}

function preparePlotData(data) {
    let output_template = {
        snr: { x: [], y: [], mode: 'markers', type: 'scatter' },
        frequency: { x: [], y: [], mode: 'markers', type: 'scatter' },
        pds1x: { x: [], y: [], mode: 'markers', type: 'scatter' },
        pds1y: { x: [], y: [], mode: 'markers', type: 'scatter' },
        pds1diag1: { x: [], y: [], mode: 'markers', type: 'scatter' },
        pds1diag2: { x: [], y: [], mode: 'markers', type: 'scatter' },
        pds5x: { x: [], y: [], mode: 'markers', type: 'scatter' },
        pds5y: { x: [], y: [], mode: 'markers', type: 'scatter' },
        pds5diag1: { x: [], y: [], mode: 'markers', type: 'scatter' },
        pds5diag2: { x: [], y: [], mode: 'markers', type: 'scatter' },
        hcod: { x: [], y: [], mode: 'markers', type: 'scatter' },
        st: { x: [], y: [], mode: 'markers', type: 'scatter' },
        spa1: { x: [], y: [], mode: 'markers', type: 'scatter' },
        spa11: { x: [], y: [], mode: 'markers', type: 'scatter' },
        pui: { x: [], y: [], mode: 'markers', type: 'scatter' },
        gr: { x: [], y: [], mode: 'markers', type: 'scatter' },
        gr5: { x: [], y: [], mode: 'markers', type: 'scatter' },
        noise: { x: [], y: [], mode: 'markers', type: 'scatter' }
    };

    let output = [];

    let i = 0;
    while ( i < data.length ) {
        let tmp = data[i];
        const traceName = tmp.reported_machine.machine;

        output.snr.x.append(tmp.acquisition_time);
        output.snr.y.append();

        output.frequency.x.append(tmp.acquisition_time);
        output.frequency.y.append(tmp.image_frequency);

        output.pds1x.x.append(tmp.acquisition_time);
        output.pds1x.y.append(tmp.diameter_x_slice1);
        output.pds1y.x.append(tmp.acquisition_time);
        output.pds1y.y.append(tmp.diameter_y_slice1);
        output.pds1diag1.x.append(tmp.acquisition_time);
        output.pds1diag1.y.append(tmp.diameter_diag1_slice1);
        output.pds1diag2.x.append(tmp.acquisition_time);
        output.pds1diag2.y.append(tmp.diameter_diag2_slice1);

        output.pds5x.x.append(tmp.acquisition_time);
        output.pds5x.y.append(tmp.diameter_x_slice5);
        output.pds5y.x.append(tmp.acquisition_time);
        output.pds5y.y.append(tmp.diameter_y_slice5);
        output.pds5diag1.x.append(tmp.acquisition_time);
        output.pds5diag1.y.append(tmp.diameter_diag1_slice5);
        output.pds5diag2.x.append(tmp.acquisition_time);
        output.pds5diag2.y.append(tmp.diameter_diag2_slice5);

        output.hcod.x.append(tmp.acquisition_time);
        output.hcod.y.append();

        output.st.x.append(tmp.acquisition_time);
        output.st.y.append(tmp.slice_thickness);

        output.spa1.x.append(tmp.acquisition_time);
        output.spa1.y.append(tmp.slice_position_accuracy_slice1);

        output.spa11.x.append(tmp.acquisition_time);
        output.spa11.y.append(tmp.slice_position_accuracy_slice11);

        output.pui.x.append(tmp.acquisition_time);
        output.pui.y.append(tmp.percent_uniformity_integral);

        output.gr.x.append(tmp.acquisition_time);
        output.gr.y.append(tmp.ghosting_ratio);

        output.gr5.x.append(tmp.acquisition_time);
        output.gr5.y.append(tmp.ghosting_ratio_slice5);

        output.noise.x.append(tmp.acquisition_time);
        output.noise.y.append(tmp.noise);

        i = i + 1;
    }

    return output;
}

function updatePlots(source) {
    const timeLimit = $("#idTime").val();
    const modality = $("#idModality").val();
    const rfCoil = $("#idRfCoil").val();
    const sequence = $("#idSequence").val();

    queryLimits = {'timeLimit': timeLimit, 'modality': modality};
    if ( rfCoil !== '')

    $.ajax({
        url: "idUpdatePlotsUrl",
        data: {'timeLimit': timeLimit, 'modality': modality}
    })
}

function plotData(data) {}