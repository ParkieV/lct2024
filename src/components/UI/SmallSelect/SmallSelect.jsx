import React from 'react';
import * as style from './SmallSelect.module.css'
import * as styleSelect from '../Input/Input.module.css'
import dropdownIcon from '../Select/img/dropdown.svg'

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
const SmallSelect = ({
                         placeholder = "",
                         name = "",
                         onChange = (e, option) => {
                         },
                         options = [],
                         currentOption = {value: "", label: ""}
                     }) => {
    const [isDropdownOpen, setIsDropdownOpen] = React.useState(false);
    const isShowDropDown = isDropdownOpen && options.length > 0;

    const showDropdown = (e) => {
        setIsDropdownOpen(!isDropdownOpen);
    }

    /**
     * @param e
     * @param {{value: string, label: string}} option
     */
    const choseDropdownOptions = (e, option) => {
        console.log(option)
        onChange(e, option);
    }

    return (
        <div className={`${style.selectBlock} ${isDropdownOpen && style.selectBlockOpen}`} onClick={() => {
            showDropdown()
        }}>
            <div data-options-value={currentOption.value}>
                {placeholder + currentOption.label}
            </div>
            <button className={styleSelect.dropdownButton} type={'button'}>
                <img className={`${isShowDropDown && styleSelect.dropdownIconUp}`} src={dropdownIcon} alt=""/>
            </button>
            {
                isShowDropDown &&
                <div className={styleSelect.dropdown}>
                    {
                        options?.map((option, index) => {
                            return <button key={index}
                                           onClick={(e) => choseDropdownOptions(e, option)}
                            >{option.label}</button>
                        })
                    }
                </div>
            }
        </div>
    );
}

export default SmallSelect;