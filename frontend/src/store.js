import { configureStore } from '@reduxjs/toolkit'

import codeChallengesReducer from './features/codeChallenges/codeChallengesSlice'
import codeInteractionsReducer from './features/codeInteractions/codeInteractionsSlice'
import conceptsReducer from './features/concepts/conceptsSlice'
import contentsReducer from './features/contents/contentsSlice'
import traceChallengesReducer from './features/traceChallenges/traceChallengesSlice'
import traceInteractionsReducer from './features/traceInteractions/traceInteractionsSlice'

const store = configureStore({
  reducer: {
    codeChallenges: codeChallengesReducer,
    codeInteractions: codeInteractionsReducer,
    concepts: conceptsReducer,
    contents: contentsReducer,
    traceChallenges: traceChallengesReducer,
    traceInteractions: traceInteractionsReducer,
  }
})

export default store
