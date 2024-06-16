import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import * as style from './Header.module.css'
import headerLogo from './img/logo.png';
import exitSvg from './img/exit.svg';
import Wrapper from "../UI/Wrapper/Wrapper";
import {setLogin} from "../../store/userSlice";
import {useNavigate} from "react-router-dom";
import {LOGIN_PAGE_URL} from "../../constants";

const Header = (props) => {
    const userStore = useSelector(state => state.user);
    const dispatch = useDispatch();

    const navigate = useNavigate();

    const logout = () => {
        dispatch(setLogin(false))
        localStorage.clear();
        navigate(LOGIN_PAGE_URL);
    }

    return (
        <header className={style.headerContainer}>
            <Wrapper>
                <div className={style.header}>
                    <img className={!userStore.isLogin && style.isOnlyLogo || ""} src={headerLogo} alt="logo"/>
                    {userStore.isLogin && <div className={style.user}>
                        <p>{userStore.name}</p>
                        <button onClick={logout}>
                            <img src={exitSvg} alt="exit"/>
                        </button>
                    </div>}
                </div>
            </Wrapper>
        </header>
    );
}

export default Header;