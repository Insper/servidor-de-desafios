import { csrftoken } from '../components/django'

const API_USER = '/api/user/'
const API_CHANGE_PASS = '/api/change-password/'
const API_CHALLENGES = '/api/coding/'


const fetchUserData = () => {
  return fetch(API_USER, { credentials: 'include' })
}

const postNewPassword = (oldPassword, newPassword, repeatPassword) => {
  return fetch(API_CHANGE_PASS, {
    credentials: 'include',
    method: 'POST',
    mode: 'same-origin',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken
    },
    body: JSON.stringify({
      oldPassword: oldPassword,
      newPassword: newPassword,
      repeatPassword: repeatPassword
    })
  })
}

const fetchChallengeList = () => {
  return fetch(API_CHALLENGES, { credentials: 'include' })
}

const fetchChallenge = (slug) => {
  return fetch(`${API_CHALLENGES}${slug}/`, { credentials: 'include' })
}

export { fetchUserData, postNewPassword, fetchChallengeList, fetchChallenge }
