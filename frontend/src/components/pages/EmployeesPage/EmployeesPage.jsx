import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import * as style from './EmployeesPage.module.css'
import ToolBar from "./ToolBar/ToolBar";
import EmployeesList from "./EmployeesList/EmployeesList";
import ListOptions from "./EmployeesList/ListOptions/ListOptions";
import {getOrganizations} from "../../../store/thunk";

const EmployeesPage = (props) => {
    const data = useSelector(state => state.data);
    const dispatch = useDispatch();

    React.useEffect(() => {
        dispatch(getOrganizations())
    }, [])

    return (
        <div className={style.employeesContainer}>
            <ToolBar/>
            <ListOptions/>
            <EmployeesList/>
        </div>
    );
}

export default EmployeesPage;