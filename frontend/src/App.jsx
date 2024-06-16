import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import Header from "./components/Header/Header";
import {Route, Routes, useLocation, useNavigate} from "react-router-dom";
import Login from "./components/pages/Login/Login";
import EmployeesPage from "./components/pages/EmployeesPage/EmployeesPage";
import {EMPLOYEES_PAGE_URL, LOGIN_PAGE_URL} from "./constants";
import Wrapper from "./components/UI/Wrapper/Wrapper";
import {setLogin} from "./store/userSlice";

const App = () => {
    const location = useLocation();
    const navigate = useNavigate();

    const userStore = useSelector(state => state.user);
    const dispatch = useDispatch();

    React.useEffect(() => {
        const isLogin = localStorage.getItem("isLogin");
        isLogin && dispatch(setLogin(true));
    }, [])

    React.useEffect(() => {
        const isLogin = localStorage.getItem("isLogin");
        if (!isLogin) {
            navigate(LOGIN_PAGE_URL);
        } else if (isLogin) {
            navigate(EMPLOYEES_PAGE_URL);
        }
    }, [location.pathname]);

    return (
        <>
            <Header/>
            <Wrapper>
                <Routes>
                    <Route path={LOGIN_PAGE_URL} element={<Login/>}/>
                    <Route path={EMPLOYEES_PAGE_URL} element={<EmployeesPage/>}/>
                </Routes>
            </Wrapper>
        </>
    );
}

export default App;