import React from 'react';
import { Button, Dropdown, Avatar, Typography } from 'antd';
import { UserOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router';
import Logo from '../../media/og.png';
import '../../index.css';
import '../../pages/home/home.css'; // ← стили хедера и нового профиля

const { Text } = Typography;

function Header({ showBackButton = false, onBack }) {
    const navigate = useNavigate();

    // ──────────────────────── КРАСИВЫЙ ПРОФИЛЬ-ДРОПДАУН (как на Home) ────────────────────────
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

    return (
        <div id="home-header" style={{ paddingLeft: '20px' }}>
            <div className="header-half">
                {/* Логотип-кнопка на главную */}
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
                    <img
                        src={Logo}
                        alt="OSTIS-geometry logo"
                        style={{ height: '60%', width: 'auto', pointerEvents: 'none' }}
                    />
                </Button>

                {/* Кнопка "Назад" — появляется по пропсу */}
                {showBackButton && (
                    <Button
                        className="button header-button"
                        onClick={onBack || (() => navigate('/seven-grade-tests-theory-problems'))}
                    >
                        <span className="header-button-text">Назад</span>
                    </Button>
                )}
            </div>

            {/* ──────────────────────── АВАТАР + КРАСИВЫЙ ПРОФИЛЬ ──────────────────────── */}
            <div className="header-half" style={{ flexDirection: 'row-reverse', marginRight: '40px' }}>
                <Dropdown
                    menu={{ items: profileDropdownItems }}
                    placement="bottomRight"
                    trigger={['click']}
                    overlayClassName="home-profile-dropdown"  // ← используем тот же класс, что и на главной
                    dropdownRender={(menu) => (
                        <div style={{ borderRadius: '20px', overflow: 'hidden' }}>
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
    );
}

export default Header;
