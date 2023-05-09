const loader = $("#global-loader");

//region New sale creation
let saleItemsTable = null;
let saleItemsSummaryPrice = null;
let saleSaleDate = null;
let saleIssueDate = null;
const quantityTypeMultiplier = {
    21: 1,
    22: 10,
    23: 100,
    24: 1000,
    25: 1,
};
const calendarConfig = {
    display: {
        components: {
            clock: true,
            hours: false,
            minutes: false,
            seconds: false,
            useTwentyfourHour: false,
        },
        buttons: {
            today: true,
            close: true,
            clear: true
        },
        icons: {
            time: 'fa fa-clock-o',
            date: 'fa fa-calendar',
            up: 'fa fa-arrow-up',
            down: 'fa fa-arrow-down',
            next: 'fa fa-chevron-right',
            previous: 'fa fa-chevron-left',
            today: 'fa fa-calendar-check-o',
            clear: 'fa fa-trash',
            close: 'fa fa-times',
        },
        viewMode: 'calendar',
    },
};
let saleCreationTemplate;
let realizationNumber;
let addFiles;

function initNewSaleTemplate(requesterName, requesterId, realization_number) {
    saleCreationTemplate = `
        <div class="form-row">
            <div class="form-group col-md-12 mb-0">
                <label class="form-label" id="newSaleCompanyLabel"><b>Firma</b></label>
                <div class="form-control fake-disabled-input-text" id="newSaleCompanySelect" data-requester-id="${requesterId}">${requesterName}</div>
            </div>
        </div>
        <div class="form-row" style="margin-top: 1rem;">
            <div class="col-3">
                <label class="form-label" id="newSaleSaleDate"><b>Data sprzedaży</b><span class="asteriskField">*</span></label>
                <div class="input-group" id="datetimepicker1" data-td-target-input="nearest" data-td-target-toggle="nearest">
                    <input type="text" class="form-control" name="sale_date" id="id_sale_date" data-td-target="#datetimepicker1" style="border-right: none;"/>
                    <div class="input-group-append date-select-btn" data-td-target="#datetimepicker1" data-td-toggle="datetimepicker">
                        <div class="input-group-text" style="height: 100%"><i class="fa fa-calendar"></i></div>
                    </div>
                </div>
            </div>
            <div class="col-3">
                <label class="form-label" id="newSaleIssueDate"><b>Data wystawienia</b><span class="asteriskField">*</span></label>
                <div class="input-group" id="datetimepicker2" data-td-target-input="nearest" data-td-target-toggle="nearest">
                    <input type="text" class="form-control" name="issue_date" id="id_issue_date" data-td-target="#datetimepicker2" style="border-right: none;"/>
                    <div class="input-group-append date-select-btn" data-td-target="#datetimepicker2" data-td-toggle="datetimepicker">
                        <div class="input-group-text" style="height: 100%"><i class="fa fa-calendar"></i></div>
                    </div>
                </div>
            </div>
            <div class="col-3">
                <div class="form-group col-md-12 mb-0">
                    <label class="form-label" id="newSalePaymentTimeLabel"><b>Termin płatności</b><span class="asteriskField">*</span></label>
                    ${paymentTimeSelectTemplate}
                </div>
            </div>
        </div>
        <div class="form-row" style="margin-top: 1rem;">
            <div class="col-3">
                <div class="form-group col-md-12 mb-0">
                    <label class="form-label" id="newSaleInvoiceSeriesSelectLabel"><b>Szablon numeracji</b><span class="asteriskField">*</span></label>
                    ${invoiceSeriesSelectTemplate}
                </div>
            </div>
            <div class="col-3">
                <div class="form-group col-md-12 mb-0">
                    <label class="form-label" id="newSaleStatusLabel"><b>Status</b><span class="asteriskField">*</span></label>
                    <select name="newSaleStatus" class="form-control form-select" id="newSaleStatus" tabindex="-1" aria-hidden="true">
                        <option value="0" selected="">Do zapłacenia</option>
                        <option value="1">Zapłacone</option>
                    </select>
                </div>
            </div>
            <div class="col-3">
                <div class="form-group col-md-12 mb-0">
                    <label class="form-label" id="newSaleActionLabel"><b>Wystaw natychmiast</b><span class="asteriskField">*</span></label>
                    <select name="newSaleAction" class="form-control form-select" id="newSaleAction" tabindex="-1" aria-hidden="true">
                        <option value="0" selected="">Nie</option>
                        <option value="1">Tak</option>
                    </select>
                </div>
            </div>
        </div>
        <div class="form-row" style="margin-top: 1rem;">
            <div class="form-group col-md-12 mb-0">
                <table class="table border mg-b-0">
                    <thead>
                        <tr>
                            <th style="width: 5%; text-align: center; vertical-align: middle;">Lp.</th>
                            <th style="width: 30%; text-align: left; vertical-align: middle;"">Produkt</th>
                            <th style="width: 12.5%; text-align: left; vertical-align: middle;"">Jednostka</th>
                            <th style="width: 7.5%; text-align: left; vertical-align: middle;"">Ilość</th>
                            <th style="width: 15%; text-align: left; vertical-align: middle;"">Cena netto</th>
                            <th style="width: 10%; text-align: left; vertical-align: middle;"">Stawka</th>
                            <th style="width: 15%; text-align: left; vertical-align: middle;"">Wart. brutto &asymp;</th>
                            <th style="width: 5%; text-align: center; vertical-align: middle;""><i class="fe fe-x" style="font-size: 1.25rem; cursor: pointer;" onclick="removeAllSaleItems()"></i></th>
                        </tr>
                    </thead>
                    <tbody id="newSaleNewSaleItem"></tbody>
                </table>
            </div>
        </div>
        <div class="form-row">
            <div class="col-2">
                <button type="button" class="add-sale-item-btn" onclick="addNewSaleItem()">DODAJ POZYCJĘ <i class="fe fe-plus" style="color: var(--primary-bg-color);"></i></button>
            </div>
            <div class="col-4"></div>
            <div class="col-4" style="padding-left: 4.5rem;"><b>Razem (PLN)</b></div>
            <div class="col-1" style="margin-left: 1rem;"><b id="newSaleSummaryPrice" style="float: right;">0.00</b></div>
        </div>
        <div class="form-row">
            <div class="form-group col-md-12 mb-0">
                <label class="form-label"><b>Opis</b></label>
                <textarea id="newSaleDescription" class="bootbox-input bootbox-input-textarea form-control" placeholder="Opis" rows="10" maxlength="2000"></textarea>
            </div>
        </div>
    `;
    realizationNumber = realization_number;
}

function nettoToBrutto(netto, vat) {
    if (vat < 100) {
        return (((100.0 + vat) / 100.0) * netto).toFixed(2);
    } else {
        return netto;
    }
}

