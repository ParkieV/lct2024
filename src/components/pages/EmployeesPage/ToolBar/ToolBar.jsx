import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import * as style from './ToolBar.module.css';
import Input from "../../../UI/Input/Input";
import EmployeeEdit from "../EmployeeEdit/EmployeeEdit";
import {setFindUserValues} from "../../../../store/listFilterSlice";

import search_icon from './img/search_icon.svg';
import options_icon from './img/options.svg';
import add_employee_icon from './img/add_employee.svg';
import save_employee_icon from '../../../assets/img/save_employee.svg';
import OptionsPanel from "./OptionsPanel/OptionsPanel";

const ToolBar = () => {
    const [isOpenSaveEmployeeBlock, setIsOpenSaveEmployeeBlock] = React.useState(false);
    const [isOpenOptionsBlock, setIsOpenOptionsBlock] = React.useState(false);
    const buttonFormSubmitRef = React.useRef(null);

    const filterStore = useSelector(state => state.filter);
    const dispatch = useDispatch();

    const findEmployee = (e, input) => {
        if (input.value.length === 0) {
            dispatch(setFindUserValues(null));
            return;
        }

        dispatch(setFindUserValues(input.value));
    }

    const openSaveEmployeeBlockOnClick = (e) => {
        setIsOpenOptionsBlock(false);
        setIsOpenSaveEmployeeBlock(!isOpenSaveEmployeeBlock);
    }

    const saveEmployeeOnClick = () => {
        buttonFormSubmitRef?.current?.click();
    }

    const saveEmployeeHandler = (form) => {
        const inputsData = Array
            .from(form.elements)
            .filter(elem => elem.tagName.toLowerCase() === 'input')
            .map(input => {
                return {
                    name: input.name, value: input.value
                }
            });
        form.reset();
        console.log(inputsData);
    }

    const showOptionsOnClick = (e) => {
        setIsOpenSaveEmployeeBlock(false);
        setIsOpenOptionsBlock(!isOpenOptionsBlock);
    }

    return (<>
        <div className={`${style.toolBar} ${isOpenOptionsBlock && style.toolBarExpand}`}>
            <Input placeholder="Найти пользователя..."
                   buttonIcon={search_icon}
                   inputStyle={{fontSize: '1em'}}
                   buttonIconOnClick={findEmployee}/>
            <div className={style.newUser}>
                <b>Пользователи</b>
                <button onClick={isOpenSaveEmployeeBlock ? saveEmployeeOnClick : openSaveEmployeeBlockOnClick}>
                    <img src={isOpenSaveEmployeeBlock ? save_employee_icon : add_employee_icon} alt=""/>
                </button>
                <button className={style.optionsButton} onClick={showOptionsOnClick}>
                    <img src={isOpenOptionsBlock ? save_employee_icon : options_icon} alt=""/>
                </button>
            </div>

            {isOpenOptionsBlock && <OptionsPanel/>}
        </div>
        {isOpenSaveEmployeeBlock && <EmployeeEdit submitFormHandler={saveEmployeeHandler}
                                                  isClosable={true}
                                                  closeHandler={openSaveEmployeeBlockOnClick}
                                                  buttonFormSubmitRef={buttonFormSubmitRef}
                                                  description="Добавление нового пользователя"/>}
    </>);
}

export default ToolBar;