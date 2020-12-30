import React, { useState, useEffect } from "react"
import { useTranslation } from 'react-i18next'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import Typography from '@material-ui/core/Typography'
import _ from 'lodash'

import { getConcept, getChallengeList, getTraceList } from '../api/pygym'
import ROUTES from '../routes'


function ConceptDetails(props) {
  const { slug, ...otherProps } = props
  const { t } = useTranslation()

  const [concept, setConcept] = useState([])
  const [challenges, setChallenges] = useState([])
  const [traces, setTraces] = useState([])

  useEffect(() => {
    getConcept(slug)
      .then(setConcept)
      .catch(console.log)

    getChallengeList(slug)
      .then(setChallenges)
      .catch(console.log)

    getTraceList(slug)
      .then(setTraces)
      .catch(console.log)
  }, [])

  return (
    <>
      <Typography variant="h1" component="h2" gutterBottom={true}>{concept.name}</Typography>
      {!_.isEmpty(challenges) && <Typography variant="h3">{t("Code Challenges")}</Typography>}
      <List component="nav">
        {challenges.map(challenge =>
          <ListItem button component="a" key={`challenge-${challenge.slug}`} href={ROUTES.challenge.link({ slug: challenge.slug })}>
            {challenge.title}
          </ListItem>
        )}
      </List>
      {!_.isEmpty(traces) && <Typography variant="h3">{t("Trace Challenges")}</Typography>}
      <List component="nav">
        {traces.map(challenge =>
          <ListItem button component="a" key={`challenge-${challenge.slug}`} href={ROUTES.challenge.link({ slug: challenge.slug })}>
            {challenge.title}
          </ListItem>
        )}
      </List>
    </>
  )
}

export default ConceptDetails
