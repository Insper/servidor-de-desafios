import React, { useState, useEffect } from "react"
import { useTranslation } from 'react-i18next'
import Typography from '@material-ui/core/Typography'
import { Box, Button, Paper } from "@material-ui/core"
import { useSelector } from "react-redux"
import { Link } from "react-router-dom"
import _ from 'lodash'
import clsx from 'clsx'

import { useStyles } from '../styles'
import { selectConceptBySlug } from "../features/concepts/conceptsSlice"
import CircularProgressWithLabel from "./CircularProgressWithLabel"
import ROUTES from "../routes"

export default function ContentSummary(props) {
  const { content, codeInteractionsBySlug, traceInteractionsBySlug, idx, ...otherProps } = props
  const { t } = useTranslation()
  const classes = useStyles()
  const concept = useSelector(state => selectConceptBySlug(state, content.concept)) || {}

  const totalCodeChallenges = concept.codeChallenges ? concept.codeChallenges.length : 0
  const totalTraceChallenges = concept.traceChallenges ? concept.traceChallenges.length : 0
  const completedCodeChallenges = concept.codeChallenges ? concept.codeChallenges.map(codeChallenge => {
    const interactions = codeInteractionsBySlug[codeChallenge]
    return interactions ? interactions.completed : 0
  }).reduce((a, b) => a + b, 0) : 0
  const completedTraceChallenges = concept.traceChallenges ? concept.traceChallenges.map(trace => {
    const interactions = traceInteractionsBySlug[trace]
    return interactions ? interactions.completed : 0
  }).reduce((a, b) => a + b, 0) : 0

  return (
    <Paper {...otherProps}>
      <Box p={1} className={clsx(classes.fillParent, classes.flexbox)}>
        <Typography variant="h5" component="h3" gutterBottom>{_.padStart(idx + 1, 2, '0') + ". " + content.title}</Typography>
        {totalCodeChallenges ? (
          <>
            <Typography>{t("Code Challenges")}:</Typography>
            <CircularProgressWithLabel value={completedCodeChallenges} maxValue={totalCodeChallenges} />
          </>
        ) : null}
        {totalTraceChallenges ? (
          <>
            <Typography>{t("Trace Challenges")}:</Typography>
            <CircularProgressWithLabel value={completedTraceChallenges} maxValue={totalTraceChallenges} />
          </>
        ) : null}
        <Box mt="auto">
          <Button variant="contained" color="primary" fullWidth component={Link} to={ROUTES.content.link({ slug: content.slug })}>{t("Handout")}</Button>
        </Box>
        <Box mt={1}>
          <Button variant="contained" color="primary" fullWidth component={Link} to={ROUTES.contentChallenges.link({ slug: content.slug })}>{t("Challenges")}</Button>
        </Box>
      </Box>
    </Paper>
  )
}
