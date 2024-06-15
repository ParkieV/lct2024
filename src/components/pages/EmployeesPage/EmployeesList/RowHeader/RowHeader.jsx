import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import * as styleRow from '../Row/Row.module.css'
import * as style from './RowHeader.module.css'

import sortIcon from './img/sort.png';
import {setSorting} from "../../../../../store/listFilterSlice";

const SortButton = ({sort_name}) => {
    const filterStore = useSelector(state => state.filter);
    const dispatch = useDispatch();
    const sortHandler = (e) => {
        dispatch(setSorting(sort_name))
    }

    return (
        <button className={style.sortButton}
                title="Cортировка по алфавиту"
                onClick={sortHandler}>
            <img src={sortIcon} alt=""/>
        </button>

    )
}

const RowHeader = (props) => {
    return (
        <div className={`${styleRow.row} ${style.header}`}>
            <div className={style.headerField}>
                <p>ID</p>
                <SortButton sort_name="id"/>
            </div>
            <div className={style.headerField}>
                <p>ФИО</p>
                <SortButton sort_name="full_name"/>
            </div>
            <div className={style.headerField}>
                <p className={styleRow.position}>Должность</p>
                <SortButton sort_name="position"/>
            </div>
            <div className={style.headerField}>
                <p className={styleRow.organization}>Организация</p>
                <SortButton sort_name="organization"/>
            </div>
            <div className={style.headerField}>
                <p className={styleRow.type}>Роль</p>
                <SortButton sort_name="type"/>
            </div>
            <div className={styleRow.actions}>
            </div>
        </div>
    );
}

export default RowHeader;