function addSale(popUpTitle) {
    const salePopUp = bootbox.dialog({
        title: popUpTitle,
        message: saleCreationTemplate,
        onEscape: true,
        backdrop: false,
        centerVertical: true,
        locale: 'pl',
        size: 'xl',
        scrollable: true,
        buttons: {
            cancel: {
                label: '<i class="fa fa-times"></i> Anuluj',
                className: 'btn-danger',
                callback: function () {
                }
            },
            ok: {
                label: '<i class="fa fa-check"></i> Zatwierdź',
                className: 'btn-primary',
                callback: function () {
                    const data = serializeSaleData();
                    console.log(data);

                    const rows = saleItemsTable.getElementsByTagName('tr');
                    let areItemsValid = true;

                    for (let i = 0; i < data['sale_items'].length; i++) {
                        const cells = rows[i].getElementsByTagName('td');

                        if (data['sale_items'][i].name === '') {
                            areItemsValid = false;
                            addInvalidItemCss(cells[1].childNodes[0], 'Nazwa produktu nie może być pusta!', 'Nazwa produktu');
                        }
                        if (data['sale_items'][i].quantity === '' || Number(data['sale_items'][i].quantity < 1)) {
                            areItemsValid = false;
                            addInvalidItemCss(cells[3].childNodes[0], '1', '1');
                        }
                        if (data['sale_items'][i].netto === '' || Number(data['sale_items'][i].netto < 0)) {
                            areItemsValid = false;
                            addInvalidItemCss(cells[4].childNodes[0], '0.00', '0.00');
                        }
                    }

                    if (data['sell_date'] === '' || data['issue_date'] === '' || data['invoice_series'] === '' ||
                        data['payment_time'] === '' || data['sale_items'].length < 1 || areItemsValid === false) {
                        if (data['sell_date'] === '') {
                            addInvalidCss('input#id_sale_date', 'label#newSaleSaleDate');
                        }
                        if (data['issue_date'] === '') {
                            addInvalidCss('input#id_issue_date', 'label#newSaleIssueDate');
                        }
                        if (data['payment_time'] === '') {
                            addInvalidCss('select#newSalePaymentTime', 'label#newSalePaymentTimeLabel');
                        }
                        if (data['invoice_series'] === '') {
                            addInvalidCss('select#newSaleInvoiceSeriesSelect', 'label#newSaleInvoiceSeriesSelectLabel');
                        }
                        if (data['sale_items'].length === 0) {
                            $(saleItemsTable).parent().children('thead').children('tr').children().addClass('invalid-sale-items-table');
                        }

                        return false;
                    }

                    loader.show();

                    $.ajax({
                        url: window.location.pathname,
                        data: JSON.stringify(data),
                        type: 'POST',
                        headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
                        contentType: "application/json",
                        success: (data, textStatus, jqXHR) => {
                            console.log(textStatus, data);
                            if (data['status'] !== 'error') {
                                window.location.reload();
                            } else {
                                loader.hide();
                                bootbox.alert({
                                    title: `<span style="font-family: Roboto, sans-serif !important;"><i class="fa fa-exclamation"></i>&emsp;Błąd podczas wystawiania faktury!</span>`,
                                    message: `Error: ${data['msg']}\nStatus: ${data['status']} \nJeśli widzisz ten komunikat zgłoś to do programisty!`,
                                    onEscape: true,
                                    backdrop: false,
                                    centerVertical: true,
                                    size: 'large',
                                });
                            }
                        },
                        error: (jqXHR, textStatus, errorThrown) => {
                            console.log(textStatus, errorThrown);
                            loader.hide();
                            bootbox.alert({
                                title: `<span style="font-family: Roboto, sans-serif !important;"><i class="fa fa-exclamation"></i>&emsp;Błąd podczas wystawiania faktury!</span>`,
                                message: `Error: ${errorThrown}\nStatus: ${textStatus}`,
                                onEscape: true,
                                backdrop: false,
                                centerVertical: true,
                                size: 'large',
                            });
                        }
                    });
                }
            }
        },
        onShown: function(e) {
            addNewSaleItem('Usługa ' + realizationNumber)
        }
    });
    salePopUp.init(function () {
        saleItemsTable = $('tbody#newSaleNewSaleItem')[0];
        saleItemsSummaryPrice = $('b#newSaleSummaryPrice');
        const popUpContainer = $('div.bootbox-body');

        $('#newSalePaymentTime').select2({
            minimumResultsForSearch: Infinity,
            dropdownParent: popUpContainer,
        });
        $('#newSaleInvoiceSeriesSelect').select2({
            minimumResultsForSearch: Infinity,
            dropdownParent: popUpContainer,
        });
        $('#newSaleStatus').select2({
            minimumResultsForSearch: Infinity,
            dropdownParent: popUpContainer,
        });
        $('#newSaleAction').select2({
            minimumResultsForSearch: Infinity,
            dropdownParent: popUpContainer,
        });

        let saleSaleDateContainer = document.getElementById('datetimepicker1');
        saleSaleDate = new tempusDominus.TempusDominus(saleSaleDateContainer, calendarConfig);
        let saleIssueDateContainer = document.getElementById('datetimepicker2');
        saleIssueDate = new tempusDominus.TempusDominus(saleIssueDateContainer, calendarConfig);
    });

    return false;
}

function addInvalidCss(inputJsQuery, labelJsQuery) {
    const saleFromInput = $(inputJsQuery);
    const saleFromLabel = $(labelJsQuery);
    const calendar = saleFromInput.parent().find('div.input-group-text');
    const isItCalendar = calendar[0] !== undefined && calendar[1] !== null;

    saleFromInput.addClass('is-invalid');
    saleFromLabel.addClass('invalid-form-label-asterix');
    if (isItCalendar === true) {
        calendar.addClass('invalid-input-group-text');
    }

    if (saleFromInput.is('select')) {
        saleFromInput.parent().find('.select2-selection').attr('style', 'border-color: #f82649 !important;');
        saleFromInput.one('change', function () {
            saleFromInput.removeClass('is-invalid');
            saleFromLabel.removeClass('invalid-form-label-asterix');
            saleFromInput.parent().find('.select2-selection').attr('style', '');
        });
    } else if (isItCalendar === true) {
        saleFromInput.one('change', function () {
            saleFromInput.removeClass('is-invalid');
            saleFromLabel.removeClass('invalid-form-label-asterix');
            calendar.removeClass('invalid-input-group-text');
        });
    } else {
        saleFromInput.one('input', function () {
            saleFromInput.removeClass('is-invalid');
            saleFromLabel.removeClass('invalid-form-label-asterix');
        });
    }
}

function addInvalidItemCss(element, placeholderErrorMsg, placeholderDefaultMsg) {
    const saleItemFromInput = $(element);

    saleItemFromInput.addClass('is-invalid');
    saleItemFromInput.attr('placeholder', placeholderErrorMsg);
    saleItemFromInput.one('input', function () {
        $(this).removeClass('is-invalid');
        $(this).attr('placeholder', placeholderDefaultMsg);
    });
}

