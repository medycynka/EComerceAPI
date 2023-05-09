function initializeDatatable(opt) {
    if (opt.preview === true) {
        opt.columns.pop();
    }

    const table = $(opt.elementId).DataTable({
        "language": {
            "sProcessing": "Przetwarzanie...",
            "sLengthMenu": "Pokaż _MENU_ pozycji",
            "sZeroRecords": "Nie znaleziono pasujących pozycji",
            "sInfoThousands": " ",
            "sInfo": "Pozycje od _START_ do _END_ z _TOTAL_ łącznie",
            "sInfoEmpty": "Pozycji 0 z 0 dostępnych",
            "sInfoFiltered": "(filtrowanie spośród _MAX_ dostępnych pozycji)",
            "sInfoPostFix": "",
            "sSearch": "Szukaj:",
            "sUrl": "",
            "oPaginate": {
                "sFirst": "Pierwsza",
                "sPrevious": "Poprzednia",
                "sNext": "Następna",
                "sLast": "Ostatnia"
            },
            "sEmptyTable": "Brak danych",
            "sLoadingRecords": "Wczytywanie...",
            "oAria": {
                "sSortAscending": ": aktywuj, by posortować kolumnę rosnąco",
                "sSortDescending": ": aktywuj, by posortować kolumnę malejąco"
            }
        },
        "buttons": [{extend: 'excelHtml5', exportOptions: opt.exportOptions}],
        "stateSave": opt.autoSave !== undefined ? opt.autoSave : false,
        "stateDuration": opt.stateCacheTimeout !== undefined ? opt.stateCacheTimeout : -1,
        "autoWidth": false,
        "columns": opt.columns,
        order: opt.order,
    });

    if (opt.useExcelExport === true || opt.useExcelExport === undefined) {
        const excelExportBtn = table.buttons()[0].node;
        if (opt.exportButtonTitle !== undefined && opt.exportButtonTitle !== '') {
            excelExportBtn.innerHTML = `<i class="fa fa-file-excel-o"></i>&emsp;${opt.exportButtonTitle}`;
        } else {
            excelExportBtn.innerHTML = `<i class="fa fa-file-excel-o"></i>&emsp;Eksportuj do pliku Excel`;
        }
        $(excelExportBtn).removeClass('btn');
        $(excelExportBtn).removeClass('btn-primary');
        $(excelExportBtn).addClass('secondary-button-manager');
        excelExportBtn.style.width = '100%';
        excelExportBtn.style.textAlign = 'left';

        const excelBtnParent = $('<li></li>');
        excelBtnParent.append(excelExportBtn);
        if (opt.addButtonBefore === true) {
            $(excelBtnParent).insertBefore(opt.excelButtonPredecessor);
        } else {
            $(excelBtnParent).insertAfter(opt.excelButtonPredecessor);
        }

        if (opt.addButtonListDivider === true) {
            $('<li class="divider"></li>').insertBefore(excelBtnParent);
        }
    }
    if (opt.addRowClickEvent === true) {
        $(opt.elementId + ' tbody').on('click', 'tr', function (e) {
            const target = $(e.target);
            if (target.children(":first").hasClass('information-action-dropdown') === false &&
                target.hasClass('information-action-dropdown') === false &&
                target.is('div') === false &&
                target.is('a') === false &&
                target.hasClass('dataTables_empty') === false) {
                opt.rowClickEvent(table, this, target);
            }
        });
    }

    table.on('order.dt', function (e, settings, ordArr) {
        sessionStorage.setItem('table-sorting-order', JSON.stringify([ordArr[0].col, ordArr[0].dir]))
    });

    return table;
}

