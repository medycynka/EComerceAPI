const globalLoader = $('#global-loader');

//region Common variables & functions
const dataTableLanguageOpt = {
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
};
const changesInTabs = {
    tab2: {
        newRows: new Set(),
        editedRows: new Set(),
        removedRows: new Set(),
    },
    tab3: {
        newRows: new Set(),
        editedRows: new Set(),
        removedRows: new Set(),
    },
    tab4: {
        newRows: new Set(),
        editedRows: new Set(),
        removedRows: new Set(),
    },
};
const fileMimeTypes = {
    abs: "audio/x-mpeg",
    ai: "application/postscript",
    aif: "audio/x-aiff",
    aifc: "audio/x-aiff",
    aiff: "audio/x-aiff",
    aim: "application/x-aim",
    art: "image/x-jg",
    asf: "video/x-ms-asf",
    asx: "video/x-ms-asf",
    au: "audio/basic",
    avi: "video/x-msvideo",
    avx: "video/x-rad-screenplay",
    bcpio: "application/x-bcpio",
    bin: "application/octet-stream",
    bmp: "image/bmp",
    body: "text/html",
    cdf: "application/x-cdf",
    cer: "application/pkix-cert",
    class: "application/java",
    cpio: "application/x-cpio",
    csh: "application/x-csh",
    css: "text/css",
    dib: "image/bmp",
    doc: "application/msword",
    dtd: "application/xml-dtd",
    dv: "video/x-dv",
    dvi: "application/x-dvi",
    eot: "application/vnd.ms-fontobject",
    eps: "application/postscript",
    etx: "text/x-setext",
    exe: "application/octet-stream",
    gif: "image/gif",
    gtar: "application/x-gtar",
    gz: "application/x-gzip",
    hdf: "application/x-hdf",
    hqx: "application/mac-binhex40",
    htc: "text/x-component",
    htm: "text/html",
    html: "text/html",
    ief: "image/ief",
    jad: "text/vnd.sun.j2me.app-descriptor",
    jar: "application/java-archive",
    java: "text/x-java-source",
    jnlp: "application/x-java-jnlp-file",
    jpe: "image/jpeg",
    jpeg: "image/jpeg",
    jpg: "image/jpeg",
    js: "application/javascript",
    jsf: "text/plain",
    json: "application/json",
    jspf: "text/plain",
    kar: "audio/midi",
    latex: "application/x-latex",
    m3u: "audio/x-mpegurl",
    mac: "image/x-macpaint",
    man: "text/troff",
    mathml: "application/mathml+xml",
    me: "text/troff",
    mid: "audio/midi",
    midi: "audio/midi",
    mif: "application/x-mif",
    mov: "video/quicktime",
    movie: "video/x-sgi-movie",
    mp1: "audio/mpeg",
    mp2: "audio/mpeg",
    mp3: "audio/mpeg",
    mp4: "video/mp4",
    mpa: "audio/mpeg",
    mpe: "video/mpeg",
    mpeg: "video/mpeg",
    mpega: "audio/x-mpeg",
    mpg: "video/mpeg",
    mpv2: "video/mpeg2",
    ms: "application/x-wais-source",
    nc: "application/x-netcdf",
    oda: "application/oda",
    odb: "application/vnd.oasis.opendocument.database",
    odc: "application/vnd.oasis.opendocument.chart",
    odf: "application/vnd.oasis.opendocument.formula",
    odg: "application/vnd.oasis.opendocument.graphics",
    odi: "application/vnd.oasis.opendocument.image",
    odm: "application/vnd.oasis.opendocument.text-master",
    odp: "application/vnd.oasis.opendocument.presentation",
    ods: "application/vnd.oasis.opendocument.spreadsheet",
    odt: "application/vnd.oasis.opendocument.text",
    otg: "application/vnd.oasis.opendocument.graphics-template",
    oth: "application/vnd.oasis.opendocument.text-web",
    otp: "application/vnd.oasis.opendocument.presentation-template",
    ots: "application/vnd.oasis.opendocument.spreadsheet-template",
    ott: "application/vnd.oasis.opendocument.text-template",
    ogx: "application/ogg",
    ogv: "video/ogg",
    oga: "audio/ogg",
    ogg: "audio/ogg",
    otf: "application/x-font-opentype",
    spx: "audio/ogg",
    flac: "audio/flac",
    anx: "application/annodex",
    axa: "audio/annodex",
    axv: "video/annodex",
    xspf: "application/xspf+xml",
    pbm: "image/x-portable-bitmap",
    pct: "image/pict",
    pdf: "application/pdf",
    pgm: "image/x-portable-graymap",
    pic: "image/pict",
    pict: "image/pict",
    pls: "audio/x-scpls",
    png: "image/png",
    pnm: "image/x-portable-anymap",
    pnt: "image/x-macpaint",
    ppm: "image/x-portable-pixmap",
    ppt: "application/vnd.ms-powerpoint",
    pps: "application/vnd.ms-powerpoint",
    ps: "application/postscript",
    psd: "image/vnd.adobe.photoshop",
    qt: "video/quicktime",
    qti: "image/x-quicktime",
    qtif: "image/x-quicktime",
    ras: "image/x-cmu-raster",
    rdf: "application/rdf+xml",
    rgb: "image/x-rgb",
    rm: "application/vnd.rn-realmedia",
    roff: "text/troff",
    rtf: "application/rtf",
    rtx: "text/richtext",
    sfnt: "application/font-sfnt",
    sh: "application/x-sh",
    shar: "application/x-shar",
    sit: "application/x-stuffit",
    snd: "audio/basic",
    src: "application/x-wais-source",
    sv4cpio: "application/x-sv4cpio",
    sv4crc: "application/x-sv4crc",
    svg: "image/svg+xml",
    svgz: "image/svg+xml",
    swf: "application/x-shockwave-flash",
    t: "text/troff",
    tar: "application/x-tar",
    tcl: "application/x-tcl",
    tex: "application/x-tex",
    texi: "application/x-texinfo",
    texinfo: "application/x-texinfo",
    tif: "image/tiff",
    tiff: "image/tiff",
    tr: "text/troff",
    tsv: "text/tab-separated-values",
    ttf: "application/x-font-ttf",
    txt: "text/plain",
    ulw: "audio/basic",
    ustar: "application/x-ustar",
    vxml: "application/voicexml+xml",
    xbm: "image/x-xbitmap",
    xht: "application/xhtml+xml",
    xhtml: "application/xhtml+xml",
    xls: "application/vnd.ms-excel",
    xml: "application/xml",
    xpm: "image/x-xpixmap",
    xsl: "application/xml",
    xslt: "application/xslt+xml",
    xul: "application/vnd.mozilla.xul+xml",
    xwd: "image/x-xwindowdump",
    vsd: "application/vnd.visio",
    wav: "audio/x-wav",
    wbmp: "image/vnd.wap.wbmp",
    wml: "text/vnd.wap.wml",
    wmlc: "application/vnd.wap.wmlc",
    wmls: "text/vnd.wap.wmlsc",
    wmlscriptc: "application/vnd.wap.wmlscriptc",
    wmv: "video/x-ms-wmv",
    woff: "application/font-woff",
    woff2: "application/font-woff2",
    wrl: "model/vrml",
    wspolicy: "application/wspolicy+xml",
    z: "application/x-compress",
    zip: "application/zip",
    docx: "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
};

