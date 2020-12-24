import React, { useState, useEffect, useRef } from "react"
import PropTypes from 'prop-types'
import clsx from 'clsx'
import { useTranslation } from 'react-i18next'
import { useStyles } from '../styles'
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import EjectIcon from '@material-ui/icons/Eject'
import MoreHorizIcon from '@material-ui/icons/MoreHoriz'
import Box from '@material-ui/core/Box'
import Collapse from '@material-ui/core/Collapse'
import IconButton from '@material-ui/core/IconButton'
import TextField from '@material-ui/core/TextField';
import Card from '@material-ui/core/Card';
import CardHeader from '@material-ui/core/CardHeader';
import CardContent from '@material-ui/core/CardContent';

function TraceMemory(props) {
  const { t } = useTranslation()
  const classes = useStyles()
  const [expanded, setExpanded] = useState(true);
  const [disabled, setDisabled] = useState(false);
  const { memory, prefix, isFunction, onDisabledChanged, forceDisable, stateEditable, ...other } = props

  const names = Object.keys(memory)
  names.sort()
  let name = names.shift()
  const curContext = memory[name]
  if (!curContext) return null
  const varNames = Object.keys(curContext).sort()
  const childMemory = {}
  names.forEach((childFullName) => {
    childMemory[childFullName.substr(name.length + 1)] = memory[childFullName]
  })
  const validPrefix = prefix ? `${prefix}-` : ""
  const hasChildren = names.length > 0
  const canExpand = hasChildren
  const actuallyDisabled = disabled || (forceDisable && isFunction)

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const handleDisableClick = () => {
    setDisabled(!disabled)
    onDisabledChanged && onDisabledChanged(!disabled)
  }


  return (
    <Card className={clsx(classes.fillParent, { [classes.cardDisabled]: actuallyDisabled })} elevation={3}>
      <CardHeader
        title={name === '<module>' ? t("Program") : name}
        action={canExpand ?
          <IconButton
            className={clsx(classes.expand, {
              [classes.expandOpen]: expanded,
            })}
            onClick={handleExpandClick}
            aria-expanded={expanded}
            aria-label="show more"
          >
            <ExpandMoreIcon />
          </IconButton>
          : (isFunction && !forceDisable && stateEditable &&
            <IconButton
              className={clsx(classes.expand, {
                [classes.expandOpen]: disabled,
              })}
              onClick={handleDisableClick}
              aria-label="Disable memory"
            >
              <EjectIcon />
            </IconButton>)}
      />
      <Collapse in={(expanded || !canExpand) && !actuallyDisabled} timeout="auto" unmountOnExit>
        <CardContent>
          {varNames.map((varName) =>
            <Box
              m={1}
              key={`${validPrefix}${name}-${varName}`}
              className={classes.inlineSiblings} >

              <TextField
                id={`${validPrefix}${name}-${varName}`}
                InputLabelProps={{ classes: { root: classes.sourceCode } }}
                label={varName}
                defaultValue={curContext[varName]}
                disabled={!stateEditable}
                InputProps={{
                  readOnly: !stateEditable,
                  classes: { root: classes.sourceCode, input: classes.tightTextField },
                }}
                variant="outlined"
              />
            </Box>
          )}
        </CardContent>
      </Collapse>
      {hasChildren &&
        <CardContent>
          {!expanded && canExpand && <MoreHorizIcon />}
          <TraceMemory
            memory={childMemory}
            prefix={`${validPrefix}${name}`}
            isFunction={true}
            onDisabledChanged={onDisabledChanged}
            forceDisable={forceDisable}
            stateEditable={stateEditable}
            {...other} />
        </CardContent>}
    </Card>
  )
}

TraceMemory.propTypes = {
  isFunction: PropTypes.bool,
  memory: PropTypes.object.isRequired,
  prefix: PropTypes.string,
  onDisabledChanged: PropTypes.func,
  forceDisable: PropTypes.bool,
  stateEditable: PropTypes.bool,
}

TraceMemory.defaultProps = {
  isFunction: false,
  forceDisable: false,
  stateEditable: true,
}

export default TraceMemory
