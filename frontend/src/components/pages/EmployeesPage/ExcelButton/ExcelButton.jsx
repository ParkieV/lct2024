import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import * as style from './ExcelButton.module.css'
import excelDownload from './img/excel.svg';
import excelWhiteDownload from './img/excelWhite.svg';

const ExcelButton = (props) => {
    const imgRef = React.useRef(null);

    const data = useSelector(state => state.data);
    const dispatch = useDispatch();

    const hoverButtonHandler = (e, isHover) => {
        imgRef.current.style.backgroundImage = `url(${isHover ? excelWhiteDownload : excelDownload})`
    }

    const downloadHandler = (e) => {
        console.log(1)
    }

    return (
        <button className={style.excelButton}
                onMouseOver={e => hoverButtonHandler(e, true)}
                onMouseOut={e => hoverButtonHandler(e, false)}
                onClick={downloadHandler}
        >
            <span ref={imgRef}
                  style={{backgroundImage: `url(${excelDownload})`}}></span>
            <p>Скачать в формате Excel</p>
        </button>
    );
}

export default ExcelButton;