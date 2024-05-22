$(document).ready(function() {
    // Show modal
    const sharemodal = document.getElementById('shareModal');
    $(document).on('click', '.share_file', function() {
        var fileId = $(this).data('file-id');
        console.log(fileId)
        $('#fileId').val(fileId);
        $('#shareModal').removeClass('hidden');
    });

    // Hide modal
    $('#cancelButton').click(function() {
        $('#shareModal').addClass('hidden');
    });


    // Share file
    $('#shareButton').click(function() {
        var fileId = $('#fileId').val();
        var email = $('#shareEmail').val();

        $.ajax({
            url: shareFileUrl,  // This will be defined in the HTML
            type: "POST",
            data: {
                'file_id': fileId,
                'email': email,
                'csrfmiddlewaretoken': csrfToken
            },
            success: function(response) {
                if (response.status == 'success') {
                    alert('File shared successfully!');
                    $('#shareModal').addClass('hidden');
                } else {
                    alert('An error occurred. Please try again.');
                }
            }
        });
    });

    $(document).on('click', '.download_file', function() {
        var fileId = $(this).data('file-id');

        $.ajax({
            url: downloadFileUrl,
            type: "POST",
            data: {
                'file_id': fileId,
                'csrfmiddlewaretoken': csrfToken
            },
            xhrFields: {
                responseType: 'blob'  // Important to handle binary data
            },
            success: function(blob, status, xhr) {
                var filename = "";
                var disposition = xhr.getResponseHeader('Content-Disposition');
                if (disposition && disposition.indexOf('attachment') !== -1) {
                    var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                    var matches = filenameRegex.exec(disposition);
                    if (matches != null && matches[1]) {
                        filename = matches[1].replace(/['"]/g, '');
                    }
                }

                if (typeof window.navigator.msSaveBlob !== 'undefined') {
                    // IE workaround for "HTML7007: One or more blob URLs were revoked by closing the blob for which they were created. 
                    // These URLs will no longer resolve as the data backing the URL has been freed."
                    window.navigator.msSaveBlob(blob, filename);
                } else {
                    var URL = window.URL || window.webkitURL;
                    var downloadUrl = URL.createObjectURL(blob);

                    if (filename) {
                        // use HTML5 a[download] attribute to specify filename
                        var a = document.createElement("a");
                        // safari doesn't support this yet
                        if (typeof a.download === 'undefined') {
                            window.location = downloadUrl;
                        } else {
                            a.href = downloadUrl;
                            a.download = filename;
                            document.body.appendChild(a);
                            a.click();
                            document.body.removeChild(a);
                        }
                    } else {
                        window.location = downloadUrl;
                    }

                    setTimeout(function () {
                        URL.revokeObjectURL(downloadUrl);
                    }, 100); // cleanup
                }

                alert('File downloaded successfully!');
            },
            error: function() {
                alert('An error occurred. Please try again.');
            }
        });
    });
});
