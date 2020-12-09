import React, { Component } from "react";
import { withTranslation } from 'react-i18next';
import { withStyles } from '@material-ui/core/styles';
import Box from '@material-ui/core/Box'
import Button from '@material-ui/core/Button'
import FormHelperText from '@material-ui/core/FormHelperText'
import TextField from '@material-ui/core/TextField'
import Paper from '@material-ui/core/Paper'
import Typography from '@material-ui/core/Typography'
import { customClasses } from '../styles'
import logoPt from '../img/logo-big-pt.png'
import logoDefault from '../img/logo-big.png'
import { CSRFToken, formErrors } from './django'

class Login extends Component {
  constructor(props) {
    super(props);
    this.handleUsernameChanged = this.handleUsernameChanged.bind(this)
    this.handlePasswordChanged = this.handlePasswordChanged.bind(this)
    const loginError = (formErrors["__all__"] && formErrors["__all__"][0].message) ? formErrors["__all__"][0].message : ""
    this.state = {
      usernameError: "",
      passwordError: "",
      loginError: loginError,
    }
  }

  handleUsernameChanged(event) {
    let username = event.target.value
    let error;
    if (!username) error = this.props.t("Can't be empty")
    this.setState({ usernameError: error })
  }

  handlePasswordChanged(event) {
    let password = event.target.value
    let error;
    if (!password) error = this.props.t("Can't be empty")
    this.setState({ passwordError: error })
  }

  render() {
    const t = this.props.t
    const i18n = this.props.i18n
    const classes = this.props.classes
    const logoImg = i18n.language === 'pt' ? logoPt : logoDefault

    return (
      <Box height="100%" className={classes.centerVerticalContent}>
        <img src={logoImg} className={classes.loginLogo} />
        <Paper className={classes.loginBack} elevation={3}>
          <Box className={classes.centerVerticalContent} p={2}>
            <Typography variant="h2" color="textPrimary">Login</Typography>

            <Box component="form" method="post" action="/login/" m={2} className={classes.centerVerticalContent}>
              <CSRFToken />

              <TextField id="id-username" onChange={this.handleUsernameChanged} label={t('Username')} variant="outlined" required={true} name="username" autoFocus={true} autoCapitalize="none" autoComplete="username" maxLength="150" helperText={this.state.usernameError} error={Boolean(this.state.usernameError)} fullWidth />

              <TextField id="id-password" onChange={this.handlePasswordChanged} label={t('Password')} variant="outlined" type="password" required={true} name="password" autoComplete="current-password" helperText={this.state.passwordError ? this.state.passwordError : t("In case you haven't changed it, it is the same as your username")} error={Boolean(this.state.passwordError)} fullWidth />

              <Button variant="contained" color="secondary" type="submit" fullWidth >Login</Button>
              <FormHelperText error={true}>{this.state.loginError}</FormHelperText>
            </Box>
          </Box>

          {/* < p > <a href="{% url 'password_reset' %}">Esqueceu a senha?</a></p> */}
        </Paper>
      </Box>
    )
  }
}

export default withTranslation()(withStyles(customClasses)(Login));
