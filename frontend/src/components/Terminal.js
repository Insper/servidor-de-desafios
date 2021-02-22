import React from "react"
import PropTypes from 'prop-types'
import styled from "styled-components";
import clsx from 'clsx'
import { useStyles } from '../styles'
import Box from '@material-ui/core/Box'
import Typography from '@material-ui/core/Typography'


const TerminalTextArea = styled.textarea`
  padding: 0;
  background-color: black;
  border: none;
  color: white;
  font-family: source-code-pro, Menlo, Monaco, Consolas, "Courier New", monospace;
  font-size: 1rem;
  letter-spacing: 0.01em;
  line-height: 1.5;
  width: 100%;
  &:focus {
    outline: none
  }
`


function Terminal(props) {
  const { keyPrefix, getInput, getOutput, lines, className, onChange, editable, ...otherProps } = props
  const classes = useStyles()

  const handleChange = (event) => {
    onChange && onChange(event.target.value)
  }

  return (
    <Box className={clsx(classes.terminal, { [className]: className })} {...otherProps}>
      {lines.map((line, idx) => (
        <Box key={`${keyPrefix}${idx}`}>
          <Typography className={classes.sourceCode} component="code">{getOutput(line)}</Typography>
          <Typography className={`${classes.sourceCode} ${classes.terminalInput}`} component="code">{getInput(line)}</Typography>
        </Box>
      ))}
      {editable &&
        <Box>
          <TerminalTextArea rows="3" onChange={handleChange}></TerminalTextArea>
        </Box>
      }
    </Box>
  )
}

Terminal.propTypes = {
  lines: PropTypes.arrayOf(PropTypes.object).isRequired,
  keyPrefix: PropTypes.string,
  getOutput: PropTypes.func.isRequired,
  getInput: PropTypes.func.isRequired,
  onChange: PropTypes.func,
  editable: PropTypes.bool,
}

Terminal.defaultProps = {
  keyPrefix: "",
  editable: true,
}

export default Terminal
