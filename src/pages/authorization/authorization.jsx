import React, { useState } from 'react';
import LogIn from './log-in';
import SignUp from './sign-up';
import Logo from '../../media/og.png';
import './authorization.css';
import { Typography } from 'antd';

const { Text } = Typography;

function Authorization() {
    const [isLogin, setIsLogin] = useState(true);

    return (
        <div className="authorization-page">
            <img src={Logo} alt="OSTIS Geometry" className="auth-logo" />
            <Text strong className="app-title">OSTIS Geometry</Text>
            <div className="authorization-box">
                <Text strong className="authorization-title">
                    {isLogin ? 'Log In' : 'Sign Up'}
                </Text>

                <div className="auth-subtitle">
                    {isLogin ? (
                        <>
                            Нет аккаунта? <span className="auth-link" onClick={() => setIsLogin(false)}>Зарегистрироваться</span>
                        </>
                    ) : (
                        <>
                            Уже есть аккаунт? <span className="auth-link" onClick={() => setIsLogin(true)}>Войти</span>
                        </>
                    )}
                </div>

                {isLogin ? <LogIn /> : <SignUp />}
            </div>
        </div>
    );
}

export default Authorization;
