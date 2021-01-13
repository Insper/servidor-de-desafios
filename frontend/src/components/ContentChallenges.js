import React, { useState, useEffect } from "react"
import { Link } from "react-router-dom";
import { useSelector } from 'react-redux'
import { useTranslation } from 'react-i18next'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import Typography from '@material-ui/core/Typography'
import _ from 'lodash'

import { selectCodeChallengesBySlug } from '../features/codeChallenges/codeChallengesSlice'
import { selectContentBySlug } from '../features/contents/contentsSlice'
import { selectConceptBySlug } from '../features/concepts/conceptsSlice'
import { selectTraceChallengesBySlug } from '../features/traceChallenges/traceChallengesSlice'
import ROUTES from '../routes'


function ContentChallenges(props) {
  const { slug, ...otherProps } = props
  const { t } = useTranslation()

  const content = useSelector(state => selectContentBySlug(state, slug))
  const concept = useSelector(state => selectConceptBySlug(state, content && content.concept))
  const challenges = useSelector(state => selectCodeChallengesBySlug(state, concept ? concept.codeChallenges : []))
  const traces = useSelector(state => selectTraceChallengesBySlug(state, concept ? concept.traceChallenges : []))
  if (!content || !concept) return (<></>)

  return (
    <>
      <Typography variant="h1" component="h2" gutterBottom={true}>{content.title}</Typography>
      { !_.isEmpty(challenges) && <Typography variant="h3">{t("Code Challenges")}</Typography>}
      <List component="nav">
        {challenges.map(challenge =>
          <ListItem button component={Link} key={`challenge-${challenge.slug}`} to={ROUTES.challenge.link({ slug: challenge.slug })}>
            {challenge.title}
          </ListItem>
        )}
      </List>
      { !_.isEmpty(traces) && <Typography variant="h3">{t("Trace Challenges")}</Typography>}
      <List component="nav">
        {traces.map(challenge =>
          <ListItem button component={Link} key={`challenge-${challenge.slug}`} to={ROUTES.trace.link({ slug: challenge.slug })}>
            {challenge.title}
          </ListItem>
        )}
      </List>
    </>
  )
}

export default ContentChallenges