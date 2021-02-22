import React, { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import Card from '@material-ui/core/Card'
import CardContent from '@material-ui/core/CardContent'
import CardMedia from '@material-ui/core/CardMedia'
import Grid from '@material-ui/core/Grid'
import { Typography } from '@material-ui/core'
import { useStyles } from '../styles'
import { getThanks } from '../api/pygym'
import { STATIC_URL } from './django'

const ThanksPage = (props) => {
  const classes = useStyles()
  const { t } = useTranslation()
  const [authors, setAuthors] = useState([])

  useEffect(() => {
    getThanks().then(setAuthors)
  }, [])

  return (
    <>
      <Typography variant="h1" component="h2">{t("Thanks")}</Typography>
      <Typography paragraph={true}>{t("This page lists people who contributed directly to this software")}.</Typography>
      <Grid container justify="center" spacing={2}>
        {authors.map(author => (
          <Grid item className={classes.flexbox} xs={6} md={3} key={author.title}>
            <Card className={classes.fillParent}>
              <CardMedia
                component="img"
                alt={author.title}
                image={STATIC_URL + "thanks/img/" + author.photo}
                title={author.title}
              />
              <CardContent>
                <Typography variant="h5" component="h2">
                  {author.title}
                </Typography>
                <Typography gutterBottom color="textSecondary" variant="h6" component="h5">
                  {author.subtitle}
                </Typography>
                <Typography paragraph={true}>
                  {author.contribution}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </>
  )
}

export default ThanksPage