function getTabIdFromLink(href) {
    return href.split('#').slice(-1)[0];
}

function hasTabAnyChanges(tabId) {
    if (changesInTabs[tabId] !== undefined && changesInTabs[tabId] !== null) {
        return (changesInTabs[tabId].newRows.size + changesInTabs[tabId].editedRows.size + changesInTabs[tabId].removedRows.size) > 0;
    }

    return false;
}

function sendTabData(serializedData) {
    $.ajax({
        url: window.location.pathname,
        data: JSON.stringify(serializedData),
        type: 'PUT',
        headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
        contentType: "application/json",
        success: (data, textStatus, jqXHR) => {
            window.location.reload();
        },
        error: (jqXHR, textStatus, errorThrown) => {
            console.log(textStatus, errorThrown);
        }
    });
}

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

function sendOrRemoveFiles(formData) {
    $.ajax({
        url: window.location.pathname,
        data: formData,
        type: 'POST',
        headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
        contentType: false,
        processData: false,
        success: (data, textStatus, jqXHR) => {
            window.location.reload();
        },
        error: (jqXHR, textStatus, errorThrown) => {
            console.log(textStatus, errorThrown);
        }
    });
}

const tabs = document.querySelectorAll('li.tab-fit-btn');
for (let i = 0; i < tabs.length; i++) {
    tabs[i].childNodes[0].addEventListener('shown.bs.tab', function (event) {
        // let newTab = getTabIdFromLink(event.target.href) // newly activated tab
        // let prevTab = getTabIdFromLink(event.relatedTarget.href) // previous active tab

        if (hasTabAnyChanges(getTabIdFromLink(event.relatedTarget.href)) === true && event.relatedTarget.childNodes.length === 1) {
            const tabBtn = $(event.relatedTarget);
            const tabName = tabBtn.text().trim();
            tabBtn.append($('<i class="fe fe-edit tab-not-saved"></i>'));
            bootbox.alert({
                title: `<i class="fa fa-exclamation-triangle" style="color: red;"></i>&emsp; Uwaga!`,
                message: `W zakładce \"${tabName}\" są niezapisane zmiany. Odświeżenie strony lub zapisanie danych z innej zakładki spowoduje <b>utratę danych!<b>`,
                onEscape: true,
                backdrop: true,
                centerVertical: true,
                locale: 'pl',
            });
        }
    });
}
//endregion

//region Services
const servicesTable = $('#data-table1').DataTable({
    "language": dataTableLanguageOpt,
    "stateSave": true,
    "autoWidth": false,
    "columns": [
        {"searchable": true, 'width': '30%'},
        {"searchable": true, 'width': '60%'},
        {
            "searchable": false, 'orderable': false, 'width': '10%', 'render': function (data, type, row) {
                return `<div class="information-action-dropdown dataTables_empty" style="width: 100%; height: 100%;">
                            <button class="information-action-dropdown-btn dataTables_empty">...</button>
                            <div class="information-action-dropdown-content dataTables_empty">
                                <a href="#" onclick="editServiceRow(this)"><i class="fe fe-edit mr-2"></i>&ensp;Edytuj</a>
                                <a href="#" style="color: #6C757D;" onclick="removeServiceRow(this)" data-service-name="${data[0]}"><i class="fe fe-trash-2 mr-2"></i>&ensp;Usuń</a>
                            </div>
                        </div>`;
            }
        },
    ],
});
const servicesToRemove = new Set();

function addService() {
    const serviceAddPopUp = bootbox.dialog({
        title: 'Podaj dane nowej usługi.',
        message: `
            <label class="form-label" id="newServiceNameLabel">Nazwa<span class="asteriskField">*</span></label>
            <input type="text" id="newServiceName" class="bootbox-input bootbox-input-textarea form-control" required placeholder="Nazwa usługi" maxlength="128"/>
            <p></p>
            <label class="form-label">Opis usługi</label>
            <textarea id="newServiceDescription" class="bootbox-input bootbox-input-textarea form-control" placeholder="Opis usługi" rows="5" maxlength="2000"></textarea>
        `,
        onEscape: true,
        backdrop: true,
        centerVertical: true,
        locale: 'pl',
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
                    let serviceName = $('#newServiceName');

                    if (serviceName.val() == null || serviceName.val().replace(/^\s+|\s+$/gm, '') === '') {
                        serviceName.attr('placeholder', "Nazwa usługi nie może być pusta!");
                        serviceName.addClass('is-invalid');
                        $('label#newServiceNameLabel').addClass('invalid-form-label-asterix');
                        serviceName.on('input', function () {
                            serviceName.removeClass('is-invalid');
                            $('label#newServiceNameLabel').removeClass('invalid-form-label-asterix');
                            serviceName.off('input');
                        });

                        return false;
                    } else {
                        const serviceDescription = $('#newServiceDescription');
                        changesInTabs['tab2'].newRows.add(servicesTable.data().length);
                        servicesTable.row.add([serviceName.val().trim(), serviceDescription.val().trim(), [
                            serviceName.val().trim(), true
                        ]]).draw(false);
                    }
                }
            }
        }
    });

    return false;
}

