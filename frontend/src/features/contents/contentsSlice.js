import { createSlice, createAsyncThunk, createEntityAdapter, createSelector } from '@reduxjs/toolkit'
import _ from "lodash"
import { getContents, getPageList } from '../../api/pygym'

export const fetchContents = createAsyncThunk('contents/fetchContents', async () => {
  const [allContents, allPages] = await Promise.all([getContents(), getPageList()])
  const contentsBySlug = {}
  let contents = allContents.topics

  contents.forEach(content => {
    contentsBySlug[content.slug] = content
    content.pages = []
  })

  allPages.forEach(page => {
    const parts = _.split(page, '/')
    const content = contentsBySlug[parts[0]]
    if (content) {
      content.pages.push(page)
    }
  })

  return allContents
})

export const contentsAdapter = createEntityAdapter({
  selectId: content => content.slug,
})

const initialState = contentsAdapter.getInitialState({ status: 'idle', topics: [] })

const contentsSlice = createSlice({
  name: 'contents',
  initialState,
  extraReducers: builder => {
    builder
      .addCase(fetchContents.pending, (state, action) => {
        state.status = 'loading'
      })
      .addCase(fetchContents.fulfilled, (state, { payload }) => {
        if (payload.topics) {
          state.topics = payload.topics.map(topic => topic.slug)
        }
        contentsAdapter.setAll(state, payload.topics || [])
        state.status = 'idle'
      })
  }
})

export const { selectAll: selectContents, selectById: selectContentBySlug } = contentsAdapter.getSelectors(state => state.contents)
export const selectTopics = createSelector(state => state.contents, contents => {
  return contents.topics.map(slug => contents.entities[slug])
})

export default contentsSlice.reducer
