import React, { useState, useEffect, useRef } from "react"
import { useTranslation } from 'react-i18next'
import { useStyles } from '../styles'
import clsx from 'clsx'
import { fetchTrace, fetchTraceStateList } from '../api/pygym'
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

function TraceChallenge(props) {
  const { t } = useTranslation()
  const classes = useStyles()
  const [trace, setTrace] = useState({})
  const [snackbarOpen, setSnackbarOpen] = useState(false)
  const [passedTests, setPassedTests] = useState(false)
  const [states, setStates] = useState([])
  const [currentStateIndex, setCurrentStateIndex] = useState(0)
  const [totalStates, setTotalStates] = useState(0)
  const [nextLine, setNextLine] = useState(null)
  const [linesWithCode, setLinesWithCode] = useState(null)
  const [showRetval, setShowRetval] = useState(false)

  const updateNextLine = (curIdx, stateList) => {
    const nextState = stateList && stateList.length > curIdx + 1 ? stateList[curIdx + 1] : {}
    if (typeof nextState.line_i === 'number') setNextLine(nextState.line_i + 1)
    else setNextLine(-1)
  }

  useEffect(() => {
    fetchTrace(props.slug)
      .then(res => res.json())
      .then(traceData => {
        setTrace(traceData)
        setLinesWithCode(findLinesWithCode(traceData.code))
      })
      .catch(console.log)
    fetchTraceStateList(props.slug)
      .then(res => res.json())
      .then(result => {
        setStates(result.states)
        setTotalStates(result.totalStates)
        setCurrentStateIndex(0)
        updateNextLine(0, result.states)
      })
      .catch(console.log)
  }, []);

  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }

    setSnackbarOpen(false)
  }

  const handleNext = () => {
    // TODO SUBMIT CODE AND TEST RESULT
    const newIdx = Math.min(totalStates, currentStateIndex + 1)
    setCurrentStateIndex(newIdx)
    updateNextLine(newIdx, states)
  }

  const handleBack = () => {
    const newIdx = Math.max(0, currentStateIndex - 1)
    setCurrentStateIndex(newIdx)
    updateNextLine(newIdx, states)
  }

  const isLast = totalStates > 0 && currentStateIndex >= totalStates
  const idx = isLast ? totalStates - 1 : currentStateIndex
  const currentState = states && states.length > idx ? states[idx] : {}
  const nextState = states && states.length > idx + 1 ? states[idx + 1] : {}
  const prevState = states && states.length > 0 && idx > 0 ? states[idx - 1] : {}
  const currentMemory = currentState.name_dicts ? currentState.name_dicts : { '<module>': {} }
  const stdout = currentState.stdout ? currentState.stdout : []
  const marginBottom = 10
  const hasRetval = currentState.retval !== null
  const prevRetVal = prevState && Object.entries(prevState).length ? prevState.retval : null
  const hasPrevRetval = prevRetVal !== null
  const stateEditable = false // TODO consider islast

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
                  clickableLines={nextState ? [] : linesWithCode}
                  onClick={setNextLine}>
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
                <TraceMemory
                  memory={currentMemory}
                  onDisabledChanged={setShowRetval}
                  forceDisable={hasRetval}
                  stateEditable={stateEditable}
                />

                {(showRetval || hasRetval || hasPrevRetval) &&
                  <Box mt={2}>
                    <TextField
                      id="retval"
                      label={t("Return value")}
                      helperText={t("Enter the value returned by the function (leave empty if nothing is returned)")}
                      variant="outlined"
                      defaultValue={currentState.retval ? currentState.retval : (hasPrevRetval ? prevRetVal : "")}
                      disabled={hasRetval || hasPrevRetval}
                      InputProps={{
                        readOnly: hasRetval || hasPrevRetval,
                        classes: { root: classes.sourceCode },
                      }}
                    />
                  </Box>}

                <Box mt={2} minHeight="10em" className={classes.flexbox}>
                  <Typography variant="h3">{t("Terminal")}</Typography>
                  <Terminal
                    lines={stdout}
                    className={classes.fillParent}
                    getOutput={(line) => line.out}
                    getInput={(line) => line.in}
                  />
                </Box>

                {currentStateIndex < totalStates - 1 &&
                  <Box mt={2}>
                    <Typography variant="h3">{t("Next line")}</Typography>
                    <TextField
                      error={nextLine === null}
                      id="next-line"
                      value={nextLine ? nextLine : ""}
                      helperText={nextLine !== null ? "" : t("Select the next line that will be executed by the Python interpreter by clicking in the code")}
                      variant="outlined"
                      disabled={true}
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
          <Button size="small" onClick={handleNext} disabled={currentStateIndex > totalStates}>
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

