import {createSlice} from '@reduxjs/toolkit';
import {getOrganizations} from "./thunk";

const initialState = {
    list: [{
        index: 1,
        id: 1,
        last_name: 'Исупов',
        first_name: 'Григорий',
        middle_name: 'Сергеевич',
        telegram_nickname: "@domster704",
        email: 'domster704@mail.com',
        phone: '89127458900',
        password: 'test123',
        work_org_id: 'b0134c79-bd95-4128-9474-9d42e4c06c48',
        position: 'Программист',
        rights: ['admin'],
        type: 'admin'
    }],
    types: {
        'admin': 'Администратор',
        'user': 'Пользователь',
    },
    organizations: [{
        value: 'b0134c79-bd95-4128-9474-9d42e4c06c48',
        label: 'Тест'
    }]
};

// for (let i = 2; i < 130; i++) {
//     initialState.list.push({
//         index: i,
//         id: i,
//         last_name: 'Исупов' + i,
//         first_name: 'Григорий',
//         middle_name: 'Сергеевич',
//         email: 'domster704@mail.com',
//         phone: '89127458900',
//         password: 'test123',
//         work_org_id: '100000000',
//         position: 'Программист' + i,
//         rights: ['user'],
//         type: 'user'
//     })
// }

export const employeeSlice = createSlice({
    name: 'employeeSlice',
    initialState,
    reducers: {
        setIsSavedEmployee: (state, action) => {
            state.isSavedEmployee = action.payload
        },
        deleteEmployee: (state, action) => {
            state.list = state.list.filter(item => item.id !== action.payload.id);
        }
    },
    extraReducers: (builder) => {
        builder.addCase(getOrganizations.fulfilled, (state, action) => {
            if (!action?.payload?.data?.orgList) {
                return false;
            }
            state.organizations = action.payload.data.orgList;
            // [...action.payload.data.orgList].forEach(item => {
            //     console.log(item)
            //     state.organizations[item.value] = item;
            // });
        })
    }
})

export const {
    setIsSavedEmployee,
    deleteEmployee
} = employeeSlice.actions;
export default employeeSlice.reducer;