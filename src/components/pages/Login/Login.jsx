import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import * as style from './Login.module.css'
import Input from "../../UI/Input/Input";
import {useNavigate} from "react-router-dom";
import {login} from "../../../store/thunk";
import {EMPLOYEES_PAGE_URL} from "../../../constants";

const Login = (props) => {
    const navigate = useNavigate();
    const data = useSelector(state => state.data);
    const dispatch = useDispatch();

    const onSubmit = async (e) => {
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

        let res = await dispatch(login({
            user: {
                email: inputsData[0].value,
                password: inputsData[1].value
            }
        })).unwrap()

        if (res.status === 200) {
            navigate(EMPLOYEES_PAGE_URL);
        }

        // dispatch(setLogin(true))
        // TODO: заменить это на что-то другое
        // localStorage.setItem('isLogin', 'true');
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
                           name="email"
                           defaultValue={"user@mos.ru"}/>
                    <Input placeholder="Пароль"
                           label="Пароль"
                           required={true}
                           type="password"
                           name="password"
                           defaultValue={"test123"}/>
                </div>
                <button type="submit">Войти</button>
            </div>
        </form>
    );
}

export default Login;