import { configureStore } from '@reduxjs/toolkit'

import conceptsReducer from './features/concepts/conceptsSlice'

const store = configureStore({
  reducer: {
    concepts: conceptsReducer,
  }
})

export default store
