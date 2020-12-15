import React, { useState } from "react";
import { useTranslation } from 'react-i18next';
import { useStyles } from '../styles'
import Button from '@material-ui/core/Button'
import IconButton from '@material-ui/core/IconButton';
import AccountCircle from '@material-ui/icons/AccountCircle';
import Link from '@material-ui/core/Link'
import MenuItem from '@material-ui/core/MenuItem';
import Menu from '@material-ui/core/Menu';
import ChangePasswordDialog from './ChangePasswordDialog'
import ROUTES from '../routes'


function UserButton(props) {
  const { t } = useTranslation()
  const classes = useStyles()
  const [changePasswordOpened, setChangePasswordOpened] = useState(false)
  const [anchorEl, setAnchorEl] = useState(false)

  const handleMenu = (event) => setAnchorEl(event.currentTarget)
  const handleClose = () => setAnchorEl(null)
  const handlePasswordChange = () => setChangePasswordOpened(true)
  const handlePasswordChangeClose = () => setChangePasswordOpened(false)

  let button
  if (props.user) {
    button = <div>
      <IconButton
        aria-label="account of current user"
        aria-controls="menu-appbar"
        aria-haspopup="true"
        onClick={handleMenu}
        color="inherit"
      >
        <AccountCircle />
      </IconButton>
      <Menu
        id="menu-appbar"
        anchorEl={anchorEl}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        keepMounted
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >

        <MenuItem onClick={handlePasswordChange}>{t("Change password")}</MenuItem>
        <Link href={ROUTES.logout.link()} className={classes.blankLink}><MenuItem>{t("Logout")}</MenuItem></Link>
      </Menu>
      <ChangePasswordDialog opened={changePasswordOpened} onClose={handlePasswordChangeClose} />
    </div >
  }
  else {
    button = <Button color="inherit" href={ROUTES.login.link()}>Login</Button>
  }

  return button
}

export default UserButton
