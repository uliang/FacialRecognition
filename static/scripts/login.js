let streaming = false
let width = 500
let height = 0

$(function () {
  let video = $('#video')[0]
  let canvas = $('canvas')[0]


  video.addEventListener("canplay", ev => {
    if (!streaming) {
      height = (video.videoHeight / video.videoWidth) * width

      video.setAttribute("width", width)
      video.setAttribute("height", height)
      canvas.setAttribute("width", width)
      canvas.setAttribute("height", height)
      streaming = true
    }
  }, false)

  navigator.mediaDevices
    .getUserMedia({ 'video': true })
    .then((stream) => {
      video.srcObject = stream;
      video.play()
    })
    .catch((err) => {
      console.error(`An error occured: ${err}`)
    })

  $('#login-form').on('submit', e => {
    e.preventDefault()
    takeandsendpicture()
  })
})

function takeandsendpicture() {
  let form = $('#login-form')[0]
  let formData = new FormData(form)
  let context = canvas.getContext('2d')
  if (width && height) {
    canvas.width = width
    canvas.height = height
    context.drawImage(video, 0, 0, width, height)
    canvas.toDataURL()
    canvas.toBlob(blob => {
      let file = new File([blob], 'photo.jpeg', { type: 'image/jpeg' })
      formData.set('photo', file)
      let postSettings = {
        url: form.action,
        data: formData,
        processData: false,
        contentType: false,
        success: resp => {
          let { status, redirect } = resp
          $('#login-result').css('height', 100)
          if (status === '200') {
            $('#success-container').css('visibility', 'visible') 
            $('#failure-container').remove()
            console.log(status);
            // window.location = redirect
          } else if( status === '403') {
            $('#failure-container').css('visibility', 'visible') 
            $('#success-container').remove()
            console.log(status);
          }
          setTimeout(() => {
            window.location = redirect
          }, 1000)
        },
        error: err => {
          console.log(err);
        }
      }
      $.post(postSettings)
    }, 'image/jpeg', 1.)
  }

}
