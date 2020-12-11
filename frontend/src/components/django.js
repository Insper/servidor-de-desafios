import React from 'react';

const STATIC_URL = '/static/'

// CRSF code from: https://docs.djangoproject.com/en/3.1/ref/csrf/#ajax
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

export { csrftoken, CSRFToken, formErrors, STATIC_URL };
