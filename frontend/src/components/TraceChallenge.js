import React, { useState, useEffect } from "react"
import { useTranslation } from 'react-i18next'
import { useStyles } from '../styles'
import clsx from 'clsx'
import _ from 'lodash'
import { getTrace, postTrace, getTraceStateList } from '../api/pygym'
import StaticCodeHighlight from './StaticCodeHighlight'
import { vs } from 'react-syntax-highlighter/dist/esm/styles/prism'
import Grid from '@material-ui/core/Grid'
import Typography from '@material-ui/core/Typography'
import Box from '@material-ui/core/Box'
import Paper from '@material-ui/core/Paper'
import Snackbar from '@material-ui/core/Snackbar'
import MobileStepper from '@material-ui/core/MobileStepper'
import Button from '@material-ui/core/Button'
import TextField from '@material-ui/core/TextField';
import KeyboardArrowLeft from '@material-ui/icons/KeyboardArrowLeft'
import KeyboardArrowRight from '@material-ui/icons/KeyboardArrowRight'
import Alert from './Alert'
import TraceMemory from './TraceMemory'
import Terminal from './Terminal'
import LoadingResultsProgress from './LoadingResultsProgress'
import { findLinesWithCode } from "../models/trace"
import { traceMessages } from "../api/messages"

function TraceChallenge(props) {
  const { t } = useTranslation()
  const m = traceMessages(t)
  const classes = useStyles()
  const [trace, setTrace] = useState({})
  const [snackbarOpen, setSnackbarOpen] = useState(false)
  const [passedTests, setPassedTests] = useState(false)
  const [states, setStates] = useState([])
  const [currentStateIndex, setCurrentStateIndex] = useState(0)
  const [totalStates, setTotalStates] = useState(0)
  const [nextLine, setNextLine] = useState(null)
  const [linesWithCode, setLinesWithCode] = useState(null)
  const [retval, setRetval] = useState()
  const [latestStateIndex, setLatestStateIndex] = useState(-1)
  const [currentMemory, setCurrentMemory] = useState({})
  const [terminalText, setTerminalText] = useState('')

  // Error messages
  const [memoryErrorMsg, setMemoryErrorMsg] = useState('')
  const [memoryActivateErrors, setMemoryActivateErrors] = useState()
  const [memoryValueErrors, setMemoryValueErrors] = useState()
  const [nextLineErrorMsg, setNextLineErrorMsg] = useState('')
  const [retvalErrorMsg, setRetvalErrorMsg] = useState('')
  const [terminalErrorMsg, setTerminalErrorMsg] = useState('')
  const [hasEmptyMemory, setHasEmptyMemory] = useState(false)

  const updateNextLine = (curIdx, stateList) => {
    const nextState = stateList && stateList.length > curIdx + 1 ? stateList[curIdx + 1] : {}
    if (typeof nextState.line_i === 'number') setNextLine(nextState.line_i + 1)
    else setNextLine(null)
  }

  const updateStates = () => {
    getTraceStateList(props.slug)
      .then(result => {
        setStates(result.states)
        setTotalStates(result.totalStates)
        setLatestStateIndex(result.latestState)
        setCurrentStateIndex(result.states.length - 1)
        updateNextLine(result.states.length - 1, result.states)
      })
      .catch(console.log)
  }

  useEffect(() => {
    getTrace(props.slug)
      .then(traceData => {
        setTrace(traceData)
        setLinesWithCode(findLinesWithCode(traceData.code))
      })
      .catch(console.log)

    updateStates()
  }, []);

  const stateEditable = currentStateIndex === latestStateIndex + 1

  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }

    setSnackbarOpen(false)
  }

  const replaceMessages = errors => {
    let replaced = {}
    _.entries(errors).forEach(([name, ctx]) => {
      if (typeof (ctx) === "number") {
        replaced[name] = m(ctx)
      }
      else {
        replaced[name] = {}
        _.entries(ctx).forEach(([varName, errCode]) => {
          replaced[name][varName] = m(errCode)
        })
      }
    })
    return replaced
  }

  const handleNext = () => {
    if (stateEditable) {
      postTrace(props.slug, currentStateIndex, currentMemory, terminalText, nextLine, retval)
        .then(result => {
          setMemoryErrorMsg(m(result.memory_code.code))
          setMemoryActivateErrors(replaceMessages(result.memory_code.activate_errors))
          setMemoryValueErrors(replaceMessages(result.memory_code.value_errors))
          setNextLineErrorMsg(m(result.next_line_code))
          setRetvalErrorMsg(m(result.retval_code))
          setTerminalErrorMsg(m(result.terminal_code))

          const passedAll = result.memory_code.code === 0 && result.next_line_code === 0 && result.retval_code === 0 && result.terminal_code === 0
          if (passedAll) {
            updateStates()
          }
          setPassedTests(passedAll)
          setSnackbarOpen(true)
        })
        .catch(console.log)
    }
    else {
      const newIdx = Math.min(totalStates, currentStateIndex + 1)
      setCurrentStateIndex(newIdx)
      updateNextLine(newIdx, states)
    }
  }

  const handleBack = () => {
    const newIdx = Math.max(0, currentStateIndex - 1)
    setCurrentStateIndex(newIdx)
    updateNextLine(newIdx, states)
  }

  const handleMemoryChanged = (memory, blockName, varName, value) => {
    setCurrentMemory(memory)

    const hasEmptyEntries = _.values(memory).some(block => _.values(block).some(value => !value))
    setHasEmptyMemory(hasEmptyEntries)

    if (memoryValueErrors && blockName in memoryValueErrors) {
      const newErrors = {}
      _.entries(memoryValueErrors).forEach(([block, vars]) => {
        if (block === blockName) {
          let otherKeys = _.keys(vars)
          _.remove(otherKeys, k => k === varName)
          newErrors[block] = _.pick(vars, otherKeys)
        }
        else newErrors[block] = vars
      })
      setMemoryValueErrors(newErrors)
    }
  }

  const handleRetvalChange = event => {
    setRetvalErrorMsg("")
    setRetval(event.target.value)
  }

  const isLast = totalStates > 0 && currentStateIndex >= totalStates
  const idx = isLast ? totalStates - 1 : currentStateIndex
  const currentState = states && states.length > idx ? states[idx] : {}
  const nextState = states && states.length > idx + 1 ? states[idx + 1] : {}
  const hasNextState = idx + 1 < totalStates
  const linesSelectable = Object.entries(nextState).length === 0 && hasNextState
  const prevState = states && states.length > 0 && idx > 0 ? states[idx - 1] : {}

  const lineContainsReturn = line => _.first(_.split(_.trim(line, ' '))).startsWith('return')
  let hasReturn = false
  let currentRetval = ""
  if (lineContainsReturn(currentState.line)) {
    currentRetval = currentState.retval === null ? '' : currentState.retval
    hasReturn = true
  }
  else if (lineContainsReturn(prevState.line)) {
    currentRetval = prevState.retval === null ? '' : prevState.retval
    hasReturn = true
  }

  const stdout = currentState.stdout ? currentState.stdout : []

  useEffect(() => {
    setCurrentMemory(currentState.name_dicts ? currentState.name_dicts : { '<module>': {} })
  }, [currentState])

  const marginBottom = 10

  if (!trace) return <div className={classes.loadingContainer}><CircularProgress color="secondary" size="10vw" /></div>

  return (
    <>
      <Grid container>
        <Snackbar open={snackbarOpen} autoHideDuration={5000} onClose={handleCloseSnackbar}>
          <Alert onClose={handleCloseSnackbar} severity={passedTests ? "success" : "error"}>{passedTests ? t("Passed all tests") : t("Failed some test")}!</Alert>
        </Snackbar>

        <Grid item className={classes.gridItem} sm={12}>
          <Box mb={3}>
            <Typography variant="h2" component="h1" gutterBottom={true}>{trace.title}</Typography>
            <Typography>{t("What will be the state of the program after the following line is executed? Update the memory and terminal output, and select the next line that will be evaluated by the Python interpreter")}.</Typography>
          </Box>
        </Grid>

        <Grid item className={classes.gridItem} md={6}>
          <Box mb={marginBottom}>
            <Typography variant="h3">{t("Code")}</Typography>
            <Paper className={`${classes.flexbox} ${classes.fillParent}`} elevation={3}>
              {trace.code &&
                <StaticCodeHighlight
                  style={vs}
                  highlightLinesPrimary={typeof currentState.line_i === 'number' ? [currentState.line_i + 1] : []}
                  highlightLinesSecondary={typeof currentState.call_line_i === 'number' ? [currentState.call_line_i + 1] : []}
                  highlightLineNumbers={nextLine ? [nextLine] : []}
                  clickableLines={linesSelectable ? linesWithCode : []}
                  onClick={line => { setNextLine(line); setNextLineErrorMsg("") }}>
                  {trace.code}
                </StaticCodeHighlight>}
            </Paper>
          </Box>
        </Grid>

        <Grid className={`${classes.flexbox} ${classes.gridItem} ${classes.fullHeight}`} container item md={6}>
          <Box mb={marginBottom}>
            {isLast ?
              <Box className={clsx(classes.flexbox, classes.centerContent)}>
                <LoadingResultsProgress size={200} state="success" />
              </Box> :
              <>
                <Typography variant="h3">{t("Memory")}</Typography>
                {memoryErrorMsg && <Typography color="error" variant="body2">{memoryErrorMsg}</Typography>}
                <TraceMemory
                  memory={currentMemory}
                  activateErrors={memoryActivateErrors}
                  valueErrors={memoryValueErrors}
                  onMemoryChanged={handleMemoryChanged}
                  onHasEmptyFieldsChanged={setHasEmptyMemory}
                  readOnly={!stateEditable}
                />

                {hasReturn &&
                  <Box mt={2} className={classes.flexbox}>
                    <TextField
                      id="retval"
                      className={classes.fillParent}
                      onChange={handleRetvalChange}
                      label={t("Return value")}
                      helperText={retvalErrorMsg ? retvalErrorMsg : t("Enter the value returned by the function (leave empty if nothing is returned)")}
                      variant="outlined"
                      defaultValue={currentRetval}
                      error={Boolean(retvalErrorMsg)}
                      InputLabelProps={{
                        shrink: true,
                      }}
                      InputProps={{
                        readOnly: !stateEditable,
                        classes: { root: classes.sourceCode },
                      }}
                    />
                  </Box>}

                <Box mt={2} minHeight="10em" className={classes.flexbox}>
                  <Typography variant="h3">{t("Terminal")}</Typography>
                  {terminalErrorMsg && <Typography color="error" variant="body2">{terminalErrorMsg}</Typography>}
                  <Terminal
                    lines={stdout}
                    onChange={setTerminalText}
                    className={classes.fillParent}
                    getOutput={(line) => line.out}
                    getInput={(line) => line.in}
                    editable={stateEditable}
                  />
                </Box>

                {currentStateIndex < totalStates - 1 &&
                  <Box mt={2} className={classes.flexbox}>
                    <Typography variant="h3">{t("Next line")}</Typography>
                    {nextLineErrorMsg && <Typography color="error" variant="body2">{nextLineErrorMsg}</Typography>}
                    <TextField
                      className={classes.fillParent}
                      error={_.isNil(nextLine)}
                      id="next-line"
                      value={nextLine !== null ? nextLine : ""}
                      helperText={nextLine !== null ? "" : t("Select the next line that will be executed by the Python interpreter by clicking in the code")}
                      variant="outlined"
                      InputProps={{
                        readOnly: true,
                        classes: { root: classes.sourceCode, input: classes.tightTextField },
                      }}
                    />
                  </Box>}
              </>}
          </Box>
        </Grid>
      </Grid >

      <MobileStepper
        variant="progress"
        className={classes.fixedBottom}
        steps={totalStates + 1}
        position="static"
        LinearProgressProps={{ className: classes.fillParent }}
        activeStep={currentStateIndex}
        nextButton={
          <Button size="small" onClick={handleNext} disabled={currentStateIndex >= totalStates || hasEmptyMemory || (hasNextState && !nextLine)}>
            {t("Next")}
            <KeyboardArrowRight />
          </Button>
        }
        backButton={
          <Button size="small" onClick={handleBack} disabled={currentStateIndex === 0}>
            <KeyboardArrowLeft />
            {t("Previous")}
          </Button>
        }
      />
    </>
  );
}

export default TraceChallenge

