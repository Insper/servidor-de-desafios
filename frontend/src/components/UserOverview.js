import React, { useState, useEffect } from "react"
import { useSelector } from 'react-redux'
import { useTranslation } from 'react-i18next'
import Grid from '@material-ui/core/Grid'
import Typography from '@material-ui/core/Typography'
import _ from "lodash"
import clsx from "clsx"
import { selectTraceInteractions } from '../features/traceInteractions/traceInteractionsSlice'
import { selectCodeInteractions } from '../features/codeInteractions/codeInteractionsSlice'
import { selectContentLists } from '../features/contents/contentsSlice'

import { useStyles } from '../styles'
import ContentSummary from "./ContentSummary"

function UserOverview(props) {
  const { user, ...otherProps } = props
  const { t } = useTranslation()
  const classes = useStyles()
  const codeInteractions = useSelector(selectCodeInteractions)
  const codeInteractionsBySlug = _.fromPairs(codeInteractions.map(interaction => [interaction.challenge.slug, interaction]))
  const traceInteractions = useSelector(selectTraceInteractions)
  const traceInteractionsBySlug = _.fromPairs(traceInteractions.map(interaction => [interaction.challenge.slug, interaction]))
  const contents = useSelector(selectContentLists).topics || []

  if (!user || _.isEmpty(user)) return <React.Fragment />
  return (
    <>
      <Typography variant="h1">{`${user.first_name} ${user.last_name}`}</Typography>
      <Typography variant="h3" paragraph={true}>{t("Progress")}</Typography>
      <Grid container spacing={1}>
        {contents.map((content, idx) => (
          <Grid item key={content.slug} xs={3} className={classes.flexbox}>
            <ContentSummary className={clsx(classes.fillParent, classes.flexbox)} idx={idx} content={content} codeInteractionsBySlug={codeInteractionsBySlug} traceInteractionsBySlug={traceInteractionsBySlug} />
          </Grid>
        ))}
      </Grid>
    </>
  )
}

export default UserOverview
