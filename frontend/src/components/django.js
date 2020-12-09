import React from 'react';


// CRSF code from: https://stackoverflow.com/a/50735730
const getCookie = (name) => {
  let cookieValue = null
  if (document.cookie && document.cookie !== '') {
    let cookies = document.cookie.split(';')
    for (let i = 0; i < cookies.length; i++) {
      let cookie = cookies[i].trim()
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

const csrftoken = getCookie('csrftoken');

const CSRFToken = () => {
  return (
    <input type="hidden" name="csrfmiddlewaretoken" value={csrftoken} />
  );
};

const formErrors = window.formErrors

export { CSRFToken, formErrors };
