import {createSlice} from '@reduxjs/toolkit';

const initialState = {
    isLogin: false,
    name: 'Антонов Р.А.',
};

export const userSlice = createSlice({
    name: 'userSlice',
    initialState,
    reducers: {
        setLogin: (state, action) => {
            state.isLogin = action.payload;
        },
        setName: (state, action) => {
            state.name = action.payload;
        }
    }
});

export const {
    setLogin,
    setName
} = userSlice.actions;
export default userSlice.reducer;