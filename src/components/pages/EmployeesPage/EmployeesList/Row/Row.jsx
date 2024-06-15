import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import * as style from './Row.module.css'
import editSvg from './img/edit.svg';
import saveSvg from '../../../../assets/img/save_employee.svg';
import deleteSvg from './img/delete.svg';
import EmployeeEdit from "../../EmployeeEdit/EmployeeEdit";
import {deleteEmployee} from "../../../../../store/employeeSlice";

const Row = ({
                 index,
                 employee
             }) => {
    const [isEdit, setIsEdit] = React.useState(false);

    const organizations = useSelector(state => state.employee.organizations);
    const types = useSelector(state => state.employee.types);
    const dispatch = useDispatch();

    const onClickEdit = (e) => {
        setIsEdit(!isEdit);
    }

    const onClickDelete = (e) => {
        dispatch(deleteEmployee(employee));
    }

    return (
        <>
            <div className={style.row}>
                <b>{employee.index}</b>
                <b>{employee.last_name} {employee.first_name[0]}.{employee.middle_name[0]}</b>
                <p className={style.position}>{employee.position}</p>
                <p className={style.organization}>{organizations[employee.work_org_id].label}</p>
                <p className={style.type}>{types[employee.type]}</p>
                <div className={style.actions}>
                    <button onClick={onClickEdit}>
                        <img src={isEdit ? saveSvg : editSvg} alt=""/>
                    </button>
                    <button onClick={onClickDelete}>
                        <img src={deleteSvg} alt=""/>
                    </button>
                </div>
            </div>
            {
                isEdit && <EmployeeEdit employee={employee}
                                        description="Редактирование пользователя"/>
            }
        </>

    );
}

export default Row;