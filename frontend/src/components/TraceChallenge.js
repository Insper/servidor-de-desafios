import React, { useState, useEffect, useRef } from "react"
import { useTranslation } from 'react-i18next'
import { useStyles } from '../styles'
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

  const updateNextLine = (curIdx, stateList) => {
    const nextState = stateList && stateList.length > curIdx + 1 ? stateList[curIdx + 1] : {}
    if (typeof nextState.line_i === 'number') setNextLine(nextState.line_i + 1)
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
    const newIdx = Math.min(states.length - 1, currentStateIndex + 1)
    setCurrentStateIndex(newIdx)
    updateNextLine(newIdx, states)
  }

  const handleBack = () => {
    const newIdx = newIndex = Math.max(0, currentStateIndex - 1)
    setCurrentStateIndex(newIdx)
    updateNextLine(newIdx, states)
  }

  const currentState = states && states.length ? states[currentStateIndex] : {}
  const nextState = states && states.length > currentStateIndex + 1 ? states[currentStateIndex + 1] : {}
  const currentMemory = currentState.name_dicts ? currentState.name_dicts : { '<module>': {} }
  const stdout = currentState.stdout ? currentState.stdout : []
  const marginBottom = 3

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
              {trace.code ?
                <StaticCodeHighlight
                  style={vs}
                  highlightLinesPrimary={typeof currentState.line_i === 'number' ? [currentState.line_i + 1] : []}
                  highlightLinesSecondary={typeof currentState.call_line_i === 'number' ? [currentState.call_line_i + 1] : []}
                  highlightLineNumbers={nextLine ? [nextLine] : []}
                  clickableLines={nextState ? [] : linesWithCode}
                  onClick={setNextLine}>
                  {trace.code}
                </StaticCodeHighlight>
                : null}
            </Paper>
          </Box>
        </Grid>

        <Grid className={`${classes.flexbox} ${classes.gridItem} ${classes.fullHeight}`} container item md={6}>
          <Box mb={marginBottom}>
            <Typography variant="h3">{t("Memory")}</Typography>
            <TraceMemory memory={currentMemory} />

            <Box mt={2} minHeight="10em" className={classes.flexbox}>
              <Typography variant="h3">{t("Terminal")}</Typography>
              <Terminal
                lines={stdout}
                className={classes.fillParent}
                getOutput={(line) => line.out}
                getInput={(line) => line.in}
              />
            </Box>

            <Box mt={2}>
              <Typography variant="h3">{t("Next line")}</Typography>
              <TextField
                error={nextLine === null}
                id="next-line"
                value={nextLine ? nextLine : ""}
                helperText={nextLine !== null ? "" : t("Select the next line that will be executed by the Python interpreter by clicking in the code")}
                variant="outlined"
                InputProps={{
                  readOnly: true,
                }}
              />
            </Box>
          </Box>
        </Grid>
      </Grid >

      <MobileStepper
        variant="progress"
        className={classes.fixedBottom}
        steps={totalStates}
        position="static"
        LinearProgressProps={{ className: classes.fillParent }}
        activeStep={currentStateIndex}
        nextButton={
          <Button size="small" onClick={handleNext} disabled={currentStateIndex === states.length - 1}>
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

