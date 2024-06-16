import {createSlice} from '@reduxjs/toolkit';

const initialState = {
    text: "hello world"
};

export const dataSlice = createSlice({
    name: 'data',
    initialState,
    reducers: {
        setText: (state, action) => {
            state.text = action.payload
        }
    }
});

export const {setText} = dataSlice.actions;
export default dataSlice.reducer;