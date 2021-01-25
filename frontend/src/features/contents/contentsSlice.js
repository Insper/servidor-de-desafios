import { createSlice, createAsyncThunk, createEntityAdapter, createSelector } from '@reduxjs/toolkit'
import _ from "lodash"
import { getContents, getPageList } from '../../api/pygym'

export const fetchContents = createAsyncThunk('contents/fetchContents', async () => {
  const [allContents, allPages] = await Promise.all([getContents(), getPageList()])
  const contentsBySlug = {}
  let contents = _.flatten(_.values(allContents))

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

const initialState = contentsAdapter.getInitialState({ status: 'idle', contentListNames: [] })

const contentsSlice = createSlice({
  name: 'contents',
  initialState,
  extraReducers: builder => {
    builder
      .addCase(fetchContents.pending, (state, action) => {
        state.status = 'loading'
      })
      .addCase(fetchContents.fulfilled, (state, { payload }) => {
        _.entries(payload).forEach(([contentListName, contents]) => {
          state[contentListName] = contents.map(content => content.slug)
        })
        contentsAdapter.setAll(state, _.flatten(_.values(payload)) || [])
        state.status = 'idle'
        state.contentListNames = _.keys(payload)
      })
  }
})

export const { selectAll: selectContents, selectById: selectContentBySlug } = contentsAdapter.getSelectors(state => state.contents)
export const selectContentListNames = createSelector(state => state.contents, contents => {
  return contents.contentListNames
})
export const selectContentLists = createSelector(state => state.contents, contents => {
  return _.fromPairs(contents.contentListNames.map(contentListName => [contentListName, contents[contentListName].map(slug => contents.entities[slug])]))
})

export default contentsSlice.reducer
