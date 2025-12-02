import React from 'react';
import { Button, Form, Input, Switch, Typography } from 'antd';
import { useNavigate } from 'react-router';

const { Text } = Typography;

function LogIn() {
    const navigate = useNavigate();

    const onFinish = (values) => {
        console.log('Log In Success:', values);
        navigate('/home'); // или '/'
    };

    const onFinishFailed = (errorInfo) => {
        console.log('Log In Failed:', errorInfo);
    };

    return (
        <Form
            name="log-in"
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
                name="password"
                rules={[{ required: true, message: 'Введите пароль' }]}
            >
                <Input.Password
                    placeholder="Пароль"
                    className="authorization-input"
                    size="large"
                />
            </Form.Item>


            
            <Form.Item>
    		<div className="auth-remember-wrapper">
        	    <Form.Item name="remember" valuePropName="checked" noStyle>
            		<Switch defaultChecked />
        	    </Form.Item>
            	    <Text style={{ color: '#5C6BC0', fontSize: 17, fontWeight: '600', margin: 0 }}>
            Запомнить меня
		    </Text>
   	        </div>
	    </Form.Item>

            <Form.Item style={{ margin: '24px 0 0' }}>
                <Button
                    type="primary"
                    htmlType="submit"
                    block
                    className="auth-submit-button"
                    size="large"
                >
                    Войти
                </Button>
            </Form.Item>
        </Form>
    );
}

export default LogIn;
