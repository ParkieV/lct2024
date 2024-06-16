import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import * as style from './Header.module.css'
import headerLogo from './img/logo.png';
import exitSvg from './img/exit.svg';
import Wrapper from "../UI/Wrapper/Wrapper";
import {setLogin} from "../../store/userSlice";
import {useNavigate} from "react-router-dom";
import {LOGIN_PAGE_URL} from "../../constants";
import {logout} from "../../store/thunk";

const Header = (props) => {
    const userStore = useSelector(state => state.user);
    const dispatch = useDispatch();

    const navigate = useNavigate();

    const logoutHandler = () => {
        const logoutAsync = async ()  =>  {
            await dispatch(logout())
            navigate(LOGIN_PAGE_URL);
        }
        logoutAsync().then(r => r);
    }

    return (
        <header className={style.headerContainer}>
            <Wrapper>
                <div className={style.header}>
                    <img className={!userStore.isLogin && style.isOnlyLogo || ""} src={headerLogo} alt="logo"/>
                    {userStore.isLogin && <div className={style.user}>
                        <p>{userStore?.user?.last_name} {userStore?.user?.first_name[0]}.{userStore?.user?.middle_name[0]}</p>
                        <button onClick={logoutHandler}>
                            <img src={exitSvg} alt="exit"/>
                        </button>
                    </div>}
                </div>
            </Wrapper>
        </header>
    );
}

export default Header;