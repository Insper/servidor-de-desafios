import { csrftoken } from '../components/django'

const API_USER = '/api/user/'
const API_CHANGE_PASS = '/api/change-password/'
const API_CHALLENGES = '/api/coding/'

const API_CHALLENGE = (slug) => `${API_CHALLENGES}${slug}/`


const fetchUserData = () => {
  return fetch(API_USER, { credentials: 'include' })
}

const doPost = (url, data) => {
  return fetch(url, {
    credentials: 'include',
    method: 'POST',
    mode: 'same-origin',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken
    },
    body: JSON.stringify(data)
  })
}

const postNewPassword = (oldPassword, newPassword, repeatPassword) => {
  return doPost(API_CHANGE_PASS, {
    oldPassword: oldPassword,
    newPassword: newPassword,
    repeatPassword: repeatPassword
  })
}

const fetchChallengeList = () => {
  return fetch(API_CHALLENGES, { credentials: 'include' })
}

const fetchChallenge = (slug) => {
  return fetch(API_CHALLENGE(slug), { credentials: 'include' })
}

const postChallenge = (slug, code) => {
  return doPost(API_CHALLENGE(slug), {
    code: code,
  })
}

export { fetchUserData, postNewPassword, fetchChallengeList, fetchChallenge, postChallenge }
