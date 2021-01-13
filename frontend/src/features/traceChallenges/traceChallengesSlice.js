import { createSlice, createEntityAdapter } from '@reduxjs/toolkit'
import { fetchConcepts } from '../concepts/conceptsSlice'

export const traceChallengesAdapter = createEntityAdapter({
  selectId: challenge => challenge.slug,
  sortComparer: (a, b) => a.slug < b.slug
})

export const traceChallengesSlice = createSlice({
  name: 'traceChallenges',
  initialState: traceChallengesAdapter.getInitialState(),
  reducers: {},
  extraReducers: builder => {
    builder.addCase(fetchConcepts.fulfilled, (state, action) => {
      traceChallengesAdapter.upsertMany(state, action.payload.traceChallenges)
    })
  }
})

export const { selectAll: selectTraceChallenges, selectById: selectTraceChallengeBySlug } = traceChallengesAdapter.getSelectors(state => state.traceChallenges)
export const selectTraceChallengesBySlug = (state, slugs) => slugs.map(slug => selectTraceChallengeBySlug(state, slug))

export default traceChallengesSlice.reducer
