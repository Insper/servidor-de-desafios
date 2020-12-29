import React, { useState, useEffect } from "react"
import PropTypes from 'prop-types'
import clsx from 'clsx'
import _ from 'lodash'
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
import Typography from '@material-ui/core/Typography'

function TraceMemory(props) {
  const { t } = useTranslation()
  const classes = useStyles()
  const [expanded, setExpanded] = useState(true)
  const [disabled, setDisabled] = useState(false)
  const [mutableMemory, setMutableMemory] = useState({})
  const [childMutableMemory, setChildMutableMemory] = useState({})
  const [inputErrors, setInputErrors] = useState({})
  const [localActivateErrors, setLocalActivateErrors] = useState({})
  const [localValueErrors, setLocalValueErrors] = useState({})
  const [allErrors, setAllErrors] = useState({})
  const [childrenHaveEmptyFields, setChildrenHaveEmptyFields] = useState(false)
  const { memory, activateErrors, valueErrors, prefix, isFunction, onDisabledChanged, onMemoryChanged, onHasEmptyFieldsChanged, forceDisable, stateEditable, ...other } = props

  const names = _.keys(memory)
  names.sort()
  let name = names.shift()
  const curContext = memory[name]
  if (!curContext) return null
  const curMemory = { ...curContext, ...mutableMemory }

  const updateInputErrors = errors => {
    setInputErrors(errors)
  }

  useEffect(() => {
    onHasEmptyFieldsChanged && onHasEmptyFieldsChanged(!_.isEmpty(inputErrors) || (childrenHaveEmptyFields && hasChildren))
  }, [onHasEmptyFieldsChanged, memory, inputErrors, childrenHaveEmptyFields, hasChildren])

  useEffect(() => {
    !prefix && onMemoryChanged && onMemoryChanged(memory)
  }, [])

  useEffect(() => {
    let empty = {}
    _.entries(curMemory).forEach(([varName, value]) => {
      if (!value) empty[varName] = t("Can't be empty")
    })
    updateInputErrors(empty)
  }, [curContext, mutableMemory])

  useEffect(() => {
    setLocalActivateErrors(activateErrors)
  }, [activateErrors])

  useEffect(() => {
    setLocalValueErrors(valueErrors)
  }, [valueErrors])

  useEffect(() => {
    setAllErrors(_.merge({}, localValueErrors, { [name]: inputErrors }))
  }, [localValueErrors, inputErrors])

  const removePrefixFromKeys = (obj, prefix) => {
    let clean = {}
    _.keys(obj).forEach((fullKey) => {
      if (fullKey.startsWith(prefix) && fullKey !== prefix) {
        let newName = fullKey.substr(prefix.length + 1)
        clean[newName] = obj[fullKey]
      }
    })
    return clean
  }

  const varNames = _.keys(curContext).sort()
  const hasChildren = names.length > 0
  const childMemory = removePrefixFromKeys(memory, name)

  const validPrefix = prefix ? `${prefix}-` : ""
  const canExpand = hasChildren
  const actuallyDisabled = disabled || (forceDisable && isFunction)

  const childActivateErrors = removePrefixFromKeys(activateErrors, name)
  const childValueErrors = removePrefixFromKeys(valueErrors, name)

  const handleExpandClick = () => {
    setExpanded(!expanded);
  };

  const handleDisableClick = () => {
    setDisabled(!disabled)
    onDisabledChanged && onDisabledChanged(!disabled)
  }

  const removeEntry = (varName, orig) => {
    const dst = {}
    _.entries(orig).forEach(([v, value]) => {
      if (v !== varName) dst[v] = value
    })
    return dst
  }

  const makeMemoryChangeHandler = (varName) => {
    return (event) => {
      let value = event.target.value

      // Update errors
      if (value) {
        updateInputErrors(removeEntry(varName, inputErrors))
      }
      else {
        updateInputErrors({ ...inputErrors, ...{ [varName]: t("Can't be empty") } })
      }
      setLocalValueErrors(_.merge(localValueErrors, { [name]: { [varName]: "" } }))

      // Update memory
      let newMemory = { ...mutableMemory, ...{ [varName]: value } }
      setMutableMemory(newMemory)
      onMemoryChanged && onMemoryChanged({ ...{ [name]: { ...curContext, ...newMemory } }, ...childMutableMemory })
    }
  }

  const handleChildMemoryChanged = (newMemory) => {
    let newChildMemory = {}
    Object.entries(newMemory).forEach(([memName, mem]) => {
      newChildMemory[`${name}.${memName}`] = mem
    })
    setChildMutableMemory(newChildMemory)
    onMemoryChanged && onMemoryChanged({ ...{ [name]: curMemory }, ...newChildMemory })
  }

  return (
    <Card className={clsx(classes.fillParent, { [classes.cardDisabled]: actuallyDisabled })} elevation={3}>
      <CardHeader
        title={name === '<module>' ? t("Program") : name}
        subheader={localActivateErrors[name] && <Typography color="error" variant="body2">{localActivateErrors[name]}</Typography>}
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
          {varNames.map((varName) => {
            let error = ''
            if (name in allErrors && varName in allErrors[name]) {
              error = allErrors[name][varName]
            }

            return <Box
              m={1}
              key={`${validPrefix}${name}-${varName}`}
              className={classes.inlineSiblings} >

              <TextField
                id={`${validPrefix}${name}-${varName}`}
                onChange={makeMemoryChangeHandler(varName)}
                InputLabelProps={{ classes: { root: classes.sourceCode } }}
                label={varName}
                defaultValue={curContext[varName]}
                disabled={!stateEditable || hasChildren}
                helperText={error}
                error={Boolean(error)}
                InputLabelProps={{
                  shrink: true,
                }}
                InputProps={{
                  readOnly: !stateEditable,
                  classes: { root: classes.sourceCode, input: classes.tightTextField },
                }}
                variant="outlined"
              />
            </Box>
          })}
        </CardContent>
      </Collapse>
      {hasChildren &&
        <CardContent>
          {!expanded && canExpand && <MoreHorizIcon />}
          <TraceMemory
            memory={childMemory}
            activateErrors={childActivateErrors}
            valueErrors={childValueErrors}
            prefix={`${validPrefix}${name}`}
            isFunction={true}
            onDisabledChanged={onDisabledChanged}
            onMemoryChanged={handleChildMemoryChanged}
            onHasEmptyFieldsChanged={setChildrenHaveEmptyFields}
            forceDisable={forceDisable}
            stateEditable={stateEditable}
            {...other} />
        </CardContent>}
    </Card>
  )
}

TraceMemory.propTypes = {
  isFunction: PropTypes.bool,
  activateErrors: PropTypes.object,
  valueErrors: PropTypes.object,
  memory: PropTypes.object.isRequired,
  prefix: PropTypes.string,
  onDisabledChanged: PropTypes.func,
  onMemoryChanged: PropTypes.func,
  onHasEmptyFieldsChanged: PropTypes.func,
  forceDisable: PropTypes.bool,
  stateEditable: PropTypes.bool,
}

TraceMemory.defaultProps = {
  isFunction: false,
  activateErrors: {},
  valueErrors: {},
  forceDisable: false,
  stateEditable: true,
}

export default TraceMemory
