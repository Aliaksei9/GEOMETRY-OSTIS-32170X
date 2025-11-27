import React from 'react';
import { Button, Form, Input } from 'antd';
import { useNavigate } from 'react-router';
import { createUserAgent } from '../../api/sc/agents/createUserAgent';

function SignUp() {
    const navigate = useNavigate();

    const onFinish = async (values) => {
        try {
            console.log('Sign Up Success:', values);
            await createUserAgent(values.username);
            navigate('/home');
        } catch (error) {
            console.error('Ошибка при создании пользователя:', error);
        }
    };

    const onFinishFailed = (errorInfo) => {
        console.log('Sign Up Failed:', errorInfo);
    };

    return (
        <Form
            name="sign-up"
            onFinish={onFinish}
            onFinishFailed={onFinishFailed}
            autoComplete="off"
            layout="vertical"
        >
            <Form.Item
                name="username"
                rules={[{ required: true, message: 'Введите имя пользователя' }]}
            >
                <Input
                    placeholder="Имя пользователя"
                    className="authorization-input"
                    size="large"
                />
            </Form.Item>

            <Form.Item
                name="email"
                rules={[
                    { required: true, message: 'Введите email' },
                    { type: 'email', message: 'Введите корректный email' }
                ]}
            >
                <Input
                    placeholder="Email"
                    className="authorization-input"
                    size="large"
                />
            </Form.Item>

            <Form.Item
                name="password"
                rules={[
                    { required: true, message: 'Введите пароль' },
                    { min: 6, message: 'Пароль должен быть не менее 6 символов' }
                ]}
            >
                <Input.Password
                    placeholder="Пароль"
                    className="authorization-input"
                    size="large"
                />
            </Form.Item>

            <Form.Item style={{ margin: '32px 0 0' }}>
                <Button
                    type="primary"
                    htmlType="submit"
                    block
                    className="auth-submit-button"
                    size="large"
                >
                    Создать аккаунт
                </Button>
            </Form.Item>
        </Form>
    );
}

export default SignUp;
