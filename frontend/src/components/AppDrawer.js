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
import { selectContentLists } from '../features/contents/contentsSlice'

function ContentList(props) {
  const { title, list, nestedContent, hasNumbers, startOpened } = props
  const classes = useStyles()
  const { t } = useTranslation()

  const [opened, setOpened] = useState({ [title]: !_.isNil(startOpened) })

  if (!title || !list) return <></>

  const createClickHandler = (slug) => {
    return () => {
      setOpened(prevOpened => {
        return { ...prevOpened, [slug]: !prevOpened[slug] }
      })
    }
  }

  return (
    <>
      <ListItem button onClick={createClickHandler(title)}>
        <ListItemText primary={title} />
        {opened[title] ? <ExpandLess /> : <ExpandMore />}
      </ListItem>
      <Collapse in={opened[title]} timeout="auto" unmountOnExit>
        {
          list.map((content, idx) => (
            <React.Fragment key={content.slug} >
              {!_.isNil(nestedContent) ?
                <>
                  <ListItem button className={classes.nestedListItem} onClick={createClickHandler(content.slug)} disableGutters>
                    <ListItemText primary={`${!_.isNil(hasNumbers) ? _.padStart(idx + 1, 2, '0') + ". " : ""}${content.title}`} />
                    {opened[content.slug] ? <ExpandLess /> : <ExpandMore />}
                  </ListItem>
                  <Collapse in={opened[content.slug]} timeout="auto" unmountOnExit>
                    <List component="div" disablePadding>
                      <ListItem button className={classes.doubleNestedListItem} component={Link} to={ROUTES.content.link({ slug: content.slug })} disableGutters>
                        <ListItemText primary={t("Handout")} />
                      </ListItem>
                      <ListItem button className={classes.doubleNestedListItem} component={Link} to={ROUTES.contentChallenges.link({ slug: content.slug })} disableGutters>
                        <ListItemText primary={t("Challenges")} />
                      </ListItem>
                    </List>
                  </Collapse>
                </> :
                <ListItem button className={classes.nestedListItem} component={Link} to={ROUTES.content.link({ slug: content.slug })} disableGutters>
                  <ListItemText primary={`${!_.isNil(hasNumbers) ? _.padStart(idx + 1, 2, '0') + ". " : ""}${content.title}`} />
                </ListItem>
              }
            </React.Fragment>
          ))
        }
      </Collapse>
    </>
  )
}

function AppDrawer(props) {
  const { ariaLabel, mobileOpen, onClose, ...otherProps } = props
  const classes = useStyles()
  const { t } = useTranslation()

  const contentLists = useSelector(selectContentLists)
  const topics = contentLists.topics
  const otherLists = _.omit(contentLists, ['topics'])

  const drawer = (
    <div>
      <div className={classes.toolbar} />
      <Divider />
      <List>
        <ContentList title={t("Topics")} list={topics} hasNumbers nestedContent startOpened />
        <Divider />
        {_.entries(otherLists).map(([listName, list]) => (
          <React.Fragment key={listName} >
            <ContentList title={listName} list={list} />
            <Divider />
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
