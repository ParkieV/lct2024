import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import * as style from './Row.module.css'
import editSvg from './img/edit.svg';
import saveSvg from '../../../../assets/img/save_employee.svg';
import deleteSvg from './img/delete.svg';
import EmployeeEdit from "../../EmployeeEdit/EmployeeEdit";
import {deleteEmployee} from "../../../../../store/employeeSlice";
import { patchUser } from "../../../../../store/thunk";

const ToolsButton = ({ onClickEdit, onClickDelete, isEdit }) => {
    return (
        <>
            <button onClick={onClickEdit}>
                <img src={isEdit ? saveSvg : editSvg} alt="" />
            </button>
            <button onClick={onClickDelete}>
                <img src={deleteSvg} alt="" />
            </button>
        </>
    );
};

const Row = ({ index, employee }) => {
    const [isEdit, setIsEdit] = React.useState(false);

    const organizations = useSelector((state) => state.employee.organizations);
    const types = useSelector((state) => state.employee.types);
    const dispatch = useDispatch();
    const buttonFormSubmitRef = React.useRef(null);
    const employeeStore = useSelector((state) => state.employee);

    const onClickEdit = (e) => {
        setIsEdit(!isEdit);
    };

    const editEmployeeHandler = (form) => {
        console.log("Form", form);
        const inputsData = Array.from(form.elements)
            .filter((elem) => elem.tagName.toLowerCase() === "input" && elem.type !== "checkbox")
            .map((input) => {
                return {
                    name: input.name,
                    value: input.value,
                };
            });
        const rightsData = Array.from(form.elements)
            .filter((elem) => elem.tagName.toLowerCase() === "input" && elem.type === "checkbox")
            .map((input) => {
                return {
                    name: input.name,
                    value: input.checked,
                };
            });
        const rightsStr = rightsData
            .filter((elem) => elem.value === true)
            .map((elem) => {
                return elem.name;
            })
            .join(";");

        let user = {};
        for (const input of inputsData) {
            if (input.name === "work_org_id") {
                user[input.name] = employeeStore.organizations.find((elem) => elem.label === input.value).value;
                continue;
            }
            user[input.name] = input.value;
        }
        user.rights = rightsStr;
        user.id = employee.id;
        form.reset();

        dispatch(patchUser({ user: user }));
    };

    const editEmployeeOnClick = () => {
        buttonFormSubmitRef?.current?.click();
    };

    const onClickDelete = (e) => {
        dispatch(deleteEmployee(employee));
    };

    return (
        <>
            <div className={style.row}>
                <div className={style.header_mobile}>
                    <div className={style.with_header}>
                        <p className={style.mobile_header_text}>ID</p>
                        <b className={style.id}>{employee.index}</b>
                    </div>

                    <div className={`${style.actions} ${style.actions_mobile}`}>
                        <ToolsButton onClickEdit={isEdit ? editEmployeeOnClick : onClickEdit} onClickDelete={onClickDelete} isEdit={isEdit} />
                    </div>
                </div>
                <div className={style.with_header}>
                    <p className={style.mobile_header_text}>ФИО</p>
                    <b>
                        {employee.last_name} {employee.first_name[0]}.{employee.middle_name[0]}
                    </b>
                </div>
                <div className={style.with_header}>
                    <p className={style.mobile_header_text}>Должность</p>
                    <p className={style.position}>{employee.position}</p>
                </div>
                <div className={style.with_header}>
                    <p className={style.mobile_header_text}>ID</p>
                    <p className={style.organization}>{organizations?.find((e) => e.value === employee.work_org_id)?.label}</p>
                </div>
                <div className={style.with_header}>
                    <p className={style.mobile_header_text}>ID</p>
                    <p className={style.type}>{types[employee.type]}</p>
                </div>

                <div className={style.actions}>
                    <ToolsButton onClickEdit={isEdit ? editEmployeeOnClick : onClickEdit} onClickDelete={onClickDelete} isEdit={isEdit} />
                </div>
            </div>
            {isEdit && (
                <EmployeeEdit submitFormHandler={editEmployeeHandler} employee={employee} buttonFormSubmitRef={buttonFormSubmitRef} description="Редактирование пользователя" />
            )}
        </>
    );
};

export default Row;
