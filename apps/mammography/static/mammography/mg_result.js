$(document).ready(function() {
    $('#id_modality').change(function(event) {updateResults(event.target.id)}
        );
    $('input[type=radio][name=time_span]').change(function(event) { updateResults(event.target.id) });
});

function updateFilterValues(data, selectedModality) {
    let selectList = $("#id_modality");
        selectList.empty();

    let unselected = $('<option></option>').attr("value", "").text("---------");
    if (selectedModality == ""){
        unselected.prop("selected", true)
    }
    selectList.append(unselected);

    for (ind in data) {
        let option = $('<option></option>').attr("value", data[ind].id).text(data[ind].name);
        if (data[ind].id == selectedModality){ option.prop("selected", true)}
        selectList.append(option)
    }
}

$('.update-filter-choices').change(function(event) {
    $('#idLoaderRow').toggleClass('hidden');
    updateFilterValues(event.target.id);
});

function updateResults(triggeringId) {
    const modality = $("#id_modality").val();
    const timeSpan = $('input[name=time_span]:checked').val();

    let loaderRow = $('#idLoaderRow');
    let resultPlotRow = $('#resultPlots');
    if (modality == ""){
        if (loaderRow.hasClass('hidden')){ loaderRow.removeClass('hidden') }
        if (!resultPlotRow.hasClass('hidden')) { resultPlotRow.addClass('hidden') }
    } else {
        if (loaderRow.hasClass('hidden')){ loaderRow.removeClass('hidden') }

        $.ajax({
            url: $('#idUpdatePlotsUrl').html(),
            data: {"modality": modality, "timeSpan": timeSpan},
            dataType: 'json',
            success: function(result, status, xhr) {
                if (resultPlotRow.hasClass('hidden')){ resultPlotRow.removeClass('hidden') }
                plotResults(result)
            },
            error: function(xhr, status, error){
                if (!loaderRow.hasClass('hidden')){ loaderRow.addClass('hidden') }
                alert('Kunde inte hämta mätresultat')
            }
        });
    }

    if (triggeringId != "id_modality") {
        $.ajax({
            url: $('#idFilterChoicesUrl').html(),
            data: {"timeSpan": timeSpan},
            dataType: 'json',
            success: function(result, status, xhr) {
                updateFilterValues(result.modalities, parseInt(modality))
                if (modality == "") {if (!loaderRow.hasClass('hidden')){ loaderRow.addClass('hidden') } }
            },
            error: function(xhr, status, error) {
                if (!loaderRow.hasClass('hidden')){ loaderRow.addClass('hidden') }
            }
        });
        if (!loaderRow.hasClass('hidden')){ loaderRow.addClass('hidden') }
    }
}

