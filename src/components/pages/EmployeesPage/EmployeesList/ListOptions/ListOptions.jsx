import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import * as style from './ListOptions.module.css'
import SmallSelect from "../../../../UI/SmallSelect/SmallSelect";
import {setElementsOnPage, setEmployeesType} from "../../../../../store/listFilterSlice";

const ListOptions = (props) => {
    const employeeStore = useSelector(state => state.employee);
    const filterStore = useSelector(state => state.filter);
    const dispatch = useDispatch();

    const setElementsOnPageHandler = (e, option) => {
        dispatch(setElementsOnPage(option));
    }

    const setEmployeesTypeHandler = (e, option) => {
        dispatch(setEmployeesType(option));
    }

    return (
        <div className={style.optionsBlock}>
            <b>Всего пользователей: {employeeStore.list.length}</b>
            <div className={style.optionsSelectBlock}>
                <SmallSelect placeholder="Показать: "
                             options={filterStore.employeesTypeList}
                             currentOption={filterStore.employeesType}
                             onChange={setEmployeesTypeHandler}/>
                <SmallSelect options={filterStore.elementsOnPageList}
                             currentOption={filterStore.elementsOnPage}
                             onChange={setElementsOnPageHandler}/>
            </div>
        </div>
    );
}

export default ListOptions;