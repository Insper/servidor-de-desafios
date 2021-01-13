import { createSlice, createAsyncThunk, createEntityAdapter } from '@reduxjs/toolkit'
import { normalize, schema } from 'normalizr'
import _ from "lodash"
import { getConceptList, getChallengeList, getTraceList } from '../../api/pygym'

// Normalizr entity schemas
export const codeChallengeEntity = new schema.Entity('codeChallenges', {}, { idAttribute: 'slug' })
export const traceChallengeEntity = new schema.Entity('traceChallenges', {}, { idAttribute: 'slug' })
export const conceptEntity = new schema.Entity(
  'concepts',
  {
    codeChallenges: [codeChallengeEntity],
    traceChallenges: [traceChallengeEntity],
  },
  { idAttribute: 'slug' }
)

export const conceptsAdapter = createEntityAdapter({
  selectId: concept => concept.slug,
  sortComparer: (a, b) => a.order < b.order
})

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

  const normalized = normalize(concepts, [conceptEntity])
  return normalized.entities
})

const conceptsSlice = createSlice({
  name: 'concepts',
  initialState: conceptsAdapter.getInitialState({ status: 'idle' }),
  extraReducers: builder => {
    builder
      .addCase(fetchConcepts.pending, (state, action) => {
        state.status = 'loading'
      })
      .addCase(fetchConcepts.fulfilled, (state, action) => {
        conceptsAdapter.upsertMany(state, action.payload.concepts)
        state.status = 'idle'
      })
  }
})

export const { selectAll: selectConcepts, selectById: selectConceptBySlug } = conceptsAdapter.getSelectors(state => state.concepts)

export default conceptsSlice.reducer
