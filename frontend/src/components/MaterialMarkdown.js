import React, { useState, useEffect, useRef } from "react";
import clsx from "clsx"
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { prism } from 'react-syntax-highlighter/dist/esm/styles/prism'
import _ from 'lodash'
import unified from 'unified'
import parse from 'remark-parse'
import remark2rehype from 'remark-rehype'
import rehype2react from 'rehype-react'
import math from 'remark-math'
import katex from 'rehype-katex'
import raw from 'rehype-raw'
import directive from 'remark-directive'
import visit from 'unist-util-visit'
import h from 'hastscript'
import gfm from 'remark-gfm'
import { useStyles, Colors } from '../styles'
import Card from '@material-ui/core/Card'
import CardContent from '@material-ui/core/CardContent'
import CardHeader from '@material-ui/core/CardHeader'
import Collapse from "@material-ui/core/Collapse"
import IconButton from '@material-ui/core/IconButton'
import Link from '@material-ui/core/Link'
import { Link as RouterLink } from "react-router-dom";
import Typography from '@material-ui/core/Typography'
import InfoIcon from '@material-ui/icons/Info'
import FitnessCenterIcon from '@material-ui/icons/FitnessCenter'
import ErrorIcon from '@material-ui/icons/Error'
import ExpandLess from '@material-ui/icons/ExpandLess'
import ExpandMore from '@material-ui/icons/ExpandMore'
import { STATIC_URL } from './django'
import { useTranslation } from "react-i18next";
import { useSelector } from 'react-redux'
import StaticCodeHighlight from './StaticCodeHighlight'
import ROUTES from '../routes'
import { selectCodeChallengeBySlug } from '../features/codeChallenges/codeChallengesSlice'
import { selectTraceChallengeBySlug } from '../features/traceChallenges/traceChallengesSlice'

function MarkdownParagraph(props) {
  const { children, ...otherProps } = props
  if (children && children[0].type === MarkdownImage) return children
  return <Typography paragraph={true}>{children}</Typography>
}

function MarkdownLink(props) {
  const { href, ...otherProps } = props
  let safeHref = href
  if (href.startsWith("raw/")) safeHref = STATIC_URL + href
  else if (href.startsWith("/")) {
    return <Link component={RouterLink} to={href} {...otherProps} />
  }
  return <Link href={safeHref} {...otherProps} />
}

function MarkdownImage(props) {
  const classes = useStyles()
  const { src, ...otherProps } = props
  let safeSrc = src
  if (src.startsWith("raw/")) safeSrc = STATIC_URL + src
  return <img src={safeSrc} alt={props.alt} className={classes.centeredImg} {...otherProps} />
}