function addNewSaleItem(defaultName=undefined) {
    const rowTemplate = `<tr>
            <td style="text-align: center; vertical-align: middle;">${saleItemsTable.childNodes.length + 1}</td>
            <td id="saleItemName"><input type="text" name="saleItemName" maxlength="255" class="textInput form-control" id="id_sale_item_name" placeholder="Nazwa produktu" value="${defaultName ? defaultName : ''}"></td>
            <td id="saleItemQuantityType">${saleItemQuantityTypeSelectTemplate}</td>
            <td id="saleItemQuantity"><input type="number" name="saleItemQuantity" min="1" class="form-control" id="id_sale_item_quantity" value="1"></td>
            <td id="saleItemNettoPrice"><input type="number" name="saleItemNetto" min="0" class="form-control" id="id_sale_item_netto" placeholder="0.00"></td>
            <td id="saleItemVat">${paymentVatSelectTemplate}</td>
            <td id="saleItemBruttoPrice"><input type="number" name="saleItemNetto" min="0" class="form-control" id="id_sale_item_brutto" disabled placeholder="0.00"></td>
            <td style="text-align: center; vertical-align: middle;"><i class="fe fe-x" style="font-size: 1.25rem; cursor: pointer;" onclick="removeSaleItem(this)"></i></td>
        </tr>`;
    $(saleItemsTable).append($(rowTemplate));

    $(saleItemsTable).parent().children('thead').children('tr').children().removeClass('invalid-sale-items-table');

    const popUpContainer = $('div.bootbox-body');
    const qtSelect = $(saleItemsTable.lastElementChild).find('select#newSaleItemQuantityType');

    qtSelect.select2({
        minimumResultsForSearch: Infinity,
        dropdownParent: popUpContainer,
    });
    qtSelect.on('change', function () {
        fixSaleItemsTable(false);
    });

    const vatSelect = $(saleItemsTable.lastElementChild).find('select#newSaleItemVat');
    const nettoInput = $(saleItemsTable.lastElementChild).find('input#id_sale_item_netto');
    const bruttoInput = $(saleItemsTable.lastElementChild).find('input#id_sale_item_brutto');
    const quantityInput = $(saleItemsTable.lastElementChild).find('input#id_sale_item_quantity');

    vatSelect.select2({
        minimumResultsForSearch: Infinity,
        dropdownParent: popUpContainer,
    });
    vatSelect.change(function () {
        bruttoInput.val(nettoToBrutto(Number(nettoInput.val()), Number(this.value)));

        fixSaleItemsTable(false);
    });

    nettoInput.on('input', function () {
        const checkValue = $(this).val().split('.');
        let value = Number($(this).val());

        if (value >= 0.0) {
            if (checkValue.length > 1 && checkValue[1].length > 2) {
                $(this).val(Number($(this).val()).toFixed(2));
                value = Number(Number($(this).val()).toFixed(2));
            }

            bruttoInput.val(nettoToBrutto(value, Number($(saleItemsTable.lastElementChild).find('select#newSaleItemVat')[0].value)));
        } else {
            $(this).val('0.00');
            bruttoInput.val('0.00');
        }

        fixSaleItemsTable(false);
    });

    quantityInput.on('input', function () {
        const checkValue = $(this).val().split('.');
        const value = Number(checkValue[0]);

        if (value >= 0.0) {
            if (checkValue.length > 1 && checkValue[1].length > 2) {
                $(this).val(Number($(this).val()).toFixed(2));

                return;
            }
        } else {
            $(this).val('1.00');
        }

        fixSaleItemsTable(false);
    });

    return false;
}

function removeSaleItem(el) {
    $(el).closest('tr').remove();

    fixSaleItemsTable();

    return false;
}

function removeAllSaleItems() {
    $(saleItemsTable).empty();

    return false;
}

function fixSaleItemsTable(withIndexes = true) {
    let summaryPrice = 0.0;

    for (let i = 0; i < saleItemsTable.childNodes.length; i++) {
        if (withIndexes === true) {
            for (let j = 0; j < saleItemsTable.childNodes[i].childNodes.length; j++) {
                if (saleItemsTable.childNodes[i].childNodes[j].nodeName === 'TD') {
                    $(saleItemsTable.childNodes[i].childNodes[j]).text(i + 1);
                    break;
                }
            }
        }

        summaryPrice += Number($(saleItemsTable.childNodes[i]).children('td#saleItemBruttoPrice').children('input').val()) *
            Number($(saleItemsTable.childNodes[i]).children('td#saleItemQuantity').children('input').val()) *
            quantityTypeMultiplier[$(saleItemsTable.childNodes[i]).children('td#saleItemQuantityType').children('select')[0].value];
    }

    saleItemsSummaryPrice.text(summaryPrice.toFixed(2));
}

function serializeSaleData() {
    // new Date(saleSaleDate.viewDate).toLocaleDateString('pl-PL', {
    //     year: 'numeric',
    //     month: '2-digit',
    //     day: '2-digit'
    // })

    const data = {
        'company': $('div#newSaleCompanySelect').data('requester-id'),
        'sell_date': $('input#id_sale_date').val(),
        'issue_date': $('input#id_issue_date').val(),
        'payment_time': $('select#newSalePaymentTime')[0].value,
        'invoice_series': $('select#newSaleInvoiceSeriesSelect')[0].value,
        'paid': $('select#newSaleStatus')[0].value === '1',
        'issue_now': $('select#newSaleAction')[0].value === '1',
        'sale_items': [],
        'note': $('textarea#newSaleDescription').val(),
    };

    for (let i = 0; i < saleItemsTable.childNodes.length; i++) {
        const qt = $(saleItemsTable.childNodes[i]).children('td#saleItemQuantityType').children('select')[0].value;
        data['sale_items'].push({
            'name': $(saleItemsTable.childNodes[i]).children('td#saleItemName').children('input').val(),
            'quantity_type': qt,
            'quantity': quantityTypeMultiplier[qt] * Number($(saleItemsTable.childNodes[i]).children('td#saleItemQuantity').children('input').val()),
            'netto': $(saleItemsTable.childNodes[i]).children('td#saleItemNettoPrice').children('input').val(),
            'brutto': $(saleItemsTable.childNodes[i]).children('td#saleItemBruttoPrice').children('input').val(),
            'vat': $(saleItemsTable.childNodes[i]).children('td#saleItemVat').children('select')[0].value,
        });
    }

    return data;
}

//endregion

function FakeDataTransfer(files) {
    this.dropEffect = 'all';
    this.effectAllowed = 'all';
    this.items = [];
    this.types = ['Files'];
    this.getData = function () {
        return this.dt;
    };
    this.dt = new DataTransfer();
    for (let i = 0; i < files.length; i++) {
        this.dt.items.add(files[i]);
    }
}

