$(document).ready(function() {
    $.ajax({
        url: $("#idUpdateUrl").html(),
        dataType: 'json',
        success: function(result, status, xhr) {
            updatePlots(result)
        },
        error: function(xhr, status, error){
            alert('Kunde inte hämta data')
        }
    })
});

function updatePlots(data){
    let plotWidth = 0.9 * $("#medianYearPlot").width();
    let plotHeight = 0.6 * plotWidth;

    data.medianTimePerYear.layout.width = plotWidth;
    data.medianTimePerYear.layout.height = plotHeight;
    Plotly.react('medianYearPlot', data.medianTimePerYear.data, data.medianTimePerYear.layout);

    data.medianTimePerClinicCategory.layout.width = plotWidth;
    data.medianTimePerClinicCategory.layout.height = plotHeight;
    Plotly.react('medianClinicCategoryPlot', data.medianTimePerClinicCategory.data, data.medianTimePerClinicCategory.layout);

    data.medianTimePerAnatomyRegion.layout.width = plotWidth;
    data.medianTimePerAnatomyRegion.layout.height = plotHeight;
    Plotly.react('medianAnatomyYearPlot', data.medianTimePerAnatomyRegion.data, data.medianTimePerAnatomyRegion.layout);

    data.examsPerAnatomyRegion.layout.width = plotWidth;
    data.examsPerAnatomyRegion.layout.height = plotHeight;
    Plotly.react('countAnatomyYearPlot', data.examsPerAnatomyRegion.data, data.examsPerAnatomyRegion.layout);
}