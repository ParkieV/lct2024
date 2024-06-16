import {createSlice} from '@reduxjs/toolkit';

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
        work_org_id: '1',
        position: 'Программист',
        rights: ['admin'],
        type: 'admin'
    }],
    types: {
        'admin': 'Администратор',
        'user': 'Пользователь',
    },
    organizations: {
        '1': {
            value: '1',
            label: 'ТОО Асмас'
        }
    }
};

for (let i = 2; i < 130; i++) {
    initialState.list.push({
        index: i,
        id: i,
        last_name: 'Исупов' + i,
        first_name: 'Григорий',
        middle_name: 'Сергеевич',
        email: 'domster704@mail.com',
        phone: '89127458900',
        work_org_id: '1',
        position: 'Программист' + i,
        rights: ['user'],
        type: 'user'
    })
}

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
    }
});

export const {
    setIsSavedEmployee,
    deleteEmployee
} = employeeSlice.actions;
export default employeeSlice.reducer;