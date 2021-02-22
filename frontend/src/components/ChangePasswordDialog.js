import React, { useState } from "react";
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogTitle from '@material-ui/core/DialogTitle';
import { useTranslation } from 'react-i18next';
import { postNewPassword } from '../api/pygym'


function ChangePasswordDialog(props) {
  const [oldPassword, setOldPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [repeatPassword, setRepeatPassword] = useState("")
  const [oldPasswordError, setOldPasswordError] = useState("")
  const [newPasswordError, setNewPasswordError] = useState("")
  const [repeatPasswordError, setRepeatPasswordError] = useState("")

  const { t } = useTranslation()

  const handleSubmit = () => {
    setOldPasswordError("")
    setNewPasswordError("")
    setRepeatPasswordError("")
    postNewPassword(oldPassword, newPassword, repeatPassword)
      .then(data => {
        if (data.code === 0) handleClose()
        else if (data.code === 1) setOldPasswordError(t("The old password you typed is incorrect"))
        else if (data.code === 2) setRepeatPasswordError(t("The new passwords you typed don't match"))
        else if (data.code === 3) setNewPasswordError(t("New password can't be the same as the old one"))
      })
      .catch(console.log)
  }

  const handleClose = () => {
    props.onClose && props.onClose()
  };

  const setOrError = (setter, errorSetter) => {
    return (event) => {
      let password = event.target.value
      let error = "";
      if (!password) error = t("Can't be empty")
      setter(password)
      errorSetter(error)
    }
  }

  const handleOldPasswordChanged = setOrError(setOldPassword, setOldPasswordError)
  const handleNewPasswordChanged = setOrError(setNewPassword, setNewPasswordError)
  const handleRepeatPasswordChanged = setOrError(setRepeatPassword, setRepeatPasswordError)

  const hasEmptyFields = !(oldPassword && newPassword && repeatPassword)

  return (
    <Dialog open={props.opened} onClose={handleClose} aria-labelledby="form-dialog-title">
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
          helperText={oldPasswordError}
          error={Boolean(oldPasswordError)}
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
          helperText={newPasswordError}
          error={Boolean(newPasswordError)}
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
          helperText={repeatPasswordError}
          error={Boolean(repeatPasswordError)}
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


export default ChangePasswordDialog
