import React from "react"
import PropTypes from 'prop-types'
import { useStyles } from '../styles'
import Box from '@material-ui/core/Box'
import Typography from '@material-ui/core/Typography'

function Terminal(props) {
  const { keyPrefix, getInput, getOutput, lines, className, ...otherProps } = props
  const classes = useStyles()
  const mergeClassName = className ? `${classes.terminal} ${className}` : classes.terminal

  return (
    <Box className={mergeClassName} {...otherProps}>
      {lines.map((line, idx) => (
        <Box className={classes.terminalLine} key={`${keyPrefix}${idx}`}>
          <Typography className={classes.sourceCode} component="code">{getOutput(line)}</Typography>
          <Typography className={`${classes.sourceCode} ${classes.terminalInput}`} component="code">{getInput(line)}</Typography>
        </Box>
      ))}
    </Box>
  )
}

Terminal.propTypes = {
  lines: PropTypes.arrayOf(PropTypes.object).isRequired,
  keyPrefix: PropTypes.string,
  getOutput: PropTypes.func.isRequired,
  getInput: PropTypes.func.isRequired,
}

Terminal.defaultProps = {
  keyPrefix: "",
}

export default Terminal
