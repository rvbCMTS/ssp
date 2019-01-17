$(document).ready(function() {

});

function validateField(event) {
    var refs = JSON.parse($("#idReferences").html());

    var param = event.target.id.split(/_(.+)/)[1];

    if (param.includes('mean') || param.includes('stdev') || param.includes('snr')) {
        param = 'roi' + param
    }

    if (refs.hasOwnProperty(param)) {
        var param_val = event.target.valueAsNumber;
        if (!isNaN(param_val) && isFinite(param_val)) {
            removeValidationTags($('#' + event.target.id));
            if (param_val <= refs[param]['max'] && param_val >= refs[param]['min']) {
                $('#' + event.target.id).addClass('alert-success')
            } else {
                $('#' + event.target.id).addClass('alert-warning')
            }
        } else {
            $('#' + event.target.id).addClass('alert-danger')
        }
    }
}

function removeValidationTags(htmlObj) {
    if(htmlObj.hasClass('alert-success')){
        htmlObj.removeClass('alert-success')
    }
    if(htmlObj.hasClass('alert-warning')){
        htmlObj.removeClass('alert-warning')
    }
    if(htmlObj.hasClass('alert-danger')){
        htmlObj.removeClass('alert-danger')
    }
}

$('#id_modality').change(function(event) {
    const modality = $('#id_modality').val();

    $.ajax({
        type: "GET",
        url: $("#idFormUpdateUrl").html(),
        data: {'modality': modality, 'updateForm': true},
        dataType: 'json',
        success: function(result, status, xhr) {
            if($('#defaultFields').hasClass('hidden')){
               $('#defaultFields').removeClass('hidden')
            }
            var endFields = $('#defaultFields2');
            if(endFields.hasClass('hidden')){
               endFields.removeClass('hidden')
            }

            $("#idSubmitContainer").empty().append(
                "<input type='submit' class='btn btn-primary btn-lg' value='Spara'>"
            );

            if (result.hasOwnProperty('rois')){
                var roi_field_container = $('#idRoiFormFields');
                roi_field_container.empty();
                for (var i = 0; i < result.rois; i++){
                    roi_field_container.append(
                        "<div class=row><div class='col-lg-12'><h4>ROI " + (i+1).toString() + "</h4></div>" +
                        "  <div class='col-lg-4 col-md-4 col-sm-12'>" +
                        "    <div class='form-group'>" +
                        "      <label for='id_" + (i+1).toString() + "_mean'>Medel:</label>" +
                        "      <input class='validate-field' type='number' name='" + (i+1).toString() + "_mean' min='0' step='any' required='' id='id_"+ (i+1).toString() + "_mean'>" +
                        "    </div>" +
                        "  </div> " +
                        "  <div class='col-lg-4 col-md-4 col-sm-12'>" +
                        "    <div class='form-group'>" +
                        "      <label for='id_" + (i+1).toString() + "_stdev'>Standardavvikelse:</label>" +
                        "      <input class='validate-field' type='number' name='" + (i+1).toString() + "_stdev' min='0' step='any' required='' id='id_"+ (i+1).toString() + "_stdev'>" +
                        "    </div>" +
                        "  </div> " +
                        "  <div class='col-lg-4 col-md-4 col-sm-12'>" +
                        "    <div class='form-group'>" +
                        "      <label for='id_" + (i+1).toString() + "_snr'>SNR:</label>" +
                        "      <input class='validate-field' type='number' name='" + (i+1).toString() + "_snr' min='0' step='any' required='' id='id_"+ (i+1).toString() + "_snr'>" +
                        "    </div>" +
                        "  </div> " +
                        "</div>"
                    )
                }
            }
            if (result.hasOwnProperty('instructions')){
                $('#idInstruction').html(result.instructions);
            } else {
                $('#idInstruction').empty();
            }

            var referenceDiv = $("#idReferences");
            referenceDiv.empty();
            if (result.hasOwnProperty('references')) {
                referenceDiv.html(JSON.stringify(result.references));
            }

            // Add "on change" event here to make it apply to the dynamically added ROI-fields as well
            $(".validate-field").keyup(function(event) {
                validateField(event)
            });
        },
        error: function(xhr, status, error){
            if(!$('#defaultFields').hasClass('hidden')){
               $('#defaultFields').addClass('hidden')
            }
            if(!$('#defaultFields2').hasClass('hidden')){
               $('#defaultFields2').addClass('hidden')
            }
            $('#idInstruction').empty();

            $('#idRoiFormFields').empty();

            $("#idReferences").empty();
        }
    });
});