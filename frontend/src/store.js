import { configureStore } from '@reduxjs/toolkit'

import codeChallengesReducer from './features/codeChallenges/codeChallengesSlice'
import conceptsReducer from './features/concepts/conceptsSlice'
import contentsReducer from './features/contents/contentsSlice'
import traceChallengesReducer from './features/traceChallenges/traceChallengesSlice'

const store = configureStore({
  reducer: {
    codeChallenges: codeChallengesReducer,
    concepts: conceptsReducer,
    contents: contentsReducer,
    traceChallenges: traceChallengesReducer,
  }
})

export default store
