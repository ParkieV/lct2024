import {createAsyncThunk} from '@reduxjs/toolkit'
import {apiUrl} from "../constants";
import {CookieJar} from "tough-cookie";
import {wrapper} from "axios-cookiejar-support";

function createAxios() {
    const axios = require('axios');
    return wrapper(axios.create({
        baseURL: apiUrl,
        withCredentials: true,
        jar: jar,
        proxy: "http://localhost:8000"
    }));
}

const jar = new CookieJar();

const axiosInstance = createAxios();

export const updateCookies = async () => {
    let res = await axiosInstance.post(`/api/auth/refresh`);
    return res.status;
}

export const login = createAsyncThunk(
    'user/login', async ({user}, thunkAPI) => {
        let res = await axiosInstance.post(`/api/auth/login`, {
            ...user
        });
        await updateCookies();
        return res;
    });


export const logout = createAsyncThunk(
    'user/logout', async (_, thunkAPI) => {
        await updateCookies();
        let res = await axiosInstance.get(`/api/auth/logout`);
        return res;
    });


export const getOrganizations = createAsyncThunk(
    'organization/getOrganizations', async (_, thunkAPI) => {
        await updateCookies();
        let res = await axiosInstance.get(`/api/organization/organizations`);
        console.log(res);
        return res;
    });

export const getEmployees = createAsyncThunk(
    'user/getUsers', async ({recipe}, thunkAPI) => {
        let response = await fetch(`${apiUrl}/update_recipe`, {
            method: 'POST', headers: {
                'Content-Type': 'application/json'
            }, body: JSON.stringify(recipe),
        });
        return response.json();
    });

export const addUser = createAsyncThunk(
    'user/addUser', async ({user}, thunkAPI) => {
        await updateCookies();
        console.log(user);
        let res = await axiosInstance.post(`/api/user/`, {
            ...user
        });
        console.log(res)
        return res;
})