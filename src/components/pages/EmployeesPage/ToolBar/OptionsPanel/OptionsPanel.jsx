import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import * as style from './OptionsPanel.module.css'
import {setElementsOnPage, setEmployeesType} from "../../../../../store/listFilterSlice";

const OptionsPanel = (props) => {
    const filterStore = useSelector(state => state.filter);
    const dispatch = useDispatch();

    const chooseElementsOnPage = (e, value) => {
        dispatch(setElementsOnPage(value));
    }

    const chooseEmployeesType = (e, value) => {
        console.log(value)
        dispatch(setEmployeesType(value));
    }

    return (
        <div className={style.optionsContainer}>
            <div className={style.pageElementsBlock}>
                <b>Показывать на странице</b>
                <div className={style.pageElementsButtons}>
                    {
                        filterStore.elementsOnPageList.map((value, index) => {
                            return <button
                                className={`${filterStore.elementsOnPage.value === value.value ? style.active : ''}`}
                                key={index}
                                onClick={e => chooseElementsOnPage(e, value)}>{value.label}</button>
                        })
                    }
                </div>
            </div>
            <div className={style.typeEmployeesBlock}>
                <b>Кого отобразить</b>
                <div className={style.typeEmployeesButtons}>
                    {
                        filterStore.employeesTypeList.map((value, index) => {
                            return <button
                                className={`${filterStore.employeesType.value === value.value ? style.active : ''}`}
                                key={index}
                                onClick={e => chooseEmployeesType(e, value)}>{value.label}</button>
                        })
                    }
                </div>
            </div>
        </div>
    );
}

export default OptionsPanel;