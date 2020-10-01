$(document).ready(function() {
    $('#id_clinic').change();
    $('#id_modality').change();
    let timeObj = new Date();
    $('#id_exam_id').val("SSP_" + timeObj.getTime() );
});

$('#id_clinic').change(function(event){$('#idSelectedClinic').html($('#id_clinic').val()); filter_modality();filter_operator();});

$('#idShowAllModalitiesCheck').change(function(event){filter_modality();});

$('#idShowAllOperatorsCheck').change(function(event){filter_operator();});

function filter_modality(){
    let clinic = parseInt($('#idSelectedClinic').html());
    let showAll = $('#idShowAllModalitiesCheck')[0].checked;
    let modalityMap = JSON.parse($('#idClinicModalityMap').html());
    let allModalityList = JSON.parse($('#idAllModalities').html());
    let modalityList = $('#id_modality');
    modalityList.empty();

    if ( showAll || !modalityMap.hasOwnProperty(clinic.toString())) {
        modalityList.append('<option value="" selected>---------</option>');
        for ( let ind = 0; ind < allModalityList.length; ind++ ) {
            modalityList.append('<option value="' + allModalityList[ind].modalityId + '">' +
                allModalityList[ind].modalityName + '</option>');
        }
    }
    else {
        modalityList.append('<option value="">---------</option>');
        let modalities = modalityMap[clinic.toString()];
        let specificModalities = 0;

        for ( let ind = 0; ind < allModalityList.length; ind++ ) {
            if ( modalities.indexOf(allModalityList[ind].modalityId) !== -1 ) {
                specificModalities = specificModalities + 1;
                if (specificModalities == 1 ) {
                    modalityList.append('<option value="' + allModalityList[ind].modalityId + '" selected>' +
                        allModalityList[ind].modalityName + '</option>');
                } else {
                    modalityList.append('<option value="' + allModalityList[ind].modalityId + '">' +
                        allModalityList[ind].modalityName + '</option>');
                }
            }
        }
    }
}

function filter_operator(){
    let clinic = parseInt($('#idSelectedClinic').html());
    let showAll = $('#idShowAllOperatorsCheck')[0].checked;
    let allOperatorList = JSON.parse($('#idAllOperators').html());
    let operatorMap = JSON.parse($('#idClinicOperatorMap').html());
    let operatorList = $('#id_operator');
    operatorList.empty();

    if ( showAll || !operatorMap.hasOwnProperty(clinic.toString())) {
        operatorList.append('<option value="" selected>---------</option>');
        for ( let ind = 0; ind < allOperatorList.length; ind++ ) {
            operatorList.append('<option value="' + allOperatorList[ind].operatorId + '">' +
                allOperatorList[ind].operatorName + '</option>');
        }
    }
    else {
        operatorList.append('<option value="" selected>---------</option>');
        let operators = operatorMap[clinic.toString()];

        for ( let ind = 0; ind < allOperatorList.length; ind++ ) {
            if ( operators.indexOf(allOperatorList[ind].operatorId) !== -1 ) {
                operatorList.append('<option value="' + allOperatorList[ind].operatorId + '">' +
                    allOperatorList[ind].operatorName + '</option>');
            }
        }
    }
}

$('#id_modality').change(function(event){
    let modality = $('#id_modality').val();
    let doseUnitMap = JSON.parse($('#idModalityDoseUnit').html());

    if (doseUnitMap.hasOwnProperty(modality.toString())) { $('#id_fluoro_dose_unit').val(doseUnitMap[modality.toString()]); }
});