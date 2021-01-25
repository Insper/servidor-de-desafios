import { createSlice, createEntityAdapter, createAsyncThunk } from '@reduxjs/toolkit'
import { getTraceInteractionList } from '../../api/pygym'

export const traceInteractionsAdapter = createEntityAdapter({
  selectId: interaction => interaction.challenge.slug,
  sortComparer: (a, b) => a.challenge.slug < b.challenge.slug
})

export const fetchTraceInteractions = createAsyncThunk('traceInteractions/fetchTraceInteractions', async () => {
  return await getTraceInteractionList()
})

export const traceInteractionsSlice = createSlice({
  name: 'traceInteractions',
  initialState: traceInteractionsAdapter.getInitialState({ status: 'idle' }),
  reducers: {},
  extraReducers: builder => {
    builder
      .addCase(fetchTraceInteractions.pending, (state, action) => {
        state.status = 'loading'
      })
      .addCase(fetchTraceInteractions.fulfilled, (state, action) => {
        traceInteractionsAdapter.upsertMany(state, action.payload)
        state.status = 'idle'
      })
  }
})

export const { selectAll: selectTraceInteractions, selectById: selectTraceInteractionBySlug } = traceInteractionsAdapter.getSelectors(state => state.traceInteractions)

export default traceInteractionsSlice.reducer
