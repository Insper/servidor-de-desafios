import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from 'react-markdown'
const gfm = require('remark-gfm')
import { useStyles } from '../styles'
import Typography from '@material-ui/core/Typography'
import Link from '@material-ui/core/Link'
import { STATIC_URL } from './django'

function MarkdownParagraph(props) {
  const children = props.children
  if (children && children[0].type == MarkdownImage) return children
  return <Typography paragraph={true}>{children}</Typography>
}

function MarkdownImage(props) {
  const classes = useStyles()
  let src = props.src
  if (src.startsWith("raw/")) src = STATIC_URL + src
  return <img src={src} alt={props.alt} className={classes.centeredImg} />
}

function MaterialMarkdown(props) {
  return <ReactMarkdown plugins={[gfm]} children={props.children} renderers={{
    paragraph: MarkdownParagraph,
    image: MarkdownImage,
    link: Link,
  }} />
}

export default MaterialMarkdown
