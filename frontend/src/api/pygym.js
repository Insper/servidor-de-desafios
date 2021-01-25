import { csrftoken } from '../components/django'

const API_USER = '/api/user/'
const API_CHANGE_PASS = '/api/change-password/'
const API_THANKS = '/api/thanks/'
const API_CONCEPTS = '/api/concept/'
const API_CONCEPT = (slug) => `${API_CONCEPTS}${slug}/`
const API_CHALLENGES = '/api/code/'
const API_CHALLENGE_INTERACTIONS = '/api/code/interaction/'
const API_CONCEPT_CHALLENGES = (slug) => `${API_CHALLENGES}?concept=${slug}`
const API_CHALLENGE = (slug) => `${API_CHALLENGES}${slug}/`
const API_SUBMISSIONS = (slug) => `${API_CHALLENGE(slug)}submission`
const API_SUBMISSION_CODE = (slug, submissionId) => `${API_CHALLENGE(slug)}submission/${submissionId}/code`
const API_TRACES = '/api/trace/'
const API_TRACE_INTERACTIONS = '/api/trace/interaction/'
const API_CONCEPT_TRACES = (slug) => `${API_TRACES}?concept=${slug}`
const API_TRACE = (slug) => `${API_TRACES}${slug}/`
const API_TRACE_STATES = (slug) => `${API_TRACE(slug)}state/`
const API_CONTENTS = '/api/content/'
const API_PAGES = '/api/content/page/'
const API_PAGE = (conceptSlug, pageSlug) => `${API_PAGES}${conceptSlug}/${pageSlug}${pageSlug ? "/" : ""}`


const getJSON = (url, extraParams) => {
  return fetch(url, { ...{ credentials: 'include' }, ...extraParams })
    .then(res => {
      if (res.status >= 400) {
        if (res.status === 403) location.reload()
        let error = new Error(res.statusText || res.status)
        error.response = res
        return Promise.reject(error)
      }
      return res.json()
    })
}

const postJSON = (url, data) => {
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
    .then(res => res.json())
}

const getUserData = () => {
  return getJSON(API_USER)
}

const postNewPassword = (oldPassword, newPassword, repeatPassword) => {
  return postJSON(API_CHANGE_PASS, {
    oldPassword: oldPassword,
    newPassword: newPassword,
    repeatPassword: repeatPassword
  })
}

const getThanks = () => {
  return getJSON(API_THANKS)
}

const getConceptList = () => {
  return getJSON(API_CONCEPTS)
}

const getConcept = (slug) => {
  return getJSON(API_CONCEPT(slug))
}

const getChallengeList = (concept) => {
  if (concept) return getJSON(API_CONCEPT_CHALLENGES(concept))
  return getJSON(API_CHALLENGES)
}

const getCodeInteractionList = () => {
  return getJSON(API_CHALLENGE_INTERACTIONS)
}

const getChallenge = (slug) => {
  return getJSON(API_CHALLENGE(slug))
}

const postChallenge = (slug, code) => {
  return postJSON(API_CHALLENGE(slug), {
    code: code,
  })
}

const getSubmissionList = (slug) => {
  return getJSON(API_SUBMISSIONS(slug))
}

const getSubmissionCode = (slug, submissionId) => {
  return getJSON(API_SUBMISSION_CODE(slug, submissionId))
}

const getTraceList = (concept) => {
  if (concept) return getJSON(API_CONCEPT_TRACES(concept))
  return getJSON(API_TRACES)
}

const getTrace = (slug) => {
  return getJSON(API_TRACE(slug))
}

const postTrace = (slug, stateIndex, memory, terminal, nextLine, retval) => {
  return postJSON(API_TRACE(slug), {
    state_index: stateIndex,
    memory: memory,
    terminal: terminal,
    next_line: nextLine,
    retval: retval,
  })
}

const getTraceInteractionList = () => {
  return getJSON(API_TRACE_INTERACTIONS)
}

const getTraceStateList = (slug) => {
  return getJSON(API_TRACE_STATES(slug))
}

const getContents = () => {
  return getJSON(API_CONTENTS)
}

const getPageList = () => {
  return getJSON(API_PAGES)
}

const getPage = (concept_slug, page_slug) => {
  return getJSON(API_PAGE(concept_slug, page_slug))
}

export {
  getUserData,
  postNewPassword,
  getThanks,
  getConceptList,
  getConcept,
  getChallengeList,
  getCodeInteractionList,
  getChallenge,
  postChallenge,
  getSubmissionList,
  getSubmissionCode,
  getTraceList,
  getTrace,
  postTrace,
  getTraceInteractionList,
  getTraceStateList,
  getContents,
  getPageList,
  getPage,
}
