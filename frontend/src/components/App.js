import React, { Component } from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
} from "react-router-dom";
import { withTranslation } from 'react-i18next';
import CssBaseline from '@material-ui/core/CssBaseline';
import AppBar from '@material-ui/core/AppBar'
import Link from '@material-ui/core/Link'
import Toolbar from '@material-ui/core/Toolbar'
import 'fontsource-roboto';
import { ThemeProvider, withStyles } from '@material-ui/core/styles';
import { customClasses, theme } from '../styles'
import Home from './Home'
import logoPt from '../img/logo-horizontal-small-pt.png'
import logoDefault from '../img/logo-horizontal-small.png'
import UserButton from './UserButton'



class App extends Component {
  constructor(props) {
    super(props);
    this.state = {}
  }

  componentDidMount() {
    fetch('/api/user/', { credentials: 'include' })
      .then(res => res.json())
      .then(data => {
        this.setState({ user: data })
      })
      .catch(console.log)
  }

  render() {
    const maxContainer = "lg"
    const t = this.props.t
    const i18n = this.props.i18n
    const classes = this.props.classes
    const logoImg = i18n.language === 'pt' ? logoPt : logoDefault

    return (
      <React.Fragment>
        <CssBaseline />
        <ThemeProvider theme={theme}>
          <Router>
            <AppBar position="static">
              <Toolbar disableGutters={true}>
                <div className={classes.appTitle}>
                  <Link href="/" className={classes.homeButton}>
                    <img src={logoImg} alt="Logo" className={classes.appLogo} />
                  </Link>
                </div>
                <UserButton user={this.state.user} />
              </Toolbar>
            </AppBar>

            <Switch>
              <Route path="/">
                <Home maxContainer={maxContainer} />
              </Route>
            </Switch>
          </Router>
        </ThemeProvider>
      </React.Fragment>
    );
  }
}

export default withTranslation()(withStyles(customClasses)(App))

