import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import * as style from '../Input/Input.module.css'
import dropdownIcon from './img/dropdown.svg'

/**
 *
 * @param placeholder
 * @param label
 * @param required
 * @param name
 * @param selectStyle
 * @param onChange
 * @param {Array.<{value: string, label: string}>} options
 * @param small
 * @param {JSX.Element} block
 * @constructor
 */
const Select = ({
                    placeholder = "",
                    label = "",
                    required = false,
                    name = "",
                    selectStyle = {},
                    onChange = (e) => {
                    },
                    options = [],
                    defaultValue = "",
                    block = null,
                    invalid = false,
                }) => {
    const [isDropdownOpen, setIsDropdownOpen] = React.useState(false);
    const [optionLabel, setOptionLabel] = React.useState("");
    const [optionValue, setOptionValue] = React.useState(defaultValue);

    const selectRef = React.useRef(null);
    const data = useSelector(state => state.data);
    const dispatch = useDispatch();

    const isShowDropDown = isDropdownOpen && (block !== null || options.length > 0);

    const showDropdown = (e) => {
        setIsDropdownOpen(!isDropdownOpen);
    }

    /**
     *
     * @param e
     * @param {{value: string, label: string}} option
     */
    const choseDropdownOptions = (e, option) => {
        e.preventDefault();
        setOptionLabel(option.label);
        setOptionValue(option.value);
        console.log(option)
    }

    return (
        <div className={style.inputContainer}>
            {label &&
                <label>{label}
                    {required && <span className={style.required}>*</span>}
                </label>
            }
            <div>
                <div className={`${style.inputBlock} ${style.selectBlock} ${isDropdownOpen && style.selectBlockOpen}`}
                     onClick={() => {
                         block === null && showDropdown();
                     }}>
                    <input className={`${invalid && style.invalid}`}
                           ref={selectRef}
                           placeholder={placeholder}
                           required={required && (block !== null || options.length > 0) || false}
                           value={optionLabel}
                           name={name}
                           style={selectStyle}
                           data-options-value={optionValue}
                           autoComplete={'off'}
                           onChange={(e) => {
                               setOptionLabel(e.target.value);
                               onChange(e);
                           }}/>
                    <button className={style.dropdownButton} type={'button'} onClick={e => {
                        block !== null && showDropdown()
                    }}>
                        <img className={`${isShowDropDown && style.dropdownIconUp}`} src={dropdownIcon} alt=""/>
                    </button>
                    {
                        isShowDropDown &&
                        <div className={style.dropdown}>
                            {
                                block === null && options.length > 0 &&
                                options.map((option, index) => {
                                    return <button key={index}
                                                   onClick={(e) => choseDropdownOptions(e, option)}
                                    >{option.label}</button>
                                })
                                ||
                                block
                            }
                        </div>
                    }
                </div>
                <p className={style.requiredFiledMessage}>Заполните обязательное поле</p>
            </div>
        </div>
    );
}

export default Select;