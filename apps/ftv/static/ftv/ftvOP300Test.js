$("#id_modality").change(function(event) {
  var modChange = $("#id_modality_change");
  modChange.val("1");
  modChange.change();
  modChange.val("0");
});



/*
$('#id_modality').change(function(event) {
  const modality = $('#id_modality').val();

  $.ajax({
    type: "GET",
    url: $("#idFormUpdateUrl").html(),
    data: {'modality': modality, 'updateForm': true},
    dataType: 'json',
    success: function (result, status, xhr) {
      if ($('#defaultFields').hasClass('hidden')) {
        $('#defaultFields').removeClass('hidden')
      }

      var panoramicFields = $('#idPanoramicTestFields');
      var cbctFields = $('#idCbctTestFields');
      var cefFields = $('#idCefTestFields');

      panoramicFields.empty();
      cbctFields.empty();
      cefFields.empty();

      $("#idSubmitContainer").empty().append(
        "<input type='submit' class='btn btn-primary btn-lg' value='Spara'>"
      )
    },
    error: function (xhr, status, error) {
      if (!$('#defaultFields').hasClass('hidden')) {
        $('#defaultFields').addClass('hidden')
      }
      
      $('#idInstruction').empty();

      $('#idPanoramicTestFields').empty();
      $('#idCbctTestFields').empty();
      $('#idCefTestFields').empty();

      $("#idReferences").empty();
    }
  });
});
*/