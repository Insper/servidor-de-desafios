import React, { Component } from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
} from "react-router-dom";
import { withTranslation } from 'react-i18next';
import CssBaseline from '@material-ui/core/CssBaseline';
import AppBar from '@material-ui/core/AppBar'
import Box from '@material-ui/core/Box'
import Toolbar from '@material-ui/core/Toolbar'
import Container from '@material-ui/core/Container';
import 'fontsource-roboto';
import { ThemeProvider, withStyles } from '@material-ui/core/styles';
import { customClasses, theme } from '../styles'
import CodingChallengeList from './CodingChallengeList'
import CodingChallenge from './CodingChallenge'
import logoPt from '../img/logo-horizontal-small-pt.png'
import logoDefault from '../img/logo-horizontal-small.png'
import UserButton from './UserButton'
import { fetchUserData } from '../api/pygym'
import ROUTES from '../routes'

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {}
  }

  componentDidMount() {
    fetchUserData()
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
                  <Link to={ROUTES.home.link()} className={classes.homeButton}>
                    <img src={logoImg} alt="Logo" className={classes.appLogo} />
                  </Link>
                </div>
                <UserButton user={this.state.user} />
              </Toolbar>
            </AppBar>

            <Box mt={3}>
              <Switch>
                <Route exact path={ROUTES.home.path}>
                  <Container maxWidth={maxContainer}>
                    <CodingChallengeList />
                  </Container>
                </Route>
                <Route path={ROUTES.challenge.path} render={(props) =>
                  <CodingChallenge slug={props.match.params.slug} />
                } />
              </Switch>
            </Box>
          </Router>
        </ThemeProvider>
      </React.Fragment>
    );
  }
}

export default withTranslation()(withStyles(customClasses)(App))

