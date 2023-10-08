function myFunction() {
    document.getElementById("artist").submit();
    document.getElementById("album").submit();
    document.getElementById("year").submit();
    document.getElementById("format").submit();
  }

  const form = document.querySelector('form')
form.addEventListener('submit', (e) => {
  e.preventDefault()
  const formData = new FormData(form)
  for (const pair of formData.entries()) {
    console.log(pair)
  }
})