const certificateStepManager = {
    1: function (popUpTitle, popUpBody) {
        bootbox.dialog({
            title: popUpTitle,
            message: popUpBody,
            onEscape: true,
            backdrop: false,
            centerVertical: true,
            locale: 'pl',
            size: 'large',
            buttons: {
                cancel: {
                    label: '<i class="fa fa-times"></i> Anuluj',
                    className: 'btn-danger',
                    callback: function () {
                    }
                },
                ok: {
                    label: '<i class="fa fa-check"></i> Potwierdź',
                    className: 'btn-primary',
                    callback: function () {
                        loader.show();

                        const certData = new FormData();

                        $.ajax({
                            url: window.location.pathname,
                            data: certData,
                            type: 'POST',
                            headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
                            contentType: false,
                            processData: false,
                            success: (data, textStatus, jqXHR) => {
                                console.log(textStatus, data);
                                window.location.reload();
                                // loader.hide()
                            },
                            error: (jqXHR, textStatus, errorThrown) => {
                                console.log(textStatus, errorThrown);
                                loader.hide();
                            }
                        });
                    }
                }
            }
        });
    },
    2: function (popUpTitle) {
        addSale(popUpTitle);
    },
    3: function (popUpTitle) {
        const stepProgressPopUp = bootbox.dialog({
            title: popUpTitle,
            message: `
                <div class="form-row">
                    <div class="col-6">
                        <label class="form-label requiredField" id="auditStartDateLabel"><b>Data startu audytu</b><span class="asteriskField">*</span></label>
                        <div class="input-group" id="datetimepicker1" data-td-target-input="nearest" data-td-target-toggle="nearest">
                            <input type="text" class="form-control" name="audit_start_date" id="id_audit_start_date" data-td-target="#datetimepicker1" style="border-right: none;"/>
                            <div class="input-group-append date-select-btn" data-td-target="#datetimepicker1" data-td-toggle="datetimepicker">
                                <div class="input-group-text" style="height: 100%"><i class="fa fa-calendar"></i></div>
                            </div>
                        </div>
                    </div>
                    <div class="col-6">
                        <label class="form-label requiredField" id="auditEndDateLabel"><b>Data końca audytu</b><span class="asteriskField">*</span></label>
                        <div class="input-group" id="datetimepicker2" data-td-target-input="nearest" data-td-target-toggle="nearest">
                            <input type="text" class="form-control" name="audit_end_date" id="id_audit_end_date" data-td-target="#datetimepicker2" style="border-right: none;"/>
                            <div class="input-group-append date-select-btn" data-td-target="#datetimepicker2" data-td-toggle="datetimepicker">
                                <div class="input-group-text" style="height: 100%"><i class="fa fa-calendar"></i></div>
                            </div>
                        </div>
                    </div>
                </div>
            `,
            onEscape: true,
            backdrop: false,
            centerVertical: true,
            locale: 'pl',
            size: 'large',
            buttons: {
                cancel: {
                    label: '<i class="fa fa-times"></i> Anuluj',
                    className: 'btn-danger',
                    callback: function () {
                    }
                },
                ok: {
                    label: '<i class="fa fa-check"></i> Potwierdź',
                    className: 'btn-primary',
                    callback: function () {
                        const auditStartDateValue = $('input#id_audit_start_date').val();
                        const auditEndDateValue = $('input#id_audit_end_date').val();
                        if (auditStartDateValue === '' || auditEndDateValue === '') {
                            if (auditStartDateValue === '') {
                                addInvalidCss('input#id_audit_start_date', 'label#auditStartDateLabel');
                            }
                            if (auditEndDateValue === '') {
                                addInvalidCss('input#id_audit_end_date', 'label#auditEndDateLabel');
                            }

                            return false;
                        }

                        loader.show();

                        const certData = new FormData();
                        certData.append('audit_start_date', auditStartDateValue);
                        certData.append('audit_end_date', auditEndDateValue);

                        $.ajax({
                            url: window.location.pathname,
                            data: certData,
                            type: 'POST',
                            headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
                            contentType: false,
                            processData: false,
                            success: (data, textStatus, jqXHR) => {
                                console.log(textStatus, data);
                                window.location.reload();
                                // loader.hide()
                            },
                            error: (jqXHR, textStatus, errorThrown) => {
                                console.log(textStatus, errorThrown);
                                loader.hide();
                            }
                        });
                    }
                }
            }
        });
        stepProgressPopUp.init(function () {
            let auditStartDateContainer = document.getElementById('datetimepicker1');
            let auditStartDateDate = new tempusDominus.TempusDominus(auditStartDateContainer, calendarConfig);
            let auditEndDateContainer = document.getElementById('datetimepicker2');
            let auditEndDateDate = new tempusDominus.TempusDominus(auditEndDateContainer, calendarConfig);
        });
    },
    4: function (popUpTitle) {
        const stepProgressPopUp = bootbox.dialog({
            title: popUpTitle,
            message: `
                <div class="form-row">
                    <div class="form-group col-md-12 mb-0">
                        <div id="div_id_audit_results" class="mb-3">
                            <label for="id_audit_results" class="form-label requiredField">Dodaj wyniki audytu<span class="asteriskField">*</span></label>
                            <input type="file" name="audit_results" class="form-control" accept="*" id="id_audit_results" multiple>
                        </div>
                    </div>
                </div>
            `,
            onEscape: true,
            backdrop: false,
            centerVertical: true,
            locale: 'pl',
            size: 'large',
            buttons: {
                cancel: {
                    label: '<i class="fa fa-times"></i> Anuluj',
                    className: 'btn-danger',
                    callback: function () {
                    }
                },
                ok: {
                    label: '<i class="fa fa-check"></i> Potwierdź',
                    className: 'btn-primary',
                    callback: function () {
                        const fileInput = document.getElementById('id_audit_results');
                        if (fileInput.files.length === 0) {
                            return false;
                        }

                        loader.show();

                        const certData = new FormData();
                        for (let i = 0; i < fileInput.files.length; i++) {
                            certData.append(`audit_result_${i}`, fileInput.files[i]);
                        }

                        $.ajax({
                            url: window.location.pathname,
                            data: certData,
                            type: 'POST',
                            headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
                            contentType: false,
                            processData: false,
                            success: (data, textStatus, jqXHR) => {
                                console.log(textStatus, data);
                                window.location.reload();
                                // loader.hide()
                            },
                            error: (jqXHR, textStatus, errorThrown) => {
                                console.log(textStatus, errorThrown);
                                loader.hide();
                            }
                        });
                    },
                }
            },
            onShow: function (e) {
                const filesUploader = $('#id_audit_results');
                const uploadedFiles = {};

                function sendFakeDropEvent() {
                    let fakeDropEvent = new DragEvent('drop');
                    Object.defineProperty(fakeDropEvent, 'dataTransfer', {
                        value: new FakeDataTransfer(Object.values(uploadedFiles))
                    });
                    filesUploader[0].dispatchEvent(fakeDropEvent);
                }

                const filesExtensions = new Set([]);
                filesUploader.FancyFileUpload({
                    accept: ['*'],
                    edit: false,
                    allowUpload: false,
                    originalInputId: '#id_files',
                    added: function (e, data) {
                        this.find('.ff_fileupload_actions button.ff_fileupload_start_upload').hide();

                        for (let i = 0; i < data.files.length; i++) {
                            // if (filesExtensions.has(data.files[i].type)) {
                            //     uploadedFiles[data.files[i].name] = data.files[i]
                            // }
                            uploadedFiles[data.files[i].name] = data.files[i];
                        }

                        sendFakeDropEvent();
                    },
                    fileRemoveOption: function (fileName) {
                        if (uploadedFiles[fileName] !== undefined) {
                            delete uploadedFiles[fileName];

                            sendFakeDropEvent();
                        }
                    },
                    langmap: {
                        'Starting upload...': 'Rozpoczynanie przesyłania...',
                        'Cancel upload and remove from list': 'Anuluj przesłanie i usuń z listy',
                        'Preview': 'Podgląd',
                        'No preview available': 'Podgląd jest niedostępny',
                        'Invalid file extension.': 'Blędne rozszerzenie pliku. ',
                        'Accepted extensions: ': 'Dopuszczalne rozszerzenia: ',
                        'File is too large.  Maximum file size is {0}.': 'Plik jest zbyt duży. Maksymalny rozmiar pliku to {0}',
                        'Start uploading': 'Rozpocznij przesyłanie',
                        'Remove from list': 'Usuń plik z listy',
                        '{0} of {1} | {2}%': '{0} z {1} | {2}%',
                        '{0} | Network error, retrying in a moment...': '{0} | Bląd połączenia, za chwilę rozpocznie się ponowna próba...',
                        'The upload was cancelled': 'Przesyłanie zostało anulowane',
                        'The upload failed.  {0} ({1})': 'Błąd przesyłania.  {0} ({1})',
                        'The upload failed.': 'Błąd przesyłania.',
                        'Upload completed': 'Zakończono przesyłanie',
                        'Browse, drag-and-drop, or paste files to upload': 'Przeglądaj, upuść, lub wklej pliki, które chcesz przesłać',
                    }
                });

                filesUploader.on('drop', function (e) {
                    if (e.originalEvent.dataTransfer && typeof e.originalEvent.dataTransfer.getData === 'function') {
                        filesUploader[0].files = e.originalEvent.dataTransfer.getData().files;
                    }
                });
            },
        });
    },
    5: function (popUpTitle) {
        const stepProgressPopUp = bootbox.dialog({
            title: popUpTitle,
            message: `
                <div class="form-row">
                    <div class="form-group col-md-12 mb-0">
                        <div id="div_id_documentation" class="mb-3">
                            <label for="id_documentation" class="form-label requiredField">Dodaj pliki dokumentacji<span class="asteriskField">*</span></label>
                            <input type="file" name="documentation" class="form-control" accept="application/pdf" id="id_documentation" multiple>
                        </div>
                    </div>
                </div>
            `,
            onEscape: true,
            backdrop: false,
            centerVertical: true,
            locale: 'pl',
            size: 'large',
            buttons: {
                cancel: {
                    label: '<i class="fa fa-times"></i> Anuluj',
                    className: 'btn-danger',
                    callback: function () {
                    }
                },
                ok: {
                    label: '<i class="fa fa-check"></i> Potwierdź',
                    className: 'btn-primary',
                    callback: function () {
                        const fileInput = document.getElementById('id_documentation');
                        if (fileInput.files.length === 0) {
                            return false;
                        }

                        loader.show();

                        const certData = new FormData();
                        for (let i = 0; i < fileInput.files.length; i++) {
                            certData.append(`documentation_${i}`, fileInput.files[i]);
                        }

                        $.ajax({
                            url: window.location.pathname,
                            data: certData,
                            type: 'POST',
                            headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
                            contentType: false,
                            processData: false,
                            success: (data, textStatus, jqXHR) => {
                                console.log(textStatus, data);
                                window.location.reload();
                                // loader.hide()
                            },
                            error: (jqXHR, textStatus, errorThrown) => {
                                console.log(textStatus, errorThrown);
                                loader.hide();
                            }
                        });
                    },
                }
            },
            onShow: function (e) {
                const filesUploader = $('#id_documentation');
                const uploadedFiles = {};

                function sendFakeDropEvent() {
                    let fakeDropEvent = new DragEvent('drop');
                    Object.defineProperty(fakeDropEvent, 'dataTransfer', {
                        value: new FakeDataTransfer(Object.values(uploadedFiles))
                    });
                    filesUploader[0].dispatchEvent(fakeDropEvent);
                }

                const filesExtensions = new Set([]);
                filesUploader.FancyFileUpload({
                    accept: ['*'],
                    edit: false,
                    allowUpload: false,
                    originalInputId: '#id_files',
                    added: function (e, data) {
                        this.find('.ff_fileupload_actions button.ff_fileupload_start_upload').hide();

                        for (let i = 0; i < data.files.length; i++) {
                            // if (filesExtensions.has(data.files[i].type)) {
                            //     uploadedFiles[data.files[i].name] = data.files[i]
                            // }
                            uploadedFiles[data.files[i].name] = data.files[i];
                        }

                        sendFakeDropEvent();
                    },
                    fileRemoveOption: function (fileName) {
                        if (uploadedFiles[fileName] !== undefined) {
                            delete uploadedFiles[fileName];

                            sendFakeDropEvent();
                        }
                    },
                    langmap: {
                        'Starting upload...': 'Rozpoczynanie przesyłania...',
                        'Cancel upload and remove from list': 'Anuluj przesłanie i usuń z listy',
                        'Preview': 'Podgląd',
                        'No preview available': 'Podgląd jest niedostępny',
                        'Invalid file extension.': 'Blędne rozszerzenie pliku. ',
                        'Accepted extensions: ': 'Dopuszczalne rozszerzenia: ',
                        'File is too large.  Maximum file size is {0}.': 'Plik jest zbyt duży. Maksymalny rozmiar pliku to {0}',
                        'Start uploading': 'Rozpocznij przesyłanie',
                        'Remove from list': 'Usuń plik z listy',
                        '{0} of {1} | {2}%': '{0} z {1} | {2}%',
                        '{0} | Network error, retrying in a moment...': '{0} | Bląd połączenia, za chwilę rozpocznie się ponowna próba...',
                        'The upload was cancelled': 'Przesyłanie zostało anulowane',
                        'The upload failed.  {0} ({1})': 'Błąd przesyłania.  {0} ({1})',
                        'The upload failed.': 'Błąd przesyłania.',
                        'Upload completed': 'Zakończono przesyłanie',
                        'Browse, drag-and-drop, or paste files to upload': 'Przeglądaj, upuść, lub wklej pliki, które chcesz przesłać',
                    }
                });

                filesUploader.on('drop', function (e) {
                    if (e.originalEvent.dataTransfer && typeof e.originalEvent.dataTransfer.getData === 'function') {
                        filesUploader[0].files = e.originalEvent.dataTransfer.getData().files;
                    }
                });
            },
        });
    },
    6: function (popUpTitle, popUpBody) {
        const stepProgressPopUp = bootbox.dialog({
            title: popUpTitle,
            message: popUpBody,
            onEscape: true,
            backdrop: false,
            centerVertical: true,
            locale: 'pl',
            size: 'large',
            buttons: {
                cancel: {
                    label: '<i class="fa fa-times"></i> Anuluj',
                    className: 'btn-danger',
                    callback: function () {
                    }
                },
                ok: {
                    label: '<i class="fa fa-check"></i> Potwierdź',
                    className: 'btn-primary',
                    callback: function () {
                        loader.show();

                        const certData = new FormData();

                        $.ajax({
                            url: window.location.pathname,
                            data: certData,
                            type: 'POST',
                            headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
                            contentType: false,
                            processData: false,
                            success: (data, textStatus, jqXHR) => {
                                console.log(textStatus, data);
                                window.location.reload();
                                // loader.hide()
                            },
                            error: (jqXHR, textStatus, errorThrown) => {
                                console.log(textStatus, errorThrown);
                                loader.hide();
                            }
                        });
                    }
                }
            }
        });
    },
    7: function (popUpTitle) {
        addSale(popUpTitle);
    },
    8: function (popUpTitle, popUpBody) {
        const stepProgressPopUp = bootbox.dialog({
            title: popUpTitle,
            message: `
                <div class="form-row">
                    <div class="form-group col-md-12 mb-0">
                        <div id="message" class="mb-3">
                            <label class="form-label"><b>${popUpBody}</b></label>
                        </div>
                    </div>
                </div>
                <div class="form-row">
                    <div class="form-group col-md-12 mb-0">
                        <div id="div_id_documentation" class="mb-3">
                            <label for="id_documentation" class="form-label"><b>Dodaj opcjonalne pliki potwierdzające zakończenie usługi</b></label>
                            <input type="file" name="documentation" class="form-control" accept="application/pdf" id="id_documentation" multiple>
                        </div>
                    </div>
                </div>
            `,
            onEscape: true,
            backdrop: false,
            centerVertical: true,
            locale: 'pl',
            size: 'large',
            buttons: {
                cancel: {
                    label: '<i class="fa fa-times"></i> Anuluj',
                    className: 'btn-danger',
                    callback: function () {
                    }
                },
                ok: {
                    label: '<i class="fa fa-check"></i> Potwierdź',
                    className: 'btn-primary',
                    callback: function () {
                        const fileInput = document.getElementById('id_documentation');

                        loader.show();

                        const certData = new FormData();
                        for (let i = 0; i < fileInput.files.length; i++) {
                            certData.append(`finalisation_${i}`, fileInput.files[i]);
                        }

                        // generate summary data

                        $.ajax({
                            url: window.location.pathname,
                            data: certData,
                            type: 'POST',
                            headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
                            contentType: false,
                            processData: false,
                            success: (data, textStatus, jqXHR) => {
                                console.log(textStatus, data);
                                window.location.reload();
                                // loader.hide()
                            },
                            error: (jqXHR, textStatus, errorThrown) => {
                                console.log(textStatus, errorThrown);
                                loader.hide();
                            }
                        });
                    },
                }
            },
            onShow: function (e) {
                const filesUploader = $('#id_documentation');
                const uploadedFiles = {};

                function sendFakeDropEvent() {
                    let fakeDropEvent = new DragEvent('drop');
                    Object.defineProperty(fakeDropEvent, 'dataTransfer', {
                        value: new FakeDataTransfer(Object.values(uploadedFiles))
                    });
                    filesUploader[0].dispatchEvent(fakeDropEvent);
                }

                const filesExtensions = new Set([]);
                filesUploader.FancyFileUpload({
                    accept: ['*'],
                    edit: false,
                    allowUpload: false,
                    originalInputId: '#id_files',
                    added: function (e, data) {
                        this.find('.ff_fileupload_actions button.ff_fileupload_start_upload').hide();

                        for (let i = 0; i < data.files.length; i++) {
                            uploadedFiles[data.files[i].name] = data.files[i];
                        }

                        sendFakeDropEvent();
                    },
                    fileRemoveOption: function (fileName) {
                        if (uploadedFiles[fileName] !== undefined) {
                            delete uploadedFiles[fileName];

                            sendFakeDropEvent();
                        }
                    },
                    langmap: {
                        'Starting upload...': 'Rozpoczynanie przesyłania...',
                        'Cancel upload and remove from list': 'Anuluj przesłanie i usuń z listy',
                        'Preview': 'Podgląd',
                        'No preview available': 'Podgląd jest niedostępny',
                        'Invalid file extension.': 'Blędne rozszerzenie pliku. ',
                        'Accepted extensions: ': 'Dopuszczalne rozszerzenia: ',
                        'File is too large.  Maximum file size is {0}.': 'Plik jest zbyt duży. Maksymalny rozmiar pliku to {0}',
                        'Start uploading': 'Rozpocznij przesyłanie',
                        'Remove from list': 'Usuń plik z listy',
                        '{0} of {1} | {2}%': '{0} z {1} | {2}%',
                        '{0} | Network error, retrying in a moment...': '{0} | Bląd połączenia, za chwilę rozpocznie się ponowna próba...',
                        'The upload was cancelled': 'Przesyłanie zostało anulowane',
                        'The upload failed.  {0} ({1})': 'Błąd przesyłania.  {0} ({1})',
                        'The upload failed.': 'Błąd przesyłania.',
                        'Upload completed': 'Zakończono przesyłanie',
                        'Browse, drag-and-drop, or paste files to upload': 'Przeglądaj, upuść, lub wklej pliki, które chcesz przesłać',
                    }
                });

                filesUploader.on('drop', function (e) {
                    if (e.originalEvent.dataTransfer && typeof e.originalEvent.dataTransfer.getData === 'function') {
                        filesUploader[0].files = e.originalEvent.dataTransfer.getData().files;
                    }
                });
            },
        });
    },
};
Object.seal(certificateStepManager);
Object.freeze(certificateStepManager);
Object.preventExtensions(certificateStepManager);

