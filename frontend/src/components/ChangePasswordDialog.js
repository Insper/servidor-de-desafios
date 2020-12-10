import React, { Component } from 'react';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import { withTranslation } from 'react-i18next';
import { csrftoken } from './django'


class ChangePasswordDialog extends Component {
  constructor(props) {
    super(props);
    this.state = {
      oldPasswordError: "",
      newPasswordError: "",
      repeatPasswordError: "",
    }
  }

  render() {
    const t = this.props.t

    const handleSubmit = () => {
      this.setState({
        oldPasswordError: "",
        newPasswordError: "",
        repeatPasswordError: "",
      })
      fetch('/api/change-password/', {
        credentials: 'include',
        method: 'POST',
        mode: 'same-origin',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({
          oldPassword: this.state.oldPassword,
          newPassword: this.state.newPassword,
          repeatPassword: this.state.repeatPassword
        })
      })
        .then(res => res.json())
        .then(data => {
          if (data.code === 0) handleClose()
          else if (data.code === 1) this.setState({ oldPasswordError: t("The old password you typed is incorrect") })
          else if (data.code === 2) this.setState({ repeatPasswordError: t("The new passwords you typed don't match") })
          else if (data.code === 3) this.setState({ newPasswordError: t("New password can't be the same as the old one") })
        })
        .catch(console.log)
    }

    const handleClose = () => {
      this.props.onClose && this.props.onClose()
    };

    const handleOldPasswordChanged = (event) => {
      let password = event.target.value
      let error = "";
      if (!password) error = this.props.t("Can't be empty")
      this.setState({ oldPassword: password, oldPasswordError: error })
    }

    const handleNewPasswordChanged = (event) => {
      let password = event.target.value
      let error = "";
      if (!password) error = this.props.t("Can't be empty")
      this.setState({ newPassword: password, newPasswordError: error })
    }

    const handleRepeatPasswordChanged = (event) => {
      let password = event.target.value
      let error = "";
      if (!password) error = this.props.t("Can't be empty")
      this.setState({ repeatPassword: password, repeatPasswordError: error })
    }

    const hasEmptyFields = !(this.state.oldPassword && this.state.newPassword && this.state.repeatPassword)

    return (
      <Dialog open={this.props.opened} onClose={handleClose} aria-labelledby="form-dialog-title">
        <DialogTitle id="form-dialog-title">{t("Change password")}</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label={t("Old password")}
            type="password"
            required={true}
            onChange={handleOldPasswordChanged}
            autoComplete="current-password"
            variant="outlined"
            helperText={this.state.oldPasswordError}
            error={Boolean(this.state.oldPasswordError)}
            fullWidth
          />
          <TextField
            margin="dense"
            label={t("New password")}
            type="password"
            required={true}
            onChange={handleNewPasswordChanged}
            name="new-password"
            variant="outlined"
            helperText={this.state.newPasswordError}
            error={Boolean(this.state.newPasswordError)}
            fullWidth
          />
          <TextField
            margin="dense"
            label={t("Repeat new password")}
            type="password"
            required={true}
            onChange={handleRepeatPasswordChanged}
            name="repeat-password"
            variant="outlined"
            helperText={this.state.repeatPasswordError}
            error={Boolean(this.state.repeatPasswordError)}
            fullWidth
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="primary">
            {t("Cancel")}
          </Button>
          <Button onClick={handleSubmit} color="primary" type="submit" disabled={hasEmptyFields}>
            {t("Submit")}
          </Button>
        </DialogActions>
      </Dialog>
    )
  }
}


export default withTranslation()(ChangePasswordDialog)
