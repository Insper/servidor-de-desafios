import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
} from "react-router-dom";
import { useTranslation } from 'react-i18next';
import CssBaseline from '@material-ui/core/CssBaseline';
import AppBar from '@material-ui/core/AppBar'
import Box from '@material-ui/core/Box'
import Toolbar from '@material-ui/core/Toolbar'
import Container from '@material-ui/core/Container';
import 'fontsource-roboto';
import { ThemeProvider } from '@material-ui/core/styles';
import ContentList from './ContentList'
import CodeChallenge from './CodeChallenge'
import TraceChallenge from './TraceChallenge'
import logo from '../img/logo.svg'
import UserButton from './UserButton'
import { getUserData } from '../api/pygym'
import { useStyles, theme } from '../styles'
import ROUTES from '../routes'

function App(props) {
  const [user, setUser] = useState({})

  useEffect(() => {
    getUserData()
      .then(setUser)
      .catch(console.log)
  }, []);

  const maxContainer = "lg"
  const { i18n } = useTranslation()
  const classes = useStyles()

  return (
    <React.Fragment>
      <CssBaseline />
      <ThemeProvider theme={theme}>
        <Router>
          <AppBar position="static">
            <Toolbar disableGutters={true}>
              <div className={classes.appTitle}>
                <Link to={ROUTES.home.link()} className={classes.homeButton}>
                  <img src={logo} alt="Logo" className={classes.appLogo} />
                </Link>
              </div>
              <UserButton user={user} />
            </Toolbar>
          </AppBar>

          <Box mt={3}>
            <Switch>
              <Route exact path={ROUTES.home.path}>
                <Container maxWidth={maxContainer}>
                  <ContentList />
                </Container>
              </Route>
              <Route path={ROUTES.challenge.path} render={(props) =>
                <CodeChallenge slug={props.match.params.slug} />
              } />
              <Route path={ROUTES.trace.path} render={(props) =>
                <TraceChallenge slug={props.match.params.slug} />
              } />
            </Switch>
          </Box>
        </Router>
      </ThemeProvider>
    </React.Fragment>
  );
}

export default App

