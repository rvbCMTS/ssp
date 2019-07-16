$(document).ready(function() {
    (function( factory ) {
        "use strict";

        if ( typeof define === 'function' && define.amd ) {
            // AMD
            define( ['jquery'], function ( $ ) {
                return factory( $, window, document );
            } );
        }
        else if ( typeof exports === 'object' ) {
            // CommonJS
            module.exports = function (root, $) {
                if ( ! root ) {
                    root = window;
                }

                if ( ! $ ) {
                    $ = typeof window !== 'undefined' ?
                        require('jquery') :
                        require('jquery')( root );
                }

                return factory( $, root, root.document );
            };
        }
        else {
            // Browser
            factory( jQuery, window, document );
        }
    }
    (function( $, window, document ) {
        $.fn.dataTable.render.moment = function (from, to, locale) {
            // Argument shifting
            if (arguments.length === 1) {
                locale = 'en';
                to = from;
                from = 'YYYY-MM-DD';
            } else if (arguments.length === 2) {
                locale = 'en';
            }

            return function (d, type, row) {
                var m = window.moment(d, from, locale, true);

                // Order and type get a number value from Moment, everything else
                // sees the rendered value
                return m.format(type === 'sort' || type === 'type' ? 'x' : to);
            };
        };
    }));

    updateRoomList();
    getFilterData(null);

   $("#roomTable").DataTable({
       paging: false,
       columns:[
           {title: "Rumsid", data: "id"},
           {title: "Avdelning", data: "department"},
           {title: "Klinik", data: "clinic"},
           {title: "Rum", data: "room"},
           {title: "Klassificering", data: "classification"},
           {title: "Ritning", data: "drawing"},
       ],
       columnDefs: [
           {
               targets: 0,
               visible: false,
               searchable: false
           },
           {
               targets: 5,
               render: function(data, type, row, meta){ if ( data !== null ){data = '<a target="_blank" href="' + data + '">' + data.split('/').pop() + '</a>';} return data},
           }
       ],
       order: [[1, 'asc'], [2, 'asc'], [3, 'asc']],
   })
});

$("#idDepartmentCategory").change( function () {
    getFilterData('departmentCategory');
});


$("#idDepartment").change( function () {
    getFilterData('department');
});

$('.update-data').change(function() { updateRoomList(); });

function getFilterData(changedParam) {
    if ( changedParam !== 'department' ) {
        let departmentData = {filterType: 'department'};

        const depCatVal = $("#idDepartmentCategory").val();
        if ( changedParam === 'departmentCategory' && depCatVal > 0) { departmentData.deparmentCategory = depCatVal }

        $.ajax({
            url: $("#getRoomListUrl").html(),
            data: departmentData,
            dataType: 'json',
            success: function (result, status, xhr) {
                if ( changedParam !== 'departmentCategory' ){
                    var depCatSel = $("#idDepartmentCategory");
                    var depCatList = [];
                    depCatSel.empty();
                    depCatSel.append('<option value="null">Välj avdelningstyp</option>');
                }
                var depSel = $("#idDepartment");
                depSel.empty();
                depSel.append('<option value="null">Välj avdelning</option>');
                result.map( function (obj) {
                    depSel.append('<option value="' + obj.id + '">' + obj.departmentName + '</option>')
                    if ( changedParam !== 'departmentCategory' ) {
                        if ( depCatList.indexOf(obj.departmentCategory.id) < 0 ) {
                            depCatSel.append('<option value="' + obj.departmentCategory.id + '">' + obj.departmentCategory.category + '</option>');
                            depCatList.push(obj.departmentCategory.id);
                        }
                    }
                })
            },
            error: function (xhr, status, error) {
                console.log('Could not get department filter list')
            }
        });
    }

    if ( changedParam === 'department' ){
        const clinicData = { filterType: "clinic", department: $("#idDepartment").val() };
        $.ajax({
            url: $("#getRoomListUrl").html(),
            data: clinicData,
            dataType: 'json',
            success: function (result, status, xhr) {
                var clinSel = $("#idClinic");
                clinSel.empty();
                clinSel.append('<option value="null">Välj klinik</option>');
                result.map(function (obj) {
                    clinSel.append('<option value="' + obj.id + '">' + obj.clinicName + '</option>')
                })
            },
            error: function (xhr, status, error) {
                console.log('Could not get clinic filter list')
            }
        });
    }
    else {
        const clinicData = { filterType: "clinic" };
        $.ajax({
            url: $("#getRoomListUrl").html(),
            data: clinicData,
            dataType: 'json',
            success: function (result, status, xhr) {
                var clinSel = $("#idClinic");
                clinSel.empty();
                clinSel.append('<option value="null">Välj klinik</option>');
                result.map(function (obj) {
                    clinSel.append('<option value="' + obj.id + '">' + obj.clinicName + '</option>')
                })
            },
            error: function (xhr, status, error) {
                console.log('Could not get clinic filter list')
            }
        });
    }

    if ( changedParam !== 'department' ) {
        $.ajax({
            url: $("#getRoomListUrl").html(),
            data: {filterType: "classification"},
            dataType: 'json',
            success: function (result, status, xhr) {
                var classSel = $("#idClassification");
                classSel.empty();
                classSel.append('<option value="null">Välj klassificering</option>');
                result.map(function (obj) {
                    classSel.append('<option value="' + obj.id + '">' + obj.classification + '</option>')
                })
            },
            error: function (xhr, status, error) {
                console.log('Could not get classification filter list')
            }
        });
    }

}

function updateRoomList() {
    let idLoaderRow = $('#idLoaderRow');
    const departmentCategory = $('#idDepartmentCategory').val();
    const department = $('#idDepartment').val();
    const clinic = $('#idClinic').val();
    const classification = $('#idClassification').val();

    let queryData = {};
    departmentCategory != null && departmentCategory > 0 ? queryData.departmentCategory = departmentCategory : queryData = queryData;
    department != null && department > 0 ? queryData.department = department : queryData = queryData;
    clinic != null && clinic > 0 ? queryData.clinic = clinic : queryData = queryData;
    classification != null && classification > 0 ? queryData.classification = classification : queryData = queryData;

    if ( idLoaderRow.hasClass('hidden')) { idLoaderRow.removeClass('hidden')}
    $.ajax({
        url: $("#getRoomListUrl").html(),
        data: queryData,
        dataType: 'json',
        success: function (result, status, xhr) {
            if ( !idLoaderRow.hasClass('hidden')) { idLoaderRow.addClass('hidden')}
            _updateTable(result);
        },
        error: function (xhr, status, error) {
            if ( !idLoaderRow.hasClass('hidden')) { idLoaderRow.addClass('hidden')}
            alert('Kunde inte hämta data')
        }
    })
}

$('#roomTable').on( 'click', 'tr', function () {
    var table = $("#roomTable").DataTable();
    var id = table.row( this ).id();

    window.location.href = 'room/' + id;
} );

function _updateTable(data) {
    let table = $("#roomTable").DataTable();

    let tableData = [];

    data.map(function (obj) {
        tableData.push({
            DT_RowId: obj.id,
            id: obj.id,
            department: obj.clinic.department.departmentName,
            clinic: obj.clinic.clinicName,
            room: obj.room,
            classification: obj.shieldingClassification ? obj.shieldingClassification.classification : null,
            drawing: obj.drawing,
        })
    });

    table.clear().rows.add(tableData).draw();
}


