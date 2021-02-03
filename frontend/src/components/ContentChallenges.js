import React, { useState, useEffect } from "react"
import { useHistory, Link } from "react-router-dom";
import { useSelector } from 'react-redux'
import { useTranslation } from 'react-i18next'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Typography from '@material-ui/core/Typography'
import Paper from '@material-ui/core/Paper';
import _ from 'lodash'

import { selectCodeChallengesBySlug } from '../features/codeChallenges/codeChallengesSlice'
import { selectContentBySlug } from '../features/contents/contentsSlice'
import { selectConceptBySlug } from '../features/concepts/conceptsSlice'
import { selectTraceChallengesBySlug } from '../features/traceChallenges/traceChallengesSlice'
import ROUTES from '../routes'


function ContentChallenges(props) {
  const { slug, ...otherProps } = props
  const { t } = useTranslation()
  const history = useHistory();

  const content = useSelector(state => selectContentBySlug(state, slug))
  const concept = useSelector(state => selectConceptBySlug(state, content && content.concept))
  const challenges = useSelector(state => selectCodeChallengesBySlug(state, concept ? concept.codeChallenges : []))
  const traces = useSelector(state => selectTraceChallengesBySlug(state, concept ? concept.traceChallenges : []))
  if (!content || !concept) return (<></>)

  return (
    <>
      <Typography variant="h1" component="h2" gutterBottom={true}>{content.title}</Typography>
      { !_.isEmpty(challenges) && <Typography variant="h3">{t("Code Challenges")}</Typography>}
      <TableContainer component={Paper}>
        <Table aria-label="code challenges">
          <TableHead>
            <TableRow>
              <TableCell>{t("Title")}</TableCell>
              <TableCell>{t("Status")}</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {challenges.map(challenge =>
              <TableRow
                hover
                key={`challenge-${challenge.slug}`}
                onClick={() => history.push(ROUTES.challenge.link({ slug: challenge.slug }))}
              >
                <TableCell component="th" scope="row">
                  {challenge.title}
                </TableCell>
                <TableCell>Ok</TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </TableContainer>
      {!_.isEmpty(traces) && <Typography variant="h3">{t("Trace Challenges")}</Typography>}
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