// Admonitions had to be implemented by hand: https://github.com/elviswolcott/remark-admonitions/issues/27
// Implementation based on: https://github.com/remarkjs/remark-directive
// Style and more from: https://squidfunk.github.io/mkdocs-material/reference/admonitions/
function MarkdownAdmonition(props) {
  const { children, type, title, collapse, ...otherProps } = props
  const classes = useStyles()
  const [open, setOpen] = useState(!_.isNil(collapse) ? collapse : true)
  const { t } = useTranslation()
  const collapsable = !_.isNil(collapse)

  const toggleOpen = () => {
    setOpen(op => !op)
    return true
  }

  let typeClass
  let titleClass
  let icon
  switch (type) {
    case 'info':
      typeClass = classes.admonitionCardInfo
      titleClass = classes.admonitionTitleInfo
      icon = <InfoIcon className={classes.admonitionIcon} htmlColor={Colors.INFO} />
      break
    case 'danger':
      typeClass = classes.admonitionCardDanger
      titleClass = classes.admonitionTitleDanger
      icon = <ErrorIcon className={classes.admonitionIcon} htmlColor={Colors.DANGER} />
      break
    case 'exercise':
      typeClass = classes.admonitionCardExercise
      titleClass = classes.admonitionTitleExercise
      icon = <FitnessCenterIcon className={classes.admonitionIcon} htmlColor={Colors.EXERCISE} />
      break
    case 'success':
      typeClass = classes.admonitionCardSuccess
      titleClass = classes.admonitionTitleSuccess
      icon = <FitnessCenterIcon className={classes.admonitionIcon} htmlColor={Colors.SUCCESS} />
      break
  }

  return (
    <Card className={clsx(classes.admonitionCard, typeClass)}>
      {title && (
        <CardHeader
          title={(
            <>
              {icon}
              <MaterialMarkdown raw>{title}</MaterialMarkdown>
            </>
          )}
          action={
            collapsable && <IconButton aria-label={t("show more")}>
              {open ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          }
          onClick={toggleOpen}
          className={clsx(classes.admonitionTitle, titleClass)} titleTypographyProps={{ noWrap: true, className: classes.admonitionTitleTypography }} />
      )}
      <Collapse in={open || !collapsable}>
        <CardContent className={classes.admonitionContent}>
          {children}
        </CardContent>
      </Collapse>
    </Card>
  )
}

function MarkdownCodeSnippet(props) {
  const { file, ...otherProps } = props
  const [content, setContent] = useState()

  useEffect(() => {
    fetch(STATIC_URL + file)
      .then(response => response.text())
      .then(setContent)
      .catch(console.log)
  }, [])

  if (!content) return <></>
  return (
    <MarkdownCode {...otherProps}>{[content]}</MarkdownCode>
  )
}

function MarkdownChallenge(props) {
  const { type, slug, ...otherProps } = props
  let selector, route
  switch (type) {
    case "trace":
      selector = selectTraceChallengeBySlug
      route = ROUTES.trace
      break
    default:
      selector = selectCodeChallengeBySlug
      route = ROUTES.challenge
      break
  }
  const challenge = useSelector(state => selector(state, slug))

  if (!challenge) return <></>
  return (
    <>
      <RouterLink to={route.link({ slug })}>{challenge.title}</RouterLink>
    </>)
}

function MarkdownCode(props) {
  // We assume there is always a single child
  const { children, showLineNumbers, className } = props
  let language = "python"
  if (_.split(children, '\n').length <= 1) {
    let newChildren = children
    if (children && children[0].startsWith("#!")) {
      const start = children[0].indexOf(' ')
      language = children[0].substring(2, start)
      newChildren = [children[0].substring(start + 1)]
    }
    return (
      <SyntaxHighlighter language={language} customStyle={{ padding: "0.1em" }} PreTag={"span"} style={prism}>
        {newChildren}
      </SyntaxHighlighter>
    )
  }
  if (className && className.startsWith("language-")) language = className.substring(9)
  return (
    <StaticCodeHighlight
      language={language}
      customStyle={{
        padding: "8px",
      }}
      showLineNumbers={!_.isNil(showLineNumbers)}
    >
      {[_.trim(children[0])]}
    </StaticCodeHighlight>
  )
}

function makeDirectives(directives) {
  return () => tree => {
    visit(tree, ['textDirective', 'leafDirective', 'containerDirective'], node => {
      if (!directives.includes(node.name)) return
      const data = node.data || (node.data = {})
      var hast = h(node.name, node.attributes)

      data.hName = hast.tagName
      data.hProperties = hast.properties
    })
  }
}

function parseMarkdown(markdown, components) {
  return unified()
    .use(parse)
    .use(gfm)
    .use(directive)
    .use(makeDirectives(['admonition', 'snip', 'challenge']))
    .use(math)
    .use(remark2rehype, { allowDangerousHtml: true })
    .use(katex)
    .use(raw)
    .use(rehype2react, {
      createElement: React.createElement,
      components: components
    })
    .processSync(markdown).result
}

function MaterialMarkdown(props) {
  const { children, raw } = props

  return (
    parseMarkdown(
      children,
      {
        admonition: MarkdownAdmonition,
        snip: MarkdownCodeSnippet,
        challenge: MarkdownChallenge,
        img: MarkdownImage,
        a: MarkdownLink,
        code: MarkdownCode,
        p: _.isNil(raw) ? MarkdownParagraph : 'span',
      }
    )
  )
}

export default MaterialMarkdown
