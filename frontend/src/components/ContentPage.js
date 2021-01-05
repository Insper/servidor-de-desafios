import React, { useEffect, useState } from 'react'
import { getPage } from '../api/pygym'
import { useTranslation } from 'react-i18next';
import { Typography } from '@material-ui/core'
import LoadingResultsProgress from './LoadingResultsProgress'
import MaterialMarkdown from './MaterialMarkdown'

function ContentPage(props) {
  const { conceptSlug, pageSlug, ...otherProps } = props
  const { t } = useTranslation()

  const [loading, setLoading] = useState(true)
  const [mdContent, setMdContent] = useState()

  useEffect(() => {
    getPage(conceptSlug, pageSlug)
      .then(setMdContent)
      .catch(console.log)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <LoadingResultsProgress strokeWeight={3} />
  if (typeof mdContent !== 'string') return <Typography>{t("Page not found")}</Typography>
  return (
    <>
      <MaterialMarkdown>
        {mdContent}
      </MaterialMarkdown>
    </>
  )
}

export default ContentPage
