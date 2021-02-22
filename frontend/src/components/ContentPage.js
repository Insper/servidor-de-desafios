import React, { useEffect, useState } from 'react'
import { getPage } from '../api/pygym'
import { useTranslation } from 'react-i18next';
import { Typography } from '@material-ui/core'
import MaterialMarkdown from './MaterialMarkdown'

function ContentPage(props) {
  const { contentSlug, pageSlug, ...otherProps } = props
  const { t } = useTranslation()

  const [loading, setLoading] = useState(true)
  const [mdContent, setMdContent] = useState()

  useEffect(() => {
    getPage(contentSlug, pageSlug || "")
      .then(setMdContent)
      .catch(console.error)
      .finally(() => setLoading(false)
      )
  }, [contentSlug, pageSlug])

  if (loading) return <></>
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