function editServiceRow(el) {
    const row = $(el).closest('tr');
    const rowElements = row.children();
    const name = $(rowElements[0]).text();
    const description = $(rowElements[1]).text();

    const serviceAddPopUp = bootbox.dialog({
        title: 'Edytuj dane usługi.',
        message: `
            <label class="form-label" id="newServiceNameLabel">Nazwa<span class="asteriskField">*</span></label>
            <input type="text" id="newServiceName" class="bootbox-input bootbox-input-textarea form-control" required value="${name}" placeholder="Nazwa usługi" maxlength="32"/>
            <p></p>
            <label class="form-label">Opis usługi</label>
            <textarea id="newServiceDescription" class="bootbox-input bootbox-input-textarea form-control" placeholder="Opis usługi" rows="5" maxlength="2000">${description}</textarea>
        `,
        onEscape: true,
        backdrop: true,
        centerVertical: true,
        locale: 'pl',
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
                    let serviceName = $('#newServiceName');

                    if (serviceName.val() == null || serviceName.val().replace(/^\s+|\s+$/gm, '') === '') {
                        serviceName.attr('placeholder', "Nazwa usługi nie może być pusta!");
                        serviceName.addClass('is-invalid');
                        $('label#newServiceNameLabel').addClass('invalid-form-label-asterix');
                        serviceName.on('input', function () {
                            serviceName.removeClass('is-invalid');
                            $('label#newServiceNameLabel').removeClass('invalid-form-label-asterix');
                            serviceName.off('input');
                        });

                        return false;
                    } else {
                        const currentRowData = servicesTable.row(row).data();
                        currentRowData[0] = serviceName.val();
                        currentRowData[1] = $('#newServiceDescription').val();

                        // true - new row
                        // false edited old raw
                        if (Array.isArray(currentRowData[2]) === false) {
                            currentRowData[2] = [serviceName.val(), false];
                        } else if (currentRowData[2][1] !== true) {
                            if (currentRowData[2].length > 1) {
                                currentRowData[2][0] = serviceName.val();
                                currentRowData[2][1] = false;
                            } else {
                                currentRowData[2].push(false);
                            }
                        }

                        const serviceId = row.data('company-service-id');
                        if (serviceId !== undefined && serviceId !== null && serviceId !== '') {
                            if (currentRowData[2].length === 3) {
                                currentRowData[2][2] = Number(serviceId);
                            } else {
                                currentRowData[2].push(Number(serviceId));
                            }
                        }

                        servicesTable.row(row).data(currentRowData);
                        changesInTabs['tab2'].editedRows.add(servicesTable.row(row).index());
                    }
                }
            }
        }
    });

    return false;
}

function removeServiceRow(el) {
    const rowEl = $(el).closest('tr');
    const serviceId = rowEl.data('company-service-id');

    if (serviceId !== undefined && serviceId !== null && serviceId !== '') {
        servicesToRemove.add(Number(serviceId));
    }

    const rowIdx = servicesTable.row(rowEl).index();
    rowEl.addClass('selected');

    if (changesInTabs['tab2'].newRows.has(rowIdx) === false) {
        changesInTabs['tab2'].removedRows.add(rowIdx);
    }
    changesInTabs['tab2'].newRows.delete(rowIdx);
    changesInTabs['tab2'].editedRows.delete(rowIdx);

    servicesTable.row('.selected').remove().draw(false);

    return false;
}

function serializeServices() {
    const tableData = servicesTable.data();
    const servicesData = {
        'type': 'services',
        'new': [],
        'edited': [],
        'deleted': [...servicesToRemove]
    };

    for (let i = 0; i < tableData.length; i++) {
        if (Array.isArray(tableData[i][2]) === true) {
            if (tableData[i][2].length > 1) {
                if (tableData[i][2][1] === true) {
                    servicesData['new'].push({
                        name: tableData[i][0],
                        description: tableData[i][1],
                    });
                } else {
                    servicesData['edited'].push({
                        id: tableData[i][2][2],
                        name: tableData[i][0],
                        description: tableData[i][1],
                    });
                }
            }
        }
    }

    return servicesData;
}

function saveServices() {
    if (hasTabAnyChanges('tab2') === true) {
        globalLoader.show();

        sendTabData(serializeServices());
    }

    return false;
}

//endregion

//region Description
function editCompanyDesc() {
    const serviceAddPopUp = bootbox.dialog({
        title: 'Podaj opis firmy.',
        message: `
            <label class="form-label">Opis firmy</label>
            <textarea id="newCompanyDescription" class="bootbox-input bootbox-input-textarea form-control" placeholder="Opis firmy" rows="5" maxlength="2000">${$("div#companyDescText").text()}</textarea>
        `,
        onEscape: true,
        backdrop: true,
        centerVertical: true,
        locale: 'pl',
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
                    globalLoader.show();
                    sendTabData({
                        'type': 'description',
                        'description': $('#newCompanyDescription').val()
                    });
                }
            }
        }
    });

    return false;
}

//endregion

//region Logo
function editCompanyLogo() {
    const serviceAddPopUp = bootbox.dialog({
        title: 'Podaj nowe logo firmy.',
        message: `
            <div class="form-row">
                <div class="form-group col-md-12 mb-0">
                    <div id="div_id_company_logo" class="mb-3">
                        <label for="id_company_logo" class="form-label"><b>Logo</b></label>
                        <div class=" mb-2">
                            <div>
                                <input type="file" name="company_logo" class="form-control" accept="image/*" id="id_company_logo">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `,
        onEscape: true,
        backdrop: true,
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
                label: '<i class="fa fa-check"></i> Zatwierdź',
                className: 'btn-primary',
                callback: function () {
                    const newCompanyLogo = document.getElementById('id_company_logo').files[0];
                    if (newCompanyLogo) {
                        globalLoader.show();
                        const logoData = new FormData();
                        logoData.append('type', 'logo');
                        logoData.append('new_logo', newCompanyLogo);
                        sendOrRemoveFiles(logoData);
                    }
                }
            }
        }
    });

    return false;
}

//endregion

