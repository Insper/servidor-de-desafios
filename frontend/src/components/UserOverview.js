import React, { useState, useEffect } from "react"
import Grid from '@material-ui/core/Grid'
import Typography from '@material-ui/core/Typography'
import _ from "lodash"

import { useStyles } from '../styles'

function UserOverview(props) {
  const { user, ...otherProps } = props
  const classes = useStyles()

  if (!user || _.isEmpty(user)) return <React.Fragment />
  return (
    <>
      <Typography variant="h1">{`${user.first_name} ${user.last_name}`}</Typography>
      <Grid container spacing={3}>
        <Grid item xs={3}>
        </Grid>
        <Grid item xs={6}>
        </Grid>
      </Grid>
    </>
  )
}

export default UserOverview
