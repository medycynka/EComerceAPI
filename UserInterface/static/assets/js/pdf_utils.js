// include before this script
// <!-- PDFMAKE JS -->
// <script src="{% static 'assets/plugins/pdfmake/pdfmake.min.js' %}"></script>
// <script src="{% static 'assets/plugins/pdfmake/vfs_fonts.min.js' %}"></script>

const toDataURL = (image) => {
    const canvas = document.createElement('canvas')
    canvas.width = image.naturalWidth
    canvas.height = image.naturalHeight
    canvas.getContext('2d').drawImage(image, 0, 0)
    return canvas.toDataURL()
}
const getPdfTemplate = (config) => {
    return {}
}
const generatePdf = (config) => {
    let start = new Date()
    const pdf = pdfMake.createPdf(getPdfTemplate(config))
    pdf.getDataUrl().then((dataUri) => {
        let stop = new Date()
        console.log(`Took ${stop - start}ms`)

        let pdfData = new FormData()
        pdfData.append('cert_name', config.name)
        pdfData.append('pdf_data', dataUri)
        console.log(config)
        console.log(pdfData)

        $.ajax({
            url: window.location,
            data: pdfData,
            type: 'POST',
            headers: {'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value},
            contentType: false,
            processData: false,
            success: (result, textStatus, jqXHR) => {
                console.log(result, textStatus, jqXHR)

                pdf.download(`${config.name}.pdf`)
            },
            error: (jqXHR, textStatus, errorThrown) => {
                console.log(errorThrown, textStatus, jqXHR)
            },
            complete: (jqXHR, textStatus) => {
                console.log(jqXHR, textStatus)
            }
        })
    }, err => {
        console.error("PDFMAKE ERROR:", err);
    });
}