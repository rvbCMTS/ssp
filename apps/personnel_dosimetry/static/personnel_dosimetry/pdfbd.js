$(document).ready(function() {
    $("#measurementTableContainer").DataTable( {
        data: JSON.parse($('#tableData').html()),
        paging: false,
        searching: true,
        columns: [
            {title: "Mätdatum", target: 0}, {title: "Namn", target: 1}, {title: "Resultat", target: 2}, {title: "Kommentar", target: 3}
        ],
        order: [[0, "desc"]]
    } );
});