//region Certificates
const certificatesTable = $('#data-table2').DataTable({
    "language": dataTableLanguageOpt,
    "stateSave": true,
    "autoWidth": false,
    "columns": [
        {"searchable": true, 'width': '40%'},
        {"searchable": true, 'width': '20%'},
        {"searchable": false, 'orderable': true, 'width': '20%'},
        {
            "searchable": false, 'orderable': false, 'width': '10%', 'render': function (data, type, row) {
                if (data !== null && data[0] !== null && data[0] !== undefined && data[1] > -1) {
                    let url = '';
                    let name = '';
                    if (data.length === 3) {
                        url = data[0];
                        name = data[2];
                    } else {
                        url = URL.createObjectURL(data[0]);
                        name = data[0].name;
                    }
                    return `<a href="${url}" download="${name}" data-file-index="${data[1]}" class="cert-file-icon">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <g clip-path="url(#clip0_1720_10924)">
                                            <path d="M15 2H6C4.9 2 4 2.9 4 4V20C4 21.1 4.9 22 6 22H18C19.1 22 20 21.1 20 20V7L15 2ZM6 20V4H14V8H18V20H6ZM16 10V15C16 17.21 14.21 19 12 19C9.79 19 8 17.21 8 15V8.5C8 7.03 9.26 5.86 10.76 6.01C12.06 6.14 13 7.33 13 8.64V15H11V8.5C11 8.22 10.78 8 10.5 8C10.22 8 10 8.22 10 8.5V15C10 16.1 10.9 17 12 17C13.1 17 14 16.1 14 15V10H16Z" fill="#23c678"/>
                                        </g>
                                        <defs>
                                            <clipPath id="clip0_1720_10924">
                                                <rect width="24" height="24" fill="#23c678"/>
                                            </clipPath>
                                        </defs>
                                    </svg>
                                </a>`;
                } else {
                    return `<a href="javascript:void(0)" class="cert-file-icon-empty">
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                        <g clip-path="url(#clip0_1720_10942)">
                                            <path d="M17 19.22H5V7H12V5H3V21H19V12H17V19.22Z" fill="grey"/>
                                            <path d="M19 2H17V5H14C14.01 5.01 14 7 14 7H17V9.99C17.01 10 19 9.99 19 9.99V7H22V5H19V2Z" fill="#8A92A6"/>
                                            <path d="M15 9H7V11H15V9Z" fill="#8A92A6"/>
                                            <path d="M7 12V14H15V12H12H7Z" fill="#8A92A6"/>
                                            <path d="M15 15H7V17H15V15Z" fill="#8A92A6"/>
                                        </g>
                                        <defs>
                                            <clipPath id="clip0_1720_10942">
                                                <rect width="24" height="24" fill="grey"/>
                                            </clipPath>
                                        </defs>
                                    </svg>
                                </a>`;
                }
            }
        },
        {
            "searchable": false, 'orderable': false, 'width': '10%', 'render': function (data, type, row) {
                return `<div class="information-action-dropdown dataTables_empty" style="width: 100%; height: 100%;">
                                <button class="information-action-dropdown-btn dataTables_empty">...</button>
                                <div class="information-action-dropdown-content dataTables_empty">
                                    <a href="#" onclick="editCertRow(this)" data-cert-file-index="${data[1]}"><i class="fe fe-edit mr-2"></i>&ensp;Edytuj</a>
                                    <a href="#" style="color: #6C757D;" onclick="removeCertRow(this)"><i class="fe fe-trash-2 mr-2"></i>&ensp;Usuń</a>
                                </div>
                            </div>`;
            }
        },
    ],
});
let certificatesCounter = 0;
const certTypesDict = {};
let certTypesSelectTemplate = '<select name="type" class="select form-select" required="" id="id_type"><option value="" selected="">---------</option>';
const certFiles = {};
let datePicker;
let wasDateUpdate = false;
const certificatesToRemove = new Set();

function addCertificate() {
    const certificateAddPopUp = bootbox.dialog({
        title: 'Podaj dane nowego certyfikatu.',
        message: `
            <label class="form-label" id="newCertNameLabel">Nazwa<span class="asteriskField">*</span></label>
            <input type="text" id="newCertName" class="bootbox-input bootbox-input-textarea form-control" required placeholder="Nazwa certyfikatu" maxlength="128"/>
            <p></p>
            <label class="form-label" id="newCertTypeLabel">Typ certyfikatu<span class="asteriskField">*</span></label>
            ${certTypesSelectTemplate}
            <p></p>
            <label class="form-label" id="newCertDateLabel">Data wystawienia<span class="asteriskField">*</span></label>
            <label class="form-label">(Jeśli data nie zostanie wybrana, zostanie użyta dzisiejsza data)</label>
            <div class="input-group" id="datetimepicker1" data-td-target-input="nearest" data-td-target-toggle="nearest">
                <input type="text" class="form-control" name="date" id="id_date" data-td-target="#datetimepicker1" placeholder="Data wystawienia"/>
                <div class="input-group-append date-select-btn" data-td-target="#datetimepicker1" data-td-toggle="datetimepicker">
                    <div class="input-group-text" style="height: 100%"><i class="fa fa-calendar"></i></div>
                </div>
            </div>
            <p></p>
            <label class="form-label">Plik</label>
            <div class=" mb-2">
                <div><input type="file" name="cert_file" class="form-control" accept="*" id="id_cert_file"></div>
            </div>
        `,
        onEscape: true,
        backdrop: true,
        centerVertical: true,
        locale: 'pl',
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
                    const certName = $('input#newCertName');
                    const certType = $('select#id_type');
                    const certTypeVal = certType.find(":selected").val();
                    const isNameEmpty = certName.val() == null || certName.val().replace(/^\s+|\s+$/gm, '') === '';
                    const isTypeEmpty = certTypeVal === '';

                    if (isNameEmpty || isTypeEmpty) {
                        if (isNameEmpty) {
                            certName.attr('placeholder', "Nazwa certyfikatu nie może być pusta!");
                            certName.addClass('is-invalid');
                            $('label#newCertNameLabel').addClass('invalid-form-label-asterix');
                            certName.on('input', function () {
                                certName.removeClass('is-invalid');
                                $('label#newCertNameLabel').removeClass('invalid-form-label-asterix');
                                certName.off('input');
                            });
                        }
                        if (isTypeEmpty) {
                            certType.addClass('is-invalid');
                            $('label#newTypeNameLabel').addClass('invalid-form-label-asterix');
                            certType.on('input', function () {
                                certType.removeClass('is-invalid');
                                $('label#newTypeNameLabel').removeClass('invalid-form-label-asterix');
                                certType.off('input');
                            });
                        }

                        return false;
                    } else {
                        const dateInput = new Date(datePicker.viewDate).toLocaleDateString('pl-PL', {
                            year: 'numeric',
                            month: '2-digit',
                            day: '2-digit'
                        });
                        const certFileInputFiles = document.getElementById('id_cert_file').files;
                        let certFile = null;
                        let currentFileCounter = -1;

                        if (certFileInputFiles.length > 0) {
                            certFile = certFileInputFiles[0];
                            certFiles[certificatesCounter] = certFileInputFiles[0];
                            currentFileCounter = certificatesCounter;
                            certificatesCounter++;
                        }

                        changesInTabs['tab3'].newRows.add(certificatesTable.data().length);

                        certificatesTable.row.add([
                            certName.val().trim(),
                            certType.find(":selected").text(),
                            dateInput,
                            [certFile, currentFileCounter],
                            [certName.val().trim(), currentFileCounter, true]
                        ]).draw(false);
                    }
                }
            }
        }
    });
    certificateAddPopUp.init(function () {
        let requestDateContainer = document.getElementById('datetimepicker1');
        datePicker = new tempusDominus.TempusDominus(requestDateContainer, {
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
        });
    });

    return false;
}

