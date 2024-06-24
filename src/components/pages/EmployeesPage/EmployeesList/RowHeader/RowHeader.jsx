import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import * as styleRow from '../Row/Row.module.css'
import * as style from './RowHeader.module.css'

import sortIcon from './img/sort.png';
import {setSorting} from "../../../../../store/listFilterSlice";

const SortButton = ({sort}) => {
    const filterStore = useSelector(state => state.filter);
    const dispatch = useDispatch();
    const sortHandler = (e) => {
        dispatch(setSorting(sort))
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
    const filterStore  = useSelector(state  => state.filter);

    return (
        <div className={`${styleRow.row} ${style.header}`}>
            <div className={style.headerField}>
                <p>{filterStore.sortingList[0].label}</p>
                <SortButton sort={filterStore.sortingList[0]}/>
            </div>
            <div className={style.headerField}>
                <p>{filterStore.sortingList[1].label}</p>
                <SortButton sort={filterStore.sortingList[1]}/>
            </div>
            <div className={style.headerField}>
                <p className={styleRow.position}>{filterStore.sortingList[2].label}</p>
                <SortButton sort={filterStore.sortingList[2]}/>
            </div>
            <div className={`${style.headerField} ${style.organizationField}`}>
                <p className={styleRow.organization}>{filterStore.sortingList[3].label}</p>
                <SortButton sort={filterStore.sortingList[3]}/>
            </div>
            <div className={`${style.headerField} ${style.typeField}`}>
                <p className={styleRow.type}>{filterStore.sortingList[4].label}</p>
                <SortButton sort={filterStore.sortingList[4]}/>
            </div>
            <div className={styleRow.actions}>
            </div>
        </div>
    );
}

export default RowHeader;