import React, { useRef } from 'react';
import { Typography, Form, Input, Switch, Button, Space } from 'antd';
import { useNavigate } from 'react-router';
import Header from '../../pages/theory-tests-problems/header'; // ← твой общий Header
import ChatButton from '../../components/corner-chat/corner-chat-button';
import './settings.css';

const { Text } = Typography;

function Settings() {
    const navigate = useNavigate();
    const passwordForm = useRef(null);

    const handlePasswordFormFinish = (values) => {
        if (values['new-password'] === values['old-password']) {
            passwordForm.current.setFieldsValue({
                'new-password': '',
            });
            passwordForm.current.setFields([
                {
                    name: 'new-password',
                    errors: ['Новый пароль не должен совпадать со старым'],
                },
            ]);
            return;
        }
        console.log('Пароль успешно изменён:', values);
        // Здесь будет запрос на сервер
    };

    return (
        <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', overflowX: 'hidden' }}>
            {/* Единая верхняя панель */}
            <Header showBackButton={true} onBack={() => navigate(-1)} />

            {/* Основной контент */}
            <div style={{ flex: 1, display: 'flex', justifyContent: 'center', padding: '20px 40px' }}>
                <div className="settings-main">
                    {/* === ОПОВЕЩЕНИЯ === */}
                    <div>
                        <Text className="settings-section-title">Оповещения</Text>
                        
                        <div style={{ marginTop: 32 }}>
                            <div className="notifications-item">
                                <Text className="notifications-text">Почта для оповещения</Text>
                                <div className="email-input-wrapper">
                                    <Input
                                        defaultValue="alicebobovna@gmail.com"
                                        size="large"
                                        onPressEnter={(e) => console.log('Email сохранён:', e.target.value)}
                                    />
                                </div>
                            </div>

                            <div className="notifications-item">
                                <Text className="notifications-text">
                                    Получать оповещения о новых темах, тестах и задачах
                                </Text>
                                <Switch defaultChecked disabled />
                            </div>

                            <div className="notifications-item" style={{ borderBottom: 'none' }}>
                                <Text className="notifications-text">
                                    Получать новости о новом функционале
                                </Text>
                                <Switch defaultChecked disabled />
                            </div>
                        </div>
                    </div>

                    {/* === БЕЗОПАСНОСТЬ === */}
                    <div>
                        <Text className="settings-section-title">Безопасность</Text>

                        <Form
                            ref={passwordForm}
                            onFinish={handlePasswordFormFinish}
                            layout="vertical"
                            className="password-form"
                            style={{ marginTop: 32 }}
                        >
                            <Form.Item
                                name="old-password"
                                label="Старый пароль"
                                rules={[{ required: true, message: 'Введите старый пароль' }]}
                            >
                                <Input.Password placeholder="••••••••" />
                            </Form.Item>

                            <Form.Item
                                name="new-password"
                                label="Новый пароль"
                                rules={[
                                    { required: true, message: 'Введите новый пароль' },
                                    { min: 6, message: 'Минимум 6 символов' }
                                ]}
                            >
                                <Input.Password placeholder="••••••••" />
                            </Form.Item>

                            <Form.Item>
                                <Button
                                    type="primary"
                                    htmlType="submit"
                                    className="change-password-btn"
                                >
                                    Изменить пароль
                                </Button>
                            </Form.Item>
                        </Form>
                    </div>
                </div>
            </div>

            <ChatButton />
        </div>
    );
}

export default Settings;