function editCertRow(el) {
    const row = $(el).closest('tr');
    const rowElements = row.children();
    const name = $(rowElements[0]).text();
    const type = $(rowElements[1]).text();
    const date = $(rowElements[2]).text();
    const fileIndex = Number($(el).data('cert-file-index'));

    const certificateAddPopUp = bootbox.dialog({
        title: 'Edytuj dane certyfikatu.',
        message: `
            <label class="form-label" id="newCertNameLabel">Nazwa<span class="asteriskField">*</span></label>
            <input type="text" id="newCertName" class="bootbox-input bootbox-input-textarea form-control" required value="${name}" placeholder="Nazwa certyfikatu" maxlength="128"/>
            <p></p>
            <label class="form-label" id="newCertTypeLabel">Typ certyfikatu<span class="asteriskField">*</span></label>
            ${window.getCertTypeSelectedSelect(type)}
            <p></p>
            <label class="form-label" id="newCertDateLabel">Data wystawienia<span class="asteriskField">*</span></label>
            <div class="input-group" id="datetimepicker1" data-td-target-input="nearest" data-td-target-toggle="nearest">
                <input type="text" class="form-control" name="date" id="id_date" data-td-target="#datetimepicker1" value="${date}" placeholder="${date}"/>
                <div class="input-group-append date-select-btn" data-td-target="#datetimepicker1" data-td-toggle="datetimepicker">
                    <div class="input-group-text" style="height: 100%"><i class="fa fa-calendar"></i></div>
                </div>
            </div>
            <p></p>
            <label class="form-label">Plik</label>
            <div class="row">
                <div class="mb-2 col-11 c-pr-0">
                    <div>
                        <input type="file" name="cert_file" class="form-control" accept="*" id="id_cert_file">
                    </div>
                </div>
                <span class="input-group-text btn-danger col-1 delete-file-btn"><i class="fe fe-trash"></i></span>
            </div>
        `,
        onEscape: true,
        backdrop: true,
        centerVertical: true,
        locale: 'pl',
        buttons: {
            cancel: {
                label: '<i class="fa fa-times"></i> Anuluj',
                className: 'btn-danger',
                callback: function () {
                    if (datePicker) {
                        datePicker.hide();
                    }
                }
            },
            ok: {
                label: '<i class="fa fa-check"></i> Zatwierdź',
                className: 'btn-primary',
                callback: function () {
                    const certName = $('input#newCertName');
                    const certType = $('select#id_type');
                    const certTypeVal = certType.find(":selected").val();
                    const isNameEmpty = certName.val() == null || certName.val().replace(/^\s+|\s+$/gm, '') === '';
                    const isTypeEmpty = certTypeVal === '';

                    if (isNameEmpty || isTypeEmpty) {
                        if (isNameEmpty) {
                            certName.attr('placeholder', "Nazwa certyfikatu nie może być pusta!");
                            certName.addClass('is-invalid');
                            $('label#newCertNameLabel').addClass('invalid-form-label-asterix');
                            certName.on('input', function () {
                                certName.removeClass('is-invalid');
                                $('label#newCertNameLabel').removeClass('invalid-form-label-asterix');
                                certName.off('input');
                            });
                        }
                        if (isTypeEmpty) {
                            certType.addClass('is-invalid');
                            $('label#newTypeNameLabel').addClass('invalid-form-label-asterix');
                            certType.on('input', function () {
                                certType.removeClass('is-invalid');
                                $('label#newTypeNameLabel').removeClass('invalid-form-label-asterix');
                                certType.off('input');
                            });
                        }

                        return false;
                    } else {
                        let dateInput = $('input#id_date').val();
                        if (wasDateUpdate === true) {
                            dateInput = new Date(datePicker.viewDate).toLocaleDateString('pl-PL', {
                                year: 'numeric',
                                month: '2-digit',
                                day: '2-digit'
                            });
                        }
                        wasDateUpdate = false;
                        const currentRowData = certificatesTable.row(row).data();

                        currentRowData[0] = certName.val().trim();
                        currentRowData[1] = certType.find(":selected").text();
                        currentRowData[2] = dateInput;

                        const uploadedFiles = document.getElementById('id_cert_file').files;
                        if (uploadedFiles.length > 0) {
                            if (fileIndex > -1) {
                                certFiles[fileIndex] = uploadedFiles[0];

                                URL.revokeObjectURL($(rowElements[3]).children()[0].href);

                                currentRowData[3] = [uploadedFiles[0], fileIndex];
                            } else {
                                certFiles[certificatesCounter] = uploadedFiles[0];

                                currentRowData[3] = [uploadedFiles[0], certificatesCounter];

                                certificatesCounter++;
                            }
                        } else if (uploadedFiles.length === 0) {
                            if (currentRowData[3] !== null && typeof currentRowData[3][0] === "string") {
                                currentRowData[3] = ["---*|REMOVED FILE|*---", -1];
                            } else if (currentRowData[4][2] === null) {
                                currentRowData[3] = ["---*|REMOVED FILE|*---", -1];
                            }
                        } else if (fileIndex > -1) {
                            delete certFiles[fileIndex];
                            currentRowData[3] = null;
                        }

                        currentRowData[4][2] = false;

                        certificatesTable.row(row).data(currentRowData);
                        changesInTabs['tab3'].editedRows.add(certificatesTable.row(row).index());
                        datePicker.hide();
                    }
                }
            }
        }
    });

    certificateAddPopUp.init(function () {
        if (fileIndex > -1) {
            let fileInput = $('input#id_cert_file');
            fileInput.on('drop', function (e) {
                if (e.originalEvent.dataTransfer && typeof e.originalEvent.dataTransfer.getData === 'function') {
                    fileInput[0].files = e.originalEvent.dataTransfer.getData().files;
                }
            });
            if (typeof certFiles[fileIndex] !== 'string') {
                let fakeDropEvent = new DragEvent('drop');
                Object.defineProperty(fakeDropEvent, 'dataTransfer', {
                    value: new FakeDataTransfer([certFiles[fileIndex]])
                });
                fileInput[0].dispatchEvent(fakeDropEvent);
            } else {
                fileInput.attr('placeholder', certFiles[fileIndex]);
                fileInput.attr('value', certFiles[fileIndex]);
            }
        }

        let requestDateContainer = document.getElementById('datetimepicker1');
        datePicker = new tempusDominus.TempusDominus(requestDateContainer, {
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
        });
        const changeEvent = datePicker.subscribe(tempusDominus.Namespace.events.change, (e) => {
            // const currentDate = e.date
            // console.log(e)
            wasDateUpdate = true;
        });

        $('span.delete-file-btn').click(function () {
            document.getElementById('id_cert_file').value = "";
        });
    });

    return false;
}