function plotResults(data) {
    var mas = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var entranceDose = {y: [], signature: [], x: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var meanRoi1 = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var meanRoi2 = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var meanRoi3 = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var meanRoi4 = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var meanRoi5 = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var snrRoi1 = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var snrRoi2 = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var snrRoi3 = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var snrRoi4 = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var snrRoi5 = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var stdevRoi1 = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var stdevRoi2 = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var stdevRoi3 = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var stdevRoi4 = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var stdevRoi5 = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var snrAllRoi = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var meanAllRoi = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};
    var stdevAllRoi = {y: [], x: [], signature: [], tolerance: {min: {y: [], x: []}, max: {y: [], x: []}}};

    for (let obj of data.roi_result){
        switch(obj.roi){
            case 1:
                meanRoi1.x.push(obj.measurement.measurement_date);
                meanRoi1.y.push(obj.mean);
                meanRoi1.signature.push(obj.measurement.signature);
                snrRoi1.x.push(obj.measurement.measurement_date);
                snrRoi1.y.push(obj.signal_noise_ratio);
                snrRoi1.signature.push(obj.measurement.signature);
                stdevRoi1.x.push(obj.measurement.measurement_date);
                stdevRoi1.y.push(obj.stdev);
                stdevRoi1.signature.push(obj.measurement.signature);
                mas.x.push(obj.measurement.measurement_date);
                mas.y.push(obj.measurement.mas);
                mas.signature.push(obj.measurement.signature);
                entranceDose.x.push(obj.measurement.measurement_date);
                entranceDose.y.push(obj.measurement.entrance_dose);
                entranceDose.signature.push(obj.measurement.signature);
                break;
            case 2:
                meanRoi2.x.push(obj.measurement.measurement_date);
                meanRoi2.y.push(obj.mean);
                meanRoi2.signature.push(obj.measurement.signature);
                snrRoi2.x.push(obj.measurement.measurement_date);
                snrRoi2.y.push(obj.signal_noise_ratio);
                snrRoi2.signature.push(obj.measurement.signature);
                stdevRoi2.x.push(obj.measurement.measurement_date);
                stdevRoi2.y.push(obj.stdev);
                stdevRoi2.signature.push(obj.measurement.signature);
                break;
            case 3:
                meanRoi3.x.push(obj.measurement.measurement_date);
                meanRoi3.y.push(obj.mean);
                meanRoi3.signature.push(obj.measurement.signature);
                snrRoi3.x.push(obj.measurement.measurement_date);
                snrRoi3.y.push(obj.signal_noise_ratio);
                snrRoi3.signature.push(obj.measurement.signature);
                stdevRoi3.x.push(obj.measurement.measurement_date);
                stdevRoi3.y.push(obj.stdev);
                stdevRoi3.signature.push(obj.measurement.signature);
                break;
            case 4:
                meanRoi4.x.push(obj.measurement.measurement_date);
                meanRoi4.y.push(obj.mean);
                meanRoi4.signature.push(obj.measurement.signature);
                snrRoi4.x.push(obj.measurement.measurement_date);
                snrRoi4.y.push(obj.signal_noise_ratio);
                snrRoi4.signature.push(obj.measurement.signature);
                stdevRoi4.x.push(obj.measurement.measurement_date);
                stdevRoi4.y.push(obj.stdev);
                stdevRoi4.signature.push(obj.measurement.signature);
                break;
            case 5:
                meanRoi5.x.push(obj.measurement.measurement_date);
                meanRoi5.y.push(obj.mean);
                meanRoi5.signature.push(obj.measurement.signature);
                snrRoi5.x.push(obj.measurement.measurement_date);
                snrRoi5.y.push(obj.signal_noise_ratio);
                snrRoi5.signature.push(obj.measurement.signature);
                stdevRoi5.x.push(obj.measurement.measurement_date);
                stdevRoi5.y.push(obj.stdev);
                stdevRoi5.signature.push(obj.measurement.signature);
                break;
        }
    }
    for (let obj of data.mean_all){
        meanAllRoi.x.push(obj.measurement_date);
        meanAllRoi.y.push(obj.mean_all);
        meanAllRoi.signature.push(obj.signature);
        snrAllRoi.x.push(obj.measurement_date);
        snrAllRoi.y.push(obj.snr_all);
        snrAllRoi.signature.push(obj.signature);
        stdevAllRoi.x.push(obj.measurement_date);
        stdevAllRoi.y.push(obj.stdev_all);
        stdevAllRoi.signature.push(obj.signature);
    }
    for (let obj of data.reference){
        if (obj.tolerance_unit == 'percent'){
            let minTol = obj.parameter_value * (1 - obj.tolerance / 100);
            let maxTol = obj.parameter_value * (1 + obj.tolerance / 100);
            switch(obj.parameter.parameter){
            case 'entrance-dose':
                entranceDose.tolerance.min.y.push(minTol);
                entranceDose.tolerance.min.x.push(obj.set_date);
                entranceDose.tolerance.max.y.push(maxTol);
                entranceDose.tolerance.max.x.push(obj.set_date);
                break;
            case 'mas':
                mas.tolerance.min.y.push(minTol);
                mas.tolerance.min.x.push(obj.set_date);
                mas.tolerance.max.y.push(maxTol);
                mas.tolerance.max.x.push(obj.set_date);
                break;
            case 'mean-all-rois':
                meanAllRoi.tolerance.min.y.push(minTol);
                meanAllRoi.tolerance.min.x.push(obj.set_date);
                meanAllRoi.tolerance.max.y.push(maxTol);
                meanAllRoi.tolerance.max.x.push(obj.set_date);
                break;
            case 'mean-roi1':
                meanRoi1.tolerance.min.y.push(minTol);
                meanRoi1.tolerance.min.x.push(obj.set_date);
                meanRoi1.tolerance.max.y.push(maxTol);
                meanRoi1.tolerance.max.x.push(obj.set_date);
                break;
            case 'snr-roi1':
                snrRoi1.tolerance.min.y.push(minTol);
                snrRoi1.tolerance.min.x.push(obj.set_date);
                snrRoi1.tolerance.max.y.push(maxTol);
                snrRoi1.tolerance.max.x.push(obj.set_date);
                break;
            case 'std-roi1':
                stdevRoi1.tolerance.min.y.push(minTol);
                stdevRoi1.tolerance.min.x.push(obj.set_date);
                stdevRoi1.tolerance.max.y.push(maxTol);
                stdevRoi1.tolerance.max.x.push(obj.set_date);
                break;
            case 'mean-roi2':
                meanRoi2.tolerance.min.y.push(minTol);
                meanRoi2.tolerance.min.x.push(obj.set_date);
                meanRoi2.tolerance.max.y.push(maxTol);
                meanRoi2.tolerance.max.x.push(obj.set_date);
                break;
            case 'snr-roi2':
                snrRoi2.tolerance.min.y.push(minTol);
                snrRoi2.tolerance.min.x.push(obj.set_date);
                snrRoi2.tolerance.max.y.push(maxTol);
                snrRoi2.tolerance.max.x.push(obj.set_date);
                break;
            case 'std-roi2':
                stdevRoi2.tolerance.min.y.push(minTol);
                stdevRoi2.tolerance.min.x.push(obj.set_date);
                stdevRoi2.tolerance.max.y.push(maxTol);
                stdevRoi2.tolerance.max.x.push(obj.set_date);
                break;
            case 'mean-roi3':
                meanRoi3.tolerance.min.y.push(minTol);
                meanRoi3.tolerance.min.x.push(obj.set_date);
                meanRoi3.tolerance.max.y.push(maxTol);
                meanRoi3.tolerance.max.x.push(obj.set_date);
                break;
            case 'snr-roi3':
                snrRoi3.tolerance.min.y.push(minTol);
                snrRoi3.tolerance.min.x.push(obj.set_date);
                snrRoi3.tolerance.max.y.push(maxTol);
                snrRoi3.tolerance.max.x.push(obj.set_date);
                break;
            case 'std-roi3':
                stdevRoi3.tolerance.min.y.push(minTol);
                stdevRoi3.tolerance.min.x.push(obj.set_date);
                stdevRoi3.tolerance.max.y.push(maxTol);
                stdevRoi3.tolerance.max.x.push(obj.set_date);
                break;
            case 'mean-roi4':
                meanRoi4.tolerance.min.y.push(minTol);
                meanRoi4.tolerance.min.x.push(obj.set_date);
                meanRoi4.tolerance.max.y.push(maxTol);
                meanRoi4.tolerance.max.x.push(obj.set_date);
                break;
            case 'snr-roi4':
                snrRoi4.tolerance.min.y.push(minTol);
                snrRoi4.tolerance.min.x.push(obj.set_date);
                snrRoi4.tolerance.max.y.push(maxTol);
                snrRoi4.tolerance.max.x.push(obj.set_date);
                break;
            case 'std-roi4':
                stdevRoi4.tolerance.min.y.push(minTol);
                stdevRoi4.tolerance.min.x.push(obj.set_date);
                stdevRoi4.tolerance.max.y.push(maxTol);
                stdevRoi4.tolerance.max.x.push(obj.set_date);
                break;
            case 'mean-roi5':
                meanRoi5.tolerance.min.y.push(minTol);
                meanRoi5.tolerance.min.x.push(obj.set_date);
                meanRoi5.tolerance.max.y.push(maxTol);
                meanRoi5.tolerance.max.x.push(obj.set_date);
                break;
            case 'snr-roi5':
                snrRoi5.tolerance.min.y.push(minTol);
                snrRoi5.tolerance.min.x.push(obj.set_date);
                snrRoi5.tolerance.max.y.push(maxTol);
                snrRoi5.tolerance.max.x.push(obj.set_date);
                break;
            case 'std-roi5':
                stdevRoi5.tolerance.min.y.push(minTol);
                stdevRoi5.tolerance.min.x.push(obj.set_date);
                stdevRoi5.tolerance.max.y.push(maxTol);
                stdevRoi5.tolerance.max.x.push(obj.set_date);
                break;
            }
        }
    }

    let widthOneCol = 0.95 * $('#mean-all-plot').width();
    let widthTwoCol = 0.95 * $('#mas-plot').width();
    let widthThreeCol = 0.95 * $('#mean1-plot').width();
    let plotHeight = 0.6 * widthThreeCol;

    create_plot(mas, 'mas-plot', widthTwoCol, plotHeight);
    create_plot(entranceDose, 'ed-plot', widthTwoCol, plotHeight);

    //create_plot(snrAllRoi, 'snr-all-plot', widthThreeCol, plotHeight, 'SNR');
    create_plot(meanAllRoi, 'mean-all-plot', widthOneCol, plotHeight, 'Medel');
    //create_plot(stdevAllRoi, 'stdev-all-plot', widthThreeCol, plotHeight, 'Standardavvikelse');

    create_plot(snrRoi1, 'snr1-plot', widthThreeCol, plotHeight, 'SNR');
    create_plot(meanRoi1, 'mean1-plot', widthThreeCol, plotHeight, 'Medel');
    create_plot(stdevRoi1, 'stdev1-plot', widthThreeCol, plotHeight, 'Standardavvikelse');

    create_plot(snrRoi2, 'snr2-plot', widthThreeCol, plotHeight, 'SNR');
    create_plot(meanRoi2, 'mean2-plot', widthThreeCol, plotHeight, 'Medel');
    create_plot(stdevRoi2, 'stdev2-plot', widthThreeCol, plotHeight, 'Standardavvikelse');

    create_plot(snrRoi3, 'snr3-plot', widthThreeCol, plotHeight, 'SNR');
    create_plot(meanRoi3, 'mean3-plot', widthThreeCol, plotHeight, 'Medel');
    create_plot(stdevRoi3, 'stdev3-plot', widthThreeCol, plotHeight, 'Standardavvikelse');

    create_plot(snrRoi4, 'snr4-plot', widthThreeCol, plotHeight, 'SNR');
    create_plot(meanRoi4, 'mean4-plot', widthThreeCol, plotHeight, 'Medel');
    create_plot(stdevRoi4, 'stdev4-plot', widthThreeCol, plotHeight, 'Standardavvikelse');

    create_plot(snrRoi5, 'snr5-plot', widthThreeCol, plotHeight, 'SNR');
    create_plot(meanRoi5, 'mean5-plot', widthThreeCol, plotHeight, 'Medel');
    create_plot(stdevRoi5, 'stdev5-plot', widthThreeCol, plotHeight, 'Standardavvikelse');

    let loaderRow = $('#idLoaderRow');
    if (!loaderRow.hasClass('hidden')){ loaderRow.addClass('hidden') }
}

