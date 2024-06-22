import React from 'react';
import {useDispatch, useSelector} from "react-redux";
import Header from "./components/Header/Header";
import {Route, Routes, useLocation, useNavigate} from "react-router-dom";
import Login from "./components/pages/Login/Login";
import EmployeesPage from "./components/pages/EmployeesPage/EmployeesPage";
import {EMPLOYEES_PAGE_URL, LOGIN_PAGE_URL} from "./constants";
import Wrapper from "./components/UI/Wrapper/Wrapper";
import {setLogin} from "./store/userSlice";
import {login} from "./store/thunk";

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
        const checkLogin = async () => {
            if (userStore.isLogin) {
                navigate(EMPLOYEES_PAGE_URL);
                return;
            }

            if (localStorage.getItem('email') !== null &&
                localStorage.getItem('password') !== null) {
                console.log(localStorage.getItem('email'), localStorage.getItem('password'))
                let res = await dispatch(login({
                    user: {
                        email: localStorage.getItem('email'),
                        password: localStorage.getItem('password'),
                    }
                })).unwrap();
                if (res.status ===  200)  {
                    navigate(EMPLOYEES_PAGE_URL);
                }
            } else {
                localStorage.clear();
                navigate(LOGIN_PAGE_URL);
            }
        }
        checkLogin().then(r => r);
    }, [location.pathname]);

    return (
        <>
            <Header/>
            <Wrapper>
                <Routes>
                    <Route exact path={LOGIN_PAGE_URL} element={<Login/>}/>
                    <Route exact path={EMPLOYEES_PAGE_URL} element={<EmployeesPage/>}/>
                </Routes>
            </Wrapper>
        </>
    );
}

export default App;
