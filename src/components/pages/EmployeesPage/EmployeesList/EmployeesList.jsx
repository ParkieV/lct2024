import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import * as style from './EmployeesList.module.css'
import RowHeader from "./RowHeader/RowHeader";
import Row from "./Row/Row";
import ExcelButton from "../ExcelButton/ExcelButton";
import EmployeePagination from "./EmployeePagination/EmployeePagination";


/**
 * Тут происходит фильтрация списка сотрудников
 */
const filter = (filterStore, employeeStore, employees) => {
    if (filterStore.employeesType.value === 'all') {
        return employees;
    }

    return employees.filter(elem => {
        return elem.type === filterStore.employeesTypeList
            .find(type => type.value === filterStore.employeesType.value).value;
    });
}


/**
 * Тут происходит сортировка списка сотрудников
 */
const sort = (filterStore, organizations, employees) => {
    const coefficient = filterStore.sortingDirection ? 1 : -1;
    const localEmployees = [...employees];

    localEmployees.sort((employee1, employee2) => {
        switch (filterStore.sorting) {
            case 'id':
            case 'type':
            case 'position': {
                if (employee1[filterStore.sorting] > employee2[filterStore.sorting]) return 1 * coefficient;
                if (employee1[filterStore.sorting] < employee2[filterStore.sorting]) return -1 * coefficient;
                return 0;
            }
            case 'full_name': {
                const full_name1 = `${employee1.first_name} ${employee1.last_name} ${employee1.middle_name}`;
                const full_name2 = `${employee2.first_name} ${employee2.last_name} ${employee2.middle_name}`;
                if (full_name1 > full_name2) return 1 * coefficient;
                if (full_name1 < full_name2) return -1 * coefficient;
                return 0;
            }
            case 'organization': {
                const organization1 = organizations[employee1.work_org_id];
                const organization2 = organizations[employee2.work_org_id];
                if (organization1.name > organization2.name) return 1 * coefficient;
                if (organization1.name < organization2.name) return -1 * coefficient;
                return 0;
            }
            default:
                return 0;
        }
    });

    return localEmployees;
}


/**
 * Тут происходит поиск сотрудника по id
 */
const findEmployee = (filterStore, employeeStore, employees) => {
    if (filterStore.findUserValues === null) {
        return employees;
    }

    return employees.filter(elem => {
        return elem.id.toString() === filterStore.findUserValues;
    });
}


/**
 * Отображение списка сотрудников по страницам на основной текущей страницы
 */
const paginate = (filterStore, employees) => {
    return employees.slice(
        (filterStore.currentPage - 1) * filterStore.elementsOnPage.label,
        filterStore.currentPage * filterStore.elementsOnPage.label
    );
}

const EmployeesList = () => {
    const employeeStore = useSelector(state => state.employee);
    const filterStore = useSelector(state => state.filter);
    const organizations = useSelector(state => state.employee.organizations);

    const [employees, setEmployees] = React.useState(employeeStore.list);
    const [visibleList, setVisibleList] = React.useState(paginate(filterStore, employees));

    const dispatch = useDispatch();

    React.useEffect(() => {
        setEmployees(findEmployee(filterStore, employeeStore, employees));
    }, [filterStore.findUserValues])

    React.useEffect(() => {
        setEmployees(filter(filterStore, employeeStore, employees));
    }, [filterStore.employeesType]);

    React.useEffect(() => {
        setEmployees(sort(filterStore, organizations, employees));
    }, [filterStore.sorting, filterStore.sortingDirection]);

    React.useEffect(() => {
        setVisibleList(paginate(filterStore, employees));
    }, [filterStore.currentPage, filterStore.elementsOnPage, employees]);

    React.useEffect(() => {
        let localList = [...employeeStore.list];
        localList = findEmployee(filterStore, employeeStore, localList);
        localList = sort(filterStore, organizations, localList);
        localList = filter(filterStore, employeeStore, localList);
        setEmployees(localList);
    }, [employeeStore.list]);

    return (
        <>
            <div className={style.list}>
                <RowHeader/>
                {
                    visibleList.map((employee, index) => {
                        return <Row index={index + 1}
                                    employee={employee}
                                    key={index}/>
                    })
                }
            </div>
            <div className={style.footer}>
                <ExcelButton/>
                <EmployeePagination/>
            </div>
        </>
    );
}

export default EmployeesList;