function removeCertRow(el) {
    const rowEl = $(el).closest('tr');
    const certificateId = certificatesTable.row(rowEl).data()[4][1];

    if (certificateId !== undefined && certificateId !== null && certificateId > -1) {
        certificatesToRemove.add(certificateId);
    }

    const rowIdx = certificatesTable.row(rowEl).index();
    rowEl.addClass('selected');

    if (changesInTabs['tab3'].newRows.has(rowIdx) === false) {
        changesInTabs['tab3'].removedRows.add(rowIdx);
    }
    changesInTabs['tab3'].newRows.delete(rowIdx);
    changesInTabs['tab3'].editedRows.delete(rowIdx);

    certificatesTable.row('.selected').remove().draw(false);

    return false;
}

function saveCertificates() {
    if (hasTabAnyChanges('tab3')) {
        globalLoader.show();

        const tableData = certificatesTable.data();
        const certificatesData = {
            'type': 'certificates',
            'new': [],
            'edited': [],
            'new-files': [],
            'edited-files': [],
        };

        for (let i = 0; i < tableData.length; i++) {
            // null - not edited existing data
            // true - new data
            // false - edited existing data
            if (tableData[i][4][2] === true) {
                certificatesData['new'].push({
                    name: tableData[i][0],
                    type: certTypesDict[tableData[i][1]],
                    date: tableData[i][2]
                });
                //type-<loop counter>-<cert name>
                if (tableData[i][3][0] !== null && tableData[i][3][1] > -1) {
                    certificatesData['new-files'].push({
                        id: `new-||-${i}-||-${tableData[i][0]}`,
                        file: tableData[i][3][0]
                    });
                }
            } else if (tableData[i][4][2] === false) {
                certificatesData['edited'].push({
                    id: Number(tableData[i][4][3]),
                    name: tableData[i][0],
                    type: certTypesDict[tableData[i][1]],
                    date: tableData[i][2]
                });
                if (tableData[i][3][0] !== null && tableData[i][3][1] > -1) {
                    if (typeof tableData[i][3][0] !== 'string') {
                        certificatesData['edited-files'].push({
                            id: `edited-||-${i}-||-${tableData[i][0]}`,
                            file: tableData[i][3][0]
                        });
                    } else if (tableData[i][3][0] === '---*|REMOVED FILE|*---') {
                        certificatesData['edited-files'].push({
                            id: `removed-edited-||-${i}-||-${tableData[i][0]}`
                        });
                    }
                } else if (tableData[i][3][0] !== null && tableData[i][3][0] === '---*|REMOVED FILE|*---') {
                    certificatesData['edited-files'].push({
                        id: `removed-edited-||-${i}-||-${tableData[i][0]}`
                    });
                }
            }
        }

        const certFormData = new FormData();
        certFormData.append('type', 'certificates');
        certFormData.append('new', JSON.stringify(certificatesData['new']));
        certFormData.append('edited', JSON.stringify(certificatesData['edited']));
        certFormData.append('deleted', [...certificatesToRemove]);

        for (let i = 0; i < certificatesData['new-files'].length; i++) {
            certFormData.append(certificatesData['new-files'][i].id, certificatesData['new-files'][i].file);
        }
        for (let i = 0; i < certificatesData['edited-files'].length; i++) {
            if (certificatesData['edited-files'][i].file !== undefined && certificatesData['edited-files'][i].file !== null) {
                certFormData.append(certificatesData['edited-files'][i].id, certificatesData['edited-files'][i].file);
            } else {
                certFormData.append(certificatesData['edited-files'][i].id, true);
            }
        }

        sendOrRemoveFiles(certFormData);
    }

    return false;
}

//endregion

//region Projects
const projectsTable = $('#data-table3').DataTable({
    "language": dataTableLanguageOpt,
    "stateSave": true,
    "autoWidth": false,
    "columns": [
        {"searchable": true, 'width': '25%'},
        {"searchable": true, 'width': '50%'},
        {
            "searchable": false, 'orderable': false, 'width': '15%', 'render': function (data, type, row) {
                if (data !== null && data !== undefined && data !== '') {
                    return `<a href="${data}" target="_blank">Strona projektu</a>`;
                } else {
                    return '-';
                }
            }
        },
        {
            "searchable": false, 'orderable': false, 'width': '10%', 'render': function (data, type, row) {
                return `<div class="information-action-dropdown dataTables_empty" style="width: 100%; height: 100%;">
                        <button class="information-action-dropdown-btn dataTables_empty">...</button>
                        <div class="information-action-dropdown-content dataTables_empty">
                            <a href="#" onclick="editProjectRow(this)"><i class="fe fe-edit mr-2"></i>&ensp;Edytuj</a>
                            <a href="#" style="color: #6C757D;" onclick="removeProjectRow(this)"><i class="fe fe-trash-2 mr-2"></i>&ensp;Usuń</a>
                        </div>
                    </div>`;
            }
        },
    ],
});
const projectsToRemove = new Set();

