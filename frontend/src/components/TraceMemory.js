import React, { useState, useEffect, useRef } from "react"
import { useTranslation } from 'react-i18next'
import { useStyles } from '../styles'
import Box from '@material-ui/core/Box'
import TextField from '@material-ui/core/TextField';
import Typography from '@material-ui/core/Typography'
import Paper from '@material-ui/core/Paper'

function TraceMemory(props) {
  const { t } = useTranslation()
  const classes = useStyles()
  const { memory, prefix, ...other } = props

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

  return (
    <Paper className={`${classes.flexbox} ${classes.fillParent}`} elevation={3}>
      <Box p={2}>
        <Typography variant="h5">{name === '<module>' ? t("Program") : name}</Typography>
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
              InputProps={{
                readOnly: true,
                classes: { root: classes.sourceCode },
              }}
              variant="outlined"
            />
          </Box>
        )}
        <TraceMemory memory={childMemory} prefix={`${validPrefix}${name}`} {...other} />
      </Box>
    </Paper>
  )
}

export default TraceMemory
