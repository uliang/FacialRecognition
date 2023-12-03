// const { event } = require("jquery")

let width = 500
let height = 0

let streaming = false
let video = null
let canvas = null
let photo = null
let startbutton = null
let form = null

$(function () {
  video = $('#video')[0]
  canvas = $('#canvas')[0]
  photo = $('#photo')[0]
  startbutton = $('#take-photo-button')[0]
  form = $('form')[0]

  $('form').css("width", width)
  let formData = new FormData(form)

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

  startbutton.addEventListener("click", ev => {
    takepicture();
    ev.preventDefault()
  }, false)

  form.addEventListener('submit', (event) => {
    event.preventDefault()
    $.post({
      url: form.action,
      data: formData,
      processData: false,
      contentType: false,
      success: (resp) => {
        let {status, redirect} = JSON.parse(resp) 
        if (status === "201") {
          window.location = redirect
        } else {
          console.log(status);
        }
      },
      error: (err) => {
        console.log(err)
      }

    })
  })

  $('input#name').on('change', (e) => {
    let name = e.target.value
    formData.set('username', name)
  })

  $('#reset').on('click', clearphoto)

  navigator.mediaDevices
    .getUserMedia({ 'video': true })
    .then((stream) => {
      video.srcObject = stream;
      video.play()
    })
    .catch((err) => {
      console.error(`An error occured: ${err}`)
    })

  clearphoto()

  function clearphoto() {
    let context = canvas.getContext('2d')
    context.fillStyle = '#AAA'
    context.fillRect(0, 0, canvas.width, canvas.height)

    let data = canvas.toDataURL("image/jpeg")
    photo.setAttribute("src", data)
  }

  function takepicture() {
    let context = canvas.getContext('2d')
    if (width && height) {
      canvas.width = width
      canvas.height = height
      context.drawImage(video, 0, 0, width, height)

      let data = canvas.toDataURL('image/jpeg')
      photo.setAttribute('src', data)
      canvas.toBlob((blob) => {
        let file = new File([blob], 'photo.jpeg', { type: 'image/jpeg' })
        formData.set('photo', file)
      }, 'image/jpeg', 1.)

    } else {
      clearphoto()
    }
  }
})

