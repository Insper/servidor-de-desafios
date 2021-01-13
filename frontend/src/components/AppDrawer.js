import React, { useState, useEffect } from "react";
import { useTranslation } from 'react-i18next'
import { Link } from "react-router-dom";
import { useSelector } from 'react-redux'
import Collapse from '@material-ui/core/Collapse'
import Divider from '@material-ui/core/Divider'
import Drawer from '@material-ui/core/Drawer'
import Hidden from '@material-ui/core/Hidden'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import ListItemText from '@material-ui/core/ListItemText'
import ExpandLess from '@material-ui/icons/ExpandLess'
import ExpandMore from '@material-ui/icons/ExpandMore'
import { useStyles } from '../styles'
import ROUTES from '../routes'
import { selectTopics } from '../features/contents/contentsSlice'

function AppDrawer(props) {
  const { ariaLabel, mobileOpen, onClose, ...otherProps } = props
  const classes = useStyles()
  const { t } = useTranslation()

  const topics = useSelector(selectTopics)
  const [opened, setOpened] = useState({})

  const createClickHandler = (slug) => {
    return () => {
      setOpened(prevOpened => {
        return { ...prevOpened, [slug]: !prevOpened[slug] }
      })
    }
  }

  const drawer = (
    <div>
      <div className={classes.toolbar} />
      <Divider />
      <List>
        <ListItem>
          <ListItemText primary={t("Topics")} />
        </ListItem>
        {topics.map((topic, idx) => (
          <React.Fragment key={topic.slug} >
            <ListItem button onClick={createClickHandler(topic.slug)}>
              <ListItemText primary={`${_.padStart(idx + 1, 2, '0')}. ${topic.title}`} />
              {opened[topic.slug] ? <ExpandLess /> : <ExpandMore />}
            </ListItem>
            <Collapse in={opened[topic.slug]} timeout="auto" unmountOnExit>
              <List component="div" disablePadding>
                <ListItem button className={classes.nestedListItem} component={Link} to={ROUTES.content.link({ slug: topic.slug })} disableGutters>
                  <ListItemText primary={t("Handout")} />
                </ListItem>
                <ListItem button className={classes.nestedListItem} component={Link} to={ROUTES.contentChallenges.link({ slug: topic.slug })} disableGutters>
                  <ListItemText primary={t("Challenges")} />
                </ListItem>
              </List>
            </Collapse>
          </React.Fragment>
        ))}
        <Divider />
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
