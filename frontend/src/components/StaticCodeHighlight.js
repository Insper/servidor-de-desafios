import React from 'react'
import PropTypes from 'prop-types'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';


function StaticCodeHighlight(props) {
  const { children, style, language, highlightLinesPrimary, highlightLinesSecondary, highlightLineNumbers, clickableLines, onClick, ...otherProps } = props

  return (
    <SyntaxHighlighter
      language={language}
      style={style}
      wrapLines={true}
      showLineNumbers={true}
      wrapLongLines={true}
      lineNumberStyle={lineNumber => {
        let style = {
          '&::before': {
            content: '"some content"',
            display: 'block',
            height: 60,
            marginTop: -60
          }
        }
        if (highlightLineNumbers.includes(lineNumber)) style.background = "linear-gradient(to right, rgba(255, 232, 115, 1) 70%, rgba(255, 232, 115, 0))"
        return style
      }}
      lineProps={lineNumber => {
        const lineIsClickable = clickableLines && clickableLines.includes(lineNumber)
        let style = {
          flexFlow: 'wrap',
        };
        if (lineIsClickable) style.cursor = 'pointer'
        if (highlightLinesPrimary && highlightLinesPrimary.includes(lineNumber)) {
          style.background = "linear-gradient(to right, rgba(193, 222, 241, 0.9) 90%, rgba(221, 222, 241, 0))";
        } else if (highlightLinesSecondary && highlightLinesSecondary.includes(lineNumber)) {
          style.background = "linear-gradient(to right, rgba(222, 222, 222, 0.9) 90%, rgba(222, 222, 222, 0))";
        }
        return {
          style: style,
          onClick: () => onClick && lineIsClickable && onClick(lineNumber),
        };
      }}
      customStyle={{
        margin: 0,
        padding: "1em",
        fontSize: "1rem",
      }}
      {...otherProps}>
      { children}
    </SyntaxHighlighter >
  )
}

StaticCodeHighlight.propTypes = {
  highlightLinesPrimary: PropTypes.arrayOf(PropTypes.number),
  highlightLinesSecondary: PropTypes.arrayOf(PropTypes.number),
  highlightLineNumbers: PropTypes.arrayOf(PropTypes.number),
  clickableLines: PropTypes.arrayOf(PropTypes.number),
  onClick: PropTypes.func,
  language: PropTypes.string,
}

StaticCodeHighlight.defaultProps = {
  highlightLinesPrimary: [],
  highlightLinesSecondary: [],
  highlightLineNumbers: [],
  clickableLines: [],
  language: "python",
}

export default StaticCodeHighlight
