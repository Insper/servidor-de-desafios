import { configureStore } from '@reduxjs/toolkit'

import conceptsReducer from './features/concepts/conceptsSlice'
import contentsReducer from './features/contents/contentsSlice'

const store = configureStore({
  reducer: {
    contents: contentsReducer,
    concepts: conceptsReducer,
  }
})

export default store
