import React, { useState } from 'react';
import { Typography, Button, Dropdown, Avatar } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import { theory, tests, problems } from './seventh-grade-data';
import { useNavigate } from 'react-router';
import ChatButton from '../../../components/corner-chat/corner-chat-button';
import UnknownProblemsButton from './problems/UnknownProblemsButton'; 
import Logo from '../../../media/og.png';
import '../../../index.css';
import '../../../pages/home/home.css';
import '../theory-tests-problems.css';

const { Text } = Typography;

function SeventhGradeTTP() {
    const navigate = useNavigate();
    const [activeTab, setActiveTab] = useState('theory');

    // ──────────────────────────────── ПРОФИЛЬ ДРОПДАУН ────────────────────────────────
    const profileDropdownItems = [
        {
            key: 'header',
            label: (
                <div className="profile-header">
                    <Avatar
                        icon={<UserOutlined />}
                        size={88}
                        style={{ backgroundColor: '#6F60C1', color: 'white' }}
                    />
                    <div className="user-name">Alica Bubnova</div>
                </div>
            ),
            disabled: true,
        },
        { type: 'divider' },
        { key: 'profile', label: 'Профиль', onClick: () => navigate('/profile') },
        { key: 'balance', label: 'Баланс остиков' },
        { key: 'settings', label: 'Настройки', onClick: () => navigate('/settings') },
        { key: 'help', label: 'Помощь', onClick: () => navigate('/help') },
        { type: 'divider' },
        {
            key: 'logout',
            label: <span className="profile-logout">Выйти</span>,
            onClick: () => navigate('/'),
        },
    ];

    const content = activeTab === 'theory' ? theory : activeTab === 'tests' ? tests : problems;
    const headerText =
        activeTab === 'theory' ? 'ВЫБЕРИТЕ ТЕМУ' :
        activeTab === 'tests' ? 'ВЫБЕРИТЕ ТЕСТ' :
        'ВЫБЕРИТЕ ЗАДАЧУ';

    return (
        <div className="ttp-root-wrapper">
            {/* ====================== ХЕДЕР ====================== */}
            <div id="home-header" style={{ paddingLeft: '20px' }}>
                <div className="header-half">
                    <Button
                        className="button header-button header-logo-button"
                        onClick={() => navigate('/home')}
                        style={{
                            padding: '0 20px',
                            height: '70%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                        }}
                    >
                        <img src={Logo} alt="OSTIS-geometry logo" style={{ height: '60%', width: 'auto' }} />
                    </Button>

                    <Button
                        className={`button header-button ${activeTab === 'theory' ? 'active' : ''}`}
                        onClick={() => setActiveTab('theory')}
                        data-tab="theory" 
                    >
                        <span className="header-button-text">Теория</span>
                    </Button>
                    <Button
                        className={`button header-button ${activeTab === 'tests' ? 'active' : ''}`}
                        onClick={() => setActiveTab('tests')}
                        data-tab="tests"
                    >
                        <span className="header-button-text">Тесты</span>
                    </Button>
                    <Button
                        className={`button header-button ${activeTab === 'problems' ? 'active' : ''}`}
                        onClick={() => setActiveTab('problems')}
                        data-tab="problems" 
                    >
                        <span className="header-button-text">Задачи</span>
                    </Button>
                </div>

            {/* ──────────────────────── АВАТАР + КРАСИВЫЙ ПРОФИЛЬ ──────────────────────── */}
            <div className="header-half" style={{ flexDirection: 'row-reverse', marginRight: '40px' }}>
                <Dropdown
                    menu={{ items: profileDropdownItems }}
                    placement="bottomRight"
                    trigger={['click']}
                    overlayClassName="home-profile-dropdown"  
                    dropdownRender={(menu) => (
                        <div style={{ marginTop: '23px', borderRadius: '20px', overflow: 'hidden' }}>
                            {React.cloneElement(menu)}
                        </div>
                    )}
                >
                    <Avatar
                        icon={<UserOutlined />}
                        size={68}
                        style={{
                            cursor: 'pointer',
                            backgroundColor: 'white',
                            border: '3px solid #6F60C1',
                            color: '#6F60C1',
                            boxShadow: '0 0 12px rgba(111, 96, 193, 0.35)',
                            transition: 'all 0.3s ease',
                        }}
                        onMouseEnter={(e) => (e.currentTarget.style.transform = 'scale(1.1)')}
                        onMouseLeave={(e) => (e.currentTarget.style.transform = 'scale(1)')}
                    />
                </Dropdown>
            </div>
        </div>

            {/* ====================== ЦЕНТРАЛЬНЫЙ БЛОК ====================== */}
            <div className="ttp-main-container">
                <div className="ttp-content-block">
                    {/* Заголовок */}
                    <Text className="content-header" strong>
                        {headerText}
                    </Text>

                    {/* Кнопка "Решение неизвестных задач" — всегда сверху, не скроллится */}
                    {activeTab === 'problems' && (
                        <div style={{ textAlign: 'center' }}>
                            <UnknownProblemsButton />
                        </div>
                    )}

                    {/* Только этот блок скроллится */}
                    <div className="ttp-scroll-area">
                        {content.length > 0 ? (
                            content.map((item, index) => (
                                <div key={item.key || `item-${index}`}>
                                    {item}
                                </div>
                            ))
                        ) : (
                            <Text style={{ color: '#999', fontSize: 18, textAlign: 'center', marginTop: '60px' }}>
                                Нет доступного контента
                            </Text>
                        )}
                    </div>
                </div>
            </div>

            <ChatButton />
        </div>
    );
}

export default SeventhGradeTTP;
