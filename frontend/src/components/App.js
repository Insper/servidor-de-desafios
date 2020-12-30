import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
} from "react-router-dom";
import { useTranslation } from 'react-i18next'
import clsx from 'clsx'
import AppBar from '@material-ui/core/AppBar'
import Box from '@material-ui/core/Box'
import CssBaseline from '@material-ui/core/CssBaseline'
import IconButton from '@material-ui/core/IconButton'
import MenuIcon from '@material-ui/icons/Menu'
import Toolbar from '@material-ui/core/Toolbar'
import { ThemeProvider } from '@material-ui/core/styles'
import 'fontsource-roboto';
import ContentList from './ContentList'
import CodeChallenge from './CodeChallenge'
import TraceChallenge from './TraceChallenge'
import logo from '../img/logo.svg'
import UserButton from './UserButton'
import { getUserData } from '../api/pygym'
import { useStyles, theme } from '../styles'
import ROUTES from '../routes'
import AppDrawer from "./AppDrawer";
import ConceptDetails from "./ConceptDetails";

function App(props) {
  const classes = useStyles()
  const { t } = useTranslation()

  const [user, setUser] = useState({})
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    getUserData()
      .then(setUser)
      .catch(console.log)
  }, [])

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  return (
    <React.Fragment>
      <CssBaseline />
      <ThemeProvider theme={theme}>
        <Router>
          <div className={classes.root}>
            <AppBar position="fixed" className={classes.appBar}>
              <Toolbar>
                <IconButton
                  color="inherit"
                  aria-label={t("open drawer")}
                  edge="start"
                  onClick={handleDrawerToggle}
                  className={classes.menuButton}
                >
                  <MenuIcon />
                </IconButton>
                <div className={classes.appTitle}>
                  <Link to={ROUTES.home.link()} className={classes.homeButton}>
                    <img src={logo} alt="Logo" className={classes.appLogo} />
                  </Link>
                </div>
                <UserButton user={user} />
              </Toolbar>
            </AppBar>

            <AppDrawer ariaLabel={t("course contents")} mobileOpen={mobileOpen} onClose={handleDrawerToggle} />

            <main className={clsx(classes.content, classes.fillParent)}>
              <div className={classes.toolbar} />
              <Box m={3} className={classes.flexbox}>
                <Switch>
                  <Route exact path={ROUTES.home.path}>
                    <ContentList />
                  </Route>
                  <Route path={ROUTES.challenge.path} render={(props) =>
                    <CodeChallenge slug={props.match.params.slug} />
                  } />
                  <Route path={ROUTES.trace.path} render={(props) =>
                    <TraceChallenge slug={props.match.params.slug} />
                  } />
                  {/* Concepts must be last so the other routes take priority */}
                  <Route path={ROUTES.concept.path} render={(props) =>
                    <ConceptDetails slug={props.match.params.slug} />
                  } />
                </Switch>
              </Box>
            </main>
          </div>
        </Router>
      </ThemeProvider>
    </React.Fragment >
  );
}

export default App