function initializeStepsManager(can_view_buttons, is_terminated, data){
    const certificateSteps = $('div#smartwizard');
    certificateSteps.smartWizard({
        selected: 0, // Initial selected step, 0 = first step
        theme: 'dots', // theme for the wizard, related css need to include for other than default theme
        justified: true, // Nav menu justification. true/false
        autoAdjustHeight: true, // Automatically adjust content height
        backButtonSupport: false, // Enable the back button support
        enableUrlHash: false, // Enable selection of the step based on url hash
        transition: {
            animation: 'fade', // Animation effect on navigation, none|fade|slideHorizontal|slideVertical|slideSwing|css(Animation CSS class also need to specify)
            speed: '400', // Animation speed. Not used if animation is 'css'
        },
        toolbar: {
            position: 'none', // none|top|bottom|both
            showNextButton: false, // show/hide a Next button
            showPreviousButton: false, // show/hide a Previous button
        },
        anchor: {
            enableNavigation: false, // Enable/Disable anchor navigation
            enableNavigationAlways: false, // Activates all anchors clickable always
            enableDoneState: true, // Add done state on visited steps
            markPreviousStepsAsDone: true, // When a step selected by url hash, all previous steps are marked done
            unDoneOnBackNavigation: false, // While navigate back, done state will be cleared
            enableDoneStateNavigation: false // Enable/Disable the done state navigation
        },
        keyboard: {
            keyNavigation: false, // Enable/Disable keyboard navigation(left and right keys are used if enabled)
            keyLeft: [37], // Left key code
            keyRight: [39] // Right key code
        },
        lang: { // Language variables for button
            next: 'Dalej',
            previous: 'Cofnij'
        },
    });

    const table = initializeDatatable({
        elementId: '#data-table1',
        columns: [
            {"searchable": true, 'width': '35%'},
            {"searchable": false, 'width': '7.5%'},
            {"searchable": false, 'width': '7.5%'},
            {"searchable": false, 'orderable': true, 'width': '7.5%'},
            {"searchable": false, 'width': '7.5%'},
            {"searchable": true, 'width': '5%'},
            {"searchable": false, 'orderable': false, 'width': '5%'},
        ],
        order: [[0, 'desc']],
        addRowClickEvent: true,
        rowClickEvent: (dataTable, row, target) => {
            const objectId = $(dataTable.row(row).nodes()[0]).data('invoice-id');
            console.log(objectId);

            if (!target.is('input') && objectId !== undefined && objectId !== null && objectId !== '') {
                if (typeof objectId === 'string') {
                    console.log(objectId.replaceAll(/\s/g, ''));
                    window.location = window.location.href.replace(`certificates/${data.objId}/`, 'invoices/' + objectId.replaceAll(/\s/g, ''));
                } else {
                    console.log(objectId);
                    window.location = window.location.href.replace(`certificates/${data.objId}/`, 'invoices/' + objectId);
                }
            }
        },
    });

    addFiles = function() {
        if (!is_terminated) {
            let promptBody = `<div class="form-row">
                            <div class="form-group col-md-12 mb-0">
                                <div id="div_id_files" class="mb-3">
                                    <label for="id_files" class="form-label">Dodaj nowe pliki</label>
                                    <input type="file" name="files" class="form-control" accept="*" id="id_files" multiple>
                                </div>
                            </div>
                        </div>`;
            let companiesManager = bootbox.confirm({
                title: `<span style="font-family: Roboto, sans-serif !important;"><i class="fe fe-file-plus"></i>&emsp;Dodaj pliki</span>`,
                message: promptBody,
                onEscape: true,
                backdrop: true,
                centerVertical: true,
                size: 'large',
                buttons: {
                    cancel: {
                        label: '<i class="fa fa-times"></i> Anuluj',
                        className: 'btn-danger'
                    },
                    confirm: {
                        label: '<i class="fa fa-check"></i> Potwierdź',
                        className: 'btn-primary'
                    }
                },
                callback: function (result) {
                    if (result === true) {
                        loader.show();

                        const uploaded_files = $('#id_files')[0].files;
                        console.log(uploaded_files);
                        const files = new FormData();
                        for (let i = 0; i < uploaded_files.length; i++) {
                            files.append('file_' + i, uploaded_files[i])
                        }
                        files.append('type', 'files_upload');

                        $.ajax({
                            url: window.location.pathname,
                            data: files,
                            type: 'POST',
                            headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
                            contentType: false,
                            processData: false,
                            success: (data, textStatus, jqXHR) => {
                                window.location.reload()
                            },
                            error: (jqXHR, textStatus, errorThrown) => {
                                loader.hide();
                                console.log(textStatus, errorThrown)
                            }
                        })
                    }
                },
                onShow: function (e) {
                    const filesUploader = $('#id_files');
                    const uploadedFiles = {};

                    function sendFakeDropEvent() {
                        let fakeDropEvent = new DragEvent('drop');
                        Object.defineProperty(fakeDropEvent, 'dataTransfer', {
                            value: new FakeDataTransfer(Object.values(uploadedFiles))
                        });
                        filesUploader[0].dispatchEvent(fakeDropEvent)
                    }

                    filesUploader.FancyFileUpload({
                        accept: ['*'],
                        edit: false,
                        allowUpload: false,
                        originalInputId: '#id_files',
                        added: function (e, data) {
                            this.find('.ff_fileupload_actions button.ff_fileupload_start_upload').hide();

                            for (let i = 0; i < data.files.length; i++) {
                                uploadedFiles[data.files[i].name] = data.files[i]
                            }

                            sendFakeDropEvent()
                        },
                        fileRemoveOption: function (fileName) {
                            if (uploadedFiles[fileName] !== undefined) {
                                delete uploadedFiles[fileName];

                                sendFakeDropEvent()
                            }
                        },
                        langmap: {
                            'Starting upload...': 'Rozpoczynanie przesyłania...',
                            'Cancel upload and remove from list': 'Anuluj przesłanie i usuń z listy',
                            'Preview': 'Podgląd',
                            'No preview available': 'Podgląd jest niedostępny',
                            'Invalid file extension.': 'Blędne rozszerzenie pliku.',
                            'File is too large.  Maximum file size is {0}.': 'Plik jest zbyt duży. Maksymalny rozmiar pliku to {0}',
                            'Start uploading': 'Rozpocznij przesyłanie',
                            'Remove from list': 'Usuń plik z listy',
                            '{0} of {1} | {2}%': '{0} z {1} | {2}%',
                            '{0} | Network error, retrying in a moment...': '{0} | Bląd połączenia, za chwilę rozpocznie się ponowna próba...',
                            'The upload was cancelled': 'Przesyłanie zostało anulowane',
                            'The upload failed.  {0} ({1})': 'Błąd przesyłania.  {0} ({1})',
                            'The upload failed.': 'Błąd przesyłania.',
                            'Upload completed': 'Zakończono przesyłanie',
                            'Browse, drag-and-drop, or paste files to upload': 'Przeglądaj, upuść, lub wklej pliki, które chcesz przesłać',
                        }
                    });

                    filesUploader.on('drop', function (e) {
                        if (e.originalEvent.dataTransfer && typeof e.originalEvent.dataTransfer.getData === 'function') {
                            filesUploader[0].files = e.originalEvent.dataTransfer.getData().files
                        }
                    })
                },
            })
        }

        return false
    };

    $(document).ready(function () {
        certificateSteps.smartWizard('goToStep', Number(data.objStatus) - 1, true);

        if (is_terminated) {
            const progressElements = document.querySelectorAll('.sw-theme-dots>.nav .nav-link.active, .sw-theme-dots>.nav .nav-link.done, .sw-theme-dots>.nav, .sw>.progress>.progress-bar');
            for (let i = 0; i < progressElements.length; i++) {
                progressElements[i].classList.add('terminated');
            }
        }

        if (can_view_buttons) {
            const nextStepBtn = document.querySelector('[id^="stepProgressBtn_"]');
            if (nextStepBtn && !nextStepBtn.classList.contains('disabled')) {
                nextStepBtn.onclick = function () {
                    const stepNumber = Number(this.id.replace('stepProgressBtn_', ''));
                    console.log(stepNumber);

                    if (stepNumber > 0 && stepNumber < 9){
                        certificateStepManager[stepNumber](
                            data.stepPopUp[stepNumber][0],
                            data.stepPopUp[stepNumber][1],
                        )
                    }

                    return false
                };
            }

            $('button#certTerminateBtn').click(function () {
                bootbox.dialog({
                    title: '<i class="fe fe-alert-triangle" style="color: #f82649;"></i>&emsp;Czy na pewno chcesz zakończyć proces?',
                    message: 'Zakończenie tego procesu spowoduje natychmiastowe przerwanie realizacji tego zamówienia, a decyzji tej nie da się cofnąć!',
                    onEscape: true,
                    backdrop: false,
                    centerVertical: true,
                    locale: 'pl',
                    size: 'large',
                    buttons: {
                        cancel: {
                            label: '<i class="fa fa-times"></i> Anuluj',
                            className: 'btn-danger',
                            callback: function () {
                            }
                        },
                        ok: {
                            label: '<i class="fa fa-check"></i> Potwierdź',
                            className: 'btn-primary',
                            callback: function () {
                                loader.show();
                                const terminationData = new FormData();
                                terminationData.append('type', 'terminate');

                                $.ajax({
                                    url: window.location.pathname,
                                    data: terminationData,
                                    type: 'POST',
                                    headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
                                    contentType: false,
                                    processData: false,
                                    success: (data, textStatus, jqXHR) => {
                                        window.location.reload()
                                    },
                                    error: (jqXHR, textStatus, errorThrown) => {
                                        loader.hide();
                                        console.log(textStatus, errorThrown)
                                    }
                                });
                            }
                        }
                    }
                });

                return false
            });

            $('button#auditDatesChangeBtn').click(function () {
                const auditDatesChanger = bootbox.dialog({
                    title: '<i class="fe fe-clock"></i>&emsp;Zmień daty audytu',
                    message: `
                        <div class="form-row">
                            <div class="col-6">
                                <label class="form-label requiredField" id="auditStartDateLabel"><b>Data startu audytu</b><span class="asteriskField">*</span></label>
                                <div class="input-group" id="datetimepicker1" data-td-target-input="nearest" data-td-target-toggle="nearest">
                                    <input type="text" class="form-control" name="audit_start_date" id="id_audit_start_date" data-td-target="#datetimepicker1" style="border-right: none;"/>
                                    <div class="input-group-append date-select-btn" data-td-target="#datetimepicker1" data-td-toggle="datetimepicker">
                                        <div class="input-group-text" style="height: 100%"><i class="fa fa-calendar"></i></div>
                                    </div>
                                </div>
                            </div>
                            <div class="col-6">
                                <label class="form-label requiredField" id="auditEndDateLabel"><b>Data końca audytu</b><span class="asteriskField">*</span></label>
                                <div class="input-group" id="datetimepicker2" data-td-target-input="nearest" data-td-target-toggle="nearest">
                                    <input type="text" class="form-control" name="audit_end_date" id="id_audit_end_date" data-td-target="#datetimepicker2" style="border-right: none;"/>
                                    <div class="input-group-append date-select-btn" data-td-target="#datetimepicker2" data-td-toggle="datetimepicker">
                                        <div class="input-group-text" style="height: 100%"><i class="fa fa-calendar"></i></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `,
                    onEscape: true,
                    backdrop: false,
                    centerVertical: true,
                    locale: 'pl',
                    size: 'large',
                    buttons: {
                        cancel: {
                            label: '<i class="fa fa-times"></i> Anuluj',
                            className: 'btn-danger',
                            callback: function () {
                            }
                        },
                        ok: {
                            label: '<i class="fa fa-check"></i> Potwierdź',
                            className: 'btn-primary',
                            callback: function () {
                                const auditStartDateValue = $('input#id_audit_start_date').val();
                                const auditEndDateValue = $('input#id_audit_end_date').val();
                                if (auditStartDateValue === '' || auditEndDateValue === '') {
                                    if (auditStartDateValue === '') {
                                        addInvalidCss('input#id_audit_start_date', 'label#auditStartDateLabel');
                                    }
                                    if (auditEndDateValue === '') {
                                        addInvalidCss('input#id_audit_end_date', 'label#auditEndDateLabel');
                                    }

                                    return false;
                                }

                                loader.show();

                                const certData = new FormData();
                                certData.append('audit_start_date', auditStartDateValue);
                                certData.append('audit_end_date', auditEndDateValue);
                                certData.append('type', 'audit_change_dates');

                                $.ajax({
                                    url: window.location.pathname,
                                    data: certData,
                                    type: 'POST',
                                    headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
                                    contentType: false,
                                    processData: false,
                                    success: (data, textStatus, jqXHR) => {
                                        console.log(textStatus, data);
                                        window.location.reload();
                                        // loader.hide()
                                    },
                                    error: (jqXHR, textStatus, errorThrown) => {
                                        console.log(textStatus, errorThrown);
                                        loader.hide();
                                    }
                                });
                            }
                        }
                    }
                });
                auditDatesChanger.init(function () {
                    let auditStartDateContainer = document.getElementById('datetimepicker1');
                    let auditStartDateDate = new tempusDominus.TempusDominus(auditStartDateContainer, calendarConfig);
                    let auditEndDateContainer = document.getElementById('datetimepicker2');
                    let auditEndDateDate = new tempusDominus.TempusDominus(auditEndDateContainer, calendarConfig);
                });

                return false
            });
        }
    })
}