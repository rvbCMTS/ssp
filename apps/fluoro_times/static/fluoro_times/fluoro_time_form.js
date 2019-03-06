$(document).ready(function() {$('#id_clinic').change();});

$('#id_clinic').change(function(event){$('#idSelectedClinic').html($('#id_clinic').val()); filter_modality();filter_operator();});

$('#idShowAllModalitiesCheck').change(function(event){filter_modality();});

$('#idShowAllOperatorsCheck').change(function(event){filter_operator();});

function filter_modality(){
    let clinic = parseInt($('#idSelectedClinic').html());
    let showAll = $('#idShowAllModalitiesCheck')[0].checked;
    let modalityMap = JSON.parse($('#idClinicModalityMap').html());

    var specificModalities = 0;
    if ( showAll || !modalityMap.hasOwnProperty(clinic.toString()) ){
        for (option of $('#id_modality')[0].children){
            option.hidden = false; specificModalities = specificModalities + 1;
        }
    } else {
        let modalities = modalityMap[clinic.toString()];
        for (option of $('#id_modality')[0].children){
            if ( option.value.toString() == "" || modalities.includes(parseInt(option.value)) ){
                if ( option.value.toString() != "" ){ specificModalities = specificModalities + 1 }
                option.hidden = false
            } else {
                option.hidden = true;
            }
            option.selected = false;
            if ( modalities.length == 1 && specificModalities == 1 ){
                for ( option of $('#id_modality')[0].children ){
                    option.selected = modalities.includes(parseInt(option.value))
                }
            }
        }
    }

    if ( specificModalities > 1 ){ $('#id_modality option:first').prop('selected', true); }
    $('#id_modality').change();
}

function filter_operator(){
    let clinic = parseInt($('#idSelectedClinic').html());
    let showAll = $('#idShowAllOperatorsCheck')[0].checked;
    let operatorMap = JSON.parse($('#idClinicOperatorMap').html());

    var specificOperator = 0;
    if ( showAll || !operatorMap.hasOwnProperty(clinic.toString()) ){
        for ( option of $('#id_operator')[0].children ){ option.hidden = false; specificOperator += 1; }
    } else {
        let operators = operatorMap[clinic.toString()];
        for (option of $('#id_operator')[0].children){
            if ( option.value.toString() == "" || operators.includes(parseInt(option.value)) ){
                if ( option.value.toString() == "" ){specificOperator = specificOperator + 1}
                option.hidden = false
            } else {
                option.hidden = true;
            }
            option.selected = false;
            if ( operators.length == 1 && specificOperator == 1 ){
                for ( option of $('#id_operator')[0].children ){
                    option.selected = operators.includes(parseInt(option.value))
                }
            }
        }
    }

    if ( specificOperator > 1 ){ $('#id_operator option:first').prop('selected', true); }
}

$('#id_modality').change(function(event){
    let modality = $('#id_modality').val();
    let doseUnitMap = JSON.parse($('#idModalityDoseUnit').html());

    if (doseUnitMap.hasOwnProperty(modality.toString())) { $('#id_fluoro_dose_unit').val(doseUnitMap[modality.toString()]); }
});