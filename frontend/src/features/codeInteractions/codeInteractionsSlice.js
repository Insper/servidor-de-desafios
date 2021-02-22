import { createSlice, createEntityAdapter, createAsyncThunk } from '@reduxjs/toolkit'
import { getCodeInteractionList } from '../../api/pygym'

export const codeInteractionsAdapter = createEntityAdapter({
  selectId: interaction => interaction.challenge.slug,
  sortComparer: (a, b) => a.challenge.slug < b.challenge.slug
})

export const fetchCodeInteractions = createAsyncThunk('codeInteractions/fetchCodeInteractions', async () => {
  return await getCodeInteractionList()
})

export const codeInteractionsSlice = createSlice({
  name: 'codeInteractions',
  initialState: codeInteractionsAdapter.getInitialState({ status: 'idle' }),
  reducers: {},
  extraReducers: builder => {
    builder
      .addCase(fetchCodeInteractions.pending, (state, action) => {
        state.status = 'loading'
      })
      .addCase(fetchCodeInteractions.fulfilled, (state, action) => {
        codeInteractionsAdapter.upsertMany(state, action.payload)
        state.status = 'idle'
      })
  }
})

export const { selectAll: selectCodeInteractions, selectById: selectCodeInteractionBySlug } = codeInteractionsAdapter.getSelectors(state => state.codeInteractions)

export default codeInteractionsSlice.reducer
