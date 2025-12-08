import React from 'react';
import { Avatar, Typography } from 'antd';
import { UserOutlined, MailOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router';
import Header from '../../pages/theory-tests-problems/header'; 
import ChatButton from '../../components/corner-chat/corner-chat-button';
import Logo from '../../media/og.png';
import './profile.css';

const { Text } = Typography;

function Profile() {
    const navigate = useNavigate();

    const passedTestsAmount = 52;
    const totalScore = 69;
    const totalTime = '9:11';

    return (
        <div style={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column', overflowX: 'hidden' }}>
            {/* Единая верхняя панель — как везде */}
            <Header showBackButton={true} onBack={() => navigate('/home')} />

            {/* Основной контент — центрированный белый блок */}
            <div style={{ width: '100%', display: 'flex', justifyContent: 'center', padding: '20px' }}>
                <div className="profile-main">
                    {/* === АВАТАР + ИМЯ + EMAIL === */}
                    <div className="profile-header-info">
                        <Avatar
                            icon={<UserOutlined />}
                            size={140}
                            style={{ backgroundColor: '#6F60C1', color: 'white' }}
                        />
                        <div>
                            <div className="user-name">Alica Bubnova</div>
                            <div className="user-email">
                                <Avatar size={48} icon={<MailOutlined />} />
                                <span>alicebubnova@gmail.com</span>
                            </div>
                        </div>
                    </div>

                    {/* === СТАТИСТИКА === */}
                    <div className="profile-stats">
                        <div className="stat-circle-box">
                            <div className="stat-circle">
                                <div className="stat-value">{passedTestsAmount}</div>
                            </div>
                            <div className="stat-label">Пройдено тестов</div>
                        </div>

                        <div className="stat-circle-box">
                            <div className="stat-circle">
                                <div className="stat-value">{totalScore}</div>
                            </div>
                            <div className="stat-label">Заработано баллов</div>
                        </div>

                        <div className="stat-circle-box">
                            <div className="stat-circle">
                                <div className="stat-value">{totalTime}</div>
                            </div>
                            <div className="stat-label">Время тренировок</div>
                        </div>
                    </div>
                </div>
            </div>

            <ChatButton />
        </div>
    );
}

export default Profile;