function initializeAjaxDatatable(opt) {
    if (opt.preview === true) {
        opt.columns.pop();
    }

    const table = $(opt.elementId).on( 'init.dt', function (e, settings, json) {
        $(opt.elementId).off('init.dt');

        const tooltipsCells = $('[data-bs-toggle="tooltip"]');
        if (tooltipsCells.length > 0) {
            if(typeof tooltipsCells.tooltip === 'function'){
                tooltipsCells.tooltip()
            } else {
                // wait for document ready state
                $(document).ready(function () {
                    tooltipsCells.tooltip()
                })
            }
        }

        if (opt.useExcelExport === true || opt.useExcelExport === undefined) {
            const excelExportBtn = table.buttons()[0].node;
            if (opt.exportButtonTitle !== undefined && opt.exportButtonTitle !== '') {
                excelExportBtn.innerHTML = `<i class="fa fa-file-excel-o"></i>&emsp;${opt.exportButtonTitle}`;
            } else {
                excelExportBtn.innerHTML = `<i class="fa fa-file-excel-o"></i>&emsp;Eksportuj do pliku Excel`;
            }
            $(excelExportBtn).removeClass('btn');
            $(excelExportBtn).removeClass('btn-primary');
            $(excelExportBtn).addClass('secondary-button-manager');
            excelExportBtn.style.width = '100%';
            excelExportBtn.style.textAlign = 'left';

            const excelBtnParent = $('<li></li>');
            excelBtnParent.append(excelExportBtn);
            if (opt.addButtonBefore === true) {
                $(excelBtnParent).insertBefore(opt.excelButtonPredecessor);
            } else {
                $(excelBtnParent).insertAfter(opt.excelButtonPredecessor);
            }

            if (opt.addButtonListDivider === true) {
                $('<li class="divider"></li>').insertBefore(excelBtnParent);
            }
        }
        if (opt.addRowClickEvent === true) {
            $(opt.elementId + ' tbody').on('click', 'tr', function (e) {
                const target = $(e.target);
                if (target.children(":first").hasClass('information-action-dropdown') === false &&
                    target.hasClass('information-action-dropdown') === false &&
                    target.is('div') === false &&
                    target.is('a') === false &&
                    target.hasClass('dataTables_empty') === false) {
                    opt.rowClickEvent(table, this, target);
                }
            });
        }

        $(opt.elementId).on('order.dt', function (e, settings, ordArr) {
            console.log('Ordering: ', [ordArr[0].col, ordArr[0].dir]);
            sessionStorage.setItem('table-sorting-order', JSON.stringify([ordArr[0].col, ordArr[0].dir]))
        });
    }).DataTable({
        "language": {
            "sProcessing": "Przetwarzanie...",
            "sLengthMenu": "Pokaż _MENU_ pozycji",
            "sZeroRecords": "Nie znaleziono pasujących pozycji",
            "sInfoThousands": " ",
            "sInfo": "Pozycje od _START_ do _END_ z _TOTAL_ łącznie",
            "sInfoEmpty": "Pozycji 0 z 0 dostępnych",
            "sInfoFiltered": "(filtrowanie spośród _MAX_ dostępnych pozycji)",
            "sInfoPostFix": "",
            "sSearch": "Szukaj:",
            "sUrl": "",
            "oPaginate": {
                "sFirst": "Pierwsza",
                "sPrevious": "Poprzednia",
                "sNext": "Następna",
                "sLast": "Ostatnia"
            },
            "sEmptyTable": "Brak danych",
            "sLoadingRecords": "Wczytywanie...",
            "oAria": {
                "sSortAscending": ": aktywuj, by posortować kolumnę rosnąco",
                "sSortDescending": ": aktywuj, by posortować kolumnę malejąco"
            }
        },
        "buttons": [{extend: 'excelHtml5', exportOptions: opt.exportOptions}],
        "stateSave": opt.autoSave !== undefined ? opt.autoSave : false,
        "stateDuration": opt.stateCacheTimeout !== undefined ? opt.stateCacheTimeout : -1,
        "autoWidth": false,
        "columns": opt.columns,
        "ajax": opt.ajax,
        serverSide: false,
        deferRender: true,
        order: opt.order,
    });
    table.baseFilterUrl = opt.ajax.url;

    return table;
}