function addProject() {
    const projectAddPopUp = bootbox.dialog({
        title: 'Podaj dane nowego projektu.',
        message: `
            <label class="form-label" id="newProjectNameLabel">Nazwa<span class="asteriskField">*</span></label>
            <input type="text" id="newProjectName" class="bootbox-input bootbox-input-textarea form-control" required placeholder="Nazwa projektu" maxlength="128"/>
            <p></p>
            <label class="form-label">Opis</label>
            <textarea id="newProjectDescription" class="bootbox-input bootbox-input-textarea form-control" placeholder="Opis projektu" rows="5" maxlength="2000"></textarea>
            <p></p>
            <label class="form-label">Strona projektu</label>
            <input type="url" id="newProjectUrl" class="bootbox-input bootbox-input-textarea form-control" placeholder="Strona projektu: https://example.com"/>
        `,
        onEscape: true,
        backdrop: true,
        centerVertical: true,
        locale: 'pl',
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
                    let projectName = $('input#newProjectName');

                    if (projectName.val() == null || projectName.val().replace(/^\s+|\s+$/gm, '') === '') {
                        projectName.attr('placeholder', "Nazwa projektu nie może być pusta!");
                        projectName.addClass('is-invalid');
                        $('label#newProjectNameLabel').addClass('invalid-form-label-asterix');
                        projectName.on('input', function () {
                            projectName.removeClass('is-invalid');
                            $('label#newProjectNameLabel').removeClass('invalid-form-label-asterix');
                            projectName.off('input');
                        });

                        return false;
                    } else {
                        let projectUrl = $('#newProjectUrl').val().trim();
                        if (projectUrl !== '') {
                            if (projectUrl.startsWith('https://') === false && projectUrl.startsWith('http://') === false) {
                                projectUrl = "https://" + projectUrl;
                            }
                        }
                        changesInTabs['tab4'].newRows.add(projectsTable.data().length);
                        projectsTable.row.add([
                            projectName.val().trim(),
                            $('#newProjectDescription').val().trim(),
                            projectUrl,
                            [true],
                        ]).draw(false);
                    }
                }
            }
        }
    });

    return false;
}

function editProjectRow(el) {
    const row = $(el).closest('tr');
    const rowElements = row.children();
    const name = $(rowElements[0]).text();
    const description = $(rowElements[1]).text();
    const urlNode = $(rowElements[2].childNodes[0]);
    let url = '';
    if (urlNode.is('a') === true) {
        url = urlNode[0].href;
    }

    const projectAddPopUp = bootbox.dialog({
        title: 'Podaj dane projektu.',
        message: `
            <label class="form-label" id="newProjectNameLabel">Nazwa<span class="asteriskField">*</span></label>
            <input type="text" id="newProjectName" class="bootbox-input bootbox-input-textarea form-control" required value="${name}" placeholder="Nazwa projektu" maxlength="128"/>
            <p></p>
            <label class="form-label">Opis</label>
            <textarea id="newProjectDescription" class="bootbox-input bootbox-input-textarea form-control" placeholder="Opis projektu" rows="5" maxlength="2000">${description}</textarea>
            <p></p>
            <label class="form-label">Strona projektu</label>
            <input type="url" id="newProjectUrl" class="bootbox-input bootbox-input-textarea form-control" value="${url}" placeholder="Strona projektu: https://example.com"/>
        `,
        onEscape: true,
        backdrop: true,
        centerVertical: true,
        locale: 'pl',
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
                    let projectName = $('input#newProjectName');

                    if (projectName.val() == null || projectName.val().replace(/^\s+|\s+$/gm, '') === '') {
                        projectName.attr('placeholder', "Nazwa projektu nie może być pusta!");
                        projectName.addClass('is-invalid');
                        $('label#newProjectNameLabel').addClass('invalid-form-label-asterix');
                        projectName.on('input', function () {
                            projectName.removeClass('is-invalid');
                            $('label#newProjectNameLabel').removeClass('invalid-form-label-asterix');
                            projectName.off('input');
                        });

                        return false;
                    } else {
                        let projectUrl = $('#newProjectUrl').val().trim();
                        if (projectUrl !== '') {
                            if (projectUrl.startsWith('https://') === false && projectUrl.startsWith('http://') === false) {
                                projectUrl = "https://" + projectUrl;
                            }
                            $(rowElements[2]).empty();
                            $(rowElements[2]).append($(`<a href="${projectUrl}" target="_blank">Strona projektu</a>`));
                        } else {
                            $(rowElements[2]).text('-');
                        }

                        const currentRowData = projectsTable.row(row).data();
                        currentRowData[0] = projectName.val().trim();
                        currentRowData[1] = $('#newProjectDescription').val().trim();
                        currentRowData[2] = projectUrl;

                        // true - new row
                        // false edited old raw
                        if (Array.isArray(currentRowData[3]) === false) {
                            currentRowData[3] = [false];
                        } else if (currentRowData[3][0] !== true) {
                            if (currentRowData[3].length > 0) {
                                currentRowData[3][0] = false;
                            } else {
                                currentRowData[3].push(false);
                            }
                        }

                        const projectId = row.data('company-project-id');
                        if (projectId !== undefined && projectId !== null && projectId !== '') {
                            if (currentRowData[3].length === 2) {
                                currentRowData[3][1] = Number(projectId);
                            } else {
                                currentRowData[3].push(Number(projectId));
                            }
                        }

                        projectsTable.row(row).data(currentRowData);

                        changesInTabs['tab4'].editedRows.add(projectsTable.row(row).index());
                    }
                }
            }
        }
    });

    return false;
}

function removeProjectRow(el) {
    const rowEl = $(el).closest('tr');
    const serviceId = rowEl.data('company-project-id');

    if (serviceId !== undefined && serviceId !== null && serviceId !== '') {
        projectsToRemove.add(Number(serviceId));
    }

    const rowIdx = projectsTable.row(rowEl).index();
    rowEl.addClass('selected');

    if (changesInTabs['tab4'].newRows.has(rowIdx) === false) {
        changesInTabs['tab4'].removedRows.add(rowIdx);
    }
    changesInTabs['tab4'].newRows.delete(rowIdx);
    changesInTabs['tab4'].editedRows.delete(rowIdx);

    projectsTable.row('.selected').remove().draw(false);

    return false;
}

function serializeProjects() {
    const tableData = projectsTable.data();
    const projectsData = {
        'type': 'projects',
        'new': [],
        'edited': [],
        'deleted': [...projectsToRemove]
    };

    for (let i = 0; i < tableData.length; i++) {
        if (Array.isArray(tableData[i][3]) === true) {
            if (tableData[i][3].length > 0) {
                if (tableData[i][3][0] === true) {
                    projectsData['new'].push({
                        name: tableData[i][0],
                        description: tableData[i][1],
                        www: tableData[i][2]
                    });
                } else {
                    projectsData['edited'].push({
                        id: tableData[i][3][1],
                        name: tableData[i][0],
                        description: tableData[i][1],
                        www: tableData[i][2],
                    });
                }
            }
        }
    }

    return projectsData;
}

