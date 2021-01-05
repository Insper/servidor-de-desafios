import { generatePath } from "react-router";

class Route {
  constructor(path) {
    this.path = path
  }

  link(args) {
    return generatePath(this.path, args)
  }
}

const ROUTES = {
  home: new Route('/'),
  login: new Route('/login/'),
  logout: new Route('/logout/'),
  challenge: new Route('/challenge/:slug'),
  trace: new Route('/trace/:slug'),
  concept: new Route('/:slug'),
  page: new Route('/:slug/:page'),
}


export default ROUTES
