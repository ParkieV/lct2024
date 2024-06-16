import {configureStore} from '@reduxjs/toolkit'
import dataSlice from "./dataSlice";
import userSlice from "./userSlice";
import employeeSlice from "./employeeSlice";
import listFilterSlice from "./listFilterSlice";

const store = configureStore({
    reducer: {
        data: dataSlice,
        user: userSlice,
        employee: employeeSlice,
        filter: listFilterSlice,
    },
    middleware: (getDefaultMiddleware) => getDefaultMiddleware({
        serializableCheck: false,
    })
});

export default store;