import React, { Component } from "react";
import Button from '@material-ui/core/Button'
import IconButton from '@material-ui/core/IconButton';
import AccountCircle from '@material-ui/icons/AccountCircle';
import Link from '@material-ui/core/Link'
import MenuItem from '@material-ui/core/MenuItem';
import Menu from '@material-ui/core/Menu';
import { customClasses } from '../styles'
import { withTranslation } from 'react-i18next';
import { withStyles } from '@material-ui/core/styles';
import ChangePasswordDialog from './change-password'


class UserButton extends Component {
  constructor(props) {
    super(props);
    this.state = {
      changePasswordOpened: false,
    }
  }

  render() {
    const handleMenu = (event) => {
      this.setState({ anchorEl: event.currentTarget });
    };

    const handleClose = () => {
      this.setState({ anchorEl: null });
    };

    const handlePasswordChange = () => {
      this.setState({ changePasswordOpened: true })
    }

    const handlePasswordChangeClose = () => {
      this.setState({ changePasswordOpened: false })
    }

    const classes = this.props.classes
    const t = this.props.t

    let button
    if (this.props.user) {
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
          anchorEl={this.state.anchorEl}
          anchorOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          keepMounted
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          open={Boolean(this.state.anchorEl)}
          onClose={handleClose}
        >

          <MenuItem onClick={handlePasswordChange}>{t("Change password")}</MenuItem>
          <Link href="/logout/" className={classes.blankLink}><MenuItem>{t("Logout")}</MenuItem></Link>
        </Menu>
        <ChangePasswordDialog opened={this.state.changePasswordOpened} onClose={handlePasswordChangeClose} />
      </div >
    }
    else {
      button = <Button color="inherit" href="/login/">Login</Button>
    }

    return button
  }
}

export default withTranslation()(withStyles(customClasses)(UserButton))