function create_plot(plotData, plotId, plotWidth, plotHeight, ytitle=null){
    let traces = [];
    traces.push({x: plotData.x, y: plotData.y, text: plotData.signature, mode: 'markers', type: 'scatter'});

    let layout = {"width": plotWidth, "height": plotHeight};

    let margin = {
        "r": 50,
        "b": 50,
        "t": 50,
        "pad": 4
    };

    if (ytitle == null){
        margin["l"] = 50;
    } else {
        layout["yaxis"] = {"title": ytitle};
    }

    layout["margin"] = margin;

    if (plotData.tolerance.min.x.length > 0){
        let shape = {'type': 'rect', 'line': {'width': 0}, 'fillcolor': '#66ff66', 'opacity': 0.2};
        layout['shapes'] = [];
        if (plotData.tolerance.min.x.length == 1){
            shape['xref'] = 'paper';
            shape['x0'] = 0;
            shape['x1'] = 1;
            shape['yref'] = 'y';
            shape['y0'] = plotData.tolerance.min.y[0];
            shape['y1'] = plotData.tolerance.max.y[0];

            layout['shapes'].push(shape)
        } else {
            for (ind = 0; ind < plotData.tolerance.min.x.length; ind++){
                if (ind > 0){
                    let shape0 = layout['shapes'][layout['shapes'].length - 1];
                    shape0['x1'] = plotData.tolerance.min.x[ind];
                    layout['shapes'].push(shape0)
                }

                shape['xref'] = 'x';
                shape['x0'] = plotData.tolerance.min.x[ind];
                shape['x1'] = plotData.tolerance.min.x[ind];
                shape['yref'] = 'y';
                shape['y0'] = plotData.tolerance.min.y[0];
                shape['y1'] = plotData.tolerance.max.y[0];

            }

            let shape0 = layout['shapes'][layout['shapes'].length - 1];
            shape0['x1'] = plotData.x[plotData.x.length - 1];
            layout['shapes'].push(shape0)
        }
    }

    Plotly.react(plotId, traces, layout, {"displayModeBar": false})
}