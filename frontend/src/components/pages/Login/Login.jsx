import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import * as style from './Login.module.css'
import Input from "../../UI/Input/Input";
import {useNavigate} from "react-router-dom";
import {EMPLOYEES_PAGE_URL} from "../../../constants";
import {setLogin} from "../../../store/userSlice";

const Login = (props) => {
    const navigate = useNavigate();
    const data = useSelector(state => state.data);
    const dispatch = useDispatch();
    console.log(data);

    const onSubmit = (e) => {
        e.preventDefault();
        const inputsData = Array
            .from(e.target.elements)
            .filter(elem => elem.tagName.toLowerCase() === 'input')
            .map(input => {
                return {
                    name: input.name,
                    value: input.value
                }
            });
        e.target.reset();

        dispatch(setLogin(true))
        // TODO: заменить это на что-то другое
        localStorage.setItem('isLogin', 'true');
        navigate(EMPLOYEES_PAGE_URL);
    }

    return (
        <form className={style.loginContainer} onSubmit={onSubmit}>
            <div className={style.login}>
                <div className={style.header}>
                    <b>Вход</b>
                    {/*<hr/>*/}
                </div>
                <div className={style.body}>
                    <Input placeholder="Эл. почта @mos.ru или номер телефона"
                           label="Логин"
                           required={true}
                           type="email"
                           name="email"/>
                    <Input placeholder="Пароль"
                           label="Пароль"
                           required={true}
                           type="password"
                           name="password"/>
                </div>
                <button type="submit">Войти</button>
            </div>
        </form>
    );
}

export default Login;