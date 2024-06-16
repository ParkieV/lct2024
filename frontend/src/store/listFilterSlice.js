import {createSlice} from '@reduxjs/toolkit';

const LIST_OPTIONS_EMPLOYEE_TYPES = [{
    value: 'all',
    label: 'Все'
}, {
    value: 'admin',
    label: 'Администраторы'
}, {
    value: 'user',
    label: 'Пользователи'
}];

const LIST_OPTIONS_PAGE_ELEMENTS = [{
    value: 10,
    label: 10
}, {
    value: 15,
    label: 15
}, {
    value: 20,
    label: 20
}, {
    value: 25,
    label: 25
}, {
    value: 50,
    label: 50,
}];

const LIST_OPTIONS_SORTING = [{
    value: 'id',
    label: 'ID'
}, {
    value: 'full_name',
    label: 'ФИО'
}, {
    value: 'position',
    label: 'Должность'
}, {
    value: 'organization',
    label: 'Организация'
}, {
    value: 'type',
    label: 'Роль'
}]

const initialState = {
    employeesTypeList: LIST_OPTIONS_EMPLOYEE_TYPES,
    elementsOnPageList: LIST_OPTIONS_PAGE_ELEMENTS,
    sortingList: LIST_OPTIONS_SORTING,

    employeesType: LIST_OPTIONS_EMPLOYEE_TYPES[0],
    elementsOnPage: LIST_OPTIONS_PAGE_ELEMENTS[0],
    baseMaxPageNumberInPagination: 4,
    currentPage: 1,

    sorting: LIST_OPTIONS_SORTING[0],
    sortingDirection: true,
    findUserValues: null,
};

export const listFilterSlice = createSlice({
    name: 'listFilterSlice',
    initialState,
    reducers: {
        setCurrentPage: (state, action) => {
            state.currentPage = action.payload;
        },
        setElementsOnPage: (state, action) => {
            state.elementsOnPage = action.payload;
        },
        setEmployeesType: (state, action) => {
            state.employeesType = action.payload;
        },
        setSorting: (state, action) => {
            if (state.sorting.value !== action.payload.value) {
                state.sortingDirection = true;
            } else {
                state.sortingDirection = !state.sortingDirection;
            }

            state.sorting = state.sortingList.find(sort => sort.value === action.payload.value);
        },
        setSortingWithDirection: (state, action) => {
            console.log(action.payload.sort, action.payload.direction);
            state.sorting = state.sortingList.find(sort => sort.value === action.payload.sort.value);
            state.sortingDirection = action.payload.direction;
        },
        setFindUserValues: (state, action) => {
            state.findUserValues = action.payload;
        }
    }
});

export const {
    setCurrentPage,
    setElementsOnPage,
    setEmployeesType,
    setSorting,
    setFindUserValues,
    setSortingWithDirection
} = listFilterSlice.actions;
export default listFilterSlice.reducer;