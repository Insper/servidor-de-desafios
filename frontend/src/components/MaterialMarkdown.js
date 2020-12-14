import React, { Component } from "react"
import ReactMarkdown from 'react-markdown'
const gfm = require('remark-gfm')
import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography'
import Link from '@material-ui/core/Link'
import { STATIC_URL } from './django'
import { customClasses } from '../styles'

class MarkdownParagraph extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    const children = this.props.children
    if (children && children[0].type == MarkdownImage) return children
    return <Typography paragraph={true}>{children}</Typography>
  }
}

class MarkdownImage extends Component {
  constructor(props) {
    super(props)
  }

  render() {
    let src = this.props.src
    if (src.startsWith("raw/")) src = STATIC_URL + src
    return <img src={src} alt={this.props.alt} className={this.props.classes.centeredImg} />
  }
}
MarkdownImage = withStyles(customClasses)(MarkdownImage)

class MaterialMarkdown extends Component {
  constructor(props) {
    super(props)
    this.state = {}
  }

  render() {
    const renderers = {
      paragraph: MarkdownParagraph,
      image: MarkdownImage,
      link: Link,
    }
    return <ReactMarkdown plugins={[gfm]} children={this.props.children} renderers={renderers} />
  }
}

export default MaterialMarkdown
