import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import * as style from './OptionsPanel.module.css'
import {setElementsOnPage, setEmployeesType, setSortingWithDirection} from "../../../../../store/listFilterSlice";
import Select from "../../../../UI/Select/Select";

class SortingOptions {
    constructor(sortOption, direction) {
        this.sortOption = sortOption;
        if (sortOption.value === 'id') {
            this.text = "Сначала " + (direction ?  "старые"  :  "новые");
        } else  {
            this.text = sortOption.label + " " + (direction ? "А-Я" : "Я-А");
        }
        this.direction = direction;
    }

    getObject() {
        return {
            value: this.sortOption.value,
            label: this.text,
            direction: this.direction,
        }
    }
}


const OptionsPanel = (props) => {
    const filterStore = useSelector(state => state.filter);
    const dispatch = useDispatch();

    const [sortOptions, setSortOptions] = React.useState([
        new SortingOptions(filterStore.sortingList[0], false).getObject(),
        new SortingOptions(filterStore.sortingList[0], true).getObject(),

        new SortingOptions(filterStore.sortingList[1], true).getObject(),
        new SortingOptions(filterStore.sortingList[1], false).getObject(),

        new SortingOptions(filterStore.sortingList[2], true).getObject(),
        new SortingOptions(filterStore.sortingList[2], false).getObject(),

        new SortingOptions(filterStore.sortingList[3], true).getObject(),
        new SortingOptions(filterStore.sortingList[3], false).getObject(),

        new SortingOptions(filterStore.sortingList[4], true).getObject(),
        new SortingOptions(filterStore.sortingList[4], false).getObject(),
    ])

    const chooseElementsOnPage = (e, value) => {
        dispatch(setElementsOnPage(value));
    }

    const chooseEmployeesType = (e, value) => {
        dispatch(setEmployeesType(value));
    }

    const chooseSorting = (e, option) => {
        dispatch(setSortingWithDirection({
            sort: option,
            direction: option.direction
        }));
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
            <div className={style.sortBlock}>
                <b>Сортировка</b>
                <Select options={sortOptions}
                        placeholder="Сортировка"
                        onChange={chooseSorting}/>
            </div>
        </div>
    );
}

export default OptionsPanel;