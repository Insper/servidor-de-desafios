import { createSlice, createEntityAdapter } from '@reduxjs/toolkit'
import { fetchConcepts } from '../concepts/conceptsSlice'

export const codeChallengesAdapter = createEntityAdapter({
  selectId: challenge => challenge.slug,
  sortComparer: (a, b) => a.slug < b.slug
})

export const codeChallengesSlice = createSlice({
  name: 'codeChallenges',
  initialState: codeChallengesAdapter.getInitialState(),
  reducers: {},
  extraReducers: builder => {
    builder.addCase(fetchConcepts.fulfilled, (state, action) => {
      codeChallengesAdapter.upsertMany(state, action.payload.codeChallenges)
    })
  }
})

export const { selectAll: selectCodeChallenges, selectById: selectCodeChallengeBySlug } = codeChallengesAdapter.getSelectors(state => state.codeChallenges)
export const selectCodeChallengesBySlug = (state, slugs) => slugs.map(slug => selectCodeChallengeBySlug(state, slug))

export default codeChallengesSlice.reducer
