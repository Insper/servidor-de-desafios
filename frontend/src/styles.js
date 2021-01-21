import { createMuiTheme, makeStyles, responsiveFontSizes } from '@material-ui/core/styles';

// Python color pallete (https://www.schemecolor.com/python-logo-colors.php#:~:text=The%20Python%20Logo%20Colors%20with,and%20Granite%20Gray%20(%23646464).):
const Colors = {
  BLUE1: '#4b8bbe',
  BLUE2: '#306998',
  YELLOW1: '#ffe873',
  YELLOW2: '#ffd43b',
  GRAY1: '#646464',
  GRAY2: '#e0e0e0',
  DISABLED: '#cccccc',
  TERMINAL_INPUT: '#27e427',
  SUCCESS: '#39c27c',
  SUCCESS_BACKGROUND: 'rgba(0,200,83,.1)',
  DANGER: '#ff1744',
  DANGER_BACKGROUND: 'rgba(255,23,68,.1)',
  INFO: '#448aff',
  INFO_BACKGROUND: 'rgba(68,138,255,.1)',
  EXERCISE: '#651fff',
  EXERCISE_BACKGROUND: 'rgba(101,31,255,.1)',
}


let theme = createMuiTheme({
  palette: {
    primary: {
      main: Colors.BLUE2,
      light: Colors.BLUE1,
    },
    secondary: {
      main: Colors.YELLOW2,
      light: Colors.YELLOW1,
    },
  },
  typography: {
    fontSize: 12,
  },
});
theme = responsiveFontSizes(theme);

const drawerWidth = 240
const admonitionLeftBorder = 5

const customClasses = {
  root: {
    display: 'flex',
  },
  titleIcon: {
    marginRight: "10px"
  },
  appTitle: {
    flexGrow: 1
  },
  homeButton: {
    display: "flex"
  },
  loginLogo: {
    maxHeight: "30vh"
  },
  loginBack: {
    backgroundColor: Colors.GRAY2,
    display: "flex",
    flexDirection: "column",
    alignItems: "center"
  },
  centerVerticalContent: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "2em",
  },
  blankLink: {
    textDecoration: "none",
    display: "block",
  },
  appLogo: {
    maxHeight: "3rem",
    margin: theme.spacing(1),
  },
  loadingContainer: {
    margin: "8em",
    display: "flex",
    justifyContent: "center",
  },
  centeredImg: {
    display: "block",
    marginLeft: "auto",
    marginRight: "auto",
    maxWidth: "100%",
    padding: theme.spacing(2, 0),
  },
  flexbox: {
    display: "flex",
    flexDirection: "column",
  },
  horizontalFlexbox: {
    display: "flex",
    flexDirection: "row",
  },
  fillParent: {
    flexGrow: 1,
  },
  inlineSiblings: {
    display: "inline-flex",
  },
  gridItem: {
    paddingLeft: theme.spacing(3),
    paddingRight: theme.spacing(3),
  },
  success: {
    color: Colors.SUCCESS,
  },
  danger: {
    color: Colors.DANGER,
  },
  centerContent: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
  },
  contentHolder: {
    padding: theme.spacing(3),
  },
  w100: {
    width: "100%",
  },
  sourceCode: {
    fontFamily: 'source-code-pro, Menlo, Monaco, Consolas, "Courier New", monospace !important',
    letterSpacing: "0.01em",
  },
  terminal: {
    backgroundColor: "black",
    color: "white",
    padding: theme.spacing(2),
    width: "100%",
  },
  terminalInput: {
    color: Colors.TERMINAL_INPUT,
  },
  editor: {
    flexGrow: 1,
    minHeight: "70vh",
  },
  fullHeight: {
    minHeight: "100vh",
  },
  fixedBottom: {
    position: "fixed",
    bottom: 0,
    width: "100%",
    [theme.breakpoints.up('sm')]: {
      width: `calc(100% - ${drawerWidth}px - 2*${theme.spacing(3)}px)`,
    },
  },
  tightTextField: {
    padding: "0.7em !important",
  },
  expand: {
    transform: 'rotate(0deg)',
    marginLeft: 'auto',
    transition: theme.transitions.create('transform', {
      duration: theme.transitions.duration.shortest,
    }),
  },
  expandOpen: {
    transform: 'rotate(180deg)',
  },
  cardDisabled: {
    backgroundColor: Colors.DISABLED,
  },
  drawer: {
    [theme.breakpoints.up('sm')]: {
      width: drawerWidth,
      flexShrink: 0,
    },
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
  },
  menuButton: {
    marginRight: theme.spacing(2),
    [theme.breakpoints.up('sm')]: {
      display: 'none',
    },
  },
  // necessary for content to be below app bar
  toolbar: theme.mixins.toolbar,
  drawerPaper: {
    width: drawerWidth,
  },
  // Admonitions
  admonitionCard: {
    margin: theme.spacing(3, 0),
    borderLeft: `${admonitionLeftBorder}px solid`
  },
  admonitionCardInfo: {
    borderLeft: `${admonitionLeftBorder}px solid ${Colors.INFO}`
  },
  admonitionCardDanger: {
    borderLeft: `${admonitionLeftBorder}px solid ${Colors.DANGER}`
  },
  admonitionCardExercise: {
    borderLeft: `${admonitionLeftBorder}px solid ${Colors.EXERCISE}`
  },
  admonitionCardSuccess: {
    borderLeft: `${admonitionLeftBorder}px solid ${Colors.SUCCESS}`
  },
  admonitionTitle: {
    padding: `${theme.spacing(1, 2)} !important`,
  },
  admonitionTitleInfo: {
    backgroundColor: Colors.INFO_BACKGROUND,
  },
  admonitionTitleDanger: {
    backgroundColor: Colors.DANGER_BACKGROUND,
  },
  admonitionTitleExercise: {
    backgroundColor: Colors.EXERCISE_BACKGROUND,
  },
  admonitionTitleSuccess: {
    backgroundColor: Colors.SUCCESS_BACKGROUND,
  },
  admonitionContent: {
    padding: `${theme.spacing(2, 2, 0)} !important`,
  },
  admonitionTitleTypography: {
    display: "flex !important",
    flexDirection: "row",
    alignItems: "center",
  },
  admonitionIcon: {
    marginRight: theme.spacing(1),
  },
  nestedListItem: {
    paddingLeft: theme.spacing(4),
    paddingRight: theme.spacing(2),
  },
  doubleNestedListItem: {
    paddingLeft: theme.spacing(8),
    paddingRight: theme.spacing(2),
  },
}

const useStyles = makeStyles(customClasses)


export { customClasses, useStyles, theme, Colors }
