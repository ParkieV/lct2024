import {createSlice} from '@reduxjs/toolkit';
import {login, logout} from "./thunk";

const initialState = {
    isLogin: false,
    user: {},
    // name: 'Антонов Р.А.',
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
        },
    },
    extraReducers: (builder) => {
        builder.addCase(login.fulfilled, (state, action) => {
            if (action?.payload?.status !== 200) {
                return;
            }
            state.user = action.payload.data;
            state.isLogin = true;

            localStorage.setItem('email', action.payload.data.email);
            localStorage.setItem('password', action.payload.data.password);
            delete action.payload.data['password'];
        })
        builder.addCase(logout.fulfilled,  (state, action)  =>  {
            state.isLogin = false;
            state.user = {};
            localStorage.clear();
        })
    },
});

export const {
    setLogin,
    setName
} = userSlice.actions;
export default userSlice.reducer;