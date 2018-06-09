var requestDownload = function () {
    var url = document.querySelector("[name=url]").value;
    var _xsrf = document.querySelector("[name=_xsrf]").value;

    var data = {
        url: url,
        _xsrf: _xsrf
    };

    axios.request({
        url: '/api',
        data: data,
        params: {
            _xsrf: _xsrf
        },
        method: 'post',
    }).then(console.log).catch(console.error);
};