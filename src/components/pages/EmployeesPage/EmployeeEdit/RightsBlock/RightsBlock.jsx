import React from 'react';
import * as style from './RightsBlock.module.css'

class Right {
    constructor(name, label, checked = false) {
        this.name = name;
        this.label = label;
        this.checked = checked;
    }

    setChecked(checked) {
        this.checked = checked;
    }
}

const RightsBlock = (props) => {
    const [isActiveAdmin, setActiveAdmin] = React.useState(null);

    const [rightsAdmin, setRightsAdmin] = React.useState([
        // new Right("add_user", "Добавление и удаление пользователей"),
        new Right("excel", "Выгрузка данных в Excel"),
    ]);
    const [rightsUser, setRightsUser] = React.useState([
        new Right("permission_suggestion", "Доступ к прогнозу по закупкам"),
        new Right("create_purchase", "Создание новых закупок"),
        new Right("analysis_common", "Просмотр аналитики истории закупок"),
        new Right("analysis_product", "Просмотр аналитики по товару"),
        new Right("balance", "Добавление сведений о балансе"),
    ]);

    React.useEffect(() => {
        let flag = null;
        rightsAdmin.forEach((right, index) => {
            if (right.checked) {
                flag = 'admin';
            }
        });
        if (flag === 'admin') {
            setActiveAdmin(true);
            return;
        }

        rightsUser.forEach((right, index) => {
            if (right.checked) {
                flag = 'user';
            }
        });
        if (flag === 'user') {
            setActiveAdmin(false);
            return;
        }
        setActiveAdmin(null);

    }, [rightsAdmin, rightsUser])
    console.log(isActiveAdmin)
    return (
        <div className={style.rights}>
            <div
                className={`${style.rightBlock} ${isActiveAdmin !== null ? (isActiveAdmin === true ? style.active : style.inactive) : ''}`}>
                <b className={style.blockHeader}>Администратор</b>
                <div className={style.rightCheckboxBlock}>
                    {
                        rightsAdmin.map((right, index) => {
                            return (
                                <div key={index} className={style.rightCheckboxContainer}>
                                    <input type="checkbox"
                                           name={right.name}
                                           onChange={e => {
                                               if (isActiveAdmin !== null && isActiveAdmin === false) {
                                                   e.target.checked = false;
                                                   return;
                                               }
                                               let localRights = [...rightsAdmin];
                                               localRights[index].setChecked(e.target.checked);
                                               console.log(localRights)
                                               setRightsAdmin(localRights);
                                           }}/>
                                    <label>{right.label}</label>
                                </div>
                            )
                        })
                    }
                </div>
            </div>
            <div
                className={`${style.rightBlock} ${isActiveAdmin !== null ? (isActiveAdmin === false ? style.active : style.inactive) : ''}`}>
                <b className={style.blockHeader}>Пользователь</b>
                <div className={style.rightCheckboxBlock}>
                    {
                        rightsUser.map((right, index) => {
                            return (
                                <div key={index} className={style.rightCheckboxContainer}>
                                    <input type="checkbox"
                                           name={right.name}
                                           onChange={e => {
                                               if (isActiveAdmin !== null && isActiveAdmin === true) {
                                                   e.target.checked = false;
                                                   return;
                                               }
                                               let localRights = [...rightsUser];
                                               localRights[index].setChecked(e.target.checked);
                                               setRightsUser(localRights);
                                           }}/>
                                    <label>{right.label}</label>
                                </div>
                            )
                        })
                    }
                </div>
            </div>
        </div>
    );
}

export default RightsBlock;