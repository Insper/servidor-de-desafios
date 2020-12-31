import { createSlice, createAsyncThunk, createEntityAdapter } from '@reduxjs/toolkit'
import _ from "lodash"
import { getConceptList, getChallengeList, getTraceList } from '../../api/pygym'

export const fetchConcepts = createAsyncThunk('concepts/fetchConcepts', async () => {
  const concepts = await getConceptList()
  const promises = []
  concepts.forEach(concept => {
    promises.push(getChallengeList(concept.slug)
      .then(challenges => concept.codeChallenges = challenges))
    promises.push(getTraceList(concept.slug)
      .then(traces => concept.traceChallenges = traces))
  })
  await Promise.all(promises)
  return concepts
})

export const conceptsAdapter = createEntityAdapter({
  selectId: concept => concept.slug,
  sortComparer: (a, b) => a.order < b.order
})

const initialState = conceptsAdapter.getInitialState({ status: 'idle' })

const conceptsSlice = createSlice({
  name: 'concepts',
  initialState,
  extraReducers: builder => {
    builder
      .addCase(fetchConcepts.pending, (state, action) => {
        state.status = 'loading'
      })
      .addCase(fetchConcepts.fulfilled, (state, { payload }) => {
        conceptsAdapter.setAll(state, payload)
        state.status = 'idle'
      })
  }
})

export const { selectAll: selectConcepts, selectById: selectConceptBySlug } = conceptsAdapter.getSelectors(state => state.concepts)

export default conceptsSlice.reducer
