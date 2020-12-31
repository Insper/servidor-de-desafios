import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useSelector } from 'react-redux'
import Divider from '@material-ui/core/Divider'
import Drawer from '@material-ui/core/Drawer'
import Hidden from '@material-ui/core/Hidden'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import ListItemText from '@material-ui/core/ListItemText'
import { useStyles } from '../styles'
import ROUTES from '../routes'
import { selectConcepts } from '../features/concepts/conceptsSlice'

function AppDrawer(props) {
  const { ariaLabel, mobileOpen, onClose, ...otherProps } = props
  const classes = useStyles()

  const concepts = useSelector(selectConcepts)

  const drawer = (
    <div>
      <div className={classes.toolbar} />
      <Divider />
      <List>
        {concepts.map(concept => (
          <React.Fragment key={concept.slug} >
            <ListItem button component={Link} to={ROUTES.concept.link({ slug: concept.slug })}>
              <ListItemText primary={concept.name} />
            </ListItem>
            {/* <Divider /> */}
          </React.Fragment>
        ))}
      </List>
    </div >
  )

  return (
    <nav className={classes.drawer} aria-label={ariaLabel}>
      <Hidden smUp implementation="css">
        <Drawer
          variant="temporary"
          anchor="left"
          open={mobileOpen}
          onClose={onClose}
          classes={{
            paper: classes.drawerPaper,
          }}
          ModalProps={{
            keepMounted: true, // Better open performance on mobile.
          }}
        >
          {drawer}
        </Drawer>
      </Hidden>
      <Hidden xsDown implementation="css">
        <Drawer
          classes={{
            paper: classes.drawerPaper,
          }}
          variant="permanent"
          open
        >
          {drawer}
        </Drawer>
      </Hidden>
    </nav>
  )
}

export default AppDrawer
