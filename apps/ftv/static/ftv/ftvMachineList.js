$(document).ready(function() {
  $("#idMachineListTable").DataTable( {
    "ajax": $("#idUpdateDataUrl").html() + '?format=datatables',
    "columns": [
      { "data": "machine_name" },
      { "data": "model.model" },
      { "data": "machine_type.machine_type" },
      { "data": "room.room_number" },
      { "data": "room.protection_class.protection_class" },
      { "data": "installed_date" },
      { "data": "in_use" }
      ]
  });
});