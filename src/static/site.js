var success = function (response) {
    console.log(response.data)
    var video = document.getElementById("video_link");
    var audio = document.getElementById("audio_link");

    video.href = response.data.video;
    audio.href = response.data.audio;

    video.innerText = "Video: " + response.data.id;
    audio.innerText = "Audio: " + response.data.id;

};

var error = function (err) {
    debugger
    console.error(err)
};

var requestDownload = function () {

    document.getElementById("video_link").innerText = null;
    document.getElementById("audio_link").innerText = null;

    var url = document.querySelector("[name=url]").value;

    if (url === "") {
        alert("Url is not valid");
        return;
    }

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
    }).then(success).catch(error);
};