function saveProjects() {
    if (hasTabAnyChanges('tab4') === true) {
        globalLoader.show();

        sendTabData(serializeProjects());
    }

    return false;
}

//endregion

//region Galery
const photosUploader = $('#id_photos');
const uploadedPhotos = {};

function sendFakePhotoDropEvent() {
    let fakeDropEvent = new DragEvent('drop');
    Object.defineProperty(fakeDropEvent, 'dataTransfer', {
        value: new FakeDataTransfer(Object.values(uploadedPhotos))
    });
    photosUploader[0].dispatchEvent(fakeDropEvent);
}

photosUploader.FancyFileUpload({
    accept: [
        'image/apng',
        'image/avif',
        'image/gif',
        'image/jpeg',
        'image/jpg',
        'image/png',
        'image/svg+xml',
        'image/webp',
        'image/bmp'
    ],
    edit: false,
    allowUpload: false,
    originalInputId: '#id_photos',
    added: function (e, data) {
        this.find('.ff_fileupload_actions button.ff_fileupload_start_upload').hide();

        for (let i = 0; i < data.files.length; i++) {
            uploadedPhotos[data.files[i].name] = data.files[i];
            let fileUrl = window.URL.createObjectURL(data.files[i]);
            window.URL.revokeObjectURL(fileUrl);
        }

        sendFakePhotoDropEvent();
    },
    fileRemoveOption: function (fileName) {
        if (uploadedPhotos[fileName] !== undefined) {
            delete uploadedPhotos[fileName];

            sendFakePhotoDropEvent();
        }
    },
    langmap: {
        'Starting upload...': 'Rozpoczynanie przesyłania...',
        'Cancel upload and remove from list': 'Anuluj przesłanie i usuń z listy',
        'Preview': 'Podgląd',
        'No preview available': 'Podgląd jest niedostępny',
        'Invalid file extension.': 'Błędne rozszerzenie pliku.',
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
        'Accepted extensions: ': 'Dopuszczalne rozszerzenia: ',
    }
});

photosUploader.on('drop', function (e) {
    if (e.originalEvent.dataTransfer && typeof e.originalEvent.dataTransfer.getData === 'function') {
        photosUploader[0].files = e.originalEvent.dataTransfer.getData().files;
    }
});

const photos = [];
document.querySelectorAll('div#galleryPhotoElement').forEach(function (el) {
    photos.push({
        "src": $(el).data('src'),
        "thumb": $(el).data('src'),
        "subHtml": $(el).data('sub-html')
    });
});

$('.pagination').rpmPagination({
    domElement: '.gallery-page-container',
    limit: 1,
    total: document.querySelectorAll('div.gallery-page-container').length,
    forceTotalPages: true,
});

lightGallery(document.getElementById('lightgallery'), {
    'dynamic': true,
    'dynamicEl': photos,
    pager: true,
    zoom: true,
    showZoomInOutIcons: true,
});

const gallery = window.lgData['lg' + (window.lgData.uid - 1)];

document.querySelectorAll('div#galleryPhotoElement > img').forEach(function (el) {
    $(el).click(function () {
        gallery.build(Number($(this).data('gallery-idx')));
    });
});

function addPhotos() {
    let promptBody = `<div class="form-row">
                <div class="form-group col-md-12 mb-0">
                    <div id="div_id_files" class="mb-3">
                        <label for="id_files" class="form-label">Dodaj nowe zdjęcia</label>
                        <input type="file" name="files" class="form-control" accept="image/*" id="id_files" multiple>
                    </div>
                </div>
            </div>`;
    let companiesManager = bootbox.confirm({
        title: `<span style="font-family: Roboto, sans-serif !important;"><i class="fe fe-file-plus"></i>&emsp;Dodaj zdjęcia do firmy</span>`,
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
                $('#global-loader').show();

                const uploaded_files = $('#id_files')[0].files;
                const files = new FormData();
                files.append('type', 'photos');
                for (let i = 0; i < uploaded_files.length; i++) {
                    files.append('file_' + i, uploaded_files[i]);
                }

                sendOrRemoveFiles(files);
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
                filesUploader[0].dispatchEvent(fakeDropEvent);
            }

            filesUploader.FancyFileUpload({
                accept: [
                    'image/apng',
                    'image/avif',
                    'image/gif',
                    'image/jpeg',
                    'image/jpg',
                    'image/png',
                    'image/svg+xml',
                    'image/webp',
                    'image/bmp'
                ],
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
                    filesUploader[0].files = e.originalEvent.dataTransfer.getData().files;
                }
            });
        },
    });
}

function removePhotos() {
    const values = [];
    document.querySelectorAll('input[name=photo-delete]:checked').forEach(function (checkbox) {
        values.push(checkbox.value);
    });

    if (values.length > 0) {
        // send files ids to remove
        globalLoader.show();
        const files = new FormData();
        files.append('type', 'delete_photos');
        files.append('ids', values);

        sendOrRemoveFiles(files);
    }

    return false;
}

//endregion

//region Files
function addFiles() {
    let promptBody = `<div class="form-row">
                        <div class="form-group col-md-12 mb-0">
                            <div id="div_id_files" class="mb-3">
                                <label for="id_files" class="form-label">Dodaj nowe pliki</label>
                                <input type="file" name="files" class="form-control" accept="*" id="id_files" multiple>
                            </div>
                        </div>
                    </div>`;
    let companiesManager = bootbox.confirm({
        title: `<span style="font-family: Roboto, sans-serif !important;"><i class="fe fe-file-plus"></i>&emsp;Dodaj pliki do firmy</span>`,
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
                $('#global-loader').show();

                const uploaded_files = $('#id_files')[0].files;
                const files = new FormData();
                files.append('type', 'files');
                for (let i = 0; i < uploaded_files.length; i++) {
                    files.append('file_' + i, uploaded_files[i]);
                }

                sendOrRemoveFiles(files);
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
                filesUploader[0].dispatchEvent(fakeDropEvent);
            }

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
                    filesUploader[0].files = e.originalEvent.dataTransfer.getData().files;
                }
            });
        },
    });
}

function removeFiles() {
    const values = [];
    document.querySelectorAll('input[name=file-delete]:checked').forEach(function (checkbox) {
        values.push(checkbox.value);
    });

    if (values.length > 0) {
        globalLoader.show();
        const files = new FormData();
        files.append('type', 'delete_files');
        files.append('ids', values);

        sendOrRemoveFiles(files);
    }

    return false;
}

//endregion