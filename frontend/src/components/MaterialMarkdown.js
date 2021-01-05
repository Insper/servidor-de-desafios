import React, { useState, useEffect, useRef } from "react";
import clsx from "clsx"
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { prism } from 'react-syntax-highlighter/dist/esm/styles/prism'
import _ from 'lodash'
import unified from 'unified'
import parse from 'remark-parse'
import remark2rehype from 'remark-rehype'
import rehype2react from 'rehype-react'
import raw from 'rehype-raw'
import directive from 'remark-directive'
import visit from 'unist-util-visit'
import h from 'hastscript'
import gfm from 'remark-gfm'
import { useStyles, Colors } from '../styles'
import Card from '@material-ui/core/Card'
import CardContent from '@material-ui/core/CardContent'
import CardHeader from '@material-ui/core/CardHeader'
import Link from '@material-ui/core/Link'
import Typography from '@material-ui/core/Typography'
import InfoIcon from '@material-ui/icons/Info'
import FitnessCenterIcon from '@material-ui/icons/FitnessCenter'
import ErrorIcon from '@material-ui/icons/Error'
import { STATIC_URL } from './django'
import StaticCodeHighlight from './StaticCodeHighlight'

function MarkdownParagraph(props) {
  const { children, ...otherProps } = props
  if (children && children[0].type === MarkdownImage) return children
  return <Typography paragraph={true}>{children}</Typography>
}

function MarkdownLink(props) {
  const { href, ...otherProps } = props
  let safeHref = href
  if (href.startsWith("raw/")) safeHref = STATIC_URL + href
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
function MarkdownAdmonition(props) {
  const { children, type, title, ...otherProps } = props
  const classes = useStyles()
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
  }

  return (
    <Card className={clsx(classes.admonitionCard, typeClass)}>
      {title && (
        <CardHeader title={(
          <>
            {icon}
            <RawMarkdown>{title}</RawMarkdown>
          </>
        )} className={clsx(classes.admonitionTitle, titleClass)} titleTypographyProps={{ noWrap: true, className: classes.admonitionTitleTypography }} />
      )}
      <CardContent className={classes.admonitionContent}>
        {children}
      </CardContent>
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
    <MarkdownCode>{[content]}</MarkdownCode>
  )
}

function MarkdownCode(props) {
  // We assume there is always a single child
  const { children } = props
  if (_.split(children, '\n').length <= 1) {
    let newChildren = children
    let language = "python"
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
  return (
    <StaticCodeHighlight
      customStyle={{
        padding: "8px",
      }}
      showLineNumbers={false}
    >
      {[_.trim(children[0])]}
    </StaticCodeHighlight>
  )
}

function makeDirectives(directives) {
  return () => tree => {
    visit(tree, ['textDirective', 'leafDirective', 'containerDirective'], node => {
      if (!_.includes(directives, node.name)) return

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
    .use(makeDirectives(['admonition', 'snip']))
    .use(remark2rehype, { allowDangerousHtml: true })
    .use(raw)
    .use(rehype2react, {
      createElement: React.createElement,
      components: components
    })
    .processSync(markdown).result
}

function RawMarkdown(props) {
  return parseMarkdown(
    props.children,
    {
      admonition: MarkdownAdmonition,
      img: MarkdownImage,
      p: "span",
      a: MarkdownLink,
      code: MarkdownCode,
    }
  )
}

function MaterialMarkdown(props) {
  return (
    parseMarkdown(
      props.children,
      {
        admonition: MarkdownAdmonition,
        snip: MarkdownCodeSnippet,
        img: MarkdownImage,
        p: MarkdownParagraph,
        a: MarkdownLink,
        code: MarkdownCode,
      }
    )
  )
}

export default MaterialMarkdown
