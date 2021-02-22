import React, { useState, useEffect } from "react"
import PropTypes from 'prop-types'
import clsx from 'clsx'
import _ from 'lodash'
import { useTranslation } from 'react-i18next'
import { useStyles } from '../styles'
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import MoreHorizIcon from '@material-ui/icons/MoreHoriz'
import Box from '@material-ui/core/Box'
import Collapse from '@material-ui/core/Collapse'
import IconButton from '@material-ui/core/IconButton'
import TextField from '@material-ui/core/TextField';
import Card from '@material-ui/core/Card';
import CardHeader from '@material-ui/core/CardHeader';
import CardContent from '@material-ui/core/CardContent';
import Typography from '@material-ui/core/Typography'

function MemoryEntry(props) {
  const { onChange, variableName, initialValue, errorMsg, readOnly, ...otherProps } = props
  const classes = useStyles()

  return (
    <Box
      m={1}
      className={classes.inlineSiblings} >

      <TextField
        onChange={onChange}
        InputLabelProps={{ classes: { root: classes.sourceCode } }}
        label={variableName}
        defaultValue={initialValue}
        helperText={errorMsg}
        error={Boolean(errorMsg)}
        InputLabelProps={{
          shrink: true,
        }}
        InputProps={{
          readOnly: readOnly,
          classes: { root: classes.sourceCode, input: classes.tightTextField },
        }}
        variant="outlined"
      />
    </Box>
  )
}

MemoryEntry.propTypes = {
  onChange: PropTypes.func,
  variableName: PropTypes.string.isRequired,
  initialValue: PropTypes.any,
  errorMsg: PropTypes.string,
  readOnly: PropTypes.bool,
}

function MemoryBlock(props) {
  const {
    memory,
    blockName,
    readOnly,
    onMemoryChanged,
    activateErrors,
    valueErrors,
    descendantNames,
    ...otherProps } = props
  const { t } = useTranslation()
  const classes = useStyles()

  // States
  const [expanded, setExpanded] = useState(true)
  const [inputErrors, setInputErrors] = useState({})

  // Effects
  useEffect(() => {
    const newInputErrors = {}
    _.entries(memory[blockName]).forEach(([varName, value]) => {
      if (!value) newInputErrors[varName] = t("Can't be empty")
    })
    newInputErrors !== inputErrors && setInputErrors(newInputErrors)
  }, [memory[blockName]])

  // Handlers
  const handleExpandClick = () => {
    setExpanded(!expanded);
  }
  const makeMemoryChangeHandler = varName => {
    return event => {
      const value = event.target.value

      // Update memory
      let newMemory = _.merge({}, memory, { [blockName]: { [varName]: value } })
      onMemoryChanged && onMemoryChanged(newMemory, blockName, varName, value)
    }
  }

  // Constants
  const varNames = _.keys(memory[blockName]).sort()
  const name = _.last(_.split(blockName, ','))
  const hasChildren = !_.isEmpty(descendantNames)
  const varErrors = _.merge({}, valueErrors, { [blockName]: inputErrors })
  const activateError = activateErrors[blockName]

  // Components
  let action
  if (hasChildren) action = (
    <IconButton
      className={clsx(classes.expand, { [classes.expandOpen]: expanded })}
      onClick={handleExpandClick}
      aria-expanded={expanded}
      aria-label={t("show more")}
    >
      <ExpandMoreIcon />
    </IconButton >
  )

  return (
    <Card className={clsx(classes.fillParent, { [classes.cardDisabled]: readOnly || hasChildren })} elevation={3}>
      <CardHeader
        title={name === '<module>' ? t("Program") : name}
        subheader={activateError && <Typography color="error" variant="body2">{activateError}</Typography>}
        action={action}
      />
      <Collapse in={expanded} timeout="auto" unmountOnExit>
        <CardContent>
          {varNames.map(varName => {
            const error = _.hasIn(varErrors, `${blockName}.${varName}`) ? varErrors[blockName][varName] : ''

            return <MemoryEntry
              key={`${blockName}-${varName}`}
              variableName={varName}
              onChange={makeMemoryChangeHandler(varName)}
              initialValue={memory[blockName][varName]}
              readOnly={readOnly || hasChildren}
              errorMsg={error}
            />
          })}
        </CardContent>
      </Collapse>
      {
        hasChildren &&
        <CardContent>
          {!expanded && hasChildren && <MoreHorizIcon />}
          <MemoryBlock
            memory={memory}
            blockName={descendantNames[0]}
            readOnly={readOnly}
            onMemoryChanged={onMemoryChanged}
            activateErrors={activateErrors}
            valueErrors={valueErrors}
            descendantNames={_.slice(descendantNames, 1)}
            {...otherProps}
          />
        </CardContent>
      }
    </Card >
  )
}

MemoryBlock.propTypes = {
  memory: PropTypes.object.isRequired,
  blockName: PropTypes.string,
  readOnly: PropTypes.bool,
  onMemoryChanged: PropTypes.func,
  activateErrors: PropTypes.object,
  valueErrors: PropTypes.object,
  descendantNames: PropTypes.arrayOf(PropTypes.string),
}

MemoryBlock.defaultProps = {
  descendantNames: [],
}

function TraceMemory(props) {
  const { memory, readOnly, activateErrors, valueErrors, onMemoryChanged, ...otherProps } = props
  const { t } = useTranslation()

  // Constants
  const names = _.keys(memory)
  names.sort()

  return (
    <MemoryBlock
      memory={memory}
      blockName={names[0]}
      readOnly={readOnly}
      onMemoryChanged={onMemoryChanged}
      activateErrors={activateErrors}
      valueErrors={valueErrors}
      descendantNames={_.slice(names, 1)}
      {...otherProps}
    />
  )
}

TraceMemory.propTypes = {
  memory: PropTypes.object.isRequired,
  readOnly: PropTypes.bool,
  activateErrors: PropTypes.object,
  valueErrors: PropTypes.object,
  onMemoryChanged: PropTypes.func,
}

TraceMemory.defaultProps = {
  activateErrors: {},
  valueErrors: {},
  readOnly: false,
}

export default TraceMemory
