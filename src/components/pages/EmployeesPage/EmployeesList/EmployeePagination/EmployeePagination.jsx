import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import * as style from './EmployeePagination.module.css'

import arrow_left from './img/arrow_left.svg'
import arrow_right from './img/arrow_right.svg'
import {setCurrentPage} from "../../../../../store/listFilterSlice";

const PaginationButton = ({
                              children,
                              buttonStyle,
                              onClickCallback = (e) => {
                              },
                              isActive = false
                          }) => {
    const onClick = (e) => {
        onClickCallback(e, parseInt(children));
    }

    return (<button className={`${isActive && style.active}`}
                    style={buttonStyle}
                    onClick={onClick}>{children}</button>)
}

const EmployeePagination = (props) => {
    const employeeStore = useSelector(state => state.employee);
    const filterStore = useSelector(state => state.filter);

    const [maxPage, setMaxPage] = React.useState(filterStore.baseMaxPageNumberInPagination);
    const dispatch = useDispatch();

    const arrowClick = (e, arrowDirection) => {
        switch (arrowDirection) {
            case 'left': {
                if (filterStore.currentPage <= 1) {
                    return;
                }
                dispatch(setCurrentPage(filterStore.currentPage - 1))
                return;
            }
            case 'right': {
                if (filterStore.currentPage >= Math.ceil(employeeStore.list.length / filterStore.elementsOnPage.value)) {
                    return;
                }
                dispatch(setCurrentPage(filterStore.currentPage + 1))
                return;
            }
        }
    }

    const onClick = (e, page) => {
        dispatch(setCurrentPage(parseInt(page)))
    }

    // Сдвиг номеров пагинации
    const pageDelta = filterStore.currentPage - maxPage >= 0 ? filterStore.currentPage - maxPage + 1 : 0;
    const pageCount = Math.ceil(employeeStore.list.length / filterStore.elementsOnPage.value);

    return (<div className={style.pagination}>
        <PaginationButton onClickCallback={e => arrowClick(e, 'left')}>
                <span className={style.arrow}
                      style={{backgroundImage: `url(${arrow_left})`}}></span>
        </PaginationButton>

        {[...Array(Math.ceil(employeeStore.list.length / filterStore.elementsOnPage.value))].map((elem, index) => {
            const isActive = filterStore.currentPage - 1 === index;
            const isLastPages = filterStore.currentPage >= pageCount - 3;
            const maxLeftIndex = pageCount - maxPage - 2;


            if (index === maxPage + pageDelta && filterStore.currentPage + 1 < pageCount - 2) {
                return <PaginationButton key={index}>...</PaginationButton>
            }
            if (filterStore.currentPage + 1 < pageCount - 1 &&
                index >= maxPage + (isLastPages ? 0 : pageDelta) &&
                (!isLastPages ? index < pageCount - 1 : index < maxLeftIndex)) {
                return null;
            }
            if (index < (isLastPages ? maxLeftIndex : pageDelta)) {
                return null;
            }

            return <PaginationButton key={index}
                                     isActive={isActive}
                                     onClickCallback={onClick}>{index + 1}</PaginationButton>
        })}

        <PaginationButton onClickCallback={e => arrowClick(e, 'right')}>
                <span className={style.arrow}
                      style={{backgroundImage: `url(${arrow_right})`}}></span>
        </PaginationButton>
    </div>);
}

export default EmployeePagination;