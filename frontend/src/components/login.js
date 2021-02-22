import React, { useState, useEffect, useRef } from "react";
import { useTranslation } from 'react-i18next';
import { useStyles } from '../styles'
import Box from '@material-ui/core/Box'
import Button from '@material-ui/core/Button'
import FormHelperText from '@material-ui/core/FormHelperText'
import TextField from '@material-ui/core/TextField'
import Paper from '@material-ui/core/Paper'
import Typography from '@material-ui/core/Typography'
import logoPt from '../img/logo-big-pt.png'
import logoDefault from '../img/logo-big.png'
import { CSRFToken, formErrors } from './django'

function Login(props) {
  const { t, i18n } = useTranslation()
  const classes = useStyles()
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [usernameError, setUsernameError] = useState("")
  const [passwordError, setPasswordError] = useState("")
  const [loginError, setLoginError] = useState((formErrors["__all__"] && formErrors["__all__"][0].message) ? formErrors["__all__"][0].message : "")

  const setOrError = (setter, errorSetter) => {
    return (event) => {
      let value = event.target.value
      let error = "";
      if (!value) error = t("Can't be empty")
      setter(value)
      errorSetter(error)
    }
  }

  const handleUsernameChanged = setOrError(setUsername, setUsernameError)
  const handlePasswordChanged = setOrError(setPassword, setPasswordError)

  const logoImg = i18n.language === 'pt' ? logoPt : logoDefault
  const hasEmptyFields = !(username && password)

  return (
    <Box height="100%" className={classes.centerVerticalContent}>
      <img src={logoImg} className={classes.loginLogo} />
      <Paper className={classes.loginBack} elevation={3}>
        <Box className={classes.centerVerticalContent} p={2}>
          <Typography variant="h2" color="textPrimary">Login</Typography>

          <Box component="form" method="post" action="/login/" m={2} className={classes.centerVerticalContent}>
            <CSRFToken />

            <TextField
              id="id-username"
              onChange={handleUsernameChanged}
              label={t('Username')}
              variant="outlined"
              required={true}
              name="username"
              autoFocus={true}
              autoCapitalize="none"
              autoComplete="username"
              maxLength="150"
              helperText={usernameError}
              error={Boolean(usernameError)}
              fullWidth />

            <TextField
              id="id-password"
              onChange={handlePasswordChanged}
              label={t('Password')}
              variant="outlined"
              type="password"
              required={true}
              name="password"
              autoComplete="current-password"
              helperText={passwordError ? passwordError : t("In case you haven't changed it, it is the same as your username")}
              error={Boolean(passwordError)}
              fullWidth />

            <Button variant="contained" color="secondary" type="submit" fullWidth disabled={hasEmptyFields}>Login</Button>
            <FormHelperText error={true}>{loginError}</FormHelperText>
          </Box>
        </Box>
      </Paper>
    </Box>
  )
}

export default Login
